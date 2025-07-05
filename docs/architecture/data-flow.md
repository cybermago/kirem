Fluxo de Dados, ETL e Pipeline do Projeto EcoTrack

Esta seção detalha a arquitetura e os processos envolvidos no gerenciamento de dados do EcoTrack, desde a sua entrada no sistema até o seu uso em análises e modelos preditivos. Abordaremos o fluxo de dados, as etapas de ETL (Extract, Transform, Load) e a orquestração dos pipelines.
1. Fluxo de Dados (Data Flow)

O fluxo de dados no EcoTrack é projetado para garantir que as informações sejam capturadas, processadas e disponibilizadas de forma eficiente para os usuários e para os módulos de análise.
1.1. Entrada de Dados

Os dados entram no sistema principalmente através de duas fontes:

    Entrada Manual do Usuário (Interface Web):

        Fonte: Formulários Django na interface web (ex: criação/edição de EnergyProfiles, ProfileDevices, BillingRecords, EnergyReadings, ConsumptionGoals, DeviceUsagePatterns).

        Formato: Dados estruturados inseridos diretamente pelos usuários.

        Validação Inicial: Realizada pelo Django Forms (tipos de dados, campos obrigatórios, regras básicas).

    Catálogo de Referência (Pré-carregado):

        Fonte: Dados predefinidos no DeviceCatalog e OptimizationSuggestion.

        Formato: Dados estruturados, geralmente populados no início do projeto ou via interface de administração.

1.2. Processamento e Armazenamento Temporário

Uma vez inseridos, os dados passam por validação e são temporariamente manipulados na camada de aplicação (views Django, lógica de negócios em Python) antes de serem persistidos.
1.3. Persistência de Dados

Todos os dados processados são armazenados no banco de dados PostgreSQL. Cada entidade (como EnergyProfiles, ProfileDevices, BillingRecords) corresponde a uma tabela no banco de dados, garantindo a integridade e a persistência dos dados.
1.4. Saída de Dados

Os dados são recuperados do PostgreSQL e apresentados aos usuários ou utilizados por outros módulos:

    Interface Web (Dashboard e Página Pública):

        Consumo: Exibição de totais, tabelas detalhadas, gráficos (Chart.js) e carrosséis (Swiper.js).

        Relatórios: Geração de relatórios básicos.

        Sugestões: Apresentação de OptimizationSuggestions.

        Alertas: Notificações de Alerts.

    Módulos de Análise e Machine Learning:

        Dados são consultados para alimentar os modelos de previsão (ConsumptionPredictions, ModelAccuracyScores, HistoricalPredictionComparison).

2. ETL (Extract, Transform, Load)

As etapas de ETL são cruciais para garantir que os dados estejam limpos, consistentes e prontos para uso analítico.
2.1. Extract (Extração)

A fase de extração no EcoTrack ocorre principalmente de duas maneiras:

    Extração em Tempo Real (On-Demand):

        Processo: Quando um usuário interage com um formulário na interface web (ex: cria um EnergyProfile ou BillingRecord), os dados são extraídos diretamente do request.POST no Django.

        Ferramentas: Django Forms e a lógica das views (CreateView, UpdateView).

    Extração de Banco de Dados (Para Análise/ML):

        Processo: Para análises e modelos de Machine Learning, os dados são extraídos diretamente do PostgreSQL usando ORM do Django (QuerySets) ou, em casos mais complexos, SQL puro.

        Ferramentas: Django ORM, Pandas (para carregar dados em DataFrames para manipulação).

2.2. Transform (Transformação)

A fase de transformação é onde os dados brutos são limpos, validados, enriquecidos e preparados.

    Validação de Dados:

        Nível de Formulário: Django Forms realiza validações de tipo, formato e regras de negócio (ex: min, max, unique_together).

        Nível de Modelo: Django Models impõe restrições de banco de dados (ex: null=False, unique=True, choices).

    Cálculos Derivados:

        Consumo: Conversão de potência e horas de uso para kWh (daily_kwh_consumption, monthly_kwh_consumption, annual_kwh_consumption em ProfileDevices).

        Emissão de CO₂e: Cálculo baseado no consumo de kWh e um fator de emissão (Emissão de CO₂e (kg) = Consumo (kWh) \times \text{Fator de Emissão de Carbono por kWh (kg CO₂e/kWh)}).

        Custo: Cálculo de custo total da fatura, incluindo tarifas base, adicionais de bandeira e impostos.

        Erros de Previsão: Cálculo de error_kwh e percentage_error em HistoricalPredictionComparison.

    Normalização/Padronização (Para ML):

        Processo: Se necessário para modelos de ML, dados numéricos podem ser normalizados ou padronizados para melhorar o desempenho do algoritmo.

        Ferramentas: Scikit-Learn (ex: StandardScaler, MinMaxScaler).

    Engenharia de Features (Para ML):

        Processo: Criação de novas variáveis a partir das existentes (ex: "dia da semana" a partir de uma data, "hora do dia" a partir de um timestamp) para melhorar a capacidade preditiva dos modelos.

        Ferramentas: Pandas, lógica Python.

2.3. Load (Carregamento)

A fase de carregamento consiste em persistir os dados transformados no armazenamento final.

    Banco de Dados (PostgreSQL):

        Processo: Os dados validados e transformados são salvos nos modelos Django, que por sua vez, os persistem nas tabelas correspondentes do PostgreSQL.

        Ferramentas: Django ORM (.save(), bulk_create()).

        Transações: Uso de django.db.transaction.atomic() para garantir a integridade em operações que envolvem múltiplos modelos (ex: criar EnergyProfile e LocationInfo juntos).

3. Pipeline

O conceito de pipeline no EcoTrack refere-se à orquestração de etapas sequenciais para processar dados e gerar resultados, especialmente no contexto de Machine Learning.
3.1. Pipeline de Dados (Geral)

Este pipeline descreve o fluxo de dados através do sistema:

    Captura de Dados: Usuário insere dados via formulários web.

    Validação Inicial: Django Forms valida a entrada.

    Pré-processamento Leve: Cálculos básicos (kWh, CO₂e) e associações de FK.

    Persistência: Dados salvos no PostgreSQL.

    Consulta para Análise/ML: Dados extraídos do PostgreSQL.

    Transformação Profunda: Limpeza, engenharia de features, normalização (se para ML).

    Modelagem/Análise: Aplicação de algoritmos de ML ou funções de análise.

    Geração de Resultados: Previsões, KPIs, sugestões, alertas.

    Persistência de Resultados: Resultados (ex: ConsumptionPredictions, ModelAccuracyScores) salvos no PostgreSQL.

    Visualização: Resultados apresentados na interface web.

3.2. Pipeline de Machine Learning (Exemplo: Previsão de Consumo)

Focado especificamente no módulo de Machine Learning:

    Coleta de Dados Históricos:

        Origem: EnergyReadings, ProfileDevices, DeviceUsagePattern, BillingRecords do PostgreSQL.

        Processo: Consulta e extração de dados relevantes para treinamento do modelo.

    Preparação de Dados (Pré-processamento):

        Limpeza: Tratamento de valores ausentes, outliers (se aplicável).

        Engenharia de Features: Criação de variáveis como "consumo por hora", "dia da semana", "mês", "temperatura média" (se dados externos forem integrados).

        Codificação: Transformação de variáveis categóricas (ex: tipo de dispositivo) em formato numérico (One-Hot Encoding).

        Escalonamento: Normalização ou padronização de variáveis numéricas.

        Ferramentas: Pandas, Scikit-Learn (pré-processadores).

    Treinamento do Modelo:

        Processo: O modelo LinearRegression() (ou outro algoritmo) é treinado com os dados preparados.

        Ferramentas: Scikit-Learn.

        Persistência do Modelo: O modelo treinado pode ser serializado (ex: com joblib ou pickle) e salvo para uso futuro, evitando retreinamento constante.

    Geração de Previsões:

        Processo: O modelo treinado recebe novos dados de entrada (ex: horas de uso futuras, quantidade de dispositivos) e gera predicted_daily_kwh.

        Ferramentas: Scikit-Learn.

    Armazenamento de Previsões:

        Processo: As previsões são salvas na entidade ConsumptionPredictions no PostgreSQL.

    Avaliação do Modelo:

        Processo: Acurácia do modelo é calculada comparando previsões com consumo real (HistoricalPredictionComparison, ModelAccuracyScores).

        Ferramentas: Scikit-Learn (métricas de regressão), lógica Python.

    Feedback Loop (Futuro):

        Processo: A performance do modelo é monitorada. Se a acurácia cair, o modelo pode ser retreinado com novos dados.

        Ferramentas: Tarefas agendadas (ex: Celery, Cron jobs) para retreinamento periódico.
