# coding: utf-8

"""
Datos de prueba para la sección Notas de Caseta (+ Nueva Nota, Pendientes,
Cerradas y Todos; script notes.py).
"""

from passes.integration.data.do_access_data import (  # noqa: F401
    LOCATION,
    AREA,
)

# Nota con el payload que arma el modal + Nueva Nota (add-note-modal.tsx →
# notes.ts crearNota): título, descripción como lista, caseta y status
# 'abierto'.
NOTA_NUEVA = {
    "note": "Nota de prueba QA",
    "note_comments": ["Comentario de prueba de la nota"],
    "note_booth": AREA,
    "note_status": "abierto",
    "note_file": [],
    "note_pic": [],
    "note_guard_close": "",
}

# La lista de notas del front consulta todas las áreas de la ubicación.
TODAS_LAS_AREAS = "todas"

# Estatus de la lista: Pendientes = abierto, Cerradas = cerrado.
ESTATUS_ABIERTO = "abierto"
ESTATUS_CERRADO = "cerrado"

# Registros por página al consultar la lista de notas (más nueva primero).
LIMITE_LISTA = 50
