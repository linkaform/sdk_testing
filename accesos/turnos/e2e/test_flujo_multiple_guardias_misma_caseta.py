import pytest, logging

from turnos.data.turns_data import TURN_DATA_10, TURN_DATA_15864

@pytest.mark.e2e
def test_multiple_guards_same_booth_sequential_checkout(accesos_turnos_api, accesos_turnos_api_15864):
    """
    Test de apertura y cierre de caseta con varios guardias. 
    
    Detalles:
        1. Inicia turno guardia con user_id = 10 en Planta Monterrey - Caseta Principal
        2. Inicia turno guardia con user_id = 15864 en la misma caseta
        3. Cierra el turno del guardia con user_id = 10
        4. Cierra el turno del guardia con user_id = 15864
    """
    logging.info('================> Arranca TEST: Multiple Guards Same Booth Sequential Checkout')
    checkin_id = None
    turn_closed_1 = False
    turn_closed_2 = False

    try:
        start_turn_data_10 = accesos_turnos_api.do_checkin(accesos_turnos_api, TURN_DATA_10)
        assert start_turn_data_10.get("status_code") in [200, 201, 202], "Error al iniciar turno - usuario 10: status code != [200, 201, 202]"
        assert start_turn_data_10.get("registro_de_asistencia") == "Correcto", "Error al iniciar turno - usuario 10: registro_de_asistencia != Correcto"
        assert "json" in start_turn_data_10, "Error al iniciar turno - usuario 10: json no encontrado"
        assert "id" in start_turn_data_10["json"], "Error al iniciar turno - usuario 10: id no encontrado"

        checkin_id = start_turn_data_10["json"]["id"]
        assert isinstance(checkin_id, str), "Error al iniciar turno - usuario 10: checkin_id no es string"
        assert checkin_id != "", "Error al iniciar turno - usuario 10: checkin_id es vacio"
        logging.info('================> Paso 1: COMPLETADO')

        TURN_DATA_15864['checkin_id'] = checkin_id # <--- Obligatorio para iniciar turno en una caseta abierta
        start_turn_data_15864 = accesos_turnos_api_15864.do_checkin(accesos_turnos_api_15864, TURN_DATA_15864)
        assert start_turn_data_15864.get("status_code") in [200, 201, 202], "Error al iniciar turno - usuario 15864: status code != [200, 201, 202]"
        assert start_turn_data_15864.get("registro_de_asistencia") == "Correcto", "Error al iniciar turno - usuario 15864: registro_de_asistencia != Correcto"
        logging.info('================> Paso 2: COMPLETADO')

        TURN_DATA_10['checkin_id'] = checkin_id # <--- Obligatorio para cerrar turno abierto
        end_turn_data_10 = accesos_turnos_api.do_checkout(accesos_turnos_api, TURN_DATA_10)
        assert end_turn_data_10.get("status_code") in [200, 201, 202], "Error al finalizar turno - usuario 10: status code != [200, 201, 202]"
        assert end_turn_data_10.get("registro_de_asistencia") == "Correcto", "Error al finalizar turno - usuario 10: registro_de_asistencia != Correcto"
        turn_closed_1 = True
        logging.info('================> Paso 3: COMPLETADO')

        TURN_DATA_15864['checkin_id'] = checkin_id # <--- Obligatorio para cerrar turno abierto
        end_turn_data_15864 = accesos_turnos_api_15864.do_checkout(accesos_turnos_api_15864, TURN_DATA_15864)
        assert end_turn_data_15864.get("status_code") in [200, 201, 202], "Error al finalizar turno - usuario 15864: status code != [200, 201, 202]"
        # TODO: Agregar registro de asistencias para guardias que cierran turno abierto
        # assert end_turn_data_15864.get("registro_de_asistencia") == "Correcto", "Error al finalizar turno - usuario 15864: registro_de_asistencia != Correcto"
        turn_closed_2 = True
        logging.info('================> Paso 4: COMPLETADO')
    finally:
        if checkin_id and not turn_closed_1:
            logging.info("Cleanup: cerrando turno por seguridad")
            TURN_DATA_10['checkin_id'] = checkin_id
            TURN_DATA_10['guards'] = []
            TURN_DATA_10['forzar'] = True
            TURN_DATA_10['comments'] = "Cleanup automático por fallo de test"
            accesos_turnos_api.do_checkout(accesos_turnos_api, TURN_DATA_10)
        if checkin_id and not turn_closed_2:
            logging.info("Cleanup: cerrando turno por seguridad")
            TURN_DATA_15864['checkin_id'] = checkin_id
            TURN_DATA_15864['guards'] = []
            TURN_DATA_15864['forzar'] = True
            TURN_DATA_15864['comments'] = "Cleanup automático por fallo de test"
            accesos_turnos_api_15864.do_checkout(accesos_turnos_api_15864, TURN_DATA_15864)