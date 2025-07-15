from rest_framework.permissions import BasePermission
from .models import EnergyProfiles

class HasValidAPIKey(BasePermission):
    """
    Permissão que verifica se uma chave de API válida foi enviada no cabeçalho.
    """
    def has_permission(self, request, view):
        # O software Avalonia deve enviar a chave no cabeçalho 'X-API-KEY'
        api_key_str = request.META.get('HTTP_X_API_KEY')
        if not api_key_str:
            return False

        try:
            # Busca o perfil associado à chave de API
            profile = EnergyProfiles.objects.get(api_key=api_key_str)
            # Anexa o perfil ao objeto request para que a view possa usá-lo
            request.profile = profile
            return True
        except EnergyProfiles.DoesNotExist:
            return False