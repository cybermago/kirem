# home/middleware.py (exemplo conceitual)

from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

class RedirectAuthenticatedUsersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Define as URLs para as quais este middleware deve agir
        self.index = reverse('home')
        self.dashboard_url = reverse('dashboard')

    def __call__(self, request):
        # Verifica se o usuário está autenticado E a requisição é para a página pública
        if request.user.is_authenticated and request.path == self.index:
            # Redireciona para o dashboard
            return redirect(self.dashboard_url)
        
        # Continua o processamento normal da requisição
        response = self.get_response(request)
        return response