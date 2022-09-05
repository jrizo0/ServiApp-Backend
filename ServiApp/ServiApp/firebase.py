import pyrebase

config = {
  "apiKey": "AIzaSyD-fhcsE9BCPiVWcPB9F0pDQKS2T5Wk9as",
  "authDomain": "tests-django.firebaseapp.com",
  "databaseURL": "https://tests-django-default-rtdb.firebaseio.com",
  "storageBucket": "tests-django.appspot.com"
}

firebase = pyrebase.initialize_app(config)

auth = firebase.auth()
storage = firebase.storage()
db = firebase.database()

# test = storage.child("categorias/parrilla.jpg").get_url(None)
# test = storage.child("categorias/parrilla.jpg").download("../", "downloaded.jpg")
# test = storage.child("categorias/parrilla.jpg").put("downloaded.jpg")

# data = {"id": 3, "nombre": "Pecera"}
# test = db.child("restaurantes").push(data)
# data = {"nombre": "DOMICILIOS 2020"}
# test = db.child("restaurantes").child(3).set(data)


"""
Categorias: 
    1. Almuerzo
    2. Comida rapida
RestaurantesXCategoria:
    1 -> [3, 11, 15, 20, 121, 124, 125, 127]
    2 -> [3, 13, 14, 15, 20]
"""
# categoria_almuerzo = [3, 11, 15, 20, 121, 124, 125, 127]
# categoria_comida_rapida = [3, 13, 14, 15, 20]
# from restaurantes.models import Tarifav as Restaurante
# from restaurantes.serializers import TarifavSerializer

# data = Restaurante.objects.get(pk = 3)
# data = TarifavSerializer(data)
# for r in categoria_comida_rapida:
#     db.child("restaurantes-categoria-2").child(r).set("")

# data = db.child("restaurantes-categoria-1").get()
# print(data.val())
# for r in list(data.val()):
#     print(r)

# print(data.val())

