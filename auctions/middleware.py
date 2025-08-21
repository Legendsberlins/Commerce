from django.shortcuts import redirect
from django.urls import reverse

class BlockSuperuserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow access to admin or static files
        admin_path = reverse('admin:index')
        if request.user.is_authenticated and request.user.is_superuser:
            if not request.path.startswith('/admin') and not request.path.startswith('/static'):
                from django.contrib.auth import logout
                logout(request)
                return redirect('login')  # Or show a 403 page if preferred

        return self.get_response(request)