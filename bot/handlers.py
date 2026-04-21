# bot/handlers.py

import logging
from datetime import datetime
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

from services.state_manager import set_state, get_state, clear_state
from services.parser_comida_simple import crear_registro_manual
from services.parser_sensaciones import crear_metrics
from services.storage_v2 import load_day, save_day, get_today
from services.food_daily_procesor import analizar_imagen_comida
from services.insight_service import get_today_summary

from bot.keyboards import main_kb, comida_kb, confirmar_kb, TIPO_COMIDA_MAP
from bot.formatters import reset
from services.backend_client import post_event

PHOTOS_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "telegram_photos"

log = logging.getLogger(__name__)


async def cmd_hoy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_today_summary())


# ================= SYNC HELPER =================

async def _sync(raw_text: str, event_type: str, parsed: dict):
    """Fire-and-forget hacia el backend. Si falla, storage_v2 ya guardó."""
    result = await post_event(raw_text, event_type, parsed)
    if result:
        log.info(f"Backend sync OK → event id {result.get('id')}")
    else:
        log.warning(f"Backend sync falló para '{raw_text[:50]}' — solo en storage_v2")


# ================= EDITOR INTELIGENTE =================

def editar_alimentos(lista_original: list, texto: str) -> list:
    alimentos = [a["nombre"].lower() for a in lista_original]
    t = texto.lower()

    if "cambiar" in t and "por" in t:
        try:
            viejo = t.split("cambiar")[1].split("por")[0].strip()
            nuevo = t.split("por")[1].strip()
            alimentos = [nuevo if viejo in a else a for a in alimentos]
        except Exception:
            pass
    elif "agregar" in t:
        alimentos.append(t.replace("agregar", "").strip())
    elif "sacar" in t or "quitar" in t:
        alimentos = [a for a in alimentos if a not in t]
    else:
        alimentos = [x.strip() for x in texto.split(",")]

    return [{"nombre": a, "categoria": "manual"} for a in alimentos]


# ================= COMANDOS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_state(update.effective_user.id)
    await update.message.reply_text("¿Qué querés registrar?", reply_markup=main_kb())


# ================= TEXTO =================

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    texto = update.message.text
    estado = get_state(user_id)
    now = datetime.now()

    fecha = get_today()
    data, path = load_day(fecha)

    # ── Comida: entrada al flujo ──
    if texto == "🍽 Comida":
        set_state(user_id, {"mode": "comida", "step": "tipo"})
        return await update.message.reply_text("¿Qué comida es?", reply_markup=comida_kb())

    # ── Comida: selección de tipo ──
    if estado.get("mode") == "comida" and estado.get("step") == "tipo":
        tipo = TIPO_COMIDA_MAP.get(texto)
        if tipo:
            estado.update({"tipo_comida": tipo, "step": "input"})
            set_state(user_id, estado)
            return await update.message.reply_text("Mandá foto o escribí")

    # ── Comida: confirmar foto ──
    if estado.get("step") == "confirmar":
        resultado = estado["foto_resultado"]

        if texto == "✅ Correcto":
            data["registros"].append(resultado)
            save_day(data, path)
            await _sync(resultado.get("texto_original", "foto"), "food", resultado)
            clear_state(user_id)
            return await reset(update, "📸 Guardado", data)

        if texto == "✏️ Editar":
            lista = "\n".join(f"- {a['nombre']}" for a in resultado.get("alimentos", []))
            estado["mode"] = "editar"
            set_state(user_id, estado)
            return await update.message.reply_text(f"Detecté:\n{lista}\n\nEditá:")

    # ── Comida: editar alimentos ──
    if estado.get("mode") == "editar":
        resultado = estado["foto_resultado"]
        resultado["alimentos"] = editar_alimentos(resultado.get("alimentos", []), texto)
        data["registros"].append(resultado)
        save_day(data, path)
        await _sync(texto, "food", resultado)
        clear_state(user_id)
        return await reset(update, "✏️ Corregido", data)

    # ── Estado: entrada al flujo ──
    if texto == "🧠 Estado":
        set_state(user_id, {"mode": "estado", "step": "energia"})
        return await update.message.reply_text("Energía (1-10)?")

    # ── Estado: flujo numérico ──
    if estado.get("mode") == "estado":
        step = estado.get("step")

        if step == "bano":
            estado["bano"] = texto.lower() in ["si", "s"]
            metrics = crear_metrics(
                estado["energia"], estado["aire"], estado["hinchado"], estado["bano"]
            )
            data["metrics"] = metrics
            save_day(data, path)
            raw = f"estado: e={estado['energia']} a={estado['aire']} h={estado['hinchado']} b={estado['bano']}"
            await _sync(raw, "mood", metrics)
            clear_state(user_id)
            return await reset(update, "✅ Estado guardado", data)

        try:
            val = int(texto)
        except ValueError:
            return await update.message.reply_text("Número inválido")

        next_step = {"energia": ("aire", "Aire (1-10)?"),
                     "aire":   ("hinchado", "Hinchado (1-10)?"),
                     "hinchado": ("bano", "¿Baño frío? (si/no)")}

        if step in next_step:
            estado[step] = val
            estado["step"] = next_step[step][0]
            set_state(user_id, estado)
            return await update.message.reply_text(next_step[step][1])

    # ── Comida: input texto ──
    if estado.get("mode") == "comida" and estado.get("step") == "input":
        reg = crear_registro_manual(texto, now)
        reg["tipo_comida"] = estado.get("tipo_comida")
        data["registros"].append(reg)
        save_day(data, path)
        await _sync(texto, "food", reg)
        clear_state(user_id)
        return await reset(update, "🍽 Guardado", data)

    # ── Nota ──
    if texto == "📝 Nota":
        set_state(user_id, {"mode": "nota"})
        return await update.message.reply_text("Escribí nota")

    if estado.get("mode") == "nota":
        data["notes"] += f"\n[{now.strftime('%H:%M')}] {texto}"
        save_day(data, path)
        await _sync(texto, "note", {"nota": texto, "hora": now.strftime("%H:%M")})
        clear_state(user_id)
        return await reset(update, "📝 Nota guardada", data)

    return await reset(update, "No entendí", data)


# ================= FOTO =================

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    estado = get_state(user_id)

    if estado.get("mode") != "comida":
        return await update.message.reply_text("Primero seleccioná comida")

    await update.message.reply_text("🧠 Analizando...")

    file = await context.bot.get_file(update.message.photo[-1].file_id)
    now = datetime.now()
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    img_path = PHOTOS_DIR / (now.strftime("%Y%m%d_%H%M%S") + ".jpg")
    await file.download_to_drive(img_path)

    resultado = analizar_imagen_comida(img_path, timestamp=now)
    resultado["tipo_comida"] = estado.get("tipo_comida")

    estado.update({"foto_resultado": resultado, "step": "confirmar"})
    set_state(user_id, estado)

    alimentos = ", ".join(a["nombre"] for a in resultado.get("alimentos", []))
    await update.message.reply_text(f"Detecté: {alimentos}", reply_markup=confirmar_kb())
