"""Opstartpunt van de API: uvicorn app.main:app --reload"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.models import Base, SessionLocal, engine
from app.routes import meta, reservations, rooms
from app.services.errors import ConflictError, ForbiddenError, NotFoundError
from app.services.seed import seed_if_empty


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Tabellen en verzonnen testdata aanmaken bij het opstarten (voor de workshop; in productie gebruik je migraties).
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed_if_empty(db)
    yield


app = FastAPI(title="Lokalen reserveren", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "X-Dev-User"],
)


@app.exception_handler(NotFoundError)
def not_found_handler(_request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ForbiddenError)
def forbidden_handler(_request: Request, exc: ForbiddenError):
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(ConflictError)
def conflict_handler(_request: Request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


app.include_router(meta.router)
app.include_router(rooms.router)
app.include_router(reservations.router)
