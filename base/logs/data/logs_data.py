# coding: utf-8

"""
Datos de prueba para la sección Logs (Script Log y Workflow Log; scripts
script_logs_sdk.py y workflow_logs_sdk.py de Sanic).
"""

from datetime import datetime

# Nombres que resuelve _name_maps con la API: scripts que el usuario puede ver
# y usuarios de la cuenta.
SCRIPTS_VISIBLES = {101: "Cierre de turno", 102: "Alta de usuario", 103: "Cierre masivo de pases"}
USUARIOS_CUENTA = {10: "Seguridad QA"}

# Filtro de fechas del Script Log (YYYY-MM-DD) y el rango que debe consultar:
# del inicio del primer día al último milisegundo del día final.
FECHA_INICIO = "2026-11-01"
FECHA_FIN = "2026-11-02"
DESDE = datetime(2026, 11, 1)
HASTA = datetime(2026, 11, 2, 23, 59, 59, 999000)

# Buscar por nombre de script (sin mayúsculas): "cierre" está en dos de los
# tres scripts visibles.
NOMBRE_SCRIPT = "CIERRE"
IDS_CON_ESE_NOMBRE = {101, 103}

# Logs guardados en script_log (lo mínimo que lee list_script_logs).
LOGS_GUARDADOS = [
    {"_id": "6a0000000000000000000371", "script_id": 101, "user_id": 10, "status": "done", "traceback": ""},
    {"_id": "6a0000000000000000000372", "script_id": 102, "user_id": 10, "status": "done", "traceback": ""},
    {"_id": "6a0000000000000000000373", "script_id": 103, "user_id": 10, "status": "done", "traceback": ""},
]
# Página de 2 logs cuando hay 3: hay página siguiente.
LOGS_POR_PAGINA = 2
