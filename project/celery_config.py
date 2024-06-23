from celery import Celery
import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('project')

app.config_from_object('django.conf:settings', namespace='CELERY')


"""

# This config is needed for priortizing tasks

app.conf.broker_transport_options = {
     'priority_steps': list(range(10)),
     'sep': ':',
     'queue_order_strategy': 'priority',
} 

"""


# app.conf.task_default_rate_limit = '1/m'

app.autodiscover_tasks()