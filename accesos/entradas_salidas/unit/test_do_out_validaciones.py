# coding: utf-8

"""
Validaciones de la salida (do_out) sin tocar preprod: se simula la última
visita del pase y se revisa que no se guarde la salida cuando no debe.
Notion: TB-185 a TB-187.
"""

import pytest

from ..data.bitacora_data import (
    LOCATION,
    AREA,
    VISITA_ABIERTA_DURACION,
    GAFETE_SIN_DEVOLVER,
    OTRA_UBICACION_ENTRADA,
)


@pytest.mark.unit
def test_no_se_registra_la_salida_si_no_se_ha_devuelto_el_gafete(accesos_no_api, mocker):
    """
    TB-185: si la visita tiene el gafete asignado y no se ha devuelto,
    do_out debe detenerse con el aviso de liberar el gafete y no guardar la
    salida. Si la guarda, la persona sale con el gafete y queda 'En Uso'.
    """
    visita = {**VISITA_ABIERTA_DURACION, "status_gafete": GAFETE_SIN_DEVOLVER}
    mocker.patch.object(accesos_no_api, "get_last_user_move", return_value=visita)
    guardar = mocker.patch.object(accesos_no_api.lkf_api, "patch_multi_record")

    with pytest.raises(Exception, match="liberar el gafete"):
        accesos_no_api.do_out(VISITA_ABIERTA_DURACION["folio"], LOCATION, AREA)
    guardar.assert_not_called()


@pytest.mark.unit
def test_no_se_puede_salir_por_otra_ubicacion_distinta_a_la_de_entrada(accesos_no_api, mocker):
    """
    TB-186: si la persona entró por otra ubicación, do_out en una caseta de
    esta ubicación debe detenerse con el aviso de dónde ingresó y no guardar
    la salida. Si la guarda, la bitácora registra una salida por un lugar
    por el que la persona no entró.
    """
    visita = {**VISITA_ABIERTA_DURACION, "ubicacion_entrada": OTRA_UBICACION_ENTRADA}
    mocker.patch.object(accesos_no_api, "get_last_user_move", return_value=visita)
    mocker.patch.object(accesos_no_api, "get_booth_locations", return_value=[LOCATION])
    guardar = mocker.patch.object(accesos_no_api.lkf_api, "patch_multi_record")

    with pytest.raises(Exception, match="no puede salir en"):
        accesos_no_api.do_out(VISITA_ABIERTA_DURACION["folio"], LOCATION, AREA)
    guardar.assert_not_called()


@pytest.mark.unit
def test_sin_entrada_registrada_la_salida_responde_un_error_claro(accesos_no_api, mocker):
    """
    TB-187: si el pase no tiene una entrada registrada en la ubicación,
    do_out debe detenerse con el aviso de que no hay entrada y no guardar
    nada. Si truena con otro error, el guardia no sabe por qué no puede
    registrar la salida.
    """
    mocker.patch.object(accesos_no_api, "get_last_user_move", return_value={})
    guardar = mocker.patch.object(accesos_no_api.lkf_api, "patch_multi_record")

    with pytest.raises(Exception, match="no tiene una entrada registrada"):
        accesos_no_api.do_out(VISITA_ABIERTA_DURACION["folio"], LOCATION, AREA)
    guardar.assert_not_called()
