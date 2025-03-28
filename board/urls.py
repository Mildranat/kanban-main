from django.urls import path
from . import views

app_name = 'board'

urlpatterns = [
    path('', views.home, name='home'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('workspace/<int:workspace_id>/', views.workspace_view, name='workspace'),
    path('project/<int:project_id>/', views.board_view, name='project'),
    path('register/', views.register_request, name='register'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
]