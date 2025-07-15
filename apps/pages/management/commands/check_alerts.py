from django.core.management.base import BaseCommand
from apps.pages.models import EnergyProfiles
from apps.pages.utils import check_and_create_alerts_for_profile

class Command(BaseCommand):
    help = 'Verifica todas as condições de alerta e cria alertas para perfis de energia.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando verificação de alertas...'))
        
        profiles = EnergyProfiles.objects.filter(user__is_active=True)
        if not profiles.exists():
            self.stdout.write('Nenhum perfil de energia ativo encontrado.')
            return

        for profile in profiles:
            try:
                check_and_create_alerts_for_profile(profile)
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Erro ao processar perfil {profile.name}: {e}'))

        self.stdout.write(self.style.SUCCESS('Verificação de alertas concluída.'))