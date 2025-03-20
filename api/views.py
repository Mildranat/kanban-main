from rest_framework import generics
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from api import serializers
from board.models import Task, Column, Project, Workspace
from api.serializers import TaskSerializer, ColumnSerializer, ProjectSerializer, WorkspaceSerializer

# Задачи
class ListTask(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(column__project__workspace__owner=user)

    def perform_create(self, serializer):
        column_id = self.request.data.get('column')
        name = self.request.data.get('name')  # Проверь, получаешь ли name
        print(f"Column: {column_id}, Task Name: {name}")  # Логирование
        column = Column.objects.get(id=column_id)
        serializer.save(column=column)

class DetailTask(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(column__project__workspace__owner=user)
    
class ListTasksByColumn(generics.ListAPIView):
    serializer_class = TaskSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        column_id = self.kwargs['column_id']
        return Task.objects.filter(column_id=column_id, column__project__workspace__owner=self.request.user)

# Колонки
class ListCreateColumn(generics.ListCreateAPIView):
    serializer_class = ColumnSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Column.objects.filter(project__workspace__owner=user)

    def perform_create(self, serializer):
        project_id = self.request.data.get('project')
        project = Project.objects.get(id=project_id)
        serializer.save(project=project)

class ListColumnsByProject(generics.ListAPIView):
    serializer_class = ColumnSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return Column.objects.filter(project_id=project_id, project__workspace__owner=self.request.user)

class DetailColumn(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ColumnSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Column.objects.filter(project__workspace__owner=user)

# Проекты
class ListCreateProject(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(workspace__owner=user)

    def perform_create(self, serializer):
        workspace_id = self.request.data.get('workspace')
        workspace = Workspace.objects.get(id=workspace_id)
        serializer.save(workspace=workspace)

class DetailProject(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(workspace__owner=user)

# Пространства
class ListCreateWorkspace(generics.ListCreateAPIView):
    serializer_class = WorkspaceSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Workspace.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class DetailWorkspace(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkspaceSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Workspace.objects.filter(owner=user)

class ListProjectsByWorkspace(generics.ListAPIView):
    serializer_class = ProjectSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        workspace_id = self.kwargs['workspace_id']
        return Project.objects.filter(workspace_id=workspace_id, workspace__owner=self.request.user)