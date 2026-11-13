# coding: utf-8

"""
Datos de prueba de la sección Rondines (unitarios; script rondines_sdk.py de
Sanic). Los de integración viven en integration/data/.
"""

from pases_entrada.data.datos_base import (  # noqa: F401
    LOCATION,
    AREA,
)

# Guardia que inicia (reclama) el rondín y el usuario que regresa get_user_by_id.
USER_ID_GUARDIA = 15864
USUARIO_GUARDIA = {"name": "Guardia de prueba QA", "email": "guardia.qa@ejemplo.com"}

# Registros de la Bitácora de Rondines (ObjectId en texto).
RONDIN_ID = "6a1000000000000000000001"
HERMANO_ID = "6a1000000000000000000002"
PADRE_ID = "6a1000000000000000000003"

# Respuestas simuladas de patch_multi_record.
PATCH_OK = {"status_code": 202}
PATCH_ERROR = {"status_code": 400, "json": {"error": "simulado"}}

# Rondín nuevo (Configuración de recorridos) como lo manda el front al crear.
RONDIN_NUEVO = {
    "nombre_rondin": "Rondín de prueba QA",
    "ubicacion": LOCATION,
    "areas": [AREA],
    "tipo_rondin": "Recorrido",
}
GRUPO_RONDIN = "Guardias turno A"
ROLES_RONDIN = ["Guardia", "Supervisor"]
PERSONA_RONDIN = "Juan Escutia"
