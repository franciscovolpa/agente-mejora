# Agente de Mejora Continua

## Estado actual
Backend FastAPI funcionando con:

- POST /event
- GET /event/{id}
- background parsing (parse_status: pending → done)
- SQLite storage
- separación en services

## Flujo actual
1. se recibe texto
2. se guarda raw_text
3. se ejecuta parser async
4. se guarda parsed (JSON estructurado)

## Decisiones importantes
- raw_text nunca se pierde
- parsed debe ser JSON (no string)
- parser desacoplado (service)

## Próximo paso
- conectar bot de Telegram al endpoint /event

## Notas
Este sistema está en fase MVP.
No se busca sobreingeniería, sino iteración rápida sobre datos reales.