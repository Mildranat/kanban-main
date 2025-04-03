from django.db import models
from django.utils import timezone  
from django.utils.crypto import get_random_string

class Workspace(models.Model):
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='workspaces')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Пространство'
        verbose_name_plural = 'Пространства'

class Project(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

class Column(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='columns')
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Колонка'
        verbose_name_plural = 'Колонки'

    def __str__(self):
        return self.name

class Task(models.Model):
    column = models.ForeignKey(Column, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        
    def save(self, *args, **kwargs):
        if self.completed and not self.completed_at:
            self.completed_at = timezone.now()
            # Начисление очков за выполнение задачи
            member = OrganizationMember.objects.get(user=self.column.project.workspace.owner)
            MemberRating.objects.create(
                member=member,
                points=10  # Базовые очки за задачу
            )
        super().save(*args, **kwargs)
        
class Notification(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=[
        ('task_completed', 'Задача выполнена'),
        ('task_assigned', 'Задача назначена'),
        ('task_rejected', 'Задача отклонена')  
    ])
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey('Task', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'

    def __str__(self):
        return f"{self.get_type_display()} - {self.message[:50]}"
    

class OrganizationMember(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)  # Измените на ForeignKey
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)  # Добавьте связь с пространством
    role = models.CharField(max_length=50, choices=[
        ('owner', 'Владелец'),
        ('member', 'Сотрудник')
    ], default='member')

    def __str__(self):
        return f"{self.user.username} ({self.role})"

class MemberRating(models.Model):
    member = models.ForeignKey(OrganizationMember, on_delete=models.CASCADE, related_name='ratings')
    points = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-points']

class WorkspaceInvite(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    email = models.EmailField()
    token = models.CharField(max_length=50, unique=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = get_random_string(32)
        super().save(*args, **kwargs)