# coding: utf-8

"""
Datos de los unitarios de guardias de apoyo en el turno (agregar un guardia
con update_guards_checkin y darle salida con do_checkout). Aparte de
turnos_data.py para no chocar con los cambios de Turnos B.
"""

from pases_entrada.data.datos_base import LOCATION, AREA  # noqa: F401

# Turno abierto en la caseta: _id del registro y zona con la que se creó.
TURNO_ID = "000000000000000000000071"
ZONA_TURNO = "America/Monterrey"

# Guardia principal del turno y guardia de apoyo que agrega add-guard-modal
# (support_guards [{user_id, name}]).
GUARDIA_PRINCIPAL_ID = 1001
GUARDIA_APOYO_ID = 1002
GUARDIA_APOYO = {"user_id": GUARDIA_APOYO_ID, "name": "Guardia de apoyo QA"}

ESTATUS_ENTRADA = "entrada"
ESTATUS_SALIDA = "salida"
GUARDADO_OK = {"status_code": 202}
ASISTENCIA_OK = "Correcto"
