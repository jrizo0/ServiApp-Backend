from django.urls import path

from .views import UsuarioAPIView

app_name = "usuarios"

usu_get = UsuarioAPIView.as_view({"get": "retrieve"})

usu_retrieve_cart = UsuarioAPIView.as_view({"get": "retrieve_cart"})
usu_add_prod_cart = UsuarioAPIView.as_view({"post": "add_prod_cart"})
usu_remove_prod_cart = UsuarioAPIView.as_view({"post": "remove_prod_cart"})
usu_clear_cart = UsuarioAPIView.as_view({"post": "clear_cart"})
usu_pay_cart = UsuarioAPIView.as_view({"post": "pay_cart"})

usu_list_cards = UsuarioAPIView.as_view({"get": "list_cards"})
usu_add_card = UsuarioAPIView.as_view({"post": "add_card"})
usu_del_card = UsuarioAPIView.as_view({"delete": "delete_card"})

usu_create = UsuarioAPIView.as_view({"post": "create"})
usu_update = UsuarioAPIView.as_view({"put": "update"})
usu_change_pass = UsuarioAPIView.as_view({"put": "change_pass"})
usu_update_device_token = UsuarioAPIView.as_view({"put": "update_device_token"})

usu_list_orders = UsuarioAPIView.as_view({"get": "list_orders"})
usu_rate_order = UsuarioAPIView.as_view({"post": "rate_order"})
usu_finish_order = UsuarioAPIView.as_view({"post": "finish_order"})

usu_list_delivery = UsuarioAPIView.as_view({"get": "list_delivery"})
usu_accept_delivery = UsuarioAPIView.as_view({"post": "accept_delivery"})
usu_reject_delivery = UsuarioAPIView.as_view({"post": "reject_delivery"})

urlpatterns = [
    path("", usu_get),

    path("cart/", usu_retrieve_cart),
    path("addcart/<str:id_prod>/<int:cant>/<str:id_rest>/<str:delivery>/", usu_add_prod_cart),
    path("removecart/<str:id_prod>/", usu_remove_prod_cart),
    path("clearcart/", usu_clear_cart),
    path("pay/", usu_pay_cart),

    path("cards/", usu_list_cards),
    path("addcard/", usu_add_card),
    path("delcard/", usu_del_card),

    path("create/", usu_create),
    path("update/", usu_update),
    path("changepass/", usu_change_pass),
    path("dt/", usu_update_device_token),

    path("orders/<str:role>/<int:delivery>/", usu_list_orders),
    path("rateorder/", usu_rate_order),

    path("delivery/", usu_list_delivery),
    path("acceptdelivery/", usu_accept_delivery),
    path("rejectdelivery/", usu_reject_delivery),
]
