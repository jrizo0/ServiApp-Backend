from rest_framework import viewsets
from rest_framework import mixins
# from .models import Tarifav, Tarifa
# from .serializers import TarifavSerializer, TarifaSerializer

import requests
# import json

from rest_framework.response import Response
from rest_framework.decorators import action
# from django.core.cache import cache

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from ServiApp.firebase import db
from django.conf import settings

# from .objects import TarifaObject, TarifavObject

API_Restaurantes = settings.SA_API_URL + "/restaurantes/"


# NOTE: No se puede @api_view por cache solo se puede con clases), 
class RestauranteAPIView(
    mixins.ListModelMixin,
    # mixins.CreateModelMixin,
    # mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):

    def get_queryset(self):
        try:
            res = requests.get(API_Restaurantes)
        except requests.exceptions.RequestException as e:
            response = {"status": 400, "message": e.__str__()}
            return Response(response)
        return res.json()

    @method_decorator(vary_on_cookie)
    @method_decorator(cache_page(60 * 1))
    def list(self, request):
        return Response(self.get_queryset())

    @method_decorator(vary_on_cookie)
    @method_decorator(cache_page(60 * 1))
    @action(detail=False, methods=["GET"])
    def list_category(self, request, id_category):
        db_query = db.collection('restaurantes').where('categoria', '==', str(id_category)).get()

        rests_in_category = []
        for doc in db_query:
            doc_id = {'id': doc.id}
            doc_id.update(doc.to_dict())
            rests_in_category.append(doc_id)

        return Response(rests_in_category)

    # @method_decorator(vary_on_cookie)
    # @method_decorator(cache_page(60*1))
    # def dispatch(self, *args, **kwargs):
    #     return super(RestauranteViewSet, self).dispatch(*args, **kwargs)
