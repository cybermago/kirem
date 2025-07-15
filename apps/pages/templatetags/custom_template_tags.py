# em home/templatetags/custom_template_tags.py

from django import template
from apps.pages.models import Alert

register = template.Library()

@register.filter
def alert_severity_color(alert):
    """Retorna uma classe de cor Bootstrap com base na severidade do alerta."""
    if alert.severity == Alert.AlertSeverityChoices.CRITICAL:
        return 'danger'
    elif alert.severity == Alert.AlertSeverityChoices.HIGH:
        return 'warning'
    elif alert.severity == Alert.AlertSeverityChoices.MEDIUM:
        return 'info'
    else: # LOW
        return 'secondary'

@register.filter
def alert_severity_icon(alert):
    """Retorna um ícone do Material Symbols com base na severidade do alerta."""
    if alert.severity == Alert.AlertSeverityChoices.CRITICAL:
        return 'error'
    elif alert.severity == Alert.AlertSeverityChoices.HIGH:
        return 'warning'
    elif alert.severity == Alert.AlertSeverityChoices.MEDIUM:
        return 'info'
    else: # LOW
        return 'notifications'