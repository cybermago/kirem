from django.apps import AppConfig


class PagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pages"

    def ready(self):
        # Importa os sinais para que eles sejam registrados quando o app carregar
        import apps.pages.signals