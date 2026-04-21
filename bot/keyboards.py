# bot/keyboards.py

from telegram import ReplyKeyboardMarkup


def main_kb():
    return ReplyKeyboardMarkup(
        [["🍽 Comida", "🧠 Estado"], ["📝 Nota"]],
        resize_keyboard=True
    )


def comida_kb():
    return ReplyKeyboardMarkup(
        [
            ["🥞 Desayuno", "🍝 Almuerzo"],
            ["☕ Merienda", "🍽 Cena"],
            ["🌙 Bajón"]
        ],
        resize_keyboard=True
    )


def confirmar_kb():
    return ReplyKeyboardMarkup(
        [["✅ Correcto", "✏️ Editar"]],
        resize_keyboard=True
    )


TIPO_COMIDA_MAP = {
    "🥞 Desayuno": "desayuno",
    "🍝 Almuerzo": "almuerzo",
    "☕ Merienda": "merienda",
    "🍽 Cena": "cena",
    "🌙 Bajón": "bajon_nocturno",
}
