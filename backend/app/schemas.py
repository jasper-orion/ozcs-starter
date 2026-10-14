"""Contracten: elke aanvraag en elk antwoord van de API is een Pydantic-schema.

FastAPI maakt hier automatisch de OpenAPI-beschrijving van (zie /docs). De frontend
spiegelt deze types in frontend/src/api.ts. Spreek het contract eerst af, schrijf daarna pas code.
"""

from datetime import datetime, timedelta
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

MAX_DURATION = timedelta(hours=8)


class RoomOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    capacity: int
    location: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    display_name: str
    school_name: str


class ReservationCreate(BaseModel):
    room_id: int = Field(gt=0)
    title: str = Field(min_length=3, max_length=100)
    start: datetime
    end: datetime

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 3:
            raise ValueError("De titel moet minstens 3 tekens bevatten.")
        return value

    @field_validator("start", "end")
    @classmethod
    def no_timezone(cls, value: datetime) -> datetime:
        # We werken met lokale schooltijd zonder tijdzone, bijvoorbeeld 2026-10-20T09:00.
        if value.tzinfo is not None:
            raise ValueError("Geef de tijd zonder tijdzone op, bijvoorbeeld 2026-10-20T09:00.")
        return value

    @model_validator(mode="after")
    def check_period(self) -> Self:
        if self.start >= self.end:
            raise ValueError("Het einde moet na het begin liggen.")
        if self.end - self.start > MAX_DURATION:
            raise ValueError("Een reservatie duurt maximaal 8 uur.")
        return self


class ReservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_id: int
    room_name: str
    user_id: int
    user_display_name: str
    title: str
    start: datetime
    end: datetime


class VersionOut(BaseModel):
    version: str


class HealthOut(BaseModel):
    status: str
