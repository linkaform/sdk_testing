# coding: utf-8

"""
Crear una falla (create_failure, + Nueva Falla) sin tocar preprod: se simula
el guardado y se revisan los answers que se mandan a la forma.
Notion: TB-217 a TB-219.
"""

import pytest

from ..data.fallas_data import LOCATION, AREA, FALLA_UNIT, SEGUIMIENTO_UNIT, METADATA_FALLAS, GUARDADO_OK


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


@pytest.mark.unit
def test_crear_falla_guarda_la_falla_quien_reporta_y_el_responsable(accesos_no_api, mocker):
    """
    TB-218: create_failure debe guardar la falla con su objeto afectado en el
    catálogo de fallas, y quién reporta y el responsable de solucionarla en
    sus catálogos de empleados. Si falta uno, nadie sabe qué falló o a quién
    le toca resolverlo.
    """
    acc = accesos_no_api
    campos = acc.fallas_fields
    mocker.patch.object(acc.lkf_api, "get_metadata", return_value=dict(METADATA_FALLAS))
    guardar = mocker.patch.object(acc.lkf_api, "post_forms_answers", return_value=dict(GUARDADO_OK))

    acc.create_failure(dict(FALLA_UNIT))

    answers = guardar.call_args.args[0]["answers"]
    assert answers[campos["falla_catalog"]] == {
        campos["falla"]: FALLA_UNIT["falla"],
        campos["falla_subconcepto"]: FALLA_UNIT["falla_objeto_afectado"],
    }, f"El catálogo de fallas quedó {answers[campos['falla_catalog']]}"
    assert answers[campos["falla_reporta_catalog"]] == {
        campos["falla_reporta_nombre"]: FALLA_UNIT["falla_reporta_nombre"],
    }, f"Quién reporta quedó {answers[campos['falla_reporta_catalog']]}"
    assert answers[campos["falla_responsable_solucionar_catalog"]] == {
        campos["falla_responsable_solucionar_nombre"]: FALLA_UNIT["falla_responsable_solucionar_nombre"],
    }, f"El responsable quedó {answers[campos['falla_responsable_solucionar_catalog']]}"


@pytest.mark.unit
def test_crear_falla_con_seguimiento_lo_guarda_con_lo_que_manda_el_front(accesos_no_api, mocker):
    """
    TB-219: add-falla.tsx manda los seguimientos con las llaves
    accion_correctiva_incidencia, fecha_inicio_seg y tiempo_transcurrido.
    create_failure debe guardarlos en el grupo de seguimiento con la acción,
    la fecha y el tiempo transcurrido. Si quedan vacíos, se pierde lo que ya
    se hizo para resolver la falla.
    """
    acc = accesos_no_api
    campos = acc.fallas_fields
    mocker.patch.object(acc.lkf_api, "get_metadata", return_value=dict(METADATA_FALLAS))
    guardar = mocker.patch.object(acc.lkf_api, "post_forms_answers", return_value=dict(GUARDADO_OK))

    acc.create_failure({**FALLA_UNIT, "falla_grupo_seguimiento": [dict(SEGUIMIENTO_UNIT)]})

    seguimientos = guardar.call_args.args[0]["answers"][campos["falla_grupo_seguimiento"]]
    assert len(seguimientos) == 1, f"Se guardaron {len(seguimientos)} seguimientos, se mandó 1"
    seguimiento = seguimientos[0]
    assert seguimiento[campos["falla_accion_realizada"]] == SEGUIMIENTO_UNIT["accion_correctiva_incidencia"]
    assert seguimiento[campos["falla_fecha_seguimiento"]] == SEGUIMIENTO_UNIT["fecha_inicio_seg"]
    assert seguimiento[campos["falla_tiempo_transcurrido"]] == SEGUIMIENTO_UNIT["tiempo_transcurrido"]
