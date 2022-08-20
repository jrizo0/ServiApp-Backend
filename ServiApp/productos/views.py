from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Producto
from .serializers import ProductoSerializer

@api_view(['GET'])
def getProductos(request):
    productos = Producto.objects.all()
    serializer = ProductoSerializer(productos, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getProducto(request, pk):
    producto = Producto.objects.get(pk=pk)
    serializer = ProductoSerializer(producto)
    return Response(serializer.data)

@api_view(['POST'])
def createProducto(request):
    serializer = ProductoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)

@api_view(['PUT'])
def updateProducto(request, pk):
    producto = Producto.objects.get(pk=pk)
    serializer = ProductoSerializer(instance=producto, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)

@api_view(['DELETE'])
def deleteProducto(request, pk):
    producto = Producto.objects.get(pk=pk)
    producto.delete()
    return Response('Producto eliminado')



