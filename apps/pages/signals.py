from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import EnergyReading, Alert
from .utils import send_alert_notification

@receiver(post_save, sender=EnergyReading)
def check_instant_alerts(sender, instance, created, **kwargs):
    """
    Esta função é executada IMEDIATAMENTE após um novo EnergyReading ser salvo.
    """
    if created: # Executa apenas para novos registros
        # Exemplo de regra de alerta instantâneo:
        # Se o consumo total for maior que um limiar crítico (ex: 5 kWh em uma única leitura)
        CRITICAL_THRESHOLD_KWH = 5.0
        
        if instance.total_kwh_consumption and instance.total_kwh_consumption > CRITICAL_THRESHOLD_KWH:
            message = (
                f"Alerta Crítico: Consumo instantâneo de {instance.total_kwh_consumption:.2f} kWh detectado! "
                f"Um equipamento de alta potência pode ter sido ligado."
            )

            alert = Alert.objects.create(
                profile=instance.profile,
                user=instance.profile.user,
                alert_type='INSTANT_HIGH_CONSUMPTION',
                severity=Alert.AlertSeverityChoices.CRITICAL,
                message=message
            )
            send_alert_notification(alert)