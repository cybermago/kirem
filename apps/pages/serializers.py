# Em apps/pages/serializers.py

from rest_framework import serializers
from .models import EnergyReading

class EnergyReadingSerializer(serializers.ModelSerializer):
    # Adicionamos um campo extra que não está no modelo, apenas para receber a chave da API
    # O `write_only=True` garante que este campo é usado para entrada, mas não é exibido na saída.
    api_key = serializers.UUIDField(write_only=True)

    class Meta:
        model = EnergyReading
        # Lista dos campos que o software Avalonia deve enviar.
        # Note que 'profile' não está aqui, pois será determinado pela api_key.
        fields = [
            'api_key',
            'reading_datetime',
            'total_kwh_consumption',
            'peak_kwh_consumption',
            'intermediate_kwh_consumption',
            'off_peak_kwh_consumption',
            'peak_demand_reading_kw',
            'off_peak_demand_reading_kw',
            'reactive_kvarh_consumption'
        ]
        # Define campos opcionais
        extra_kwargs = {
            'peak_kwh_consumption': {'required': False},
            'intermediate_kwh_consumption': {'required': False},
            'off_peak_kwh_consumption': {'required': False},
            'peak_demand_reading_kw': {'required': False},
            'off_peak_demand_reading_kw': {'required': False},
            'reactive_kvarh_consumption': {'required': False},
        }