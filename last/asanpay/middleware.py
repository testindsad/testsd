from django.conf import settings
from django.utils import timezone
from django.http import Http404
from django.middleware.csrf import CsrfViewMiddleware
from django.http import HttpResponseForbidden
from .models import BannedIP
from django.urls import resolve
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
class DisableCSRFMiddleware(CsrfViewMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if request.path.startswith('/admin/'):
            return None
        return super().process_view(request, callback, callback_args, callback_kwargs)
class VisitCountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the session already contains a visit count
        visit_count = request.session.get('visit_count', 0)
        
        # Increment the visit count and update the session
        request.session['visit_count'] = visit_count + 1/20
        
        # Update the last visit timestamp
        request.session['last_visit'] = str(timezone.now())

        response = self.get_response(request)
        return response
class BanIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        banned_ips = ['2a09:bac2:456:126e::1d6:115']  # Replace with the IP address you want to ban
        if request.META['REMOTE_ADDR'] in banned_ips:
            raise Http404('Page not found')
        response = self.get_response(request)
        return response


class IPBanMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
        if BannedIP.objects.filter(ip_address=user_ip).exists():
            return HttpResponseForbidden("Your IP address has been banned.")
        response = self.get_response(request)
        return response
    
    
class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Check if the user has an active session
        if request.user.is_authenticated:
            # Update the user's session data with the current URL
            request.session['last_visited_url'] = resolve(request.path_info).url_name

        return response