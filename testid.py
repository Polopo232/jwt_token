import base64
import json
import os
import time

os.environ["SALAVOTI"] = "testi-salavoti-mis-on-vaga-pikk-ja-juhuslik-123"

import jwt
from app import app, SALAVOTI

klient = app.test_client()


def pais(token):
    return {"Authorization": "Bearer " + token}


def b64url(andmed):
    tekst = json.dumps(andmed, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(tekst).rstrip(b"=").decode()


mari = klient.post("/login", json={"kasutajanimi": "mari", "parool": "maasikas1"}).json["token"]
juhan = klient.post("/login", json={"kasutajanimi": "juhan", "parool": "admin123"}).json["token"]

# Võltsitud token: payloadis role muudetud adminiks, allkiri jäetakse vana
p, pl, allkiri = mari.split(".")
mari_andmed = jwt.decode(mari, SALAVOTI, algorithms=["HS256"])
voltsitud = f"{p}.{b64url(dict(mari_andmed, role='admin'))}.{allkiri}"

# Aegunud token: kehtivus 2 sekundit, saadetakse pärast ootamist
lyhike = jwt.encode(
    {"sub": "1024", "name": "mari", "role": "student", "exp": int(time.time()) + 2},
    SALAVOTI,
    algorithm="HS256",
)
time.sleep(3)

# alg: none - allkirjata token
alg_none = f"{b64url({'alg': 'none', 'typ': 'JWT'})}.{b64url(dict(mari_andmed, role='admin'))}."

testid = [
    ("Edukas sisselogimine", "/login", 200, lambda: klient.post("/login", json={"kasutajanimi": "mari", "parool": "maasikas1"})),
    ("Vale parool", "/login", 401, lambda: klient.post("/login", json={"kasutajanimi": "mari", "parool": "vale"})),
    ("Profiil kehtiva tokeniga", "/profiil", 200, lambda: klient.get("/profiil", headers=pais(mari))),
    ("Profiil ilma tokenita", "/profiil", 401, lambda: klient.get("/profiil")),
    ("Muudetud (võltsitud) token", "/profiil", 401, lambda: klient.get("/profiil", headers=pais(voltsitud))),
    ("Aegunud token", "/profiil", 401, lambda: klient.get("/profiil", headers=pais(lyhike))),
    ("Tavakasutaja admini lõpp-punktil", "/admin", 403, lambda: klient.get("/admin", headers=pais(mari))),
    ("Admin admini lõpp-punktil", "/admin", 200, lambda: klient.get("/admin", headers=pais(juhan))),
    ("Vale algoritm", "/profiil", 401, lambda: klient.get("/profiil", headers=pais(alg_none))),
]

labis = 0
for nr, (nimi, otspunkt, oodatav, kaivita) in enumerate(testid, 1):
    vastus = kaivita()
    tegelik = vastus.status_code
    tulemus = "Läbis" if tegelik == oodatav else "Ei läbinud"
    labis += tegelik == oodatav
    print(f"{nr}. {nimi:34} {otspunkt:9} oodatav {oodatav}  tegelik {tegelik}  {tulemus}")

print(f"\nLäbis {labis}/{len(testid)} testi")