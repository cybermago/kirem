from decimal import Decimal
import json
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta, timezone
import pytz
from django.db.models.functions import TruncDate
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from io import StringIO
from django.template.loader import render_to_string
from weasyprint import HTML
from twilio.rest import Client
from webpush import send_user_notification
from pywebpush import WebPushException  

from .models import (
    DeviceCatalog, EnergyQualityRecord, EnergyReading, HistoricalPredictionComparison, ProfileDevices, KPI, BillingRecord, ConsumptionGoal,
    OptimizationSuggestion, Alert, ConsumptionPredictions, ModelAccuracyScores,
    EnergyTariff, TariffFlagAdditive, DeviceUsagePattern
)
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Avg
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

# Para Florestas Aleatórias
from sklearn.ensemble import RandomForestRegressor

# Para Clusterização
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture

# Para K-NN
from sklearn.neighbors import KNeighborsClassifier



try:
    from prophet import Prophet
except ImportError:
    Prophet = None 

def get_brazil_timezone():
    """Retorna o objeto de fuso horário do Brasil (São Paulo)."""
    return pytz.timezone('America/Sao_Paulo')



def get_quality_of_service_data(profile, start_date=None, end_date=None):
    """
    Calcula e retorna métricas, visualizações e registros brutos de qualidade de serviço
    para um perfil específico, com filtragem opcional por período.
    (Refatorado para usar os campos corretos de EnergyQualityRecord).
    """
    quality_records = EnergyQualityRecord.objects.filter(profile=profile)

    if start_date:
        # Usa __date para filtrar um DateTimeField por data
        quality_records = quality_records.filter(record_datetime__date__gte=start_date)
    if end_date:
        quality_records = quality_records.filter(record_datetime__date__lte=end_date)

    if not quality_records.exists():
        return {
            'metrics': {},
            'charts': {
                'interruptions_chart_json': None,
                'duration_chart_json': None,
                'tariff_flag_impact_chart_json': None,
            },
            'records_list': []
        }, "Nenhum registro de qualidade de serviço disponível para este perfil no período selecionado."

    # Correção dos nomes dos campos na agregação
    total_interruptions = quality_records.aggregate(Sum('num_interruptions'))['num_interruptions__sum'] or 0
    total_duration_hours = quality_records.aggregate(Sum('total_duration_interruptions_hours'))['total_duration_interruptions_hours__sum'] or Decimal('0.0')
    num_records = quality_records.count()

    # Correção dos nomes dos campos para o DataFrame
    df = pd.DataFrame(list(quality_records.values('record_datetime', 'num_interruptions', 'total_duration_interruptions_hours', 'tariff_flag_applied')))
    df['record_datetime'] = pd.to_datetime(df['record_datetime'])
    df['year_month'] = df['record_datetime'].dt.to_period('M')

    monthly_summary = df.groupby('year_month').agg(
        total_interruptions_month=('num_interruptions', 'sum'),
        total_duration_month=('total_duration_interruptions_hours', 'sum')
    ).reset_index()

    avg_interruptions_per_month = monthly_summary['total_interruptions_month'].mean() if not monthly_summary.empty else 0
    avg_duration_per_month = monthly_summary['total_duration_month'].mean() if not monthly_summary.empty else 0
    
    if start_date and end_date:
        total_period_days = (end_date - start_date).days + 1
        total_period_hours = total_period_days * 24
    else:
        # Usa a data mínima e máxima dos registros se não houver um range definido
        if quality_records.exists():
            min_date = quality_records.earliest('record_datetime').record_datetime.date()
            max_date = quality_records.latest('record_datetime').record_datetime.date()
            total_period_days = (max_date - min_date).days + 1
            total_period_hours = total_period_days * 24
        else:
            total_period_hours = 0
    
    avg_downtime_percentage = (Decimal(total_duration_hours) / Decimal(total_period_hours) * 100) if total_period_hours else Decimal('0.0')

    interruptions_chart_fig = go.Figure(data=[
        go.Bar(x=df['year_month'].astype(str), y=df['num_interruptions'])
    ])
    interruptions_chart_fig.update_layout(title_text='Número de Interrupções por Mês', xaxis_title='Mês', yaxis_title='Número de Interrupções', template="plotly_white", margin=dict(l=0, r=0, t=40, b=0), height=300)
    interruptions_chart_json = interruptions_chart_fig.to_json()

    duration_chart_fig = go.Figure()
    duration_chart_fig.add_trace(go.Scatter(x=df['year_month'].astype(str), y=df['total_duration_interruptions_hours'], mode='lines+markers'))
    duration_chart_fig.update_layout(title_text='Duração Total das Interrupções por Mês (horas)', xaxis_title='Mês', yaxis_title='Duração (horas)', template="plotly_white", margin=dict(l=0, r=0, t=40, b=0), height=300)
    duration_chart_json = duration_chart_fig.to_json()

    # Correção do nome do campo no groupby
    tariff_flag_impact_data = df.groupby('tariff_flag_applied')['num_interruptions'].mean().reset_index()
    tariff_flag_impact_chart_json = None
    if not tariff_flag_impact_data.empty:
        tariff_flag_impact_chart_fig = go.Figure(data=[
            go.Bar(x=tariff_flag_impact_data['tariff_flag_applied'], y=tariff_flag_impact_data['num_interruptions'])
        ])
        tariff_flag_impact_chart_fig.update_layout(title_text='Média de Interrupções por Bandeira Tarifária', xaxis_title='Bandeira Tarifária', yaxis_title='Média de Interrupções', template="plotly_white", margin=dict(l=0, r=0, t=40, b=0), height=300)
        tariff_flag_impact_chart_json = tariff_flag_impact_chart_fig.to_json()

    combined_metrics = {
        'total_interruptions': total_interruptions,
        'total_duration_hours': round(total_duration_hours, 2),
        'avg_interruptions_per_month': f"{avg_interruptions_per_month:.2f} interrupções",
        'avg_duration_per_month': f"{avg_duration_per_month:.2f} horas",
        'avg_downtime_percentage': f"{avg_downtime_percentage:.4f}% do tempo",
        'num_records_data': num_records,
    }

    return {
        'metrics': combined_metrics,
        'charts': {
            'interruptions_chart_json': interruptions_chart_json,
            'duration_chart_json': duration_chart_json,
            'tariff_flag_impact_chart_json': tariff_flag_impact_chart_json,
        },
        'records_list': list(quality_records.values('record_datetime', 'num_interruptions', 'total_duration_interruptions_hours', 'tariff_flag_applied'))
    }, None

def get_model_accuracy_scatter_chart_data(model_accuracy_score_instance):
    """
    Gera dados para um gráfico de dispersão 'Previsto vs. Real'.
    (Refatorado para usar 'model' em vez de 'prediction_model').
    """

    prediction_model = model_accuracy_score_instance.model

    comparisons = HistoricalPredictionComparison.objects.filter(
        prediction__model=prediction_model
    ).select_related('prediction').order_by('comparison_date')

    if not comparisons.exists():
        return {'chart_json': None, 'message': "Nenhum dado de comparação histórica de previsão encontrado para este modelo."}

    data_list = [{'actual': float(comp.actual_kwh), 'predicted': float(comp.prediction.predicted_kwh), 'date': comp.comparison_date.strftime('%Y-%m-%d')} for comp in comparisons]
    df = pd.DataFrame(data_list)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['actual'], y=df['predicted'], mode='markers', marker=dict(size=8, opacity=0.7, color='rgba(63, 81, 181, 0.8)'), hovertemplate='<b>Real:</b> %{x:.2f} kWh<br><b>Previsto:</b> %{y:.2f} kWh<br><b>Data:</b> %{text}<extra></extra>', text=df['date']))
    
    max_val = max(df['actual'].max(), df['predicted'].max())
    min_val = min(df['actual'].min(), df['predicted'].min())
    fig.add_trace(go.Scatter(x=[min_val, max_val], y=[min_val, max_val], mode='lines', name='Previsão Perfeita', line=dict(color='red', dash='dash', width=1), hoverinfo='skip'))
    
    fig.update_layout(title_text=f'Previsões vs. Real para o Modelo "{prediction_model.name}"', xaxis_title='Consumo Real (kWh)', yaxis_title='Consumo Previsto (kWh)', template="plotly_white", margin=dict(l=50, r=50, t=60, b=50), height=500, showlegend=True)
    
    chart_json = json.dumps(fig.to_dict())
    return {'chart_json': chart_json, 'message': "Gráfico de dispersão de previsões vs. real gerado com sucesso."}



def get_latest_kwh_data(profile):
    """
    Retorna os dados de kWh mais recentes para um perfil.
    (Refatorado para usar 'reading_datetime' e 'total_kwh_consumption').
    """
    # Correção: Ordenar por 'reading_datetime'
    latest_reading = EnergyReading.objects.filter(profile=profile).order_by('-reading_datetime').first()
    latest_prediction = ConsumptionPredictions.objects.filter(profile=profile).order_by('-prediction_date').first()
    
    return {
        # Correção: O campo é 'total_kwh_consumption'
        'latest_actual_kwh': latest_reading.total_kwh_consumption if latest_reading else Decimal('0.00'),
        'latest_predicted_kwh': latest_prediction.predicted_kwh if latest_prediction else Decimal('0.00'),
        # Correção: O campo é 'reading_datetime'
        'latest_reading_date': latest_reading.reading_datetime if latest_reading else None,
        'latest_prediction_date': latest_prediction.prediction_date if latest_prediction else None,
    }

def analyze_interruptions_consumption_correlation(profile):
    """
    Analisa a correlação entre interrupções, consumo e custo.
    (Refatorado para usar os campos de data e bandeira corretos).
    """
    # Correção: Usar 'record_datetime' e 'invoice_date'
    quality_records = EnergyQualityRecord.objects.filter(profile=profile).order_by('record_datetime')
    billing_records = BillingRecord.objects.filter(profile=profile).order_by('invoice_date')

    if not quality_records.exists() or not billing_records.exists():
        return None, "Dados insuficientes para análise de correlação (qualidade de serviço ou faturas)."

    # Correção dos nomes dos campos para o DataFrame
    quality_df = pd.DataFrame(list(quality_records.values('record_datetime', 'num_interruptions', 'total_duration_interruptions_hours', 'tariff_flag_applied')))
    billing_df = pd.DataFrame(list(billing_records.values('invoice_date', 'kwh_total_billed', 'total_cost', 'applied_tariff_flag')))

    if quality_df.empty or billing_df.empty:
        return None, "Dados insuficientes para análise de correlação (qualidade de serviço ou faturas)."

    # Renomear colunas de data para um nome comum antes de extrair mês/ano
    quality_df.rename(columns={'record_datetime': 'date', 'tariff_flag_applied': 'tariff_flag'}, inplace=True)
    billing_df.rename(columns={'invoice_date': 'date', 'applied_tariff_flag': 'tariff_flag'}, inplace=True)

    quality_df['month_year'] = pd.to_datetime(quality_df['date']).dt.to_period('M')
    billing_df['month_year'] = pd.to_datetime(billing_df['date']).dt.to_period('M')

    merged_df = pd.merge(quality_df, billing_df, on='month_year', how='outer', suffixes=('_quality', '_billing'))
    merged_df = merged_df.sort_values('month_year')
    
    merged_df['num_interruptions'] = merged_df['num_interruptions'].fillna(0)
    merged_df['total_duration_interruptions_hours'] = merged_df['total_duration_interruptions_hours'].fillna(0.0)
    merged_df['kwh_total_billed'] = merged_df['kwh_total_billed'].fillna(0.0).astype(float)
    merged_df['total_cost'] = merged_df['total_cost'].fillna(0.0).astype(float)
    
    analysis_results = {}

    if not merged_df.empty and merged_df['kwh_total_billed'].notna().any():
        correlation_interruptions_consumption = merged_df[['num_interruptions', 'kwh_total_billed']].corr().iloc[0, 1]
        analysis_results['correlation_interruptions_consumption'] = f"{correlation_interruptions_consumption:.2f}"
        
        scatter_fig = go.Figure(data=[go.Scatter(x=merged_df['num_interruptions'], y=merged_df['kwh_total_billed'], mode='markers')])
        scatter_fig.update_layout(title_text='Interrupções vs. Consumo Total Faturado', xaxis_title='Número de Interrupções', yaxis_title='Consumo Total Faturado (kWh)', template="plotly_white", margin=dict(l=0, r=0, t=40, b=0), height=300)
        analysis_results['interruptions_consumption_scatter_chart_json'] = scatter_fig.to_json()
    else:
        analysis_results['correlation_interruptions_consumption'] = "N/A"
        analysis_results['interruptions_consumption_scatter_chart_json'] = None

    if not billing_df.empty:
        tariff_flag_summary = billing_df.groupby('tariff_flag').agg(
            avg_kwh=('kwh_total_billed', 'mean'),
            avg_cost=('total_cost', 'mean')
        ).reset_index()
        analysis_results['tariff_flag_summary'] = tariff_flag_summary.to_dict('records')

        consumption_by_flag_fig = go.Figure(data=[go.Bar(x=tariff_flag_summary['tariff_flag'], y=tariff_flag_summary['avg_kwh'])])
        consumption_by_flag_fig.update_layout(title_text='Consumo Médio por Bandeira Tarifária (kWh)', xaxis_title='Bandeira Tarifária', yaxis_title='Consumo Médio (kWh)', template="plotly_white", margin=dict(l=0, r=0, t=40, b=0), height=300)
        analysis_results['consumption_by_flag_chart_json'] = consumption_by_flag_fig.to_json()

        cost_by_flag_fig = go.Figure(data=[go.Bar(x=tariff_flag_summary['tariff_flag'], y=tariff_flag_summary['avg_cost'])])
        cost_by_flag_fig.update_layout(title_text='Custo Médio por Bandeira Tarifária (R$)', xaxis_title='Bandeira Tarifária', yaxis_title='Custo Médio (R$)', template="plotly_white", margin=dict(l=0, r=0, t=40, b=0), height=300)
        analysis_results['cost_by_flag_chart_json'] = cost_by_flag_fig.to_json()
    else:
        analysis_results['tariff_flag_summary'] = []
        analysis_results['consumption_by_flag_chart_json'] = None
        analysis_results['cost_by_flag_chart_json'] = None

    return analysis_results, None


def get_consumption_goals_overview(profile):
    """
    Verifica e calcula o status e o progresso de todas as metas de consumo ativas
    para um perfil específico.

    Args:
        profile: O objeto do modelo Profile para o qual as metas serão verificadas.

    Returns:
        Um dicionário contendo:
        - 'goal_overviews': Uma lista de dicionários, cada um com os detalhes e o progresso de uma meta.
        - 'message': Uma mensagem informativa (por exemplo, se não houver metas ativas).
    """
    brazil_tz = get_brazil_timezone()
    today = datetime.now(brazil_tz).date()
    current_month_start = today.replace(day=1)

    active_goals = ConsumptionGoal.objects.filter(
        profile=profile,
        start_date__lte=today,
        end_date__gte=today,
        is_active=True
    ).order_by('start_date') # Ordenar para melhor visualização

    goal_overviews = []
    message = "Processando metas de consumo."

    if not active_goals.exists():
        message = "Nenhuma meta de consumo ativa definida para este perfil no período atual."
        return {'goal_overviews': goal_overviews, 'message': message}

    for goal in active_goals:
        # Calcular consumo no período da meta (do início da meta até hoje)
        consumption_in_goal_period = EnergyReading.objects.filter(
            profile=profile,
            reading_datetime__date__gte=goal.start_date,
            reading_datetime__date__lte=today 
        ).aggregate(total_consumption=Sum('total_kwh_consumption'))['total_consumption'] or Decimal('0.00')

        status = "Em Andamento"
        progress_percentage = Decimal('0.00')
        goal_specific_status = ""
        current_consumption_for_goal = Decimal('0.00') # Para o caso de goal_type 'kwh_absolute'

        # Lógica de cálculo de progresso baseada no tipo de meta
        if goal.goal_type == 'kwh_absolute':
            current_consumption_for_goal = consumption_in_goal_period
            if goal.target_kwh and goal.target_kwh > 0:
                progress_percentage = (current_consumption_for_goal / goal.target_kwh) * 100
                if current_consumption_for_goal <= goal.target_kwh:
                    goal_specific_status = f"Dentro da meta! Consumo atual: {current_consumption_for_goal:.2f} kWh."
                else:
                    goal_specific_status = f"Acima da meta! Consumo atual: {current_consumption_for_goal:.2f} kWh."
            else:
                goal_specific_status = "Meta absoluta inválida (valor alvo deve ser maior que zero)."
                #progress_percentage = Decimal('0.00') 
            # Atualiza o status geral da meta
            if goal.target_kwh and current_consumption_for_goal >= goal.target_kwh:
                status = "Meta Atingida (ou Excedida)"
        elif goal.goal_type == 'kwh_reduction_percent':
            # Placeholder para lógica de redução percentual
            # Necessitaria de um consumo de referência (ex: mês anterior, média histórica)
            goal_specific_status = "Cálculo de meta de redução percentual não implementado."
        elif goal.goal_type == 'cost_target':
            # Placeholder para lógica de meta de custo
            # Necessitaria somar os custos das faturas no período
            goal_specific_status = "Cálculo de meta de custo não implementado."
        else:
            goal_specific_status = "Tipo de meta desconhecido."

        goal_overviews.append({
            'goal_id': goal.id,
            'goal_name': goal.name,
            'goal_type': goal.goal_type,
            'target_value': float(goal.target_value) if goal.target_value else None,
            'target_kwh': float(goal.target_kwh) if hasattr(goal, 'target_kwh') else None, # Adicionado para clareza
            'start_date': goal.start_date,
            'end_date': goal.end_date,
            'is_active': goal.is_active,
            'consumption_to_date': round(consumption_in_goal_period, 2), # Consumo no período da meta até hoje
            'current_consumption_for_kwh_absolute': round(current_consumption_for_goal, 2), # Consumo específico para tipo KWH_absolute
            'progress_percentage': round(progress_percentage, 2),
            'status': status, # Status geral (Em Andamento / Atingida)
            'goal_specific_status_message': goal_specific_status, # Mensagem detalhada por tipo de meta
        })
    
    message = f"{len(goal_overviews)} meta(s) ativa(s) encontrada(s)."
    return {'goal_overviews': goal_overviews, 'message': message}


def classify_brand_efficiency(analysis_type='HYBRID'):
    """
    Analisa e classifica a eficiência das marcas.

    Args:
        analysis_type (str): O tipo de análise a ser executada.
            - 'THEORETICAL': Baseado apenas nos dados do catálogo (Selo Procel).
            - 'HYBRID': Combina dados teóricos com dados de consumo real.

    Returns:
        Uma lista de dicionários com o ranking das marcas e uma mensagem de status.
    """
    # --- PASSO 1: ANÁLISE TEÓRICA (COMUM A AMBOS OS MÉTODOS) ---
    
    devices = DeviceCatalog.objects.exclude(marca__isnull=True).exclude(marca='OUTRA').exclude(procel_seal='NA')
    
    if not devices.exists():
        return [], "Nenhum dispositivo com dados suficientes no catálogo para análise.", None

    score_map = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1}
    theoretical_data = [{'device_id': d.id, 'marca': d.marca, 'theoretical_score': score_map.get(d.procel_seal, 0)} for d in devices]
    df_catalog = pd.DataFrame(theoretical_data)

    # If theoretical_score might implicitly become Decimal due to other operations
    # or if you want to ensure it's a float for later calculations:
    # df_catalog['theoretical_score'] = df_catalog['theoretical_score'].astype(float)


    # Se a análise for apenas teórica, já podemos pular para o final.
    if analysis_type == 'THEORETICAL':
        print("Executando análise de eficiência TEÓRICA...")
        brand_ranking_df = df_catalog.groupby('marca')['theoretical_score'].agg(['mean', 'size']).reset_index()
        brand_ranking_df.rename(columns={'mean': 'average_score', 'size': 'device_count'}, inplace=True)
    
    elif analysis_type == 'HYBRID':
        print("Executando análise de eficiência HÍBRIDA (Teórico vs. Real)...")
        
        # --- PASSO 2 (HÍBRIDO): CALCULAR O SCORE DE USO REAL ---
        real_usage_data = EnergyReading.objects.filter(profile_device__isnull=False).values(
            'profile_device__device__id', 
        ).annotate(
            real_avg_consumption=Avg('total_kwh_consumption')
        ).order_by('real_avg_consumption')

        df_real_usage = pd.DataFrame(list(real_usage_data))
        
        # Explicitly convert 'real_avg_consumption' to float here
        # This is the key change to ensure type consistency
        df_real_usage['real_avg_consumption'] = df_real_usage['real_avg_consumption'].astype(float) #
        
        real_world_score = pd.DataFrame(columns=['device_id', 'real_world_score'])
        if not df_real_usage.empty:
            min_cons = df_real_usage['real_avg_consumption'].min()
            max_cons = df_real_usage['real_avg_consumption'].max()
            if max_cons > min_cons:
                df_real_usage['real_world_score'] = 5 - 4 * (df_real_usage['real_avg_consumption'] - min_cons) / (max_cons - min_cons)
            else:
                # Ensure this is a float for consistency with other float operations
                df_real_usage['real_world_score'] = 5.0 #
            
            df_real_usage.rename(columns={'profile_device__device__id': 'device_id'}, inplace=True)
            real_world_score = df_real_usage[['device_id', 'real_world_score']]

        # --- PASSO 3 (HÍBRIDO): COMBINAR DADOS E CALCULAR SCORE HÍBRIDO ---
        if not real_world_score.empty:
            df_merged = pd.merge(df_catalog, real_world_score, on='device_id', how='left')
            # Ensure fillna value is float for consistency
            df_merged['real_world_score'].fillna(3.0, inplace=True) #
        else:
            df_merged = df_catalog
            # Ensure this is a float for consistency
            df_merged['real_world_score'] = 3.0 #
        
        # Peso: 60% para o Selo Procel, 40% para o desempenho real.
        # Use float literals for weights to match the float type of the scores
        df_merged['final_score'] = (df_merged['theoretical_score'] * 0.6) + (df_merged['real_world_score'] * 0.4) #
        
        brand_ranking_df = df_merged.groupby('marca')['final_score'].agg(['mean', 'size']).reset_index()
        brand_ranking_df.rename(columns={'mean': 'average_score', 'size': 'device_count'}, inplace=True)
        
    else:
        return [], f"Tipo de análise '{analysis_type}' desconhecido.", None


    def get_category(score):
        if score >= 4.5: return 'Excelente'
        elif score >= 4.0: return 'Muito Boa'
        elif score >= 3.0: return 'Boa'
        elif score >= 2.0: return 'Regular'
        else: return 'Ineficiente'

    
            
    brand_ranking_df['efficiency_category'] = brand_ranking_df['average_score'].apply(get_category)
    brand_ranking_df = brand_ranking_df.sort_values(by='average_score', ascending=False)

    chart_json = None
    if not brand_ranking_df.empty:
        # Define uma cor para cada categoria de eficiência
        category_color_map = {
            'Excelente': 'rgba(25, 135, 84, 0.9)', # Verde Escuro
            'Muito Boa': 'rgba(13, 202, 240, 0.8)',  # Azul Claro
            'Boa': 'rgba(13, 110, 253, 0.7)',       # Azul
            'Regular': 'rgba(255, 193, 7, 0.8)',      # Amarelo
            'Ineficiente': 'rgba(220, 53, 69, 0.9)'   # Vermelho
        }
        brand_ranking_df['color'] = brand_ranking_df['efficiency_category'].map(category_color_map)

        fig = go.Figure(data=[go.Scatter(
            x=brand_ranking_df['device_count'], 
            y=brand_ranking_df['average_score'],
            mode='markers',
            marker=dict(
                color=brand_ranking_df['color'],
                # O tamanho da bolha é proporcional à contagem de dispositivos
                size=brand_ranking_df['device_count'],
                sizemode='area', # 'area' ou 'diameter'
                sizeref=2.*max(brand_ranking_df['device_count'])/(40.**2), # Ajusta a escala do tamanho
                showscale=False
            ),
            # Texto que aparece ao passar o mouse sobre a bolha
            hovertemplate=(
                "<b>%{text}</b><br><br>" +
                "Pontuação de Eficiência: %{y:.2f}<br>" +
                "Produtos Analisados: %{x}<br>" +
                "Classificação: %{customdata[0]}" +
                "<extra></extra>"
            ),
            text=brand_ranking_df['marca'],
            customdata=brand_ranking_df[['efficiency_category']]
        )])

        fig.update_layout(
            title_text='Análise de Eficiência: Pontuação vs. Volume de Produtos por Marca',
            template="plotly_white",
            xaxis_title='Número de Produtos Analisados (confiança)',
            yaxis_title='Pontuação Média de Eficiência',
            height=500,
            margin=dict(l=40, r=40, t=60, b=40)
        )
        
        chart_json = fig.to_json()
    
    ranked_brands = brand_ranking_df.to_dict('records')
    return ranked_brands, f"Análise do tipo '{analysis_type}' concluída para {len(ranked_brands)} marcas.", chart_json

def calculate_benchmark_data(profile_devices_queryset):
    if not profile_devices_queryset.exists():
        return {
            'total_kwh_daily': 0, 'device_kwh_data': [], 'highest_consumer': None,
            'optimization_suggestions': ["Nenhum dispositivo para analisar."],
            'bar_chart_json': None, 'pie_chart_json': None, 'gauge_chart_json': None,
            'device_count': 0, 'optimization_percentage': 0
        }

    device_kwh_data = []
    total_kwh_daily = Decimal('0.0')
    for pd_instance in profile_devices_queryset:
        daily_kwh = pd_instance.daily_kwh_consumption or Decimal('0.0')
        device_kwh_data.append({
            'name': pd_instance.device.name, 'daily_kwh': float(daily_kwh),
            'monthly_kwh': float(pd_instance.monthly_kwh_consumption or 0.0),
            'annual_kwh': float(pd_instance.annual_kwh_consumption or 0.0),
            'quantity': int(pd_instance.quantity),
            'hours_per_day': float(pd_instance.hours_per_day or 0.0),
            'procel_seal': pd_instance.device.procel_seal or 'N/A', 'icon': pd_instance.device.icon
        })
        total_kwh_daily += daily_kwh
    
    device_kwh_data_sorted = sorted(device_kwh_data, key=lambda x: x['daily_kwh'], reverse=True)
    highest_consumer_data = device_kwh_data_sorted[0] if device_kwh_data_sorted else None
    
    optimization_suggestions = []
    if highest_consumer_data and highest_consumer_data['daily_kwh'] > 0:
        optimization_suggestions.append(
            f"O dispositivo que mais consome é '{highest_consumer_data['name']}' com {highest_consumer_data['daily_kwh']:.2f} kWh/dia."
        )

    if highest_consumer_data and highest_consumer_data['daily_kwh'] > 0 and total_kwh_daily > 0:
        # 1. Análise do Maior Consumidor
        impact_percentage = (Decimal(highest_consumer_data['daily_kwh']) / total_kwh_daily) * 100
        optimization_suggestions.append(
            f"Foco no '{highest_consumer_data['name']}', que representa {impact_percentage:.1f}% do seu consumo diário."
        )

        # 2. Sugestão de Redução de Tempo de Uso com Cálculo
        if highest_consumer_data['hours_per_day'] > 1:
            kwh_per_hour = Decimal(highest_consumer_data['daily_kwh']) / Decimal(highest_consumer_data['hours_per_day'])
            annual_savings_kwh = kwh_per_hour * Decimal(365.25)
            optimization_suggestions.append(
                f"Reduzir o uso do(a) '{highest_consumer_data['name']}' em apenas 1 hora por dia pode economizar aproximadamente {annual_savings_kwh:.2f} kWh ao longo de um ano."
            )

    # 3. Análise de Eficiência (Selo Procel) para todos os dispositivos
    for device in device_kwh_data_sorted:
        if device['procel_seal'] in ['C', 'D', 'E'] and device['daily_kwh'] > 0:
             optimization_suggestions.append(
                f"Atenção: Seu dispositivo '{device['name']}' tem Selo Procel '{device['procel_seal']}', que indica baixa eficiência. Substituí-lo por um modelo 'A' pode gerar economias significativas."
            )

    if not optimization_suggestions:
        optimization_suggestions.append("Parabéns, seu perfil de consumo parece bem otimizado com base nos dados atuais!")
    

    bar_chart_json, pie_chart_json, gauge_chart_json = None, None, None
    optimization_percentage = 0
    if total_kwh_daily > 0:
        bar_fig = go.Figure(data=[go.Bar(x=[d['name'] for d in device_kwh_data_sorted], y=[d['daily_kwh'] for d in device_kwh_data_sorted])])
        bar_fig.update_layout(title_text='Consumo por Dispositivo', template="plotly_white", margin=dict(l=20, r=20, t=40, b=20), height=300)
        bar_chart_json = bar_fig.to_json()

        pie_fig = go.Figure(data=[go.Pie(labels=[d['name'] for d in device_kwh_data_sorted], values=[d['daily_kwh'] for d in device_kwh_data_sorted], hole=.3)])
        pie_fig.update_layout(title_text='Distribuição de Consumo', template="plotly_white", margin=dict(l=20, r=20, t=40, b=20), height=300)
        pie_chart_json = pie_fig.to_json()

        optimization_percentage = max(Decimal('0.0'), min(Decimal('100'), (Decimal('20.0') - total_kwh_daily) * 5))
        gauge_fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = float(optimization_percentage),
        title = {'text': "Nível de Otimização (%)"},
        delta = {'reference': 80, 'increasing': {'color': "RebeccaPurple"}}, # Mostra a diferença em relação a um valor de referência
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"}, # Cor da barra de valor
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            # As faixas de cor (indicadores)
            'steps': [
                {'range': [0, 50], 'color': 'rgba(255, 0, 0, 0.7)'},
                {'range': [50, 80], 'color': 'rgba(255, 255, 0, 0.7)'},
                {'range': [80, 100], 'color': 'rgba(0, 128, 0, 0.7)'}
            ],
            # A linha de objetivo (seta)
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 95  # Define o objetivo em 95%
            }
        }))

        gauge_fig.update_layout(template="plotly_white", margin=dict(l=30, r=30, t=30, b=0), height=250)
        gauge_chart_json = gauge_fig.to_json()

    return {
        'total_kwh_daily': round(total_kwh_daily, 2),
        'device_kwh_data': device_kwh_data_sorted,
        'highest_consumer': highest_consumer_data,
        'optimization_suggestions': optimization_suggestions,
        'bar_chart_json': bar_chart_json,
        'pie_chart_json': pie_chart_json,
        'gauge_chart_json': gauge_chart_json,
        'device_count': len(device_kwh_data),  # <-- NOVO DADO
        'optimization_percentage': round(optimization_percentage, 1), # <-- NOVO DADO
    }


def monitoring_performance_and_consumption(profile, profile_devices, accuracy_scores_queryset):
    """
    Monitora a performance do modelo (acurácia) e o consumo de energia,
    fornecendo dados históricos (diário, semanal, mensal, anual) e comparações.

    Args:
        profile: O objeto Profile do Django.
        profile_devices: QuerySet de ProfileDevice para o perfil.
        accuracy_scores_queryset: QuerySet de ModelAccuracyScore para o perfil.

    Returns:
        Um dicionário contendo:
        - Métricas de consumo atual.
        - Dados históricos e comparativos de consumo.
        - Dados e gráfico de acurácia do modelo.
    """
    brazil_tz = get_brazil_timezone()
    now_brazil = datetime.now(brazil_tz)

    print(f"\n--- DEBUG: monitoring_performance_and_consumption para Perfil: {profile.name} (ID: {profile.pk}) ---")
    print(f"DEBUG: Data/Hora atual (Brasil): {now_brazil}")
    print(f"DEBUG: Início do mês atual: {now_brazil.replace(day=1, hour=0, minute=0, second=0, microsecond=0)}")
    print(f"DEBUG: Início do mês anterior: {(now_brazil.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)}")

    # --- Dados de Consumo e Comparativos ---
    consumption_data = {}

    # Períodos de faturamento
    start_of_current_month = now_brazil.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_of_last_month = (start_of_current_month - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    current_month_readings = EnergyReading.objects.filter(
        profile=profile,
        reading_datetime__gte=start_of_current_month,
        reading_datetime__lt=now_brazil
    )
    last_month_readings = EnergyReading.objects.filter(
        profile=profile,
        reading_datetime__gte=start_of_last_month,
        reading_datetime__lt=start_of_current_month
    )

    # ... (código existing para current_month_readings e last_month_readings)

    total_kwh_current_month = current_month_readings.aggregate(Sum('total_kwh_consumption'))['total_kwh_consumption__sum'] or Decimal('0')
    total_kwh_last_month = last_month_readings.aggregate(Sum('total_kwh_consumption'))['total_kwh_consumption__sum'] or Decimal('0')

    estimated_cost_current_month = 0
    if profile.default_tariff:
        estimated_cost_current_month = total_kwh_current_month * profile.default_tariff.cost_per_kwh
        current_flag = TariffFlagAdditive.objects.filter(
            start_date__lte=now_brazil.date(),
            end_date__gte=now_brazil.date()
        ).first()
        if current_flag:
            estimated_cost_current_month += (Decimal(total_kwh_current_month) / Decimal('100')) * current_flag.additional_cost_per_100kwh

    kwh_diff = total_kwh_current_month - total_kwh_last_month
    kwh_diff_percentage = (kwh_diff / total_kwh_last_month * Decimal('100')) if total_kwh_last_month > Decimal('0') else Decimal('0')
    co2_emissions_current_month = total_kwh_current_month * Decimal('0.05')

    consumption_data.update({
        'total_kwh_current_month': round(total_kwh_current_month, 2),
        'estimated_cost_current_month': round(estimated_cost_current_month, 2),
        'kwh_diff_percentage': round(kwh_diff_percentage, 2),
        'co2_emissions_current_month': round(co2_emissions_current_month, 2),
        'recent_alerts': Alert.objects.filter(profile=profile).order_by('-triggered_at')[:5],
        'recent_suggestions': OptimizationSuggestion.objects.filter(profile=profile).order_by('-suggested_at')[:5],
    })

    # Histórico de Consumo (Diário, Semanal, Mensal, Anual)
    all_readings = EnergyReading.objects.filter(profile=profile, reading_datetime__lte=now_brazil)
    readings_df = pd.DataFrame(list(all_readings.values('reading_datetime', 'total_kwh_consumption')))

    # --- CORREÇÃO AQUI: Inicialize historical_consumption ANTES DO IF ---
    historical_consumption = {
        'daily': [],
        'weekly': [],
        'monthly': [],
        'annual': []
    } # Garante que historical_consumption sempre é um dicionário com listas vazias

    if not readings_df.empty:
        readings_df['total_kwh_consumption'] = pd.to_numeric(readings_df['total_kwh_consumption'], errors='coerce')
        readings_df['reading_datetime'] = pd.to_datetime(readings_df['reading_datetime']).dt.tz_convert(brazil_tz) # JÁ VEM TZ-AWARE, SÓ CONVERTE
        readings_df.set_index('reading_datetime', inplace=True)

        # Diário (últimos 30 dias)
        daily_consumption = readings_df.resample('D')['total_kwh_consumption'].sum().tail(30).reset_index()
        daily_consumption.columns = ['ds', 'y']
        daily_consumption['ds'] = daily_consumption['ds'].dt.strftime('%Y-%m-%d %H:%M:%S')
        historical_consumption['daily'] = daily_consumption.to_dict(orient='records')

        # Semanal (últimas 12 semanas)
        weekly_consumption = readings_df.resample('W')['total_kwh_consumption'].sum().tail(12).reset_index()
        weekly_consumption.columns = ['ds', 'y']
        weekly_consumption['ds'] = weekly_consumption['ds'].dt.strftime('%Y-%m-%d')
        historical_consumption['weekly'] = weekly_consumption.to_dict(orient='records')

        # Mensal (últimos 12 meses)
        monthly_consumption = readings_df.resample('ME')['total_kwh_consumption'].sum().tail(12).reset_index()
        monthly_consumption.columns = ['ds', 'y']
        monthly_consumption['ds'] = monthly_consumption['ds'].dt.strftime('%Y-%m-%d')
        historical_consumption['monthly'] = monthly_consumption.to_dict(orient='records')

        # Anual (últimos 5 anos)
        yearly_consumption = readings_df.resample('YE')['total_kwh_consumption'].sum().tail(5).reset_index()
        yearly_consumption.columns = ['ds', 'y']
        yearly_consumption['ds'] = yearly_consumption['ds'].dt.strftime('%Y-%m-%d')
        historical_consumption['annual'] = yearly_consumption.to_dict(orient='records')

    # --- CORREÇÃO AQUI: ATRIBUIR historical_consumption A consumption_data DEPOIS QUE ESTIVER PREENCHIDO ---
    # Movi esta linha para depois do if not readings_df.empty,
    # para garantir que consumption_data.update() sempre veja o historical_consumption mais atualizado.
    consumption_data['historical_consumption'] = historical_consumption

    print(f"DEBUG: Total kWh Mês Atual: {total_kwh_current_month}")
    print(f"DEBUG: Total kWh Mês Anterior: {total_kwh_last_month}")
    print(f"DEBUG: Custo Estimado Mês Atual: {estimated_cost_current_month}")

    print(f"DEBUG: Número de leituras mês atual: {current_month_readings.count()}")
    print(f"DEBUG: Número de leituras mês anterior: {last_month_readings.count()}")
    print(f"DEBUG: Número total de leituras EnergyReading: {EnergyReading.objects.filter(profile=profile).count()}")

    print(f"DEBUG: readings_df.empty: {readings_df.empty}, readings_df.shape: {readings_df.shape if not readings_df.empty else 'N/A'}")

    print(f"DEBUG: historical_consumption content (keys): {historical_consumption.keys()}")
    if 'daily' in historical_consumption and historical_consumption['daily']:
        print(f"DEBUG: Exemplo de dado diário histórico: {historical_consumption['daily'][:3]}")

    # Gráfico de Consumo Diário (para o mês atual)
    daily_current_month_df = pd.DataFrame(list(current_month_readings.values('reading_datetime', 'total_kwh_consumption')))
    daily_current_month_chart = None
    daily_consumption_chart = None
    if not daily_current_month_df.empty:
        daily_current_month_df['total_kwh_consumption'] = pd.to_numeric(daily_current_month_df['total_kwh_consumption'], errors='coerce')
        daily_current_month_df['reading_date'] = daily_current_month_df['reading_datetime'].dt.date
        daily_consumption_current_month = daily_current_month_df.groupby('reading_date')['total_kwh_consumption'].sum().reset_index()
        daily_consumption_current_month.columns = ['ds', 'y']

        daily_consumption_fig = go.Figure(data=[
            go.Scatter(x=daily_consumption_current_month['ds'], y=daily_consumption_current_month['y'], mode='lines+markers', name='Consumo Diário')
        ])
        daily_consumption_fig.update_layout(
            title_text='Consumo Diário (Mês Atual)',
            xaxis_title='Data',
            yaxis_title='Consumo (kWh)',
            template="plotly_white",
            margin=dict(l=0, r=0, t=40, b=0),
            height=300
        )
        daily_consumption_chart = daily_consumption_fig.to_json()
    consumption_data['daily_consumption_chart_json'] = daily_consumption_chart
    print(f"DEBUG: daily_current_month_df.empty: {daily_current_month_df.empty}, daily_current_month_df.shape: {daily_current_month_df.shape if not daily_current_month_df.empty else 'N/A'}")


    # --- Dados de Acurácia ---
    accuracy_data = {'monitoring_data': [], 'monitoring_chart_json': None}

    plot_data = []
    unique_profiles_with_scores = set()

    for score_obj in accuracy_scores_queryset.order_by('profile__name', 'evaluation_date'):
        profile_name = score_obj.profile.name
        if profile_name not in unique_profiles_with_scores:
            unique_profiles_with_scores.add(profile_name)
            
            profile_scores_filtered = accuracy_scores_queryset.filter(profile=score_obj.profile).order_by('evaluation_date')
            profile_dates = [s.evaluation_date for s in profile_scores_filtered]
            profile_scores = [float(s.score) for s in profile_scores_filtered]

            if profile_dates:
                plot_data.append({
                    'name': profile_name,
                    'dates': profile_dates,
                    'scores': profile_scores,
                    'latest_score': profile_scores[-1]
                })
    print(f"DEBUG: accuracy_scores_queryset count: {accuracy_scores_queryset.count()}")
    print(f"DEBUG: plot_data (antes da simulação): {plot_data}")

    
    if not plot_data and profile_devices:

        print(f"DEBUG: Gerando dados de acurácia simulados. profile_devices count: {profile_devices.count()}")
       
        base_date = datetime.now()
        main_profile_id = profile_devices[0].profile.id if profile_devices else None
        latest_profile_score = (accuracy_scores_queryset.filter(profile_id=main_profile_id).order_by('-evaluation_date').first().score if accuracy_scores_queryset.filter(profile_id=main_profile_id).exists() else 0.85)

        simulated_dates = [base_date - timedelta(days=i) for i in range(10, 0, -1)]
        simulated_scores = [max(0.0, min(1.0, latest_profile_score + (i % 5 - 2) * 0.02)) for i in range(10)]
        
        if profile_devices:
            plot_data.append({
                'name': profile_devices[0].profile.name + " (Simulado)",
                'dates': simulated_dates,
                'scores': simulated_scores,
                'latest_score': simulated_scores[-1]
            })
        else:
             plot_data.append({
                'name': "Acurácia Geral (Simulado)",
                'dates': simulated_dates,
                'scores': simulated_scores,
                'latest_score': simulated_scores[-1]
            })
    print(f"DEBUG: plot_data (final): {plot_data}")

    fig = go.Figure()
    for data in plot_data:
        print(f"  - Perfil: {data['name']}, Datas count: {len(data['dates'])}, Scores count: {len(data['scores'])}")
        print(f"    Primeira Data: {data['dates'][0] if data['dates'] else 'N/A'}, Última Data: {data['dates'][-1] if data['dates'] else 'N/A'}")
        print(f"    Primeiro Score: {data['scores'][0] if data['scores'] else 'N/A'}, Último Score: {data['scores'][-1] if data['scores'] else 'N/A'}")

        fig.add_trace(go.Scatter(
            x=data['dates'],
            y=data['scores'],
            mode='lines+markers',
            name=data['name']
        ))

    attention_line = 0.75
    danger_line = 0.60
    fig.add_hline(y=attention_line, line_dash="dash", line_color="orange", annotation_text="Atenção (0.75)", annotation_position="top right")
    fig.add_hline(y=danger_line, line_dash="dash", line_color="red", annotation_text="Perigo (0.60)", annotation_position="bottom right")

    fig.update_layout(
        title_text='Acurácia do Modelo por Perfil ao Longo do Tempo',
        xaxis_title='Data e Hora da Avaliação',
        yaxis_title='Acurácia (0-1)',
        template="plotly_white",
        margin=dict(l=0, r=0, t=40, b=0),
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_tickformat='%d/%m %H:%M'
    )
    # accuracy_data['monitoring_chart_json'] = fig.to_json()
    # accuracy_data['monitoring_data'] = plot_data

    print(f"DEBUG: consumption_data['daily_consumption_chart_json'] is None: {consumption_data['daily_consumption_chart_json'] is None}")
    print(f"DEBUG: accuracy_data['monitoring_chart_json'] is None: {accuracy_data['monitoring_chart_json'] is None}")
    print("--- FIM DEBUG monitoring_performance_and_consumption ---\n")

    accuracy_data['monitoring_chart_json'] = fig.to_json() 

    accuracy_data['monitoring_data'] = plot_data


    return {
        'consumption_metrics': consumption_data,
        'accuracy_metrics': accuracy_data
    }


def calculate_comprehensive_trends_data(profile, historical_data_queryset=None):
    """
    Calcula e retorna dados abrangentes de tendências de consumo, incluindo:
    - Consumo mensal histórico.
    - Comparação de consumo anual (mês a mês).
    - Histórico de consumo diário (se aplicável, para diferentes tipos de dados).

    Args:
        profile: O objeto Profile do Django.
        historical_data_queryset: QuerySet opcional de EnergyReading, BillingRecord ou ConsumptionPredictions.
                                  Se fornecido, será usado para o histórico de consumo diário.
                                  Caso contrário, EnergyReading será usado por padrão.

    Returns:
        Um dicionário contendo:
        - 'monthly_consumption_chart_json': Gráfico de linha do consumo mensal histórico.
        - 'annual_comparison_chart_json': Gráfico de barras para comparação anual.
        - 'daily_trend_chart_json': Gráfico de linha do histórico de consumo diário.
        - 'total_consumption_history_daily': Dados brutos do histórico diário.
        - 'error_message_daily_trend': Mensagem de erro para o gráfico de tendência diária, se houver.
    """
    brazil_tz = get_brazil_timezone()
    now_brazil = datetime.now(brazil_tz)

    # --- 1. Dados de Consumo Mensal e Comparação Anual ---
    monthly_consumption_chart_json = None
    annual_comparison_chart_json = None

    # Últimos 24 meses de dados para análise mensal/anual
    end_date_monthly = now_brazil.date().replace(day=1) # Início do mês atual
    # Para garantir 24 meses completos, vá para o primeiro dia do mês 24 meses atrás
    start_date_monthly = (end_date_monthly - timedelta(days=365*2)).replace(day=1)

    monthly_readings = EnergyReading.objects.filter(
        profile=profile,
        reading_datetime__date__gte=start_date_monthly,
        reading_datetime__date__lt=now_brazil.date() + timedelta(days=1) # Inclui leituras até o dia atual
    ).values('reading_datetime__year', 'reading_datetime__month').annotate(
        total_kwh=Sum('total_kwh_consumption')
    ).order_by('reading_datetime__year', 'reading_datetime__month')

    data_monthly_df = []
    for entry in monthly_readings:
        year = entry['reading_datetime__year']
        month = entry['reading_datetime__month']
        date_str = f"{year}-{month:02d}-01"
        data_monthly_df.append({'date': date_str, 'kwh': float(entry['total_kwh'])})

    df_monthly = pd.DataFrame(data_monthly_df)

    if not df_monthly.empty:
        df_monthly['date'] = pd.to_datetime(df_monthly['date'])
        df_monthly = df_monthly.set_index('date')

        # Gráfico de Consumo Mensal Histórico (Linha)
        monthly_fig = go.Figure(data=[
            go.Scatter(x=df_monthly.index, y=df_monthly['kwh'], mode='lines+markers', name='Consumo Mensal')
        ])
        monthly_fig.update_layout(
            title_text='Consumo Mensal Histórico',
            xaxis_title='Data',
            yaxis_title='Consumo (kWh)',
            template="plotly_white",
            margin=dict(l=0, r=0, t=40, b=0),
            height=300
        )
        monthly_consumption_chart_json = monthly_fig.to_json()

        # Gráfico de Comparação Anual (Exemplo: Ano a Ano para o mesmo mês)
        df_monthly['year'] = df_monthly.index.year
        df_monthly['month'] = df_monthly.index.month

        annual_comparison_data = []
        current_year = now_brazil.year
        
        # Obter os anos presentes nos dados
        available_years = sorted(df_monthly['year'].unique(), reverse=True)
        # Comparar o ano mais recente com o anterior, se existirem
        if len(available_years) >= 2:
            year1 = available_years[0] # Ano mais recente
            year2 = available_years[1] # Ano anterior

            for month_num in range(1, 13):
                kwh_year1 = df_monthly[(df_monthly['year'] == year1) & (df_monthly['month'] == month_num)]['kwh'].sum()
                kwh_year2 = df_monthly[(df_monthly['year'] == year2) & (df_monthly['month'] == month_num)]['kwh'].sum()
                
                if kwh_year1 > 0 or kwh_year2 > 0:
                    annual_comparison_data.append({
                        'month': datetime(1900, month_num, 1).strftime('%b'), # Mês abreviado
                        'year1_label': str(year1),
                        'year2_label': str(year2),
                        'year1_kwh': float(kwh_year1),
                        'year2_kwh': float(kwh_year2)
                    })

            if annual_comparison_data:
                annual_comparison_df = pd.DataFrame(annual_comparison_data)
                annual_comparison_fig = go.Figure(data=[
                    go.Bar(name=f'Consumo {annual_comparison_df["year2_label"].iloc[0]}', x=annual_comparison_df['month'], y=annual_comparison_df['year2_kwh']),
                    go.Bar(name=f'Consumo {annual_comparison_df["year1_label"].iloc[0]}', x=annual_comparison_df['month'], y=annual_comparison_df['year1_kwh'])
                ])
                annual_comparison_fig.update_layout(
                    barmode='group',
                    title_text=f'Comparação de Consumo Anual ({year2} vs {year1})',
                    xaxis_title='Mês',
                    yaxis_title='Consumo (kWh)',
                    template="plotly_white",
                    margin=dict(l=0, r=0, t=40, b=0),
                    height=300
                )
                annual_comparison_chart_json = annual_comparison_fig.to_json()
    
    # --- 2. Histórico de Consumo Diário (para diferentes modelos) ---
    daily_trend_chart_json = None
    total_consumption_history_daily = []
    error_message_daily_trend = None

    # Se historical_data_queryset não for fornecido, usa EnergyReading como padrão para histórico diário
    if historical_data_queryset is None:
        historical_data_queryset = EnergyReading.objects.filter(profile=profile)
        
    if not historical_data_queryset.exists():
        error_message_daily_trend = "Nenhum dado histórico de consumo encontrado para o gráfico de tendência diária."
    else:
        df_daily_trend = pd.DataFrame()
        model_name = historical_data_queryset.model.__name__

        if model_name == 'EnergyReading':
            # CORREÇÃO AQUI: Use 'total_kwh_consumption' em vez de 'kwh_value'
            df_daily_trend = pd.DataFrame(list(historical_data_queryset.values('reading_datetime', 'total_kwh_consumption')))
            df_daily_trend = df_daily_trend.rename(columns={'reading_datetime': 'date', 'total_kwh_consumption': 'consumption'})
        elif model_name == 'BillingRecord':
            df_daily_trend = pd.DataFrame(list(historical_data_queryset.values('invoice_date', 'kwh_total_billed')))
            df_daily_trend = df_daily_trend.rename(columns={'invoice_date': 'date', 'kwh_total_billed': 'consumption'})
        elif model_name == 'ConsumptionPredictions':
            df_daily_trend = pd.DataFrame(list(historical_data_queryset.values('prediction_date', 'predicted_daily_kwh')))
            df_daily_trend = df_daily_trend.rename(columns={'prediction_date': 'date', 'predicted_daily_kwh': 'consumption'})
        else:
            error_message_daily_trend = f"Tipo de dado histórico '{model_name}' não suportado para tendências diárias."

        if not df_daily_trend.empty:
            df_daily_trend['consumption'] = pd.to_numeric(df_daily_trend['consumption'], errors='coerce')
            df_daily_trend['date'] = pd.to_datetime(df_daily_trend['date'])
            df_daily_trend['date'] = df_daily_trend['date'].dt.tz_localize(brazil_tz, ambiguous='NaT', nonexistent='NaT')
            df_daily_trend['date'] = df_daily_trend['date'].dt.tz_convert(brazil_tz)
            df_daily_trend = df_daily_trend.groupby(df_daily_trend['date'].dt.date)['consumption'].sum().reset_index()
            df_daily_trend = df_daily_trend.sort_values(by='date')

            fig_daily_trend = go.Figure(data=[go.Scatter(
                x=df_daily_trend['date'],
                y=df_daily_trend['consumption'],
                mode='lines+markers',
                name='Consumo Total Diário'
            )])
            fig_daily_trend.update_layout(
                title_text='Histórico de Consumo Diário do Perfil',
                xaxis_title='Data',
                yaxis_title='Consumo Total (kWh)',
                template="plotly_white",
                margin=dict(l=0, r=0, t=40, b=0),
                height=400
            )
            daily_trend_chart_json = fig_daily_trend.to_json()
            total_consumption_history_daily = df_daily_trend.to_dict('records')
        else:
            error_message_daily_trend = "Dados insuficientes para gerar o gráfico de tendência diária após processamento."

    return {
        'monthly_consumption_chart_json': monthly_consumption_chart_json,
        'annual_comparison_chart_json': annual_comparison_chart_json,
        'daily_trend_chart_json': daily_trend_chart_json,
        'total_consumption_history_daily': total_consumption_history_daily,
        'error_message_daily_trend': error_message_daily_trend
    }



def get_outlier_detection_chart_data(profile, start_date=None, end_date=None, period='daily'):
    """
    Detecta outliers no consumo de energia para um perfil e período,
    e gera um gráfico Plotly.

    Args:
        profile: Objeto EnergyProfiles.
        start_date (datetime.date): Data de início para a análise.
        end_date (datetime.date): Data de fim para a análise.
        period (str): 'daily' para agregação diária (pode ser expandido para 'hourly', 'weekly' etc.).

    Returns:
        Um dicionário contendo:
        - 'chart_json': JSON do gráfico Plotly.
        - 'num_outliers': Número de outliers detectados.
        - 'total_readings': Número total de leituras no período.
        - 'message': Mensagem de status ou erro.
    """
    if not start_date or not end_date:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30) # Padrão: últimos 30 dias

    readings = EnergyReading.objects.filter(
        profile=profile,
        reading_datetime__date__range=[start_date, end_date]
    ).annotate(
        date_only=TruncDate('reading_datetime') # Agrupa por data
    ).values('date_only').annotate(
        daily_kwh=Sum('total_kwh_consumption')
    ).order_by('date_only')

    if not readings.exists():
        return {
            'chart_json': None,
            'num_outliers': 0,
            'total_readings': 0,
            'message': "Nenhum dado de leitura de energia encontrado para o período selecionado."
        }

    df = pd.DataFrame(list(readings))
    df.rename(columns={'date_only': 'date', 'daily_kwh': 'kwh'}, inplace=True)
    df['kwh'] = pd.to_numeric(df['kwh'], errors='coerce')
    df.dropna(subset=['kwh'], inplace=True)

    if df.empty: 
        return {
            'chart_json': None,
            'num_outliers': 0,
            'total_readings': 0,
            'message': "Dados insuficientes após a limpeza de valores não numéricos."
        }
    
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df.sort_index(inplace=True)

    # --- Detecção de Outliers usando IQR ---
    Q1 = df['kwh'].quantile(0.25)
    Q3 = df['kwh'].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outliers = df[(df['kwh'] < lower_bound) | (df['kwh'] > upper_bound)]
    inliers = df[~((df['kwh'] < lower_bound) | (df['kwh'] > upper_bound))]

    # --- Geração do Gráfico Plotly ---
    fig = go.Figure()

    formatted_inliers_index = inliers.index.strftime('%Y-%m-%d').to_list()
    formatted_outliers_index = outliers.index.strftime('%Y-%m-%d').to_list()
    formatted_df_index = df.index.strftime('%Y-%m-%d').to_list()

    # Inliers (pontos normais)
    fig.add_trace(go.Scatter(
        x=formatted_inliers_index, # Usar o índice formatado
        y=inliers['kwh'].to_list(),
        mode='lines+markers',
        name='Consumo Normal',
        marker=dict(color='rgba(76, 175, 80, 0.8)', size=6), # Verde
        line=dict(color='rgba(76, 175, 80, 0.5)')
    ))

    # Outliers
    if not outliers.empty:
        fig.add_trace(go.Scatter(
            x=formatted_outliers_index, # Usar o índice formatado
            y=outliers['kwh'].to_list(),
            mode='markers',
            name='Outlier',
            marker=dict(color='rgba(244, 67, 54, 0.9)', size=8, symbol='x'), # Vermelho
            text=[f"Outlier: {val:.2f} kWh" for val in outliers['kwh'].to_list()],
            hoverinfo='x+y+text'
        ))

    # Linhas de Limite (Opcional, para visualização dos thresholds)
    fig.add_trace(go.Scatter(
        x=formatted_df_index, # Usar o índice formatado
        y=[float(lower_bound)] * len(df),
        mode='lines',
        name='Limite Inferior (IQR)',
        line=dict(dash='dash', color='gray', width=1),
        hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter(
        x=formatted_df_index, # Usar o índice formatado
        y=[float(upper_bound)] * len(df),
        mode='lines',
        name='Limite Superior (IQR)',
        line=dict(dash='dash', color='gray', width=1),
        hoverinfo='skip'
    ))


    fig.update_layout(
        title_text=f'Detecção de Outliers no Consumo Diário - {profile.name}',
        xaxis_title='Data',
        yaxis_title='Consumo Diário (kWh)',
        template="plotly_white",
        hovermode="x unified",
        margin=dict(l=50, r=50, t=60, b=50),
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    chart_json = json.dumps(fig.to_dict())

    return {
        'chart_json': chart_json,
        'num_outliers': len(outliers),
        'total_readings': len(df),
        'message': f"Análise de outliers para {len(df)} dias de dados."
    }

def run_prediction(profile, model, periods=30, custom_data=None):
    """
    Função ORQUESTRADORA principal.
    Lê o tipo de modelo e chama a função de análise correspondente.
    """
    
    # --- Passo 1: Obter Dados (Exemplo simplificado, pode variar por modelo) ---
    # Para muitos modelos, usar os dados de leitura como base é um bom começo.
    readings = EnergyReading.objects.filter(profile=profile).order_by('reading_datetime')
    if not readings.exists() and custom_data is None:
        return {'error_message': 'Dados históricos insuficientes.'}

    df = pd.DataFrame(list(readings.values('reading_datetime', 'total_kwh_consumption')))
    df = df.rename(columns={'reading_datetime': 'ds', 'total_kwh_consumption': 'y'})
    df['ds'] = pd.to_datetime(df['ds'])
    df['y'] = pd.to_numeric(df['y'], errors='coerce')

    # --- Passo 2: Executar o Modelo Específico ---
    model_type = model.model_type
    
    print(f"Executando lógica para o modelo do tipo: {model.get_model_type_display()}")

    # --- Modelos de Regressão / Previsão ---
    if model_type == 'LINEAR_REGRESSION':
        return _run_linear_regression(df)
    
    elif model_type == 'PROPHET':
        return _run_prophet(df, model, periods)
        
    elif model_type == 'RANDOM_FOREST_REG':
        # Placeholder para Florestas Aleatórias
        # Aqui você treinaria um RandomForestRegressor(n_estimators=100)
        # com os dados do df e faria a previsão.
        return {'message': 'Lógica para Florestas Aleatórias (Regressão) a ser implementada.'}

    elif model_type == 'TF_REG':
        # Placeholder para Keras/TensorFlow
        # Aqui você definiria, treinaria e usaria um modelo sequencial do Keras.
        return {'message': 'Lógica para Rede Neural de Regressão (Keras/TF) a ser implementada.'}
        
    # --- Modelos de Classificação ---
    elif model_type == 'LOGISTIC_REGRESSION':
        # Aqui você precisaria de uma coluna alvo categórica (ex: 'bandeira_tarifaria')
        return {'message': 'Lógica para Regressão Logística (Classificação) a ser implementada.'}
        
    elif model_type == 'DECISION_TREE_CLASS':
        return {'message': 'Lógica para Árvore de Decisão (Classificação) a ser implementada.'}
        
    # --- Modelos de Clusterização ---
    elif model_type == 'KMEANS':
        # Aqui você passaria dados de múltiplos perfis para agrupá-los
        return {'message': 'Lógica para K-Means (Clusterização) a ser implementada.'}
        
    elif model_type == 'GMM':
        return {'message': 'Lógica para Misturas de Gaussianas (Clusterização) a ser implementada.'}
        
    # --- Outros Algoritmos ---
    elif model_type == 'APRIORI':
        # Apriori é usado para encontrar itens frequentemente associados,
        # ex: "clientes que usam ar condicionado também usam umidificador".
        return {'message': 'Lógica para Apriori (Regras de Associação) a ser implementada.'}
        
    elif model_type == 'BAYESIAN_INFERENCE':
        # Usado para atualizar a probabilidade de uma hipótese à medida que mais evidências se tornam disponíveis.
        return {'message': 'Lógica para Inferência Bayesiana a ser implementada.'}
        
    elif model_type == 'KNN':
        # Usado para classificar ou prever com base nos 'k' vizinhos mais próximos.
        return {'message': 'Lógica para K-NN a ser implementada.'}
        
    elif model_type == 'UPLOAD':
        # Aqui entraria a lógica para carregar e usar um arquivo .pkl
        return {'message': 'Lógica para modelo via Upload a ser implementada.'}

    else:
        return {'error_message': f"Tipo de modelo '{model_type}' desconhecido ou sem lógica implementada."}



def calculate_forecast_data(profile, model, periods=None):
    """
    Calcula previsões de consumo usando as configurações definidas no objeto do modelo.
    """

    print(f"Iniciando previsão com a fonte de dados: {model.get_data_source_display()}")

    # --- Passo 1: Obter e validar os dados históricos com base na fonte definida no modelo ---
    if model.data_source == 'readings':
        queryset = EnergyReading.objects.filter(profile=profile).order_by('reading_datetime')
        date_field, value_field = 'reading_datetime', 'total_kwh_consumption'
    elif model.data_source == 'billing':
        queryset = BillingRecord.objects.filter(profile=profile).order_by('invoice_date')
        date_field, value_field = 'invoice_date', 'kwh_total_billed'
    elif model.data_source == 'devices': # <-- Adicione este bloco

        queryset = EnergyReading.objects.filter(
            profile=profile,
            profile_device__isnull=False # Garante que está ligado a um dispositivo
        ).annotate(
            # Agrega o consumo total por dia, se as leituras são horárias/diárias
            daily_date=TruncDate('reading_datetime')
        ).values('daily_date').annotate(
            total_daily_kwh=Sum('total_kwh_consumption')
        ).order_by('daily_date')
        
        date_field, value_field = 'daily_date', 'total_daily_kwh'
        if not queryset.exists():
             return {'error_message': "Nenhum dado de leitura de dispositivos encontrado para este perfil."}


    elif model.data_source == 'weather':
        # 1. código para chamar uma API de previsão do tempo.
        # 2. combinar os dados de temperatura com os de consumo.
        return {'error_message': 'Fonte de dados "Clima" ainda não implementada.'}

    elif model.data_source == 'solar':
        # 1. Aqui você buscaria os dados de um inversor solar.
        return {'error_message': 'Fonte de dados "Geração Solar" ainda não implementada.'}
    else:
        return {'error_message': f"Fonte de dados '{model.data_source}' desconhecida."}

    if queryset.count() < 5:
        return {'error_message': "Dados históricos insuficientes para gerar uma previsão."}

    df = pd.DataFrame(list(queryset.values(date_field, value_field)))
    df = df.rename(columns={date_field: 'ds', value_field: 'y'})
    df['ds'] = pd.to_datetime(df['ds']).dt.tz_localize(None)
    df['y'] = pd.to_numeric(df['y'], errors='coerce')
    df = df.groupby(df['ds'].dt.date).agg(y=('y', 'sum')).reset_index()
    df['ds'] = pd.to_datetime(df['ds'])

    # Usa o horizonte de previsão do modelo, se não for passado um específico
    forecast_periods = periods if periods is not None else model.default_forecast_horizon

    # --- Passo 2: Escolher e configurar o algoritmo com base no tipo de modelo ---
    
    if model.model_type == 'LINEAR_REGRESSION':
        print(f"Executando Regressão Linear para o modelo '{model.name}'...")
        chart_json, accuracy = _linear_regression_forecast(df)
        return {'forecast_chart_json': chart_json, 'forecast_accuracy': accuracy}

    elif model.model_type == 'PROPHET':
        print(f"Executando Prophet para o modelo '{model.name}'...")
        if Prophet is None:
            return {'error_message': "A biblioteca Prophet não está instalada."}
        
        
        prophet_model = Prophet(
            yearly_seasonality=model.yearly_seasonality,
            weekly_seasonality=model.weekly_seasonality,
            daily_seasonality=model.daily_seasonality,
            seasonality_mode=model.seasonality_mode,
            ** (model.additional_params or {}) # Adiciona quaisquer parâmetros extras do JSON
        )
        
        if model.include_brazil_holidays:
            prophet_model.add_country_holidays(country_name='BR')

        prophet_model.fit(df)
        future = prophet_model.make_future_dataframe(periods=forecast_periods)
        forecast = prophet_model.predict(future)

        # Geração do gráfico...
        fig = go.Figure()
        # ... (código do gráfico continua o mesmo)
        fig.add_trace(go.Scatter(x=df['ds'], y=df['y'], mode='markers', name='Histórico'))
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Previsão'))
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], fill='tonexty', mode='lines', line=dict(width=0), name='Intervalo de Confiança', fillcolor='rgba(0,100,80,0.2)'))
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], fill='tonexty', mode='lines', line=dict(width=0), showlegend=False, fillcolor='rgba(0,100,80,0.2)'))
        fig.update_layout(title_text=f'Previsão de Consumo ({model.name})', template="plotly_white")

        accuracy_metrics = {
            'metric_type': 'N/A (Prophet)',
            'accuracy_score': None # Ou calcule um valor se tiver um conjunto de teste
        }
        
        return {
            'forecast_data': forecast.to_dict('records'), 
            'forecast_chart_json': fig.to_json(),       
            'forecast_accuracy': accuracy_metrics        
        }

        
        #return {'forecast_data': forecast.to_dict('records'), 'forecast_chart_json': fig.to_json()}

    elif model.model_type == 'UPLOAD':
        # ... (lógica de upload)
        return {'error_message': "Previsão por upload ainda não implementada."}

    else:
        return {'error_message': f"Tipo de modelo '{model.model_type}' desconhecido."}



def _linear_regression_forecast(df):
    """
    Função auxiliar para previsão usando Regressão Linear Simples como fallback.
    """
    if len(df) < 2: # Precisamos de pelo menos 2 pontos para regressão
        return None, {'message': 'Dados insuficientes para regressão linear.'}

    df['timestamp'] = df['ds'].apply(lambda x: x.timestamp())
    X = df[['timestamp']]
    y = df['y']

    model = LinearRegression()
    model.fit(X, y)

    # Prever os próximos 30 dias
    last_date = df['ds'].max()
    future_dates = [last_date + timedelta(days=i) for i in range(1, 31)]
    future_timestamps = pd.DataFrame([d.timestamp() for d in future_dates], columns=['timestamp'])
    
    # Adicionar os dados históricos e futuros para plotagem completa
    all_dates = pd.concat([df['ds'], pd.Series(future_dates)])
    all_timestamps = pd.concat([df['timestamp'], future_timestamps['timestamp']])

    all_predictions = model.predict(all_timestamps.to_frame())
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['ds'], y=df['y'], mode='markers', name='Histórico'))
    fig.add_trace(go.Scatter(x=all_dates, y=all_predictions, mode='lines', name='Previsão (Regressão Linear)', line=dict(color='orange')))

    fig.update_layout(
        title_text='Previsão de Consumo Futuro (Regressão Linear)',
        xaxis_title='Data',
        yaxis_title='Consumo (kWh)',
        template="plotly_white",
        margin=dict(l=0, r=0, t=40, b=0),
        height=350,
        legend=dict(x=0.01, y=0.99, bordercolor="Black", borderwidth=1)
    )
    
    # Acurácia de regressão linear (exemplo simples: R-quadrado no conjunto de treinamento)
    r_squared = model.score(X, y)
    accuracy_metrics = {
        'metric_type': 'R-squared (Linear Regression)',
        'accuracy_score': round(r_squared, 4)
    }

    return fig.to_json(), accuracy_metrics


# --- Novas Funções de Utilidade (Exemplos) ---

def calculate_billing_summary(profile, billing_records_queryset):
    """
    Calcula um resumo de faturamento para um perfil, com base nos BillingRecords.
    """
    total_billed_kwh = billing_records_queryset.aggregate(Sum('kwh_total_billed'))['kwh_total_billed__sum'] or 0
    total_billed_cost = billing_records_queryset.aggregate(Sum('total_cost'))['total_cost__sum'] or 0

    # Exemplo de cálculo de custo médio por kWh
    avg_cost_per_kwh = (total_billed_cost / total_billed_kwh) if total_billed_kwh > 0 else 0

    # Calcular impostos totais
    total_icms = billing_records_queryset.aggregate(Sum('icms_value'))['icms_value__sum'] or 0
    total_pis = billing_records_queryset.aggregate(Sum('pis_value'))['pis_value__sum'] or 0
    total_cofins = billing_records_queryset.aggregate(Sum('cofins_value'))['cofins_value__sum'] or 0
    total_cip = billing_records_queryset.aggregate(Sum('cip_cost'))['cip_cost__sum'] or 0

    return {
        'total_billed_kwh': round(total_billed_kwh, 2),
        'total_billed_cost': round(total_billed_cost, 2),
        'avg_cost_per_kwh': round(avg_cost_per_kwh, 4),
        'total_icms': round(total_icms, 2),
        'total_pis': round(total_pis, 2),
        'total_cofins': round(total_cofins, 2),
        'total_cip': round(total_cip, 2),
    }


def analyze_device_usage_patterns(profile_device_instance):
    """
    Analisa os padrões de uso horário de um dispositivo em um perfil.
    Retorna dados para um gráfico de barras horárias.
    """
    usage_patterns = DeviceUsagePattern.objects.filter(profile_device=profile_device_instance).order_by('hour_of_day')
    
    if not usage_patterns.exists():
        return None, "Nenhum padrão de uso horário registrado para este dispositivo."

    hours = [p.hour_of_day for p in usage_patterns]
    percentages = [float(p.usage_percentage) for p in usage_patterns]

    fig = go.Figure(data=[
        go.Bar(x=hours, y=percentages)
    ])
    fig.update_layout(
        title_text=f'Padrão de Uso Horário para {profile_device_instance.device.name}',
        xaxis_title='Hora do Dia',
        yaxis_title='Porcentagem de Uso (%)',
        template="plotly_white",
        margin=dict(l=0, r=0, t=40, b=0),
        height=300
    )
    return fig.to_json(), None

def get_prediction_comparison_analytics(profile, limit=None):
    """
    Compara previsões históricas com consumo real para um perfil,
    gera um gráfico de linha e calcula métricas de erro (MAPE, RMSE).

    Args:
        profile: O objeto do modelo Profile para o qual as comparações serão recuperadas.
        limit (int, opcional): O número máximo de comparações históricas mais recentes a serem retornadas.
                                Se None, todas as comparações serão retornadas.

    Returns:
        Um dicionário contendo:
        - 'chart_json': String JSON do gráfico Plotly de comparação de previsões.
        - 'metrics': Dicionário com as métricas de erro (MAPE, RMSE) e o número de comparações.
        - 'message': Uma mensagem informativa (por exemplo, se não houver dados).
    """
    # Consulta base para todas as comparações históricas do perfil, ordenadas pela data
    comparisons_queryset = HistoricalPredictionComparison.objects.filter(profile=profile).order_by('comparison_date')

    if limit is not None and limit > 0:
        # Se um limite for especificado, reverta a ordem para pegar os mais recentes
        comparisons_queryset = HistoricalPredictionComparison.objects.filter(profile=profile).order_by('-comparison_date')[:limit]

    if not comparisons_queryset.exists():
        return {
            'chart_json': None,
            'metrics': {'MAPE': 'N/A', 'RMSE': 'N/A', 'num_comparisons': 0},
            'message': "Nenhuma comparação histórica de previsão disponível para este perfil."
        }

    # Converta a queryset para um DataFrame pandas
    # Usamos 'prediction__predicted_kwh' para acessar o valor previsto do objeto Prediction relacionado
    df = pd.DataFrame(list(comparisons_queryset.values(
        'comparison_date',
        'prediction__predicted_kwh', # Acessa o campo 'predicted_kwh' do modelo 'Prediction' relacionado
        'actual_kwh'
    ))).rename(columns={'prediction__predicted_kwh': 'predicted_kwh'}) # Renomeia para 'predicted_kwh' para consistência

    df['comparison_date'] = pd.to_datetime(df['comparison_date'])
    df = df.sort_values('comparison_date') # Garante que os dados estão ordenados para o gráfico

    # --- Geração do Gráfico Plotly ---
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['comparison_date'], y=df['predicted_kwh'], mode='lines+markers', name='Previsto'))
    fig.add_trace(go.Scatter(x=df['comparison_date'], y=df['actual_kwh'], mode='lines+markers', name='Real'))

    fig.update_layout(
        title_text='Previsão vs. Consumo Real Histórico',
        xaxis_title='Data',
        yaxis_title='Consumo (kWh)',
        template="plotly_white",
        margin=dict(l=0, r=0, t=40, b=0),
        height=300
    )
    chart_json = fig.to_json()

    df['actual_kwh'] = pd.to_numeric(df['actual_kwh'], errors='coerce')
    df['predicted_kwh'] = pd.to_numeric(df['predicted_kwh'], errors='coerce')

    # --- Cálculo de Métricas de Erro (MAPE, RMSE) ---
    actual_positive = df[df['actual_kwh'] != 0] # Filtra valores reais não zero para MAPE

    # MAPE (Mean Absolute Percentage Error)
    # Retorna np.nan se não houver valores reais positivos para evitar divisão por zero
    if not actual_positive.empty:
        mape = np.mean(np.abs((actual_positive['actual_kwh'] - actual_positive['predicted_kwh']) / actual_positive['actual_kwh'])) * 100
    else:
        mape = np.nan

    # RMSE (Root Mean Squared Error)
    rmse = np.sqrt(np.mean((df['actual_kwh'] - df['predicted_kwh'])**2))

    metrics = {
        'MAPE': round(mape, 2) if not np.isnan(mape) else "N/A",
        'RMSE': round(rmse, 2) if not np.isnan(rmse) else "N/A",
        'num_comparisons': len(df)
    }

    return {
        'chart_json': chart_json,
        'metrics': metrics,
        'message': f"Análise de {len(df)} comparações de previsão histórica concluída."
    }

# ALERTS


def check_consumption_goal_alerts(profile):
    """
    Verifica se alguma meta de consumo ativa está próxima de ser ou foi excedida.
    """
    brazil_tz = get_brazil_timezone()
    today = datetime.now(brazil_tz).date()
    
    # Busca metas ativas para o perfil
    active_goals = ConsumptionGoal.objects.filter(
        profile=profile,
        start_date__lte=today,
        end_date__gte=today,
        is_active=True
    )

    for goal in active_goals:
        # Calcula o consumo atual no período da meta
        current_consumption = EnergyReading.objects.filter(
            profile=profile,
            reading_datetime__date__gte=goal.start_date,
            reading_datetime__date__lte=today
        ).aggregate(total=Sum('total_kwh_consumption'))['total'] or Decimal('0.0')

        # Calcula a porcentagem do progresso da meta
        progress_percentage = 0
        if goal.target_kwh and goal.target_kwh > 0:
            progress_percentage = (current_consumption / goal.target_kwh) * 100

        # Condição de Alerta: Se o progresso ultrapassou o limiar definido na meta
        if progress_percentage >= goal.alert_threshold_percentage:
            # Verifica se já existe um alerta similar e não resolvido para evitar duplicatas
            existing_alert = Alert.objects.filter(
                profile=profile,
                alert_type=Alert.AlertTypeChoices.GOAL_THRESHOLD_REACHED,
                related_goal=goal, # Supondo que você adicione um FK para 'goal' no modelo Alert
                is_resolved=False
            ).exists()

            if not existing_alert:
                message = (
                    f"Atenção: Você atingiu {progress_percentage:.2f}% da sua meta de consumo "
                    f"'{goal.name}' ({current_consumption:.2f} de {goal.target_kwh} kWh)."
                )
                alert = Alert.objects.create(
                    profile=profile,
                    user=profile.user,
                    alert_type=Alert.AlertTypeChoices.GOAL_THRESHOLD_REACHED,
                    severity=Alert.AlertSeverityChoices.MEDIUM,
                    message=message,
                    # Adicione o related_goal=goal aqui
                )
                send_alert_notification(alert) # Função para enviar e-mail (próximo passo)


def check_energy_quality_alerts(profile):
    """
    Verifica se houve um número excessivo de interrupções de energia recentemente.
    """
    # Define o período de análise (ex: últimos 7 dias)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # Define o limiar (ex: mais de 3 interrupções em 7 dias é um problema)
    INTERRUPTION_THRESHOLD = 3


    interruption_count = EnergyReading.objects.filter(
        profile=profile,
        reading_datetime__range=[start_date, end_date],
        quality_of_service__in=['INTERRUPTION', 'VOLTAGE_FLUCTUATION'] 
    ).count()

    if interruption_count >= INTERRUPTION_THRESHOLD:
        recent_quality_alert_exists = Alert.objects.filter(
            profile=profile,
            alert_type=Alert.AlertTypeChoices.QUALITY_ISSUE,
            triggered_at__gte=start_date,
            is_resolved=False
        ).exists()

        if not recent_quality_alert_exists:
            message = (
                f"Notamos {interruption_count} problemas de qualidade de energia (interrupções/flutuações) "
                f"nos últimos 7 dias. Se o problema persistir, contate sua concessionária."
            )
            
            alert = Alert.objects.create(
                profile=profile,
                user=profile.user,
                alert_type=Alert.AlertTypeChoices.QUALITY_ISSUE,
                severity=Alert.AlertSeverityChoices.MEDIUM,
                message=message
            )
            
            # Dispara as notificações
            send_alert_notification(alert)
            print(f"Alerta de qualidade de energia criado para o perfil {profile.name}.")



def check_high_consumption_outliers(profile):
    """
    Usa a detecção de outliers para identificar e alertar sobre picos de consumo anormais.
    """
    # A função get_outlier_detection_chart_data já retorna os dados necessários.
    # Vamos assumir que ela retorna um dicionário incluindo uma lista de outliers.
    # Ex: {'outliers': [{'reading_datetime': dt, 'value': val}, ...], 'num_outliers': N}
    outlier_data = get_outlier_detection_chart_data(profile) 

    if outlier_data and outlier_data.get('num_outliers', 0) > 0:
        # Pega o outlier mais recente para o alerta
        latest_outlier = outlier_data['outliers'][-1]
        outlier_datetime = latest_outlier['reading_datetime']
        outlier_value = latest_outlier['value']

        # Para evitar spam, só cria um alerta se não houver um alerta de outlier recente (nas últimas 24h)
        recent_outlier_alert_exists = Alert.objects.filter(
            profile=profile,
            alert_type=Alert.AlertTypeChoices.OUTLIER_DETECTED,
            triggered_at__gte=datetime.now() - timedelta(hours=24),
            is_resolved=False
        ).exists()

        if not recent_outlier_alert_exists:
            message = (
                f"Detectamos um pico de consumo incomum de {outlier_value:.2f} kWh "
                f"em {outlier_datetime.strftime('%d/%m/%Y às %H:%M')}. "
                f"Recomendamos verificar seus aparelhos."
            )
            
            alert = Alert.objects.create(
                profile=profile,
                user=profile.user,
                alert_type=Alert.AlertTypeChoices.OUTLIER_DETECTED,
                severity=Alert.AlertSeverityChoices.HIGH, # Picos de consumo são de alta severidade
                message=message
            )
            
            # Dispara as notificações (E-mail, Push, SMS)
            send_alert_notification(alert)
            print(f"Alerta de pico de consumo criado para o perfil {profile.name}.")

def check_and_create_alerts_for_profile(profile):
    """
    Função orquestradora que verifica todas as condições de alerta para um perfil.
    """
    print(f"Verificando alertas para o perfil: {profile.name}")
    check_consumption_goal_alerts(profile)
    check_high_consumption_outliers(profile)
    check_energy_quality_alerts(profile)


def send_alert_notification(alert):
    """
    Envia uma notificação por e-mail para o usuário associado ao alerta.
    """
    user = alert.profile.user
    user_prefs = getattr(user, 'preferences', None)

    if not user.email:
        print(f"Usuário {user.username} não possui e-mail para notificação.")
        return

    subject = f"[KIREM] Alerta de Energia: {alert.get_alert_type_display()}"
    context = {'alert': alert, 'user': user}
    
    # Renderiza um template de texto e HTML para o e-mail
    text_message = render_to_string('emails/alert_notification.txt', context)
    html_message = render_to_string('emails/alert_notification.html', context)
    
    try:
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"E-mail de alerta enviado para {user.email}")
    except Exception as e:
        print(f"Falha ao enviar e-mail de alerta: {e}")

    if user_prefs and user_prefs.receive_sms_notifications:
        send_sms_notification(alert)


    if user_prefs and user_prefs.receive_push_notifications:
        send_push_notification(alert)



def generate_dynamic_recommendations(profile):
    """
    Analisa os dados de um perfil e cria sugestões de otimização personalizadas.
    """
    print(f"Gerando recomendações dinâmicas para o perfil: {profile.name}")

    # 1. Sugestão baseada no maior consumidor
    profile_devices = profile.profile_devices.select_related('device').all()
    benchmark_data = calculate_benchmark_data(profile_devices) #
    highest_consumer = benchmark_data.get('highest_consumer')

    if highest_consumer:
        title = f"Foco no Maior Consumidor: {highest_consumer['name']}"
        # Evita criar sugestões duplicadas
        if not OptimizationSuggestion.objects.filter(profile=profile, title=title).exists():
            description = (
                f"Seu dispositivo '{highest_consumer['name']}' é o maior consumidor de energia, "
                f"com {highest_consumer['daily_kwh']:.2f} kWh/dia. "
                f"Reduzir seu tempo de uso ou verificar sua eficiência pode gerar economias significativas."
            )
            OptimizationSuggestion.objects.create(
                profile=profile,
                title=title,
                description=description,
                category=OptimizationSuggestion.CategoryChoices.EQUIPAMENTOS,
                impact_level=OptimizationSuggestion.ImpactChoices.HIGH
            )

    # 2. Sugestão baseada em dispositivos ineficientes (Selo Procel)
    inefficient_devices = profile_devices.filter(device__procel_seal__in=['C', 'D', 'E'])
    
    for pd_instance in inefficient_devices:
        title = f"Avalie a Troca do Dispositivo: {pd_instance.device.name}"
        if not OptimizationSuggestion.objects.filter(profile=profile, title=title).exists():
            # Simulação de economia: um aparelho A gasta ~50% de um C/D/E
            potential_savings = (pd_instance.monthly_kwh_consumption or 0) * Decimal('0.5')
            description = (
                f"Seu dispositivo '{pd_instance.device.name}' possui um selo Procel '{pd_instance.device.procel_seal}', "
                f"indicando baixa eficiência. Substituí-lo por um modelo 'A' poderia economizar "
                f"aproximadamente {potential_savings:.2f} kWh por mês."
            )
            OptimizationSuggestion.objects.create(
                profile=profile,
                title=title,
                description=description,
                category=OptimizationSuggestion.CategoryChoices.APPLIANCES,
                impact_level=OptimizationSuggestion.ImpactChoices.MEDIUM,
                estimated_savings_kwh_per_month=potential_savings,
                procel_seal_target='A'
            )



def generate_custom_report(profile, start_date, end_date, metrics, report_format):
    """
    Coleta dados e gera um relatório em PDF ou CSV.
    """
    # Coleta de dados com base nas métricas
    report_data = {'profile': profile, 'start_date': start_date, 'end_date': end_date}
    
    readings = EnergyReading.objects.filter(
        profile=profile, reading_datetime__date__range=[start_date, end_date]
    )
    
    if 'total_consumption' in metrics:
        total_kwh = readings.aggregate(Sum('total_kwh_consumption'))['total_kwh_consumption__sum'] or 0
        report_data['total_consumption'] = total_kwh


    if report_format == 'csv':
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Metrica', 'Valor'])
        if 'total_consumption' in report_data:
            writer.writerow(['Consumo Total (kWh)', f"{report_data['total_consumption']:.2f}"])
        # ...
        
        filename = f"relatorio_{profile.name}_{start_date}_a_{end_date}.csv"
        return output.getvalue(), filename

    elif report_format == 'pdf':
        # Renderiza um template HTML com os dados
        html_string = render_to_string('reports/template.html', {'data': report_data})
        
        # Gera o PDF a partir do HTML
        pdf_file = HTML(string=html_string).write_pdf()
        filename = f"relatorio_{profile.name}_{start_date}_a_{end_date}.pdf"
        return pdf_file, filename

    return None, None


def send_sms_notification(alert):
    """
    Envia um SMS usando a API do Twilio.
    """
    user_prefs = getattr(alert.profile.user, 'preferences', None)
    if not (user_prefs and user_prefs.phone_number):
        print(f"SMS não enviado para {alert.profile.user.username}: número de telefone não cadastrado.")
        return

    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message_body = f"[KIREM Alerta] {alert.message}"

        message = client.messages.create(
            body=message_body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=str(user_prefs.phone_number)
        )
        print(f"SMS enviado para {user_prefs.phone_number}. SID: {message.sid}")
    except Exception as e:
        print(f"Falha ao enviar SMS para {user_prefs.phone_number}: {e}")


def send_push_notification(alert):
    """
    Envia uma notificação push para todos os dispositivos/navegadores
    assinados pelo usuário.
    """
    try:
        payload = {
            "head": f"Alerta KIREM: {alert.get_severity_display()}",
            "body": alert.message,
            "icon": "https://sua-url.com/static/assets/img/logo-ct-dark.png", # URL para seu ícone
            "url": f"/alerts/{alert.id}/" # URL para onde o usuário será direcionado ao clicar
        }
        send_user_notification(user=alert.profile.user, payload=payload, ttl=1000)
        print(f"Notificação push enviada para o usuário {alert.profile.user.username}")
    except Exception as e:
        print(f"Falha ao enviar notificação push: {e}")