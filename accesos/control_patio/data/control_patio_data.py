# coding: utf-8

"""
Datos de prueba para la sección Transportistas – Control de patio
(bitácora de transportistas, script transportistas.py).
"""

from passes.integration.data.do_access_data import (  # noqa: F401
    LOCATION,
    AREA,
)

# Llegada de un camión sin pase, con el payload que arma el front en
# "Nuevo Acceso Transportista" (nuevo-acceso-transportista-modal.tsx).
# Placas únicas de esta suite para encontrarlo en el patio.
LLEGADA_SIN_PASE = {
    "creado_desde": "acceso_web",
    "tipo_operacion": "Entrega",
    "ubicacion": LOCATION,
    "area": AREA,
    "vehiculo": {
        "transportista": "Transportes prueba QA",
        "procedencia": "Monterrey",
        "tipo_vehiculo": "Tractocamión",
        "placa": "QA-PATIO-087",
        "no_economico": "QA-087",
        "marca": "Kenworth",
        "modelo": "2020",
        "color": "Blanco",
        "placa_tarjeta_circulacion": None,
    },
    "conductor": {
        "nombre": "Conductor prueba patio",
        "celular": None,
        "no_licencia": None,
        "vigencia_licencia": None,
        "rfc": None,
        "acompanante": None,
    },
    "embarque": {
        "proveedor_cliente": None,
        "no_orden_compra": None,
    },
    "documentos_adicionales": [],
    "remolques": [],
    "contenedores": [],
    "materiales": [],
}

# Estatus en que queda el camión al registrar su llegada y al descartarlo.
ESTATUS_ARRIBO = "arribo"
ESTATUS_DESCARTADO = "descartado"
