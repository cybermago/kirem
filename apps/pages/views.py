from multiprocessing.pool import AsyncResult
from django.conf import settings
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView 
)
from django.views.generic.edit import FormView
import json
import plotly.graph_objects as go 
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Prefetch, Q, Sum
from django.http import HttpResponse, JsonResponse
import pandas as pd
import pytz
from django.contrib import messages
from django.utils.timesince import timesince
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import EnergyReadingSerializer
from .permissions import HasValidAPIKey

from .models import KPI, Alert, BillingRecord, ConsumptionGoal, DeviceCatalog, DeviceUsagePattern, EnergyProfiles, EnergyQualityRecord, EnergyReading, EnergyTariff, HistoricalPredictionComparison, OptimizationSuggestion, PredictionModels, ProfileDevices, ConsumptionPredictions, ModelAccuracyScores, TariffFlagAdditive, UserPreferences
from .forms import AlertForm, BillingRecordForm, ConsumptionGoalForm, DeviceCatalogForm, DeviceUsagePatternForm, EnergyProfilesForm, EnergyQualityRecordForm, EnergyReadingForm, EnergyTariffForm, HistoricalPredictionComparisonForm, KPIForm, ModelAccuracyScoresForm, OptimizationSuggestionForm, PredictionModelsForm, ProfileDevicesForm, ReportGeneratorForm, TariffFlagAdditiveForm, UserPreferencesForm
from .utils import analyze_interruptions_consumption_correlation, calculate_benchmark_data, check_consumption_goal_alerts, check_energy_quality_alerts, check_high_consumption_outliers, generate_custom_report, get_consumption_goals_overview, get_latest_kwh_data, get_model_accuracy_scatter_chart_data, get_outlier_detection_chart_data, get_prediction_comparison_analytics, get_quality_of_service_data, monitoring_performance_and_consumption, calculate_comprehensive_trends_data, calculate_forecast_data

# Create your views here.
def get_brazil_timezone():

    return pytz.timezone('America/Sao_Paulo') 

def index(request):

    return render(request, 'pages/dashboard.html', {'segment': 'dashboard'})

class PublicLandingView(TemplateView):
    """
    View para a página pública de aterrissagem. Não requer autenticação.
    """
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Você pode adicionar qualquer dado estático que a página de aterrissagem precise aqui
        # Por exemplo, uma lista de recursos, depoimentos, etc.
        context['page_title'] = 'EcoTrack - Seu Futuro Sustentável Começa Aqui'
        return context

class DashboardContextMixin:
    """
    Mixin para fornecer dados contextuais ao dashboard principal.
    Pode ser usado para todos os perfis do usuário ou para um perfil específico.
    """
    def get_dashboard_context_data(self, **kwargs):
        context = {}
        user = self.request.user
        profile_pk = self.kwargs.get('profile_pk') # Permite filtrar por perfil se houver na URL

        if profile_pk:
            # Se um profile_pk for fornecido, filtra para aquele perfil
            profiles = EnergyProfiles.objects.filter(pk=profile_pk, user=user)
            if not profiles.exists():
                context['error_message'] = "Perfil não encontrado ou você não tem permissão para acessá-lo."
                return context
        else:
            # Caso contrário, pega todos os perfis do usuário
            profiles = EnergyProfiles.objects.filter(user=user)
        
        if not profiles.exists():
            context['no_profiles_message'] = "Você não possui perfis de energia cadastrados. Crie um para ver seus dados de consumo."
            return context

        # Métricas Chave (Top Cards)
        brazil_tz = get_brazil_timezone() 
        today = datetime.now(brazil_tz).date()
        start_of_month = today.replace(day=1)
        end_of_month = (start_of_month + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        
        # Consumo e Custo (Mês Atual)
        current_month_readings = EnergyReading.objects.filter(
            profile__in=profiles,
            reading_datetime__range=[start_of_month, end_of_month]
        ).aggregate(total_kwh=Sum('total_kwh_consumption'))
        
        current_month_bills = BillingRecord.objects.filter(
            profile__in=profiles,
            invoice_date__range=[start_of_month, end_of_month]
        ).aggregate(total_cost=Sum('total_cost'))
        
        total_kwh_month = current_month_readings['total_kwh'] or Decimal('0.0')
        total_cost_month = current_month_bills['total_cost'] or Decimal('0.0')

        # Consumo do Mês Anterior para Comparação
        last_month_start = (start_of_month - timedelta(days=1)).replace(day=1)
        last_month_end = (start_of_month - timedelta(days=1))
        
        last_month_readings = EnergyReading.objects.filter(
            profile__in=profiles,
            reading_datetime__range=[last_month_start, last_month_end]
        ).aggregate(total_kwh=Sum('total_kwh_consumption'))
        
        total_kwh_last_month = last_month_readings['total_kwh'] or Decimal('0.0')

        kwh_diff = total_kwh_month - total_kwh_last_month
        kwh_percentage_change = (kwh_diff / total_kwh_last_month * Decimal('100')) if total_kwh_last_month else Decimal('0.0')

        # Emissões de CO2 (exemplo, você pode precisar de um fator de conversão real)
        # Fator de conversão: 1 kWh = ~0.08 kg de CO2 (aproximado para energia no Brasil)
        co2_factor_kg_per_kwh = Decimal(settings.CO2_EMISSION_FACTOR_KG_PER_KWH)
        total_co2_emissions_kg = total_kwh_month * co2_factor_kg_per_kwh


        context['total_kwh_month'] = total_kwh_month
        context['total_cost_month'] = total_cost_month
        context['kwh_percentage_change'] = kwh_percentage_change
        context['total_co2_emissions_kg'] = total_co2_emissions_kg


        # Dados para Gráficos
        # Gráfico 1: Consumo Mensal Histórico (Chart.js Line Chart)
        # Buscar dados de BillingRecord ou EnergyReading (monthly)
        monthly_consumption_history = BillingRecord.objects.filter(
            profile__in=profiles
        ).order_by('invoice_date').values('invoice_date', 'kwh_total_billed')
        
        if not monthly_consumption_history.exists():
             monthly_consumption_history = EnergyReading.objects.filter(
                profile__in=profiles,
                reading_period='monthly' # ou agregação mensal de diários/horários
            ).order_by('reading_datetime').values('reading_datetime', 'total_kwh_consumption')
        
        # Agrega por mês/ano para evitar múltiplos pontos para o mesmo mês
        monthly_labels = []
        monthly_data = []
        if monthly_consumption_history.exists():
            df_monthly = pd.DataFrame(list(monthly_consumption_history))
            if 'invoice_date' in df_monthly.columns:
                df_monthly.rename(columns={'invoice_date': 'date', 'kwh_total_billed': 'consumption'}, inplace=True)
            elif 'reading_datetime' in df_monthly.columns:
                df_monthly.rename(columns={'reading_datetime': 'date', 'total_kwh_consumption': 'consumption'}, inplace=True)
            
            df_monthly['date'] = pd.to_datetime(df_monthly['date'], errors='coerce')
# Remove as linhas com datas que não puderam ser convertidas
            df_monthly.dropna(subset=['date'], inplace=True)
            df_monthly['month_year'] = df_monthly['date'].dt.to_period('M')
            monthly_aggregated = df_monthly.groupby('month_year')['consumption'].sum().reset_index()
            monthly_aggregated = monthly_aggregated.sort_values('month_year')

            monthly_labels = [m.strftime('%b/%Y') for m in monthly_aggregated['month_year'].dt.to_timestamp()]
            monthly_data = monthly_aggregated['consumption'].tolist()

            monthly_data = [float(item) for item in monthly_data]

        context['monthly_consumption_labels'] = json.dumps(monthly_labels)
        context['monthly_consumption_data'] = json.dumps(monthly_data)

        # Gráfico 2: Consumo Diário Agregado por Horário ou Tipo de Dispositivo (Chart.js Bar Chart)
        # Vamos usar uma simulação ou agregação de ProfileDevices para o momento
        # Para um cenário real, precisaríamos de EnergyReading com timestamps detalhados
        daily_kwh_per_device_type = {}
        for profile_device in ProfileDevices.objects.filter(profile__in=profiles).select_related('device'):
            device_name = profile_device.device.name
            daily_kwh = profile_device.daily_kwh_consumption # Propriedade calculada no modelo
            daily_kwh_per_device_type[device_name] = daily_kwh_per_device_type.get(device_name, 0.0) + float(daily_kwh)
        
        device_labels = list(daily_kwh_per_device_type.keys())
        device_consumption_data = list(daily_kwh_per_device_type.values())

        context['daily_device_labels'] = json.dumps(device_labels)
        context['daily_device_consumption_data'] = json.dumps(device_consumption_data)

        # Gráfico 3: Desempenho de Metas de Consumo (Chart.js Line Chart - "Completed Tasks" refatorado)
        # Simula o desempenho de metas para o propósito do dashboard principal
        goal_labels = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"] # Exemplo de meses
        goal_completion_data = [60, 75, 80, 90, 85, 95] # Exemplo de % de conclusão
        
        context['goal_labels'] = json.dumps(goal_labels)
        context['goal_completion_data'] = json.dumps(goal_completion_data)
        context['goal_tasks_message'] = f"{len(profiles.first().consumption_goals.filter(is_active=True))} metas ativas este mês" if profiles.exists() and profiles.first().consumption_goals.filter(is_active=True).exists() else "Nenhuma meta ativa"


        # Seção de Alertas Recentes (substituindo 'Projects')
        recent_alerts = Alert.objects.filter(user=user).order_by('-triggered_at')[:5] # Últimos 5 alertas
        context['recent_alerts'] = recent_alerts

        # Seção de Sugestões de Otimização (substituindo 'Orders overview')
        # Poderíamos pegar sugestões gerais ou baseadas nos KPIs do usuário
        optimization_suggestions = OptimizationSuggestion.objects.all().order_by('-impact_level')[:5]
        context['optimization_suggestions_list'] = optimization_suggestions

        return context


class DashboardView(LoginRequiredMixin, DashboardContextMixin, TemplateView):
    """
    View principal do Dashboard.
    Usa o DashboardContextMixin para carregar dados relevantes.
    """
    template_name = 'pages/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona os dados do mixin ao contexto
        context.update(self.get_dashboard_context_data(**kwargs))
        context['page_title'] = 'Dashboard de Energia'
        return context

class SuperuserRequiredMixin(UserPassesTestMixin):
    """Garante que o usuário é um superusuário."""
    def test_func(self):
        return self.request.user.is_superuser
    

def unread_notification_count_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'unread_count': 0})
    
    count = Alert.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': count})


class UserProfileView(LoginRequiredMixin, TemplateView):
    """
    View completa e robusta para exibir o perfil do usuário logado,
    incluindo seus EnergyProfiles associados e outros detalhes.
    """
    template_name = 'profiles/profile.html' # Define o template a ser renderizado

    def get_context_data(self, **kwargs):
        """
        Adiciona dados ao contexto que serão passados para o template.
        """
        context = super().get_context_data(**kwargs)
        
        # Define o segmento para ativar o link correto no sidebar
        context['segment'] = 'profile' 

        user = self.request.user # O usuário logado está disponível via self.request.user

        # --- Dados do Usuário Logado ---
        # O template já usa {{ request.user.username }}, {{ request.user.email }}, etc.
        # Adicionar ao contexto é redundante para estes campos, mas não causa problemas.
        context['username'] = user.username
        context['email'] = user.email
        context['first_name'] = user.first_name
        context['last_name'] = user.last_name
        
        # Exemplo: Se você tiver um campo 'job_title' ou 'full_name' no modelo User (extensão)
        # ou em um modelo UserProfile relacionado (ex: OneToOneField com o User)
        # if hasattr(user, 'userprofile') and user.userprofile:
        #     context['user_job_title'] = user.userprofile.job_title
        #     context['user_full_name'] = user.userprofile.full_name
        # else:
        #     context['user_job_title'] = "Usuário do Sistema"
        #     context['user_full_name'] = f"{user.first_name} {user.last_name}".strip() or user.username


        # --- EnergyProfiles Associados ao Usuário ---
        # Filtra os EnergyProfiles que pertencem ao usuário logado.
        # Ordena por data de criação para consistência.
        user_profiles = EnergyProfiles.objects.filter(user=user).order_by('-created_at')
        
        # CORREÇÃO AQUI: Renomeie 'user_profiles_list' para 'energy_profiles'
        # para corresponder ao que o template 'profile.html' espera.
        context['energy_profiles'] = user_profiles

        # --- Outros Dados (Opcional, dependendo do seu profile.html) ---
        # Se você tiver outras informações que deseja exibir diretamente no perfil do usuário,
        # como as preferências de usuário, você pode adicioná-las aqui.
        # Exemplo:
        # try:
        #     context['user_preferences'] = UserPreferences.objects.get(user=user)
        # except UserPreferences.DoesNotExist:
        #     context['user_preferences'] = None # Ou um objeto padrão/vazio


        # O título da página será definido pelo bloco {% block title %} no template
        # mas você pode definir um valor padrão aqui se preferir.
        # context['page_title'] = "Meu Perfil de Usuário"

        return context
    
class SensorDataIngestionView(APIView):
    """
    Recebe e processa dados de sensores externos.
    """
    # Define que esta view requer uma chave de API válida para ser acessada.
    permission_classes = [HasValidAPIKey]

    def post(self, request):
        serializer = EnergyReadingSerializer(data=request.data)
        if serializer.is_valid():
            # O 'profile' foi adicionado ao request pela nossa classe de permissão (próximo passo).
            # Associamos a leitura ao perfil correto antes de salvar.
            serializer.save(profile=request.profile, user=request.profile.user)
            return Response(
                {"status": "success", "message": "Dados recebidos e salvos."},
                status=status.HTTP_201_CREATED
            )
        # Se os dados forem inválidos, retorna os erros de validação.
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SensorStatusView(LoginRequiredMixin, TemplateView):
    template_name = 'sensors/status.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        context['all_user_profiles'] = user_profiles

        # Pega o perfil do parâmetro GET ou o primeiro perfil do usuário
        selected_pk = self.request.GET.get('profile_pk')
        profile = None
        if selected_pk:
            profile = user_profiles.filter(pk=selected_pk).first()
        elif user_profiles.exists():
            profile = user_profiles.first()
        
        context['profile'] = profile
        if not profile:
            return context

        # Lógica para status inicial
        last_reading = EnergyReading.objects.filter(profile=profile).order_by('-reading_datetime').first()
        now = datetime.now()
        
        status_info = {'text': 'Desconhecido', 'color': 'secondary', 'icon': 'help'}
        if last_reading:
            time_diff_seconds = (now - last_reading.reading_datetime).total_seconds()
            if time_diff_seconds < 300: # Menos de 5 minutos
                status_info = {'text': 'Conectado', 'color': 'success', 'icon': 'wifi'}
            else:
                status_info = {'text': 'Inativo', 'color': 'warning', 'icon': 'wifi_off'}
            context['last_reading_time_ago'] = f"{timesince(last_reading.reading_datetime)} atrás"
            context['last_reading_timestamp_iso'] = last_reading.reading_datetime.isoformat()
        else:
            status_info = {'text': 'Aguardando Dados', 'color': 'info', 'icon': 'hourglass_top'}
            context['last_reading_time_ago'] = "Nunca"
            context['last_reading_timestamp_iso'] = ""

        context['connection_status'] = status_info
        context['recent_readings'] = EnergyReading.objects.filter(profile=profile).order_by('-reading_datetime')[:10]
        context['readings_last_hour'] = EnergyReading.objects.filter(
            profile=profile, reading_datetime__gte=now - timedelta(hours=1)
        ).count()
        
        return context

def sensor_status_api(request, profile_pk):
    # Lógica da API para polling
    profile = get_object_or_404(EnergyProfiles, pk=profile_pk, user=request.user)
    last_known_timestamp = request.GET.get('last_timestamp')

    # Lógica de status (igual à da view principal)
    last_reading = EnergyReading.objects.filter(profile=profile).order_by('-reading_datetime').first()
    now = datetime.now()
    status_info = {'text': 'Desconhecido', 'color': 'secondary', 'icon': 'help'}
    last_reading_time_ago = "Nunca"
    last_reading_timestamp_iso = ""

    if last_reading:
        if (now - last_reading.reading_datetime).total_seconds() < 300:
            status_info = {'text': 'Conectado', 'color': 'success', 'icon': 'wifi'}
        else:
            status_info = {'text': 'Inativo', 'color': 'warning', 'icon': 'wifi_off'}
        last_reading_time_ago = f"{timesince(last_reading.reading_datetime)} atrás"
        last_reading_timestamp_iso = last_reading.reading_datetime.isoformat()
    
    # Busca leituras mais novas que a última conhecida pelo frontend
    new_readings_query = EnergyReading.objects.filter(profile=profile)
    if last_known_timestamp:
        new_readings_query = new_readings_query.filter(reading_datetime__gt=last_known_timestamp)
    
    new_readings = [{
        'time': r.reading_datetime.strftime('%H:%M:%S'),
        'kwh': r.total_kwh_consumption
    } for r in new_readings_query.order_by('reading_datetime')]
    
    readings_last_hour = EnergyReading.objects.filter(
        profile=profile, reading_datetime__gte=now - timedelta(hours=1)
    ).count()

    data = {
        'connection_status': status_info,
        'last_reading_time_ago': last_reading_time_ago,
        'last_reading_timestamp_iso': last_reading_timestamp_iso,
        'new_readings': new_readings,
        'readings_last_hour': readings_last_hour,
    }
    return JsonResponse(data)


# --- DeviceCatalog CRUD ---

class DeviceCatalogListView(ListView):
    """
    Lista todos os dispositivos no catálogo. (READ all)
    """
    model = DeviceCatalog
    template_name = 'devices/device_catalog_list.html'
    context_object_name = 'devices' # O nome da variável que será usada no template

class DeviceCatalogDetailView(DetailView):
    """
    Exibe os detalhes de um único dispositivo. (READ one)
    """
    model = DeviceCatalog
    template_name = 'devices/device_catalog_detail.html'
    context_object_name = 'device'

class DeviceCatalogCreateView(CreateView):
    """
    Permite criar um novo dispositivo no catálogo. (CREATE)
    """
    model = DeviceCatalog
    form_class = DeviceCatalogForm # Usa o formulário que definimos
    template_name = 'devices/device_catalog_form.html'
    success_url = reverse_lazy('device_list') # Redireciona após criar com sucesso

class DeviceCatalogUpdateView(UpdateView):
    """
    Permite atualizar um dispositivo existente no catálogo. (UPDATE)
    """
    model = DeviceCatalog
    form_class = DeviceCatalogForm
    template_name = 'devices/device_catalog_form.html'
    success_url = reverse_lazy('device_list') # Redireciona após atualizar com sucesso

class DeviceCatalogDeleteView(DeleteView):
    """
    Permite deletar um dispositivo do catálogo. (DELETE)
    """
    model = DeviceCatalog
    template_name = 'devices/device_catalog_confirm_delete.html'
    success_url = reverse_lazy('device_list') # Redireciona após deletar com sucesso


# --- EnergyProfiles CRUD (Gerenciar Perfis de Consumo - CRUD 1) ---

class EnergyProfileListView(LoginRequiredMixin, ListView):
    """
    Lista todos os perfis de energia do usuário logado.
    """
    model = EnergyProfiles
    template_name = 'energy_profiles/energy_profile_list.html' # Template que exibirá os cards
    context_object_name = 'profiles'
    paginate_by = 6 # Exemplo de paginação para cards

    def get_queryset(self):
        """
        Retorna apenas os perfis pertencentes ao usuário logado.
        """
        return EnergyProfiles.objects.filter(user=self.request.user).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Formulário para criar um novo perfil, que será usado no modal
        context['form'] = EnergyProfilesForm() 
        return context


class EnergyProfileDetailView(LoginRequiredMixin, DetailView):
    """
    Exibe os detalhes de um perfil de energia específico e os dispositivos associados.
    Aqui é onde o CRUD embutido para ProfileDevices será exibido.
    """
    model = EnergyProfiles
    template_name = 'energy_profiles/energy_profile_detail.html'
    context_object_name = 'profile'

    def get_queryset(self):
        """
        Garanta que o usuário só possa ver seus próprios perfis.
        Pré-carrega os ProfileDevices para otimizar a consulta.
        """
        return EnergyProfiles.objects.filter(user=self.request.user).prefetch_related(
            Prefetch('profile_devices', queryset=ProfileDevices.objects.select_related('device').order_by('name'))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Formulário para adicionar um novo ProfileDevice a este perfil
        context['profile_device_form'] = ProfileDevicesForm()
        # Obtém os dispositivos associados a este perfil
        context['profile_devices'] = self.object.profile_devices.all()
        # Passa o ID do perfil para o template, útil para as URLs de ProfileDevices
        context['profile_pk'] = self.object.pk
        return context

    
class EnergyProfileCreateView(LoginRequiredMixin, CreateView):
    model = EnergyProfiles
    form_class = EnergyProfilesForm
    template_name = 'energy_profiles/energy_profile_list.html' 
    success_url = reverse_lazy('profile_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['create_form'] = kwargs.get('form', EnergyProfilesForm())
        
        # Também passa a lista de perfis para que a página de listagem seja renderizada corretamente
        context['profiles'] = EnergyProfiles.objects.filter(user=self.request.user).order_by('name')
        return context
    
    def form_valid(self, form):
        # MUITO IMPORTANTE: Associa o usuário logado ao perfil ANTES de salvar.
        # Isso garante que o campo 'user' no modelo EnergyProfiles seja preenchido.
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Perfil de consumo criado com sucesso!')
        return response

    def form_invalid(self, form):
        # Para depuração, imprima os erros do formulário no terminal do VS Code
        print("\n--- ERROS DO FORMULÁRIO (EnergyProfilesCreateView) ---")
        print(form.errors.as_data()) # Imprime todos os erros, incluindo non_field_errors
        print("---------------------------------------------------\n")
        messages.error(self.request, 'Erro ao criar perfil. Verifique os campos com erro.')
        # Para o caso de modal, o ideal seria que ele reabrisse com os erros.
        # Uma forma simples para depuração seria redirecionar e mostrar os erros no template
        # mas para modais complexos, AJAX seria melhor.
        return super().form_invalid(form) # Isso renderiza o template novamente com os erros

    def get_success_url(self):
        """
        Redireciona para a lista de perfis após a criação.
        """
        return reverse_lazy('profile_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class EnergyProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    Atualiza um perfil de energia existente.
    """
    model = EnergyProfiles
    form_class = EnergyProfilesForm
    template_name = 'energy_profiles/energy_profile_form.html' 
    
    def get_queryset(self):
        """
        Garanta que o usuário só possa editar seus próprios perfis.
        """
        return EnergyProfiles.objects.filter(user=self.request.user)

    def get_success_url(self):
        """
        Redireciona para a página de detalhes do perfil após a atualização.
        """
        return reverse_lazy('profile_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Perfil atualizado com sucesso!')
        return response


class EnergyProfileDeleteView(LoginRequiredMixin, DeleteView):
    """
    Deleta um perfil de energia existente.
    """
    model = EnergyProfiles
    template_name = 'profiles/profile_confirm_delete.html' # Será usado por um modal
    success_url = reverse_lazy('profile_list') # Redireciona para a lista após a exclusão

    def get_queryset(self):
        """
        Garanta que o usuário só possa deletar seus próprios perfis.
        """
        return EnergyProfiles.objects.filter(user=self.request.user)


# --- ProfileDevices CRUD (Gerenciar Dispositivos Associados a Perfis - CRUD 2) ---

# Trecho hipotético baseado no contexto de outras views no seu arquivo
from django.shortcuts import get_object_or_404
from .models import EnergyProfiles # Certifique-se de importar EnergyProfiles

class ProfileDeviceCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = ProfileDevices
    form_class = ProfileDevicesForm
    template_name = 'energy_profiles/energy_profile_device_form.html'
    success_message = "Dispositivo adicionado ao perfil com sucesso!"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        profile_pk = self.kwargs.get('profile_pk') # Assumindo que o PK do perfil vem da URL
        if profile_pk:
            profile_instance = get_object_or_404(EnergyProfiles, pk=profile_pk, user=self.request.user)
            kwargs['profile'] = profile_instance # Passa a instância para o __init__ do formulário
        return kwargs

    def form_valid(self, form):
        # Garante que o profile_id seja definido na instância do formulário ANTES de salvar.
        # Isso é crucial se o campo 'profile' estiver oculto no formulário e não for enviado via POST
        # ou se você quer ter certeza que a instância correta do profile está ligada.
        profile_pk = self.kwargs.get('profile_pk')
        if profile_pk:
            profile_instance = get_object_or_404(EnergyProfiles, pk=profile_pk, user=self.request.user)
            form.instance.profile = profile_instance # ATRIBUIÇÃO CRÍTICA AQUI!

        # O super().form_valid(form) vai chamar form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_pk = self.kwargs.get('profile_pk')
        if profile_pk:
            context['profile'] = get_object_or_404(EnergyProfiles, pk=profile_pk, user=self.request.user)
        context['page_title'] = "Adicionar Dispositivo ao Perfil"
        return context

    def get_success_url(self):
        # Redireciona para a página de detalhes do perfil
        return reverse_lazy('profile_detail', kwargs={'pk': self.kwargs.get('profile_pk')})

class ProfileDeviceUpdateView(LoginRequiredMixin, UpdateView):
    """
    Atualiza um dispositivo associado a um perfil.
    """
    model = ProfileDevices
    form_class = ProfileDevicesForm
    template_name = 'energy_profiles/energy_profile_device_form.html' # Será usado por um modal

    def get_queryset(self):
        """
        Garanta que o usuário só possa editar seus próprios ProfileDevices,
        verificando também se o perfil pai pertence ao usuário.
        """
        return ProfileDevices.objects.filter(profile__user=self.request.user)
    
    def get_context_data(self, **kwargs):
        """Adiciona o perfil pai ao contexto do template."""
        context = super().get_context_data(**kwargs)
        # self.object é a instância de ProfileDevices que está sendo editada.
        # Adicionamos seu perfil pai ao contexto com a chave 'profile'.
        context['profile'] = self.object.profile
        return context

    def get_success_url(self):
        """
        Redireciona para a página de detalhes do perfil do dispositivo após a atualização.
        """
        return reverse_lazy('profile_detail', kwargs={'pk': self.object.profile.pk})

class ProfileDeviceDeleteView(LoginRequiredMixin, DeleteView):
    """
    Deleta um dispositivo associado a um perfil.
    """
    model = ProfileDevices
    template_name = 'profiles/profile_device_confirm_delete.html' # Será usado por um modal

    def get_queryset(self):
        """
        Garanta que o usuário só possa deletar seus próprios ProfileDevices,
        verificando também se o perfil pai pertence ao usuário.
        """
        return ProfileDevices.objects.filter(profile__user=self.request.user)

    def get_success_url(self):
        """
        Redireciona para a página de detalhes do perfil do dispositivo após a exclusão.
        """
        return reverse_lazy('profile_detail', kwargs={'pk': self.object.profile.pk})


class BillingRecordListView(LoginRequiredMixin, ListView):
    """
    Exibe uma lista de todos os registros de faturamento.
    Filtra por perfis que o usuário logado possui.
    """
    model = BillingRecord
    template_name = 'billing_records/list.html'
    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self):
        # Filtra os registros de faturamento para mostrar apenas aqueles
        # associados aos perfis que o usuário logado tem permissão.
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return BillingRecord.objects.filter(profile__in=user_profiles).order_by('-invoice_date')


class BillingRecordDetailView(LoginRequiredMixin, DetailView):
    """
    Exibe os detalhes de um registro de faturamento específico.
    """
    model = BillingRecord
    template_name = 'billing_records/detail.html'
    context_object_name = 'object'

    def get_queryset(self):
        # Garante que o usuário só possa ver registros de faturamento
        # associados aos seus perfis.
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(profile__in=user_profiles)


class BillingRecordCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Permite a criação de um novo registro de faturamento.
    """
    model = BillingRecord
    form_class = BillingRecordForm
    template_name = 'billing_records/form.html'
    success_url = reverse_lazy('billing_record_list')
    success_message = "Registro de faturamento criado com sucesso!"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Filtra as opções de perfil no formulário para mostrar apenas
        # os perfis associados ao usuário logado.
        kwargs['request'] = self.request # Passa o request para o formulário
        return kwargs

    def form_valid(self, form):
        # O perfil já deve ser filtrado no __init__ do formulário
        # mas pode-se adicionar lógica de validação extra aqui se necessário.
        return super().form_valid(form)


class BillingRecordUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Permite a atualização de um registro de faturamento existente.
    """
    model = BillingRecord
    form_class = BillingRecordForm
    template_name = 'billing_records/form.html'
    context_object_name = 'object'
    success_url = reverse_lazy('billing_record_list')
    success_message = "Registro de faturamento atualizado com sucesso!"

    def get_queryset(self):
        # Garante que o usuário só possa editar registros de faturamento
        # associados aos seus perfis.
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(profile__in=user_profiles)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Filtra as opções de perfil no formulário para mostrar apenas
        # os perfis associados ao usuário logado.
        kwargs['request'] = self.request # Passa o request para o formulário
        return kwargs


class BillingRecordDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    Permite a exclusão de um registro de faturamento.
    """
    model = BillingRecord
    template_name = 'billing_records/confirm_delete.html'
    success_url = reverse_lazy('billing_record_list')
    success_message = "Registro de faturamento excluído com sucesso!"

    def get_queryset(self):
        # Garante que o usuário só possa excluir registros de faturamento
        # associados aos seus perfis.
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(profile__in=user_profiles)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        return context


class TariffFlagAdditiveListView(LoginRequiredMixin, ListView):
    """
    Exibe uma lista de todas as bandeiras tarifárias cadastradas.
    """
    model = TariffFlagAdditive
    template_name = 'tariff_flags/list.html'
    context_object_name = 'object_list' # Nome padrão é object_list, mas explicitar é bom
    paginate_by = 10 # Opcional: para paginação, defina a quantidade de itens por página

    def get_queryset(self):
        # Exemplo: pode-se filtrar bandeiras ativas ou ordenar
        return TariffFlagAdditive.objects.all().order_by('-start_date')


class TariffFlagAdditiveDetailView(LoginRequiredMixin, DetailView):
    """
    Exibe os detalhes de uma bandeira tarifária específica.
    """
    model = TariffFlagAdditive
    template_name = 'tariff_flags/detail.html'
    context_object_name = 'object' # Nome padrão é object, mas explicitar é bom


class TariffFlagAdditiveCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Permite a criação de uma nova bandeira tarifária.
    """
    model = TariffFlagAdditive
    form_class = TariffFlagAdditiveForm
    template_name = 'tariff_flags/form.html'
    success_url = reverse_lazy('tariff_flag_list') # Redireciona para a lista após a criação
    success_message = "Bandeira tarifária criada com sucesso!"


class TariffFlagAdditiveUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Permite a atualização de uma bandeira tarifária existente.
    """
    model = TariffFlagAdditive
    form_class = TariffFlagAdditiveForm
    template_name = 'tariff_flags/form.html'
    context_object_name = 'object'
    success_url = reverse_lazy('tariff_flag_list') # Redireciona para a lista após a atualização
    success_message = "Bandeira tarifária atualizada com sucesso!"


class TariffFlagAdditiveDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    Permite a exclusão de uma bandeira tarifária.
    """
    model = TariffFlagAdditive
    template_name = 'tariff_flags/confirm_delete.html' # Um template para confirmar a exclusão
    success_url = reverse_lazy('tariff_flag_list') # Redireciona para a lista após a exclusão
    success_message = "Bandeira tarifária excluída com sucesso!"

    # Opcional: Adicionar um método get_context_data para passar o objeto para o template de confirmação
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object() # Passa o objeto a ser excluído
        return context

class EnergyTariffListView(LoginRequiredMixin, ListView):
    """
    Exibe uma lista de todas as tarifas de energia cadastradas.
    """
    model = EnergyTariff
    template_name = 'energy_tariffs/list.html'
    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self):
        # Pode-se adicionar filtros aqui, por exemplo, tarifas ativas
        return EnergyTariff.objects.all().order_by('-start_date')


class EnergyTariffDetailView(LoginRequiredMixin, DetailView):
    """
    Exibe os detalhes de uma tarifa de energia específica.
    """
    model = EnergyTariff
    template_name = 'energy_tariffs/detail.html'
    context_object_name = 'object'


class EnergyTariffCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Permite a criação de uma nova tarifa de energia.
    """
    model = EnergyTariff
    form_class = EnergyTariffForm
    template_name = 'energy_tariffs/form.html'  # Ou 'energy_tariffs/create_form.html' se for um template dedicado
    success_url = reverse_lazy('energy_tariff_list')
    success_message = "Tarifa de energia criada com sucesso!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['create_form'] = kwargs.get('form', EnergyTariffForm())
        

        context['energy_tariffs'] = EnergyTariff.objects.all().order_by('name') 
        return context

    def form_valid(self, form):
        """
        Método chamado quando o formulário é validado com sucesso.
        Pode adicionar lógica adicional antes de salvar, se necessário.
        """

        return super().form_valid(form)



class EnergyTariffUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Permite a atualização de uma tarifa de energia existente.
    """
    model = EnergyTariff
    form_class = EnergyTariffForm
    template_name = 'energy_tariffs/form.html'
    context_object_name = 'object'
    success_url = reverse_lazy('energy_tariff_list')
    success_message = "Tarifa de energia atualizada com sucesso!"


class EnergyTariffDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    Permite a exclusão de uma tarifa de energia.
    """
    model = EnergyTariff
    template_name = 'energy_tariffs/confirm_delete.html' # Template para confirmar exclusão
    success_url = reverse_lazy('energy_tariff_list')
    success_message = "Tarifa de energia excluída com sucesso!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        return context
    
class EnergyQualityRecordListView(LoginRequiredMixin, ListView):
    """
    Exibe uma lista de todos os registros de qualidade de energia.
    Filtra por perfis que o usuário logado possui.
    """
    model = EnergyQualityRecord
    template_name = 'energy_quality/list.html'
    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return EnergyQualityRecord.objects.filter(profile__in=user_profiles).order_by('-record_datetime')


class EnergyQualityRecordDetailView(LoginRequiredMixin, DetailView):
    """
    Exibe os detalhes de um registro de qualidade de energia específico.
    """
    model = EnergyQualityRecord
    template_name = 'energy_quality/detail.html'
    context_object_name = 'object'

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(profile__in=user_profiles)


class EnergyQualityRecordCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Permite a criação de um novo registro de qualidade de energia.
    """
    model = EnergyQualityRecord
    form_class = EnergyQualityRecordForm
    template_name = 'energy_quality/form.html'
    success_url = reverse_lazy('energy_quality_list')
    success_message = "Registro de qualidade de energia criado com sucesso!"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request # Passa o request para o formulário
        return kwargs


class EnergyQualityRecordUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Permite a atualização de um registro de qualidade de energia existente.
    """
    model = EnergyQualityRecord
    form_class = EnergyQualityRecordForm
    template_name = 'energy_quality/form.html'
    context_object_name = 'object'
    success_url = reverse_lazy('energy_quality_list')
    success_message = "Registro de qualidade de energia atualizado com sucesso!"

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(profile__in=user_profiles)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request # Passa o request para o formulário
        return kwargs


class EnergyQualityRecordDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    Permite a exclusão de um registro de qualidade de energia.
    """
    model = EnergyQualityRecord
    template_name = 'energy_quality/confirm_delete.html'
    success_url = reverse_lazy('energy_quality_list')
    success_message = "Registro de qualidade de energia excluído com sucesso!"

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(profile__in=user_profiles)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        return context
    
class OptimizationSuggestionListView(LoginRequiredMixin, ListView):
    """
    Exibe uma lista de todas as sugestões de otimização.
    Filtra por perfis que o usuário logado possui.
    """
    model = OptimizationSuggestion
    template_name = 'optimization_suggestions/list.html'
    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return OptimizationSuggestion.objects.filter(profile__in=user_profiles).order_by('-suggested_at')


class OptimizationSuggestionDetailView(LoginRequiredMixin, DetailView):
    """
    Exibe os detalhes de uma sugestão de otimização específica.
    """
    model = OptimizationSuggestion
    template_name = 'optimization_suggestions/detail.html'
    context_object_name = 'object'

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(profile__in=user_profiles)


class OptimizationSuggestionCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Permite a criação de uma nova sugestão de otimização.
    """
    model = OptimizationSuggestion
    form_class = OptimizationSuggestionForm
    template_name = 'optimization_suggestions/form.html'
    success_url = reverse_lazy('optimization_suggestion_list')
    success_message = "Sugestão de otimização criada com sucesso!"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request # Passa o request para o formulário
        return kwargs


class OptimizationSuggestionUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Permite a atualização de uma sugestão de otimização existente.
    """
    model = OptimizationSuggestion
    form_class = OptimizationSuggestionForm
    template_name = 'optimization_suggestions/form.html'
    context_object_name = 'object'
    success_url = reverse_lazy('optimization_suggestion_list')
    success_message = "Sugestão de otimização atualizada com sucesso!"

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(profile__in=user_profiles)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request # Passa o request para o formulário
        return kwargs


class OptimizationSuggestionDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    Permite a exclusão de uma sugestão de otimização.
    """
    model = OptimizationSuggestion
    template_name = 'optimization_suggestions/confirm_delete.html'
    success_url = reverse_lazy('optimization_suggestion_list')
    success_message = "Sugestão de otimização excluída com sucesso!"

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(profile__in=user_profiles)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        return context

@require_POST # Garante que esta view só aceite requisições POST
def bulk_update_notifications(request):
    alert_ids = request.POST.getlist('alert_ids')
    action = request.POST.get('action')

    if not alert_ids:
        messages.warning(request, "Nenhuma notificação foi selecionada.")
        return redirect('notification_inbox')

    # Filtra apenas alertas que pertencem ao usuário logado, por segurança
    queryset = Alert.objects.filter(user=request.user, pk__in=alert_ids)

    if action == 'mark_read':
        updated_count = queryset.update(is_read=True)
        messages.success(request, f"{updated_count} notificações foram marcadas como lidas.")
    elif action == 'delete':
        deleted_count, _ = queryset.delete()
        messages.success(request, f"{deleted_count} notificações foram excluídas.")
    else:
        messages.error(request, "Ação inválida.")
        
    return redirect('notification_inbox')

class AdminAlertListView(LoginRequiredMixin, SuperuserRequiredMixin, ListView):
    """
    Exibe uma lista de TODOS os alertas no formato de tabela,
    visível apenas para superusuários para fins de gerenciamento.
    """
    model = Alert
    # Usa o template original, no estilo de tabela CRUD
    template_name = 'alerts/list.html' 
    context_object_name = 'object_list'
    paginate_by = 20

    #def get_queryset(self):
        # Superusuários veem TODOS os alertas do sistema, não apenas os seus
    #    return Alert.objects.all().order_by('-triggered_at')
    
    def get_queryset(self):
        queryset = super().get_queryset() # Pega o queryset base (já filtrado por usuário)
        
        # Filtra por status (lida/não lida)
        status = self.request.GET.get('status')
        if status == 'read':
            queryset = queryset.filter(is_read=True)
        elif status == 'unread':
            queryset = queryset.filter(is_read=False)

        # Filtra por severidade
        severity = self.request.GET.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Passa as opções de severidade para o template preencher o dropdown
        context['alert_severity_choices'] = Alert.AlertSeverityChoices.choices
        return context

class AlertListView(LoginRequiredMixin, ListView):
    """
    Exibe uma lista de todos os alertas.
    Filtra por perfis que o usuário logado possui.
    """
    model = Alert
    template_name = 'notifications/inbox.html'
    context_object_name = 'object_list'
    paginate_by = 15

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return Alert.objects.filter(profile__in=user_profiles).order_by('-triggered_at')


class AlertDetailView(LoginRequiredMixin, DetailView):
    """
    Exibe os detalhes de um alerta específico.
    """
    model = Alert
    template_name = 'alerts/detail.html'
    context_object_name = 'object'

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(profile__in=user_profiles)


class AlertCreateView(LoginRequiredMixin, SuccessMessageMixin, SuperuserRequiredMixin, CreateView):
    """
    Permite a criação de um novo alerta.
    """
    model = Alert
    form_class = AlertForm
    template_name = 'alerts/form.html'
    success_url = reverse_lazy('alert_list')
    success_message = "Alerta criado com sucesso!"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request # Passa o request para o formulário
        return kwargs


class AlertUpdateView(LoginRequiredMixin, SuccessMessageMixin,SuperuserRequiredMixin, UpdateView):
    """
    Permite a atualização de um alerta existente.
    """
    model = Alert
    form_class = AlertForm
    template_name = 'alerts/form.html'
    context_object_name = 'object'
    success_url = reverse_lazy('alert_list')
    success_message = "Alerta atualizado com sucesso!"

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(profile__in=user_profiles)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request # Passa o request para o formulário
        return kwargs


class AlertDeleteView(LoginRequiredMixin, SuccessMessageMixin,SuperuserRequiredMixin, DeleteView):
    """
    Permite a exclusão de um alerta.
    """
    model = Alert
    template_name = 'alerts/confirm_delete.html'
    success_url = reverse_lazy('alert_list')
    success_message = "Alerta excluído com sucesso!"

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(profile__in=user_profiles)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        return context
    
class ConsumptionGoalListView(LoginRequiredMixin, ListView):
    """
    Exibe uma lista de todas as metas de consumo.
    Filtra por perfis que o usuário logado possui.
    """
    model = ConsumptionGoal
    template_name = 'consumption_goals/list.html'
    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return ConsumptionGoal.objects.filter(profile__in=user_profiles).order_by('-start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = date.today() # Adiciona a data atual ao contexto para o template
        return context


class ConsumptionGoalDetailView(LoginRequiredMixin, DetailView):
    """
    Exibe os detalhes de uma meta de consumo específica.
    """
    model = ConsumptionGoal
    template_name = 'consumption_goals/detail.html'
    context_object_name = 'object'

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(profile__in=user_profiles)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = date.today() # Adiciona a data atual ao contexto para o template
        return context


class ConsumptionGoalCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Permite a criação de uma nova meta de consumo.
    """
    model = ConsumptionGoal
    form_class = ConsumptionGoalForm
    template_name = 'consumption_goals/form.html'
    success_url = reverse_lazy('consumption_goal_list')
    success_message = "Meta de consumo criada com sucesso!"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request # Passa o request para o formulário
        return kwargs


class ConsumptionGoalUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Permite a atualização de uma meta de consumo existente.
    """
    model = ConsumptionGoal
    form_class = ConsumptionGoalForm
    template_name = 'consumption_goals/form.html'
    context_object_name = 'object'
    success_url = reverse_lazy('consumption_goal_list')
    success_message = "Meta de consumo atualizada com sucesso!"

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(profile__in=user_profiles)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request # Passa o request para o formulário
        return kwargs


class ConsumptionGoalDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    Permite a exclusão de uma meta de consumo.
    """
    model = ConsumptionGoal
    template_name = 'consumption_goals/confirm_delete.html'
    success_url = reverse_lazy('consumption_goal_list')
    success_message = "Meta de consumo excluída com sucesso!"

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(profile__in=user_profiles)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        return context
    
class EnergyReadingListView(LoginRequiredMixin, ListView):
    """
    Exibe uma lista de todas as leituras de energia.
    Filtra por perfis que o usuário logado possui.
    """
    model = EnergyReading
    template_name = 'energy_readings/list.html'
    context_object_name = 'object_list'
    paginate_by = 20 # Um número maior para leituras, que podem ser muitas

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return EnergyReading.objects.filter(profile__in=user_profiles).order_by('-reading_datetime')


class EnergyReadingDetailView(LoginRequiredMixin, DetailView):
    """
    Exibe os detalhes de uma leitura de energia específica.
    """
    model = EnergyReading
    template_name = 'energy_readings/detail.html'
    context_object_name = 'object'

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(profile__in=user_profiles)


class EnergyReadingCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Permite a criação de uma nova leitura de energia.
    """
    model = EnergyReading
    form_class = EnergyReadingForm
    template_name = 'energy_readings/form.html'
    success_url = reverse_lazy('energy_reading_list')
    success_message = "Leitura de energia criada com sucesso!"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request # Passa o request para o formulário
        return kwargs


class EnergyReadingUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Permite a atualização de uma leitura de energia existente.
    """
    model = EnergyReading
    form_class = EnergyReadingForm
    template_name = 'energy_readings/form.html'
    context_object_name = 'object'
    success_url = reverse_lazy('energy_reading_list')
    success_message = "Leitura de energia atualizada com sucesso!"

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(profile__in=user_profiles)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request # Passa o request para o formulário
        return kwargs


class EnergyReadingDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    Permite a exclusão de uma leitura de energia.
    """
    model = EnergyReading
    template_name = 'energy_readings/confirm_delete.html'
    success_url = reverse_lazy('energy_reading_list')
    success_message = "Leitura de energia excluída com sucesso!"

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(profile__in=user_profiles)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        return context
    
class ModelAccuracyScoresListView(LoginRequiredMixin, ListView):
    """
    Exibe uma lista de todos os scores de acurácia do modelo.
    Filtra por perfis que o usuário logado possui.
    """
    model = ModelAccuracyScores
    template_name = 'model_accuracy_scores/list.html'
    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return ModelAccuracyScores.objects.filter(profile__in=user_profiles).order_by('-evaluation_date')

class SmartDashboardView(LoginRequiredMixin, DetailView):
    """
    Exibe um dashboard de visão geral imersiva para um perfil de energia específico,
    otimizado para Smart TVs e IoT.
    """
    model = EnergyProfiles
    template_name = 'profiles/smart_dashboard.html'
    context_object_name = 'profile'
    pk_url_kwarg = 'profile_pk' # O nome do parâmetro PK na URL - DetailView usará isso por padrão

    def get_queryset(self):
        # Garante que o usuário só possa ver seus próprios perfis
        return EnergyProfiles.objects.filter(user=self.request.user)

    def get_object(self, queryset=None):
        # Sobrescreve o método get_object para lidar com URLs sem PK
        queryset = queryset or self.get_queryset()
        
        # Tenta pegar o profile_pk dos argumentos da URL
        profile_pk = self.kwargs.get(self.pk_url_kwarg)

        if profile_pk:
            # Se profile_pk está na URL, usa a lógica padrão do DetailView
            return get_object_or_404(queryset, pk=profile_pk)
        else:
            # Se profile_pk NÃO está na URL (ex: /smart_dashboard/),
            # tenta pegar o primeiro perfil do usuário logado como padrão.
            profile = queryset.first()
            if not profile:
                # Se o usuário não tem perfis, você pode levantar um Http404,
                # redirecionar, ou retornar None para que get_context_data lide com isso.
                # Para este cenário, vamos levantar um Http404 ou lidar em get_context_data.
                # Levantar Http404 aqui é mais direto se não houver perfil.
                from django.http import Http404
                raise Http404("Nenhum perfil de energia encontrado para este usuário.")
            return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.object # O objeto 'profile' já foi obtido por get_object()

        # Adiciona todos os perfis do usuário ao contexto para um possível dropdown de seleção
        context['all_user_profiles'] = EnergyProfiles.objects.filter(user=self.request.user).order_by('name')

        # --- O RESTO DA SUA LÓGICA DE get_context_data CONTINUA AQUI ---
        # Certifique-se de que todas as queries para 'profile' usam 'self.object' ou 'profile' local
        
        # --- 1. Dados de Consumo Atual e Última Leitura ---
        latest_reading = EnergyReading.objects.filter(profile=profile).order_by('-reading_datetime').first()
        context['current_kwh'] = latest_reading.total_kwh_consumption if latest_reading else None
        context['last_reading_time'] = latest_reading.reading_datetime.strftime('%d/%m/%Y %H:%M:%S') if latest_reading else None

        # --- 2. Contagem de Dispositivos Ativos (Exemplo simplificado) ---
        context['active_devices_count'] = ProfileDevices.objects.filter(profile=profile).count()

        # --- 3. Contagem de Alertas Ativos ---
        context['active_alerts_count'] = Alert.objects.filter(profile=profile, is_resolved=False).count()
        context['recent_alerts'] = Alert.objects.filter(profile=profile).order_by('-alert_date')[:5]

        # --- 4. Previsão para as Próximas 24h (Exemplo) ---
        forecast_24h_obj = ConsumptionPredictions.objects.filter(
            profile=profile,
            prediction_date__gte=datetime.now(get_brazil_timezone()) # Usa timezone correto
        ).order_by('prediction_date').first()

        context['forecast_24h'] = forecast_24h_obj.predicted_kwh if forecast_24h_obj else None

        # --- 5. Economia Sugerida Mensal (Exemplo) ---
        estimated_savings_sum = OptimizationSuggestion.objects.filter(
            profile=profile,
            is_implemented=False
        ).aggregate(total_savings=Sum('estimated_savings_money'))['total_savings']
        context['estimated_savings_month'] = estimated_savings_sum if estimated_savings_sum else None


        # --- 6. Gráfico de Consumo Recente (Últimas 24h ou 7 dias) ---
        brazil_tz = get_brazil_timezone()
        recent_readings = EnergyReading.objects.filter(
            profile=profile,
            reading_datetime__gte=datetime.now(tz=brazil_tz) - timedelta(days=7) # Correção: usar reading_datetime
        ).order_by('reading_datetime') # Correção: usar reading_datetime

        recent_consumption_chart_json = None
        if recent_readings.exists():
            dates = [r.reading_datetime.strftime('%d/%m %H:%M') for r in recent_readings]
            
            kwh_values = [float(r.total_kwh_consumption) if r.total_kwh_consumption is not None else None for r in recent_readings]

            fig = go.Figure(data=go.Scatter(x=dates, y=kwh_values, mode='lines+markers', name='Consumo'))
            fig.update_layout(
                title_text='Consumo nos Últimos 7 Dias',
                xaxis_title='Data/Hora',
                yaxis_title='Consumo (kWh)',
                template="plotly_white",
                margin=dict(l=50, r=50, t=50, b=50),
                height=350
            )
            recent_consumption_chart_json = json.dumps(fig.to_dict())

        context['recent_consumption_chart_json'] = recent_consumption_chart_json

        context['page_title'] = f'Smart Dashboard para: {profile.name}'
        return context


class SmartDashboardDataAPIView(LoginRequiredMixin, View):
    """
    View para retornar os dados do Smart Dashboard em formato JSON para chamadas AJAX.
    """
    def get(self, request, profile_pk, *args, **kwargs):
        profile = get_object_or_404(EnergyProfiles, pk=profile_pk, user=request.user)

        # Reutilize a lógica de get_context_data da SmartDashboardView
        # ou crie funções auxiliares específicas para API para otimização
        
        # --- Dados de Consumo Atual e Última Leitura ---
        latest_reading = EnergyReading.objects.filter(profile=profile).order_by('-reading_datetime').first()
        current_kwh = float(latest_reading.total_kwh_consumption) if latest_reading and latest_reading.total_kwh_consumption is not None else None
        last_reading_time = latest_reading.reading_datetime.strftime('%d/%m/%Y %H:%M:%S') if latest_reading else None

        # --- Contagem de Dispositivos Ativos ---
        active_devices_count = ProfileDevices.objects.filter(profile=profile).count()

        # --- Contagem de Alertas Ativos ---
        active_alerts_count = Alert.objects.filter(profile=profile, is_resolved=False).count()

        # --- Previsão para as Próximas 24h ---
        brazil_tz = get_brazil_timezone()
        forecast_24h_obj = ConsumptionPredictions.objects.filter(
            profile=profile,
            prediction_date__gte=datetime.now(tz=brazil_tz)
        ).order_by('prediction_date').first()
        forecast_24h = float(forecast_24h_obj.predicted_kwh) if forecast_24h_obj and forecast_24h_obj.predicted_kwh is not None else None

        # --- Economia Sugerida Mensal ---
        estimated_savings_sum = OptimizationSuggestion.objects.filter(
            profile=profile,
            is_implemented=False
        ).aggregate(total_savings=Sum('estimated_savings_money'))['total_savings']
        estimated_savings_month = float(estimated_savings_sum) if estimated_savings_sum is not None else None
        
        # --- Gráfico de Consumo Recente (JSON) ---
        recent_readings = EnergyReading.objects.filter(
            profile=profile,
            reading_datetime__gte=datetime.now(tz=brazil_tz) - timedelta(days=7)
        ).order_by('reading_datetime')

        recent_consumption_chart_json = None
        if recent_readings.exists():
            dates = [r.reading_datetime.strftime('%d/%m %H:%M') for r in recent_readings]
            kwh_values = [float(r.total_kwh_consumption) if r.total_kwh_consumption is not None else None for r in recent_readings]

            fig = go.Figure(data=go.Scatter(x=dates, y=kwh_values, mode='lines+markers', name='Consumo'))
            fig.update_layout(
                title_text='Consumo nos Últimos 7 Dias',
                xaxis_title='Data/Hora',
                yaxis_title='Consumo (kWh)',
                template="plotly_white",
                margin=dict(l=50, r=50, t=50, b=50),
                height=350
            )
            recent_consumption_chart_json = json.dumps(fig.to_dict())


        data = {
            'current_kwh': current_kwh,
            'last_reading_time': last_reading_time,
            'active_devices_count': active_devices_count,
            'active_alerts_count': active_alerts_count,
            'forecast_24h': forecast_24h,
            'estimated_savings_month': estimated_savings_month,
            'recent_consumption_chart_json': recent_consumption_chart_json # Incluir o JSON do gráfico aqui
        }
        return JsonResponse(data)

    
class ModelAccuracyScoresDetailView(LoginRequiredMixin, DetailView):
    """
    Exibe os detalhes de um score de acurácia de modelo específico,
    agora com cards de métricas e um gráfico de dispersão.
    """
    model = ModelAccuracyScores
    template_name = 'model_accuracy_scores/detail.html' # Este será refatorado
    context_object_name = 'accuracy_score'

    def get_queryset(self):
        # Garante que o usuário só possa ver scores de acurácia para modelos
        # associados aos seus perfis de energia, ou modelos globais se aplicável.
        # Assumindo que PredictionModels tem um link para EnergyProfiles
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(
            prediction_model__profiles__in=user_profiles
        ).distinct()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        accuracy_score = self.get_object() # A instância de ModelAccuracyScores

        # --- Geração do Gráfico de Dispersão ---
        scatter_chart_data = get_model_accuracy_scatter_chart_data(accuracy_score)

        context['scatter_chart_json'] = scatter_chart_data['chart_json']
        context['scatter_chart_message'] = scatter_chart_data['message']

        # Métricas do modelo (já devem estar na instância accuracy_score)
        context['mape'] = accuracy_score.mape if accuracy_score.mape is not None else 'N/A'
        context['rmse'] = accuracy_score.rmse if accuracy_score.rmse is not None else 'N/A'
        # Adicione outras métricas se o seu modelo ModelAccuracyScores as tiver (ex: r_squared)
        # context['r_squared'] = accuracy_score.r_squared if hasattr(accuracy_score, 'r_squared') else 'N/A'


        context['page_title'] = f'Detalhes da Acurácia do Modelo: {accuracy_score.prediction_model.name}'
        return context



class ModelAccuracyScoresCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Permite a criação de um novo score de acurácia.
    """
    model = ModelAccuracyScores
    form_class = ModelAccuracyScoresForm
    template_name = 'model_accuracy_scores/form.html'
    success_url = reverse_lazy('model_accuracy_score_list')
    success_message = "Score de acurácia criado com sucesso!"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request # Passa o request para o formulário
        return kwargs


class ModelAccuracyScoresUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Permite a atualização de um score de acurácia existente.
    """
    model = ModelAccuracyScores
    form_class = ModelAccuracyScoresForm
    template_name = 'model_accuracy_scores/form.html'
    context_object_name = 'object'
    success_url = reverse_lazy('model_accuracy_score_list')
    success_message = "Score de acurácia atualizado com sucesso!"

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(profile__in=user_profiles)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request # Passa o request para o formulário
        return kwargs


class ModelAccuracyScoresDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    Permite a exclusão de um score de acurácia.
    """
    model = ModelAccuracyScores
    template_name = 'model_accuracy_scores/confirm_delete.html'
    success_url = reverse_lazy('model_accuracy_score_list')
    success_message = "Score de acurácia excluído com sucesso!"

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(profile__in=user_profiles)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        return context
    


class DeviceUsagePatternListView(LoginRequiredMixin, ListView):
    """
    Exibe uma lista de todos os padrões de uso de dispositivos.
    Filtra por perfis que o usuário logado possui.
    """
    model = DeviceUsagePattern
    template_name = 'device_usage_patterns/list.html'
    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return DeviceUsagePattern.objects.filter(profile_device__profile__in=user_profiles)


class DeviceUsagePatternDetailView(LoginRequiredMixin, DetailView):
    """
    Exibe os detalhes de um padrão de uso de dispositivo específico.
    """
    model = DeviceUsagePattern
    template_name = 'device_usage_patterns/detail.html'
    context_object_name = 'object'

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(profile__in=user_profiles)


class DeviceUsagePatternCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Permite a criação de um novo padrão de uso de dispositivo.
    """
    model = DeviceUsagePattern
    form_class = DeviceUsagePatternForm
    template_name = 'device_usage_patterns/form.html'
    success_url = reverse_lazy('device_usage_pattern_list')
    success_message = "Padrão de uso de dispositivo criado com sucesso!"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request # Passa o request para o formulário
        return kwargs


class DeviceUsagePatternUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Permite a atualização de um padrão de uso de dispositivo existente.
    """
    model = DeviceUsagePattern
    form_class = DeviceUsagePatternForm
    template_name = 'device_usage_patterns/form.html'
    context_object_name = 'object'
    success_url = reverse_lazy('device_usage_pattern_list')
    success_message = "Padrão de uso de dispositivo atualizado com sucesso!"

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(profile__in=user_profiles)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request # Passa o request para o formulário
        return kwargs


class DeviceUsagePatternDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    Permite a exclusão de um padrão de uso de dispositivo.
    """
    model = DeviceUsagePattern
    template_name = 'device_usage_patterns/confirm_delete.html'
    success_url = reverse_lazy('device_usage_pattern_list')
    success_message = "Padrão de uso de dispositivo excluído com sucesso!"

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(profile__in=user_profiles)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        return context
    

class HistoricalPredictionComparisonListView(LoginRequiredMixin, ListView):
    """
    Exibe uma lista de todas as comparações históricas de previsão.
    Filtra por perfis que o usuário logado possui.
    """
    model = HistoricalPredictionComparison
    template_name = 'historical_prediction_comparisons/list.html'
    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        # Garante que apenas comparações de previsões para perfis do usuário logado sejam mostradas
        return HistoricalPredictionComparison.objects.filter(profile__in=user_profiles).order_by('-comparison_date')

class OutlierAnalysisView(LoginRequiredMixin, DetailView):
    """
    Exibe a análise de outliers para um perfil de energia específico.
    Permite selecionar o período de análise.
    """
    model = EnergyProfiles
    template_name = 'profiles/outliers_analisys.html' 
    context_object_name = 'profile'
    pk_url_kwarg = 'profile_pk'

    def get_queryset(self):
        # Garante que o usuário só possa ver perfis que lhe pertencem
        return EnergyProfiles.objects.filter(user=self.request.user)
    
    def get_object(self, queryset=None):
        """
        Overrides get_object to handle cases where profile_pk is not in the URL,
        defaulting to the user's first profile if available.
        """
        queryset = queryset or self.get_queryset()

        profile_pk = self.kwargs.get(self.pk_url_kwarg) # Tries to get profile_pk from URL kwargs

        if profile_pk:
            # If profile_pk is in the URL, use default DetailView logic to get the object
            return get_object_or_404(queryset, pk=profile_pk)
        else:
            # If profile_pk is NOT in the URL (e.g., /outliers/),
            # try to get the first profile for the logged-in user as a default.
            profile = queryset.first()
            if not profile:
                # If the user has no profiles, raise Http404 or handle gracefully.
                # Here, we'll raise Http404 as there's no data to display.
                from django.http import Http404
                raise Http404("Nenhum perfil de energia encontrado para este usuário.")
            return profile
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()

        context['all_user_profiles'] = EnergyProfiles.objects.filter(user=self.request.user).order_by('name')
        
        profile_pk = self.kwargs.get('profile_pk')
        profile = None

        if profile_pk:
            # Se um PK de perfil é fornecido na URL (ex: /profiles/1/benchmark/)
            profile = get_object_or_404(EnergyProfiles, pk=profile_pk, user=self.request.user)
        else:
            # Se nenhum PK for fornecido (acesso via /benchmark/), tenta pegar o primeiro perfil do usuário logado.
            # Você pode ajustar essa lógica para pegar, por exemplo, o perfil mais recente, ou um perfil "padrão".
            profile = EnergyProfiles.objects.filter(user=self.request.user).first()

        # Obter datas do request (GET) ou usar padrão
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30) # Padrão: últimos 30 dias

        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass # Usa o padrão se a data for inválida
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass # Usa o padrão se a data for inválida

        # Chamar a função de utilitário para obter os dados do gráfico e métricas
        outlier_data = get_outlier_detection_chart_data(profile, start_date, end_date)

        context['outlier_chart_json'] = outlier_data['chart_json']
        context['num_outliers'] = outlier_data['num_outliers']
        context['total_readings'] = outlier_data['total_readings']
        context['message'] = outlier_data['message']
        context['start_date'] = start_date.strftime('%Y-%m-%d')
        context['end_date'] = end_date.strftime('%Y-%m-%d')

        context['page_title'] = f'Análise de Outliers para: {profile.name}'
        return context
    
class HistoricalPredictionComparisonDetailView(LoginRequiredMixin, DetailView):
    """
    Exibe os detalhes de uma comparação histórica de previsão específica,
    agora com cards de métricas e um gráfico.
    """
    model = HistoricalPredictionComparison
    template_name = 'historical_prediction_comparisons/detail.html'
    context_object_name = 'object'

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(profile__in=user_profiles)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comparison = self.get_object() # Obtém a instância da comparação

        # --- Geração do Gráfico de Comparação ---
        chart_json = None
        if comparison.prediction and comparison.actual_kwh is not None:
            data = [
                go.Bar(
                    name='Previsto',
                    x=['Consumo'],
                    y=[comparison.prediction.predicted_kwh],
                    marker_color='rgba(63, 81, 181, 0.8)' # Azul Material Info
                ),
                go.Bar(
                    name='Real',
                    x=['Consumo'],
                    y=[comparison.actual_kwh],
                    marker_color='rgba(76, 175, 80, 0.8)' # Verde Material Success
                )
            ]

            layout = go.Layout(
                title_text=f'Previsão vs. Real para {comparison.comparison_date.strftime("%d/%m/%Y %H:%M")}',
                barmode='group',
                yaxis_title='Consumo (kWh)',
                margin=dict(l=50, r=50, t=50, b=50),
                height=300,
                template="plotly_white"
            )
            fig = go.Figure(data=data, layout=layout)
            chart_json = json.dumps(fig.to_dict())

        context['chart_json'] = chart_json
        return context


class HistoricalPredictionComparisonCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = HistoricalPredictionComparison
    form_class = HistoricalPredictionComparisonForm
    template_name = 'historical_prediction_comparisons/form.html'
    success_url = reverse_lazy('historical_prediction_comparison_list')
    success_message = "Comparação de previsão histórica criada com sucesso!"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request # IMPORTANTE: Passa o request para o formulário
        return kwargs

    # Opcional: Se você quiser preencher o 'profile' automaticamente com base na 'prediction' selecionada
    def form_valid(self, form):
        # A instância de `prediction` já virá selecionada do formulário
        # e o 'profile' pode ser derivado dela.
        # Isso é útil se o campo 'profile' não for visível no formulário ou se for auto-preenchido.
        if form.instance.prediction and not form.instance.profile:
            form.instance.profile = form.instance.prediction.profile
        return super().form_valid(form)


class HistoricalPredictionComparisonUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = HistoricalPredictionComparison
    form_class = HistoricalPredictionComparisonForm
    template_name = 'historical_prediction_comparisons/form.html'
    context_object_name = 'object'
    success_url = reverse_lazy('historical_prediction_comparison_list')
    success_message = "Comparação de previsão histórica atualizada com sucesso!"

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        # Garante que o usuário só pode editar comparações de seus próprios perfis
        return super().get_queryset().filter(profile__in=user_profiles)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request # IMPORTANTE: Passa o request para o formulário
        return kwargs


class HistoricalPredictionComparisonDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    Permite a exclusão de uma comparação histórica de previsão.
    """
    model = HistoricalPredictionComparison
    template_name = 'historical_prediction_comparisons/confirm_delete.html'
    success_url = reverse_lazy('historical_prediction_comparison_list')
    success_message = "Comparação de previsão histórica excluída com sucesso!"

    def get_queryset(self):
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user)
        return super().get_queryset().filter(profile__in=user_profiles)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        return context

class UserPreferencesDetailView(LoginRequiredMixin, DetailView):
    """
    Exibe os detalhes das preferências do usuário logado.
    Redireciona para a criação se não houver preferências existentes.
    """
    model = UserPreferences
    template_name = 'user_preferences/detail.html'
    context_object_name = 'object'

    def get_object(self, queryset=None):
        """
        Busca as preferências para o usuário logado.
        Cria uma nova instância se não existir.
        """
        user_preferences, created = UserPreferences.objects.get_or_create(user=self.request.user)
        # Se foi criada, redireciona para o formulário de criação/edição para que o usuário possa preencher
        if created:
            return None # Retorna None para que o template saiba que não há objeto
        return user_preferences

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not context['object']: # Se get_object retornou None (preferências criadas mas vazias)
            return redirect('user_preferences_create') # Redireciona para a view de criação para preencher
        return context


class UserPreferencesCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Permite a criação das preferências do usuário logado.
    Se as preferências já existirem, redireciona para a página de edição.
    """
    model = UserPreferences
    form_class = UserPreferencesForm
    template_name = 'user_preferences/form.html'
    success_url = reverse_lazy('user_preferences_detail')
    success_message = "Preferências configuradas com sucesso!"

    def dispatch(self, request, *args, **kwargs):
        # Se as preferências já existirem para o usuário, redireciona para a edição
        if UserPreferences.objects.filter(user=request.user).exists():
            return redirect('user_preferences_update', pk=request.user.userpreferences.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user # Associa as preferências ao usuário logado
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request # Passa o request para o formulário, caso precise para filtragem
        return kwargs


class UserPreferencesUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Permite a atualização das preferências do usuário logado.
    """
    model = UserPreferences
    form_class = UserPreferencesForm
    template_name = 'user_preferences/form.html'
    context_object_name = 'object'
    success_url = reverse_lazy('user_preferences_detail')
    success_message = "Preferências atualizadas com sucesso!"

    def get_object(self, queryset=None):
        """
        Busca as preferências para o usuário logado.
        """
        return get_object_or_404(UserPreferences, user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request # Passa o request para o formulário
        return kwargs


class UserPreferencesDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    Permite a exclusão das preferências do usuário logado.
    """
    model = UserPreferences
    template_name = 'user_preferences/confirm_delete.html'
    success_url = reverse_lazy('user_preferences_detail') # Redireciona para o detalhe (que pode mostrar a opção de criar de novo)
    success_message = "Preferências excluídas com sucesso! (Configurações resetadas)"

    def get_object(self, queryset=None):
        """
        Busca as preferências para o usuário logado.
        """
        return get_object_or_404(UserPreferences, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object() # Garante que o objeto esteja no contexto
        return context



class BenchmarkView(LoginRequiredMixin, TemplateView):
    """
    View para a seção de Benchmark.
    Calcula e exibe dados de benchmark para os dispositivos de um perfil.
    Pode operar com ou sem um profile_pk na URL.
    """
    template_name = 'benchmark.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_user_profiles'] = EnergyProfiles.objects.filter(user=self.request.user).order_by('name')
        
        profile_pk = self.kwargs.get('profile_pk')
        profile = None

        if profile_pk:
            # Se um PK de perfil é fornecido na URL (ex: /profiles/1/benchmark/)
            profile = get_object_or_404(EnergyProfiles, pk=profile_pk, user=self.request.user)
        else:
            # Se nenhum PK for fornecido (acesso via /benchmark/), tenta pegar o primeiro perfil do usuário logado.
            # Você pode ajustar essa lógica para pegar, por exemplo, o perfil mais recente, ou um perfil "padrão".
            profile = EnergyProfiles.objects.filter(user=self.request.user).first()
            
            if not profile:
                # Se o usuário não tem nenhum perfil, preenche o contexto com dados vazios e uma mensagem.
                context['total_kwh_daily'] = 0
                context['device_kwh_data_json'] = json.dumps([])
                context['highest_consumer'] = None
                context['optimization_suggestions'] = ["Nenhum perfil de energia encontrado para análise. Por favor, crie um perfil para visualizar o benchmark."]
                context['bar_chart_json'] = None
                context['pie_chart_json'] = None
                context['gauge_chart_json'] = None
                context['profile'] = None # Indica que nenhum perfil foi selecionado/encontrado
                context['page_title'] = 'Benchmark de Consumo (Nenhum Perfil)'
                return context

        # Se um perfil foi encontrado (seja via PK ou como padrão)
        # Pré-carrega os dispositivos do perfil selecionado/encontrado
        profile_devices = profile.profile_devices.select_related('device').all()
        
        # Chama a função utilitária para calcular os dados do benchmark
        benchmark_data = calculate_benchmark_data(profile_devices)
        
        # Converte os dados do dispositivo para JSON para uso no frontend (gráficos)
        context['device_kwh_data_json'] = json.dumps(benchmark_data.get('device_kwh_data', []))
        
        # Adiciona todos os outros dados retornados por calculate_benchmark_data ao contexto
        context.update(benchmark_data)
        context['profile'] = profile # Adiciona o objeto profile ao contexto
        context['page_title'] = f'Benchmark de Consumo do Perfil: {profile.name}' # Título dinâmico

        return context


    
class MonitoringView(LoginRequiredMixin, TemplateView):
    """
    View para a seção de Monitoramento.
    Exibe a acurácia do modelo para os dispositivos do perfil.
    """
    template_name = 'monitoring.html' # Sugestão: organize em uma subpasta 'profiles'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user_profiles = EnergyProfiles.objects.filter(user=self.request.user).order_by('name')
        
        profile = None
        profile_pk = self.kwargs.get('profile_pk') # Tenta pegar da URL (ex: /profiles/1/monitoring/)
        
        if not profile_pk:
            profile_pk = self.request.GET.get('selected_profile') # Tenta pegar do parâmetro GET (ex: /monitoring/?selected_profile=2)

        if profile_pk:
            profile = get_object_or_404(user_profiles, pk=profile_pk)
        elif user_profiles.exists():
            profile = user_profiles.first() # Pega o primeiro perfil do usuário como padrão
        
        context['profile'] = profile # O perfil atualmente ativo
        context['all_user_profiles'] = user_profiles # Todos os perfis do usuário para o dropdown

        if profile:
            profile_devices = profile.profile_devices.select_related('device').all()
            accuracy_scores = ModelAccuracyScores.objects.filter(profile=profile) 

            monitoring_data = monitoring_performance_and_consumption(profile, profile_devices, accuracy_scores)
            context.update(monitoring_data)
            
            context['accuracy_metrics'] = monitoring_performance_and_consumption(profile, profile_devices, accuracy_scores)
            context['page_title'] = f'Monitoramento Completo para: {profile.name}' 
        else:
            context['accuracy_metrics'] = {} # Ou um dicionário vazio
            context['page_title'] = 'Monitoramento de Rede'
            messages.info(self.request, "Você não tem perfis de energia. Por favor, crie um para começar a monitorar.")
            # O template pode mostrar uma mensagem ou um botão para criar perfil.
            # Um redirecionamento direto aqui em get_context_data pode ser complicado,
            # é melhor deixar o template lidar com o caso de 'profile' ser None.

        return context


# apps/pages/views.py
# ... (seus imports existentes)

class TrendsView(LoginRequiredMixin, TemplateView):
    """
    View para a seção de Tendências.
    Exibe o histórico de consumo do perfil.
    """
    template_name = 'trends.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Tenta obter profile_pk dos kwargs. Se não estiver presente, retorna None.
        # Isso evita o KeyError se 'profile_pk' não for fornecido na URL.
        profile_pk = self.kwargs.get('profile_pk')
        profile = None
        user = self.request.user

        if profile_pk:
            # Se um profile_pk foi fornecido na URL, tenta buscar aquele perfil específico
            profile = get_object_or_404(EnergyProfiles, pk=profile_pk, user=user)
        else:
            # Se nenhum profile_pk foi fornecido, tenta pegar o primeiro perfil do usuário
            # como um perfil padrão para exibir.
            profile = EnergyProfiles.objects.filter(user=user).first()
            
            # Se mesmo assim não houver perfis, exibe uma mensagem de erro e retorna
            if not profile:
                context['message'] = "Você não possui perfis de energia. Por favor, crie um para visualizar as tendências."
                context['page_title'] = 'Tendências de Consumo (Nenhum Perfil)'
                return context

        # Pega as previsões de consumo associadas aos dispositivos deste perfil
        # Certifique-se de que a queryset seja filtrada pelo perfil obtido
        consumption_predictions_queryset = ConsumptionPredictions.objects.filter(
            profile=profile # Agora 'profile' certamente será um objeto EnergyProfiles válido
        ).order_by('prediction_date')

        # Chama a função utilitária para calcular os dados de tendência
        context['trends_data'] = calculate_comprehensive_trends_data(profile, consumption_predictions_queryset)
        context['profile'] = profile # Passa o objeto perfil para o template
        context['page_title'] = f'Tendências de Consumo para: {profile.name}' # Título dinâmico

        # Adiciona todos os perfis do usuário ao contexto. Isso é útil se você quiser
        # ter um seletor de perfil na página de tendências para que o usuário possa alternar.
        context['all_user_profiles'] = EnergyProfiles.objects.filter(user=user).order_by('name')

        return context


class ForecastView(LoginRequiredMixin, TemplateView):
    template_name = 'forecast.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        profile_pk = self.kwargs.get('profile_pk')
        profile = None

        if profile_pk:
            profile = get_object_or_404(EnergyProfiles, pk=profile_pk, user=user)
        else:
            profile = EnergyProfiles.objects.filter(user=user).first()
            if not profile:
                context['message'] = "Você não possui perfis de energia. Por favor, crie um para visualizar as previsões."
                context['page_title'] = 'Previsão de Consumo (Nenhum Perfil)'
                return context

        # Pega o primeiro modelo de previsão ativo
        prediction_model_instance = PredictionModels.objects.filter(is_active=True).first()

        if not prediction_model_instance:
            context['message'] = "Nenhum modelo de previsão ativo encontrado para gerar a previsão. Por favor, configure um modelo."
            context['page_title'] = f'Previsões de Consumo para: {profile.name}'
            context['profile'] = profile
            context['all_user_profiles'] = EnergyProfiles.objects.filter(user=user).order_by('name')
            return context

        # --- NOVO: Tenta obter um ProfileDevice padrão para o perfil ---
        # Vamos pegar o primeiro ProfileDevice do perfil, ou None se não houver.
        # Se for None e o campo for NOT NULL, teremos um problema,
        # então precisamos garantir que haja ProfileDevices para o perfil.
        default_profile_device = ProfileDevices.objects.filter(profile=profile).first()

        if not default_profile_device:
            context['message'] = "Não foi possível gerar previsões. O perfil não possui dispositivos cadastrados, e um dispositivo é necessário para a previsão."
            context['page_title'] = f'Previsões de Consumo para: {profile.name}'
            context['profile'] = profile
            context['all_user_profiles'] = EnergyProfiles.objects.filter(user=user).order_by('name')
            messages.error(self.request, "Crie um dispositivo para o perfil para gerar previsões.")
            return context


        forecast_data = {
            'forecast_data': [],
            'forecast_chart_json': None,
            'forecast_accuracy': None,
            'error_message': None
        }

        result_forecast_data = calculate_forecast_data(profile, prediction_model_instance)

        if 'forecast_data' in result_forecast_data and result_forecast_data['forecast_data']:
            for record in result_forecast_data['forecast_data']:
                prediction_date_obj = record['ds'].date() if hasattr(record['ds'], 'date') else record['ds']
                predicted_kwh_val = Decimal(str(record.get('yhat', 0.0)))
                predicted_daily_kwh_val = Decimal(str(record.get('yhat', 0.0)))

                ConsumptionPredictions.objects.update_or_create(
                    profile=profile,
                    prediction_date=prediction_date_obj,
                    defaults={
                        'profile_device': default_profile_device, 
                        'model': prediction_model_instance,
                        'predicted_kwh': predicted_kwh_val,
                        'predicted_daily_kwh': predicted_daily_kwh_val,
                        'confidence_score': Decimal('0.90'),
                        'is_final': True,
                    }
                )
            messages.success(self.request, "Previsões futuras geradas e salvas com sucesso!")
            forecast_data = result_forecast_data
        else:
            messages.warning(self.request, result_forecast_data.get('error_message', "Não foi possível gerar previsões futuras ou dados insuficientes."))
            forecast_data['error_message'] = result_forecast_data.get('error_message')
            context['message'] = result_forecast_data.get('error_message')

        context['forecast_data'] = forecast_data
        context['profile'] = profile
        context['page_title'] = f'Previsões de Consumo para: {profile.name}'
        context['all_user_profiles'] = EnergyProfiles.objects.filter(user=user).order_by('name')

        return context


class KPIListView(LoginRequiredMixin, ListView):
    """
    Lista todos os KPIs aos quais o usuário tem acesso (associados aos seus perfis ou globais).
    """
    model = KPI
    template_name = 'kpis/kpi_list.html'
    context_object_name = 'kpis'
    paginate_by = 10

    def get_queryset(self):
        # Retorna KPIs associados aos perfis do usuário OU KPIs sem perfil (globais)
        # Agora você pode usar Q diretamente
        return KPI.objects.filter(Q(profile__user=self.request.user) | Q(profile__isnull=True)).distinct().order_by('kpi_name')


class KPIDetailView(LoginRequiredMixin, DetailView):
    """
    Exibe os detalhes de um único KPI.
    """
    model = KPI
    template_name = 'kpis/kpi_detail.html'
    context_object_name = 'kpi'

    def get_queryset(self):
        # Garante que o usuário só possa ver KPIs que pertencem aos seus perfis ou são globais.
        # Agora você pode usar Q diretamente
        return KPI.objects.filter(Q(profile__user=self.request.user) | Q(profile__isnull=True)).distinct()


class KPICreateView(LoginRequiredMixin, CreateView):
    """
    Permite criar um novo KPI.
    """
    model = KPI
    form_class = KPIForm
    template_name = 'kpis/kpi_form.html'
    success_url = reverse_lazy('kpi_list')

    def get_form_kwargs(self):
        """Passa o usuário para o formulário para filtrar perfis."""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request # Passa a request para o formulário, se necessário para filtros no ChoiceField
        return kwargs

    def form_valid(self, form):
        # Se o perfil não for selecionado no formulário, pode ser um KPI global
        if not form.instance.profile:
            form.instance.profile = None # Define explicitamente como None se não for selecionado

        return super().form_valid(form)
    

class MonitoramentoRedeView(LoginRequiredMixin, TemplateView):
    """
    View para a página de monitoramento de rede, exibindo dados de diversas análises.
    Requer autenticação do usuário.
    """
    template_name = 'monitoring_network.html' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Busca todos os perfis do usuário uma única vez
        all_profiles = EnergyProfiles.objects.filter(user=user).order_by('name')
        context['all_user_profiles'] = all_profiles

        profile = None
        profile_pk = self.kwargs.get('profile_pk')
        
        # Tenta obter o perfil de energia do usuário logado
        if profile_pk:
            # Busca o perfil pelo PK, se fornecido na URL
            profile = get_object_or_404(all_profiles, pk=profile_pk)
        elif all_profiles.exists():
            # Se não houver PK na URL, pega o primeiro perfil do usuário como padrão
            profile = all_profiles.first()
        
        context['profile'] = profile 

        # Se nenhum perfil foi encontrado, exibe uma mensagem amigável e retorna
        if not profile:
            context['message'] = "Nenhum perfil de energia encontrado para análise."
            context['page_title'] = 'Monitoramento da Rede'
            return context
        
        context['page_title'] = f'Monitoramento da Rede: {profile.name}'

        # --- Chamada das funções do utils.py ---
        start_date_quality = date.today() - timedelta(days=30)
        end_date_quality = date.today()

        quality_data, quality_message = get_quality_of_service_data(
            profile, start_date=start_date_quality, end_date=end_date_quality
        )
        context['quality_data'] = quality_data
        if quality_message:
            context['quality_data_message'] = quality_message
        
        prediction_analytics = get_prediction_comparison_analytics(profile)
        context['prediction_data'] = prediction_analytics
        if prediction_analytics.get('message'):
            context['prediction_data_message'] = prediction_analytics['message']

        return context

class ReportGeneratorView(LoginRequiredMixin, FormView):
    template_name = 'reports/generator.html'
    form_class = ReportGeneratorForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        profile = form.cleaned_data['profile']
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        metrics = form.cleaned_data['metrics']
        report_format = form.cleaned_data['format']

        # Chama a função de utilidade para gerar o arquivo
        file_content, filename = generate_custom_report(
            profile, start_date, end_date, metrics, report_format
        )

        if report_format == 'pdf':
            response = HttpResponse(file_content, content_type='application/pdf')
        elif report_format == 'csv':
            response = HttpResponse(file_content, content_type='text/csv')
        
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

class KPIUpdateView(LoginRequiredMixin, UpdateView):
    """
    Permite atualizar um KPI existente.
    """
    model = KPI
    form_class = KPIForm
    template_name = 'kpis/kpi_form.html'

    def get_queryset(self):
        # Garante que o usuário só possa editar KPIs que pertencem aos seus perfis ou são globais.
        return KPI.objects.filter(models.Q(profile__user=self.request.user) | models.Q(profile__isnull=True)).distinct()

    def get_success_url(self):
        return reverse_lazy('kpi_detail', kwargs={'pk': self.object.pk})


class KPIDeleteView(LoginRequiredMixin, DeleteView):
    """
    Permite deletar um KPI.
    """
    model = KPI
    template_name = 'kpis/kpi_confirm_delete.html'
    success_url = reverse_lazy('kpi_list')

    def get_queryset(self):
        # Garante que o usuário só possa deletar KPIs que pertencem aos seus perfis ou são globais.
        return KPI.objects.filter(models.Q(profile__user=self.request.user) | models.Q(profile__isnull=True)).distinct()

from .utils import classify_brand_efficiency 

class BrandEfficiencyReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/brand_efficiency_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # A função agora retorna 3 valores
        brand_ranking, message, chart_json = classify_brand_efficiency(analysis_type='HYBRID')
        
        context['brand_ranking'] = brand_ranking
        context['message'] = message
        context['chart_json'] = chart_json # Adiciona o JSON do gráfico ao contexto
        context['page_title'] = "Relatório de Eficiência de Marcas (Teórico vs. Real)"
        return context

class PredictionModelsListView(LoginRequiredMixin, ListView):
    model = PredictionModels
    template_name = 'prediction_models/list.html'
    context_object_name = 'object_list'
    paginate_by = 10

class PredictionModelsDetailView(LoginRequiredMixin, DetailView):
    model = PredictionModels
    template_name = 'prediction_models/detail.html'
    context_object_name = 'object'

class PredictionModelsCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = PredictionModels
    form_class = PredictionModelsForm
    template_name = 'prediction_models/form.html'
    success_url = reverse_lazy('prediction_model_list')
    success_message = "Modelo de previsão criado com sucesso!"

class PredictionModelsUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = PredictionModels
    form_class = PredictionModelsForm
    template_name = 'prediction_models/form.html'
    success_url = reverse_lazy('prediction_model_list')
    success_message = "Modelo de previsão atualizado com sucesso!"

class PredictionModelsDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = PredictionModels
    template_name = 'prediction_models/confirm_delete.html'
    success_url = reverse_lazy('prediction_model_list')
    success_message = "Modelo de previsão excluído com sucesso!"