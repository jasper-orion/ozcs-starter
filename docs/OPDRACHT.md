# Opdracht: geen dubbele boekingen

De app laat nu toe dat twee mensen hetzelfde lokaal op hetzelfde moment reserveren. Dat is geen vergissing: het is jouw opdracht. Je voegt de regel "een lokaal kan niet twee keer tegelijk geboekt worden" toe volgens de werkwijze van een ervaren softwarebouwer: eerst een test die faalt, dan pas de oplossing.

Je werkt met Copilot, maar jij blijft verantwoordelijk. Copilot stelt voor, jij beoordeelt.

## Voor je begint

- Voor de tests hoef je de backend niet te starten. Om het resultaat in de app te zien wel (zie `README.md`).
- Maak een eigen werkbranch zodat `main` ongemoeid blijft:

```powershell
git switch -c dubbele-boekingen
```

- Draai de bestaande tests om te zien dat alles groen is:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest
```

## Stappen

### 1. Vraag Copilot om een plan, nog geen code

Open Copilot Chat in VS Code en vraag:

```text
Ik wil dat een lokaal niet twee keer tegelijk gereserveerd kan worden.
Lees de projectregels in .github/copilot-instructions.md en kijk naar
backend/app/services/reservations.py. Maak een plan in stappen: welke
bestanden, welke tests, welke foutmelding. Schrijf nog geen code.
```

Lees het plan. Klopt het met de regels? Let op drie dingen:

- De controle hoort in de **service** (`services/reservations.py`), niet in de route en niet in de frontend.
- Wat is een overlap? Twee reservaties van hetzelfde lokaal overlappen als de ene begint voor de andere eindigt, en de andere begint voor de eerste eindigt. Een reservatie van 9u tot 10u en een van 10u tot 11u overlappen niet.
- Welke HTTP-statuscode past bij "dit lokaal is al bezet"? (Tip: 409.)

Vraag Copilot het plan aan te passen als iets niet klopt.

### 2. Schrijf eerst de test die faalt

Vraag Copilot om de test, of schrijf hem zelf in `backend/tests/test_reservations.py`. Een bruikbare test:

- Maak een reservatie van 9u tot 10u voor een lokaal.
- Probeer een tweede reservatie van 9u30 tot 10u30 voor hetzelfde lokaal.
- Verwacht statuscode 409.

Maak er ook een tweede test bij die bewijst dat het mag als de tijden elkaar alleen raken (9u tot 10u, daarna 10u tot 11u).

Draai de tests:

```powershell
pytest
```

De eerste nieuwe test **moet nu falen**: de app geeft nog 201 in plaats van 409. Faalt hij niet, dan test hij niets en moet je hem aanpassen. Bewaar de foutmelding even als bewijs dat de test echt faalde.

### 3. Implementeer in de servicelaag

Vraag Copilot om de oplossing, met de uitdrukkelijke opdracht: "pas geen bestaande tests aan". Je ziet in `services/reservations.py` een opmerking waar de controle komt. De bouwstenen:

- een nieuwe fout in `services/errors.py` (bijvoorbeeld `ConflictError`),
- een controle in `create_reservation` met een query op hetzelfde lokaal,
- een handler in `app/main.py` die de fout vertaalt naar 409 met een duidelijke Nederlandse melding.

### 4. Draai de tests

```powershell
pytest
```

Alles moet groen zijn, ook de test uit stap 2. Staat er een oude test op rood, dan heeft de oplossing iets stukgemaakt. Pas de test dan niet aan: zoek de fout in de code.

Probeer het ook met de hand: start backend en frontend (zie `README.md`), kies een testgebruiker en reserveer twee keer hetzelfde lokaal op overlappende tijden. Je ziet de foutmelding in het formulier.

### 5. Beoordeel de diff tegen de instructies

Bekijk wat er veranderd is:

```powershell
git diff
```

Loop de checklist af op basis van `.github/copilot-instructions.md`:

- [ ] De controle zit in de service, niet in de route.
- [ ] De query filtert op de school van de ingelogde gebruiker.
- [ ] Er is geen school-id of gebruikers-id uit de request gebruikt.
- [ ] Er is een test die kan falen en die ook echt faalde.
- [ ] Geen bestaande test is aangepast.
- [ ] Geen geheimen en geen echte gegevens in de code.
- [ ] Copilot heeft de wijziging kort uitgelegd en jij begrijpt die uitleg.

Begrijp je een stuk niet? Vraag Copilot het uit te leggen, of laat het weg.

### 6. Commit

```powershell
git add backend/app backend/tests
git commit -m "Voorkom dubbele boekingen van een lokaal"
```

Zet in het commitbericht wat je deed, niet hoe. Eén stap, één commit.

## Uitbreidingen (als je tijd over hebt)

### A. Openingsuren per lokaal

Een lokaal is alleen te reserveren tussen bijvoorbeeld 8u en 18u.

- Voeg `opens_at` en `closes_at` toe aan het model `Room` en aan de seed-data.
- Schrijf eerst de test: een reservatie van 19u tot 20u wordt geweigerd met een duidelijke melding.
- Laat de frontend de openingsuren bij het lokaal tonen. Pas daarvoor eerst het contract (`RoomOut` en `frontend/src/api.ts`) aan.

Denk na: wat gebeurt er met reservaties die al bestaan?

### B. Een beheerdersrol

Een beheerder van de school mag ook reservaties van collega's annuleren.

- Voeg een veld `is_admin` toe aan `User` en maak in de seed-data een beheerder aan.
- Schrijf eerst twee tests: een beheerder van dezelfde school mag annuleren, een beheerder van een andere school niet.
- De regel hoort in de service. De rol komt uit de database, via `get_current_user`, nooit uit iets wat de browser meestuurt.
- Controleer dat het auditspoor nog klopt: wie annuleerde er echt?

## Hulp nodig?

Op de branch `oplossing` staat een uitgewerkte versie van stap 1 tot en met 4. Kijk er pas naar als je zelf vastzit:

```powershell
git diff main oplossing
```
