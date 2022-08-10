from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Restaurante
from .serializers import RestauranteSerializer

@api_view(['GET'])
def getRestaurantes(request):
    restaurantes = Restaurante.objects.all()
    serializer = RestauranteSerializer(restaurantes, many=True)
    return Response(serializer.data)



