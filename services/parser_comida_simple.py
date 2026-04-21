from datetime import datetime
import re


def clasificar_comida_por_hora(dt: datetime):
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


def detectar_hora_en_texto(texto: str):
    match = re.search(r'(\d{1,2})(?::(\d{2}))?', texto)
    if match:
        hora = int(match.group(1))
        minuto = int(match.group(2)) if match.group(2) else 0
        if 0 <= hora <= 23:
            return hora, minuto
    return None


def detectar_tipo_por_palabra(texto: str):
    t = texto.lower()
    if "desayuno" in t:
        return "desayuno"
    if "almuerzo" in t:
        return "almuerzo"
    if "merienda" in t:
        return "merienda"
    if "cena" in t:
        return "cena"
    if "bajon" in t:
        return "bajon_nocturno"
    return None


def extraer_alimentos_basico(texto: str):
    palabras = texto.lower().replace(",", "").split()
    stopwords = [
        "comi", "comí", "comer", "comiendo",
        "desayuno", "almuerzo", "merienda", "cena",
        "a", "las", "de", "con", "y", "en"
    ]
    alimentos = [p for p in palabras if p not in stopwords and len(p) > 2]
    return [{"nombre": a, "categoria": "desconocido"} for a in alimentos]


def crear_registro_manual(texto: str, now: datetime):
    hora_detectada = detectar_hora_en_texto(texto)
    dt = now.replace(hour=hora_detectada[0], minute=hora_detectada[1]) if hora_detectada else now

    tipo_texto = detectar_tipo_por_palabra(texto)
    tipo_por_hora = clasificar_comida_por_hora(dt)
    tipo_final = tipo_texto if tipo_texto else tipo_por_hora
    inconsistencia = bool(tipo_texto and tipo_texto != tipo_por_hora)

    return {
        "fecha": dt.strftime("%Y-%m-%d"),
        "hora": dt.strftime("%H:%M"),
        "timestamp": dt.isoformat(),
        "tipo_comida": tipo_final,
        "alimentos": extraer_alimentos_basico(texto),
        "origen": "manual",
        "texto_original": texto,
        "hora_detectada": bool(hora_detectada),
        "tipo_detectado_por_texto": bool(tipo_texto),
        "inconsistencia_tipo_hora": inconsistencia,
        "confirmado": True,
    }
