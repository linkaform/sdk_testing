# coding: utf-8

"""
Datos de prueba para la sección Fallas de Seguridad (+ Nueva Falla, Abiertas,
Cerradas y Todos; script fallas.py).
"""

from passes.integration.data.do_access_data import (  # noqa: F401
    LOCATION,
    AREA,
    FOTO_VALIDA,
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
COMENTARIO_EDITADO = "Falla de prueba QA editada"

# Estatus de la lista: Abiertas = abierto, Cerradas = resuelto, Todos = sin filtro.
ESTATUS_ABIERTO = "abierto"
ESTATUS_RESUELTO = "resuelto"
ESTATUS_TODOS = ""

# Seguimiento con el payload de add-seguimiento-falla-cerrar.tsx (un solo
# seguimiento por envío, sin cerrar la falla: status 'abierto'). La fecha y
# el tiempo transcurrido se llenan en el helper: una hora después de la falla,
# con el formato de calcularTiempoDesdeIncidencia del front.
SEGUIMIENTO_FALLA = {
    "accion_correctiva_incidencia": "Se cambió la pieza dañada (prueba QA)",
    "incidencia_personas_involucradas": "Guardia de prueba QA",
    "incidencia_documento_solucion": [],
    "incidencia_evidencia_solucion": FOTO_VALIDA,
}
TIEMPO_SEGUIMIENTO = "1 hora(s)"

# Lo que manda el botón de close-falla-modal (update_failure).
CERRAR_FALLA = {"falla_estatus": "resuelto"}

# La lista del front pagina y filtra con el buscador (facets); el comentario
# escrito va con exact False ("contiene").
FACET_COMENTARIOS = "falla_comentarios"
LIMITE_LISTA = 50

# Unitarios del filtro y el borrado (fallas/unit). OTRA_UBICACION es la segunda
# ubicación del selector del header; FOLIOS_FALLA son los que manda
# delete-falla-modal y REGISTROS_FALLA el _id de cada uno.
OTRA_UBICACION = "Planta Durango"
FOLIO_FALLA = "1-FALLA"
FOLIOS_FALLA = ["1-FALLA", "2-FALLA"]
REGISTROS_FALLA = {
    "1-FALLA": "000000000000000000000011",
    "2-FALLA": "000000000000000000000012",
}
URL_REGISTRO = "/api/infosync/form_answer/{}/"
BORRADO_OK = {"status_code": 202}
