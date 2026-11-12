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

# Concesión como la arma + Nueva Concesión para un empleado, con un equipo.
# El front manda la foto y el comentario del préstamo con los nombres de los
# campos de Devoluciones (evidencia_entrega, comentario_entrega);
# marca_equipo_concesion no es del grupo de equipos en préstamo.
COMENTARIO_PRESTAMO = "Préstamo de prueba QA"
EQUIPO_CONCESION = {
    "categoria_equipo_concesion": "Artículos de Oficina",
    "nombre_equipo": "Linterna",
    "cantidad_equipo_concesion": 3,
    "evidencia_entrega": FOTO_VALIDA,
    "comentario_entrega": COMENTARIO_PRESTAMO,
    "marca_equipo_concesion": "Marca de prueba QA",
}
CONCESION_EMPLEADO = {
    "ubicacion_concesion": LOCATION,
    "caseta_concesion": AREA,
    "persona_nombre_concesion": "Empleado de prueba QA",
    "fecha_concesion": "2026-11-12 10:00:00",
}
CONCESION_OTRO = {
    "ubicacion_concesion": LOCATION,
    "caseta_concesion": AREA,
    "persona_nombre_otro": "Visitante de prueba QA",
    "fecha_concesion": "2026-11-12 10:00:00",
}
METADATA_CONCESION = {}
GUARDADO_OK = {"status_code": 201}
