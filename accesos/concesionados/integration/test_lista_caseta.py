# coding: utf-8

"""
Lista de Artículos Concesionados con una caseta seleccionada en el header
(get_list_articulos_concesionados con area).
Notion: TB-244.
"""

import copy
import uuid

import pytest

from .data.concesiones_data import CONCESION_BASE_OTRO, NOMBRE_CONCESION_CASETA
from .helpers import concesion_de_la_lista


@pytest.mark.integration
def test_concesion_aparece_al_filtrar_por_su_caseta(accesos_api):
    """
    TB-244: una concesión creada en una caseta debe aparecer en la lista
    cuando el guardia selecciona esa caseta en el header, no solo con
    "todas". Si no aparece, la lista de Concesionados se queda vacía en
    cuanto se elige una caseta.
    """
    concesion = copy.deepcopy(CONCESION_BASE_OTRO["data_artilce"])
    persona = f"{NOMBRE_CONCESION_CASETA} {uuid.uuid4().hex[:8]}"
    concesion["persona_nombre_otro"] = persona
    ubicacion, caseta = concesion["ubicacion_concesion"], concesion["caseta_concesion"]

    res = accesos_api.create_article_concessioned(concesion)
    assert res.get("status_code") == 201, f"No se pudo crear la concesión: {res}"

    creada = concesion_de_la_lista(accesos_api, persona, ubicacion)
    assert creada, "La concesión nueva no aparece en la lista con todas las casetas"
    try:
        en_caseta = concesion_de_la_lista(accesos_api, persona, ubicacion, area=caseta)
        assert en_caseta, f"La concesión no aparece al filtrar por su caseta '{caseta}'"
    finally:
        accesos_api.delete_article_concessioned([creada["folio"]])
