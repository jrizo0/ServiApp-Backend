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


API_Productos = settings.SA_API_URL + "/productos/"
API_Tarifas = settings.SA_API_URL + "/tarifas/"

class FBAuthenticated(BasePermission):
    def __init__(self):
        self.enable_auth = False

    def has_permission(self, request, view):
        return not self.enable_auth or fb_valid_req_token(request)

class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class ProductosAPIView(
    viewsets.GenericViewSet,
):
    permission_classes = [ReadOnly|FBAuthenticated]

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
                    prods[i] = prods[i] | {"Descripcion": doc_cat.to_dict()["Descripcion"]}
        return prods

    # NOTE: Queryset el nombre de ServiciosAlimentacionApi.
    # def get_queryset(self):
    #     try:
    #         fs_query = db.collection("Producto").get()
    #         res = []
    #         for prod in fs_query:
    #             prod_api = requests.get(API_Productos + prod.id).json()
    #             prod = {"id": prod.id} | prod.to_dict()
    #             prod['Nombre'] = prod_api['descripcion']
    #             res.append(prod)
    #     except requests.exceptions.RequestException as e:
    #         raise e
    #     return res

    # NOTE: Queryset guardando el nombre en fb.
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

    # @method_decorator(vary_on_headers("Authorization"))
    # @method_decorator(vary_on_cookie)
    # @method_decorator(cache_page(30 * 1))
    def list_rest(self, request, id_rest):
        if "20-" in id_rest: id_rest = "20"
        tarifas_api = requests.get(API_Tarifas + "tarifav/" + id_rest + "/").json()
        fs_query_prods = db.collection("Producto").get()
        rests = []
        for prod in fs_query_prods:
            if not prod.id in tarifas_api: continue
            rests.append({"id": prod.id} | prod.to_dict() | {"Precio": tarifas_api[prod.id]["precio"]})
        fs_query_cats = db.collection("CategoriaProducto").get()
        rests = self.aux_fill_missing_fields(rests, fs_query_cats)
        return Response(rests)

    # TODO : Eliminar vista?
    # @method_decorator(vary_on_headers("Authorization"))
    # @method_decorator(vary_on_cookie)
    # @method_decorator(cache_page(60 * 1))
    def list_category(self, request, id_category):
        fs_query = db.collection("Producto").where("Categoria", "==", id_category).get()
        rests_in_category = [{"id": doc.id} | doc.to_dict() for doc in fs_query]
        return Response(rests_in_category)

    # TODO : Eliminar vista?
    # @method_decorator(vary_on_cookie)
    # @method_decorator(cache_page(60 * 1))
    def list_rest_by_category(self, request, id_rest):
        prods_in_rest = []
        fs_query = db.collection("Producto").where("Restaurante", "==", id_rest).get()
        for prod in fs_query:
            prod_info = (
                db.collection("Producto").document(prod.to_dict()["Producto"]).get()
            )
            prod = {"id": prod_info.id} | prod.to_dict() | prod_info.to_dict()
            del prod["Producto"], prod["Restaurante"]
            prods_in_rest.append(prod)
        categories = set(prod["Categoria"] for prod in prods_in_rest)
        prods_by_cat = {
            cat: [prod for prod in prods_in_rest if prod["Categoria"] == cat]
            for cat in categories
        }
        return Response(prods_by_cat)
