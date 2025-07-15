from celery import shared_task
from decimal import Decimal
import pandas as pd
from plotly import graph_objects as go
from .utils import _linear_regression_forecast # Importe a função auxiliar
try:
    from prophet import Prophet
except ImportError:
    Prophet = None

# Importe os modelos necessários
from .models import EnergyProfiles, PredictionModels, EnergyReading, BillingRecord, ConsumptionPredictions, ProfileDevices

@shared_task(bind=True)
def generate_forecast_for_profile(self, profile_id, model_id, periods=30):
    """
    Tarefa Celery para gerar e salvar previsões de consumo para um perfil.
    Recebe IDs em vez de objetos de modelo, que é uma prática recomendada para tarefas assíncronas.
    """
    try:
        profile = EnergyProfiles.objects.get(pk=profile_id)
        model = PredictionModels.objects.get(pk=model_id)
        
        # O resto da lógica é muito similar à sua função original em utils.py
        # --- Passo 1: Obter e validar dados ---
        if model.data_source == 'readings':
            queryset = EnergyReading.objects.filter(profile=profile).order_by('reading_datetime')
            date_field, value_field = 'reading_datetime', 'total_kwh_consumption'
        elif model.data_source == 'billing':
            queryset = BillingRecord.objects.filter(profile=profile).order_by('invoice_date')
            date_field, value_field = 'invoice_date', 'kwh_total_billed'
        else:
            # Retornar um status de falha com uma mensagem de erro
            self.update_state(state='FAILURE', meta={'error': f"Fonte de dados '{model.data_source}' desconhecida."})
            return {'error_message': f"Fonte de dados '{model.data_source}' desconhecida."}

        if queryset.count() < 5:
            self.update_state(state='FAILURE', meta={'error': "Dados históricos insuficientes."})
            return {'error_message': "Dados históricos insuficientes para gerar uma previsão."}

        df = pd.DataFrame(list(queryset.values(date_field, value_field)))
        df = df.rename(columns={date_field: 'ds', value_field: 'y'})
        df['ds'] = pd.to_datetime(df['ds']).dt.tz_localize(None)
        df['y'] = pd.to_numeric(df['y'], errors='coerce')
        df = df.groupby(df['ds'].dt.date).agg(y=('y', 'sum')).reset_index()
        df['ds'] = pd.to_datetime(df['ds'])

        # --- Passo 2: Executar o algoritmo ---
        if model.model_type == 'PROPHET':
            # Lógica do Prophet...
            prophet_model = Prophet(
                yearly_seasonality=model.yearly_seasonality,
                weekly_seasonality=model.weekly_seasonality,
                daily_seasonality=model.daily_seasonality,
                seasonality_mode=model.seasonality_mode,
            )
            if model.include_brazil_holidays:
                prophet_model.add_country_holidays(country_name='BR')
            
            prophet_model.fit(df)
            future = prophet_model.make_future_dataframe(periods=periods)
            forecast = prophet_model.predict(future)
            
            # --- Passo 3: Salvar os resultados (parte importante) ---
            default_profile_device = ProfileDevices.objects.filter(profile=profile).first()
            if not default_profile_device:
                self.update_state(state='FAILURE', meta={'error': "Nenhum dispositivo encontrado no perfil para associar a previsão."})
                return {'error_message': "Nenhum dispositivo encontrado no perfil."}

            for index, row in forecast.iterrows():
                if row['ds'] > df['ds'].max(): # Salvar apenas as datas futuras
                    prediction_date_obj = row['ds'].date()
                    ConsumptionPredictions.objects.update_or_create(
                        profile=profile,
                        prediction_date=prediction_date_obj,
                        defaults={
                            'profile_device': default_profile_device,
                            'model': model,
                            'predicted_kwh': Decimal(str(row.get('yhat', 0.0))),
                            'predicted_daily_kwh': Decimal(str(row.get('yhat', 0.0))),
                            'is_final': True,
                        }
                    )
            
            return {'message': f'Previsão para o perfil "{profile.name}" concluída e salva com sucesso.'}

        else:
            self.update_state(state='FAILURE', meta={'error': f"Tipo de modelo '{model.model_type}' não implementado na tarefa assíncrona."})
            return {'error_message': f"Modelo '{model.model_type}' não suportado."}
            
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        return {'error_message': str(e)}