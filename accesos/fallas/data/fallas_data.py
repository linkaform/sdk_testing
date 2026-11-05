# coding: utf-8

"""
Datos de prueba para la sección Fallas de Seguridad (+ Nueva Falla, Abiertas,
Cerradas y Todos; script fallas.py).
"""

from passes.integration.data.do_access_data import (  # noqa: F401
    LOCATION,
    AREA,
)

# Falla con el payload que arma el modal + Nueva Falla (add-falla.tsx →
# fallas.ts crearFalla). El tipo de falla y el objeto afectado se toman en el
# fixture de una falla que ya existe en la ubicación (valores reales del
# catálogo); quién reporta y el responsable, del empleado del usuario. La
# fecha y el comentario se llenan en el fixture.
FALLA_NUEVA = {
    "falla": "",
    "falla_caseta": AREA,
    "falla_comentarios": "",
    "falla_documento": [],
    "falla_estatus": "abierto",
    "falla_evidencia": [],
    "falla_fecha_hora": "",
    "falla_objeto_afectado": "",
    "falla_reporta_nombre": "",
    "falla_responsable_solucionar_nombre": "",
    "falla_ubicacion": LOCATION,
    "falla_grupo_seguimiento": [],
}

# Las fallas de estas pruebas llevan un sufijo único por corrida en el
# comentario para encontrar solo la suya.
COMENTARIO_FALLA = "Falla de prueba QA"

# Estatus de la lista: Abiertas = abierto, Cerradas = resuelto, Todos = sin filtro.
ESTATUS_ABIERTO = "abierto"

# La lista del front pagina y filtra con el buscador (facets); el comentario
# escrito va con exact False ("contiene").
FACET_COMENTARIOS = "falla_comentarios"
LIMITE_LISTA = 50
