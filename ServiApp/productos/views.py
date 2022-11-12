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


API_Productos = settings.SA_API_URL + "/productos"
API_Tarifas = settings.SA_API_URL + "/tarifas"


class FBAuthenticated(BasePermission):
    def __init__(self):
        self.enable_auth = False

    def has_permission(self, request, view):
        return not self.enable_auth or fb_valid_req_token(request)


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class ProductosAPIView(viewsets.GenericViewSet):
    permission_classes = [ReadOnly | FBAuthenticated]

    def aux_fill_missing_fields(self, prods, fs_query_cats):
        for i in range(len(prods)):
            if prods[i]["Imagen"] != "" and prods[i]["Descripcion"] != "":
                continue
            for doc_cat in fs_query_cats:
                if doc_cat.id != prods[i]["Categoria"]:
                    continue
                if prods[i]["Imagen"] == "":
                    prods[i] = prods[i] | {"Imagen": doc_cat.to_dict()["Imagen"]}
                if prods[i]["Descripcion"] == "":
                    prods[i] = prods[i] | {
                        "Descripcion": doc_cat.to_dict()["Descripcion"]
                    }
        return prods

    def get_queryset(self):
        fs_query_prods = db.collection("Producto").get()
        fs_query_cats = db.collection("CategoriaProducto").get()
        prods = [{"id": doc.id} | doc.to_dict() for doc in fs_query_prods]
        prods = self.aux_fill_missing_fields(prods, fs_query_cats)
        return prods

    # @method_decorator(vary_on_cookie)
    # @method_decorator(cache_page(30 * 1))
    def list(self, request):
        return Response(self.get_queryset())

    # @method_decorator(vary_on_cookie)
    @method_decorator(cache_page(60 * 60))
    def retrieve(self, request, id_prod, id_rest):
        prod = db.collection("Producto").document(id_prod).get()
        tarifa = requests.get(f"{API_Tarifas}/{id_rest}/{id_prod}/").json()
        data = {"id": prod.id} | prod.to_dict() | {"Precio": tarifa["precio"]}
        return Response(data)

    # @method_decorator(vary_on_headers("Authorization"))
    # @method_decorator(vary_on_cookie)
    @method_decorator(cache_page(60 * 60))
    def list_rest(self, request, id_rest):
        if "20-" in id_rest:
            id_rest = "20"
        tarifas_api = requests.get(f"{API_Tarifas}/tarifav/{id_rest}/").json()
        fs_query_prods = db.collection("Producto").get()
        rests = []
        for prod in fs_query_prods:
            if not prod.id in tarifas_api:
                continue
            rests.append(
                {"id": prod.id}
                | prod.to_dict()
                | {"Precio": tarifas_api[prod.id]["precio"]}
            )
        fs_query_cats = db.collection("CategoriaProducto").get()
        rests = self.aux_fill_missing_fields(rests, fs_query_cats)
        return Response(rests)

    # @method_decorator(vary_on_headers("Authorization"))
    # @method_decorator(vary_on_cookie)
    @method_decorator(cache_page(60 * 60))
    def list_rest_delivery(self, request, id_rest):
        if "20-" in id_rest:
            id_rest = "20"
        tarifas_api = requests.get(f"{API_Tarifas}/tarifav/{id_rest}/").json()
        tarifas_domi_api = requests.get(f"{API_Tarifas}/tarifav/3/").json()
        fs_query_prods = db.collection("Producto").get()
        rests = []
        for prod in fs_query_prods:
            if not prod.id in tarifas_api or not prod.id in tarifas_domi_api:
                continue
            rests.append(
                {"id": prod.id}
                | prod.to_dict()
                | {"Precio": tarifas_api[prod.id]["precio"]}
            )
        fs_query_cats = db.collection("CategoriaProducto").get()
        rests = self.aux_fill_missing_fields(rests, fs_query_cats)
        return Response(rests)


def list_rest(id_rest, fs_query_prods):
    if "20-" in id_rest:
        id_rest = "20"
    tarifas_api = requests.get(f"{API_Tarifas}/tarifav/{id_rest}/").json()
    # fs_query_prods = db.collection("Producto").get()
    rests = []
    for prod in fs_query_prods:
        if not prod.id in tarifas_api:
            continue
        rests.append(
            {"id": prod.id}
            | prod.to_dict()
            | {"Precio": tarifas_api[prod.id]["precio"]}
        )
    fs_query_cats = db.collection("CategoriaProducto").get()
    rests = ProductosAPIView.aux_fill_missing_fields(
        ProductosAPIView, rests, fs_query_cats
    )
    return rests


def list_rest_delivery(id_rest, fs_query_prods):
    if "20-" in id_rest:
        id_rest = "20"
    tarifas_api = requests.get(f"{API_Tarifas}/tarifav/{id_rest}/").json()
    tarifas_domi_api = requests.get(f"{API_Tarifas}/tarifav/3/").json()
    # fs_query_prods = db.collection("Producto").get()
    rests = []
    for prod in fs_query_prods:
        if not prod.id in tarifas_api or not prod.id in tarifas_domi_api:
            continue
        rests.append(
            {"id": prod.id}
            | prod.to_dict()
            | {"Precio": tarifas_api[prod.id]["precio"]}
        )
    return rests


def retrieve_info(id_prod, id_rest):
    prod = db.collection("Producto").document(id_prod).get()
    if not prod.exists:
        return {}
    tarifa = requests.get(f"{API_Tarifas}/{id_rest}/{id_prod}/")
    if not tarifa.status_code in [201, 200]:
        return {}
    tarifa = tarifa.json()
    data = {"id": prod.id} | prod.to_dict() | {"Precio": tarifa["precio"]}
    return data

def retrieve_info_deliv(id_prod, id_rest):
    prod = db.collection("Producto").document(id_prod).get()
    if not prod.exists:
        return {}
    tarifa_rest = requests.get(f"{API_Tarifas}/{id_rest}/{id_prod}/")
    if not tarifa_rest.status_code in [201, 200]:
        return {}
    tarifa_del = requests.get(f"{API_Tarifas}/3/{id_prod}/")
    if not tarifa_del.status_code in [201, 200]:
        return {}
    tarifa_del = tarifa_del.json()
    data = {"id": prod.id} | prod.to_dict() | {"Precio": tarifa_del["precio"]}
    return data
