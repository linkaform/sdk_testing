# coding: utf-8

"""
Entregar o donar un artículo perdido (update_article_lost:
devolucion-article-modal) sin tocar preprod: se simulan el empleado y el
guardado, y se revisa qué se manda a guardar en el folio del artículo.
Notion: TB-232.
"""

import pytest
from lkf_back import de

from ..data.perdidos_data import (
    FOLIO_ARTICULO,
    DEVOLUCION,
    DEVOLUCION_DONADO,
    ESTATUS_DONADO,
    EMPLEADO_PERDIDOS,
    EDICION_OK,
)


@pytest.mark.bug(1530)
def test_donar_articulo_con_el_estatus_del_front_lo_deja_donado_con_fecha(accesos_no_api, mocker):
    """
    TB-232: el botón Donado de devolucion-article-modal manda el estatus
    'Donado' con mayúscula; update_article_lost debe guardar 'donado' y la
    fecha de entrega. Ticket 2610-1530: solo reconoce 'donado' en minúscula,
    así que guarda 'Donado' (no sale en ningún filtro) y sin fecha.
    """
    acc = accesos_no_api
    mocker.patch.object(de(acc, "get_employee_data"), "get_employee_data", return_value=dict(EMPLEADO_PERDIDOS))
    guardar = mocker.patch.object(acc.lkf_api, "patch_multi_record", return_value={**EDICION_OK, "json": {}})

    res = acc.update_article_lost({**DEVOLUCION, "estatus_perdido": DEVOLUCION_DONADO}, FOLIO_ARTICULO)

    guardar.assert_called_once()
    f = acc.perdidos_fields
    answers = guardar.call_args.kwargs["answers"]
    assert answers[f["estatus_perdido"]] == ESTATUS_DONADO, f"El estatus quedó {answers[f['estatus_perdido']]!r}"
    assert res["json"]["date_entrega_perdido"], "El artículo donado no tiene fecha de entrega"
    assert answers.get(f["date_entrega_perdido"]) == res["json"]["date_entrega_perdido"], (
        "La fecha de entrega no se mandó a guardar"
    )
