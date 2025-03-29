from django.contrib import admin

from .models import Task, Column, Workspace, Project, Notification

admin.site.register(Task)
admin.site.register(Column)
admin.site.register(Workspace)
admin.site.register(Project)
admin.site.register(Notification)