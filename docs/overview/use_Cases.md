2. Casos de Uso

Os casos de uso descrevem as interações entre os usuários (ou o sistema) e o EcoTrack para alcançar um objetivo específico.
2.1. Casos de Uso de Gerenciamento de Usuário e Perfil

    CU001: Registrar Novo Usuário

        Ator: Usuário não autenticado.

        Objetivo: Criar uma nova conta no sistema EcoTrack.

        Fluxo: Usuário acessa a página de registro, preenche informações (email, senha), envia formulário. Sistema valida e cria a conta.

    CU002: Realizar Login

        Ator: Usuário não autenticado.

        Objetivo: Acessar a área restrita do sistema.

        Fluxo: Usuário acessa a página de login, insere credenciais, envia formulário. Sistema autentica e redireciona para o dashboard.

    CU003: Criar Perfil de Energia

        Ator: Usuário autenticado.

        Objetivo: Configurar uma unidade de consumo (ex: casa, escritório) para monitoramento.

        Fluxo: Usuário acessa a seção de perfis, clica em "Criar Novo Perfil", preenche dados (nome, descrição, dados do talão, localização), envia formulário. Sistema valida e salva o perfil.

    CU004: Visualizar Lista de Perfis de Energia

        Ator: Usuário autenticado.

        Objetivo: Ver todos os perfis de energia associados à sua conta.

        Fluxo: Usuário acessa a seção de perfis, e a lista é exibida.

    CU005: Editar Perfil de Energia Existente

        Ator: Usuário autenticado.

        Objetivo: Atualizar as informações de um perfil de energia.

        Fluxo: Usuário seleciona um perfil, clica em "Editar", modifica os dados, envia formulário. Sistema valida e atualiza o perfil.

    CU006: Excluir Perfil de Energia

        Ator: Usuário autenticado.

        Objetivo: Remover um perfil de energia e todos os dados associados.

        Fluxo: Usuário seleciona um perfil, clica em "Excluir", confirma a exclusão. Sistema remove o perfil e seus dados relacionados.

    CU007: Gerenciar Preferências do Usuário

        Ator: Usuário autenticado.

        Objetivo: Personalizar configurações como tema, frequência de notificações e formato de relatórios.

        Fluxo: Usuário acessa a seção de preferências, modifica as opções, salva as alterações.

2.2. Casos de Uso de Gerenciamento de Dispositivos e Consumo

    CU008: Associar Dispositivo a um Perfil

        Ator: Usuário autenticado.

        Objetivo: Adicionar um eletrodoméstico ou eletrônico para monitoramento em um perfil.

        Fluxo: Usuário seleciona um perfil, clica em "Adicionar Dispositivo", escolhe um dispositivo do catálogo ou insere um novo, define quantidade e horas de uso, envia.

    CU009: Visualizar Detalhes do Dispositivo no Perfil

        Ator: Usuário autenticado.

        Objetivo: Ver informações detalhadas e consumo de um dispositivo específico associado a um perfil.

        Fluxo: Usuário seleciona um perfil, depois um dispositivo, e os detalhes são exibidos.

    CU010: Editar Detalhes de Uso de Dispositivo

        Ator: Usuário autenticado.

        Objetivo: Atualizar a quantidade ou horas de uso de um dispositivo associado a um perfil.

        Fluxo: Usuário seleciona um dispositivo, clica em "Editar", modifica os dados, envia.

    CU011: Excluir Dispositivo de um Perfil

        Ator: Usuário autenticado.

        Objetivo: Remover um dispositivo do monitoramento de um perfil.

        Fluxo: Usuário seleciona um dispositivo, clica em "Excluir", confirma.

    CU012: Registrar Leitura de Energia

        Ator: Usuário autenticado.

        Objetivo: Inserir dados de consumo real (kWh) para um dispositivo ou perfil.

        Fluxo: Usuário acessa a seção de leituras, insere data, hora e kWh consumido, seleciona dispositivo/perfil, envia.

    CU013: Definir Padrão de Uso de Dispositivo

        Ator: Usuário autenticado.

        Objetivo: Especificar horários e dias de uso para um dispositivo.

        Fluxo: Usuário seleciona um dispositivo, define dias da semana, horários de início/fim e fator de intensidade, salva.

2.3. Casos de Uso de Análise e Previsão

    CU014: Visualizar Dashboard de Consumo

        Ator: Usuário autenticado.

        Objetivo: Obter uma visão geral do consumo, custos e emissões de seus perfis.

        Fluxo: Usuário acessa o dashboard, e os gráficos e KPIs são exibidos.

    CU015: Gerar Previsão de Consumo

        Ator: Usuário autenticado.

        Objetivo: Obter estimativas de consumo futuro para seus dispositivos/perfis.

        Fluxo: Sistema (ou usuário, se houver interface) executa o modelo de ML, e a previsão é exibida.

    CU016: Comparar Previsão com Consumo Real

        Ator: Usuário autenticado.

        Objetivo: Avaliar a precisão dos modelos de previsão.

        Fluxo: Sistema compara dados reais com previsões e exibe métricas de erro.

    CU017: Identificar Maiores Consumidores

        Ator: Usuário autenticado.

        Objetivo: Descobrir quais dispositivos ou categorias de consumo são mais impactantes.

        Fluxo: Sistema analisa dados de consumo e destaca os maiores consumidores.

    CU018: Receber Sugestões de Otimização

        Ator: Usuário autenticado.

        Objetivo: Obter recomendações para reduzir o consumo de energia.

        Fluxo: Sistema (ou usuário) acessa a seção de sugestões, e dicas personalizadas são exibidas.

    CU019: Monitorar KPIs de Energia

        Ator: Usuário autenticado.

        Objetivo: Acompanhar o desempenho em relação a indicadores chave (ex: consumo total, eficiência).

        Fluxo: Usuário acessa a seção de KPIs, e os valores e status são exibidos.

2.4. Casos de Uso de Faturamento e Tarifas

    CU020: Registrar Fatura de Energia

        Ator: Usuário autenticado.

        Objetivo: Inserir dados de uma conta de energia para análise detalhada.

        Fluxo: Usuário acessa a seção de faturas, preenche todos os campos do talão (consumo, custo, impostos, leituras, etc.), envia.

    CU021: Visualizar Histórico de Faturas

        Ator: Usuário autenticado.

        Objetivo: Acessar registros de faturas anteriores para acompanhamento.

        Fluxo: Usuário acessa a seção de faturas, e a lista de registros é exibida.

    CU022: Analisar Impacto da Tarifa e Bandeira

        Ator: Usuário autenticado.

        Objetivo: Compreender como diferentes tarifas e bandeiras afetam o custo final.

        Fluxo: Sistema calcula e exibe a composição do custo da fatura, destacando o impacto da tarifa e bandeira.

    CU023: Gerenciar Tarifas de Energia (Admin)

        Ator: Administrador do Sistema.

        Objetivo: Cadastrar, editar e ativar/desativar tarifas de energia base.

        Fluxo: Admin acessa o painel de administração, gerencia as tarifas.

    CU024: Gerenciar Bandeiras Tarifárias (Admin)

        Ator: Administrador do Sistema.

        Objetivo: Cadastrar e atualizar os valores adicionais das bandeiras tarifárias.

        Fluxo: Admin acessa o painel de administração, gerencia as bandeiras.

2.5. Casos de Uso de Metas e Alertas

    CU025: Definir Meta de Consumo

        Ator: Usuário autenticado.

        Objetivo: Estabelecer um objetivo para a redução de consumo ou custo.

        Fluxo: Usuário acessa a seção de metas, define tipo de meta, valor alvo, período, salva.

    CU026: Monitorar Progresso da Meta

        Ator: Usuário autenticado.

        Objetivo: Acompanhar se está no caminho certo para atingir uma meta.

        Fluxo: Sistema compara consumo real com a meta e exibe o progresso.

    CU027: Receber Notificação de Alerta

        Ator: Usuário autenticado.

        Objetivo: Ser avisado sobre eventos importantes (ex: consumo excessivo, meta excedida).

        Fluxo: Sistema detecta condição, gera alerta e notifica o usuário (via interface ou email, conforme preferência).

    CU028: Visualizar Histórico de Alertas

        Ator: Usuário autenticado.

        Objetivo: Revisar alertas passados e seu status.

        Fluxo: Usuário acessa a seção de alertas, e a lista é exibida.

2.6. Casos de Uso de Manutenção do Sistema (Admin)

    CU029: Gerenciar Catálogo de Dispositivos (Admin)

        Ator: Administrador do Sistema.

        Objetivo: Adicionar, editar ou remover dispositivos do catálogo global.

        Fluxo: Admin acessa o painel de administração, gerencia o DeviceCatalog.

    CU030: Gerenciar Modelos de Previsão (Admin)

        Ator: Administrador do Sistema.

        Objetivo: Cadastrar e versionar modelos de Machine Learning.

        Fluxo: Admin acessa o painel de administração, gerencia PredictionModels.

    CU031: Gerenciar Sugestões de Otimização (Admin)

        Ator: Administrador do Sistema.

        Objetivo: Cadastrar, editar e categorizar dicas de economia.

        Fluxo: Admin acessa o painel de administração, gerencia OptimizationSuggestion.

    CU032: Monitorar Acurácia de Modelos (Admin)

        Ator: Administrador do Sistema.

        Objetivo: Avaliar o desempenho dos modelos de ML ao longo do tempo.

        Fluxo: Admin acessa a seção de ModelAccuracyScores, visualiza métricas.

Esta estrutura detalhada serve como um guia para o desenvolvimento e a compreensão do funcionamento do EcoTrack.