# services/backend_client.py
"""
Cliente HTTP para POST /event al backend FastAPI.
Si el backend falla → devuelve None → el bot sigue con storage_v2 sin enterarse.
"""
import httpx
import logging
import json

log = logging.getLogger(__name__)

BACKEND_URL = "http://localhost:8000"
TIMEOUT = 4.0


async def post_event(raw_text: str, event_type: str, parsed: dict, source: str = "telegram") -> dict | None:
    """
    Envía evento al backend.
    - raw_text: texto original del usuario (o descripción de la foto)
    - event_type: "food" | "mood" | "note" | "activity"
    - parsed: dict ya estructurado por los parsers existentes
    """
    payload = {
        "text": raw_text,
        "type": event_type,
        "source": source,
    }
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # 1. crear evento (guarda raw_text)
            r = await client.post(f"{BACKEND_URL}/event", json=payload)
            r.raise_for_status()
            result = r.json()
            event_id = result["id"]

            # 2. si ya tenemos parsed local, lo subimos directo (no espera al LLM)
            if parsed:
                await client.patch(
                    f"{BACKEND_URL}/event/{event_id}/parsed",
                    json={"parsed": json.dumps(parsed, ensure_ascii=False), "parse_status": "done"}
                )

            return result

    except httpx.TimeoutException:
        log.warning("Backend timeout")
        return None
    except httpx.HTTPStatusError as e:
        log.error(f"Backend HTTP {e.response.status_code}: {e.response.text}")
        return None
    except Exception as e:
        log.error(f"Backend no disponible: {e}")
        return None
