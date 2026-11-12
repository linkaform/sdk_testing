# coding: utf-8

"""
Paginación de la lista de Entradas & Salidas (get_list_bitacora): se simula
la consulta a Mongo y se revisa qué se pide y qué se regresa.
Notion: TB-267 y TB-268.
"""

import pytest

from ..data.bitacora_data import LOCATION, AREA, POR_PAGINA


def mongo_simulado(acceso_obj, mocker, respuestas):
    """Reemplaza la conexión a Mongo; cada llamada a aggregate regresa la siguiente respuesta."""
    cr = mocker.MagicMock()
    cr.aggregate.side_effect = respuestas
    mocker.patch.object(acceso_obj, "cr", cr, create=True)
    return cr


@pytest.mark.unit
def test_paginacion_invalida_se_rechaza_sin_consultar(accesos_no_api, mocker):
    """
    TB-267: limit y offset deben ser enteros (limit mayor a 0, offset 0 o
    más). Con texto, cero, negativos o True, get_list_bitacora debe detenerse
    con "Paginación inválida" y no consultar Mongo. Si consulta, Mongo
    truena con un error que el guardia no entiende.
    """
    cr = mongo_simulado(accesos_no_api, mocker, [])

    for limit, offset in ((str(POR_PAGINA), 0), (0, 0), (POR_PAGINA, -1), (True, 0)):
        with pytest.raises(Exception, match="Paginaci"):
            accesos_no_api.get_list_bitacora(LOCATION, AREA, limit=limit, offset=offset)
    cr.aggregate.assert_not_called()
