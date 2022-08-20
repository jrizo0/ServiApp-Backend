from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Tarifav, Tarifa
from .serializers import TarifavSerializer, TarifaSerializer

#Tarifav === Restaurante

@api_view(['GET'])
def getTarifasv(request):
    tarifasv = Tarifav.objects.all()
    serializer = TarifavSerializer(tarifasv, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getTarifasvId(request, id):
    tarifasv = Tarifav.objects.get(id=id)
    serializer = TarifavSerializer(tarifasv)
    return Response(serializer.data)

@api_view(['POST'])
def postTarifasv(request):
    serializer = TarifavSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)

@api_view(['PUT'])
def putTarifasv(request, id):
    tarifasv = Tarifav.objects.get(id=id)
    serializer = TarifavSerializer(instance=tarifasv, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)

@api_view(['DELETE'])
def deleteTarifasv(request, id):
    tarifasv = Tarifav.objects.get(id=id)
    tarifasv.delete()
    return Response('Tarifav eliminado')



@api_view(['GET'])
def getTarifas(request):
    tarifas = Tarifa.objects.all()
    serializer = TarifaSerializer(tarifas, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getTarifa(request, pk):
    tarifa = Tarifa.objects.get(pk=pk)
    serializer = TarifaSerializer(tarifa)
    return Response(serializer.data)

@api_view(['POST'])
def createTarifa(request):
    serializer = TarifaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)

@api_view(['PUT'])
def updateTarifa(request, pk):
    tarifa = Tarifa.objects.get(pk=pk)
    serializer = TarifaSerializer(instance=tarifa, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)

@api_view(['DELETE'])
def deleteTarifa(request, pk):
    tarifa = Tarifa.objects.get(pk=pk)
    tarifa.delete()
    return Response('Tarifa eliminada')


