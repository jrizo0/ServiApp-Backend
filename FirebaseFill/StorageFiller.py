import firebase_admin
from firebase_admin import credentials, storage

import os, sys
import csv


if not firebase_admin._apps:
    cred = credentials.Certificate("../ServiApp/serviceAccountKey.json")
    # bucket = "tests-django.appspot.com"
    bucket = "serviapp-e9a34.appspot.com"
    firebase_admin.initialize_app(cred, {"storageBucket": bucket})

ds = storage.bucket()

dir_name = sys.argv[1]

path = os.path.join(os.getcwd(), "data", dir_name)
print("Filling...")
urls = []
for filename in os.listdir(path):
    with open(os.path.join(path, filename), "r") as f:  # open in readonly mode
        f_name = f.name.split('\\')[-1]
        try:
            blob = ds.blob(dir_name + '/' + f_name)
            blob.upload_from_filename(f.name)
            blob.make_public()
            blob_url = blob.public_url
            urls.append([f_name, blob_url])
        except:
            print("-------Error al agregar el archivo: " + f_name)
print("Filled.")

with open(os.path.join(os.getcwd(), "data", "urls.csv"), "w", encoding='UTF-8') as urls_f:
    writer = csv.writer(urls_f)
    writer.writerows(urls)
