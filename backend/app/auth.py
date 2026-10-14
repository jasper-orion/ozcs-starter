"""Wie is de aanvrager? Eén dependency: get_current_user.

Elke route die een gebruiker nodig heeft, vraagt die hier op. Services krijgen de
gebruiker mee en filteren daarmee de data. Het school-id komt dus altijd uit de
gebruiker die de server zelf uit de database haalt. De server vertrouwt nooit een
school-id (of gebruikers-id voor een actie) dat de browser meestuurt.

WERKING NU (dev-stub): de frontend stuurt de header `X-Dev-User: <id>` mee, gekozen in
de testgebruiker-kiezer. Dat is alleen bedoeld voor de workshop en lokaal werk met
verzonnen gegevens. Iedereen kan zo'n header zelf instellen, dus dit is geen beveiliging.

IN PRODUCTIE: deze ene functie wordt vervangen door validatie van een Microsoft Entra ID
token (de header `Authorization: Bearer ...`). De server controleert de handtekening, de
uitgever en de doelgroep van het token, zoekt de gebruiker op via het object-id uit het
token en leest het school-id uit de eigen database. De rest van de app verandert niet,
omdat alles via get_current_user loopt.
"""

from typing import Annotated

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.models import User, get_db


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    x_dev_user: Annotated[int | None, Header()] = None,
) -> User:
    if not settings.dev_auth_enabled:
        raise HTTPException(status_code=401, detail="Aanmelden is vereist.")
    user = db.get(User, x_dev_user) if x_dev_user is not None else None
    if user is None:
        # Bewust één generieke melding: geen verschil tussen "ontbreekt" en "bestaat niet".
        raise HTTPException(status_code=401, detail="Aanmelden is vereist.")
    return user
