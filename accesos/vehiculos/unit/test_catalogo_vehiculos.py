# coding: utf-8

"""
Catálogo de vehículos por tipo y marca (vehiculo_marca y vehiculo_modelo, que
llaman los scripts get_vehiculos.py, pase_de_acceso.py y script_turnos.py con
la opción catalago_vehiculo) sin tocar la cuenta: se simula el catálogo y se
revisa qué se le pide.
Notion: TB-314 y TB-315.
"""

import pytest

from ..data.vehiculos_data import VEHICULO_VISITA


@pytest.mark.bug(1579)
def test_marcas_de_un_tipo_de_vehiculo_se_piden_al_catalogo_por_ese_tipo(accesos_no_api, mocker):
    """
    TB-314: vehiculo_marca debe pedir al catálogo de vehículos solo las
    marcas del tipo elegido (startkey con el tipo, group_level 2). Si truena o
    pide otra cosa, el selector de marca sale vacío o con marcas de otros
    tipos. Ticket 2610-1579: catalogo_vehiculos no recibe las opciones.
    """
    acc = accesos_no_api
    consultar = mocker.patch.object(acc.lkf_api, "catalog_view", return_value=[])

    acc.vehiculo_marca(VEHICULO_VISITA["tipo"])

    consultar.assert_called_once()
    opciones = consultar.call_args.args[2]
    assert opciones["startkey"] == [VEHICULO_VISITA["tipo"]]
    assert opciones["group_level"] == 2


@pytest.mark.bug(1579)
def test_modelos_de_una_marca_se_piden_al_catalogo_por_tipo_y_marca(accesos_no_api, mocker):
    """
    TB-315: vehiculo_modelo debe pedir al catálogo de vehículos solo los
    modelos del tipo y la marca elegidos (startkey con los dos, group_level
    3). Si truena o pide otra cosa, el selector de modelo sale vacío o con
    modelos de otras marcas. Ticket 2610-1579: catalogo_vehiculos no recibe
    las opciones.
    """
    acc = accesos_no_api
    consultar = mocker.patch.object(acc.lkf_api, "catalog_view", return_value=[])

    acc.vehiculo_modelo(VEHICULO_VISITA["tipo"], VEHICULO_VISITA["marca"])

    consultar.assert_called_once()
    opciones = consultar.call_args.args[2]
    assert opciones["startkey"] == [VEHICULO_VISITA["tipo"], VEHICULO_VISITA["marca"]]
    assert opciones["group_level"] == 3
