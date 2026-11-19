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

# Lo que completa el transportista con el link (preview del pase): el
# conductor con foto de licencia, el ayudante sin foto y el vehículo.
FOTO_LICENCIA = {"file_name": "licencia_qa.jpg", "file_url": "https://f001.backblazeb2.com/file/app-linkaform/licencia_qa.jpg"}
INFORMACION_TRANSPORTISTA_UNIT = {
    "record_id": PASE_ID,
    "conductor": {"nombre": "Conductor QA", "licencia": "LIC-QA-01", "foto": FOTO_LICENCIA},
    "ayudante": {"nombre": "Ayudante QA", "licencia": "LIC-QA-02", "foto": {}},
    "vehiculo": {"placas": "QA-TRANS-341", "marca": "Kenworth", "foto": {}},
}
# Contenedores que captura el transportista.
CONTENEDORES_TRANSPORTISTA = [
    {"numero": "QA-CONT-341", "sello": "QA-SELLO-341", "tipo": "dry_40"},
    {"numero": "QA-CONT-342", "sello": "QA-SELLO-342", "tipo": "reefer_20"},
]
