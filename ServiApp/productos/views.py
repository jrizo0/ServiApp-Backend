from rest_framework import viewsets

import requests

from rest_framework.response import Response

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers

from ServiApp.firebase import db, fb_valid_req_token
from django.conf import settings

from django.core.exceptions import PermissionDenied


API_Productos = settings.SA_API_URL + "/productos/"

# NOTE: No se puede @api_view por cache solo se puede con clases).
class ProductosAPIView(
    viewsets.GenericViewSet,
):
    def __init__(self):
        self.enable_auth = False

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
        fs_query = db.collection("Producto").get()
        prods = [{"id": doc.id} | doc.to_dict() for doc in fs_query]
        return prods

    # @method_decorator(vary_on_cookie)
    # @method_decorator(cache_page(60 * 1))
    def list(self, request):
        return Response(self.get_queryset())

    # @method_decorator(vary_on_headers("Authorization"))
    # @method_decorator(vary_on_cookie)
    # @method_decorator(cache_page(60 * 1))
    def list_category(self, request, id_category):
        if self.enable_auth and not fb_valid_req_token(request):
            raise PermissionDenied()
        fs_query = db.collection("Producto").where("Categoria", "==", id_category).get()
        rests_in_category = [{"id": doc.id} | doc.to_dict() for doc in fs_query]
        return Response(rests_in_category)

    # @method_decorator(vary_on_headers("Authorization"))
    # @method_decorator(vary_on_cookie)
    # @method_decorator(cache_page(60 * 1))
    def list_rest(self, request, id_rest):
        if self.enable_auth and not fb_valid_req_token(request):
            raise PermissionDenied()
        prods_in_rest = []
        fs_query = db.collection("Tarifa").where("Restaurante", "==", id_rest).get()
        for prod in fs_query:
            prod_info = (
                db.collection("Producto").document(prod.to_dict()["Producto"]).get()
            )
            prod = {"id": prod_info.id} | prod.to_dict() | prod_info.to_dict()
            del prod["Producto"], prod["Restaurante"]
            prods_in_rest.append(prod)
        return Response(prods_in_rest)

    # @method_decorator(vary_on_cookie)
    # @method_decorator(cache_page(60 * 1))
    def list_rest_by_category(self, request, id_rest):
        if self.enable_auth and not fb_valid_req_token(request):
            raise PermissionDenied()
        prods_in_rest = []
        fs_query = db.collection("Tarifa").where("Restaurante", "==", id_rest).get()
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
