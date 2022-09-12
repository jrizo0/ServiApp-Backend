from django.urls import path

from .views import UsuarioAPIView

app_name = 'usuarios'

usu_get = UsuarioAPIView.as_view({"get": "retrieve"})

urlpatterns = [
    path("", usu_get),
    # path('get/', views.getClientes, name='getClientes'),
]
