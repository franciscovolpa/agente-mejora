from datetime import datetime, date
from typing import Optional
from sqlmodel import SQLModel, Field
import json


class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    day_id: str  # "YYYY-MM-DD"

    type: str  # "food" | "mood" | "note" | "activity"
    source: str  # "telegram" | "manual"

    raw_text: str
    parsed: Optional[str] = None  # JSON string (SQLite no tiene JSON nativo)
    parse_status: str = Field(default="pending")  # "pending" | "done" | "error"

    def get_parsed(self) -> Optional[dict]:
        if self.parsed:
            return json.loads(self.parsed)
        return None

    def set_parsed(self, data: dict):
        self.parsed = json.dumps(data, ensure_ascii=False)


class EventCreate(SQLModel):
    text: str
    type: str = "note"
    source: str = "manual"


class EventRead(SQLModel):
    id: int
    timestamp: datetime
    day_id: str
    type: str
    source: str
    raw_text: str
    parse_status: str
    parsed: Optional[str] = None
