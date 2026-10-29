# coding: utf-8

"""
Datos del modal "Nueva Visita" (assets_access_pass) sin tocar preprod: se
simulan las áreas, los anfitriones y la configuración de la ubicación.
Notion: TB-079.
"""

import pytest

from ..data.nuevo_acceso_data import (
    LOCATION,
    AREAS_SIMULADAS,
    ANFITRIONES_SIMULADOS,
)


@pytest.mark.unit
def test_assets_access_pass_sin_configuracion_no_truena(accesos_no_api, mocker):
    """
    TB-079: si falla la configuración de la ubicación, assets_access_pass
    debe regresar las áreas y los anfitriones con perfiles, requerimientos y
    envíos vacíos. Hoy el except asigna 'Perfiles' (con mayúscula) y el
    return usa 'perfiles', lo que da UnboundLocalError y el modal no carga.
    """
    mocker.patch.object(accesos_no_api, "get_areas_by_location", return_value=AREAS_SIMULADAS)
    mocker.patch.object(
        accesos_no_api.Employee, "get_users_by_location_area", return_value=ANFITRIONES_SIMULADOS
    )
    mocker.patch.object(
        accesos_no_api, "get_config_modulo_seguridad", side_effect=Exception("config no disponible")
    )

    assets = accesos_no_api.assets_access_pass(LOCATION)

    assert assets["Areas"] == AREAS_SIMULADAS
    assert assets["Visita_a"] == [a["name"] for a in ANFITRIONES_SIMULADOS]
    assert assets["Perfiles"] == []
    assert assets["requerimientos"] == []
    assert assets["envios"] == []
