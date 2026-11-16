"""API pédagogique de gestion des stages : FastAPI et SQLite."""
import os
import sqlite3
from contextlib import asynccontextmanager, contextmanager
from datetime import date
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


@contextmanager
def database():
    path = Path(os.environ.get("DATABASE_PATH", "data/stages.db"))
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    try:
        with connection:
            yield connection
    finally:
        connection.close()


@asynccontextmanager
async def lifespan(app):
    with database() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS stages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_etudiant TEXT NOT NULL,
            entreprise TEXT NOT NULL,
            intitule TEXT NOT NULL,
            date_debut TEXT NOT NULL,
            date_fin TEXT NOT NULL CHECK(date_fin >= date_debut)
        )""")
    yield


app = FastAPI(
    title="Stages API",
    description="Mini-projet Cloud Computing, Microservices et API. Données fictives uniquement.",
    version="1.0.0",
    lifespan=lifespan,
)


class StageInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    nom_etudiant: str = Field(min_length=1, max_length=120)
    entreprise: str = Field(min_length=1, max_length=160)
    intitule: str = Field(min_length=1, max_length=200)
    date_debut: date
    date_fin: date

    @field_validator("date_debut", "date_fin", mode="before")
    @classmethod
    def iso_date(cls, value):
        if isinstance(value, date):
            return value
        if not isinstance(value, str):
            raise ValueError("Utiliser une date au format AAAA-MM-JJ")
        try:
            parsed = date.fromisoformat(value)
        except ValueError:
            raise ValueError("Utiliser une date au format AAAA-MM-JJ")
        if value != parsed.isoformat():
            raise ValueError("Utiliser une date au format AAAA-MM-JJ")
        return parsed

    @model_validator(mode="after")
    def ordered_dates(self):
        if self.date_fin < self.date_debut:
            raise ValueError("La date de fin doit être supérieure ou égale à la date de début")
        return self


class Stage(StageInput):
    id: int


def parameters(stage):
    return (stage.nom_etudiant, stage.entreprise, stage.intitule,
            stage.date_debut.isoformat(), stage.date_fin.isoformat())


def find(db, stage_id):
    row = db.execute("SELECT * FROM stages WHERE id = ?", (stage_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Stage introuvable")
    return dict(row)


@app.get("/", tags=["Service"])
def root():
    return {"service": "Stages API", "documentation": "/docs", "health": "/health"}


@app.get("/health", tags=["Service"])
def health():
    with database() as db:
        db.execute("SELECT COUNT(*) FROM stages").fetchone()
    return {"status": "ok", "database": "sqlite"}


@app.post("/stages", response_model=Stage, status_code=201, tags=["Stages"])
def create_stage(stage: StageInput, response: Response):
    with database() as db:
        cursor = db.execute("""INSERT INTO stages
            (nom_etudiant, entreprise, intitule, date_debut, date_fin)
            VALUES (?, ?, ?, ?, ?)""", parameters(stage))
        response.headers["Location"] = f"/stages/{cursor.lastrowid}"
        return find(db, cursor.lastrowid)


@app.get("/stages", response_model=list[Stage], tags=["Stages"])
def list_stages(offset: Annotated[int, Query(ge=0)] = 0,
                limit: Annotated[int, Query(ge=1, le=100)] = 100):
    with database() as db:
        return [dict(row) for row in db.execute(
            "SELECT * FROM stages ORDER BY id LIMIT ? OFFSET ?", (limit, offset))]


@app.get("/stages/{stage_id}", response_model=Stage, tags=["Stages"])
def read_stage(stage_id: int):
    with database() as db:
        return find(db, stage_id)


@app.put("/stages/{stage_id}", response_model=Stage, tags=["Stages"])
def update_stage(stage_id: int, stage: StageInput):
    with database() as db:
        find(db, stage_id)
        db.execute("""UPDATE stages SET nom_etudiant=?, entreprise=?, intitule=?,
            date_debut=?, date_fin=? WHERE id=?""", parameters(stage) + (stage_id,))
        return find(db, stage_id)


@app.delete("/stages/{stage_id}", status_code=204, tags=["Stages"])
def delete_stage(stage_id: int):
    with database() as db:
        find(db, stage_id)
        db.execute("DELETE FROM stages WHERE id=?", (stage_id,))
    return Response(status_code=204)
