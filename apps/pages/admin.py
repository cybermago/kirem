# home/admin.py
from django.contrib import admin
from .models import KPI, Alert, BillingRecord, ConsumptionGoal, DeviceCatalog, DeviceUsagePattern, EnergyProfiles, EnergyQualityRecord, EnergyReading, EnergyTariff, HistoricalPredictionComparison, OptimizationSuggestion, PredictionModels, ProfileDevices, ConsumptionPredictions, ModelAccuracyScores, TariffFlagAdditive, UserPreferences
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

# Obtém o modelo de usuário ativo
User = get_user_model()

# --- Configuração do Admin para os modelos ---

@admin.register(DeviceCatalog)
class DeviceCatalogAdmin(admin.ModelAdmin):
    """
    Configuração do painel de administração para o modelo DeviceCatalog.
    """
    list_display = ('name', 'avg_kwh', 'procel_seal', 'icon')
    search_fields = ('name',) 
    list_filter = ('avg_kwh','procel_seal') 


@admin.register(EnergyProfiles)
class EnergyProfilesAdmin(admin.ModelAdmin):
    # CORREÇÃO: 'tariff_classification' renomeado para 'tariff_type'.
    list_display = ('name', 'user', 'user_type', 'subgroup', 'supply_type', 'tariff_type', 'classification', 'created_at') 
    search_fields = ('name', 'user__username', 'subgroup', 'classification', 'address_line1', 'city')
    # CORREÇÃO: 'tariff_classification' renomeado para 'tariff_type'.
    list_filter = ('created_at', 'user', 'subgroup', 'supply_type', 'tariff_type', 'classification', 'user_type', 'state')
    raw_id_fields = ('user', 'default_tariff') 


@admin.register(EnergyQualityRecord)
class EnergyQualityRecordAdmin(admin.ModelAdmin):
    """
    Configuração do painel de administração para o modelo EnergyQualityRecord.
    """
    # CORREÇÃO: 'record_date' -> 'record_datetime'. Adicionados 'record_type' e 'voltage_level'.
    list_display = (
        'profile',
        'record_datetime',
        'record_type',
        'voltage_level',
        'num_interruptions',
        'total_duration_interruptions_hours',
        'tariff_flag_applied',
    )
    list_filter = (
        'profile',
        'tariff_flag_applied',
        'record_datetime', # CORREÇÃO: Campo atualizado.
        'record_type',
    )
    search_fields = (
        'profile__name',
        'notes'
    )
    # CORREÇÃO: 'record_date' -> 'record_datetime'.
    date_hierarchy = 'record_datetime'
    raw_id_fields = ('profile',)

@admin.register(PredictionModels)
class PredictionModelsAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'last_trained', 'accuracy_score', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

@admin.register(ProfileDevices)
class ProfileDevicesAdmin(admin.ModelAdmin):
    """
    Configuração do painel de administração para o modelo ProfileDevices.
    """
    list_display = (
        'name', 
        'profile', 
        'device', 
        'quantity', 
        'hours_per_day', 
        'display_tempo_uso_semanal', # Usar um método para exibir
        'display_daily_kwh_consumption', # Usar um método para exibir
        'display_monthly_kwh_consumption', # Usar um método para exibir
        'display_annual_kwh_consumption'
    )
    search_fields = ('profile__name', 'device__name', 'name')
    list_filter = ('profile', 'device', 'last_updated')
    raw_id_fields = ('profile', 'device')

    fields = (
        'profile', 
        'device', 
        'name', 
        'quantity', 
        'hours_per_day', 
        'days_of_week', # Este é um ManyToMany, cuidado ao editar diretamente no admin sem um form customizado
        'tempo_uso_semanal', # Campo readonly
        'daily_kwh_consumption', # Campo readonly
        'monthly_kwh_consumption', # Campo readonly
        'annual_kwh_consumption',
        # 'last_updated', # Pode ser readonly ou excluído do fields
        # 'created_at',   # Pode ser readonly ou excluído do fields
    )

    readonly_fields = (
        'tempo_uso_semanal', 
        'daily_kwh_consumption', 
        'monthly_kwh_consumption',
        'annual_kwh_consumption',
        'last_updated',
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    # Métodos para exibir campos calculados na list_display
    @admin.display(description='Tempo Uso Semanal (horas)')
    def display_tempo_uso_semanal(self, obj):
        return f"{obj.tempo_uso_semanal:.2f} h" if obj.tempo_uso_semanal is not None else 'N/A'

    @admin.display(description='Consumo Diário (kWh)')
    def display_daily_kwh_consumption(self, obj):
        # Aqui, usamos o valor já salvo no objeto.
        return f"{obj.daily_kwh_consumption:.4f} kWh" if obj.daily_kwh_consumption is not None else 'N/A'

    @admin.display(description='Consumo Mensal (kWh)')
    def display_monthly_kwh_consumption(self, obj):
        # Aqui, usamos o valor já salvo no objeto.
        return f"{obj.monthly_kwh_consumption:.4f} kWh" if obj.monthly_kwh_consumption is not None else 'N/A'
    
    @admin.display(description='Consumo Anual (kWh)')
    def display_annual_kwh_consumption(self, obj):
        return f"{obj.annual_kwh_consumption:.4f} kWh" if obj.annual_kwh_consumption is not None else 'N/A'


@admin.register(ConsumptionPredictions)
class ConsumptionPredictionsAdmin(admin.ModelAdmin):
    """
    Configuração do painel de administração para o modelo ConsumptionPredictions.
    """
    list_display = ('profile_device', 'model', 'prediction_date','predicted_kwh', 'confidence_score', 'is_final')
    list_filter = ('prediction_date', 'model', 'is_final', 'profile_device__profile')
    search_fields = ('profile_device__name', 'profile_device__device__name', 'model__name')
    date_hierarchy = 'prediction_date'
    raw_id_fields = ('profile', 'profile_device', 'model')

@admin.register(ModelAccuracyScores)
class ModelAccuracyScoresAdmin(admin.ModelAdmin):
    """
    Configuração do painel de administração para o modelo ModelAccuracyScores.
    """
    list_display = ('model', 'profile', 'evaluation_date', 'mape', 'rmse', 'score', 'start_date', 'end_date')
    list_filter = ('model', 'profile', 'evaluation_date')
    search_fields = ('model__name', 'profile__name')
    date_hierarchy = 'evaluation_date'
    raw_id_fields = ('model', 'profile')
    fieldsets = (
        (None, {
            # CORREÇÃO: 'prediction_model' renomeado para 'model'.
            'fields': ('model', 'profile')
        }),
        ('Métricas de Acurácia', {
            'fields': ('evaluation_date', 'mape', 'rmse', 'score', 'start_date', 'end_date'), 
            'description': 'Detalhes das métricas de desempenho do modelo.'
        }),
    )

@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    """
    Configuração do painel de administração para o modelo KPI.
    """
    # CORREÇÃO: 'name' -> 'kpi_name'. Adicionado 'timeframe'.
    list_display = ('kpi_name', 'profile', 'kpi_type', 'timeframe', 'current_value', 'target_value', 'unit', 'is_active')
    list_filter = ('kpi_type', 'timeframe', 'profile','unit', 'is_active')
    # CORREÇÃO: 'name' -> 'kpi_name'.
    search_fields = ('kpi_name', 'description', 'profile__name')
    raw_id_fields = ('profile',) 


@admin.register(EnergyReading)
class EnergyReadingAdmin(admin.ModelAdmin):
    list_display = (
        'profile', 'reading_datetime', 'reading_period', 'total_kwh_consumption',
        'peak_kwh_consumption', 'intermediate_kwh_consumption', 'off_peak_kwh_consumption',
    )
    list_filter = ('reading_period', 'reading_datetime', 'profile')
    search_fields = ('profile__name', 'meter_number')
    date_hierarchy = 'reading_datetime'
    raw_id_fields = ('profile', 'profile_device', 'billing_record')

@admin.register(EnergyTariff)
class EnergyTariffAdmin(admin.ModelAdmin):
    # ATUALIZAÇÃO: Exibição mais completa para refletir a complexidade do modelo.
    list_display = (
        'name', 'tariff_type', 'is_active', 'start_date', 'end_date', 'cost_per_kwh', 
        'peak_energy_price', 'intermediate_energy_price', 'off_peak_energy_price'
    )
    list_filter = ('tariff_type', 'is_active', 'has_tiered_pricing')
    search_fields = ('name', 'description')
    date_hierarchy = 'start_date'

@admin.register(TariffFlagAdditive)
class TariffFlagAdditiveAdmin(admin.ModelAdmin):
    list_display = ('flag_type', 'additional_cost_per_100kwh', 'start_date', 'end_date')
    list_filter = ('flag_type', 'start_date')
    search_fields = ('flag_type', 'notes')
    date_hierarchy = 'start_date'


@admin.register(BillingRecord)
class BillingRecordAdmin(admin.ModelAdmin):
    list_display = (
        'profile', 'bill_number', 'invoice_date', 'due_date',
        'kwh_total_billed', 'total_cost', 'applied_tariff_flag',
        'energy_tariff_used',
        'previous_reading', 'current_reading', 'days_billed', 'meter_id'
    )
    list_filter = (
        'invoice_date', 'profile', 'applied_tariff_flag', 'energy_tariff_used__tariff_type', 'bill_type'
    )
    search_fields = ('profile__name', 'meter_id', 'bill_number')
    raw_id_fields = ('profile', 'energy_tariff_used')
    date_hierarchy = 'invoice_date'
    fieldsets = (
        ('Informações Gerais da Fatura', {
            'fields': (
                'profile', 'bill_type', 'bill_number', 'invoice_date', 'due_date',
                'start_period', 'end_period', 'days_billed', 'notes'
            )
        }),
        ('Detalhamento de Consumo e Custos', {
            'fields': (
                'kwh_total_billed', 'total_cost', 'energy_charge_total', 'demand_charge_total',
                'unit_price_kwh', 'tariff_unit_kwh',
                ('contracted_demand_peak_kw', 'contracted_demand_off_peak_kw'),
                ('billed_demand_peak_kw', 'billed_demand_off_peak_kw'),
                'availability_cost_value',
            )
        }),
        ('Leituras do Medidor', {
            'fields': ('meter_id', 'previous_reading', 'current_reading', 'meter_constant', 'next_reading_date')
        }),
        ('Tarifas e Bandeiras', {
            'fields': (
                'energy_tariff_used',
                'applied_tariff_flag', 'applied_tariff_flag_cost', 'flag_additional_cost_per_100kwh'
            )
        }),
        ('Tributos e Encargos Adicionais', {
            'fields': (
                ('icms_base', 'icms_aliquot', 'icms_value'),
                ('pis_base', 'pis_aliquot', 'pis_value'),
                ('cofins_base', 'cofins_aliquot', 'cofins_value'),
                ('cip_cost', 'meter_rental_cost', 'fine_cost', 'monetary_correction_cost', 'interest_cost')
            )
        }),
    )

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """
    Configuração do painel de administração para o modelo Alert.
    """
    list_display = ('profile', 'alert_type', 'severity', 'message', 'alert_date', 'is_read', 'is_resolved')
    list_filter = ('alert_type', 'severity', 'is_read', 'is_resolved', 'alert_date', 'profile')
    search_fields = ('message', 'profile__name', 'user__username', 'suggested_actions')
    date_hierarchy = 'alert_date'
    raw_id_fields = ('profile', 'user')
    fieldsets = (
        (None, {
            # CORREÇÃO: 'description' renomeado para 'message'.
            'fields': ('profile', 'user', 'alert_type', 'message', 'alert_date')
        }),
        ('Status e Ações', {
            'fields': ('severity', 'is_read', 'is_resolved', 'suggested_actions'), 
        }),
    )

@admin.register(ConsumptionGoal)
class ConsumptionGoalAdmin(admin.ModelAdmin):
    # ATUALIZAÇÃO: Exibição mais completa.
    list_display = ('name', 'profile', 'goal_type', 'target_value', 'alert_threshold_percentage', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active','goal_type', 'profile')
    search_fields = ('name', 'profile__name', 'description')
    date_hierarchy = 'start_date'
    raw_id_fields = ('profile',)

@admin.register(DeviceUsagePattern)
class DeviceUsagePatternAdmin(admin.ModelAdmin):
    list_display = ('profile_device', 'day_of_week', 'start_time', 'end_time', 'kwh_consumption', 'intensity_factor')
    list_filter = ('day_of_week', 'profile_device__profile__name')
    # CORREÇÃO: Caminhos de pesquisa ajustados para os campos corretos.
    search_fields = ('profile_device__name', 'profile_device__device__name', 'profile_device__profile__name')
    raw_id_fields = ('profile_device',)

@admin.register(HistoricalPredictionComparison)
class HistoricalPredictionComparisonAdmin(admin.ModelAdmin):
    list_display = ('profile', 'comparison_date', 'prediction', 'actual_kwh', 'deviation_percentage', 'error_kwh')
    list_filter = ('comparison_date', 'profile__name', 'prediction__model__name')
    # ATUALIZAÇÃO: Campo de pesquisa e raw_id adicionados para consistência.
    search_fields = ('profile__name', 'prediction__profile_device__name')
    date_hierarchy = 'comparison_date'
    raw_id_fields = ('profile', 'prediction',)

@admin.register(OptimizationSuggestion)
class OptimizationSuggestionAdmin(admin.ModelAdmin):
    list_display = ('profile','title','estimated_savings_kwh', 'estimated_savings_kwh_per_month', 'estimated_savings_money','is_implemented', 'suggested_at','category', 'impact_level', )
    list_filter = ('category', 'impact_level')
    search_fields = ('title', 'description')
    date_hierarchy = 'suggested_at'
    raw_id_fields = ('profile',)


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    """
    Configuração do painel de administração para o modelo UserPreferences.
    """
    # ATUALIZAÇÃO: Exibição completa de todas as preferências.
    list_display = ('user', 'theme_preference', 'notification_frequency', 'report_format_preference', 'receive_marketing_emails')
    list_filter = ('theme_preference', 'notification_frequency', 'report_format_preference')
    search_fields = ('user__username',)
    raw_id_fields = ('user',)
