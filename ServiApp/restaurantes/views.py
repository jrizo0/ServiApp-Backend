from rest_framework import viewsets
from rest_framework import mixins

import requests

# import json

from rest_framework.response import Response

# from django.core.cache import cache

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from rest_framework.views import APIView

from ServiApp.firebase import db, fb_valid_req_token
from django.conf import settings

# from .objects import TarifaObject, TarifavObject

API_Restaurantes = settings.SA_API_URL + "/restaurantes/"


# NOTE: No se puede @api_view por cache solo se puede con clases),
class RestauranteAPIView(
    viewsets.GenericViewSet,
):
    def get_queryset(self):
        try:
            res = requests.get(API_Restaurantes)
        except requests.exceptions.RequestException as e:
            return {"status": 400, "message": str(e)}
        return res.json()

    @method_decorator(vary_on_cookie)
    @method_decorator(cache_page(60 * 1))
    def list(self, request):
        return Response(self.get_queryset())

    def auth_list_category(self, request, id_category):
        if not fb_valid_req_token(request):
            response = {"status": 400, "message": "User token invalid"}
            return Response(response)
        return self.list_category(request, id_category)

    # @method_decorator(vary_on_headers("Authorization"))
    @method_decorator(vary_on_cookie)
    @method_decorator(cache_page(60 * 1))
    def list_category(self, request, id_category):
        db_query = (
            db.collection("Restaurante")
            .where("Categoria", "==", str(id_category))
            .get()
        )
        rests_in_category = [{"id": doc.id} | doc.to_dict() for doc in db_query]
        return Response(rests_in_category)
