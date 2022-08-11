from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Tarifav, Tarifa
from .serializers import TarifavSerializer, TarifaSerializer

@api_view(['GET'])
def getTarifasv(request):
    tarifasv = Tarifav.objects.all()
    serializer = TarifavSerializer(tarifasv, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getTarifas(request):
    tarifas = Tarifa.objects.all()
    serializer = TarifaSerializer(tarifas, many=True)
    return Response(serializer.data)


