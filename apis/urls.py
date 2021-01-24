from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView

from .views import *

urlpatterns = [
    path('', index ),
    path('get_sc/<str:sc_name>/', get_sc_name, name='get_sc_name'),
    path('get_sc/', get_sc_name, name='get_sc_name'),
    path('get_header/', get_header, name='get_header'),
]