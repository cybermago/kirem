# home/forms.py
from decimal import Decimal, InvalidOperation
from django import forms

from apps.pages.admin import User
from .models import (KPI, Alert, BillTypeChoices, BillingRecord, ConsumptionGoal, ConsumptionPredictions, 
DeviceCatalog, DeviceUsagePattern, EnergyProfiles, EnergyQualityRecord, EnergyReading, EnergyTariffTypeChoices, 
HistoricalPredictionComparison, EnergyTariff, ModelAccuracyScores, OptimizationSuggestion, PredictionModels, 
ProfileDevices, SupplyTypeChoices, TariffFlagAdditive, TariffFlagTypeChoices, UserPreferences, DayOfWeekChoices)


class DeviceCatalogForm(forms.ModelForm):
    days_of_week = forms.MultipleChoiceField(
        choices=DayOfWeekChoices.choices,
        widget=forms.SelectMultiple(attrs={'class': 'form-control selectpicker', 'multiple': 'multiple', 'data-live-search': 'true', 'title': 'Selecione os dias...'}), # <-- Mudança aqui
        required=False,
        label="Dias da Semana de Uso"
    )
    """
    Formulário para criar e atualizar entradas do DeviceCatalog.
    Estilizado com classes do Material Dashboard / Bootstrap 5.
    """
    class Meta:
        model = DeviceCatalog
        fields = ['name', 'icon', 'avg_kwh', 'procel_seal', 'categoria','potencia_nominal', 'tensao',  'marca'] 
        labels = {
            'name': 'Nome do Dispositivo',
            'icon': 'URL do Ícone (opcional)',
            'avg_kwh': 'Consumo Médio (kWh/dia)',
            'procel_seal': 'Selo Procel (A, B, C...)', 
            'categoria': '',
            'potencia_nominal': '',
            'tensao': '',
            'marca': '',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Geladeira, Lâmpada LED', 'required': True}),
            'icon': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Ex: [https://exemplo.com/icone.png](https://exemplo.com/icone.png)'}),
            'avg_kwh': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'placeholder': 'Ex: 0.5000', 'min': '0.0001','readonly': 'readonly'}),
            'procel_seal': forms.Select(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'potencia_nominal': forms.Select(attrs={'class': 'form-control'}),
            'tensao': forms.Select(attrs={'class': 'form-control'}),
            'marca': forms.Select(attrs={'class': 'form-control'}), # Novo widget para marca

        
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Se o objeto já existe, preenche o campo days_of_week
        if self.instance.pk and self.instance.days_of_week:
            self.initial['days_of_week'] = self.instance.days_of_week.split(',')

        # Adiciona classes CSS a todos os Selects (Dropdowns) para estilização do Material Dashboard
        for field_name in ['procel_seal', 'categoria', 'potencia_nominal', 'tensao', 'marca']:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({'class': 'form-control'})


    def clean(self):
        cleaned_data = super().clean()

        potencia_nominal_str = cleaned_data.get('potencia_nominal')
        calculated_avg_kwh = None

        # --- Cálculo de avg_kwh (para o catálogo, baseado apenas na potência nominal) ---
        potencia_nominal = None
        try:
            if potencia_nominal_str and potencia_nominal_str != 'OUTRO':
                potencia_nominal = Decimal(potencia_nominal_str)
        except InvalidOperation:
            self.add_error('potencia_nominal', 'Valor de potência nominal inválido para cálculo.')

        if potencia_nominal is not None:
            # Calcula kWh/dia assumindo 24 horas de uso para o catálogo
            # Este é um valor teórico/máximo para o dispositivo em si.
            calculated_avg_kwh = (potencia_nominal / Decimal('1000')) * Decimal('24')
            calculated_avg_kwh = round(calculated_avg_kwh, 4)

        cleaned_data['avg_kwh'] = calculated_avg_kwh

        return cleaned_data
    
class ReportGeneratorForm(forms.Form):
    METRIC_CHOICES = [
        ('total_consumption', 'Consumo Total (kWh)'),
        ('total_cost', 'Custo Total (R$)'),
        ('daily_average', 'Média Diária (kWh)'),
        ('device_breakdown', 'Consumo por Dispositivo'),
        ('quality_interruptions', 'Interrupções de Energia'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('csv', 'CSV'),
    ]

    profile = forms.ModelChoiceField(
        queryset=EnergyProfiles.objects.none(), 
        label="Selecione o Perfil",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        label="Data de Início",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        label="Data de Fim",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    metrics = forms.MultipleChoiceField(
        label="Métricas a Incluir",
        choices=METRIC_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )
    format = forms.ChoiceField(
        label="Formato do Arquivo",
        choices=FORMAT_CHOICES,
        widget=forms.RadioSelect
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile'].queryset = EnergyProfiles.objects.filter(user=user)


class EnergyProfilesForm(forms.ModelForm):
    """
    Formulário para criar e atualizar perfis de energia.
    Estilizado com classes do Material Dashboard / Bootstrap 5.
    """

    # default_tariff will be populated dynamically or can be left as is if all tariffs are options
    default_tariff = forms.ModelChoiceField(
        queryset=EnergyTariff.objects.all(),
        label='Tarifa Padrão',
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        empty_label="Nenhuma Tarifa Definida"
    )

    class Meta:
        model = EnergyProfiles
        fields = [
            'name', 'user_type', 'description', 'subgroup', 'voltage_group', 
            'supply_type', 'tariff_type', 'nominal_voltage', 'classification', 
            'subclass', 'default_tariff', 'address_line1', 'address_line2', 
            'city', 'state' # Removed zip_code and country as per latest models.py
        ]
        labels = {
            'name': 'Nome do Perfil',
            'user_type': 'Classificação do Cliente', # Updated label based on models.py help_text
            'description': 'Descrição',
            'subgroup': 'Subgrupo (e.g., B1 - Residencial)',
            'voltage_group': 'Grupo de Tensão (Ex: B)',
            'supply_type': 'Tipo de Fornecimento',
            'tariff_type': 'Classificação Tarifária', # Renamed from tariff_classification
            'nominal_voltage': 'Tensão Nominal',
            'classification': 'Classificação do Consumidor',
            'subclass': 'Subclasse',
            'default_tariff': 'Tarifa Padrão',
            'address_line1': 'Endereço Linha 1',
            'address_line2': 'Endereço Linha 2',
            'city': 'Cidade',
            'state': 'Estado',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'subgroup': forms.Select(attrs={'class': 'form-control'}),
            'voltage_group': forms.TextInput(attrs={'class': 'form-control'}), # Changed from Select to TextInput as it's CharField in model
            'supply_type': forms.Select(attrs={'class': 'form-control'}),
            'tariff_type': forms.Select(attrs={'class': 'form-control'}), # Renamed
            'nominal_voltage': forms.Select(attrs={'class': 'form-control'}),
            'classification': forms.Select(attrs={'class': 'form-control'}),
            'subclass': forms.Select(attrs={'class': 'form-control'}), # Changed from TextInput to Select
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['user_type'].choices = EnergyProfiles.ClientClassificationChoices.choices
        self.fields['subgroup'].choices = EnergyProfiles.SubgroupChoices.choices
        self.fields['supply_type'].choices = SupplyTypeChoices.choices
        self.fields['nominal_voltage'].choices = EnergyProfiles.NominalVoltageChoices.choices
        self.fields['classification'].choices = EnergyProfiles.ClassificationChoices.choices
        self.fields['subclass'].choices = EnergyProfiles.SubclassChoices.choices
        self.fields['tariff_type'].choices = EnergyTariffTypeChoices.choices 


        if 'default_tariff' in self.fields:
            self.fields['default_tariff'].queryset = EnergyTariff.objects.all()
        

class ProfileDevicesForm(forms.ModelForm):
    """
    Formulário para associar dispositivos a um perfil de energia.
    Estilizado com classes do Material Dashboard / Bootstrap 5.
    """
    days_of_week = forms.MultipleChoiceField(
        choices=DayOfWeekChoices.choices,
        widget=forms.SelectMultiple(attrs={'class': 'form-control selectpicker', 'multiple': 'multiple', 'data-live-search': 'true', 'title': 'Selecione os dias...'}),
        required=False,
        label="Dias da Semana de Uso"
    )
    class Meta:
        model = ProfileDevices
        fields = ['profile', 'name', 'device', 'quantity', 'hours_per_day', 'days_of_week', 'vida_util_estimativa']
        labels = {
            'profile': 'Perfil de Energia',
            'name': 'Nome',
            'device': 'Dispositivo',
            'quantity': 'Quantidade',
            'hours_per_day': 'Horas de Uso Diário',
            'days_of_week': 'Dias da Semana de Uso',
            'tempo_uso_semanal': 'Tempo de Uso Semanal (horas)',
            'consumption_kwh_per_day': 'Consumo Diário Calculado (kWh/dia - deste dispositivo no perfil)',
            'vida_util_estimativa': 'Vida Útil Estimada (anos)'
        }
        widgets = {
            'profile': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Geladeira da Cozinha'}),
            'device': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'required': True, 'placeholder': 'Número de unidades'}),
            'hours_per_day': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0, 'max': 24, 'required': True, 'placeholder': 'Horas por dia'}),
            'tempo_uso_semanal': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Horas por semana', 'readonly': 'readonly'}),
            'consumption_kwh_per_day': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'placeholder': 'Ex: 0.5000', 'min': '0.0001', 'readonly': 'readonly'}),
            'vida_util_estimativa': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Em anos'}),
        }
    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop('profile', None) # Guarda a instância do perfil
        super().__init__(*args, **kwargs)
        self.fields['device'].queryset = DeviceCatalog.objects.all()
        # Se um perfil for passado, o campo 'profile' deve ser inicializado ou oculto
        if self.profile:
            self.initial['profile'] = self.profile.pk
            # Pode-se desabilitar ou ocultar o campo 'profile' se ele for definido pela URL
            self.fields['profile'].widget = forms.HiddenInput()
            # self.fields['profile'].disabled = True # Ou desabilitar para exibição mas não edição

        # Adiciona classes CSS a todos os campos para estilização do Material Dashboard
        for field_name in self.fields:
            if isinstance(self.fields[field_name].widget, (forms.TextInput, forms.NumberInput, forms.Textarea, forms.Select)):
                attrs = self.fields[field_name].widget.attrs
                if 'class' in attrs:
                    if 'form-control' not in attrs['class']:
                        attrs['class'] += ' form-control'
                else:
                    attrs['class'] = 'form-control'
            # Lidar com MultipleChoiceField que usa SelectMultiple
            elif isinstance(self.fields[field_name].widget, forms.SelectMultiple):
                attrs = self.fields[field_name].widget.attrs
                if 'class' not in attrs or 'selectpicker' not in attrs['class']: # Assume que selectpicker já tem form-control
                    attrs['class'] = 'form-control selectpicker' # Garante que tem form-control

    def clean_days_of_week(self):
        days_of_week = self.cleaned_data.get('days_of_week')
        if days_of_week:
            return ",".join(days_of_week) # Converte a lista para string separada por vírgulas
        return ""

    def clean(self):
        cleaned_data = super().clean()
        
        device = cleaned_data.get('device')
        quantity = cleaned_data.get('quantity')
        hours_per_day = cleaned_data.get('hours_per_day')
        
        # Campos que o frontend pode ou não preencher, mas são calculados ou essenciais
        # tempo_uso_semanal e consumption_kwh_per_day são calculados no frontend e devem vir no POST
        # Se não vierem, a validação do formulário ou o save pode falhar.
        tempo_uso_semanal = cleaned_data.get('tempo_uso_semanal')
        consumption_kwh_per_day = cleaned_data.get('consumption_kwh_per_day')
        
        # Realizar o cálculo se os valores necessários estiverem presentes e forem válidos
        if device and quantity is not None and hours_per_day is not None:
            try:
                # Obter avg_kwh do DeviceCatalog
                device_avg_kwh_per_day_catalog = device.avg_kwh if device.avg_kwh else Decimal('0.0')

                if device_avg_kwh_per_day_catalog and device_avg_kwh_per_day_catalog > 0:
                    # Cálculo do consumo diário para este perfil
                    # consumption_kwh_per_day = quantidade * hours_per_day * (deviceAvgKwhFromCatalog / 24)
                    consumption_per_hour = device_avg_kwh_per_day_catalog / Decimal('24')
                    calculated_consumption = Decimal(quantity) * Decimal(hours_per_day) * consumption_per_hour
                    cleaned_data['consumption_kwh_per_day'] = round(calculated_consumption, 4)

                    # Cálculo do tempo de uso semanal
                    calculated_tempo_uso_semanal = Decimal(hours_per_day) * len(self.cleaned_data.get('days_of_week', []))
                    cleaned_data['tempo_uso_semanal'] = round(calculated_tempo_uso_semanal, 2)
                else:
                    # Se avg_kwh for 0 ou None no catálogo, defina consumo como 0
                    cleaned_data['consumption_kwh_per_day'] = Decimal('0.0')
                    cleaned_data['tempo_uso_semanal'] = Decimal('0.0')
            except (TypeError, ValueError, InvalidOperation) as e:
                self.add_error(None, f"Erro no cálculo de consumo: {e}")
                # Defina valores padrão ou nulos para evitar erros no banco se o cálculo falhar
                cleaned_data['consumption_kwh_per_day'] = Decimal('0.0')
                cleaned_data['tempo_uso_semanal'] = Decimal('0.0')
        else:
            # Se faltarem dados essenciais, garanta que os campos calculados sejam nulos ou 0
            cleaned_data['consumption_kwh_per_day'] = Decimal('0.0')
            cleaned_data['tempo_uso_semanal'] = Decimal('0.0')

        return cleaned_data

class KPIForm(forms.ModelForm):
    """
    Formulário para criar e atualizar KPIs.
    CORRIGIDO: Alinhado com o modelo KPI.
    """
    class Meta:
        model = KPI
        fields = ['profile', 'kpi_name', 'kpi_type', 'timeframe', 'description', 'unit', 'target_value', 'is_active']
        labels = {
            'profile': 'Perfil Associado',
            'kpi_name': 'Nome do KPI',
            'kpi_type': 'Tipo de KPI',
            'timeframe': 'Período de Tempo',
            'description': 'Descrição',
            'unit': 'Unidade de Medida',
            'target_value': 'Valor Alvo (opcional)',
            'is_active': 'KPI Ativo?',
        }
        widgets = {
            'profile': forms.Select(attrs={'class': 'form-control'}),
            # CORREÇÃO: 'name' -> 'kpi_name'
            'kpi_name': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'kpi_type': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'timeframe': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detalhes sobre o KPI'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'target_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ex: 10.50'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None) 
        super().__init__(*args, **kwargs)
        if self.request and self.request.user.is_authenticated:
            if 'profile' in self.fields:
                self.fields['profile'].queryset = EnergyProfiles.objects.filter(user=self.request.user)
        else:
            if 'profile' in self.fields:
                self.fields['profile'].queryset = EnergyProfiles.objects.none() # Nenhuma opção disponível


class EnergyReadingForm(forms.ModelForm):
    """
    Formulário para registrar leituras de consumo de energia.
    """
    class Meta:
        model = EnergyReading
        fields = [
            'profile', 'profile_device', 'billing_record', 'reading_datetime', 'meter_number',
            'reading_period',  # Nome do campo correto conforme o modelo
            'measurement_type',
            'total_kwh_consumption',
            'peak_kwh_consumption',
            'intermediate_kwh_consumption',
            'off_peak_kwh_consumption',
            'peak_demand_reading_kw',
            'off_peak_demand_reading_kw',
            'reactive_kvarh_consumption',
        ]
        labels = {
            'profile': 'Perfil de Energia',
            'profile_device': 'Dispositivo do Perfil (Opcional)',
            'billing_record': 'Fatura Associada (Opcional)',
            'reading_datetime': 'Data e Hora da Leitura',
            'meter_number': 'Número do Medidor',
            'reading_period': 'Periodo da Leitura',
            'measurement_type': 'Tipo de Medição',
            'total_kwh_consumption': 'Consumo Total (kWh)',
            'peak_kwh_consumption': 'Consumo na Ponta (kWh)',
            'intermediate_kwh_consumption': 'Consumo Intermediário (kWh)',
            'off_peak_kwh_consumption': 'Consumo Fora de Ponta (kWh)',
            'peak_demand_reading_kw': 'Demanda na Ponta (kW)',
            'off_peak_demand_reading_kw': 'Demanda Fora de Ponta (kW)',
            'reactive_kvarh_consumption': 'Consumo Reativo (kVARh)',
        }
        widgets = {
            'profile': forms.Select(attrs={'class': 'form-control'}),
            'profile_device': forms.Select(attrs={'class': 'form-control'}),
            'billing_record': forms.Select(attrs={'class': 'form-control'}),
            'reading_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'meter_number': forms.TextInput(attrs={'class': 'form-control'}),
            'reading_period': forms.Select(attrs={'class': 'form-control'}),
            'measurement_type': forms.Select(attrs={'class': 'form-control'}),
            'total_kwh_consumption': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'peak_kwh_consumption': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'intermediate_kwh_consumption': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'off_peak_kwh_consumption': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'peak_demand_reading_kw': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'off_peak_demand_reading_kw': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'reactive_kvarh_consumption': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        # Pega o 'request' que a view enviou e o remove dos argumentos
        # para que o construtor pai não o veja e não gere erro.
        request = kwargs.pop('request', None) 
        
        # Chama o construtor original da classe pai
        super().__init__(*args, **kwargs)
        
        # Agora, com o 'request' em mãos, podemos filtrar os campos do formulário
        # para mostrar apenas as opções relevantes para o usuário logado.
        if request and request.user.is_authenticated:
            user_profiles = EnergyProfiles.objects.filter(user=request.user)
            self.fields['profile'].queryset = user_profiles
            # Filtra os dispositivos e faturas com base nos perfis do usuário
            self.fields['profile_device'].queryset = ProfileDevices.objects.filter(profile__in=user_profiles)
            self.fields['billing_record'].queryset = BillingRecord.objects.filter(profile__in=user_profiles)
        else:
            # Se não houver usuário, não mostra nenhuma opção.
            self.fields['profile'].queryset = EnergyProfiles.objects.none()
            self.fields['profile_device'].queryset = ProfileDevices.objects.none()
            self.fields['billing_record'].queryset = BillingRecord.objects.none()


class PredictionModelsForm(forms.ModelForm):
    """
    Formulário completo para gerenciar Modelos de Previsão e seus hiperparâmetros.
    """
    class Meta:
        model = PredictionModels
        # ATUALIZAÇÃO: Adicionados todos os novos campos de configuração
        fields = [
            'name', 'description', 'model_type', 'is_active', 'data_source',
            'default_forecast_horizon', 'yearly_seasonality', 'weekly_seasonality',
            'daily_seasonality', 'seasonality_mode', 'include_brazil_holidays',
            'additional_params', 'model_file'
        ]
        labels = {
            'name': 'Nome do Modelo',
            'description': 'Descrição do Modelo',
            'model_type': 'Tipo de Algoritmo',
            'is_active': 'Ativo?',
            'data_source': 'Fonte de Dados para Treinamento',
            'default_forecast_horizon': 'Horizonte de Previsão (dias)',
            'yearly_seasonality': 'Considerar Sazonalidade Anual?',
            'weekly_seasonality': 'Considerar Sazonalidade Semanal?',
            'daily_seasonality': 'Considerar Sazonalidade Diária?',
            'seasonality_mode': 'Modo de Sazonalidade (Prophet)',
            'include_brazil_holidays': 'Incluir Feriados Brasileiros?',
            'additional_params': 'Parâmetros Adicionais (JSON)',
            'model_file': 'Arquivo do Modelo (para tipo Upload)',
            'accuracy_score': 'Última Pontuação de Acurácia', # <-- NOVO
            'last_accuracy_score': 'Detalhes da Acurácia (JSON)', # <-- NOVO
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'model_type': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'data_source': forms.Select(attrs={'class': 'form-control'}),
            'default_forecast_horizon': forms.NumberInput(attrs={'class': 'form-control'}),
            'yearly_seasonality': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'weekly_seasonality': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'daily_seasonality': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'seasonality_mode': forms.Select(attrs={'class': 'form-control'}),
            'include_brazil_holidays': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'additional_params': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ex: {"changepoint_prior_scale": 0.05}'}),
            'model_file': forms.FileInput(attrs={'class': 'form-control'}),
            'accuracy_score': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), # <-- NOVO
            'last_accuracy_score': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'readonly': 'readonly'}), # <-- NOVO
        }


class EnergyTariffForm(forms.ModelForm):
    """
    Formulário para criar e atualizar tarifas de energia.
    CORRIGIDO: Adicionados campos de ultrapassagem de demanda e precificação por faixa.
    """
    class Meta:
        model = EnergyTariff
        # CORREÇÃO: Adicionados campos faltantes.
        fields = [
            'name', 'description', 'tariff_type', 'start_date', 'end_date', 'is_active',
            'cost_per_kwh', 'peak_energy_price', 'intermediate_energy_price', 'off_peak_energy_price',
            'peak_demand_charge', 'off_peak_demand_charge', 'peak_demand_overflow_charge',
            'off_peak_demand_overflow_charge', 'has_tiered_pricing', 'availability_cost_kwh_franchise',
            'tax_icms_aliquot', 'pis_aliquot', 'cofins_aliquot',
        ]
        labels = {
            'name': 'Nome da Tarifa',
            'description': 'Descrição',
            'tariff_type': 'Tipo de Tarifa',
            'start_date': 'Data de Início',
            'end_date': 'Data de Fim',
            'is_active': 'Ativa?',
            'cost_per_kwh': 'Custo por kWh (R$/kWh) (Convencional)',
            'peak_energy_price': 'Preço kWh na Ponta (R$/kWh)',
            'intermediate_energy_price': 'Preço kWh Intermediário (R$/kWh)',
            'off_peak_energy_price': 'Preço kWh Fora de Ponta (R$/kWh)',
            'peak_demand_charge': 'Custo Demanda na Ponta (R$/kW)',
            'off_peak_demand_charge': 'Custo Demanda Fora de Ponta (R$/kW)',
            'peak_demand_overflow_charge': 'Custo Ultrapassagem Demanda Ponta (R$/kW)',
            'off_peak_demand_overflow_charge': 'Custo Ultrapassagem Demanda Fora Ponta (R$/kW)',
            'has_tiered_pricing': 'Usa Precificação por Faixa?',
            'availability_cost_kwh_franchise': 'Franquia Custo Disponibilidade (kWh)',
            'tax_icms_aliquot': 'Alíquota ICMS (%)',
            'pis_aliquot': 'Alíquota PIS (%)',
            'cofins_aliquot': 'Alíquota COFINS (%)',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tariff_type': forms.Select(attrs={'class':'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control datepicker', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control datepicker', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cost_per_kwh': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'min': 0}),
            'peak_energy_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'min': 0}),
            'intermediate_energy_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'min': 0}),
            'off_peak_energy_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'min': 0}),
            'peak_demand_charge': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'min': 0}),
            'off_peak_demand_charge': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'min': 0}),
            # CORREÇÃO: Widgets para os novos campos.
            'peak_demand_overflow_charge': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'min': 0}),
            'off_peak_demand_overflow_charge': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'min': 0}),
            'has_tiered_pricing': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'availability_cost_kwh_franchise': forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': 0}),
            'tax_icms_aliquot': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'min': 0, 'max': 100}),
            'pis_aliquot': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'min': 0, 'max': 100}),
            'cofins_aliquot': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'min': 0, 'max': 100}),
        }


class TariffFlagAdditiveForm(forms.ModelForm):
    """
    Formulário para registrar os custos adicionais das bandeiras tarifárias.
    CORRIGIDO: Adicionado campo de notas.
    """
    class Meta:
        model = TariffFlagAdditive
        
        fields = ['flag_type', 'additional_cost_per_100kwh', 'start_date', 'end_date', 'notes']
        labels = {
            'flag_type': 'Tipo de Bandeira Tarifária',
            'additional_cost_per_100kwh': 'Custo Adicional por 100 kWh (R$)',
            'start_date': 'Data de Início da Validade',
            'end_date': 'Data de Fim da Validade (opcional)',
            'notes': 'Observações',
        }
        widgets = {
            'flag_type': forms.Select(attrs={'class': 'form-control'}),
            'additional_cost_per_100kwh': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control datepicker', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control datepicker', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class EnergyQualityRecordForm(forms.ModelForm):
    """
    Formulário para registrar a qualidade de energia.
    CORRIGIDO: Sincronizado com os campos e tipos do modelo.
    """
    class Meta:
        model = EnergyQualityRecord
        # CORREÇÃO: 'record_date' -> 'record_datetime'. Adicionados 'record_type' e 'voltage_level'.
        fields = [
            'profile', 'record_datetime', 'record_type', 'voltage_level',
            'num_voltage_fluctuations', 'avg_voltage_variation', 'thd_voltage', 'thd_current',
            'num_interruptions', 'total_duration_interruptions_hours', 'tariff_flag_applied', 'notes',
        ]
        labels = {
            'profile': 'Perfil de Energia',
            'record_datetime': 'Data e Hora do Registro',
            'record_type': 'Tipo de Evento',
            'voltage_level': 'Nível de Tensão Medido (V)',
            'num_voltage_fluctuations': 'Número de Flutuações de Tensão',
            'avg_voltage_variation': 'Variação Média da Tensão (%)',
            'thd_voltage': 'Distorção Harmônica de Tensão (THD-V %)',
            'thd_current': 'Distorção Harmônica de Corrente (THD-I %)',
            'num_interruptions': 'Número de Interrupções',
            'total_duration_interruptions_hours': 'Duração Total das Interrupções (horas)',
            'tariff_flag_applied': 'Bandeira Tarifária Aplicada',
            'notes': 'Observações',
        }
        widgets = {
            'profile': forms.Select(attrs={'class': 'form-control'}),
            # CORREÇÃO: Widget e tipo corretos para DateTimeField.
            'record_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'record_type': forms.Select(attrs={'class': 'form-control'}),
            'voltage_level': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'num_voltage_fluctuations': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'avg_voltage_variation': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'thd_voltage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'thd_current': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'num_interruptions': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'total_duration_interruptions_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'tariff_flag_applied': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request and self.request.user.is_authenticated:
            self.fields['profile'].queryset = EnergyProfiles.objects.filter(user=self.request.user)



class BillingRecordForm(forms.ModelForm):
    """
    Formulário para criar e atualizar registros de faturas de energia.
    Inclui todos os campos detalhados do talão de energia.
    """
    class Meta:
        model = BillingRecord
        fields = [
            'profile', 'bill_type', 'bill_number', 'invoice_date', 'due_date', # Campos adicionados/corrigidos
            'start_period', 'end_period', 'days_billed',
            'energy_charge_total', 'demand_charge_total', # Campos adicionados
            'contracted_demand_peak_kw', 'contracted_demand_off_peak_kw', # Campos adicionados
            'billed_demand_peak_kw', 'billed_demand_off_peak_kw', # Campos adicionados
            'availability_cost_value', # Campo adicionado
            'kwh_total_billed', 'total_cost', 'energy_tariff_used', # Nome do campo corrigido
            'applied_tariff_flag', 'applied_tariff_flag_cost', 'flag_additional_cost_per_100kwh', # Nomes corrigidos, adicionado campo de custo da bandeira
            'meter_id', 'previous_reading', 'current_reading', 'meter_constant', 'next_reading_date',
            'icms_base', 'icms_aliquot', 'icms_value',
            'pis_base', 'pis_aliquot', 'pis_value',
            'cofins_base', 'cofins_aliquot', 'cofins_value',
            'cip_cost', 'meter_rental_cost', 'fine_cost', 'monetary_correction_cost', 'interest_cost', # Adicionado meter_rental_cost
            'notes'
        ]
        labels = {
            'profile': 'Perfil de Energia',
            'bill_type': 'Tipo de Fatura',
            'bill_number': 'Número da Fatura',
            'invoice_date': 'Data de Emissão da Fatura',
            'due_date': 'Data de Vencimento',
            'start_period': 'Início do Período de Consumo',
            'end_period': 'Fim do Período de Consumo',
            'days_billed': 'Nº de Dias Faturados',
            'energy_charge_total': 'Valor Total da Energia (R$)',
            'demand_charge_total': 'Valor Total da Demanda (R$)',
            'contracted_demand_peak_kw': 'Demanda Contratada na Ponta (kW)',
            'contracted_demand_off_peak_kw': 'Demanda Contratada Fora de Ponta (kW)',
            'billed_demand_peak_kw': 'Demanda Faturada na Ponta (kW)',
            'billed_demand_off_peak_kw': 'Demanda Faturada Fora de Ponta (kW)',
            'availability_cost_value': 'Custo de Disponibilidade (R$)',
            'kwh_total_billed': 'Consumo Total Faturado (kWh)',
            'total_cost': 'Custo Total da Fatura (R$)',
            'energy_tariff_used': 'Tarifa Base Aplicada',
            'unit_price_kwh': 'Preço Unitário do kWh (com impostos) (R$/kWh)',
            'tariff_unit_kwh': 'Tarifa Unitária do kWh (sem impostos) (R$/kWh)',
            'applied_tariff_flag': 'Bandeira Tarifária Aplicada',
            'applied_tariff_flag_cost': 'Custo da Bandeira Tarifária (R$)',
            'flag_additional_cost_per_100kwh': 'Adicional da Bandeira (R$/100 kWh)',
            'meter_id': 'Nº do Medidor',
            'previous_reading': 'Leitura Anterior do Medidor',
            'current_reading': 'Leitura Atual do Medidor',
            'meter_constant': 'Constante do Medidor',
            'next_reading_date': 'Próxima Leitura Prevista',
            'icms_base': 'Base de Cálculo ICMS (R$)',
            'icms_aliquot': 'Alíquota ICMS (%)',
            'icms_value': 'Valor ICMS (R$)',
            'pis_base': 'Base de Cálculo PIS (R$)',
            'pis_aliquot': 'Alíquota PIS (%)',
            'pis_value': 'Valor PIS (R$)',
            'cofins_base': 'Base de Cálculo COFINS (R$)',
            'cofins_aliquot': 'Alíquota COFINS (%)',
            'cofins_value': 'Valor COFINS (R$)',
            'cip_cost': 'CIP (Contrib. Ilum. Pública) (R$)',
            'meter_rental_cost': 'Custo Aluguel Medidor (R$)',
            'fine_cost': 'Multa (R$)',
            'monetary_correction_cost': 'Correção Monetária (R$)',
            'interest_cost': 'Juros (R$)',
            'notes': 'Observações Adicionais',
        }
        widgets = {
            'profile': forms.Select(attrs={'class': 'form-control'}),
            'bill_type': forms.Select(attrs={'class': 'form-control'}),
            'bill_number': forms.TextInput(attrs={'class': 'form-control'}),
            'invoice_date': forms.DateInput(attrs={'class': 'form-control datepicker', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control datepicker', 'type': 'date'}),
            'start_period': forms.DateInput(attrs={'class': 'form-control datepicker', 'type': 'date'}),
            'end_period': forms.DateInput(attrs={'class': 'form-control datepicker', 'type': 'date'}),
            'days_billed': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'energy_charge_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'demand_charge_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'contracted_demand_peak_kw': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'contracted_demand_off_peak_kw': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'billed_demand_peak_kw': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'billed_demand_off_peak_kw': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'availability_cost_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'kwh_total_billed': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'min': 0}),
            'total_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'energy_tariff_used': forms.Select(attrs={'class': 'form-control'}),
            'unit_price_kwh': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001', 'readonly': 'readonly'}),
            'tariff_unit_kwh': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001', 'readonly': 'readonly'}),
            'applied_tariff_flag': forms.Select(attrs={'class': 'form-control'}),
            'applied_tariff_flag_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'flag_additional_cost_per_100kwh': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'min': 0}),
            'meter_id': forms.TextInput(attrs={'class': 'form-control'}),
            'previous_reading': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001', 'min': 0}),
            'current_reading': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001', 'min': 0}),
            'meter_constant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001', 'min': 0}),
            'next_reading_date': forms.DateInput(attrs={'class': 'form-control datepicker', 'type': 'date'}),
            'icms_base': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'icms_aliquot': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'min': 0, 'max': 100}),
            'icms_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'pis_base': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'pis_aliquot': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'min': 0, 'max': 100}),
            'pis_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'cofins_base': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'cofins_aliquot': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'min': 0, 'max': 100}),
            'cofins_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'cip_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'meter_rental_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'fine_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'monetary_correction_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'interest_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['bill_type'].choices = BillTypeChoices.choices # Ensure choices are set
        self.fields['applied_tariff_flag'].choices = TariffFlagTypeChoices.choices # Ensure choices are set

        if self.request and self.request.user.is_authenticated:
            self.fields['profile'].queryset = EnergyProfiles.objects.filter(user=self.request.user)
        self.fields['energy_tariff_used'].queryset = EnergyTariff.objects.filter(is_active=True).order_by('name')



class AlertForm(forms.ModelForm):
    """
    Formulário para criar e gerenciar alertas.
    CORRIGIDO: Adicionado o campo 'alert_date'.
    """
    class Meta:
        model = Alert
        # CORREÇÃO: Adicionado 'alert_date'.
        fields = ['profile', 'user', 'message', 'alert_type', 'severity', 'threshold_value', 
                  'current_value', 'alert_date', 'is_read', 'is_resolved', 'suggested_actions']
        labels = {
            'profile': 'Perfil de Energia',
            'user': 'Usuário',
            'message': 'Mensagem do Alerta',
            'alert_type': 'Tipo de Alerta',
            'severity': 'Severidade',
            'threshold_value': 'Valor Limite',
            'current_value': 'Valor Atual Gatilho',
            'alert_date': 'Data e Hora do Alerta',
            'is_read': 'Lido?',
            'is_resolved': 'Resolvido?',
            'suggested_actions': 'Ações Sugeridas',
        }
        widgets = {
            'profile': forms.Select(attrs={'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'alert_type': forms.Select(attrs={'class': 'form-control'}),
            'severity': forms.Select(attrs={'class': 'form-control'}),
            'threshold_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'current_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            # CORREÇÃO: Widget para alert_date
            'alert_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_read': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_resolved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'suggested_actions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request and self.request.user.is_authenticated:
            self.fields['profile'].queryset = EnergyProfiles.objects.filter(user=self.request.user)


class ConsumptionGoalForm(forms.ModelForm):
    """
    Formulário para definir metas de consumo de energia.
    CORRIGIDO: Adicionados campos de configuração da meta.
    """
    class Meta:
        model = ConsumptionGoal
        # CORREÇÃO: Adicionados campos faltantes.
        fields = ['profile', 'name', 'goal_type', 'target_value', 'target_kwh', 'target_kwh_per_month', 
                  'start_date', 'end_date', 'description', 'alert_threshold_percentage', 'is_active']
        labels = {
            'profile': 'Perfil de Energia',
            'name': 'Nome da Meta',
            'goal_type': 'Tipo de Meta',
            'target_value': 'Valor Alvo',
            'target_kwh': 'Meta de Consumo (kWh)',
            'target_kwh_per_month': 'Meta Mensal (kWh)',
            'start_date': 'Data de Início',
            'end_date': 'Data de Fim',
            'description': 'Descrição',
            'alert_threshold_percentage': 'Gatilho de Alerta (%)',
            'is_active': 'Ativa?',
        }
        widgets = {
            'profile': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Redução de 10% no consumo'}),
            'goal_type': forms.Select(attrs={'class': 'form-control'}),
            'target_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'target_kwh': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'target_kwh_per_month': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'alert_threshold_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0, 'max': 100}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request and self.request.user.is_authenticated:
            self.fields['profile'].queryset = EnergyProfiles.objects.filter(user=self.request.user)


class ConsumptionPredictionsForm(forms.ModelForm):
    """
    Formulário para registrar previsões de consumo de energia.
    """
    class Meta:
        model = ConsumptionPredictions
        fields = ['profile', 'profile_device', 'model', 'prediction_date', 'predicted_kwh', 'predicted_daily_kwh', 'confidence_score']
        labels = {
            'profile': 'Perfil de Energia',
            'profile_device': 'Dispositivo do Perfil',
            'model': 'Modelo de Previsão',
            'prediction_date': 'Data da Previsão',
            'predicted_kwh': 'Consumo Previsto (kWh)',
            'predicted_daily_kwh': 'Consumo Diário Previsto (kWh)',
            'confidence_score': 'Pontuação de Confiança',
        }
        widgets = {
            'profile': forms.Select(attrs={'class': 'form-control'}),
            'profile_device': forms.Select(attrs={'class': 'form-control'}),
            'model': forms.Select(attrs={'class': 'form-control'}),
            'prediction_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'predicted_kwh': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'predicted_daily_kwh': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'confidence_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.00', 'max': '1.00'}),
        }


class ModelAccuracyScoresForm(forms.ModelForm):
    """
    Formulário para registrar pontuações de acurácia de modelos.
    """
    class Meta:
        model = ModelAccuracyScores
        fields = ['model', 'profile', 'score', 'mape', 'rmse', 'start_date', 'end_date', 'evaluation_date']
        labels = {
            'model': 'Modelo de Previsão',
            'profile': 'Perfil de Energia',
            'mape': 'MAPE (%)',
            'rmse': 'RMSE (kWh)',
            'score': 'Pontuação',
            'start_date': 'Início do Período Avaliado',
            'end_date': 'Fim do Período Avaliado',
            'evaluation_date': 'Data da Avaliação',
        }
        widgets = {
            'model': forms.Select(attrs={'class': 'form-control'}),
            'profile': forms.Select(attrs={'class': 'form-control'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'mape': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'rmse': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'evaluation_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),            
            

        }
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request and self.request.user.is_authenticated:
            self.fields['profile'].queryset = EnergyProfiles.objects.filter(user=self.request.user)


class OptimizationSuggestionForm(forms.ModelForm):
    """
    Formulário para criar e atualizar sugestões de otimização.
    """
    class Meta:
        model = OptimizationSuggestion
        fields = ['profile', 'title', 'description', 'category', 'estimated_savings_kwh', 'estimated_savings_kwh_per_month', 'estimated_savings_money', 'procel_seal_target', 'impact_level', 'is_implemented']
        labels = {
            'profile': 'Perfil de Energia',
            'title': 'Título da Sugestão',
            'description': 'Descrição',
            'category': 'Categoria',
            'estimated_savings_kwh': 'Economia Estimada (kWh)',
            'estimated_savings_kwh_per_month': 'Economia Estimada (kWh/mês)',
            'estimated_savings_money': 'Economia Estimada (R$)',
            'procel_seal_target': 'Selo Procel Alvo',
            'impact_level': 'Nível de Impacto',
            'is_implemented': 'Implementada?',
        }
        widgets = {
            'profile': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Trocar lâmpadas por LED'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'estimated_savings_kwh': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'estimated_savings_kwh_per_month': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'estimated_savings_money': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'procel_seal_target': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: A'}),
            'impact_level': forms.Select(attrs={'class': 'form-control'}),
            'is_implemented': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request and self.request.user.is_authenticated:
            self.fields['profile'].queryset = EnergyProfiles.objects.filter(user=self.request.user)


class DeviceUsagePatternForm(forms.ModelForm):
    """
    Formulário para definir padrões de uso de dispositivos.
    """
    class Meta:
        model = DeviceUsagePattern
        fields = ['profile_device', 'day_of_week', 'start_time', 'end_time', 'kwh_consumption', 'usage_percentage', 'hour_of_day', 'intensity_factor', 'description']
        labels = {
            'profile_device': 'Dispositivo do Perfil',
            'day_of_week': 'Dia da Semana',
            'start_time': 'Hora de Início',
            'end_time': 'Hora de Fim',
            'usage_percentage': 'Porcentagem de Uso',
            'hour_of_day': 'Hora do Dia (0-23)',
            'intensity_factor': 'Fator de Intensidade',
            'description': 'Descrição',
        }
        widgets = {
            'profile_device': forms.Select(attrs={'class': 'form-control'}),
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'kwh_consumption': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'usage_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.00', 'max': '100.00'}),
            'hour_of_day': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '23'}),
            'intensity_factor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request and self.request.user.is_authenticated:
            user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
            self.fields['profile_device'].queryset = ProfileDevices.objects.filter(profile__in=user_profiles).order_by('name')
        else:
            self.fields['profile_device'].queryset = ProfileDevices.objects.none()

class HistoricalPredictionComparisonForm(forms.ModelForm):
    """
    Formulário para comparação histórica de previsões.
    """
    class Meta:
        model = HistoricalPredictionComparison
        fields = ['profile', 'prediction', 'actual_kwh', 'comparison_date']
        labels = {
            'profile': 'Perfil de Energia',
            'prediction': 'Instância da Previsão',
            'actual_kwh': 'Consumo Real (kWh)',
            'comparison_date': 'Data da Comparação',
        }
        widgets = {
            'profile': forms.Select(attrs={'class': 'form-control'}),
            'prediction': forms.Select(attrs={'class': 'form-control'}),
            'predicted_kwh': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'actual_kwh': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'comparison_date': forms.DateInput(attrs={'class': 'form-control datepicker', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if self.request:
            user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
            print(f"DEBUG FORM: Perfis do usuário {self.request.user.username}: {user_profiles.values_list('name', flat=True)}")

            all_predictions_for_user_profiles = ConsumptionPredictions.objects.filter(
                profile__in=user_profiles
            )
            print(f"DEBUG FORM: Total de previsões para perfis do usuário: {all_predictions_for_user_profiles.count()}")

            compared_predictions_pks = HistoricalPredictionComparison.objects.all().values_list('prediction__pk', flat=True)
            print(f"DEBUG FORM: PKs de previsões já comparadas: {list(compared_predictions_pks)}")

            # Este é o queryset final que será usado pelo campo
            final_queryset = all_predictions_for_user_profiles.exclude(
                pk__in=compared_predictions_pks
            ).order_by('-prediction_date')

            print(f"DEBUG FORM: Total de previsões disponíveis (final_queryset): {final_queryset.count()}")
            print(f"DEBUG FORM: Primeiras 5 previsões disponíveis: {final_queryset[:5]}")

            self.fields['prediction'].queryset = final_queryset
            self.fields['profile'].queryset = user_profiles


    
    def clean(self):
        cleaned_data = super().clean()
        prediction = cleaned_data.get('prediction')
        actual = cleaned_data.get('actual_kwh')

        predicted = None
        if prediction:
            predicted = prediction.predicted_kwh # Acessa predicted_kwh do modelo ConsumptionPredictions

        if predicted is not None and actual is not None:
            deviation = actual - predicted
            deviation_percentage = (deviation / predicted * 100) if predicted != 0 else 0
            
            # Cálculo do erro absoluto
            error_kwh = abs(deviation)
            # Cálculo do erro percentual (pode ser diferente do deviation_percentage)
            percentage_error = (error_kwh / predicted * 100) if predicted != 0 else 0

            cleaned_data['deviation'] = deviation
            cleaned_data['deviation_percentage'] = deviation_percentage
            cleaned_data['error_kwh'] = error_kwh
            cleaned_data['percentage_error'] = percentage_error

        return cleaned_data
    

class UserPreferencesForm(forms.ModelForm):
    """
    Formulário para preferências do usuário.
    CORRIGIDO: Formulário completo para refletir todas as opções do modelo.
    """
    class Meta:
        model = UserPreferences
        # CORREÇÃO: Adicionados todos os campos de preferência.
        fields = ['theme_preference', 'notification_frequency', 
                  'report_format_preference', 'receive_marketing_emails',]
        labels = {
            'theme_preference': 'Tema da Interface',
            'notification_frequency': 'Frequência de Notificações',
            'report_format_preference': 'Formato de Relatório Padrão',
            'receive_marketing_emails': 'Desejo receber e-mails informativos',
            'phone_number': 'Seu número de telefone (para SMS)',
            'receive_sms_notifications': 'Desejo receber alertas importantes por SMS',
            'receive_push_notifications': 'Desejo receber alertas no navegador (notificações push)',
        
        }
        widgets = {
            'theme_preference': forms.Select(attrs={'class': 'form-control'}),
            'notification_frequency': forms.Select(attrs={'class': 'form-control'}),
            'report_format_preference': forms.Select(attrs={'class': 'form-control'}),
            'receive_marketing_emails': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+5511912345678'}),
            'receive_sms_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'receive_push_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        # O campo 'user' é a chave primária e não deve estar no formulário,
        # a instância é associada ao usuário na view.
