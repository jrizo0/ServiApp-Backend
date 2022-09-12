# import pyrebase
#
# config = {
#   "apiKey": "AIzaSyD-fhcsE9BCPiVWcPB9F0pDQKS2T5Wk9as",
#   "authDomain": "tests-django.firebaseapp.com",
#   "databaseURL": "https://tests-django-default-rtdb.firebaseio.com",
#   "storageBucket": "tests-django.appspot.com"
# }
#
# firebase = pyrebase.initialize_app(config)
#
# auth = firebase.auth()
# storage = firebase.storage()
# db = firebase.database()

# test = storage.child("categorias/parrilla.jpg").get_url(None)
# test = storage.child("categorias/parrilla.jpg").download("../", "downloaded.jpg")
# test = storage.child("categorias/parrilla.jpg").put("downloaded.jpg")

# data = {"id": 3, "nombre": "Pecera"}
# test = db.child("restaurantes").push(data)
# data = {"nombre": "DOMICILIOS 2020"}
# test = db.child("restaurantes").child(3).set(data)

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


import firebase_admin
from firebase_admin import credentials, firestore, auth
from django.conf import settings

if not firebase_admin._apps:
    cred = credentials.Certificate(settings.FIREBASE_SETTINGS)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def fb_valid_req_token(request):
    try:
        auth_token = request.META.get('HTTP_AUTHORIZATION')
        token = auth_token.replace("Bearer ", "")
        print(token)
        decoded_token = auth.verify_id_token(token)
        firebase_user_id = decoded_token['user_id']
        print(firebase_user_id)
        return True
    except:
        return False
    
        
# data = {'nombre': 'MIRADOR', 'descripcion': 'Descripcion del mirador', 'categoria': '1'}
# db.collection('restaurantes').document('11').set(data)

# result = db.collection('restaurantes').get() 
# for r in result:
#     print(r.to_dict())

# result = db.collection('Usuario').document('24').get()
# if result.exists:
#     print(result.to_dict())

# docs =  db.collection('restaurantes').where('nombre', '==', 'MIRADOR').get()
# for d in docs:
#     print(d.to_dict())
#...

# db_data = db.collection('restaurantes').where('categoria', '==', '1').get()
# data = {doc.id: doc.to_dict() for doc in db_data}
# data = [ d.to_dict().update({"id": str(d.id)}) for d in db_data ]
# print(data)


# doc = ({'id': d.id}.update(d.to_dict()) for d in db_data)
# print(doc)

# req = []
# for doc in db_data:
#     d_id = {'id': doc.id}
#     d_id.update(doc.to_dict())
#     req.append(d_id)
# print(req)

# list = [d.to_dict() for d in db_data]
# print(list)

# print(list(db_data))



