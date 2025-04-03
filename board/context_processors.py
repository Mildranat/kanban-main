# board/context_processors.py
from .models import Workspace

def workspaces(request):
    if request.user.is_authenticated:
        owned = Workspace.objects.filter(owner=request.user)
        member_of = Workspace.objects.filter(
            organizationmember__user=request.user
        )
        return {'workspaces': (owned | member_of).distinct()}
    return {'workspaces': []}