# coding: utf-8

"""
Datos de prueba para la sección Notas de Caseta (+ Nueva Nota, Pendientes,
Cerradas y Todos; script notes.py).
"""

from passes.integration.data.do_access_data import (  # noqa: F401
    LOCATION,
    AREA,
    FOTO_VALIDA,
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
# Todos = sin filtro de estatus (/notas sin ?status).
ESTATUS_TODOS = ""

# Registros por página al consultar la lista de notas (más nueva primero).
LIMITE_LISTA = 50

# Zona con la que el modal Cerrar nota arma note_close_date (close-note-modal.tsx).
ZONA_FECHA_CIERRE = "America/Mexico_City"

# Edición desde el modal Editar nota (edit-note-modal.tsx → notes.ts
# editarNota): título nuevo, la descripción como lista (así la manda el front)
# y una foto de evidencia (imagen que ya existe en preprod).
NOTA_EDITADA = {
    "note": "Nota de prueba QA editada",
    "note_comments": ["Comentario agregado al editar la nota"],
    "note_file": [],
    "note_pic": FOTO_VALIDA,
}

# Buscador de notas (notas/page.tsx → useFacetSection, script notes.py). El
# texto escrito va como facet {key, values, exact False} ("contiene"); los
# conteos usan las ubicaciones del header (locations) sin location ni área.
FACET_NOTA = "note"
FACET_CASETA = "note_booth"
# Las notas del buscador llevan un sufijo único por corrida para que la
# búsqueda solo traiga la suya.
NOTA_BUSCADOR = "Nota buscador QA"

# Unitarios (sin red): empleado que regresa get_employee_data, fecha que
# regresa today_str y folio de la nota que se edita o se cierra. La zona del
# empleado es distinta a la del usuario para revisar que se use la suya.
EMPLEADO_NOTA = {"worker_name": "Guardia de prueba QA", "timezone": "America/Cancun"}
FECHA_SERVIDOR = "2026-11-10 09:30:00"
FOLIO_NOTA = "588-10"
# Lo que manda close-note-modal al cerrar: su propia fecha (zona de CDMX) y
# el estatus. El backend debe guardar la fecha en la zona del empleado.
CERRAR_NOTA = {"note_close_date": "2026-11-10 08:30:00", "note_status": "cerrado"}
# La descripción de + Nueva Nota con dos comentarios (el front la manda como lista).
COMENTARIOS_NOTA = ["Primer comentario de prueba", "Segundo comentario de prueba"]
