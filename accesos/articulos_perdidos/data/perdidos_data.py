# coding: utf-8

"""
Datos de prueba para la sección Artículos Perdidos de Activos (+ Nuevo
Artículo, Pendientes, Entregados y Todos; script articulos_perdidos.py).
"""

from passes.integration.data.do_access_data import (  # noqa: F401
    LOCATION,
    AREA,
    FOTO_VALIDA,
    IDENTIFICACION_VALIDA,
)

# Artículo con el payload que arma el modal + Nuevo Artículo
# (add-article-lost.tsx → articulos-perdidos.ts crearArticuloPerdido). El
# tipo de artículo y el artículo se toman en el fixture de un artículo que ya
# existe en la ubicación (valores reales del catálogo); el nombre lleva un
# sufijo único por corrida y la fecha de hallazgo se llena en el fixture.
# color_perdido sale de catalogoColores() del front; quien_entrega "externo"
# es el default del modal.
ARTICULO_NUEVO = {
    "area_perdido": AREA,
    "articulo_perdido": "",
    "articulo_seleccion": "",
    "color_perdido": "Azul",
    "comentario_perdido": "Artículo de prueba QA",
    "date_hallazgo_perdido": "",
    "descripcion": "Artículo encontrado en la caseta durante la prueba",
    "estatus_perdido": "pendiente",
    "foto_perdido": [],
    "locker_perdido": "",
    "quien_entrega": "externo",
    "quien_entrega_externo": "Visitante QA",
    "quien_entrega_interno": "",
    "tipo_articulo_perdido": "",
    "ubicacion_perdido": LOCATION,
}
NOMBRE_ARTICULO = "Artículo perdido QA"

# Lo que manda devolucion-article-modal al entregar el artículo.
DEVOLUCION = {
    "foto_recibe_perdido": FOTO_VALIDA,
    "identificacion_recibe_perdido": IDENTIFICACION_VALIDA,
    "recibe_perdido": "Persona que recibe QA",
    "telefono_recibe_perdido": "8110000099",
}
DEVOLUCION_ENTREGADO = "entregado"

# Estatus de la lista: Pendientes = pendiente, Entregados = entregado,
# Todos = sin filtro.
ESTATUS_PENDIENTE = "pendiente"
ESTATUS_ENTREGADO = "entregado"

# La lista del front pagina y filtra con el buscador (facets); el nombre
# escrito va con exact False ("contiene").
FACET_NOMBRE = "articulo_perdido"
LIMITE_LISTA = 50
