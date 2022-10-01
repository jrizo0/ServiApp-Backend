from requests.adapters import ResponseError
from requests.sessions import Request
from rest_framework import viewsets

import requests

from rest_framework.response import Response
from rest_framework.permissions import SAFE_METHODS, BasePermission

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers

from ServiApp.firebase import db, firestore, fb_valid_req_token_uid, auth
from django.conf import settings
from django.core.exceptions import PermissionDenied

API_Clientes = settings.SA_API_URL + "/clientes"
API_Tarifas = settings.SA_API_URL + "/tarifas"


class FBUserRequestAuthenticated(BasePermission):
    def __init__(self):
        self.enable_auth = False

    def has_permission(self, request, view):
        if self.enable_auth and not fb_valid_req_token_uid(request):
            raise PermissionDenied()
        return True


class UsuarioAPIView(viewsets.GenericViewSet):
    permission_classes = [FBUserRequestAuthenticated]

    def get_queryset(self):
        uid = self.request.query_params.get("uid")
        res = db.collection("Usuario").document(uid).get()
        if not res.exists:
            return []
        return res.to_dict()

    # @method_decorator(vary_on_headers("Authorization"))
    # @method_decorator(vary_on_cookie)
    # @method_decorator(cache_page(60 * 1))
    def retrieve(self, request):
        return Response(self.get_queryset())

    def retrieve_cart(self, request):
        uid = self.request.query_params.get("uid")
        prods_in_cart = db.collection("Carro").where("Usuario", "==", uid).get()
        if len(prods_in_cart) == 0:
            return Response({"Restaurante": "", "Productos": []})
        cart_w_info = []
        for prod in prods_in_cart:
            prod = prod.to_dict()
            prod_info = db.collection("Producto").document(prod["Producto"]).get()
            prod_info = {"id": prod_info.id} | prod_info.to_dict()
            cart_w_info.append(prod_info | prod)
        usu = self.get_queryset()
        rest_cart = usu["RestauranteCarro"]
        rest_cart_info = db.collection("Restaurante").document(rest_cart).get()
        return Response({"Restaurante": rest_cart_info.to_dict(), "Productos": cart_w_info})

    def add_prod_cart(self, request, id_prod, cant, id_rest):
        uid = self.request.query_params.get("uid")
        user = db.collection("Usuario").document(uid).get().to_dict()
        if user["RestauranteCarro"] != "" and id_rest != user["RestauranteCarro"]:
            return ResponseError()
        if user["RestauranteCarro"] == "":
            db.collection("Usuario").document(uid).update({"RestauranteCarro": id_rest})

        same_prods_in_cart = (
            db.collection("Carro")
            .where("Usuario", "==", uid)
            .where("Producto", "==", id_prod)
            .get()
        )
        for prod in same_prods_in_cart:
            db.collection("Carro").document(prod.id).delete()

        tarifa = requests.get(f"{API_Tarifas}/{id_rest}/{id_prod}/").json()
        data = {
            "Cantidad": cant,
            "Precio": tarifa["precio"],
            "Producto": id_prod,
            "Usuario": uid,
        }
        db.collection("Carro").add(data)
        return Response()

    def remove_prod_cart(self, request, id_prod):
        uid = self.request.query_params.get("uid")
        prod_in_cart = (
            db.collection("Carro")
            .where("Usuario", "==", uid)
            .where("Producto", "==", id_prod)
            .get()
        )
        for prod in prod_in_cart:
            db.collection("Carro").document(prod.id).delete()

        user_cart = db.collection("Carro").where("Usuario", "==", uid).get()
        if len(user_cart) == 0:
            db.collection("Usuario").document(uid).update({"RestauranteCarro": ""})

        return Response()

    def clear_cart(self, request):
        uid = self.request.query_params.get("uid")
        prod_in_cart = db.collection("Carro").where("Usuario", "==", uid).get()
        for prod in prod_in_cart:
            db.collection("Carro").document(prod.id).delete()
        db.collection("Usuario").document(uid).update({"RestauranteCarro": ""})
        return Response()

    # TODO: deja guardar tarjetas repetidas.
    def add_card(self, request):
        uid = self.request.query_params.get("uid")
        db.collection("Tarjeta").add({"Usuario": uid} | request.data)
        return Response()

    # TODO: Donde guardar factura.
    def pay_cart(self, request):
        return Response(self.get_queryset())

    # TODO: Donde modificar el nombre.
    def change_name(self, request):
        new_name = request.data.get("new_name")
        print(new_name)
        return Response(self.get_queryset())

    def change_pass(self, request):
        uid = self.request.query_params.get("uid")
        new_pass = request.data.get("new_pass")
        user = auth.update_user(uid, password=new_pass)
        return Response({"msg": "Sucessfully updated user: {0}".format(user.uid)})
