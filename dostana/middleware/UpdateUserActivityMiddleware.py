from django.utils import timezone
from .models import UserActivity

class UpdateUserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Update the user's last_active timestamp
            UserActivity.objects.filter(user=request.user).update(last_active=timezone.now())
        
        response = self.get_response(request)
        return response
