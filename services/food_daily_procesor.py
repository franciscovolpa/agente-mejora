import os
import json
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
from pillow_heif import register_heif_opener

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("Falta GEMINI_API_KEY en .env")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")


def _clasificar_comida(dt: datetime) -> str:
    h = dt.hour
    if 5 <= h <= 10:
        return "desayuno"
    elif 11 <= h <= 15:
        return "almuerzo"
    elif 16 <= h <= 19:
        return "merienda"
    elif 20 <= h <= 23:
        return "cena"
    else:
        return "bajon_nocturno"


def _extraer_json(texto: str) -> dict:
    texto = texto.strip()
    start = texto.find("{")
    end = texto.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No se encontró JSON en respuesta:\n{texto}")
    return json.loads(texto[start:end + 1])


def analizar_imagen_comida(ruta_imagen, timestamp=None) -> dict:
    register_heif_opener()

    dt = timestamp if timestamp else datetime.now()
    tipo_comida = _clasificar_comida(dt)

    prompt = f"""
Analizá la imagen y devolvé únicamente JSON. Tu tarea es SOLO detección visual.

Reglas:
- nombre: en español, singular, minúsculas. Ejemplos: "arroz blanco cocido", "pechuga de pollo", "huevo frito"
- nombre_en: mismo alimento en inglés estandarizado, para mapping a base nutricional. Ejemplos: "cooked white rice", "chicken breast", "fried egg"
- proporcion_visual_pct: porcentaje visual del plato. Todos los ítems deben sumar 100.
- porcion_relativa: tamaño estimado de la porción. Valores: "pequeña" | "mediana" | "grande" | "muy grande"
- No calcules macros ni calorías.
- No agregues texto fuera del JSON.

Devolvé exactamente esta estructura:

{{
  "fecha": "{dt.date()}",
  "hora": "{dt.strftime('%H:%M')}",
  "tipo_comida": "{tipo_comida}",
  "alimentos": [
    {{
      "nombre": "string",
      "nombre_en": "string",
      "proporcion_visual_pct": number,
      "porcion_relativa": "pequeña | mediana | grande | muy grande"
    }}
  ]
}}
"""

    try:
        img = Image.open(ruta_imagen).convert("RGB")
        response = model.generate_content(
            [prompt, img],
            generation_config={"temperature": 0.1},
        )
        if not response.text:
            raise ValueError("Respuesta vacía del modelo")

        resultado = _extraer_json(response.text)
        resultado["fecha"] = dt.strftime("%Y-%m-%d")
        resultado["hora"] = dt.strftime("%H:%M")
        resultado["tipo_comida"] = tipo_comida
        return resultado

    except Exception as e:
        return {
            "fecha": dt.strftime("%Y-%m-%d"),
            "hora": dt.strftime("%H:%M"),
            "tipo_comida": tipo_comida,
            "alimentos": [
                {"nombre": "error_deteccion", "nombre_en": "detection_error", "proporcion_visual_pct": 100, "porcion_relativa": "mediana"}
            ],
            "error": True,
            "error_msg": str(e),
        }
