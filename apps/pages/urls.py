from . import views

# pages/urls.py
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from .views import (
    AdminAlertListView,
    BrandEfficiencyReportView,
    SensorDataIngestionView,
    SensorStatusView,
    UserProfileView,
    DeviceCatalogListView,
    DeviceCatalogDetailView,
    DeviceCatalogCreateView,
    DeviceCatalogUpdateView,
    DeviceCatalogDeleteView,
    EnergyProfileListView,
    EnergyProfileDetailView,
    EnergyProfileCreateView,
    EnergyProfileUpdateView,
    EnergyProfileDeleteView,
    OutlierAnalysisView,
    ProfileDeviceCreateView,
    ProfileDeviceUpdateView,
    ProfileDeviceDeleteView,

    BenchmarkView,
    MonitoringView,
    SmartDashboardView,
    TrendsView,
    ForecastView,

    KPIListView,
    KPIDetailView,
    KPICreateView,
    KPIUpdateView,
    KPIDeleteView,
    PublicLandingView,
    DashboardView,

    EnergyTariffListView,
    EnergyTariffDetailView,
    EnergyTariffCreateView,
    EnergyTariffUpdateView,
    EnergyTariffDeleteView,

    TariffFlagAdditiveListView,
    TariffFlagAdditiveDetailView,
    TariffFlagAdditiveCreateView,
    TariffFlagAdditiveUpdateView,
    TariffFlagAdditiveDeleteView,

    BillingRecordListView,
    BillingRecordDetailView,
    BillingRecordCreateView,
    BillingRecordUpdateView,
    BillingRecordDeleteView,

    EnergyQualityRecordListView,
    EnergyQualityRecordDetailView,
    EnergyQualityRecordCreateView,
    EnergyQualityRecordUpdateView,
    EnergyQualityRecordDeleteView,

    OptimizationSuggestionListView,
    OptimizationSuggestionDetailView,
    OptimizationSuggestionCreateView,
    OptimizationSuggestionUpdateView,
    OptimizationSuggestionDeleteView,

    AlertListView,
    AlertDetailView,
    AlertCreateView,
    AlertUpdateView,
    AlertDeleteView,

    ConsumptionGoalListView,
    ConsumptionGoalDetailView,
    ConsumptionGoalCreateView,
    ConsumptionGoalUpdateView,
    ConsumptionGoalDeleteView,

    EnergyReadingListView,
    EnergyReadingDetailView,
    EnergyReadingCreateView,
    EnergyReadingUpdateView,
    EnergyReadingDeleteView,

    ModelAccuracyScoresListView,
    ModelAccuracyScoresDetailView,
    ModelAccuracyScoresCreateView,
    ModelAccuracyScoresUpdateView,
    ModelAccuracyScoresDeleteView,

    DeviceUsagePatternListView,
    DeviceUsagePatternDetailView,
    DeviceUsagePatternCreateView,
    DeviceUsagePatternUpdateView,
    DeviceUsagePatternDeleteView,

    HistoricalPredictionComparisonListView,
    HistoricalPredictionComparisonDetailView,
    HistoricalPredictionComparisonCreateView,
    HistoricalPredictionComparisonUpdateView,
    HistoricalPredictionComparisonDeleteView,

    UserPreferencesDetailView,
    UserPreferencesCreateView,
    UserPreferencesUpdateView,
    UserPreferencesDeleteView,

    PredictionModelsListView,
    PredictionModelsDetailView,
    PredictionModelsCreateView,
    PredictionModelsUpdateView,
    PredictionModelsDeleteView,
    bulk_update_notifications,
    sensor_status_api,
    unread_notification_count_api
)

urlpatterns = [
    #path('', views.index, name='index'),
    path('', PublicLandingView.as_view(), name='home'),
    path('dashboard/', login_required(DashboardView.as_view()), name='dashboard'), 
    path('api/v1/reading/', SensorDataIngestionView.as_view(), name='api_ingest_reading'),
    path('sensor-status/', SensorStatusView.as_view(), name='sensor_status'),
    path('api/v1/sensor-status/<int:profile_pk>/', sensor_status_api, name='api_sensor_status'),
    # URLs para DeviceCatalog
    path('devices/', DeviceCatalogListView.as_view(), name='device_list'),
    path('devices/new/', DeviceCatalogCreateView.as_view(), name='device_create'),
    path('devices/<int:pk>/', DeviceCatalogDetailView.as_view(), name='device_detail'),
    path('devices/<int:pk>/edit/', DeviceCatalogUpdateView.as_view(), name='device_update'),
    path('devices/<int:pk>/delete/', DeviceCatalogDeleteView.as_view(), name='device_delete'),

    #path('api/task_status/<str:task_id>/', views.get_task_status, name='get_task_status'),
    path('webpush/', include('webpush.urls')),

    # --- URLs para EnergyProfiles (CRUD 1: Gerenciar Perfis de Consumo) ---

    path('profiles/', login_required(EnergyProfileListView.as_view()), name='profile_list'),
    path('profiles/new/', login_required(EnergyProfileCreateView.as_view()), name='profile_create'),
    path('profiles/<int:pk>/', login_required(EnergyProfileDetailView.as_view()), name='profile_detail'),
    path('profiles/<int:pk>/edit/', login_required(EnergyProfileUpdateView.as_view()), name='profile_update'),
    path('profiles/<int:pk>/delete/', login_required(EnergyProfileDeleteView.as_view()), name='profile_delete'),

    path('profile/', login_required(UserProfileView.as_view()), name='profile'),

    # --- URLs para ProfileDevices (CRUD 2: Gerenciar Dispositivos Associados a Perfis) ---
    path('profiles/<int:profile_pk>/devices/add/', login_required(ProfileDeviceCreateView.as_view()), name='profile_device_add'),
    path('profile_devices/<int:pk>/edit/', login_required(ProfileDeviceUpdateView.as_view()), name='profile_device_update'),
    path('profile_devices/<int:pk>/delete/', login_required(ProfileDeviceDeleteView.as_view()), name='profile_device_delete'),

    # --- URLs para as Seções do Dashboard ---
    path('profiles/<int:profile_pk>/benchmark/', login_required(BenchmarkView.as_view()), name='benchmark'),
    path('profiles/<int:profile_pk>/monitoring/', login_required(MonitoringView.as_view()), name='monitoring'),
    path('profiles/<int:profile_pk>/trends/', login_required(TrendsView.as_view()), name='trends'),
    path('profiles/<int:profile_pk>/forecast/', login_required(ForecastView.as_view()), name='forecast'),
    path('profiles/<int:profile_pk>/monitoring_network/', views.MonitoramentoRedeView.as_view(), name='monitoring_network'),
    path('profiles/<int:profile_pk>/outliers/', OutlierAnalysisView.as_view(), name='outliers_analisys'),
    path('profiles/<int:profile_pk>/smart_dashboard/', SmartDashboardView.as_view(), name='smart_dashboard'),
    path('api/smart_dashboard_data/<int:profile_pk>/', views.SmartDashboardDataAPIView.as_view(), name='get_smart_dashboard_data'),

    path('smart_dashboard/', SmartDashboardView.as_view(), name='global_smart_dashboard'),
    path('monitoring_network/', views.MonitoramentoRedeView.as_view(), name='global_monitoring_network'),
    path('outliers/', OutlierAnalysisView.as_view(), name='global_outliers_analisys'),
    path('monitoring/', MonitoringView.as_view(), name='global_monitoring'),
    path('benchmark/', BenchmarkView.as_view(), name='global_benchmark'),
    path('trends/', TrendsView.as_view(), name='global_trends'),
    path('forecast/', ForecastView.as_view(), name='global_forecast'),


    path('kpis/', login_required(KPIListView.as_view()), name='kpi_list'),
    path('kpis/new/', login_required(KPICreateView.as_view()), name='kpi_create'),
    path('kpis/<int:pk>/', login_required(KPIDetailView.as_view()), name='kpi_detail'),
    path('kpis/<int:pk>/edit/', login_required(KPIUpdateView.as_view()), name='kpi_update'),
    path('kpis/<int:pk>/delete/', login_required(KPIDeleteView.as_view()), name='kpi_delete'),

        # --- URLs para EnergyTariff ---
    path('energy_tariffs/', EnergyTariffListView.as_view(), name='energy_tariff_list'),
    path('energy_tariffs/create/', EnergyTariffCreateView.as_view(), name='energy_tariff_create'),
    path('energy_tariffs/<int:pk>/', EnergyTariffDetailView.as_view(), name='energy_tariff_detail'),
    path('energy_tariffs/<int:pk>/update/', EnergyTariffUpdateView.as_view(), name='energy_tariff_update'),
    path('energy_tariffs/<int:pk>/delete/', EnergyTariffDeleteView.as_view(), name='energy_tariff_delete'),


    path('tariff_flags/', TariffFlagAdditiveListView.as_view(), name='tariff_flag_list'),
    path('tariff_flags/<int:pk>/', TariffFlagAdditiveDetailView.as_view(), name='tariff_flag_detail'),
    path('tariff_flags/create/', TariffFlagAdditiveCreateView.as_view(), name='tariff_flag_create'),
    path('tariff_flags/<int:pk>/update/', TariffFlagAdditiveUpdateView.as_view(), name='tariff_flag_update'),
    path('tariff_flags/<int:pk>/delete/', TariffFlagAdditiveDeleteView.as_view(), name='tariff_flag_delete'),

     # --- URLs para BillingRecord ---
    path('billing_records/', BillingRecordListView.as_view(), name='billing_record_list'),
    path('billing_records/create/', BillingRecordCreateView.as_view(), name='billing_record_create'),
    path('billing_records/<int:pk>/', BillingRecordDetailView.as_view(), name='billing_record_detail'),
    path('billing_records/<int:pk>/update/', BillingRecordUpdateView.as_view(), name='billing_record_update'),
    path('billing_records/<int:pk>/delete/', BillingRecordDeleteView.as_view(), name='billing_record_delete'),

    # --- URLs para EnergyQualityRecord ---
    path('energy_quality_records/', EnergyQualityRecordListView.as_view(), name='energy_quality_list'),
    path('energy_quality_records/create/', EnergyQualityRecordCreateView.as_view(), name='energy_quality_create'),
    path('energy_quality_records/<int:pk>/', EnergyQualityRecordDetailView.as_view(), name='energy_quality_detail'),
    path('energy_quality_records/<int:pk>/update/', EnergyQualityRecordUpdateView.as_view(), name='energy_quality_update'),
    path('energy_quality_records/<int:pk>/delete/', EnergyQualityRecordDeleteView.as_view(), name='energy_quality_delete'),

    # --- URLs para OptimizationSuggestion ---
    path('optimization_suggestions/', OptimizationSuggestionListView.as_view(), name='optimization_suggestion_list'),
    path('optimization_suggestions/create/', OptimizationSuggestionCreateView.as_view(), name='optimization_suggestion_create'),
    path('optimization_suggestions/<int:pk>/', OptimizationSuggestionDetailView.as_view(), name='optimization_suggestion_detail'),
    path('optimization_suggestions/<int:pk>/update/', OptimizationSuggestionUpdateView.as_view(), name='optimization_suggestion_update'),
    path('optimization_suggestions/<int:pk>/delete/', OptimizationSuggestionDeleteView.as_view(), name='optimization_suggestion_delete'),

    path('notifications/', AlertListView.as_view(), name='notification_inbox'),
    path('notifications/', AlertListView.as_view(), name='notification_inbox'),
    path('notifications/bulk-update/', bulk_update_notifications, name='notification_bulk_update'),
    path('api/unread-notification-count/', unread_notification_count_api, name='api_unread_count'),

    path('alerts/', AdminAlertListView.as_view(), name='alert_admin_list'),

    # --- URLs para Alert ---
    path('alerts/create/', AlertCreateView.as_view(), name='alert_create'),
    path('alerts/<int:pk>/', AlertDetailView.as_view(), name='alert_detail'),
    path('alerts/<int:pk>/update/', AlertUpdateView.as_view(), name='alert_update'),
    path('alerts/<int:pk>/delete/', AlertDeleteView.as_view(), name='alert_delete'),

    # --- URLs para ConsumptionGoal ---
    path('consumption_goals/', ConsumptionGoalListView.as_view(), name='consumption_goal_list'),
    path('consumption_goals/create/', ConsumptionGoalCreateView.as_view(), name='consumption_goal_create'),
    path('consumption_goals/<int:pk>/', ConsumptionGoalDetailView.as_view(), name='consumption_goal_detail'),
    path('consumption_goals/<int:pk>/update/', ConsumptionGoalUpdateView.as_view(), name='consumption_goal_update'),
    path('consumption_goals/<int:pk>/delete/', ConsumptionGoalDeleteView.as_view(), name='consumption_goal_delete'),

    # --- URLs para EnergyReading ---
    path('energy_readings/', EnergyReadingListView.as_view(), name='energy_reading_list'),
    path('energy_readings/create/', EnergyReadingCreateView.as_view(), name='energy_reading_create'),
    path('energy_readings/<int:pk>/', EnergyReadingDetailView.as_view(), name='energy_reading_detail'),
    path('energy_readings/<int:pk>/update/', EnergyReadingUpdateView.as_view(), name='energy_reading_update'),
    path('energy_readings/<int:pk>/delete/', EnergyReadingDeleteView.as_view(), name='energy_reading_delete'),

    # --- URLs para ModelAccuracyScores ---
    path('model_accuracy_scores/', ModelAccuracyScoresListView.as_view(), name='model_accuracy_score_list'),
    path('model_accuracy_scores/create/', ModelAccuracyScoresCreateView.as_view(), name='model_accuracy_score_create'),
    path('model_accuracy_scores/<int:pk>/', ModelAccuracyScoresDetailView.as_view(), name='model_accuracy_score_detail'),
    path('model_accuracy_scores/<int:pk>/update/', ModelAccuracyScoresUpdateView.as_view(), name='model_accuracy_score_update'),
    path('model_accuracy_scores/<int:pk>/delete/', ModelAccuracyScoresDeleteView.as_view(), name='model_accuracy_score_delete'),

    # --- URLs para DeviceUsagePattern ---
    path('device_usage_patterns/', DeviceUsagePatternListView.as_view(), name='device_usage_pattern_list'),
    path('device_usage_patterns/create/', DeviceUsagePatternCreateView.as_view(), name='device_usage_pattern_create'),
    path('device_usage_patterns/<int:pk>/', DeviceUsagePatternDetailView.as_view(), name='device_usage_pattern_detail'),
    path('device_usage_patterns/<int:pk>/update/', DeviceUsagePatternUpdateView.as_view(), name='device_usage_pattern_update'),
    path('device_usage_patterns/<int:pk>/delete/', DeviceUsagePatternDeleteView.as_view(), name='device_usage_pattern_delete'),

    path('prediction_models/', PredictionModelsListView.as_view(), name='prediction_model_list'),
    path('prediction_models/create/', PredictionModelsCreateView.as_view(), name='prediction_model_create'),
    path('prediction_models/<int:pk>/', PredictionModelsDetailView.as_view(), name='prediction_model_detail'),
    path('prediction_models/<int:pk>/update/', PredictionModelsUpdateView.as_view(), name='prediction_model_update'),
    path('prediction_models/<int:pk>/delete/', PredictionModelsDeleteView.as_view(), name='prediction_model_delete'),

    path('reports/brand-efficiency/', BrandEfficiencyReportView.as_view(), name='brand_efficiency_report'),

    # --- URLs para HistoricalPredictionComparison ---
    path('historical_prediction_comparisons/', HistoricalPredictionComparisonListView.as_view(), name='historical_prediction_comparison_list'),
    path('historical_prediction_comparisons/create/', HistoricalPredictionComparisonCreateView.as_view(), name='historical_prediction_comparison_create'),
    path('historical_prediction_comparisons/<int:pk>/', HistoricalPredictionComparisonDetailView.as_view(), name='historical_prediction_comparison_detail'),
    path('historical_prediction_comparisons/<int:pk>/update/', HistoricalPredictionComparisonUpdateView.as_view(), name='historical_prediction_comparison_update'),
    path('historical_prediction_comparisons/<int:pk>/delete/', HistoricalPredictionComparisonDeleteView.as_view(), name='historical_prediction_comparison_delete'),

    # --- URLs para UserPreferences ---
    # Nota: Não usamos PK na URL para detalhe/edição/exclusão, pois é sempre do usuário logado
    path('my_preferences/', login_required(UserPreferencesDetailView.as_view()), name='user_preferences_detail'),
    path('my_preferences/create/', login_required(UserPreferencesCreateView.as_view()), name='user_preferences_create'),
    path('my_preferences/update/', login_required(UserPreferencesUpdateView.as_view()), name='user_preferences_update'),
    path('my_preferences/delete/', login_required(UserPreferencesDeleteView.as_view()), name='user_preferences_delete'),

]