from datetime import datetime
from sqlmodel import Session, select

from models import Event, EventCreate
from db import engine
from services.parser_service import parse_event_text


def create_event(data: EventCreate) -> Event:
    event = Event(
        day_id=datetime.utcnow().strftime("%Y-%m-%d"),
        type=data.type,
        source=data.source,
        raw_text=data.text,
        parse_status="pending",
    )
    with Session(engine) as session:
        session.add(event)
        session.commit()
        session.refresh(event)
    return event


async def parse_and_update(event_id: int):
    """Corre en background. Lee, parsea, guarda."""
    with Session(engine) as session:
        event = session.get(Event, event_id)
        if not event:
            return

        try:
            parsed_data = await parse_event_text(event.raw_text, event.type)
            event.set_parsed(parsed_data)
            event.parse_status = "done"
        except Exception as e:
            event.parse_status = "error"
            event.set_parsed({"error": str(e)})

        session.add(event)
        session.commit()


def get_events_by_day(day_id: str) -> list[Event]:
    with Session(engine) as session:
        statement = select(Event).where(Event.day_id == day_id)
        return session.exec(statement).all()
