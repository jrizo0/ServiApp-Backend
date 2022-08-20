from django.urls import path

from . import views

app_name = 'restaurantes'
urlpatterns = [
    path('getRestaurantes', views.getTarifasv, name='getTarifasv'),
    path('getRestaurante/<int:id>', views.getTarifasvId, name='getTarifasvId'),
    path('postRestaurante', views.postTarifasv, name='postTarifasv'),
    path('putRestaurante/<int:id>', views.putTarifasv, name='putTarifasv'),
    path('deleteRestaurante/<int:id>', views.deleteTarifasv, name='deleteTarifasv'),

    path('getTarifas', views.getTarifas, name='getTarifas'),
    path('getTarifa/<int:pk>', views.getTarifa, name='getTarifa'),
    path('createTarifa', views.createTarifa, name='createTarifa'),
    path('updateTarifa/<int:pk>', views.updateTarifa, name='updateTarifa'),
    path('deleteTarifa/<int:pk>', views.deleteTarifa, name='deleteTarifa'),
]
