from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from .forms import NewUserForm
from board.models import Workspace

@login_required
def home(request):
    # Получаем все пространства пользователя
    workspaces = Workspace.objects.filter(owner=request.user).prefetch_related('projects')
    workspaces_data = []

    for workspace in workspaces:
        workspace_dict = {
            'id': workspace.id,
            'name': workspace.name,
            'projects': []
        }

        # Получаем все проекты в пространстве
        projects = workspace.projects.all()
        for project in projects:
            project_dict = {
                'id': project.id,
                'name': project.name,
            }
            workspace_dict['projects'].append(project_dict)

        workspaces_data.append(workspace_dict)

    return render(request, 'index.html', {
        'workspaces': workspaces_data,
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