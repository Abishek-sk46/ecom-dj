from django.shortcuts import redirect
from django.urls import reverse


class RedirectAuthenticatedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            paths_to_redirect = [reverse('blog:login'), reverse('blog:register')]

            if request.path in paths_to_redirect:
                return redirect(reverse('blog:index'))            
        response=self.get_response(request)
        return response
        

class RestrictUnauthenticatedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            paths_to_redirect = [reverse('blog:dashboard'), reverse('blog:logout')]

            if request.path in paths_to_redirect:
                return redirect(reverse('blog:login'))
            
        response=self.get_response(request)
        return response