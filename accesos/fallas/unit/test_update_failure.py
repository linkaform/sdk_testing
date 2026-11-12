# coding: utf-8

"""
Editar y cerrar una falla (update_failure: editar-falla y close-falla-modal)
sin tocar preprod: se simulan el empleado y el guardado, y se revisa qué se
manda a guardar en el folio de la falla.
Notion: TB-220 y TB-221.
"""

import pytest

from ..data.fallas_data import FALLA_UNIT, FOLIO_FALLA, ESTATUS_ABIERTO, EMPLEADO_FALLA, EDICION_OK


@pytest.mark.unit
def test_editar_falla_sin_cerrarla_la_deja_abierta_y_sin_fecha_de_solucion(accesos_no_api, mocker):
    """
    TB-220: al editar una falla con el payload de editar-falla (estatus
    'abierto'), update_failure debe guardar el estatus 'abierto' en el folio
    de la falla y no ponerle fecha de solución. Si le pone fecha, la falla
    parece resuelta aunque siga abierta.
    """
    acc = accesos_no_api
    mocker.patch.object(acc, "get_employee_data", return_value=dict(EMPLEADO_FALLA))
    guardar = mocker.patch.object(acc.lkf_api, "patch_multi_record", return_value={**EDICION_OK, "json": {}})

    res = acc.update_failure({**FALLA_UNIT, "falla_estatus": ESTATUS_ABIERTO}, FOLIO_FALLA)

    guardar.assert_called_once()
    assert guardar.call_args.kwargs["folios"] == [FOLIO_FALLA]
    assert guardar.call_args.kwargs["form_id"] == acc.BITACORA_FALLAS
    answers = guardar.call_args.kwargs["answers"]
    assert answers[acc.fallas_fields["falla_estatus"]] == ESTATUS_ABIERTO, (
        f"El estatus quedó {answers[acc.fallas_fields['falla_estatus']]!r}"
    )
    assert res["json"]["falla_fecha_hora_solucion"] == "", (
        f"La falla abierta quedó con fecha de solución {res['json']['falla_fecha_hora_solucion']!r}"
    )
