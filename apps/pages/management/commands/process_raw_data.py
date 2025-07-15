# Em home/management/commands/process_raw_data.py

from django.core.management.base import BaseCommand
from django.db.models import Sum, Avg
from apps.pages.models import RawSensorData, EnergyReading, EnergyProfiles

class Command(BaseCommand):
    help = 'Processa dados brutos dos sensores e os agrega na tabela EnergyReading.'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando processo de agregação de dados brutos...')

        # Busca todos os perfis que têm dados brutos não processados
        profiles_to_process = EnergyProfiles.objects.filter(
            raw_sensor_data__processed=False
        ).distinct()

        for profile in profiles_to_process:
            # Pega todos os dados não processados para este perfil
            raw_data_queryset = RawSensorData.objects.filter(profile=profile, processed=False)
            
            # Lógica de agregação (exemplo simples: calcular kWh a partir de Watts/hora)
            # Potência Média (W) * Tempo (h) / 1000 = kWh
            # Supondo que estamos processando dados da última hora
            total_active_power_ws = raw_data_queryset.aggregate(total=Sum('active_power'))['total'] or 0
            kwh_consumed_in_period = (total_active_power_ws / len(raw_data_queryset)) * 1 / 1000 if len(raw_data_queryset) > 0 else 0

            # Cria um único registro sumarizado em EnergyReading
            EnergyReading.objects.create(
                profile=profile,
                user=profile.user,
                total_kwh_consumption=kwh_consumed_in_period,
                reading_period=EnergyReading.ReadingGranularityChoices.HORARIA,
                # ... outros campos agregados como tensão média, etc.
            )
            
            # Marca os dados brutos como processados para não contá-los novamente
            raw_data_queryset.update(processed=True)
            self.stdout.write(f'Dados agregados para o perfil: {profile.name}')

        self.stdout.write(self.style.SUCCESS('Agregação concluída.'))