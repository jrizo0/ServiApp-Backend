from django.urls import path

from .views import UsuarioAPIView

app_name = "usuarios"

usu_get = UsuarioAPIView.as_view({"get": "retrieve"})

usu_list_cards = UsuarioAPIView.as_view({"get": "list_cards"})
usu_add_card = UsuarioAPIView.as_view({"post": "add_card"})
usu_del_card = UsuarioAPIView.as_view({"delete": "delete_card"})

usu_create = UsuarioAPIView.as_view({"post": "create"})
usu_update = UsuarioAPIView.as_view({"put": "update"})
usu_change_pass = UsuarioAPIView.as_view({"put": "change_pass"})
usu_update_device_token = UsuarioAPIView.as_view({"put": "update_device_token"})

urlpatterns = [
    path("", usu_get),

    path("cards/", usu_list_cards),
    path("addcard/", usu_add_card),
    path("delcard/", usu_del_card),

    path("create/", usu_create),
    path("update/", usu_update),
    path("changepass/", usu_change_pass),
    path("dt/", usu_update_device_token),
]
