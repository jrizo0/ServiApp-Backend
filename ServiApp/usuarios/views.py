from rest_framework import viewsets

import requests

from rest_framework.response import Response

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers

from ServiApp.firebase import db, firestore, fb_valid_req_token_uid, auth
from django.conf import settings
from django.core.exceptions import PermissionDenied

API_Clientes = settings.SA_API_URL + "/clientes/"


class UsuarioAPIView(
    viewsets.GenericViewSet,
):
    def __init__(self):
        self.enable_auth = False

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
        uid = self.request.query_params.get("uid")
        if self.enable_auth and not fb_valid_req_token_uid(self.request, uid):
            raise PermissionDenied()
        return Response(self.get_queryset())

    def add_prod_cart(self, request, id_prod):
        uid = self.request.query_params.get("uid")
        if self.enable_auth and not fb_valid_req_token_uid(self.request, uid):
            raise PermissionDenied()
        user = db.collection("Usuario").document(uid).get().to_dict()
        user["Carro"].append(id_prod)
        db.collection("Usuario").document(uid).update(user)
        # return Response(self.get_queryset())
        return Response(self.get_queryset()["Carro"])

    def del_prod_cart(self, request, id_prod):
        uid = self.request.query_params.get("uid")
        if self.enable_auth and not fb_valid_req_token_uid(self.request, uid):
            raise PermissionDenied()
        user = db.collection("Usuario").document(uid).get().to_dict()
        if user["Carro"].count(id_prod) != 0:
            user["Carro"].remove(id_prod)
            db.collection("Usuario").document(uid).update(user)
        # return Response(self.get_queryset())
        return Response(self.get_queryset()["Carro"])

    def remove_prod_cart(self, request, id_prod):
        uid = self.request.query_params.get("uid")
        if self.enable_auth and not fb_valid_req_token_uid(self.request, uid):
            raise PermissionDenied()
        db.collection("Usuario").document(uid).update(
            {"Carro": firestore.ArrayRemove([id_prod])}
        )
        # return Response(self.get_queryset())
        return Response(self.get_queryset()["Carro"])

    def clear_cart(self, request):
        uid = self.request.query_params.get("uid")
        if self.enable_auth and not fb_valid_req_token_uid(self.request, uid):
            raise PermissionDenied()
        user = db.collection("Usuario").document(uid).get().to_dict()
        user["Carro"].clear()
        db.collection("Usuario").document(uid).update(user)
        # return Response(self.get_queryset())
        return Response(self.get_queryset()["Carro"])

    # TODO: Donde guardar factura
    def pay_cart(self, request):
        return Response(self.get_queryset())

    # TODO: Donde modificar el nombre
    def change_name(self, request):
        uid = self.request.query_params.get("uid")
        if self.enable_auth and not fb_valid_req_token_uid(self.request, uid):
            raise PermissionDenied()
        new_name = request.data.get("new_name")
        print(new_name)
        return Response(self.get_queryset())

    def change_pass(self, request):
        uid = self.request.query_params.get("uid")
        if self.enable_auth and not fb_valid_req_token_uid(self.request, uid):
            raise PermissionDenied()
        new_pass = request.data.get("new_pass")
        user = auth.update_user(uid, password=new_pass)
        return Response({"msg": "Sucessfully updated user: {0}".format(user.uid)})
