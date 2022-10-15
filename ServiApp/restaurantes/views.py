from rest_framework import viewsets

import requests

from rest_framework.response import Response
from rest_framework.permissions import SAFE_METHODS, BasePermission

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers

from ServiApp.firebase import db, fb_valid_req_token
from django.conf import settings

from django.core.exceptions import PermissionDenied

from productos.views import list_rest_delivery


API_Restaurantes = settings.SA_API_URL + "/restaurantes"
API_Aforo = settings.AFORO_API_URL + "/aforo"


class FBAuthenticated(BasePermission):
    def __init__(self):
        self.enable_auth = False

    def has_permission(self, request, view):
        return not self.enable_auth or fb_valid_req_token(request)


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class RestauranteAPIView(viewsets.GenericViewSet):
    permission_classes = [ReadOnly | FBAuthenticated]

    def aux_fill_missing_fields(self, rests, fs_query_cats):
        for i in range(len(rests)):
            if rests[i]["Imagen"] != "" and rests[i]["Descripcion"] != "":
                continue
            for doc_cat in fs_query_cats:
                if doc_cat.id != rests[i]["Categoria"][0]:
                    continue
                if rests[i]["Imagen"] == "":
                    rests[i] = rests[i] | {"Imagen": doc_cat.to_dict()["Imagen"]}
                if rests[i]["Descripcion"] == "":
                    rests[i] = rests[i] | {
                        "Descripcion": doc_cat.to_dict()["Descripcion"]
                    }
        return rests

    def get_queryset(self):
        fs_query_rests = db.collection("Restaurante").get()
        fs_query_cats = db.collection("CategoriaRestaurante").get()
        rests = [{"id": doc.id} | doc.to_dict() for doc in fs_query_rests]
        rests = self.aux_fill_missing_fields(rests, fs_query_cats)
        for i in range(len(rests)):
            rest_id = rests[i]["id"]
            aforo = requests.get(f"{API_Aforo}/get/{rest_id}/").json()
            rests[i] = rests[i] | aforo
        return rests

    # @method_decorator(vary_on_cookie)
    @method_decorator(cache_page(60 * 60))
    def list(self, request):
        return Response(self.get_queryset())

    def aforo(self, request, id_rest):
        aforo = requests.get(f"{API_Aforo}/get/{id_rest}/").json()
        return Response(aforo)

    def get_queryset_delivery(self, request):
        fs_query_rests = db.collection("RestauranteDomicilio").get()
        fs_query_cats = db.collection("CategoriaRestaurante").get()
        rests = [{"id": doc.id} | doc.to_dict() for doc in fs_query_rests]
        rests = self.aux_fill_missing_fields(rests, fs_query_cats)
        for i in range(len(rests)):
            rest_id = rests[i]["id"]
            rests[i]["Productos"] = list_rest_delivery(rest_id)
            if len(rests[i]["Productos"]) == 0:
                continue
            aforo = requests.get(f"{API_Aforo}/get/{rest_id}/").json()
            rests[i] = rests[i] | aforo
        rests = [rest for rest in rests if len(rest["Productos"]) > 0]
        return rests

    # @method_decorator(vary_on_cookie)
    @method_decorator(cache_page(60 * 60))
    def list_delivery(self, request):
        return Response(self.get_queryset_delivery(request))
