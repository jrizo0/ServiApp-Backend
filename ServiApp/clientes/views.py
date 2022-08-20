from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Cliente
from .serializers import ClienteSerializer

@api_view(['GET'])
def getClientes(request):
    clientes = Cliente.objects.all()
    serializer = ClienteSerializer(clientes, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getCliente(request, pk):
    cliente = Cliente.objects.get(pk=pk)
    serializer = ClienteSerializer(cliente)
    return Response(serializer.data)

@api_view(['POST'])
def createCliente(request):
    serializer = ClienteSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)

def updateCliente(request, pk):
    cliente = Cliente.objects.get(pk=pk)
    serializer = ClienteSerializer(instance=cliente, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)

def deleteCliente(request, pk):
    cliente = Cliente.objects.get(pk=pk)
    cliente.delete()
    return Response('Item deleted')

