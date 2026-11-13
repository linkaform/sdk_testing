# coding: utf-8

"""
Editar y cerrar una falla (update_failure: editar-falla y close-falla-modal)
sin tocar preprod: se simulan el empleado y el guardado, y se revisa qué se
manda a guardar en el folio de la falla.
Notion: TB-220 y TB-221.
"""

import pytest

from ..data.fallas_data import (
    FALLA_UNIT,
    FOLIO_FALLA,
    ESTATUS_ABIERTO,
    ESTATUS_RESUELTO,
    CERRAR_FALLA,
    EMPLEADO_FALLA,
    EDICION_OK,
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
    mocker.patch.object(acc, "get_employee_data", return_value=dict(EMPLEADO_FALLA))
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
