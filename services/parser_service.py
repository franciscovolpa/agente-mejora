import asyncio
import re
import unicodedata


SPANISH_STOPWORDS = {
    "a", "al", "algo", "algunas", "algunos", "ante", "con", "contra", "cual", "cuando",
    "de", "del", "desde", "donde", "el", "ella", "ellas", "ellos", "en", "entre", "era",
    "eramos", "eran", "eres", "es", "esa", "esas", "ese", "eso", "esos", "esta", "estaba",
    "estaban", "estado", "estais", "estamos", "estan", "estar", "estas", "este", "esto", "estos",
    "fue", "fueron", "ha", "hace", "hacen", "hacia", "hay", "la", "las", "le", "les", "lo",
    "los", "me", "mi", "mis", "mucho", "muy", "nada", "ni", "no", "nos", "nosotros", "o",
    "os", "otra", "otro", "para", "pero", "poco", "por", "porque", "que", "se", "si", "sin",
    "sobre", "soy", "su", "sus", "tambien", "te", "tenia", "tengo", "ti", "tu", "tus", "un",
    "una", "uno", "unos", "y", "ya", "yo",
}

COMPOSITE_FOODS = [
    "arroz con pollo",
    "tortilla de patatas",
    "ensalada de frutas",
    "jugo de naranja",
    "cafe con leche",
]

SINGLE_FOOD_KEYWORDS = {
    "arroz", "pollo", "ensalada", "pasta", "carne", "fruta", "frutas", "huevo", "huevos",
    "naranja", "cafe", "leche", "tortilla", "patatas",
}


async def parse_event_text(text: str, event_type: str) -> dict:
    """
    Stub: simula parsing con LLM.
    Reemplazar el body por una llamada real a OpenAI/Anthropic.
    Firma no cambia.
    """
    await asyncio.sleep(0.5)  # simula latencia de red

    extracted_tokens = extract_tokens(text)
    normalized_tokens = normalize_tokens(extracted_tokens)

    # Mantener contrato: keys esperadas por consumidores actuales
    result = {
        "original": text,
        "type": event_type,
        "tokens": normalized_tokens,
        "confidence": 0.95,
        "mock": True,
    }

    # Lógica mock por tipo
    if event_type == "food":
        result["items"] = _mock_extract_food(text)
    elif event_type == "mood":
        result["score"] = _mock_mood_score(normalized_tokens)

    return result


def extract_tokens(text: str) -> list[str]:
    """Extrae tokens crudos (sin stopword filtering)."""
    normalized_text = _normalize_text(text)
    return re.findall(r"[a-z0-9]+", normalized_text)


def normalize_tokens(tokens: list[str]) -> list[str]:
    """Normaliza tokens removiendo stopwords y ruido."""
    normalized: list[str] = []
    for token in tokens:
        if len(token) <= 1:
            continue
        if token in SPANISH_STOPWORDS:
            continue
        normalized.append(token)
    return normalized


def _normalize_text(text: str) -> str:
    lower = text.lower()
    without_accents = unicodedata.normalize("NFKD", lower).encode("ascii", "ignore").decode("ascii")
    return without_accents


def _mock_extract_food(text: str) -> list[str]:
    normalized_text = _normalize_text(text)
    tokens = set(extract_tokens(text))
    detected: list[str] = []

    # Priorizar compuestos
    for food in COMPOSITE_FOODS:
        if food in normalized_text:
            detected.append(food)

    # Sumar ingredientes individuales solo si aparecen
    for token in SINGLE_FOOD_KEYWORDS:
        if token in tokens and token not in detected:
            detected.append(token)

    return detected


def _mock_mood_score(tokens: list[str]) -> int:
    positive = {"bien", "genial", "contento", "feliz", "energia"}
    negative = {"mal", "cansado", "bajo", "ansioso", "stress"}
    token_set = set(tokens)

    score = 5
    score += len(positive.intersection(token_set))
    score -= len(negative.intersection(token_set))

    return max(1, min(10, score))
