from .models import Tarifav, Tarifa
from .serializers import TarifavSerializer, TarifaSerializer

from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.cache import cache
from rest_framework.viewsets import ModelViewSet

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

import requests
import json 

#Tarifav === Restaurante

class RestauranteViewSet(ModelViewSet):
    serializer_class = TarifavSerializer
    queryset = Tarifav.objects.all()
    lookup_field = "idtarifav"
    http_method_names = ['get', 'post', 'put', 'delete']

    @method_decorator(vary_on_cookie)
    @method_decorator(cache_page(60*1))
    def list(self, request):
        response = {}
        res = requests.get('http://127.0.0.1:8000/api/restaurantes')
        if res.status_code != 200:
            response['status'] = res.status_code
            response['message'] = 'error en la llamada'
            return Response(response)
        data = res.json()
        serializer = TarifavSerializer(data=data, many=True)
        serializer.is_valid()
        # TODO: compara con la bd los pk
        # return Response(serializer.validated_data)
        return Response(serializer.data)
            

    # @method_decorator(vary_on_cookie)
    # @method_decorator(cache_page(60*1))
    # def dispatch(self, *args, **kwargs):
    #     return super(RestauranteViewSet, self).dispatch(*args, **kwargs)


