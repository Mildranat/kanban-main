from django.urls import path
from api.views import (
    ListTask, DetailTask,
    ListCreateColumn, DetailColumn,
    ListCreateProject, DetailProject,
    ListCreateWorkspace, DetailWorkspace,
    ListProjectsByWorkspace,
    ListColumnsByProject,
    ListTasksByColumn
)
urlpatterns = [
    # Задачи
    path('tasks/', ListTask.as_view()),
    path('tasks/<int:pk>/', DetailTask.as_view()),
    path('columns/<int:column_id>/tasks/', ListTasksByColumn.as_view(), name='column-tasks'),

    # Колонки
    path('columns/', ListCreateColumn.as_view()),
    path('columns/<int:pk>/', DetailColumn.as_view()),
    path('projects/<int:project_id>/columns/', ListColumnsByProject.as_view(), name='project-columns'),

    # Проекты
    path('projects/', ListCreateProject.as_view()),
    path('projects/<int:pk>/', DetailProject.as_view()),
    path('workspaces/<int:workspace_id>/projects/', ListProjectsByWorkspace.as_view(), name='workspace-projects'),

    # Пространства
    path('workspaces/', ListCreateWorkspace.as_view()),
    path('workspaces/<int:pk>/', DetailWorkspace.as_view()),
]