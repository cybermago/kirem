import os
from celery import Celery

# Define a variável de ambiente para as configurações do Django para o Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Cria a instância do aplicativo Celery
app = Celery('config')

# O Celery usará o prefixo 'CELERY_' para todas as suas variáveis de configuração
# que estão no settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobre e carrega automaticamente as tarefas de todos os aplicativos registrados no Django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')