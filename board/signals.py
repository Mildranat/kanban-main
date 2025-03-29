from django.db.models.signals import post_save
from django.dispatch import receiver
from board.models import Task, Notification

@receiver(post_save, sender=Task)
def create_task_notification(sender, instance, created, **kwargs):
    if created:
        # Notification for task assignment
        Notification.objects.create(
            user=instance.column.project.workspace.owner,
            type='task_assigned',
            message=f'Вам назначена новая задача "{instance.name}"',
            task=instance
        )
    elif instance.column.name == "Завершено":
        # Notification for task completion
        Notification.objects.create(
            user=instance.column.project.workspace.owner,
            type='task_completed',
            message=f'Задача "{instance.name}" была выполнена',
            task=instance
        )