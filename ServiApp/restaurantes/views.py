from rest_framework import viewsets

import requests

from rest_framework.response import Response

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers

from ServiApp.firebase import db, fb_valid_req_token
from django.conf import settings

from django.core.exceptions import PermissionDenied


API_Restaurantes = settings.SA_API_URL + "/restaurantes/"

# NOTE: No se puede @api_view por cache solo se puede con clases).
class RestauranteAPIView(
    viewsets.GenericViewSet,
):
    def __init__(self):
        self.enable_auth = False

    # NOTE: Queryset el nombre de ServiciosAlimentacionApi.
    # def get_queryset(self):
    #     try:
    #         fs_query = db.collection("Restaurante").get()
    #         res = []
    #         for rest in fs_query:
    #             rest_api = requests.get(API_Restaurantes + rest.id).json()
    #             rest = {"id": rest.id} | rest.to_dict()
    #             rest['Nombre'] = rest_api['descripcion']
    #             res.append(rest)
    #     except requests.exceptions.RequestException as e:
    #         raise e
    #     return res

    # NOTE: Queryset guardando el nombre en fb.
    def get_queryset(self):
        fs_query = db.collection("Restaurante").get()
        rests = [{"id": doc.id} | doc.to_dict() for doc in fs_query]
        return rests

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
        fs_query = (
            db.collection("Restaurante").where("Categoria", "==", id_category).get()
        )
        rests_in_category = [{"id": doc.id} | doc.to_dict() for doc in fs_query]
        return Response(rests_in_category)
