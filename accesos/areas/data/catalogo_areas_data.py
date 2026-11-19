# coding: utf-8

"""
Datos de los tests de bugs del catálogo de áreas y del estatus del área
(Disponibles; get_catalog_areas_formatted y update_area_estado en Sanic).
"""

from pases_entrada.data.datos_base import LOCATION, AREA  # noqa: F401

# Otra ubicación con un área del mismo nombre que la de LOCATION.
OTRA_UBICACION = "Planta Durango"
AREAS_HOMONIMAS = [
    {"_id": "a1", "folio": "1-10", "area": AREA, "ubicacion": LOCATION},
    {"_id": "a2", "folio": "2-10", "area": AREA, "ubicacion": OTRA_UBICACION},
]
AREA_RECORD_ID = "6915a0c1e4b0a1b2c3d4e5f6"
ESTADO_VACIO = ""
