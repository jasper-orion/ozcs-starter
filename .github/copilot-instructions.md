# Projectregels voor de AI-assistent

Dit project is "Lokalen reserveren": een webapp waarmee personeel van een school lokalen reserveert.
Stack: React + TypeScript + Vite (map `frontend/`), FastAPI + Pydantic v2 + SQLAlchemy 2 op Python 3.14 (map `backend/`), SQLite lokaal en Azure SQL in productie via één `DATABASE_URL`.

Antwoord in het Nederlands. Code, bestandsnamen en identifiers blijven Engels.

## Zo werk je

- Werk in kleine stappen: één wijziging per keer, die ik kan nalezen.
- Bij een grotere opdracht stel je eerst een plan voor (welke bestanden, welke tests, welke volgorde) en wacht je op mijn akkoord voordat je code schrijft.
- Schrijf of pas tests aan bij elke wijziging. Bij een bug schrijf je eerst een test die faalt, en pas daarna de oplossing.
- Pas nooit een bestaande test aan om hem te laten slagen. Klopt de test niet meer, leg dan uit waarom en vraag mijn akkoord.
- Leg elke wijziging kort uit: wat je veranderde en waarom.
- Zeg niet dat iets werkt als je het niet hebt uitgevoerd. Ik beoordeel de diff en draai de tests zelf (`pytest` in `backend/`, `npm run build` in `frontend/`).

## Architectuurregels

1. **Contract eerst.** Elke aanvraag en elk antwoord van de API is een Pydantic-schema in `backend/app/schemas.py`. Pas het contract aan voordat je de code erachter schrijft, en spiegel het in `frontend/src/api.ts`.
2. **Lagen.** `routes` (alleen HTTP) roepen `services` aan (businessregels en autorisatie), en die gebruiken `models` (database). Een route raakt de database nooit rechtstreeks aan.
3. **Autorisatie komt uit de geverifieerde identiteit, nooit uit wat de browser stuurt.** De huidige gebruiker komt uit `get_current_user` in `backend/app/auth.py`. Elke query filtert op het school-id van die gebruiker. Acties die alleen de eigenaar mag doen, controleer je in de service. Neem nooit een school-id of gebruikers-id aan uit een request body, query of header.
4. **Geen geheimen in code.** Instellingen komen uit omgevingsvariabelen via `backend/app/config.py`. Lokaal staan ze in `.env` (staat in `.gitignore`), met een voorbeeld in `.env.example`. Zet nooit wachtwoorden, sleutels of connection strings in code, tests of voorbeelden.
5. **Koppel records met database-id's.** Teksten die iemand intypt (namen, codes, titels) zijn invoer, geen sleutel.
6. **Elke destructieve actie laat een logrij achter** in `audit_log`: wie, welke actie, welk id, wanneer. Geen persoonlijke inhoud. De logrij wordt in dezelfde transactie geschreven als de wijziging zelf.
7. **`/health` en `/version` blijven werken.** De versie komt uit de omgevingsvariabele `APP_VERSION`, die de pipeline bij elke build invult.
8. **Tests bewijzen gedrag, en een test moet kunnen falen.** Controleer bij een nieuwe test dat hij faalt zonder de oplossing.
9. **Kleine stappen, één commit per stap.** Ik controleer de diff en de tests voordat ik commit. Jij beoordeelt je eigen werk niet.
10. **Valideer elke invoer**: lengtes, formaten, waardebereiken. Foutmeldingen zijn algemeen en lekken geen interne details. Bij het aanpassen van CORS gebruik je een allowlist, nooit `*`. In productie alleen HTTPS, en rate limiting op publieke endpoints.

## Gegevens

- Gebruik in code, tests, seed-data en voorbeelden alleen verzonnen gegevens. Nooit echte personen, leerlingen, scholen of e-mailadressen.
- Bewaar zo weinig persoonsgegevens mogelijk. Nu is dat alleen de weergavenaam van een personeelslid. Voeg geen persoonsgegevens toe zonder dat ik dat vraag.

## Stijl

- Python: type hints, kleine functies, docstrings in het Nederlands waar de regel niet vanzelf spreekt.
- TypeScript: strikte types, geen `any`. Alle API-aanroepen lopen via `frontend/src/api.ts`.
- Gewone CSS in `frontend/src/styles.css`. Geen UI-bibliotheek toevoegen zonder overleg.
- Voeg geen nieuwe pakketten toe zonder te zeggen waarom, en pin de versie in `requirements.txt` of `package.json`.
