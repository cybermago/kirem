|-------------|------------------|
|+ title:     |KIREM             |
|+ createdAt: |16/06/2025        |
|+ author:    |Jonata Mendes     |
|+ status:    |development       |
|-------------|------------------|

# Projeto KIREM
## Contruindo um Futuro Sustentavel
    
**KIREM: Kernel de Inferência e Regulação Multinodal**

O KIREM é um sistema computacional que utiliza dados históricos através de vários nós, como dispositivos e dados de consumo energético (e com roadmap para sensores), para regulação, otimização, performance e monitoramento através de algoritmos de inferência e previsão.

# Indice:

# Introduçao e 🎯 Objetivo:

O "Projeto KIREM: Simulador de Consumo Doméstico de Energia" é um sistema interativo desenvolvido em Python para analisar o consumo de energia elétrica em residências brasileiras. Ele permite aos usuários compreender seus padrões de consumo, estimar gastos e emissões, e identificar oportunidades de economia energética. A aplicação se destaca por sua capacidade de processar dados inseridos manualmente e aplicar técnicas de Machine Learning (especificamente regressão linear simples) para oferecer previsões de consumo futuro e insights estratégicos. Seus objetivos incluem simular padrões de consumo, gerar estimativas de gastos, otimizar o consumo, prever tendências e atuar como uma plataforma educacional e analítica.

O **KIREM** é uma simulação interativa do consumo de energia elétrica por eletrodomésticos e eletrônicos em domicílios brasileiros. Ele foi concebido para:

- **Simular padrões de consumo doméstico**
- **Gerar estimativas de gasto energético**
- **Oferecer insights estratégicos para economia**
- **Aplicar técnicas básicas de Machine Learning para previsão de consumo**

A plataforma visa fornecer **ferramentas educacionais e analíticas**, permitindo que o próprio usuário insira os dados manualmente de maneira intuitiva.

---

# Escopo:

## ⚙️ Tecnologias Utilizadas:

- **Frontend**: [HTML, CSS, Bootstrap5 Material Design]
- **Backend (Web Framework)**: Django
- **Análise e Modelagem**: Python (Pandas, Scikit-Learn, Numpy)
- **Visualização**: Plotly (gráficos interativos) + ChartJS
- **Persistência de Dados**: PostgreSQL (Originalmente planejado como arquivos `.csv` locais, mas implementado com PostgreSQL para persistência e escalabilidade).
---

---

# Necessidades Atendidas:
O KIREM atende à necessidade de **conscientização** sobre o consumo de energia, **empoderando** o usuário com dados para tomar decisões. Ele supre a carência de ferramentas acessíveis para **monitorar e otimizar** o uso de eletrodomésticos, visando economia e sustentabilidade.

---

# Problemas Solucionados:
O projeto soluciona a **falta de visibilidade** sobre os gastos energéticos domésticos, a **dificuldade em identificar** os maiores consumidores de energia e a **incapacidade de prever** os impactos financeiros e ambientais do consumo. Ele mitiga o **desperdício de energia** e a **geração excessiva de CO₂e**.

---

# Casos de Uso:
* **Usuários Domésticos:** Para controlar gastos e planejar a redução do consumo.
* **Instituições de Ensino:** Como ferramenta educacional para demonstrar o impacto do consumo de energia.
* **Consultores de Eficiência Energética:** Para simular cenários e recomendar otimizações aos clientes.
* **Pesquisadores:** Para analisar padrões de consumo e desenvolver novas estratégias de otimização.

---

# Impacto na Natureza:
O KIREM contribui diretamente para a **redução da pegada de carbono** ao incentivar a diminuição do consumo de energia. Ao otimizar o uso de eletrodomésticos, ele ajuda a **preservar recursos naturais** e a **minimizar as emissões de gases de efeito estufa**, promovendo um futuro mais sustentável.

---

# Desafios e Soluções:
* **Desafio:** Coleta precisa de dados de consumo de usuários.
    * **Solução:** Interface intuitiva para inserção manual e catálogo de dispositivos com dados predefinidos.
* **Desafio:** Previsões de Machine Learning com dados limitados.
    * **Solução:** Início com modelos mais simples (regressão linear) e roadmap para modelos mais robustos e coleta de dados ao longo do tempo.
* **Desafio:** Tornar a complexidade dos cálculos compreensível.
    * **Solução:** Visualizações interativas (Plotly) e relatórios claros com sugestões práticas.

---

### 🖥️ Entrada de Dados:

O usuário insere:

- Tipo de equipamento (ex: ar-condicionado, geladeira, TV)
- Potência nominal (em watts)
- Horas de uso diário
- Frequência de uso semanal
- Número de equipamentos
- Detalhes de consumo para dispositivos (consumo diário, quantidade, horas de uso)
- Informações de usuário (nome, email)
- Informações de perfil de energia (nome, descrição, usuário associado)
- Dados de faturas de energia (registros de leitura, custos, impostos, bandeiras tarifárias)

---


### 🔄 Processamento:

1.  **Cálculo do Consumo Diário e Mensal (kWh)**
2.  **Conversão em Emissão Estimada de CO₂e**
3.  **Gerenciamento de Usuários e Perfis de Energia**: Adição, exclusão e listagem de usuários e seus respectivos perfis.
4.  **Gerenciamento de Dispositivos**: Adição e exclusão de dispositivos associados a perfis de energia, tanto do catálogo predefinido quanto de forma manual.
5.  **Cálculo de Benchmark**: Com base nos dados de consumo inseridos, calcula o consumo total, identifica o maior consumidor e oferece sugestões de otimização.
6.  **Monitoramento de Eficiência**: Calcula e exibe scores de eficiência em tempo real para dispositivos selecionados.
7.  **Análise de Tendências**: Mostra a evolução do consumo diário de um dispositivo ao longo do tempo.
8.  **Persistência de Dados**: Todas as informações de usuários, perfis, dispositivos e detalhes de consumo são armazenadas em um banco de dados PostgreSQL.
9. **Integração de Dados de Fatura**: Processamento de registros de faturas para análise de custos e tarifas.
10. **Lógica de Redirecionamento (Middleware)**: Implementação de middleware para gerenciar o fluxo de navegação, como redirecionar usuários autenticados da página pública para o dashboard.

---

### 📊 Saída de Dados

- Geração automática de relatórios básicos
- Sugestões de economia baseadas em benchmarks simulados
- Exportação de simulações para `.csv`
- Gráficos interativos (medidores, séries temporais, linhas) via Plotly.
- Exibição de scores de eficiência energética em caixas de valor.
- Tabelas detalhadas de consumo de dispositivos.

---

# Levantamento de Dados e Informação

O processo de levantamento de dados e informações no KIREM é fundamental para a precisão das simulações, análises e previsões. Ele envolve a coleta de dados diretamente do usuário e a utilização de informações de referência para enriquecer os insights.

## Fontes de Dados

* **Entrada Manual do Usuário:** A principal fonte de dados, onde o usuário insere informações detalhadas sobre:
    * **Perfis de Energia:** Nome, descrição, e dados específicos do talão de energia (subgrupo, grupo de tensão, tipo de fornecimento, classificação tarifária, tensão nominal, classificação, subclasse, tarifa padrão).
    * **Localização:** Endereço, cidade, estado, CEP, país, latitude e longitude (para futuras análises geoespaciais ou de clima).
    * **Dispositivos:** Tipo de equipamento, potência nominal, horas de uso diário, frequência de uso semanal, quantidade e nome personalizado.
    * **Leituras de Energia:** Consumo em kWh em datas e horários específicos (horário, diário, mensal).
    * **Faturas de Energia:** Dados completos do talão de energia, incluindo datas de período, consumo total faturado, custo total, tarifas aplicadas, bandeiras tarifárias, leituras de medidor, impostos (ICMS, PIS, COFINS) e outros encargos (CIP, multas, juros).
    * **Metas de Consumo:** Definição de metas de redução de kWh ou custo.
    * **Padrões de Uso:** Detalhes sobre o uso de dispositivos por dia da semana e horários.

* **Catálogo de Dispositivos (`DeviceCatalog`):** Um banco de dados interno que armazena informações de referência sobre dispositivos comuns, incluindo consumo médio (`avg_kwh`) e selo Procel. Isso agiliza a entrada de dados para o usuário e garante a consistência.

* **Modelos de Previsão (`PredictionModels`):** Informações sobre os algoritmos de Machine Learning utilizados, incluindo nome e versão, para rastreabilidade e avaliação de desempenho.

* **Tarifas de Energia (`EnergyTariff` e `TariffFlagAdditive`):** Dados sobre as tarifas base por kWh e os adicionais das bandeiras tarifárias, essenciais para o cálculo preciso dos custos.

* **Sugestões de Otimização (`OptimizationSuggestion`):** Um catálogo de dicas pré-definidas com categorias, níveis de impacto e economia estimada.

## Métodos de Coleta e Validação

* **Formulários Web:** A interface de usuário (frontend Django) oferece formulários intuitivos para a entrada manual de todos os dados mencionados.
* **Validação de Formulário:** O Django Forms é utilizado para validar a entrada de dados, garantindo que as informações estejam no formato correto e dentro dos limites esperados (ex: `min`, `max` para números, tipos de dados para datas).
* **Associação de Dados:** Chaves estrangeiras nos modelos Django garantem a correta associação entre usuários, perfis, dispositivos e outros dados relacionados.
* **Cálculos Automáticos:** O sistema realiza cálculos automáticos (ex: consumo diário/mensal, emissão de CO₂e) com base nos dados inseridos, reduzindo a carga do usuário.

## Informações Geradas e Utilizadas

As informações coletadas e processadas são utilizadas para gerar:

* **Visão Geral do Consumo:** Totais de kWh, custo e CO₂e.
* **Análises Detalhadas:** Consumo por dispositivo, por período, por tipo de tarifa.
* **Previsões de Consumo:** Estimativas futuras baseadas em Machine Learning.
* **Recomendações Personalizadas:** Sugestões de otimização adaptadas ao perfil e consumo do usuário.
* **Relatórios e Gráficos:** Visualizações interativas para facilitar a compreensão dos dados.
* **Alertas:** Notificações sobre consumo elevado ou metas excedidas.
* **Comparativos:** Desempenho do modelo de previsão vs. consumo real.

Este processo de levantamento e gestão de dados é a espinha dorsal do KIREM, permitindo que o sistema forneça insights acionáveis e suporte a tomada de decisões para uma gestão de energia mais eficiente e sustentável.

---

## 🤖 Machine Learning

**Pipeline de Previsão de Consumo:**

* **Entrada**:
    * Leituras de Energia (`EnergyReading`)
    * Registros de Faturas (`BillingRecord`)
    * Consumo Agregado de Dispositivos (`ProfileDevices`)
    * Previsões Anteriores (`ConsumptionPredictions`)
    * Registros de Qualidade de Energia (`EnergyQualityRecord`)
    * Metas de Consumo (`ConsumptionGoal`)
    * Histórico de Alertas de Consumo (`Alert`)
    * (Planejado) Dados Climáticos
    * (Planejado) Geração Solar
* **Modelos Suportados**:
    * Regressão Linear Simples (`LinearRegression`)
    * Prophet (para séries temporais com sazonalidade e feriados)
    * (Em Andamento) Florestas Aleatórias (Regressão)
    * (Em Andamento) Redes Neurais (Keras/TensorFlow) (Regressão)
    * (Em Andamento) Regressão Logística (Classificação)
    * (Em Andamento) Árvore de Decisão (Classificação)
    * (Em Andamento) K-Means (Clusterização)
    * (Em Andamento) Misturas Gaussianas (Clusterização)
    * (Em Andamento) Apriori (Regras de Associação)
    * (Em Andamento) Inferência Bayesiana
    * (Em Andamento) K-Vizinhos Mais Próximos (K-NN)
    * Modelos via Upload de arquivo externo (`.pkl`)
* **Saída**:
    * Estimativas de consumo futuro (kWh)
    * Previsões diárias de kWh
    * Pontuação de confiança da previsão
    * Gráficos de previsão (ex: histórico vs. previsão)
    * Métricas de acurácia do modelo (MAPE, RMSE)
    * Comparação histórica entre consumo previsto e real
    * Análise de outliers no consumo
    * Sugestões de otimização de consumo com base na análise

# Recursos e Funcionalidades:
**Cálculo de Consumo:** Diário, mensal e projeção de gastos.
**Estimativa de CO₂e:** Conversão do consumo em impacto ambiental.
**Gestão de Perfis e Dispositivos:** Cadastro e acompanhamento de múltiplos usuários e aparelhos.
**Modelagem Preditiva:** Previsões de consumo futuro.
**Sugestões de Otimização:** Recomendações baseadas em benchmark.
**Visualizações Interativas:** Gráficos e medidores em tempo real.
**Persistência de Dados:** Armazenamento seguro em PostgreSQL.
**Gerenciamento de Faturas**: Registro e análise de contas de energia.

---

# Componentes:
* **Interface (Frontend)**:Django Templates, HTML, CSS (Material Dashboard Theme), JavaScript.
* **Backend:** Lógica de negócios em Python (Pandas, Numpy).
* **Modelagem Preditiva:** Scikit-Learn para o pipeline de Machine Learning.
* **Visualização:** Plotly para gráficos dinâmicos.
* **Banco de Dados:** PostgreSQL para armazenamento de dados.

---

### Cálculos e Técnicas Atuais

* **Cálculo de Consumo de Energia:**
    * $Consumo (kWh) = (\text{Potência do Aparelho (Watts)} \times \text{Horas de Uso Diário} \times \text{Dias de Uso por Período}) / 1000$
    * Essencial para converter a potência em consumo real e estimar gastos.
* **Estimativa de CO₂e:**
    * $Emissão de CO₂e (kg) = Consumo (kWh) \times \text{Fator de Emissão de Carbono por kWh (kg CO₂e/kWh)}$
    * Este fator varia conforme a matriz energética (no Brasil, predominantemente hídrica, mas com termelétricas em períodos de escassez).
* **Cálculo de Benchmark:**
    * Uso de **estatísticas descritivas** (soma, média, máximo) para identificar o maior consumidor e o consumo total. Compara o consumo do usuário com padrões médios ou ideais.

---

### Algoritmos de Aprendizado Atuais

* **Regressão Linear Simples ($LinearRegression()$ do Scikit-Learn):**
    * Permite prever o consumo futuro com base em uma ou mais variáveis (ex: tempo de uso, quantidade de aparelhos).
    * Modelo: $Y = \beta_0 + \beta_1X + \epsilon$ onde $Y$ é o consumo, $X$ é a variável preditora, $\beta_0$ é o intercepto, $\beta_1$ é o coeficiente e $\epsilon$ é o erro.
    * Ideal para começar pela sua simplicidade e interpretabilidade.

---

### Cálculos e Técnicas Futuras

* **Análise de Séries Temporais:**
    * Técnicas como **ARIMA (AutoRegressive Integrated Moving Average)** ou **Prophet (do Facebook)**:
        * Permitem prever o consumo com base em dados históricos, capturando sazonalidades (ex: maior consumo no verão devido ao ar-condicionado) e tendências.
        * Útil para predições mais precisas e identificação de padrões complexos ao longo do tempo.
* **Clusterização (Ex: K-Means):**
    * Para **segmentar usuários** ou perfis de consumo em grupos com características semelhantes.
    * Isso pode ajudar a oferecer sugestões mais personalizadas com base no perfil do usuário.
* **Análise de Variância (ANOVA):**
    * Para comparar as médias de consumo entre diferentes grupos (ex: casas com diferentes tipos de isolamento, ou uso de aparelhos específicos).
* **Testes de Hipóteses (Ex: Teste T):**
    * Para verificar se a diferença de consumo entre dois cenários (ex: antes e depois de uma mudança de hábito) é estatisticamente significativa.

---

### Algoritmos de Aprendizado Futuros

* **Regressão Linear Múltipla:**
    * Permite incluir **múltiplas variáveis preditoras** no seu modelo (ex: horas de uso, número de aparelhos, temperatura ambiente, tarifa de energia) para predições mais robustas.
* **Árvores de Decisão e Random Forests:**
    * Modelos mais complexos que podem capturar **relações não lineares** nos dados e são bons para identificar variáveis importantes no consumo.
    * Úteis para determinar as condições que levam a um alto consumo ou à economia.
* **Gradient Boosting (Ex: XGBoost, LightGBM):**
    * Algoritmos de aprendizado ensemble que combinam múltiplos modelos fracos para criar um preditor forte.
    * Geralmente, oferecem **alta precisão** em problemas de regressão.
* **Redes Neurais (Básicas):**
    * Para cenários mais complexos, podem aprender padrões intrincados nos dados de consumo, especialmente se você tiver um volume maior de dados e recursos computacionais.


## 🚧 Roadmap de Desenvolvimento

| Etapa | Status |
|---|---|
| Estruturação da Interface | ✅ Concluído |
| Gerenciamento de Perfis de Energia (CRUD) | ✅ Concluído |
| Gerenciamento de Dispositivos (CRUD) | ✅ Concluído |
| Associação de Dispositivos a Perfis (CRUD) | ✅ Concluído |
| Cálculo Automático de Consumo em `ProfileDevices` | ✅ Concluído |
| Gestão de Tarifas de Energia (CRUD) | ✅ Concluído |
| Gestão de Bandeiras Tarifárias (CRUD) | ✅ Concluído |
| Registro de Faturas de Energia (CRUD) | ✅ Concluído |
| Registro de Leituras de Energia (CRUD) | ✅ Concluído |
| Gestão de KPIs (CRUD) | ✅ Concluído |
| Gestão de Alertas (CRUD) | ✅ Concluído |
| Gestão de Metas de Consumo (CRUD) | ✅ Concluído |
| Gestão de Sugestões de Otimização (CRUD) | ✅ Concluído |
| Gestão de Padrões de Uso de Dispositivos (CRUD) | ✅ Concluído |
| Gerenciamento de Modelos de Previsão (CRUD) | ✅ Concluído |
| Comparação Histórica de Previsões (CRUD) | ✅ Concluído |
| Registro de Qualidade de Energia (CRUD) | ✅ Concluído |
| Gerenciamento de Preferências do Usuário (CRUD) | ✅ Concluído |
| Dashboard Principal | ✅ Concluído |
| Dashboard para Smart TVs/IoT (`SmartDashboardView`) | ✅ Concluído |
| Relatório de Eficiência de Marcas | ✅ Concluído |
| Análise de Outliers no Consumo | ✅ Concluído |
| Benchmark de Consumo de Dispositivos | ✅ Concluído |
| Monitoramento de Performance e Consumo | ✅ Concluído |
| Tendências de Consumo | ✅ Concluído |
| Previsão de Consumo (`ForecastView`) | ✅ Concluído |
| Expansão da Modelagem Preditiva | 🔄 Em Andamento |
| Integração de Mais Fontes de Dados para Previsão | 🔄 Em Andamento |
| Sistema de Alertas e Notificações Automatizado | 🔜 Planejado |
| Recomendações de Otimização Dinâmicas | 🔜 Planejado |
| Relatórios Personalizáveis | 🔜 Planejado |
| Integração com APIs Externas | 🔜 Planejado |
| Melhorias na UX/UI | 🔜 Planejado |
| Otimização de Performance | 🔜 Planejado |
| Recursos de Geração Distribuída | 🔜 Planejado |

---

# ⏰ Linha do Tempo de Implementação do Sistema

Esta seção apresenta o progresso das funcionalidades dentro do sistema:

## ✅ Implementado

- **Configuração do Ambiente:** Repositório, ambiente virtual, requirements.txt.
- **Conexão com PostgreSQL:** Configuração básica do banco de dados.
- **Gerenciamento de Perfis de Energia (CRUD):** Criação, listagem, visualização, atualização e exclusão de perfis de energia por usuário.
- **Gerenciamento de Dispositivos (CRUD):** Criação, listagem, visualização, atualização e exclusão de dispositivos no catálogo.
- **Associação de Dispositivos a Perfis (CRUD):** Adicionar, visualizar, atualizar e remover dispositivos específicos de um perfil.
- **Cálculo Automático de Consumo em ProfileDevices:** Consumo diário, mensal e anual calculados automaticamente com base nas horas de uso e nos dias da semana.
- **Gestão de Tarifas de Energia (CRUD):** Adicionar, visualizar, atualizar e excluir diferentes tipos de tarifas de energia, incluindo precificação por faixa.
- **Gestão de Bandeiras Tarifárias (CRUD):** Adicionar, visualizar, atualizar e excluir os custos adicionais de bandeiras tarifárias.
- **Registro de Faturas de Energia (CRUD):** Adicionar, visualizar, atualizar e excluir registros detalhados de faturas, com cálculos automáticos de preço unitário.
- **Registro de Leituras de Energia (CRUD):** Adicionar, visualizar, atualizar e excluir leituras de consumo de energia com granularidade variada (horária, diária, mensal).
- **Gestão de KPIs (CRUD):** Adicionar, visualizar, atualizar e excluir Indicadores-Chave de Desempenho associados a perfis ou globais.
- **Gestão de Alertas (CRUD):** Criação, listagem, visualização, atualização e exclusão de alertas do sistema.
- **Gestão de Metas de Consumo (CRUD):** Definir, visualizar, atualizar e excluir metas de consumo de energia.
- **Gestão de Sugestões de Otimização (CRUD):** Adicionar, visualizar, atualizar e excluir sugestões para economia de energia.
- **Gestão de Padrões de Uso de Dispositivos (CRUD):** Definir e gerenciar padrões de uso horário para dispositivos.
- **Gerenciamento de Modelos de Previsão (CRUD):** Cadastrar e configurar diferentes tipos de modelos de previsão com seus hiperparâmetros.
- **Comparação Histórica de Previsões (CRUD):** Registrar e comparar previsões com consumo real, calculando desvios e erros.
- **Registro de Qualidade de Energia (CRUD):** Registrar e gerenciar indicadores de qualidade do fornecimento de energia (interrupções, flutuações, THD).
- **Gerenciamento de Preferências do Usuário (CRUD):** Definir e atualizar configurações como tema, frequência de notificações e formato de relatório.
- **Dashboard Principal:** Visão geral com métricas de consumo, custo, emissões de CO2, alertas e sugestões.
- **Dashboard para Smart TVs/IoT (SmartDashboardView):** Dashboard imersivo e atualizável via API para um perfil específico, mostrando consumo atual, alertas e previsão de 24h.
- **Relatório de Eficiência de Marcas:** Análise da eficiência de marcas de dispositivos com base no Selo Procel e dados de uso real, incluindo visualização com Plotly.
- **Análise de Outliers no Consumo:** Detecção e visualização de anomalias no consumo diário de energia para um perfil, com opções de período.
- **Benchmark de Consumo de Dispositivos:** Identificação dos maiores consumidores e sugestões de otimização para dispositivos de um perfil, com gráficos Plotly.
- **Monitoramento de Performance e Consumo:** Análise de acurácia de modelos de previsão e dados históricos de consumo (diário, semanal, mensal, anual).
- **Tendências de Consumo:** Exibição de consumo mensal histórico e comparação anual, além de histórico de consumo diário.
- **Previsão de Consumo (ForecastView):** Gera e exibe previsões de consumo futuras usando modelos configurados, como Regressão Linear e Prophet, e salva essas previsões.

## ⏳ Em Andamento

- **Expansão da Modelagem Preditiva:** Implementação e integração de outros algoritmos de ML como Florestas Aleatórias, K-Means e Regressão Logística para casos de uso específicos.
- **Integração de Mais Fontes de Dados para Previsão:** Adição de dados climáticos e de geração solar como fontes para os modelos de previsão.

## 🚀 Próximos Passos (Planejado)

- **Sistema de Alertas e Notificações Automatizado:** Desenvolvimento de lógica para disparar alertas e enviar notificações (e-mail/push) com base em limiares e eventos.
- **Recomendações de Otimização Dinâmicas:** Gerar sugestões de otimização de forma inteligente, utilizando dados de consumo e padrões de uso.
- **Relatórios Personalizáveis:** Ferramentas para que os usuários criem e exportem relatórios personalizados de consumo e eficiência.
- **Integração com APIs Externas:** Conectar-se a APIs de dados meteorológicos, informações de bandeiras tarifárias em tempo real, etc.
- **Melhorias na UX/UI:** Aprimoramentos na interface do usuário para dashboards mais interativos e intuitivos.
- **Otimização de Performance:** Melhorias contínuas nas consultas ao banco de dados e no processamento de dados para garantir escalabilidade.
- **Recursos de Geração Distribuída:** Incorporar dados de geração solar para cálculo de economia e otimização.


# 🤝 Contribuição

Este sistema está em fase de desenvolvimento. Contribuições são bem-vindas para:

* Reportar issues e bugs.
* Sugerir melhorias nas funcionalidades existentes.
* Propor novas fontes de dados ou análises.

Por favor, abra uma issue ou envie um Pull Request.

# 📄 Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

# 📞 Contato

Para dúvidas ou mais informações, entre em contato:

* **[Jonata Mendes]**
* **[cybermago@outlook.com]**