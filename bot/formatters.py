# bot/formatters.py

from telegram import Update
from bot.keyboards import main_kb


def resumen(data: dict) -> str:
    txt = "📅 Resumen del día:\n"

    if data["registros"]:
        for r in data["registros"]:
            alimentos = ", ".join([a["nombre"] for a in r.get("alimentos", [])])
            txt += f"🍽 {r.get('tipo_comida')} → {alimentos}\n"
    else:
        txt += "🍽 Sin comidas\n"

    txt += "\n"
    m = data.get("metrics", {})
    txt += (
        f"📊 Estado: "
        f"Energía {m.get('energia')} | "
        f"Aire {m.get('breath')} | "
        f"Hinchado {m.get('hinchado')} | "
        f"Frío {m.get('bano_frio')}"
    )

    return txt


async def reset(update: Update, msg: str, data: dict):
    return await update.message.reply_text(
        msg + "\n\n" + resumen(data),
        reply_markup=main_kb()
    )
