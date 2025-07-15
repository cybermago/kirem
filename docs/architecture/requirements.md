Requisitos Funcionais

O EcoTrack deve permitir ao usuário:

    Gerenciamento de Perfis de Energia:

        Criar, visualizar, editar e excluir perfis de energia.

        Associar informações gerais do talão de energia (subgrupo, grupo de tensão, tipo de fornecimento, classificação tarifária, tensão nominal, classificação, subclasse, tarifa padrão) a um perfil.

        Associar informações de localização (endereço, cidade, estado, CEP, país, latitude, longitude) a um perfil.

    Gerenciamento de Dispositivos:

        Associar dispositivos do catálogo a um perfil de energia.

        Definir quantidade de dispositivos e horas de uso diário.

        Personalizar o nome do dispositivo associado.

        Adicionar e excluir dispositivos associados a perfis.

    Cálculos de Consumo e Impacto:

        Calcular o consumo diário, mensal e anual em kWh para dispositivos e perfis.

        Converter o consumo de energia em estimativa de emissão de CO₂e.

        Calcular o custo total de energia com base nas tarifas aplicadas.

    Análise e Visualização de Dados:

        Exibir totais de consumo, custo e emissões no dashboard.

        Gerar gráficos interativos (linhas, barras, medidores) para visualização de consumo e tendências (usando Chart.js).

        Apresentar um carrossel interativo na página pública (usando Swiper.js).

        Exibir scores de eficiência energética.

        Gerar relatórios básicos.

    Previsão de Consumo (Machine Learning):

        Utilizar modelos de regressão linear para prever o consumo futuro com base em variáveis de uso.

    Sugestões e Otimização:

        Oferecer sugestões de economia baseadas em benchmarks simulados.

        Identificar os maiores consumidores de energia.

    Gerenciamento de Faturas:

        Registrar e analisar dados detalhados de faturas de energia (períodos, leituras, custos, impostos, bandeiras tarifárias).

    Gerenciamento de KPIs e Metas:

        Definir e monitorar Key Performance Indicators (KPIs) associados a perfis de energia.

        Definir metas de consumo de energia (redução percentual, meta absoluta, meta de custo).

    Alertas:

        Gerar alertas com base em condições predefinidas (ex: consumo elevado, meta excedida).

    Padrões de Uso de Dispositivos:

        Definir padrões de uso mais detalhados para dispositivos por dia da semana e horários.

    Comparação Histórica de Previsão:

        Comparar o consumo real observado com as previsões para avaliar a precisão do modelo.

    Autenticação e Autorização:

        Permitir o registro e login de usuários.

        Associar perfis de energia a usuários específicos.

        Redirecionar usuários autenticados da página pública para o dashboard.

Requisitos Não Funcionais

    Interface Leve e Responsiva: A aplicação deve ser otimizada para funcionar bem em diferentes dispositivos e tamanhos de tela.

    Código Modular e Reutilizável: A estrutura do código deve facilitar a manutenção, expansão e reutilização de componentes.

    Facilidade de Implantação: O protótipo deve ser fácil de implantar em ambientes locais (universidades, escolas, laboratórios).

    Persistência de Dados: Todos os dados devem ser armazenados de forma segura e persistente (PostgreSQL).

    Consistência Visual: A interface deve seguir um padrão de design coeso (Material Dashboard Theme).

    Clareza e Foco: O design deve priorizar a clareza da informação e a usabilidade, evitando elementos visuais excessivos.

    Acurácia das Previsões: Os modelos de Machine Learning devem buscar a maior precisão possível nas estimativas de consumo.