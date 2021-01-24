from django.shortcuts import render
import redis
from django.conf import settings
from django.http import JsonResponse

r = redis.StrictRedis(host=settings.REDIS_HOST,
                                  port=settings.REDIS_PORT, db=0)
# Create your views here.

def index(request):
    return render(request,'apis/index.html')

def get_sc_name(request,sc_name=''):
    data = []
    for i in r.scan_iter( match='*'+sc_name.upper()+'*', count=100000000):
        data.append( r.get(i).decode().split(','))

    return JsonResponse(data,safe=False)

def get_header(request):
    data = r.get('header').decode().split(',')
    return JsonResponse(data,safe=False)