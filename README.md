# JWT mini-API

Väike Flask rakendus, mis kasutab JWT-d autentimiseks.

## Käivitamine

```
python -m venv venv
venv\Scripts\activate # Windowsis: venv\Scripts\activate
pip install flask pyjwt

set SALAVOTI=pane-siia-vahemalt-32-margiline-salavoti

python app.py
```

Server töötab aadressil http://127.0.0.1:5000

## Lõpp-punktid

- `POST /login` - võtab JSON-i `{"kasutajanimi": "...", "parool": "..."}` ja tagastab tokeni (kehtib 5 minutit)
- `GET /profiil` - tagastab tokeni andmed, vaja on päist `Authorization: Bearer <token>`
- `GET /admin` - ainult rolliga `admin`

## Testkasutajad

- mari / maasikas1 (student)
- juhan / admin123 (admin)

## Testid

```
python testid.py

curl -X POST http://127.0.0.1:5000/login -H "Content-Type: application/json" -d "{\"kasutajanimi\":\"mari\",\"parool\":\"maasikas1\"}"

curl http://127.0.0.1:5000/profiil -H "Authorization: Bearer TOKEN"

curl http://127.0.0.1:5000/profiil #Saatmine ilma tokenita põhjustab vea
```
