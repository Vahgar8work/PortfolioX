import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('portfoliox')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'daily-analysis-job': {
        'task': 'analytics.tasks.daily_batch_job',
        'schedule': crontab(hour=22, minute=0),
    },
    'update-portfolio-values': {
        'task': 'analytics.tasks.update_portfolio_values',
        'schedule': crontab(hour='*/6'),
    },
}

app.conf.timezone = 'Asia/Kolkata'
