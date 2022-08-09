from django.urls import path, include
from . import views

urlpatterns = [
    path('productos/', include('productos.urls')),
]
