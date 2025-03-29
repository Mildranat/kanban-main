import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render, get_object_or_404
from .forms import NewUserForm
from board.models import Project, Task, Workspace
from datetime import datetime, timedelta

@login_required
def home(request):
    today = datetime.today().date()
    completed_tasks_count = Task.objects.filter(
        column__project__workspace__owner=request.user,
        updated_at__date=today,
        column__name="Завершено" 
    ).count()

    workspaces = Workspace.objects.filter(owner=request.user)
    
    return render(request, 'index.html', {
        'completed_tasks_count': completed_tasks_count,
        'workspaces': workspaces,
    })

@login_required
def board_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, workspace__owner=request.user)
    workspaces = Workspace.objects.filter(owner=request.user).prefetch_related('projects')
    
    # Сериализуем workspaces в JSON
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
        'workspaces_json': json.dumps(workspaces_data),  # Для JavaScript
    })

@login_required
def workspace_view(request, workspace_id):
    workspace = get_object_or_404(Workspace, id=workspace_id, owner=request.user)
    projects = workspace.projects.all()
    
    return render(request, 'workspace.html', {
        'workspace': workspace,
        'projects': projects,
    })

@login_required
def notifications_view(request):
    # This is a placeholder - you'll need to implement actual notifications logic
    notifications = [
        {
            'type': 'task_completed',
            'message': 'Задача "Обновить документацию" была выполнена',
            'created_at': datetime.now(),
            'read': False
        },
        {
            'type': 'task_assigned',
            'message': 'Вам назначена новая задача "Проверить баги" от пользователя Иван Иванов',
            'created_at': datetime.now() - timedelta(hours=2),
            'read': True
        }
    ]
    
    workspaces = Workspace.objects.filter(owner=request.user)
    
    return render(request, 'notifications.html', {
        'notifications': notifications,
        'workspaces': workspaces,
    })


@login_required
def notifications_view(request):
    notifications = request.user.notifications.all()
    workspaces = Workspace.objects.filter(owner=request.user)
    
    return render(request, 'notifications.html', {
        'notifications': notifications,
        'workspaces': workspaces,
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
            return redirect('board:login')
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