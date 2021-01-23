import os

from celery import Celery
from celery.schedules import crontab
import redis
from django.conf import settings
from celery.utils.log import get_task_logger

import datetime
import requests
import pandas as pd
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bhavcopy.settings')

app = Celery('bhavcopy',broker=settings.BROKER_URL)
logger = get_task_logger(__name__)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(settings.INSTALLED_APPS)

@app.task
def get_new_data():
    # do something
    print('start')
    r = redis.StrictRedis(host=settings.REDIS_HOST,
                                  port=settings.REDIS_PORT, db=0)
    for key in r.scan_iter("prefix:*"):
        r.delete(key)
    get_date = datetime.datetime.now().strftime("%d%m%y")

    url = 'https://www.bseindia.com/download/BhavCopy/Equity/EQ'+get_date+'_CSV.ZIP'
    header = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
            }
    print(url)
    rq = requests.get(url, headers=header)
    with open('/tmp/EQ'+get_date+'_CSV.ZIP', 'wb') as fd:
        fd.write(rq.content)

    df = pd.read_csv('/tmp/EQ'+get_date+'_CSV.ZIP',compression='zip')
    r.set('header',','.join([i for i in df.columns]))
    df = df.astype(str)
    for i in df.iloc():
        r.set(i.SC_NAME,','.join(
                            [i.SC_CODE,i.SC_NAME,i.SC_GROUP,i.SC_TYPE,i.OPEN,
                            i.HIGH,i.CLOSE,i.LAST,i.PREVCLOSE,i.NO_TRADES,i.NO_OF_SHRS,
                            i.NET_TURNOV,i.NET_TURNOV,i.TDCLOINDI]))

    r.close()
    print('Done')

app.conf.beat_schedule = {

    'add-data': {
        'task': 'bhavcopy.celery.get_new_data',
        'schedule': crontab(hour=18, minute=2, day_of_week='1-5'),
    },
}



