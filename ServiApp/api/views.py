# from rest_framework.response import Response
# from rest_framework.decorators import api_view
# from productos.models import Producto
# from .serializers import ProductoSerializer
#
# @api_view(['GET'])
# def getProductos(request):
#     productos = Producto.objects.all()
#     serializer = ProductoSerializer(productos, many=True)
#     return Response(serializer.data)
#
