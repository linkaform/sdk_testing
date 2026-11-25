# coding: utf-8

"""
Agregar un seguimiento a una incidencia (Agregar seguimiento del detalle;
update_incidence_seguimiento en Sanic) sin tocar la cuenta: se simulan la
incidencia de antes y el guardado, y se revisa qué se manda a guardar.
Notion: TB-393 a TB-395.
"""

import pytest

from .helpers import seguimiento_simulado
from ..data.incidencias_data import (
    FOLIO_INCIDENCIA,
    GUARDIA_SESION,
    SEGUIMIENTO_EXISTENTE,
    SEGUIMIENTO_NUEVO,
    INCIDENCIA_CON_SEGUIMIENTO,
    ESTATUS_ABIERTO,
    FOLIO_INEXISTENTE,
    SEGUIMIENTO_VACIO,
)

pytestmark = pytest.mark.back("sanic")


@pytest.mark.unit
@pytest.mark.target("update_incidence_seguimiento")
def test_un_seguimiento_nuevo_se_suma_a_los_existentes(accesos_no_api, mocker):
    """
    TB-393: agregar un seguimiento debe guardar los que ya tenía la
    incidencia más el nuevo. El que ya existía conserva a quien lo registró y
    el nuevo lo registra el guardia de la sesión. Si guarda solo el nuevo, se
    pierde el historial de seguimientos.
    """
    acc = accesos_no_api
    guardar = seguimiento_simulado(acc, mocker, [dict(INCIDENCIA_CON_SEGUIMIENTO)])

    acc.update_incidence_seguimiento(FOLIO_INCIDENCIA, dict(SEGUIMIENTO_NUEVO), ESTATUS_ABIERTO)

    f = acc.incidence_fields
    seguimientos = guardar.call_args.args[0]["answers"][f["seguimientos_incidencia"]]
    assert [s[f["accion_correctiva_incidencia"]] for s in seguimientos] == [
        SEGUIMIENTO_EXISTENTE["accion_correctiva_incidencia"],
        SEGUIMIENTO_NUEVO["accion_correctiva_incidencia"],
    ]
    assert [s[f["registrado_por_seguimiento"]] for s in seguimientos] == [
        SEGUIMIENTO_EXISTENTE["registrado_por"],
        GUARDIA_SESION,
    ]


@pytest.mark.unit
@pytest.mark.target("update_incidence_seguimiento")
def test_un_seguimiento_a_un_folio_que_no_existe_da_error_y_no_guarda(accesos_no_api, mocker):
    """
    TB-394: si la incidencia del folio no existe (por ejemplo, la borraron
    mientras el detalle estaba abierto), agregar un seguimiento debe responder
    "No hay una incidencia registrada." sin mandar nada a guardar.
    """
    acc = accesos_no_api
    guardar = seguimiento_simulado(acc, mocker, [])

    with pytest.raises(Exception, match="No hay una incidencia"):
        acc.update_incidence_seguimiento(FOLIO_INEXISTENTE, dict(SEGUIMIENTO_NUEVO), ESTATUS_ABIERTO)

    guardar.assert_not_called()


@pytest.mark.unit
@pytest.mark.target("update_incidence_seguimiento")
def test_un_seguimiento_vacio_no_truena(accesos_no_api, mocker):
    """
    TB-395: si el seguimiento llega vacío (incidencias_sdk.py pone [] cuando
    no viene la llave), update_incidence_seguimiento debe responder un error
    claro o ignorarlo. Hoy lo envuelve en [[]] y truena con AttributeError
    al leer el seguimiento como diccionario.
    """
    acc = accesos_no_api
    seguimiento_simulado(acc, mocker, [dict(INCIDENCIA_CON_SEGUIMIENTO)])

    try:
        acc.update_incidence_seguimiento(FOLIO_INCIDENCIA, list(SEGUIMIENTO_VACIO), ESTATUS_ABIERTO)
    except AttributeError as e:
        pytest.fail(f"Un seguimiento vacío truena: {e}")
    except Exception:
        pass
