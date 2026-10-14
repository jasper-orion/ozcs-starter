# Lokalen reserveren

Een kleine webapp waarmee personeel van een school lokalen reserveert. Ze dient als voorbeeld in de workshop "Van Vibe Coding naar Production-Ready AI Development" (OZCS, 16 oktober 2026): je ziet hoe een app met AI-hulp netjes wordt opgebouwd, en je breidt hem zelf uit.

Alle gegevens in de app (scholen, personeel, lokalen) zijn verzonnen. Er is een testlogin: je kiest een testgebruiker, er is geen echt wachtwoord. Twee testgebruikers zitten op twee verschillende scholen, zodat je ziet dat een school de gegevens van een andere school niet kan zien.

Repository: [LINK VOLGT]

## Architectuur in 10 regels

1. `frontend/`: React + TypeScript + Vite. Alle aanroepen naar de API staan in `frontend/src/api.ts`.
2. `backend/`: FastAPI + Pydantic v2 + SQLAlchemy 2 op Python 3.14.
3. Contract eerst: elke aanvraag en elk antwoord is een Pydantic-schema (`backend/app/schemas.py`), gepubliceerd als OpenAPI op `/docs`.
4. Lagen: `routes` (alleen HTTP) roepen `services` aan (regels en autorisatie), die `models` gebruiken (database).
5. De huidige gebruiker komt uit één functie, `get_current_user` in `backend/app/auth.py`. Nu is dat een testlogin, in productie een Microsoft Entra ID-token.
6. Elke query filtert op de school van de gebruiker. De server vertrouwt nooit een school-id uit de browser.
7. Alleen de eigenaar kan een reservatie annuleren. Annuleren schrijft een rij in `audit_log` (wie, wat, wanneer), in dezelfde transactie.
8. Instellingen staan in `.env` (niet in Git), met `backend/.env.example` als voorbeeld. De database is SQLite lokaal; één `DATABASE_URL` wijst in productie naar Azure SQL.
9. `/health` en `/version` laten zien of de API draait en welke build er live staat (`APP_VERSION`).
10. Tests in `backend/tests/` bewijzen het gedrag. De regels voor de AI staan in `.github/copilot-instructions.md`.

Bewust nog niet ingebouwd: dubbele boekingen tegenhouden. Dat is de opdracht van vandaag (`docs/OPDRACHT.md`).

## Wat heb je nodig?

Python 3.14, Node.js (LTS), Git en VS Code. Geen Docker en geen databaseserver.

Python haal je uit de Microsoft Store, via de app "Python Install Manager" (stappen in handout 01). We gebruiken bewust 3.14: Python 3.15.0 is uit, maar de vastgepinde pakketten zijn getest op 3.14.

## De backend starten

Open een terminal in VS Code (Terminal > New Terminal) in de map van dit project.

```powershell
cd backend
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

De API draait nu op <http://localhost:8000>. Bij de eerste start maakt de app het bestand `lokalen.db` aan met de verzonnen testgegevens.

- Interactieve documentatie van de API: <http://localhost:8000/docs>
- Gezondheidscontrole: <http://localhost:8000/health>
- Versie: <http://localhost:8000/version>

Een eigen `.env` is niet nodig, de standaardwaarden werken. Wil je de instellingen aanpassen, kopieer dan het voorbeeld:

```powershell
Copy-Item .env.example .env
```

### Meldt PowerShell dat scripts niet mogen draaien?

Bij `Activate.ps1` kan een rode fout verschijnen over "execution policy" (scripts uitvoeren is uitgeschakeld). Sta scripts alleen voor je eigen gebruiker toe:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Bevestig met `J` en voer `.\.venv\Scripts\Activate.ps1` opnieuw uit. Vooraan je regel staat nu `(.venv)`.

## De frontend starten

Open een tweede terminal (de backend blijft draaien in de eerste).

```powershell
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>, kies bovenaan een testgebruiker en reserveer een lokaal.

## De tests draaien

In de terminal van de backend, met de virtuele omgeving actief:

```powershell
cd backend
pytest
```

Controle van de frontend zonder te starten: `npm run build` in de map `frontend`.

## Mappen

```text
backend/
  app/
    main.py          opstartpunt, CORS, foutafhandeling
    config.py        instellingen uit .env
    schemas.py       Pydantic-contracten
    models.py        databasemodellen
    auth.py          get_current_user (testlogin)
    routes/          HTTP-laag: rooms, reservations, meta
    services/        regels en autorisatie
  tests/             pytest
frontend/            Vite + React + TypeScript
docs/OPDRACHT.md     de oefening
.github/copilot-instructions.md   projectregels voor de AI
```
