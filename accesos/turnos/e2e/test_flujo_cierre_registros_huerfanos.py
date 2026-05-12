import pytest, logging, simplejson, copy

from turnos.data.turns_data import TURN_DATA_10

LOCATION = TURN_DATA_10["location"]
AREA     = TURN_DATA_10["area"]


def _patch_checkin_type(accesos_api, record_id, checkin_type):
    """Parcheado directo del checkin_type de un registro y el checkin_status
    de cada guardia en guard_group para mantener consistencia interna."""
    guard_status = "salida" if checkin_type == "cerrada" else "entrada"
    data   = accesos_api.lkf_api.get_metadata(accesos_api.CHECKIN_CASETAS)
    record = accesos_api.get_record_by_id(record_id)
    answers = record["answers"]
    answers[accesos_api.checkin_fields["checkin_type"]] = checkin_type
    for guard in answers.get(accesos_api.f["guard_group"], []):
        guard[accesos_api.checkin_fields["checkin_status"]] = guard_status
    data["answers"] = answers
    return accesos_api.lkf_api.patch_record(data=data, record_id=record_id)


@pytest.mark.e2e
def test_flujo_cierre_registros_huerfanos(accesos_api):
    """
    Valida que get_shift_data detecta y cierra automáticamente un registro
    de checkin huérfano (registro abierto más antiguo cuando el más reciente
    ya fue cerrado).

    Flujo:
        1. Abrir checkin_1 (registro que quedará huérfano).
        2. Cerrar checkin_1 temporalmente para que do_checkin no lo detecte.
        3. Abrir checkin_2 (simula la condición de carrera).
        4. Reabrir checkin_1 → ahora hay dos registros abiertos en la misma caseta.
        5. Cerrar checkin_2 normalmente → estado huérfano creado.
        6. Llamar get_shift_data → debe auto-cerrar checkin_1.
        7. Verificar que get_open_checkin no devuelve nada.
    """
    logging.info("================> Arranca TEST: test_flujo_cierre_registros_huerfanos")
    checkin_id_1 = None
    checkin_id_2 = None

    # Pre-cleanup: cerrar cualquier checkin abierto del usuario para evitar falso positivo
    user_id = accesos_api.user.get('user_id')
    stale_status = accesos_api.get_employee_checkin_status([user_id])
    stale = stale_status.get(user_id, {})
    if stale.get('status') == 'in' and stale.get('_id'):
        logging.info(f"Pre-cleanup: cerrando registro previo abierto {stale['_id']}")
        _patch_checkin_type(accesos_api, stale['_id'], "cerrada")

    try:
        # Paso 1: abrir checkin_1
        result_1 = accesos_api.do_checkin(**copy.deepcopy(TURN_DATA_10))
        assert result_1.get("status_code") in [200, 201, 202], \
            f"Error al abrir checkin_1: {result_1}"
        checkin_id_1 = result_1.get("json", {}).get("id")
        assert checkin_id_1, "No se obtuvo checkin_id_1"
        logging.info(f"Paso 1: checkin_1 abierto. id={checkin_id_1}")

        # Paso 2: cerrar checkin_1 temporalmente para que do_checkin no lo encuentre
        res = _patch_checkin_type(accesos_api, checkin_id_1, "cerrada")
        assert res.get("status_code") in [200, 201, 202], \
            f"Error al cerrar temporalmente checkin_1: {res}"
        logging.info("Paso 2: checkin_1 cerrado temporalmente")

        # Paso 3: abrir checkin_2 (la caseta parece cerrada para do_checkin)
        result_2 = accesos_api.do_checkin(**copy.deepcopy(TURN_DATA_10))
        assert result_2.get("status_code") in [200, 201, 202], \
            f"Error al abrir checkin_2: {result_2}"
        checkin_id_2 = result_2.get("json", {}).get("id")
        assert checkin_id_2, "No se obtuvo checkin_id_2"
        logging.info(f"Paso 3: checkin_2 abierto. id={checkin_id_2}")

        # Paso 4: reabrir checkin_1 → dos registros abiertos en la misma caseta
        res = _patch_checkin_type(accesos_api, checkin_id_1, "abierta")
        assert res.get("status_code") in [200, 201, 202], \
            f"Error al reabrir checkin_1: {res}"
        logging.info("Paso 4: checkin_1 reabierto — dos registros abiertos simultáneos")

        # Paso 5: cerrar checkin_2 normalmente → checkin_1 queda huérfano
        result_checkout = accesos_api.do_checkout(
            checkin_id=checkin_id_2,
            location=LOCATION,
            area=AREA,
        )
        assert result_checkout.get("status_code") in [200, 201, 202], \
            f"Error al cerrar checkin_2: {result_checkout}"
        logging.info("Paso 5: checkin_2 cerrado — estado huérfano creado")

        # Verificar estado huérfano antes de llamar get_shift_data
        orphan_before = accesos_api.get_open_checkin(LOCATION, AREA)
        assert orphan_before, "No se detectó el registro huérfano antes de get_shift_data"
        assert str(orphan_before.get("_id", "")) == checkin_id_1, \
            f"El registro huérfano no es checkin_1: {orphan_before.get('_id')}"
        logging.info(f"Estado huérfano confirmado: {orphan_before.get('_id')}")

        # Paso 6: llamar get_shift_data → debe auto-cerrar checkin_1
        shift_data = accesos_api.get_shift_data(booth_location=LOCATION, booth_area=AREA)
        assert "booth_status" in shift_data, "get_shift_data no devolvió booth_status"
        logging.info("Paso 6: get_shift_data ejecutado")

        # Paso 7: verificar que no queda ningún registro abierto
        orphan_after = accesos_api.get_open_checkin(LOCATION, AREA)
        assert not orphan_after, \
            f"Aún existe un registro huérfano abierto después de get_shift_data: {orphan_after}"
        logging.info("Paso 7: No hay registros huérfanos — auto-cierre exitoso")

    finally:
        for record_id in filter(None, [checkin_id_1, checkin_id_2]):
            try:
                record = accesos_api.get_record_by_id(record_id)
                if record.get("answers", {}).get(
                    accesos_api.checkin_fields["checkin_type"]
                ) in ["abierta", "entrada", "apertura", "disponible"]:
                    logging.info(f"Cleanup: cerrando registro {record_id}")
                    accesos_api.do_checkout(
                        checkin_id=record_id,
                        location=LOCATION,
                        area=AREA,
                        forzar=True,
                        comments="Cleanup automático por fallo de test",
                    )
            except Exception as ex:
                logging.warning(f"Cleanup falló para {record_id}: {ex}")
