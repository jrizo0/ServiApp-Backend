from django.http import JsonResponse
from django.core import serializers

from .models import Producto

def getProductos(request):
    data = list(Producto.objects.values())
    # data = serializers.serialize("json", Producto.objects.all())
    # data = {
    #     'name': 'Vitor',
    #     'location': 'Finland',
    #     'is_active': True,
    #     'count': 28
    # }
    return JsonResponse(data, safe=False)
