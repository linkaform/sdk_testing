# coding: utf-8

"""
Editar una entrada de la bitácora (update_bitacora_entrada): agregar o editar
vehículos y equipos de una visita.
Notion: TB-064 a TB-067.
"""

import pytest

from .fixtures import *
from ..data.bitacora_data import LOCATION, AREA, VEHICULO_PRUEBA, EQUIPO_PRUEBA, EQUIPO_EDITADO
from .helpers import ultima_visita, salida_silenciosa


@pytest.mark.integration
def test_update_bitacora_entrada_agrega_vehiculo(acceso_obj, pase_dentro):
    """
    TB-064: con action='create', update_bitacora_entrada agrega un vehículo a
    la visita abierta sin tocar los que ya tenía. Es lo que usa el guardia
    cuando la persona llega en un vehículo que no estaba en el pase.
    """
    folio, entrada = pase_dentro
    antes = ultima_visita(acceso_obj, folio).get("vehiculos") or []

    acceso_obj.update_bitacora_entrada(
        {"action": "create", "vehiculo": VEHICULO_PRUEBA}, record_id=entrada["_id"]
    )

    despues = ultima_visita(acceso_obj, folio).get("vehiculos") or []
    assert len(despues) == len(antes) + 1, f"Se esperaba 1 vehículo más: antes={len(antes)}, después={len(despues)}"
    assert VEHICULO_PRUEBA["placas"] in {v.get("placas") for v in despues}, (
        f"El vehículo agregado no aparece en la visita: {despues}"
    )


@pytest.mark.integration
def test_update_bitacora_entrada_agrega_equipo(acceso_obj, pase_dentro):
    """
    TB-065: con action='create', update_bitacora_entrada agrega un equipo a la
    visita abierta sin tocar los que ya tenía. Sin record_id ni folio debe
    responder error en vez de intentar editar sin saber qué registro.
    """
    folio, entrada = pase_dentro
    antes = ultima_visita(acceso_obj, folio).get("equipos") or []

    acceso_obj.update_bitacora_entrada(
        {"action": "create", "equipo": EQUIPO_PRUEBA}, record_id=entrada["_id"]
    )

    despues = ultima_visita(acceso_obj, folio).get("equipos") or []
    assert len(despues) == len(antes) + 1, f"Se esperaba 1 equipo más: antes={len(antes)}, después={len(despues)}"
    assert EQUIPO_PRUEBA["serie"] in {e.get("numero_serie") for e in despues}, (
        f"El equipo agregado no aparece en la visita: {despues}"
    )

    with pytest.raises(Exception) as exc_info:
        acceso_obj.update_bitacora_entrada({"action": "create", "equipo": EQUIPO_PRUEBA})
    assert "Se requiere el folio o el id del registro" in str(exc_info.value)


@pytest.mark.integration
def test_update_bitacora_entrada_edita_equipo_existente(acceso_obj, pase_activo):
    """
    TB-066: con action='edit' y set_number, update_bitacora_entrada reemplaza
    esa fila de equipos sin duplicarla. Hoy ningún cliente manda 'edit' (el
    front y la app solo agregan); se prueba la capacidad del backend.
    """
    res = acceso_obj.do_access(pase_activo, LOCATION, AREA, {"equipo": [EQUIPO_PRUEBA]})
    assert res.get("status_code") in (200, 201, 202), f"No se pudo dar entrada con equipo: {res}"

    try:
        visita = ultima_visita(acceso_obj, pase_activo)
        antes = visita.get("equipos") or []
        assert len(antes) == 1, f"La entrada debía tener 1 equipo: {antes}"

        acceso_obj.update_bitacora_entrada(
            {"action": "edit", "set_number": 0, "equipo": EQUIPO_EDITADO}, record_id=visita["_id"]
        )

        despues = ultima_visita(acceso_obj, pase_activo).get("equipos") or []
        series = {e.get("numero_serie") for e in despues}
        assert len(despues) == 1, f"Editar duplicó el equipo: {despues}"
        assert EQUIPO_EDITADO["serie"] in series, f"El equipo no quedó editado: {despues}"
        assert EQUIPO_PRUEBA["serie"] not in series, "Sigue el equipo original"
    finally:
        salida_silenciosa(acceso_obj, pase_activo, LOCATION, AREA)
