from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

celery_app = Celery(
    'analizator_deszczowki',
    broker=broker_url,
    backend=result_backend,
    include=['backend.app.tasks.alert_tasks', 'backend.app.tasks.analysis_tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

celery_app.conf.beat_schedule = {
    'check-alerts-every-5-minutes': {
        'task': 'backend.app.tasks.alert_tasks.check_all_user_device_alerts',
        'schedule': 300.0,
        'args': (1,)
    },
    'generate-analysis-reports-every-hour': {
        'task': 'backend.app.tasks.analysis_tasks.generate_periodic_analysis_report',
        'schedule': 3600.0,
        'args': (1,)
    }
}