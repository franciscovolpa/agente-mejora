from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session

from db import init_db, get_session
from models import Event, EventCreate, EventRead
from services.event_service import create_event, parse_and_update, get_events_by_day
from pydantic import BaseModel
from typing import Dict, Any
import json

app = FastAPI(title="Agente de Mejora")


class ParsedUpdate(BaseModel):
    parsed: Dict[str, Any]
    parse_status: str


@app.patch("/event/{event_id}/parsed")
def update_parsed(event_id: int, body: ParsedUpdate, session: Session = Depends(get_session)):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    event.parsed = json.dumps(body.parsed)
    event.parse_status = body.parse_status
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/event", response_model=EventRead, status_code=201)
async def post_event(data: EventCreate, background_tasks: BackgroundTasks):
    """
    Guarda raw_text, dispara parsing async, devuelve id inmediato.
    """
    event = create_event(data)
    background_tasks.add_task(parse_and_update, event.id)
    return event


@app.get("/event/{event_id}", response_model=EventRead)
def get_event(event_id: int, session: Session = Depends(get_session)):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return event


@app.get("/day/{day_id}", response_model=list[EventRead])
def get_day(day_id: str):
    """
    Devuelve todos los eventos de un día. Formato: YYYY-MM-DD
    """
    return get_events_by_day(day_id)


@app.get("/health")
def health():
    return {"status": "ok"}
