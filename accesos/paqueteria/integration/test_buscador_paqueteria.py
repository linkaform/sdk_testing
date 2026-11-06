# coding: utf-8

"""
Buscador de la lista de paquetería (get_search_fields_paqueteria,
get_search_counts_paqueteria y get_paquetes con facets, como el front).
Notion: TB-157.
"""

import pytest

from .fixtures import *
from ..data.paqueteria_data import (
    LOCATION,
    ESTATUS_TODOS,
    FACET_DESCRIPCION,
    LIMITE_LISTA,
)


@pytest.mark.integration
def test_buscador_de_paqueteria_encuentra_el_paquete(acceso_obj, paquete_guardado):
    """
    TB-157: el buscador ofrece el campo Descripción y, al escribir la
    descripción de un paquete, lo cuenta y lo trae. Si no, el guardia no
    encuentra el paquete cuando el destinatario viene por él.
    """
    descripcion = paquete_guardado["descripcion_paqueteria"]

    campos = {c["key"]: c for c in acceso_obj.get_search_fields_paqueteria()}
    assert FACET_DESCRIPCION in campos, f"El buscador no ofrece el campo '{FACET_DESCRIPCION}': {sorted(campos)}"
    assert campos[FACET_DESCRIPCION]["type"] == "text"

    candidato = {"key": FACET_DESCRIPCION, "value": descripcion, "exact": False}
    conteo = acceso_obj.get_search_counts_paqueteria(
        location="", area="", status=ESTATUS_TODOS, locations=[LOCATION], facets=[], candidates=[candidato]
    )
    assert conteo == [1], f"El buscador cuenta {conteo} paquetes con la descripción '{descripcion}'"

    facets = [{"key": FACET_DESCRIPCION, "values": [descripcion], "exact": False}]
    lista = acceso_obj.get_paquetes("", "", ESTATUS_TODOS, limit=LIMITE_LISTA, locations=[LOCATION], facets=facets)
    assert [p["folio"] for p in lista["records"]] == [paquete_guardado["folio"]], (
        f"El buscador trae {[p['folio'] for p in lista['records']]}, se esperaba solo {paquete_guardado['folio']}"
    )
