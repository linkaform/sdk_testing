# coding: utf-8

"""
Crear una falla (create_failure, + Nueva Falla) sin tocar preprod: se simula
el guardado y se revisan los answers que se mandan a la forma.
Notion: TB-217 a TB-219.
"""

import pytest

from ..data.fallas_data import LOCATION, AREA, FALLA_UNIT, METADATA_FALLAS, GUARDADO_OK


@pytest.mark.unit
def test_crear_falla_guarda_la_ubicacion_y_la_caseta_juntas(accesos_no_api, mocker):
    """
    TB-217: con ubicación y caseta, create_failure debe guardar las dos en
    el catálogo de ubicaciones. Si se pierde una, la falla no aparece al
    filtrar por esa ubicación o caseta.
    """
    acc = accesos_no_api
    mocker.patch.object(acc.lkf_api, "get_metadata", return_value=dict(METADATA_FALLAS))
    guardar = mocker.patch.object(acc.lkf_api, "post_forms_answers", return_value=dict(GUARDADO_OK))

    acc.create_failure(dict(FALLA_UNIT))

    answers = guardar.call_args.args[0]["answers"]
    assert answers[acc.fallas_fields["falla_ubicacion_catalog"]] == {
        acc.fallas_fields["falla_ubicacion"]: LOCATION,
        acc.fallas_fields["falla_caseta"]: AREA,
    }, f"El catálogo de ubicaciones quedó {answers[acc.fallas_fields['falla_ubicacion_catalog']]}"
