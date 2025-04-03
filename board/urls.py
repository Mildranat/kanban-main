from django.urls import path
from . import views

app_name = 'board'

urlpatterns = [
    path('', views.home, name='home'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('organization/', views.organization_view, name='organization'),
    path('workspace/<int:workspace_id>/invite/', views.invite_member, name='invite_member'),
    path('workspace/create/', views.create_workspace, name='create_workspace'),
    path('accept-invite/<str:token>/', views.accept_invite, name='accept_invite'),
    path('workspace/<int:workspace_id>/', views.workspace_view, name='workspace'),
    path('notifications/mark_all_read/', views.mark_all_read, name='mark_all_read'),
    path('project/<int:project_id>/', views.board_view, name='project'),
    path('register/', views.register_request, name='register'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
]