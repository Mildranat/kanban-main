from django.db.models.signals import post_save
from django.dispatch import receiver
from board.models import Task, Notification

@receiver(post_save, sender=Task)
def create_task_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.column.project.workspace.owner,
            type='task_assigned',
            message=f'Новая задача: "{instance.name}" в проекте "{instance.column.project.name}"',
            task=instance
        )
    elif instance.completed:
        Notification.objects.create(
            user=instance.column.project.workspace.owner,
            type='task_completed',
            message=f'Задача выполнена: "{instance.name}"',
            task=instance
        )