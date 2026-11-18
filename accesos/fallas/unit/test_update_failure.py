# coding: utf-8

"""
Editar y cerrar una falla (update_failure: editar-falla y close-falla-modal)
y agregarle un seguimiento (update_failure_seguimiento:
add-seguimiento-falla-cerrar) sin tocar preprod: se simulan el empleado y el
guardado, y se revisa qué se manda a guardar en el folio de la falla.
Notion: TB-221 y TB-222.
"""

import pytest
from lkf_back import de

from ..data.fallas_data import (
    FALLA_UNIT,
    FOLIO_FALLA,
    ESTATUS_ABIERTO,
    ESTATUS_RESUELTO,
    CERRAR_FALLA,
    EMPLEADO_FALLA,
    EDICION_OK,
    SEGUIMIENTO_UNIT,
    FALLA_REGISTRADA,
)


@pytest.mark.bug(1521)
def test_cerrar_falla_la_deja_resuelta_con_fecha_de_solucion(accesos_no_api, mocker):
    """
    TB-221: al cerrar una falla con close-falla-modal ({falla_estatus:
    'resuelto'}), update_failure debe guardar 'resuelto' y la fecha de
    solución en el folio de la falla. Ticket 2610-1521: falla_fecha_hora_solucion
    no existe en fallas_fields, así que truena con KeyError y la falla no se
    cierra.
    """
    acc = accesos_no_api
    mocker.patch.object(de(acc, "get_employee_data"), "get_employee_data", return_value=dict(EMPLEADO_FALLA))
    guardar = mocker.patch.object(acc.lkf_api, "patch_multi_record", return_value={**EDICION_OK, "json": {}})

    res = acc.update_failure(dict(CERRAR_FALLA), FOLIO_FALLA)

    guardar.assert_called_once()
    answers = guardar.call_args.kwargs["answers"]
    assert answers[acc.fallas_fields["falla_estatus"]] == ESTATUS_RESUELTO, (
        f"El estatus quedó {answers[acc.fallas_fields['falla_estatus']]!r}"
    )
    fecha_solucion = res["json"]["falla_fecha_hora_solucion"]
    assert fecha_solucion, "La falla cerrada no tiene fecha de solución"
    assert fecha_solucion in answers.values(), "La fecha de solución no se mandó a guardar"


@pytest.mark.bug(1535)
def test_agregar_seguimiento_guarda_la_accion_y_la_fecha_que_manda_el_front(accesos_no_api, mocker):
    """
    TB-222: add-seguimiento-falla-cerrar manda el seguimiento con
    accion_correctiva_incidencia y fecha_inicio_seg; update_failure_seguimiento
    debe guardarlo en el grupo de seguimientos de la falla con esa acción y esa
    fecha. Ticket 2610-1535: el back lee otras llaves
    (falla_folio_accion_correctiva, fechaInicioFallaCompleta) y usa
    falla_inicio_seguimiento, que no existe en fallas_fields, así que el
    seguimiento no se guarda.
    """
    acc = accesos_no_api
    mocker.patch.object(de(acc, "get_employee_data"), "get_employee_data", return_value=dict(EMPLEADO_FALLA))
    mocker.patch.object(acc, "get_list_fallas", return_value=[dict(FALLA_REGISTRADA)])
    mocker.patch.object(acc.lkf_api, "get_metadata", return_value={})
    mocker.patch.object(acc, "get_record_by_folio", return_value={})
    guardar = mocker.patch.object(acc.net, "patch_forms_answers", return_value={**EDICION_OK, "json": {}})

    acc.update_failure_seguimiento(
        location="", area="", status=ESTATUS_ABIERTO, folio=FOLIO_FALLA, falla_grupo_seguimiento=dict(SEGUIMIENTO_UNIT)
    )

    guardar.assert_called_once()
    metadata = guardar.call_args.args[0]
    assert metadata["_id"] == FALLA_REGISTRADA["_id"], "El seguimiento se mandó a otro registro"
    f = acc.fallas_fields
    seguimientos = metadata["answers"][f["falla_grupo_seguimiento"]]
    assert len(seguimientos) == 1, f"La falla quedó con {len(seguimientos)} seguimientos, se agregó 1"
    assert seguimientos[0].get(f["falla_accion_realizada"]) == SEGUIMIENTO_UNIT["accion_correctiva_incidencia"], (
        f"La acción del seguimiento quedó {seguimientos[0].get(f['falla_accion_realizada'])!r}"
    )
    assert seguimientos[0].get(f["falla_fecha_seguimiento"]) == SEGUIMIENTO_UNIT["fecha_inicio_seg"], (
        f"La fecha del seguimiento quedó {seguimientos[0].get(f['falla_fecha_seguimiento'])!r}"
    )
