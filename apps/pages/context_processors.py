from apps.pages.models import Alert

def notifications_context(request):
    if request.user.is_authenticated:
        # Busca os 5 alertas mais recentes para o usuário logado
        recent_alerts = Alert.objects.filter(user=request.user).order_by('-triggered_at')[:5]
        
        # Conta quantos desses (ou de todos) não foram lidos
        unread_alerts_count = Alert.objects.filter(user=request.user, is_read=False).count()
        
        return {
            'recent_alerts': recent_alerts,
            'unread_alerts_count': unread_alerts_count,
        }
    return {}