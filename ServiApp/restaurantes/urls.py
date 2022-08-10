from django.urls import path

from . import views

app_name = 'restaurantes'
urlpatterns = [
    path('get/', views.getRestaurantes, name='getRestaurantes'),
]
