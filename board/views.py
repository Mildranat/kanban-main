import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render, get_object_or_404
from .forms import NewUserForm
from board.models import Notification, Project, Task, Workspace
from datetime import timedelta
from django.utils import timezone

@login_required
def home(request):
    today = timezone.now().date()
    
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
    
    workspaces = Workspace.objects.filter(owner=request.user)
    
    return render(request, 'index.html', {
        'completed_tasks_count': completed_tasks_count,
        'rejected_tasks_count': rejected_tasks_count,
        'recent_completed_tasks': recent_completed_tasks,
        'workspaces': workspaces,
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
def workspace_view(request, workspace_id):
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
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
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