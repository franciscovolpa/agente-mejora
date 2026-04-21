from services.storage_v2 import load_day, get_today


def get_today_summary() -> str:
    fecha = get_today()
    data, path = load_day(fecha)

    if not path.exists():
        return f"📅 {fecha}\n\nTodavía no hay registros para hoy."

    return _format_day(data)


def _format_day(data: dict) -> str:
    lines = [f"📅 {data['fecha']}", ""]

    # Comidas
    registros = data.get("registros", [])
    if registros:
        lines.append(f"🍽 Comidas ({len(registros)}):")
        for r in registros:
            nombres = ", ".join(a["nombre"] for a in r.get("alimentos", []))
            lines.append(f"  {r.get('tipo_comida', '?')}  {r.get('hora', '')}  →  {nombres}")
    else:
        lines.append("🍽 Sin comidas registradas")

    lines.append("")

    # Estado
    lines.append(_format_metrics(data.get("metrics", {})))

    lines.append("")

    # Notas
    notes = data.get("notes", "").strip()
    lines.append(f"📝 {notes}" if notes else "📝 Sin notas")

    return "\n".join(lines)


def _format_metrics(metrics: dict) -> str:
    presente = {k: v for k, v in metrics.items() if v is not None}
    if not presente:
        return "📊 Estado: sin registro"

    labels = {
        "energia":   "⚡ Energía",
        "breath":    "💨 Aire",
        "hinchado":  "🫃 Hinchado",
        "bano_frio": "🚿 Baño frío",
    }
    lines = ["📊 Estado:"]
    for k, v in presente.items():
        label = labels.get(k, k)
        display = ("sí" if v else "no") if isinstance(v, bool) else f"{v}/10"
        lines.append(f"  {label}: {display}")
    return "\n".join(lines)
