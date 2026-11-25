# coding: utf-8

"""
Datos de prueba para la sección Áreas (Disponibles y + Nueva Área; la sirve
Sanic con update_area_sdk.py y rondines_sdk.py).
"""

from pases_entrada.data.datos_base import (  # noqa: F401
    LOCATION,
    AREA,
)

# record_id de un área (get_area_by_id lo convierte a ObjectId).
AREA_RECORD_ID = "6915a0c1e4b0a1b2c3d4e5f6"

# Áreas de la ubicación como las regresa get_areas_details, en desorden de
# creación (el folio "NNN-x" es consecutivo: más alto = más reciente).
AREAS_DE_UBICACION = [
    {"_id": "a1", "folio": "9-10", "area": "Caseta Principal", "ubicacion": LOCATION},
    {"_id": "a2", "folio": "12-10", "area": "Almacén", "ubicacion": LOCATION},
    {"_id": "a3", "folio": "10-10", "area": "Estacionamiento", "ubicacion": LOCATION},
]

# Área guardada antes de "Múltiple ubicación" y "Utilizar Área en": el
# registro no trae esos campos.
AREA_SIN_USOS = {
    "_id": AREA_RECORD_ID,
    "folio": "12-10",
    "area": AREA,
    "ubicacion": LOCATION,
    "tipo_de_area": "Caseta",
    "area_state": "activa",
    "area_status": "disponible",
}

# data que arma la ruta /create_area de Sanic con el payload de + Nueva Área.
AREA_NUEVA = {
    "ubicacion": LOCATION,
    "nombre_nueva_area": AREA,
    "tipo_de_area": "Caseta",
    "foto_area": [],
    "qr_area": "",
    "multiple_ubicacion": "no",
    "direccion": "",
    "usos": [],
}

# Respuesta de LinkaForm cuando guarda o edita el área.
GUARDADO_OK = {"status_code": 202}
# Cambios del modal de edición: solo nombre y tipo.
EDICION_PARCIAL = {"nombre": "Caseta Principal QA editada", "tipo_de_area": "Estacionamiento"}
ESTADO_INACTIVA = "inactiva"
DISPONIBILIDAD_MANTENIMIENTO = "mantenimiento"

# Chips del buscador de Disponibles (get_search_counts_areas): un conteo por
# candidato {key, value, exact}, como los manda useFacetSection.
CANDIDATOS_BUSCADOR = [
    {"key": "tipo", "value": "Caseta", "exact": True},
    {"key": "disponibilidad", "value": "disponible", "exact": True},
]

# Filtro Tag/QR del panel (dynamic_filters de get_catalog_areas_formatted).
FILTRO_SOLO_TAG = [{"key": "tipo_identificador", "value": ["tag"]}]
FILTRO_SOLO_QR = [{"key": "tipo_identificador", "value": ["qr"]}]
FILTRO_TAG_Y_QR = [{"key": "tipo_identificador", "value": ["tag", "qr"]}]

# Pestaña Incidencias del área (get_incidencias_by_area): el área como la
# regresa get_area_by_id y dos rondines como los regresa la consulta. Tres
# incidencias son de AREA y una de otra área del mismo rondín.
OTRA_AREA = "Almacén"
AREA_DETALLE = {"_id": AREA_RECORD_ID, "rondin_area": AREA, "ubicacion": LOCATION}
RONDINES_CON_INCIDENCIAS = [
    {
        "_id": "r1",
        "folio": "101-10",
        "ubicacion": LOCATION,
        "nombre_recorrido": "Recorrido QA",
        "incidencias_rondin": [
            {"area_salida": AREA, "incidencia": "Puerta abierta"},
            {"area_salida": OTRA_AREA, "incidencia": "Luz fundida"},
        ],
    },
    {
        "_id": "r2",
        "folio": "102-10",
        "ubicacion": LOCATION,
        "nombre_recorrido": "Recorrido QA",
        "incidencias_rondin": [
            {"area_salida": AREA, "incidencia": "Candado roto"},
            {"area_salida": AREA, "incidencia": "Cámara sin señal"},
        ],
    },
]
# El front pide la pestaña con limit=0 (IncidenciasAreaDashboard.tsx): todas.
LIMIT_TODAS = 0
