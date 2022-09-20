import firebase_admin
from firebase_admin import credentials, auth

import csv, os

if not firebase_admin._apps:
    cred = credentials.Certificate("../ServiApp/serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

page = auth.list_users()

while page:
    for user in page.users:
        auth.delete_user(user.uid)

    page = page.get_next_page()

path = os.path.join(os.getcwd(), "data", "SA-AuthData.csv")
with open (path, "r", encoding='UTF-8') as f:
    print("Filling...")
    reader = csv.reader(f)
    next(reader)
    headers = []
    for row in reader:
        new_user_id = row[0]
        new_user_email = row[2]
        new_user_passw = row[3]
        try:
            user = auth.create_user(uid=new_user_id, email=new_user_email, password=new_user_passw)
            print(user.email)
        except auth.AuthError as e:
            print("------Error al agregar el usuario: " + new_user_id)

print("Filled.")
