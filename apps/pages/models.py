# models.py
from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.conf import settings
from django.db import models
from django.db.models import TextChoices, IntegerChoices
from phonenumber_field.modelfields import PhoneNumberField
import uuid


class TariffFlagTypeChoices(TextChoices):
    VERDE = 'VERDE', 'Verde'
    AMARELA = 'AMARELA', 'Amarela'
    VERMELHA1 = 'VERMELHA1', 'Vermelha Nível 1'
    VERMELHA2 = 'VERMELHA2', 'Vermelha Nível 2'

class DayOfWeekChoices(TextChoices):
    MON = 'MON', 'Segunda-feira'
    TUE = 'TUE', 'Terça-feira'
    WED = 'WED', 'Quarta-feira'
    THU = 'THU', 'Quinta-feira'
    FRI = 'FRI', 'Sexta-feira'
    SAT = 'SAT', 'Sábado'
    SUN = 'SUN', 'Domingo'

class EnergyTariffTypeChoices(TextChoices):
    CONVENCIONAL = 'CONVENCIONAL', 'Convencional'
    BRANCA = 'BRANCA', 'Branca'
    AZUL = 'AZUL', 'Horo-Sazonal Azul'
    VERDE = 'VERDE', 'Horo-Sazonal Verde'

class BillTypeChoices(models.TextChoices):
    # Grupo B (Baixa Tensão)
    BAIXA_TENSAO_CONVENCIONAL = 'BT_CONV', 'Baixa Tensão Convencional (Grupo B)'
    TARIFA_BRANCA = 'TB', 'Tarifa Branca (Grupo B)'
    MICRO_REGIAO = 'MICRO_REGIAO', 'Micro Região (Grupo B)' # Se for um tipo distinto, senão, pode ser CONV.
    # Grupo A (Alta Tensão)
    ALTA_TENSAO_AZUL = 'AT_AZUL', 'Alta Tensão Azul (Grupo A)'
    ALTA_TENSAO_VERDE = 'AT_VERDE', 'Alta Tensão Verde (Grupo A)'

class SupplyTypeChoices(TextChoices):
    MONOFASICO = 'MONOFASICO', 'Monofásico'
    BIFASICO = 'BIFASICO', 'Bifásico'
    TRIFASICO = 'TRIFASICO', 'Trifásico'

class UserTypeChoices(TextChoices):
    PESSOA_FISICA = 'PF', 'Pessoa Física'
    PESSOA_JURIDICA = 'PJ', 'Pessoa Jurídica'
    PUBLICO = 'PUB', 'Poder Público'
    RURAL_PRODUTOR = 'RURAL_PROD', 'Rural Produtor' 

class ReadingPeriodChoices(TextChoices):
    DAILY = 'DAILY', 'Diária'
    MONTHLY = 'MONTHLY', 'Mensal'
    HOURLY = 'HOURLY', 'Horária'
    MINUTELY = 'MINUTELY', 'Minutal'
    OTHER = 'OTHER', 'Outro'

class ProcelSealChoices(TextChoices):
    A = 'A', 'A - Mais Eficiente'
    B = 'B', 'B - Eficiente'
    C = 'C', 'C - Média Eficiência'
    D = 'D', 'D - Baixa Eficiência'
    E = 'E', 'E - Menos Eficiente'
    NA = 'NA', 'Não se Aplica/Não Informado'

class BaseModel(models.Model):
    """
    Abstract base model to include common fields like 'created_at'.
    """
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        abstract = True
        # Ordering by creation date by default for simplicity, can be changed
        # ordering = ['-created_at'] 


class DeviceCatalog(models.Model):
    """
    Catálogo de dispositivos disponíveis, com informações como nome e consumo médio.
    Equivalente à tabela `public.device_catalog`.
    """
    class DeviceCategoryChoices(TextChoices):
        ELETRODOMESTICO = 'ELETRODOMESTICO', 'Eletrodoméstico'
        ILUMINACAO = 'ILUMINACAO', 'Iluminação'
        ELETRONICOS = 'ELETRONICOS', 'Eletrônicos'
        CLIMATIZACAO = 'CLIMATIZACAO', 'Climatização'
        AQUECIMENTO = 'AQUECIMENTO', 'Aquecimento de Água'
        OUTROS = 'OUTROS', 'Outros'

    class NominalPowerChoices(TextChoices):
        P60 = '60', '60 Watts'
        P100 = '100', '100 Watts'
        P150 = '150', '150 Watts'
        P500 = '500', '500 Watts'
        P1000 = '1000', '1000 Watts'
        P1500 = '1500', '1500 Watts'
        P2000 = '2000', '2000 Watts'
        P2500 = '2500', '2500 Watts'
        P3000 = '3000', '3000 Watts'
        P3500 = '3500', '3500 Watts'
        P4000 = '4000', '4000 Watts'
        P5000 = '5000', '5000 Watts'
        OUTRO = 'OUTRO', 'Outra Potência' 

    class VoltageChoices(TextChoices):
        V127 = '127', '127 Volts (110V/127V)'
        V220 = '220', '220 Volts'
        BIVOLT = 'BIVOLT', 'Bivolt (127V/220V)'
        OUTRO = 'OUTRO', 'Outra Tensão'

    class BrandChoices(TextChoices): 
        SAMSUNG = 'SAMSUNG', 'Samsung'
        LG = 'LG', 'LG'
        PHILIPS = 'PHILIPS', 'Philips'
        BRASTEMP = 'BRASTEMP', 'Brastemp'
        ELETROLUX = 'ELETROLUX', 'Electrolux'
        GE = 'GE', 'GE'
        PANASONIC = 'PANASONIC', 'Panasonic'
        MIDEA = 'MIDEA', 'Midea'
        DAIKIN = 'DAIKIN', 'Daikin'
        CONSUL = 'CONSUL', 'Consul'
        OUTRA = 'OUTRA', 'Outra Marca'

    name = models.TextField(unique=True, null=False)
    icon = models.TextField(blank=True, null=True) 
    avg_kwh = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True) 
    
    procel_seal = models.CharField(
        max_length=5,
        choices=ProcelSealChoices.choices,
        default=ProcelSealChoices.NA,
        verbose_name="Selo Procel"
    )
    categoria = models.CharField(
        max_length=100,
        choices=DeviceCategoryChoices.choices,
        blank=True,
        null=True,
        verbose_name="Categoria"
    )
    potencia_nominal = models.CharField(
        max_length=10,
        choices=NominalPowerChoices.choices,
        blank=True,
        null=True,
        verbose_name="Potência Nominal (Watts)"
    )
    tensao = models.CharField(
        max_length=10, 
        choices=VoltageChoices.choices,
        blank=True,
        null=True,
        verbose_name="Tensão (Volts)"
    )
    marca = models.CharField( 
        max_length=100,
        choices=BrandChoices.choices,
        blank=True,
        null=True,
        verbose_name="Marca"
    )

    class Meta:
        db_table = 'device_catalog'
        verbose_name = 'Device Catalog Entry'
        verbose_name_plural = 'Device Catalog'
        ordering = ['name'] # Ordena pelo nome do dispositivo

    def __str__(self):
        return self.name
    
class EnergyProfiles(models.Model):
    """
    Perfis de energia criados pelos usuários, contendo nome e descrição.
    Agora usa o modelo de usuário padrão do Django para a chave estrangeira.
    """
    class SubgroupChoices(TextChoices):
        A1 = 'A1', 'Subgrupo A1'
        A2 = 'A2', 'Subgrupo A2'
        A3 = 'A3', 'Subgrupo A3'
        A3A = 'A3A', 'Subgrupo A3A'
        A4 = 'A4', 'Subgrupo A4'
        AS = 'AS', 'Subgrupo AS'
        B1 = 'B1', 'Subgrupo B1 - Residencial'
        B2 = 'B2', 'Subgrupo B2 - Rural'
        B3 = 'B3', 'Subgrupo B3 - Comercial, Serviços e Outras Atividades'
        B4 = 'B4', 'Subgrupo B4 - Iluminação Pública'


    class ClientClassificationChoices(TextChoices):
        PESSOA_FISICA = 'PF', 'Pessoa Física'
        PESSOA_JURIDICA = 'PJ', 'Pessoa Jurídica'

    class ClassificationChoices(TextChoices):
        RESIDENCIAL = 'Residencial Pleno', 'Residencial'
        COMERCIAL = 'Comercial B.T.', 'Comercial'
        INDUSTRIAL = 'Industrial B.T.', 'Industrial'
        RURAL = 'Rural', 'Rural'
        PODER_PUBLICO = 'Poder Público B.T.', 'Poder Público'
        ILUMINACAO_PUBLICA = 'Iluminação Pública', 'Iluminação Pública'
        SERVICO_PUBLICO = 'Serviço Público B.T.', 'Serviço Público'
        BAIXA_RENDA = 'Residencial Baixa Renda', 'Baixa Renda'

    class NominalVoltageChoices(TextChoices):
        V220 = '220 V - MO', '220 V - Monofásico'
        V127 = '127 V - MO', '127 V - Monofásico'
        V380 = '380 V - TF', '380 V - Trifásico'
        V240 = '240 V - DF', '240 V - Bifásico'
        V440 = '440 V - TF', '440 V - Trifásico'

    class SubclassChoices(TextChoices):
        NORMAL = 'Residencial Normal', 'Residencial Normal'
        BAIXA_RENDA = 'Residencial Baixa Renda', 'Residencial Baixa Renda'

    # Referencia o modelo de usuário padrão do Django
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.RESTRICT, 
        related_name='energy_profiles'
    )
    user_type = models.CharField(
        max_length=5,
        choices=ClientClassificationChoices.choices,
        default=ClientClassificationChoices.PESSOA_FISICA,
        help_text="Classificação do cliente (Pessoa Física ou Jurídica)"
    )
    name = models.TextField(null=False)
    description = models.TextField(blank=True, null=True)

    api_key = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name="Chave de API do Sensor"
    )

    subgroup = models.CharField(
        max_length=10,
        choices=SubgroupChoices.choices,
        default=SubgroupChoices.B1,
        help_text="Subgrupo de enquadramento (e.g., B1 - Residencial)"
    )
    voltage_group = models.CharField(max_length=50, blank=True, null=True, help_text="Ex: b")
    supply_type = models.CharField(
        max_length=15,
        choices=SupplyTypeChoices.choices,
        default=SupplyTypeChoices.MONOFASICO,
        help_text="Tipo de fornecimento (Monofásico, Bifásico, Trifásico)"
    )
    tariff_type = models.CharField(
        max_length=20,
        choices=EnergyTariffTypeChoices.choices,
        default=EnergyTariffTypeChoices.CONVENCIONAL,
        help_text="Classificação tarifária (e.g., Residencial, Comercial)"
    )
    nominal_voltage = models.CharField(max_length=50, choices=NominalVoltageChoices.choices, default=NominalVoltageChoices.V220, blank=True, help_text="Ex: 220 V - MO")
    
    classification = models.CharField(max_length=100, choices=ClassificationChoices.choices, default=ClassificationChoices.RESIDENCIAL, blank=True, help_text="Ex: Residencial Pleno")

    subclass = models.CharField(
        max_length=100,
        choices=SubclassChoices.choices, 
        blank=True,
        null=True,
        help_text="Ex: Residencial Normal"
    )
    address_line1 = models.CharField(max_length=255, null=False)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, null=False)
    state = models.CharField(max_length=100, null=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    default_tariff = models.ForeignKey('EnergyTariff', on_delete=models.SET_NULL, 
                                     related_name='profiles_with_default_tariff', 
                                     null=True, blank=True,
                                     help_text="Tarifa padrão associada a este perfil.")


    class Meta:
        db_table = 'energy_profiles'
        verbose_name = 'Energy Profile'
        verbose_name_plural = 'Energy Profiles'
        unique_together = ('user', 'name') # Garante que o nome do perfil seja único para cada usuário
        ordering = ['name'] # Ordena os perfis pelo nome

    def __str__(self):
        # Acessa o nome do usuário padrão do Django
        return f"{self.name} ({self.user.username})" 

class RawSensorData(BaseModel):
    """
    Armazena leituras brutas e de alta frequência diretamente dos sensores de IoT.
    Esta tabela é otimizada para inserções rápidas (ingestão).
    """
    profile = models.ForeignKey(EnergyProfiles, on_delete=models.CASCADE, related_name='raw_sensor_data')
    timestamp = models.DateTimeField(
        default=datetime.now,
        db_index=True, # MUITO IMPORTANTE para performance em consultas de séries temporais
        verbose_name="Timestamp da Leitura Bruta"
    )
    
    # Campos elétricos comuns de sensores
    voltage = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name="Tensão (V)")
    current = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name="Corrente (A)")
    active_power = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name="Potência Ativa (W)")
    power_factor = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True, verbose_name="Fator de Potência")

    # Flag para controlar o processamento
    processed = models.BooleanField(default=False, db_index=True, verbose_name="Processado?")

    class Meta:
        verbose_name = "Dado Bruto do Sensor"
        verbose_name_plural = "Dados Brutos dos Sensores"
        ordering = ['-timestamp']

class PredictionModels(BaseModel):
    """
    Modelos de previsão utilizados para estimar o consumo.
    Equivalente à tabela `public.prediction_models`.
    """
    class ModelTypeChoices(TextChoices):
        UPLOADED_FILE = 'UPLOAD', 'Arquivo Externo (Upload)'
        LINEAR_REGRESSION = 'LINEAR', 'Regressão Linear Simples (Automático)'
        PROPHET = 'PROPHET', 'Prophet (Automático)'

        RANDOM_FOREST_REG = 'RF_REG', 'Florestas Aleatórias (Regressão)'
        TENSORFLOW_REG = 'TF_REG', 'Rede Neural - Keras/TensorFlow (Regressão)'

        # Modelos de Classificação (para prever uma categoria, ex: Bandeira Verde/Amarela/Vermelha)
        LOGISTIC_REGRESSION = 'LOGISTIC', 'Regressão Logística (Classificação)'
        DECISION_TREE_CLASS = 'DT_CLASS', 'Árvore de Decisão (Classificação)'
        
        # Modelos de Clusterização (para agrupar perfis de consumo semelhantes)
        K_MEANS = 'KMEANS', 'K-Means (Clusterização)'
        GAUSSIAN_MIXTURE = 'GMM', 'Misturas de Gaussianas (Clusterização)'
        
        APRIORI = 'APRIORI', 'Apriori (Regras de Associação)'
        BAYESIAN_INFERENCE = 'BAYESIAN', 'Inferência Bayesiana'
        KNN = 'KNN', 'K-Vizinhos Mais Próximos (K-NN)'

    class SeasonalityModeChoices(TextChoices):
        ADDITIVE = 'additive', 'Aditiva'
        MULTIPLICATIVE = 'multiplicative', 'Multiplicativa'

    class DataSourceChoices(TextChoices):
        # --- Fontes de Dados Principais (Já existentes) ---
        READINGS = 'readings', 'Leituras de Energia (EnergyReading)'
        BILLING = 'billing', 'Faturas (BillingRecord)'

        DEVICES = 'devices', 'Consumo Agregado de Dispositivos'
        PREDICTIONS = 'predictions', 'Previsões Anteriores (Feedback Loop)'
        QUALITY = 'quality', 'Registros de Qualidade de Energia'
        GOALS = 'goals', 'Metas de Consumo'
        ALERTS = 'alerts', 'Histórico de Alertas de Consumo'

        WEATHER = 'weather', 'Dados Climáticos (Ex: Temperatura)'
        SOLAR = 'solar', 'Geração Solar (se aplicável)'
        OCCUPANCY = 'occupancy', 'Dados de Ocupação (Comercial)'
        EVENTS = 'events', 'Calendário de Eventos Especiais'
        SIMULATION = 'simulation', 'Dados de Simulação'

    name = models.TextField(unique=True, null=False)
    description = models.TextField(blank=True, null=True)
    model_type = models.CharField(
        max_length=10,
        choices=ModelTypeChoices.choices,
        default=ModelTypeChoices.LINEAR_REGRESSION,
        verbose_name="Tipo de Modelo"
    )
    model_file = models.FileField(upload_to='prediction_models/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    accuracy_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Última pontuação de acurácia registrada para este modelo (ex: MAPE).")

    data_source = models.CharField(max_length=20, choices=DataSourceChoices.choices, default=DataSourceChoices.READINGS, verbose_name="Fonte de Dados para Treinamento")

    # 2. Período de Previsão Padrão
    default_forecast_horizon = models.IntegerField(default=30, verbose_name="Horizonte de Previsão Padrão (dias)")

    # 3. Hiperparâmetros do Prophet
    yearly_seasonality = models.BooleanField(default=True, verbose_name="Sazonalidade Anual (Prophet)")
    weekly_seasonality = models.BooleanField(default=True, verbose_name="Sazonalidade Semanal (Prophet)")
    daily_seasonality = models.BooleanField(default=False, verbose_name="Sazonalidade Diária (Prophet)")
    seasonality_mode = models.CharField(max_length=15, choices=SeasonalityModeChoices.choices, default=SeasonalityModeChoices.MULTIPLICATIVE, verbose_name="Modo de Sazonalidade (Prophet)")

    # 4. Controle de Feriados
    include_brazil_holidays = models.BooleanField(default=True, verbose_name="Incluir Feriados Nacionais (Prophet)")

    # 5. Validação e Métricas
    last_trained = models.DateTimeField(null=True, blank=True, help_text="Data e hora do último treinamento do modelo.")
    last_accuracy_score = models.JSONField(null=True, blank=True, verbose_name="Últimas Métricas de Acurácia (JSON)")

    # 6. Campo para Parâmetros Adicionais (Flexibilidade Máxima)
    additional_params = models.JSONField(null=True, blank=True, verbose_name="Parâmetros Adicionais (JSON)", help_text="Para configurações avançadas, ex: {'changepoint_prior_scale': 0.05}")


    class Meta:
        db_table = 'prediction_models'
        verbose_name = 'Prediction Model'
        verbose_name_plural = 'Prediction Models'
        unique_together = (('name',),)
        ordering = ['name'] 

    def __str__(self):
        return f"{self.name}"

class ProfileDevices(models.Model):
    """
    Associação entre um perfil de energia e um dispositivo do catálogo.
    Define a quantidade de dispositivos e o tempo de uso diário.
    Equivalente à tabela `public.profile_devices`.
    """

    profile = models.ForeignKey(EnergyProfiles, on_delete=models.RESTRICT, null=False, related_name='profile_devices')
    device = models.ForeignKey(DeviceCatalog, on_delete=models.RESTRICT, null=False, related_name='profile_devices')
    name = models.TextField(blank=True, null=True)
    quantity = models.IntegerField(default=1, blank=True, verbose_name="Quantidade")
    hours_per_day = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Uso Médio Diário (horas)")
    days_of_week = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Dias da semana em que o dispositivo é usado (ex: MON,QUA,SEX)",
        verbose_name="Dias da Semana de Uso"
    )
    tempo_uso_semanal = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Tempo de Uso Semanal (horas)")
    daily_kwh_consumption = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, help_text="Consumo diário estimado em kWh para este dispositivo no perfil.")
    monthly_kwh_consumption = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, help_text="Consumo mensal estimado em kWh para este dispositivo no perfil.")
    annual_kwh_consumption = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, help_text="Consumo anual estimado em kwh para este dispositivo no perfil.")
    consumption_kwh_per_day = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, help_text="Consumo diário calculado (kWh/dia) para este dispositivo no perfil")
    vida_util_estimativa = models.IntegerField(blank=True, null=True, verbose_name="Vida Útil Estimada (anos)")
    last_updated = models.DateTimeField(auto_now=True, editable=False) 

    def save(self, *args, **kwargs):
        print("\n" + "="*50)
        print(f"--- INICIANDO SAVE PARA O DISPOSITIVO DO PERFIL ID: {self.id} ---")
        print(f"Dispositivo do Catálogo: {self.device}")
        print(f"  -> ID do Dispositivo no Catálogo: {getattr(self.device, 'id', 'N/A')}")
        print(f"  -> Consumo Médio (avg_kwh) do Catálogo: {getattr(self.device, 'avg_kwh', 'N/A')}")
        print(f"Quantidade (quantity) no Perfil: {self.quantity}")
        print(f"Horas por Dia (hours_per_day) no Perfil: {self.hours_per_day}")
        print("="*50 + "\n")
        # --- CÁLCULO DIÁRIO CORRIGIDO ---
        # Garante que temos todos os dados necessários antes de calcular.
        device_avg_kwh = getattr(self.device, 'avg_kwh', Decimal('0.0'))
        hours = self.hours_per_day or Decimal('0.0')
        qty = self.quantity or 0

        if device_avg_kwh and device_avg_kwh > 0 and hours > 0 and qty > 0:
            # 1. Calcula o consumo por hora (o avg_kwh do catálogo é para 24h).
            kwh_per_hour = device_avg_kwh / Decimal('24')
            
            # 2. Calcula o consumo diário real baseado nas horas de uso.
            self.daily_kwh_consumption = kwh_per_hour * hours * Decimal(qty)
        else:
            self.daily_kwh_consumption = Decimal('0.0')

        # --- CÁLCULO MENSAL E ANUAL (PARTE QUE FALTAVA) ---
        # Usa o valor diário recém-calculado para estimar o mensal e anual.
        if self.daily_kwh_consumption and self.daily_kwh_consumption > 0:
            # A média de dias em um mês é aproximadamente 30.44
            self.monthly_kwh_consumption = self.daily_kwh_consumption * Decimal('30.44')
            # A média de dias em um ano é aproximadamente 365.25 para incluir anos bissextos
            self.annual_kwh_consumption = self.daily_kwh_consumption * Decimal('365.25')
        else:
            self.monthly_kwh_consumption = Decimal('0.0')
            self.annual_kwh_consumption = Decimal('0.0')

        # --- CÁLCULO DO TEMPO DE USO SEMANAL ---
        # Garante que days_of_week seja uma string, caso venha como lista
        if isinstance(self.days_of_week, list):
            self.days_of_week = ",".join(self.days_of_week)

        if self.days_of_week and self.hours_per_day:
            try:
                days_list = [day for day in self.days_of_week.split(',') if day.strip()]
                num_days = len(days_list)
                self.tempo_uso_semanal = self.hours_per_day * Decimal(num_days)
            except (TypeError, InvalidOperation):
                self.tempo_uso_semanal = Decimal('0.0')
        else:
            self.tempo_uso_semanal = Decimal('0.0')
        
        # Finalmente, chama o método save original para salvar tudo no banco de dados.
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'profile_devices'
        verbose_name = 'Profile Device'
        verbose_name_plural = 'Profile Devices'
        ordering = ['profile', 'device'] 


class ConsumptionPredictions(BaseModel):
    """
    Previsões de consumo de energia para um dispositivo específico em um perfil.
    Equivalente à tabela `public.consumption_predictions`.
    """
    id = models.BigAutoField(primary_key=True) # bigserial no PostgreSQL mapeia para BigAutoField no Django
    profile = models.ForeignKey(EnergyProfiles, on_delete=models.RESTRICT, null=False, related_name='consumption_predictions')
    profile_device = models.ForeignKey(ProfileDevices, on_delete=models.CASCADE, related_name='consumption_predictions')
    model = models.ForeignKey(PredictionModels, on_delete=models.RESTRICT, related_name='consumption_predictions')
    prediction_date = models.DateField(null=False)
    predicted_kwh = models.DecimalField(max_digits=10, decimal_places=4, null=True, help_text="Consumo previsto em kWh.")
    predicted_daily_kwh = models.DecimalField(max_digits=8, decimal_places=4, null=False)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                           help_text="Pontuação de confiança da previsão (0.00-1.00).")
    is_final = models.BooleanField(default=False, help_text="Indica se esta é a previsão final para a data ou um rascunho.")

    class Meta:
        db_table = 'consumption_predictions'
        verbose_name = 'Consumption Prediction'
        verbose_name_plural = 'Consumption Predictions'
        unique_together = ('profile', 'prediction_date')
        ordering = ['prediction_date', 'profile_device'] # Ordena por data e dispositivo do perfil

    def __str__(self):
        return (f"Previsão para {self.profile.name} {self.profile_device.name or self.profile_device.device.name} "
                f"on {self.prediction_date} using {self.model.name} {self.predicted_kwh} kWh")

class ModelAccuracyScores(models.Model):
    """
    Pontuações de precisão dos modelos para perfis específicos.
    Equivalente à tabela `public.model_accuracy_scores`.
    """

    model = models.ForeignKey(PredictionModels, on_delete=models.CASCADE, related_name='accuracy_scores')
    profile = models.ForeignKey(EnergyProfiles, on_delete=models.RESTRICT, null=False, related_name='model_accuracy_scores')
    score = models.DecimalField(max_digits=5, decimal_places=4, null=False)

    evaluation_date = models.DateTimeField(
        default=datetime.now,
        verbose_name='Data da Avaliação',
        help_text='Data e hora em que o modelo foi avaliado.'
    )
    mape = models.DecimalField(
        max_digits=5, # Ex: 99.99%
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='MAPE (%)',
        help_text='Mean Absolute Percentage Error (Erro Percentual Absoluto Médio).'
    )
    rmse = models.DecimalField(
        max_digits=10, # Para valores de erro potencialmente maiores
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name='RMSE (kWh)',
        help_text='Root Mean Squared Error (Raiz do Erro Quadrático Médio) em kWh.'
    )
    start_date = models.DateField(
        verbose_name='Data de Início do Período Avaliado',
        help_text='Data de início do período para o qual a acurácia foi calculada.'
    )
    end_date = models.DateField(
        verbose_name='Data de Fim do Período Avaliado',
        help_text='Data de fim do período para o qual a acurácia foi calculada.'
    )

    class Meta:
        db_table = 'model_accuracy_scores'
        verbose_name = 'Model Accuracy Score'
        verbose_name_plural = 'Model Accuracy Scores'
        unique_together = ('model', 'profile', 'start_date', 'end_date')
        ordering = ['-evaluation_date', 'model', 'profile']

    def __str__(self):
        return (f"Acurácia do modelo {self.model.name} para {self.profile.name} "
                f"de {self.start_date.strftime('%Y-%m-%d')} a {self.end_date.strftime('%Y-%m-%d')} "
                f"(Avaliado em: {self.evaluation_date.strftime('%Y-%m-%d %H:%M')}) "
                f"Principal: {self.score or 'N/A'}, MAPE: {self.mape or 'N/A'}%, RMSE: {self.rmse or 'N/A'}kWh")


class KPIChoices(TextChoices):
    CONSUMO_TOTAL_MES = 'CONSUMO_TOTAL_MES', 'Consumo Total do Mês (kWh)'
    CUSTO_TOTAL_MES = 'CUSTO_TOTAL_MES', 'Custo Total do Mês (R$)'
    DEMANDA_MAXIMA_MES = 'DEMANDA_MAXIMA_MES', 'Demanda Máxima do Mês (kW)'
    FATOR_POTENCIA_MEDIO = 'FATOR_POTENCIA_MEDIO', 'Fator de Potência Médio'
    CONSUMO_POR_DISPOSITIVO = 'CONSUMO_POR_DISPOSITIVO', 'Consumo por Dispositivo (kWh)'
    PREVISAO_VS_REAL = 'PREVISAO_VS_REAL', 'Desvio da Previsão vs Real (%)'
    META_ATINGIDA = 'META_ATINGIDA', 'Meta de Consumo Atingida (%)'
    CONSUMO_KWH_M2 = 'CONSUMO_KWH_M2', 'Consumo (kWh/m²)'
    CUSTO_RS_M2 = 'CUSTO_R$_M2', 'Custo (R$/m²)' 
    DURACAO_INTERRUPCOES = 'DURACAO_INTERRUPCOES', 'Duração de Interrupções (horas)'
    
class KPITypeChoices(TextChoices):
    MEDIDOR = 'MEDIDOR', 'Dados do Medidor'
    FATURA = 'FATURA', 'Dados da Fatura'
    PREVISAO = 'PREVISAO', 'Dados de Previsão'
    QUALIDADE = 'QUALIDADE', 'Qualidade de Energia'
    META = 'META', 'Meta de Consumo'
    TRENDS = 'TENDENCIAS_CONSUMO', 'Tendências de Consumo'
    FORECAST = 'PREVISAO_CONSUMO', 'Previsão de Consumo'
    BENCHMARK = 'BENCHMARK_CONSUMO', 'Benchmark de Consumo'
    MONITORING = 'MONITORAMENTO_ACURACIA', 'Monitoramento de Acurácia'
    OTIMIZACAO = 'OTIMIZACAO', 'Otimização'

class KpiUnit(TextChoices):
    KWH = 'Kwh'
    PORCENTAGEM = '%'
    MOEDA = 'R$'
    COUNT = 'Count', 'Contagem' 
    HOURS = 'Hours', 'Horas' 

class KPITimeframeChoices(TextChoices):
    DIARIO = 'DIARIO', 'Diário'
    SEMANAL = 'SEMANAL', 'Semanal'
    MENSAL = 'MENSAL', 'Mensal'
    ANUAL = 'ANUAL', 'Anual'

class KPI(BaseModel):
    """
    Representa um Key Performance Indicator (KPI) associado a um perfil de energia.
    """
    profile = models.ForeignKey(EnergyProfiles, on_delete=models.RESTRICT, related_name='kpis', blank=True, null=True)
    kpi_name = models.CharField(max_length=255, choices=KPIChoices.choices, help_text="Nome/tipo do KPI.")
    kpi_type = models.CharField(
        max_length=50,
        choices=KPITypeChoices.choices,
        default=KPITypeChoices.PREVISAO,
        help_text="Tipo de KPI (e.g., Benchmark de Consumo, Monitoramento de Acurácia)."
    )
    timeframe = models.CharField(max_length=50, choices=KPITimeframeChoices.choices, help_text="Período de tempo para o KPI.")
    target_value = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True) 
    current_value = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True, help_text="Valor atual do KPI.")
    unit = models.CharField(max_length=50, choices=KpiUnit.choices, blank=True) 
    last_updated = models.DateTimeField(auto_now=True, help_text="Data e hora da última atualização do KPI.")
    is_active = models.BooleanField(default=True, help_text="Indica se o KPI está ativo para monitoramento.")
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'kpis'
        verbose_name = 'KPI'
        verbose_name_plural = 'KPIs'
        ordering = ['profile__name', 'kpi_name']
        unique_together = ('profile', 'kpi_name', 'timeframe') # Nome do KPI deve ser único por perfil ou globalmente

    def __str__(self):
        if self.profile:
            return f"{self.name} ({self.profile.name})"
        return self.name


class EnergyReading(BaseModel):
    """
    Armazena dados de consumo de energia medidos (reais) para um dispositivo ou perfil.
    """
    class ReadingGranularityChoices(TextChoices):
        HORARIA = 'HORARIA', 'Horária'
        DIARIA = 'DIARIA', 'Diária'
        MENSAL = 'MENSAL', 'Mensal'

    class MeasurementTypeChoices(TextChoices):
        CONSUMO_SIMPLES = 'SIMPLES', 'Consumo Simples (Total)'
        PONTA_FORA_PONTA = 'PFP', 'Consumo (Ponta/Fora Ponta)'
        DEMANDA = 'DEMANDA', 'Demanda e Consumo (Grupo A)'

    profile = models.ForeignKey(EnergyProfiles, on_delete=models.RESTRICT, related_name='energy_readings', null=False)
    profile_device = models.ForeignKey(ProfileDevices, on_delete=models.CASCADE, related_name='energy_readings', null=True, blank=True)
    billing_record = models.ForeignKey(
        'BillingRecord',
        on_delete=models.CASCADE,
        related_name='readings',
        null=True, blank=True,
        help_text="Fatura à qual esta leitura pertence."
    )

    reading_datetime = models.DateTimeField(null=False, help_text="Data e Horada leitura final do período de consumo.")
    meter_number = models.CharField(max_length=50, blank=True, null=True, help_text="Número do medidor.")
    reading_period = models.CharField(max_length=10, choices=ReadingGranularityChoices.choices, default=ReadingGranularityChoices.DIARIA, null=False)
    measurement_type = models.CharField(
        max_length=10,
        choices=MeasurementTypeChoices.choices,
        default=MeasurementTypeChoices.CONSUMO_SIMPLES,
        verbose_name="Tipo de Medição"
    )
    
    # Consumos em kWh para o período da leitura (consumo do mês/período)
    total_kwh_consumption = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Consumo total de kWh no período da leitura.")

    # Consumos por Período (para Tarifa Branca, Azul, Verde)
    peak_kwh_consumption = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Consumo de kWh na ponta no período.")
    intermediate_kwh_consumption = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Consumo de kWh no período intermediário (Tarifa Branca) no período.")
    off_peak_kwh_consumption = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Consumo de kWh fora de ponta no período.")

    # Leituras de Demanda (para Grupo A) - Medida
    peak_demand_reading_kw = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Demanda medida na ponta (kW).")
    off_peak_demand_reading_kw = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Demanda medida fora de ponta (kW).")

    # Consumo de Energia Reativa (para Grupo A)
    reactive_kvarh_consumption = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Consumo de energia reativa (kVARh).")
    
    class Meta:
        db_table = 'energy_readings'
        verbose_name = 'Energy Reading'
        verbose_name_plural = 'Energy Readings'
        ordering = ['-reading_datetime']
        unique_together = [
            ('profile', 'reading_datetime', 'reading_period', 'profile_device')
        ]

    def __str__(self):
        if self.profile_device:
            return f"{self.profile_device.name or self.profile_device.device.name} - {self.reading_datetime} ({self.total_kwh_consumption} kWh)"
        elif self.profile:
            return f"Perfil {self.profile.name} - {self.reading_datetime} ({self.total_kwh_consumption} kWh)"
        return f"Leitura em {self.reading_datetime} ({self.total_kwh_consumption} kWh)"

class EnergyTariff(BaseModel):
    """
    Define diferentes tarifas de energia elétrica.
    """
    class TariffTypeChoices(TextChoices):
        CONVENCIONAL = 'CONVENCIONAL', 'Convencional'
        COMERCIAL = 'COMERCIAL', 'Comercial'
        INDUSTRIAL = 'INDUSTRIAL', 'Industrial'
        BRANCA = 'BRANCA', 'Branca'
        AZUL = 'AZUL', 'Azul'
        VERDE = 'VERDE', 'Verde'
        RURAL = 'RURAL', 'Rural (Tarifa específica)'

    name = models.CharField(max_length=255, unique=True, null=False)
    description = models.TextField(blank=True, null=True)

    tariff_type = models.CharField(max_length=50, choices=TariffTypeChoices.choices, default=TariffTypeChoices.CONVENCIONAL)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    cost_per_kwh = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True,
        help_text="Custo único por kWh (para tarifas convencionais) (R$/kWh)."
    )
    peak_energy_price = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True,
        help_text="Preço da energia na ponta (R$/kWh) - para tarifas horosazonais."
    )
    intermediate_energy_price = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True,
        help_text="Preço da energia no período intermediário (Tarifa Branca) (R$/kWh)."
    )
    off_peak_energy_price = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True,
        help_text="Preço da energia fora de ponta (R$/kWh) - para tarifas horosazonais."
    )

    # Taxas de Demanda (R$/kW) - Opcionais, apenas para Grupo A
    peak_demand_charge = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, help_text="Custo da demanda na ponta (R$/kW).")
    off_peak_demand_charge = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, help_text="Custo da demanda fora de ponta (R$/kW).")

    peak_demand_overflow_charge = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, help_text="Custo por kW de ultrapassagem da demanda na Ponta (R$/kW).")
    off_peak_demand_overflow_charge = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, help_text="Custo por kW de ultrapassagem da demanda Fora de Ponta (R$/kW).")
    
    has_tiered_pricing = models.BooleanField(default=False, help_text="Indica se esta tarifa utiliza precificação por faixas de consumo.")

    availability_cost_kwh_franchise = models.IntegerField(null=True, blank=True, help_text="Franquia mínima de consumo em kWh para custo de disponibilidade (Grupo B).")
    tax_icms_aliquot = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True, help_text="Alíquota ICMS (%) para esta tarifa.")
    pis_aliquot = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True, help_text="Alíquota PIS (%) para esta tarifa.")
    cofins_aliquot = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True, help_text="Alíquota COFINS (%) para esta tarifa.")

    #has_tariff_flags = models.BooleanField(default=False, help_text="Esta tarifa utiliza bandeiras tarifárias?")

    #current_flag = models.ForeignKey('TariffFlagAdditive',on_delete=models.SET_NULL,null=True, blank=True,related_name='tariffs_with_current_flag',help_text="Bandeira tarifária atual aplicada a esta tarifa")

    class Meta:
        db_table = 'energy_tariffs'
        verbose_name = 'Energy Tariff'
        verbose_name_plural = 'Energy Tariffs'
        ordering = ['-start_date', 'name']

    def __str__(self):
        if self.cost_per_kwh:
            return f"{self.name} ({self.cost_per_kwh} R$/kWh)"
        elif self.tariff_type:
            return f"{self.name} ({self.get_tariff_type_display()})"
        return self.name
    
class EnergyTariffTier(BaseModel):
    """
    Define as faixas de consumo e seus respectivos preços para tarifas escalonadas (ex: Baixa Renda).
    Relacionado a um EnergyTariff específico com has_tiered_pricing=True.
    """
    tariff = models.ForeignKey(EnergyTariff, on_delete=models.CASCADE, related_name='tiers', help_text="Tarifa de energia à qual esta faixa de consumo pertence.")
    min_kwh = models.DecimalField(max_digits=10, decimal_places=2, help_text="Limite inferior da faixa de consumo em kWh (inclusive).")
    max_kwh = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Limite superior da faixa de consumo em kWh (exclusive). Null para faixa final 'acima de'.")
    price_per_kwh = models.DecimalField(max_digits=10, decimal_places=5, help_text="Preço por kWh para esta faixa de consumo (R$/kWh).")
    order = models.IntegerField(help_text="Ordem da faixa de consumo para processamento.")

    class Meta:
        unique_together = ('tariff', 'order') # Garante que as ordens sejam únicas por tarifa
        ordering = ['tariff', 'order']
        verbose_name = "Faixa de Tarifa de Energia"
        verbose_name_plural = "Faixas de Tarifas de Energia"

    def __str__(self):
        max_str = f"até {self.max_kwh} kWh" if self.max_kwh is not None else "acima de"
        return f"{self.tariff.name}: {self.min_kwh} kWh {max_str} - R$ {self.price_per_kwh}/kWh"


class TariffFlagAdditive(models.Model):
    """
    Registra os valores dos adicionais das Bandeiras Tarifárias por período.
    Homologados anualmente pela ANEEL.
    """
    class FlagChoices(TextChoices):
        GREEN = 'green', 'Verde'
        YELLOW = 'yellow', 'Amarela'
        RED1 = 'red1', 'Vermelha - Patamar 1'
        RED2 = 'red2', 'Vermelha - Patamar 2'
        WATER_SCARCITY = 'water_scarcity', 'Escassez Hídrica'

    flag_type = models.CharField(max_length=20, choices=FlagChoices.choices, null=False, unique=True) # Ex: 'yellow', 'red1'
    additional_cost_per_100kwh = models.DecimalField(max_digits=8, decimal_places=4, null=False, 
                                                 help_text="Adicional em R$ por 100 kWh")
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'tariff_flag_additives'
        verbose_name = 'Tariff Flag Additive'
        verbose_name_plural = 'Tariff Flag Additives'
        ordering = ['-start_date', 'flag_type']
        unique_together = ('flag_type', 'start_date', 'end_date')

    def __str__(self):
        return f"Bandeira {self.get_flag_type_display()}: (+R${self.additional_cost_per_100kwh}/100 kWh) - Válido de {self.start_date}"


class UserPreferences(models.Model):
    """
    Armazena preferências específicas do usuário, como tema e frequência de notificações.
    """
    class ThemeChoices(models.TextChoices):
        LIGHT = 'light', 'Claro'
        DARK = 'dark', 'Escuro'

    class NotificationFrequencyChoices(models.TextChoices):
        DAILY = 'daily', 'Diário'
        WEEKLY = 'weekly', 'Semanal'
        MONTHLY = 'monthly', 'Mensal'
        NEVER = 'never', 'Nunca'

    class ReportFormatChoices(models.TextChoices):
        PDF = 'pdf', 'PDF'
        CSV = 'csv', 'CSV'
        EXCEL = 'excel', 'Excel'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True, related_name='preferences')
    theme_preference = models.CharField(
        max_length=10,
        choices=ThemeChoices.choices,
        default=ThemeChoices.LIGHT
    )
    notification_frequency = models.CharField(
        max_length=10,
        choices=NotificationFrequencyChoices.choices,
        default=NotificationFrequencyChoices.DAILY
    )
    report_format_preference = models.CharField(
        max_length=10,
        choices=ReportFormatChoices.choices,
        default=ReportFormatChoices.PDF
    )
    receive_marketing_emails = models.BooleanField(default=True)
    phone_number = PhoneNumberField(
        blank=True,
        null=True,
        verbose_name='Número de Telefone',
        help_text='Número de telefone para notificações via SMS (formato: +55 11 912345678).'
    )
    receive_sms_notifications = models.BooleanField(
        default=False,
        verbose_name='Receber notificações por SMS'
    )
    receive_push_notifications = models.BooleanField(
        default=True,
        verbose_name='Receber notificações push no navegador'
    )

    class Meta:
        db_table = 'user_preferences'
        verbose_name = 'User Preference'
        verbose_name_plural = 'User Preferences'

    def __str__(self):
        return f"Preferências de {self.user.username}"

class Alert(BaseModel):
    """
    Representa um alerta gerado pelo sistema com base em condições predefinidas.
    """
    class AlertTypeChoices(TextChoices):
        HIGH_CONSUMPTION = 'high_consumption', 'Consumo Elevado'
        GOAL_EXCEEDED = 'goal_exceeded', 'Meta Excedida'
        OUTLIER_DETECTED = 'outliers_detected', 'Anomalia Detectada'
        MODEL_ACCURACY_LOW = 'model_accuracy_low', 'Acurácia do Modelo Baixa'
        SYSTEM_ERROR = 'system_error', 'Erro do Sistema'
        INFORMATION = 'information', 'Informação'
        CONSUMPTION_EXCEEDED = 'CONSUMPTION_EXCEEDED', 'Consumo Excedido'
        GOAL_THRESHOLD_REACHED = 'GOAL_THRESHOLD_REACHED', 'Limite de Meta Atingido'
        BILL_OVERDUE = 'BILL_OVERDUE', 'Fatura Vencida'
        PREDICTION_DEVIATION = 'PREDICTION_DEVIATION', 'Desvio de Previsão'
        QUALITY_ISSUE = 'QUALITY_ISSUE', 'Problema de Qualidade de Energia'

    class AlertSeverityChoices(models.IntegerChoices):
        LOW = 1, 'Baixa'
        MEDIUM = 2, 'Média'
        HIGH = 3, 'Alta'
        CRITICAL = 4, 'Crítica'


    profile = models.ForeignKey(EnergyProfiles, on_delete=models.RESTRICT, related_name='alerts', null=False)
    alert_type = models.CharField(max_length=50, choices=AlertTypeChoices.choices, default=AlertTypeChoices.INFORMATION)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='alerts', null=True, blank=True)
    message = models.TextField(null=False)
    is_read = models.BooleanField(default=False, help_text="Indica se o alerta foi lido.")
    
    threshold_value = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True) 
    current_value = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True, help_text="Valor atual que causou o alerta.")

    triggered_at = models.DateTimeField(auto_now_add=True, editable=False)
    is_resolved = models.BooleanField(default=False)
    alert_date = models.DateTimeField(
        default=datetime.now, 
        verbose_name='Data e Hora do Alerta'
    )
    suggested_actions = models.TextField(
        blank=True,
        null=True,
        verbose_name='Ações Sugeridas',
        help_text='Medidas que podem ser tomadas para resolver ou mitigar o alerta.'
    )
    related_goal = models.ForeignKey(
        'ConsumptionGoal',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alerts'
    )
    severity = models.IntegerField(
        choices=AlertSeverityChoices.choices,
        default=AlertSeverityChoices.MEDIUM, # Define um valor padrão para a severidade
        verbose_name='Severidade do Alerta',
        help_text='Nível de gravidade do alerta.'
    )
    class Meta:
        db_table = 'alerts'
        verbose_name = 'Alert'
        verbose_name_plural = 'Alerts'
        ordering = ['-triggered_at']

    def __str__(self):
        return f"Alerta para {self.profile.name}: ({self.alert_type}) em {self.alert_date.strftime('%Y-%m-%d %H:%M')}: {self.message[:50]}..."

# Em models.py (adicione este novo modelo)

class PushNotificationSubscription(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='push_subscriptions')
    endpoint = models.URLField(max_length=512, unique=True)
    p256dh = models.CharField(max_length=255)
    auth = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Push Notification Subscription'
        verbose_name_plural = 'Push Notification Subscriptions'

    def __str__(self):
        return f"Assinatura push para {self.user.username}"

class ConsumptionGoal(models.Model):
    """
    Define metas de consumo de energia para um perfil.
    """
    class GoalTypeChoices(TextChoices):
        KWH_REDUCTION_PERCENT = 'kwh_reduction_percent', 'Redução % de kWh'
        KWH_ABSOLUTE = 'kwh_absolute', 'Meta Absoluta de kWh'
        COST_TARGET = 'cost_target', 'Meta de Custo'

    profile = models.ForeignKey(EnergyProfiles, on_delete=models.RESTRICT, related_name='consumption_goals', null=False)
    name = models.CharField(max_length=255, null=False)
    goal_type = models.CharField(max_length=50, choices=GoalTypeChoices.choices, default=GoalTypeChoices.KWH_ABSOLUTE)
    target_value = models.DecimalField(max_digits=10, decimal_places=4, null=False)
    target_kwh = models.DecimalField(max_digits=10, null=True, decimal_places=4, help_text="Meta de consumo em kWh.")
    target_kwh_per_month = models.DecimalField(max_digits=10, decimal_places=2, help_text="Meta de consumo de energia em kWh por mês.")
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=False)
    description = models.TextField(blank=True, null=True, help_text="Descrição da meta.")
    alert_threshold_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('90.00'), help_text="Percentual da meta que, ao ser atingido, dispara um alerta.")
    is_active = models.BooleanField(default=True, help_text="Indica se esta meta de consumo está atualmente ativa.")
    achieved_date = models.DateField(null=True, blank=True) # Data em que a meta foi atingida

    class Meta:
        db_table = 'consumption_goals'
        verbose_name = 'Consumption Goal'
        verbose_name_plural = 'Consumption Goals'
        ordering = ['profile', '-start_date']
        unique_together = ('profile', 'name', 'start_date') # Garante metas únicas por perfil/nome/data

    def __str__(self):
        return f"Meta '{self.name}' para {self.profile.name} (Alvo: {self.target_value})"

class OptimizationSuggestion(models.Model):
    """
    Um catálogo de dicas de otimização de energia.
    """
    
    class CategoryChoices(TextChoices): # NOVA: Adicionando TextChoices para category
        APPLIANCES = 'appliances', 'Eletrodomésticos'
        EQUIPAMENTOS = 'EQUIPAMENTOS', 'Equipamentos'
        LIGHTING = 'ILUMINACAO', 'Iluminação'
        HEATING_COOLING = 'heating_cooling', 'Aquecimento e Refrigeração'
        COMPORTAMENTO = 'COMPORTAMENTO', 'Comportamento'
        INSULATION = 'insulation', 'Isolamento'
        MANUTENCAO = 'MANUTENCAO', 'Manutenção'
        GERACAO_PROPRIA = 'GERACAO_PROPRIA', 'Geração Própria'
        OTHER = 'other', 'Outro'

    class ImpactChoices(TextChoices):
        LOW = 'low', 'Baixo'
        MEDIUM = 'medium', 'Médio'
        HIGH = 'high', 'Alto'

    profile = models.ForeignKey(EnergyProfiles, on_delete=models.RESTRICT, null=False, related_name='optimization_suggestions')
    title = models.CharField(max_length=255, null=False, unique=True)
    description = models.TextField(null=False)

    estimated_savings_kwh = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True,
                                                help_text="Economia estimada em kWh (se aplicável).")
    estimated_savings_kwh_per_month = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    estimated_savings_money = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                                  help_text="Economia estimada em dinheiro (R$) (se aplicável).")
    is_implemented = models.BooleanField(default=False, help_text="Indica se a sugestão foi implementada.")
    suggested_at = models.DateTimeField(auto_now_add=True, help_text="Data e hora em que a sugestão foi gerada.")
    category = models.CharField(max_length=50, choices=CategoryChoices.choices, default=CategoryChoices.APPLIANCES)
    procel_seal_target = models.CharField(max_length=10, blank=True, null=True, 
                                          help_text="Selo Procel visado para esta sugestão (Ex: A)")
    impact_level = models.CharField(max_length=10, choices=ImpactChoices.choices)
    

    class Meta:
        db_table = 'optimization_suggestions'
        verbose_name = 'Optimization Suggestion'
        verbose_name_plural = 'Optimization Suggestions'
        ordering = ['-suggested_at', 'profile__name']

    def __str__(self):
        return f"Sugestão para {self.profile.name}: {self.title}"

class DeviceUsagePattern(models.Model):
    """
    Define padrões de uso mais detalhados para dispositivos em um perfil.
    """
    
    class DayChoices(IntegerChoices):
        MONDAY = 0, 'Segunda-feira'
        TUESDAY = 1, 'Terça-feira'
        WEDNESDAY = 2, 'Quarta-feira'
        THURSDAY = 3, 'Quinta-feira'
        FRIDAY = 4, 'Sexta-feira'
        SATURDAY = 5, 'Sábado'
        SUNDAY = 6, 'Domingo'

    id = models.BigAutoField(primary_key=True)
    profile_device = models.ForeignKey(ProfileDevices, on_delete=models.CASCADE, related_name='usage_patterns')
    hour_of_day = models.IntegerField(help_text="Hora do dia (0-23).")
    usage_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Porcentagem de uso do dispositivo naquela hora (0.00-100.00).")
    day_of_week = models.IntegerField(choices=DayChoices.choices, null=False)
    start_time = models.TimeField(null=False)
    end_time = models.TimeField(null=False)
    kwh_consumption = models.DecimalField(
        max_digits=10, 
        decimal_places=4,
        verbose_name='Consumo (kWh)',
        help_text='Consumo de energia do dispositivo durante o período de uso.'
    )
    intensity_factor = models.DecimalField(max_digits=4, decimal_places=2, default=1.0, null=False) 
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'device_usage_patterns'
        verbose_name = 'Device Usage Pattern'
        verbose_name_plural = 'Device Usage Patterns'
        unique_together = ('profile_device', 'day_of_week', 'start_time', 'end_time') # Garante padrão único
        ordering = ['profile_device', 'day_of_week', 'start_time']

    def __str__(self):
        return (f"Padrão de uso para {self.profile_device} {self.profile_device.name or self.profile_device.device.name} "
                f"na {self.get_day_of_week_display()} de {self.start_time.strftime('%H:%M')} a {self.end_time.strftime('%H:%M')}")


class HistoricalPredictionComparison(models.Model):
    """
    Compara o consumo real observado com as previsões para avaliação de modelo.
    """
    profile = models.ForeignKey(EnergyProfiles, on_delete=models.RESTRICT, null=False, related_name='prediction_comparisons')
    prediction = models.OneToOneField(ConsumptionPredictions, on_delete=models.CASCADE, primary_key=True, related_name='comparison')
    actual_kwh = models.DecimalField(max_digits=10, decimal_places=4, null=False)
    comparison_date = models.DateField(null=False)
    deviation = models.DecimalField(max_digits=10, decimal_places=4, help_text="Diferença entre previsto e real.")
    error_kwh = models.DecimalField(max_digits=10, decimal_places=4, null=False) # Erro absoluto
    percentage_error = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) # Erro percentual
    deviation_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Desvio em porcentagem.")


    class Meta:
        db_table = 'historical_prediction_comparisons'
        verbose_name = 'Historical Prediction Comparison'
        verbose_name_plural = 'Historical Prediction Comparisons'
        unique_together = ('profile', 'comparison_date')
        ordering = ['-comparison_date', 'profile__name']

    def __str__(self):
        return f"Comparação para {self.profile.name} em {self.prediction.prediction_date}: Previsto {self.prediction.predicted_daily_kwh} kWh, vs Real {self.actual_kwh} kWh"

    def save(self, *args, **kwargs):
        # Calcula o erro e o erro percentual antes de salvar
        if self.prediction.predicted_daily_kwh is not None and self.actual_kwh is not None:
            self.error_kwh = abs(self.actual_kwh - self.prediction.predicted_daily_kwh)
            if self.actual_kwh != 0:
                self.percentage_error = (self.error_kwh / self.actual_kwh) * 100
            else:
                self.percentage_error = None # Evita divisão por zero
        super().save(*args, **kwargs)

# models.py (Adicionar este novo modelo)

class EnergyQualityRecord(BaseModel):
    """
    Registra indicadores de continuidade e qualidade do fornecimento de energia
    para um perfil de energia específico, conforme informações da fatura.
    """
    class RecordTypeChoices(TextChoices): 
        INTERRUPTION = 'INTERRUPTION', 'Interrupção de Energia'
        VOLTAGE_FLUCTUATION = 'VOLTAGE_FLUCTUATION', 'Flutuação de Tensão'
        OUTAGE = 'OUTAGE', 'Queda de Energia (Blackout)'

    profile = models.ForeignKey(
        'EnergyProfiles',
        on_delete=models.RESTRICT,
        null=False,
        related_name='energy_quality_records',
        help_text="Perfil de energia ao qual este registro de qualidade se refere."
    )
    record_datetime = models.DateTimeField(help_text="Data do registro de qualidade de energia")
    record_type = models.CharField(max_length=100, choices=RecordTypeChoices.choices, help_text="Tipo de registro de qualidade de energia.") 
    total_duration_interruptions_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Duração total das interrupções no mês em horas (ex: 0.5 para 30 min)."
    )
    voltage_level = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Nível de tensão medido durante o evento (V) (se aplicável).")

    # NOVOS CAMPOS ADICIONADOS
    # Interrupções
    #num_interruptions_programed = models.IntegerField(default=0, help_text="Número de interrupções programadas (Ex: manutenção)")
    #num_interruptions_unprogramed = models.IntegerField(default=0, help_text="Número de interrupções não programadas (Ex: falhas na rede)")
    
    # Flutuações de Tensão
    num_voltage_fluctuations = models.IntegerField(default=0, help_text="Número de flutuações de tensão (Ex: quedas ou picos)")
    avg_voltage_variation = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Variação média da tensão (%)")

    # Harmônicas
    thd_voltage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Distorção Harmônica Total de Tensão (THD-V %)")
    thd_current = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Distorção Harmônica Total de Corrente (THD-I %)")

    # Indicadores de Continuidade (DIC/FIC/DMIC/DICRI - Se disponíveis com mais granularidade)
    # Assumindo a fatura fornece 'Número de Interrupções' e 'Duração (h:min)' por mês.
    num_interruptions = models.IntegerField(
        default=0,
        help_text="Número de interrupções individuais no mês."
    )
    # Pode-se adicionar campos para DIC, FIC, DMIC, DICRI se a fatura os detalhar individualmente
    # Exemplo:
    # dic_duration = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Duração de Interrupção por Unidade Consumidora (DIC) em horas.")
    # fic_frequency = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Frequência de Interrupção por Unidade Consumidora (FIC).")
    # ... e outros conforme o detalhamento da fatura ...

    tariff_flag_applied = models.CharField(
        max_length=20,
        choices=TariffFlagTypeChoices.choices,
        null=True,
        blank=True,
        help_text="Bandeira tarifária aplicada no mês de referência (ex: Verde, Amarela)."
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Observações adicionais sobre a qualidade do serviço no período."
    )

    class Meta:
        db_table = 'energy_quality_records'
        verbose_name = 'Energy Quality Record'
        verbose_name_plural = 'Energy Quality Records'
        unique_together = ('profile', 'record_datetime') # Um registro de qualidade por perfil por mês
        ordering = ['-record_datetime', 'profile']

    def __str__(self):
        return f"Qualidade de Energia para {self.profile.name} em {self.record_datetime.strftime('%Y-%m-%d %H:%M')}"


class BillingRecord(BaseModel):
    """
    Representa um registro de conta de energia (simulado ou real) para um perfil.
    Agora inclui informações sobre a bandeira tarifária aplicada.
    """

    profile = models.ForeignKey(EnergyProfiles, on_delete=models.RESTRICT, related_name='billing_records', null=False)
    bill_type = models.CharField(
        max_length=20,
        choices=BillTypeChoices.choices,
        help_text="Tipo de fatura (ex: Convencional, Tarifa Branca, Alta Tensão)"
    )

     # Informações básicas da fatura
    bill_number = models.CharField(max_length=50, unique=True, help_text="Número único da fatura.")
    invoice_date = models.DateField(help_text="Data de emissão da fatura.")
    due_date = models.DateField(help_text="Data de vencimento da fatura.")
    start_period = models.DateField(null=False, help_text="Data de início do período de consumo faturado")
    end_period = models.DateField(null=False, help_text="Data de fim do período de consumo faturado")

    # Detalhamento de valores da fatura
    # Energia
    energy_charge_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Valor total da energia consumida (R$).")
    
    # Demanda
    demand_charge_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Valor total da demanda faturada (R$).")
    contracted_demand_peak_kw = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Demanda contratada na ponta (kW).") # Apenas para Grupo A
    contracted_demand_off_peak_kw = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Demanda contratada fora de ponta (kW).") # Apenas para Grupo A
    billed_demand_peak_kw = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Demanda faturada na ponta (kW).") # Apenas para Grupo A
    billed_demand_off_peak_kw = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Demanda faturada fora de ponta (kW).") # Apenas para Grupo A

    # Custo de Disponibilidade (para Grupo B)
    availability_cost_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Valor do custo de disponibilidade (R$).")

    
    days_billed = models.IntegerField(null=True, blank=True, help_text="Número de dias faturados")

    kwh_total_billed = models.DecimalField(max_digits=10, decimal_places=4, null=False, help_text="Consumo total em kWh faturado")
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=False, help_text="Custo do valor total da fatura (R$)")
    
    # Detalhes de preço unitário do kWh conforme o talão
    unit_price_kwh = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True, help_text="Preço unitário do kWh (com impostos) R$/kWh")
    tariff_unit_kwh = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True, help_text="Tarifa unitária do kWh (sem impostos) R$/kWh")

    energy_tariff_used = models.ForeignKey(
        EnergyTariff,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='billed_records',
        help_text="Tarifa base utilizada para esta fatura."
    )

    applied_tariff_flag = models.CharField(
        max_length=20,
        choices=TariffFlagTypeChoices.choices,
        null=True, blank=True,
        help_text="Bandeira tarifária aplicada a esta fatura (ex: VERDE, AMARELA)."
    )

    applied_tariff_flag_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Custo da bandeira tarifária aplicada (R$).")
    flag_additional_cost_per_100kwh = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True,
                                                        help_text="Adicional da Bandeira Tarifária em R$ por 100 kWh")
    
    # Detalhes do Medidor
    meter_id = models.CharField(max_length=100, blank=True, null=True, help_text="Número de identificação do medidor na fatura.")
    previous_reading = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, help_text="Leitura anterior do medidor na fatura.")
    current_reading = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, help_text="Leitura atual do medidor na fatura.")
    meter_constant = models.DecimalField(max_digits=8, decimal_places=3, default=Decimal('1.0'), help_text="Constante do medidor (geralmente 1.0).")
    next_reading_date = models.DateField(null=True, blank=True, help_text="Data da próxima leitura prevista na fatura.")

    # Detalhes de Tributos e Encargos
    icms_base = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Base de cálculo do ICMS (R$).")
    icms_aliquot = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True, help_text="Alíquota do ICMS (%) na fatura. (Ajustado para 4 casas)")
    icms_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Valor do ICMS (R$) na fatura.")
    
    pis_base = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Base de cálculo do PIS (R$).")
    pis_aliquot = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True, help_text="Alíquota do PIS (%). (Ajustado para 4 casas)")
    pis_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Valor do PIS (R$) na fatura.")
    
    cofins_base = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Base de cálculo do COFINS (R$).")
    cofins_aliquot = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True, help_text="Alíquota do COFINS (%). (Ajustado para 4 casas)")
    cofins_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Valor do COFINS (R$) na fatura.")
    
    cip_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Custo da Contribuição de Iluminação Pública (CIP) (R$).")
    meter_rental_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Custo de aluguel do medidor (R$).")
    fine_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Valor de Multa (R$).")
    monetary_correction_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Valor de Correção Monetária (R$).")
    interest_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Valor de Juros (R$).")

    notes = models.TextField(blank=True, null=True, help_text="Observações adicionais sobre a fatura")

    def save(self, *args, **kwargs):
        # Garante que temos valores numéricos para calcular e evita erros
        kwh_billed = self.kwh_total_billed or Decimal('0.0')
        total_cost_val = self.total_cost or Decimal('0.0')
        energy_charge_val = self.energy_charge_total or Decimal('0.0')

        # Proteção contra divisão por zero
        if kwh_billed > 0:
            # Calcula o preço unitário com impostos
            self.unit_price_kwh = total_cost_val / kwh_billed
            # Calcula a tarifa unitária sem impostos
            self.tariff_unit_kwh = energy_charge_val / kwh_billed
        else:
            self.unit_price_kwh = Decimal('0.0')
            self.tariff_unit_kwh = Decimal('0.0')

        # Chama o método save original para salvar o objeto no banco de dados
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'billing_records'
        verbose_name = 'Billing Record'
        verbose_name_plural = 'Billing Records'
        ordering = ['-invoice_date']
        unique_together = ('profile', 'invoice_date')

    def __str__(self):
        return f"Fatura de {self.profile.name} em {self.invoice_date} - ({self.total_cost} R$)"