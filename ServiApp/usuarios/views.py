from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Cliente
from .serializers import ClienteSerializer

@api_view(['GET'])
def getClientes(request):
    clientes = Cliente.objects.all()
    serializer = ClienteSerializer(clientes, many=True)
    return Response(serializer.data)




