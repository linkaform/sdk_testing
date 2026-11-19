# coding: utf-8

"""
Datos de los unitarios de Transportistas – Nuevo Pase (pase-entrada-transportista
→ transportistas_sdk.py en Sanic).
"""

from control_patio.data.control_patio_data import PASE_TRANSPORTISTA

# El pase como lo arma el front, con fecha, horario y andén de entrega.
FECHA_ENTREGA = "2026-11-20"
ANDEN_ENTREGA = "Andén 1"
PASE_TRANSPORTISTA_UNIT = {
    **PASE_TRANSPORTISTA,
    "lugar_entrega_recepcion": {
        **PASE_TRANSPORTISTA["lugar_entrega_recepcion"],
        "fecha_pase_transportista_desde": FECHA_ENTREGA,
        "horario_disponible": "08:00 - 10:00",
        "anden": ANDEN_ENTREGA,
    },
}
PASE_ID = "000000000000000000000091"
GUARDADO_OK = {"status_code": 201}
