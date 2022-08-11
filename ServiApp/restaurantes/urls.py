from django.urls import path

from . import views

app_name = 'restaurantes'
urlpatterns = [
    path('getTarifasv', views.getTarifasv, name='getTarifasv'),
    path('getTarifas', views.getTarifas, name='getTarifas'),
]
