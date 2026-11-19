# coding: utf-8

"""
Estatus del área (activar o desactivar desde Disponibles; update_area_estado
en Sanic) sin tocar la cuenta: se simula el guardado.
Notion: TB-345.
"""

import pytest

from ..data.catalogo_areas_data import (
    AREA_RECORD_ID,
    ESTADO_VACIO,
)

pytestmark = pytest.mark.back("sanic")


@pytest.mark.bug(1607)
def test_cambiar_estatus_del_area_con_valor_vacio_no_lo_borra(accesos_no_api, mocker):
    """
    TB-345: update_area_estado (ruta /update_area_estado) no valida el valor:
    con estado vacío manda guardar el campo vacío y borra el estatus del área.
    Debe rechazar un estado que no sea activa o inactiva sin llamar al
    guardado; /update_full_area sí lo valida.
    Ticket 2611-1607.
    """
    acc = accesos_no_api
    guardar = mocker.patch.object(acc.lkf_api, "patch_multi_record", return_value={"status_code": 202})

    try:
        acc.update_area_estado(AREA_RECORD_ID, ESTADO_VACIO)
    except Exception:
        pass

    guardar.assert_not_called()
