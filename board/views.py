import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render, get_object_or_404
from .forms import NewUserForm
from board.models import MemberRating, Notification, OrganizationMember, Project, Task, Workspace, WorkspaceInvite
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from django.http import JsonResponse


@login_required
def home(request):
    today = timezone.now().date()
    
    # Получаем все рабочие пространства пользователя
    workspaces = Workspace.objects.filter(owner=request.user)
    
    # Подсчет выполненных задач за сегодня
    completed_tasks = Task.objects.filter(
        column__project__workspace__owner=request.user,
        completed=True,
        completed_at__date=today
    )
    
    # Подсчет отклоненных задач за сегодня
    rejected_tasks = Task.objects.filter(
        column__project__workspace__owner=request.user,
        rejected=True,
        rejected_at__date=today
    )
    
    completed_tasks_count = completed_tasks.count()
    rejected_tasks_count = rejected_tasks.count()
    
    # Последние выполненные задачи
    recent_completed_tasks = completed_tasks.order_by('-completed_at')[:3]
    
    return render(request, 'index.html', {
        'completed_tasks_count': completed_tasks_count,
        'rejected_tasks_count': rejected_tasks_count,
        'recent_completed_tasks': recent_completed_tasks,
        'workspaces': workspaces,  # Добавляем workspaces в контекст
    })

@login_required
def board_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, workspace__owner=request.user)
    workspaces = Workspace.objects.filter(owner=request.user).prefetch_related('projects')
    
    workspaces_data = []
    for ws in workspaces:
        workspaces_data.append({
            'id': ws.id,
            'name': ws.name,
            'projects': [{'id': p.id, 'name': p.name} for p in ws.projects.all()]
        })
    
    return render(request, 'board.html', {
        'project': project,
        'workspaces': workspaces_data,
        'workspaces_json': json.dumps(workspaces_data),  
    })

@login_required
def create_workspace(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            workspace = Workspace.objects.create(
                name=name,
                owner=request.user
            )
            # Создаем запись владельца
            OrganizationMember.objects.create(
                user=request.user,
                workspace=workspace,
                role='owner'
            )
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Название не может быть пустым'})
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'}) 

@login_required
def workspace_view(request, workspace_id):
        # Получаем все пространства, где пользователь владелец или участник
    owned_workspaces = Workspace.objects.filter(owner=request.user)
    member_workspaces = Workspace.objects.filter(
        organizationmember__user=request.user
    )
    workspaces = (owned_workspaces | member_workspaces).distinct()
    
    if workspace_id:
        workspace = get_object_or_404(workspaces, id=workspace_id)
    else:
        workspace = workspaces.first()
    
    workspace = get_object_or_404(Workspace, id=workspace_id, owner=request.user)
    
    if request.method == 'POST':
        project_name = request.POST.get('project_name')
        if project_name:
            Project.objects.create(
                workspace=workspace,
                name=project_name
            )
            return redirect('board:workspace', workspace_id=workspace_id)
    
    projects = workspace.projects.all()
    
    return render(request, 'workspace.html', {
        'workspace': workspace,
        'projects': projects,
    })

@login_required
def notifications_view(request):
    # Убираем исключение отклонённых задач
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    # Помечаем как прочитанные при открытии
    if request.method == 'GET':
        notifications.filter(read=False).update(read=True)
    
    workspaces = Workspace.objects.filter(owner=request.user)
    
    return render(request, 'notifications.html', {
        'notifications': notifications,
        'workspaces': workspaces,
    })


@login_required
def mark_all_read(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, read=False).update(read=True)
        messages.success(request, 'Все уведомления помечены как прочитанные')
    return redirect('board:notifications')

@login_required
def organization_view(request):
    # Участники (фильтруем по workspace, где пользователь владелец)
    members = OrganizationMember.objects.filter(
        workspace__owner=request.user
    ).select_related('user')
    
    # Рейтинг (топ-10 за текущую неделю)
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    top_members = (
        MemberRating.objects.filter(date__gte=start_of_week)
        .order_by('-points')[:10]
    )
    
    return render(request, 'organization.html', {
        'members': members,
        'top_members': top_members,
    })

def register_request(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request,
                             'Аккаунт зарегистрирован: '
                             'добро пожаловать на сайт!')
            return redirect('board:home')
        messages.error(request, 'Не удалось зарегистрировать аккаунт. '
                                'Проверьте корректность данных и '
                                'попробуйте еще раз!')
    form = NewUserForm()
    return render(request=request,
                  template_name='register.html',
                  context={'register_form': form})

def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request,
                              f'Вы вошли на сайт под ником {username}.')
                return redirect('board:home')
            else:
                messages.error(request, 'Неверные имя и/или пароль.')
        else:
            messages.error(request, 'Неверные имя и/или пароль.')
    form = AuthenticationForm()
    return render(request=request, template_name='login.html',
                  context={'login_form': form})

def logout_request(request):
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта.')
    return redirect('board:login')

@login_required
def invite_member(request, workspace_id):
    workspace = get_object_or_404(Workspace, id=workspace_id, owner=request.user)
    
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Создаем приглашение
        invite = WorkspaceInvite.objects.create(
            workspace=workspace,
            email=email,
            created_by=request.user
        )
        
        # Отправляем email с приглашением
        invite_link = f"{settings.SITE_URL}/accept-invite/{invite.token}/"
        send_mail(
            f"Приглашение в пространство {workspace.name}",
            f"Вас пригласили присоединиться к пространству {workspace.name}. "
            f"Перейдите по ссылке: {invite_link}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        messages.success(request, 'Приглашение отправлено!')
        return redirect('board:workspace', workspace_id=workspace_id)
    
    return redirect('board:workspace', workspace_id=workspace_id)

from django.contrib.auth import login
from django.contrib.auth.models import User

def accept_invite(request, token):
    # Сначала находим приглашение по токену без проверки email
    invite = get_object_or_404(WorkspaceInvite, token=token, email=request.user.email)
    
    # Если пользователь не авторизован
    if not request.user.is_authenticated:
        # Проверяем, есть ли пользователь с таким email
        try:
            user = User.objects.get(email=invite.email)
            # Авторизуем пользователя
            login(request, user)
        except User.DoesNotExist:
            # Предлагаем зарегистрироваться
            messages.info(request, f'Для принятия приглашения зарегистрируйтесь с email {invite.email}')
            return redirect('board:register')
    
    # Проверяем, что email пользователя совпадает с email в приглашении
    if request.user.email != invite.email:
        messages.error(request, 'Приглашение предназначено для другого email')
        return redirect('board:home')
    
    if not invite.is_accepted:
        OrganizationMember.objects.get_or_create(
            user=request.user,
            workspace=invite.workspace,  # Связываем с workspace, а не с owner
            defaults={'role': 'member'}
        )
        invite.is_accepted = True
        invite.save()
        messages.success(request, f'Вы успешно присоединились к пространству {invite.workspace.name}!')
    else:
        messages.info(request, 'Вы уже приняли это приглашение')
    
    return redirect('board:workspace', workspace_id=invite.workspace.id)