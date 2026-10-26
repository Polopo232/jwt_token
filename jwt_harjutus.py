import base64
import hashlib
import hmac
import json
from datetime import datetime
from zoneinfo import ZoneInfo

token = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJzdWIiOiIxMDI0IiwibmFtZSI6Ik1hcmkgTWFhc2lrYXMiLCJyb2xlIjoic3R1ZGVudCIs"
    "ImlhdCI6MTc2MTIwNjQwMCwiZXhwIjoxNzYxMjEwMDAwfQ"
    ".ZL6DsKKTa2hRmEkkMASGBI7hZW8ot5bJS2I8oOxVTwM"
)


def b64url_decode(tekst):
    tekst += "=" * (-len(tekst) % 4)
    return base64.urlsafe_b64decode(tekst)


def b64url_encode(baidid):
    return base64.urlsafe_b64encode(baidid).rstrip(b"=").decode()


pais_b64, payload_b64, allkiri_b64 = token.split(".")

pais = json.loads(b64url_decode(pais_b64))
payload = json.loads(b64url_decode(payload_b64))
print("Päis:", pais)
print("Payload:", payload)

tz = ZoneInfo("Europe/Tallinn")
print("Väljastatud:", datetime.fromtimestamp(payload["iat"], tz))
print("Aegub:", datetime.fromtimestamp(payload["exp"], tz))
print("Kehtib praegu:", datetime.now(tz).timestamp() < payload["exp"])


def allkirjasta(pais_b64, payload_b64, voti):
    sisend = f"{pais_b64}.{payload_b64}".encode()
    raasi = hmac.new(voti.encode(), sisend, hashlib.sha256).digest()
    return b64url_encode(raasi)


oige = allkirjasta(pais_b64, payload_b64, "saladus123")
vale = allkirjasta(pais_b64, payload_b64, "saladus124")
print("Õige võti:", hmac.compare_digest(oige, allkiri_b64))
print("Vale võti:", hmac.compare_digest(vale, allkiri_b64))

voltsitud = dict(payload, role="admin")
voltsitud_b64 = b64url_encode(
    json.dumps(voltsitud, separators=(",", ":")).encode()
)
voltsitud_token = f"{pais_b64}.{voltsitud_b64}.{allkiri_b64}"

kontroll = allkirjasta(pais_b64, voltsitud_b64, "saladus123")
print("Võltsing läbib kontrolli:", hmac.compare_digest(kontroll, allkiri_b64))
