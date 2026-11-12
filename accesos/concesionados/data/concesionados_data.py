# coding: utf-8

"""
Datos de prueba de los unitarios de Artículos Concesionados (+ Nueva
Concesión, Pendientes, Parciales, Devueltos y Todos; script
articulos_consecionados.py).
"""

from passes.integration.data.do_access_data import (  # noqa: F401
    LOCATION,
    AREA,
    FOTO_VALIDA,
)

# Filtro de la lista: segunda ubicación del selector del header y estados de
# las pestañas (Pendientes = abierto, Todos = sin estado).
OTRA_UBICACION = "Planta Durango"
ESTADO_ABIERTO = "abierto"
ESTADO_TODOS = ""

# Folio de una concesión que se manda a borrar.
FOLIO_CONCESION = "1-CONCESION"
