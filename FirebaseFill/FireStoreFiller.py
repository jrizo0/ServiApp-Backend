import firebase_admin
from firebase_admin import credentials, firestore

import sys
import csv

if not firebase_admin._apps:
    cred = credentials.Certificate("../ServiApp/serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

collection_name = sys.argv[1]
csv_name = 'SA-' + sys.argv[1] + '.csv'

docs = db.collection(collection_name).get()
for doc in docs: 
    key = doc.id
    db.collection(collection_name).document(key).delete()

with open (csv_name, "r", encoding='UTF-8') as f:
    print("Filling...")
    reader = csv.reader(f)
    headers = []
    for i, row in enumerate(reader):
        if i == 0: # Header
            for j in range(len(row)):
                if j != 0: headers.append(row[j])
            continue
        
        new_doc_id = row[0]
        new_doc = {}
        for j in range(1, len(row)):
            if j != 0: new_doc[headers[j-1]] = row[j]

        db.collection(collection_name).document(new_doc_id).set(new_doc)

print("Filled.")
