from rest_framework import serializers
from board.models import Task, Column, Project, Workspace
from django.contrib.auth.models import User

class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='column.project.workspace.owner.username')
    column = serializers.PrimaryKeyRelatedField(queryset=Column.objects.all())

    class Meta:
        model = Task
        fields = ('id', 'name', 'column', 'created_at', 'owner')

class ColumnSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Column
        fields = ('id', 'name', 'order', 'tasks')

class ProjectSerializer(serializers.ModelSerializer):
    columns = ColumnSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ('id', 'name', 'columns')

class WorkspaceSerializer(serializers.ModelSerializer):
    projects = ProjectSerializer(many=True, read_only=True)

    class Meta:
        model = Workspace
        fields = ('id', 'name', 'projects')

class UserSerializer(serializers.ModelSerializer):
    workspaces = WorkspaceSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'workspaces')