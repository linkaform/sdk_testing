# coding: utf-8

"""
Validaciones de la salida (do_out) sin tocar preprod: se simula la última
visita del pase y se revisa que no se guarde la salida cuando no debe.
Notion: TB-185.
"""

import pytest

from ..data.bitacora_data import (
    LOCATION,
    AREA,
    VISITA_ABIERTA_DURACION,
    GAFETE_SIN_DEVOLVER,
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
