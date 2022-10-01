from django.urls import path

from .views import UsuarioAPIView

app_name = "usuarios"

usu_get = UsuarioAPIView.as_view({"get": "retrieve"})

usu_retrieve_cart = UsuarioAPIView.as_view({"get": "retrieve_cart"})
usu_add_prod_cart = UsuarioAPIView.as_view({"post": "add_prod_cart"})
usu_remove_prod_cart = UsuarioAPIView.as_view({"post": "remove_prod_cart"})
usu_clear_cart = UsuarioAPIView.as_view({"post": "clear_cart"})
usu_add_card = UsuarioAPIView.as_view({"post": "add_card"})

# usu_pay_cart = UsuarioAPIView.as_view({"post": "pay_cart"})
# usu_change_name = UsuarioAPIView.as_view({"put": "change_name"})
usu_change_pass = UsuarioAPIView.as_view({"put": "change_pass"})

urlpatterns = [
    path("", usu_get),
    path("cart/", usu_retrieve_cart),
    path("addcart/<str:id_prod>/<int:cant>/<str:id_rest>/", usu_add_prod_cart),
    path("removecart/<str:id_prod>/", usu_remove_prod_cart),
    path("clearcart/", usu_clear_cart),
    path("addcard/", usu_add_card),
    # path("pay/", usu_pay_cart),
    # path("changename/", usu_change_name),
    path("changepass/", usu_change_pass),
]
