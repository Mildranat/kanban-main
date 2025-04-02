# board/context_processors.py
from .models import Workspace

def workspaces(request):
    if request.user.is_authenticated:
        return {'workspaces': Workspace.objects.filter(owner=request.user)}
    return {'workspaces': []}