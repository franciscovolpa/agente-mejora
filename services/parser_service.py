import asyncio
from typing import Optional


async def parse_event_text(text: str, event_type: str) -> dict:
    """
    Stub: simula parsing con LLM.
    Reemplazar el body por una llamada real a OpenAI/Anthropic.
    Firma no cambia.
    """
    await asyncio.sleep(0.5)  # simula latencia de red

    # Mock: extrae palabras clave simples
    result = {
        "original": text,
        "type": event_type,
        "tokens": text.lower().split(),
        "confidence": 0.95,
        "mock": True,
    }

    # Lógica mock por tipo
    if event_type == "food":
        result["items"] = _mock_extract_food(text)
    elif event_type == "mood":
        result["score"] = _mock_mood_score(text)

    return result


def _mock_extract_food(text: str) -> list[str]:
    keywords = ["arroz", "pollo", "ensalada", "pasta", "carne", "fruta", "huevo"]
    return [w for w in keywords if w in text.lower()]


def _mock_mood_score(text: str) -> int:
    positive = ["bien", "genial", "contento", "feliz", "energía"]
    negative = ["mal", "cansado", "bajo", "ansioso", "stress"]
    score = 5
    for w in positive:
        if w in text.lower():
            score += 1
    for w in negative:
        if w in text.lower():
            score -= 1
    return max(1, min(10, score))
