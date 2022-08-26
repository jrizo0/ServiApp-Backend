from .models import Tarifav, Tarifa
from .serializers import TarifavSerializer, TarifaSerializer

import requests
import json

from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from django.core.cache import cache
from rest_framework.viewsets import ModelViewSet

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie


"""
Categorias: 
    1. Almuerzo
    2. Comida rapida
RestaurantesXCategoria:
    1 -> [3, 11, 15, 20, 121, 124, 125, 127]
    2 -> [3, 13, 14, 15, 20]
"""
categoria_almuerzo = [3, 11, 15, 20, 121, 124, 125, 127]
categoria_comida_rapida = [3, 13, 14, 15, 20]


class RestauranteViewSet(ModelViewSet):
    serializer_class = TarifavSerializer
    queryset = Tarifav.objects.all()
    lookup_field = "idtarifav"
    http_method_names = ["get", "post", "put", "delete"]

    @method_decorator(vary_on_cookie)
    @method_decorator(cache_page(60 * 1))
    def list(self, request):
        try:
            res = requests.get("http://127.0.0.1:8000/api/restaurantes")
        except requests.exceptions.RequestException as e:
            response = {"status": 400, "message": e.__str__()}
            return Response(response)
        data = res.json()
        serializer = TarifavSerializer(data, many=True)
        #TODO: or model sin pk, or objects (pk error)
        return Response(serializer.data)

    #TODO: list by categorias, guardar categorias?
    @method_decorator(vary_on_cookie)
    @method_decorator(cache_page(60 * 1))
    @action(detail=False, methods=["GET"])
    def comidarapida(self, request, *args, **kwargs):
        queryset = Tarifav.objects.filter(idtarifav__in=categoria_comida_rapida)
        serializer = TarifavSerializer(queryset, many=True)
        return Response(serializer.data)

    # @method_decorator(vary_on_cookie)
    # @method_decorator(cache_page(60*1))
    # def dispatch(self, *args, **kwargs):
    #     return super(RestauranteViewSet, self).dispatch(*args, **kwargs)
