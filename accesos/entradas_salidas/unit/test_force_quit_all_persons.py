# coding: utf-8

"""
Salida masiva (force_quit_all_persons) sin tocar preprod: se simulan la
consulta a Mongo y el guardado, porque la función real cierra visitas de
toda la cuenta.
Notion: TB-072.
"""

import pytest

from ..data.bitacora_data import VISITAS_ABIERTAS_OTRAS_UBICACIONES


@pytest.mark.unit
@pytest.mark.parametrize("location", ["", None], ids=["ubicacion_vacia", "ubicacion_none"])
def test_force_quit_sin_ubicacion_no_cierra_otras_ubicaciones(accesos_no_api, mocker, location):
    """
    TB-072: sin ubicación, la salida masiva no debe cerrar las visitas
    abiertas de otras ubicaciones de la cuenta. Puede rechazar la llamada,
    pero no guardar la salida de esas visitas.
    """
    mocker.patch.object(accesos_no_api.cr, "aggregate", return_value=VISITAS_ABIERTAS_OTRAS_UBICACIONES)
    guardar = mocker.patch.object(
        accesos_no_api.lkf_api, "patch_multi_record", return_value={"status_code": 202, "json": {}}
    )

    try:
        accesos_no_api.force_quit_all_persons(location=location)
    except Exception:
        pass

    assert not guardar.called, (
        f"Sin ubicación registró la salida de {len(guardar.call_args.kwargs['record_id'])} visitas de toda la cuenta"
    )
