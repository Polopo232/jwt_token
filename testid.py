import os
import time

os.environ["SALAVOTI"] = "testi-salavoti-mis-on-vaga-pikk-ja-juhuslik-123"

import jwt
from app import app, SALAVOTI

klient = app.test_client()


def pais(token):
    return {"Authorization": "Bearer " + token}


mari = klient.post("/login", json={"kasutajanimi": "mari", "parool": "maasikas1"}).json["token"]
juhan = klient.post("/login", json={"kasutajanimi": "juhan", "parool": "admin123"}).json["token"]
muudetud = mari[:-3] + "abc"
aegunud = jwt.encode(
    {"sub": "1024", "name": "mari", "role": "student", "exp": int(time.time()) - 10},
    SALAVOTI,
    algorithm="HS256",
)

testid = [
    ("Edukas sisselogimine", "/login", 200, lambda: klient.post("/login", json={"kasutajanimi": "mari", "parool": "maasikas1"})),
    ("Vale parool", "/login", 401, lambda: klient.post("/login", json={"kasutajanimi": "mari", "parool": "vale"})),
    ("Profiil kehtiva tokeniga", "/profiil", 200, lambda: klient.get("/profiil", headers=pais(mari))),
    ("Profiil ilma tokenita", "/profiil", 401, lambda: klient.get("/profiil")),
    ("Profiil muudetud tokeniga", "/profiil", 401, lambda: klient.get("/profiil", headers=pais(muudetud))),
    ("Profiil aegunud tokeniga", "/profiil", 401, lambda: klient.get("/profiil", headers=pais(aegunud))),
    ("Admin student tokeniga", "/admin", 403, lambda: klient.get("/admin", headers=pais(mari))),
    ("Admin admin tokeniga", "/admin", 200, lambda: klient.get("/admin", headers=pais(juhan))),
]

for nimi, otspunkt, oodatav, kaivita in testid:
    tegelik = kaivita().status_code
    tulemus = "Läbis" if tegelik == oodatav else "Ei läbinud"
    print(f"{nimi:28} {otspunkt:9} oodatav {oodatav}  tegelik {tegelik}  {tulemus}")
