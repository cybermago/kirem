1. Principais Entidades (Classes)

As entidades representam os objetos de dados fundamentais no sistema, geralmente mapeados para modelos Django e tabelas no banco de dados PostgreSQL.
1.1. Entidades de Usuário e Perfil

    User (Modelo Padrão do Django)

        Descrição: Representa os usuários do sistema. É o ponto central para autenticação e autorização.

        Atributos Chave: username, email, password, first_name, last_name.

        Relacionamentos: Um usuário pode ter múltiplos EnergyProfiles, Alerts e UserPreferences.

    EnergyProfiles

        Descrição: Define um perfil de energia específico criado por um usuário, representando uma residência, escritório ou qualquer unidade de consumo.

        Atributos Chave: name, description, user (FK para User), subgroup, voltage_group, supply_type, tariff_classification, nominal_voltage, classification, subclass, default_tariff (FK para EnergyTariff).

        Relacionamentos: Associado a um User, pode ter múltiplos ProfileDevices, KPIs, EnergyReadings (agregadas), Alerts, ConsumptionGoals, BillingRecords e uma única LocationInfo.

    LocationInfo

        Descrição: Armazena informações geográficas e de endereço associadas a um EnergyProfile.

        Atributos Chave: profile (OneToOneField para EnergyProfiles), address_line1, address_line2, city, state, zip_code, country, latitude, longitude.

        Relacionamentos: Um para um com EnergyProfiles.

    UserPreferences

        Descrição: Registra as configurações e preferências personalizadas de cada usuário.

        Atributos Chave: user (OneToOneField para User), theme_preference, notification_frequency, report_format_preference, receive_marketing_emails.

        Relacionamentos: Um para um com User.

1.2. Entidades de Dispositivos e Consumo

    DeviceCatalog

        Descrição: Um catálogo global de dispositivos elétricos comuns com dados de referência.

        Atributos Chave: name, icon, avg_kwh (consumo médio em kWh/dia), procel_seal.

        Relacionamentos: Pode ser referenciado por múltiplos ProfileDevices.

    ProfileDevices

        Descrição: Representa um dispositivo específico associado a um EnergyProfile, com detalhes de uso personalizados pelo usuário.

        Atributos Chave: profile (FK para EnergyProfiles), device (FK para DeviceCatalog), quantity, hours_per_day, custom_name.

        Relacionamentos: Associado a um EnergyProfiles e um DeviceCatalog. Pode ter múltiplos ConsumptionPredictions, EnergyReadings e DeviceUsagePatterns.

    EnergyReading

        Descrição: Armazena registros de consumo de energia medidos (reais) para um dispositivo ou perfil.

        Atributos Chave: profile_device (FK opcional para ProfileDevices), profile (FK opcional para EnergyProfiles), reading_date, reading_time, kwh_consumed, reading_type (horário, diário, mensal).

        Relacionamentos: Associado a um ProfileDevices ou a um EnergyProfiles.

    DeviceUsagePattern

        Descrição: Define padrões de uso detalhados para um ProfileDevice por dia da semana e horário.

        Atributos Chave: profile_device (FK para ProfileDevices), day_of_week, start_time, end_time, intensity_factor, description.

        Relacionamentos: Associado a um ProfileDevices.

1.3. Entidades de Faturamento e Tarifas

    EnergyTariff

        Descrição: Define as diferentes tarifas base de energia elétrica (sem adicionais de bandeira).

        Atributos Chave: name, rate_per_kwh, start_date, end_date, description, is_active, tariff_type.

        Relacionamentos: Pode ser referenciada como default_tariff em EnergyProfiles e tariff_applied em BillingRecord.

    TariffFlagAdditive

        Descrição: Registra os valores adicionais das Bandeiras Tarifárias (verde, amarela, vermelha) por período.

        Atributos Chave: flag_type, additional_cost_per_100kwh, start_date, end_date, notes.

        Relacionamentos: Usado para definir as opções de tariff_flag_type em BillingRecord.

    BillingRecord

        Descrição: Representa um registro detalhado de fatura de energia para um EnergyProfile.

        Atributos Chave: profile (FK para EnergyProfiles), bill_date, start_period, end_period, days_billed, kwh_total_billed, total_cost, tariff_applied (FK para EnergyTariff), unit_price_kwh, tariff_unit_kwh, tariff_flag_type, flag_additional_cost_per_100kwh, meter_id, previous_reading, current_reading, meter_constant, next_reading_date, icms_base, icms_aliquot, icms_value, pis_base, pis_aliquot, pis_value, cofins_base, cofins_aliquot, cofins_value, cip_cost, fine_cost, monetary_correction_cost, interest_cost, notes.

        Relacionamentos: Associado a um EnergyProfiles e a uma EnergyTariff.

1.4. Entidades de Machine Learning e Análise

    PredictionModels

        Descrição: Catálogo dos modelos de previsão de Machine Learning utilizados no sistema.

        Atributos Chave: name, version.

        Relacionamentos: Pode ser referenciado por múltiplos ConsumptionPredictions e ModelAccuracyScores.

    ConsumptionPredictions

        Descrição: Armazena as previsões de consumo de energia geradas pelos modelos de ML para um ProfileDevice.

        Atributos Chave: profile_device (FK para ProfileDevices), model (FK para PredictionModels), prediction_date, predicted_daily_kwh.

        Relacionamentos: Associado a um ProfileDevices e um PredictionModels. Pode ter uma HistoricalPredictionComparison.

    ModelAccuracyScores

        Descrição: Registra as pontuações de precisão dos modelos de previsão em relação a perfis específicos.

        Atributos Chave: model (FK para PredictionModels), profile (FK para EnergyProfiles), score, calculation_date.

        Relacionamentos: Associado a um PredictionModels e um EnergyProfiles.

    HistoricalPredictionComparison

        Descrição: Compara o consumo real observado com as previsões históricas para avaliar a performance do modelo.

        Atributos Chave: prediction (OneToOneField para ConsumptionPredictions), actual_kwh_observed, comparison_date, error_kwh, percentage_error.

        Relacionamentos: Um para um com ConsumptionPredictions.

1.5. Entidades de Otimização e Metas

    KPI (Key Performance Indicator)

        Descrição: Define indicadores chave de performance para monitorar o consumo e a eficiência.

        Atributos Chave: name, description, unit, target_value, kpi_type, profile (FK opcional para EnergyProfiles).

        Relacionamentos: Pode ser associado a um EnergyProfiles.

    ConsumptionGoal

        Descrição: Permite ao usuário definir metas de consumo de energia para um perfil específico.

        Atributos Chave: profile (FK para EnergyProfiles), name, goal_type (redução %, meta absoluta, meta de custo), target_value, start_date, end_date, is_active, achieved_date.

        Relacionamentos: Associado a um EnergyProfiles.

    OptimizationSuggestion

        Descrição: Um catálogo de dicas e sugestões para otimizar o consumo de energia.

        Atributos Chave: title, description, category, estimated_savings_kwh_per_month, procel_seal_target, impact_level.

        Relacionamentos: Entidade independente, usada para fornecer recomendações.

    Alert

        Descrição: Representa um alerta gerado pelo sistema com base em condições predefinidas (ex: consumo elevado, meta excedida).

        Atributos Chave: profile (FK opcional para EnergyProfiles), user (FK opcional para User), message, alert_type, threshold_value, triggered_at, is_resolved.

        Relacionamentos: Pode ser associado a um EnergyProfiles ou a um User.