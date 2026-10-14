"""Fouten uit de businesslaag. main.py vertaalt ze naar HTTP-statuscodes."""


class NotFoundError(Exception):
    """Bestaat niet, of hoort bij een andere school (we verklappen dat verschil niet)."""


class ForbiddenError(Exception):
    """De gebruiker mag deze actie niet uitvoeren."""
