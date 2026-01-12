from lkf_modules.accesos.items.scripts.Accesos.turnos import get_turn_data, start_turn, end_turn
from .fixtures import accesos_turnos_api, accesos_turnos_api_15864
import logging

def test_turn_happy_path(accesos_turnos_api):
    """
    Test para iniciar y finalizar un turno correctamente. 
    
    Detalles:
        1. Se obtiene informacion del turno
        2. Se inicia el turno
        3. Se obtiene informacion del turno
        4. Se finaliza el turno
    """
    logging.info('================> Arranca TEST #1: Happy Path')
    checkin_id = None
    turn_closed = False

    turn_data = get_turn_data(accesos_turnos_api, {
        "location": "Planta Monterrey", 
        "area": "Caseta Principal"
    })
    assert isinstance(turn_data, dict), "Error al obtener turno: no es un diccionario"
    logging.info('================> Paso 1: COMPLETADO')

    try:
        start_turn_data = start_turn(accesos_turnos_api, {
            "location": "Planta Monterrey",
            "area": "Caseta Principal",
            "employee_list": [],
            "fotografia": [{
                "file_name": "evidencia.jpeg", 
                "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/116852/660459dde2b2d414bce9cf8f/6962b6d8c8deee17fb7843f8.jpeg"
            }],
            "nombre_suplente": "",
            "checkin_id": ""
        })
        assert start_turn_data.get("status_code") in [200, 201, 202], "Error al iniciar turno: status code != [200, 201, 202]"
        assert start_turn_data.get("registro_de_asistencia") == "Correcto", "Error al iniciar turno: registro_de_asistencia != Correcto"
        assert "json" in start_turn_data, "Error al iniciar turno: json no encontrado"
        assert "id" in start_turn_data["json"], "Error al iniciar turno: id no encontrado"

        checkin_id = start_turn_data["json"]["id"]
        assert isinstance(checkin_id, str), "Error al iniciar turno: checkin_id no es string"
        assert checkin_id != "", "Error al iniciar turno: checkin_id es vacio"
        logging.info('================> Paso 2: COMPLETADO')

        turn_data = get_turn_data(accesos_turnos_api, {
            "location": "Planta Monterrey",
            "area": "Caseta Principal",
        })
        assert isinstance(turn_data, dict), "Error al obtener turno: no es un diccionario"
        logging.info('================> Paso 3: COMPLETADO')

        end_turn_data = end_turn(accesos_turnos_api, {
            "location": "Planta Monterrey", 
            "area": "Caseta Principal",
            "checkin_id": checkin_id, # <--- Obligatorio
            "fotografia": [{
                "file_name": "evidencia.jpeg",
                "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/116852/660459dde2b2d414bce9cf8f/6962dc4237ad31d382c20714.jpeg"
            }],
            "guards": [],
            "forzar": False,
            "comments": ""
        })
        assert end_turn_data.get("status_code") in [200, 201, 202], "Error al finalizar turno: status code != [200, 201, 202]"
        assert end_turn_data.get("registro_de_asistencia") == "Correcto", "Error al finalizar turno: registro_de_asistencia != Correcto"
        turn_closed = True
        logging.info('================> Paso 4: COMPLETADO')
    finally:
        if checkin_id and not turn_closed:
            logging.info("Cleanup: cerrando turno por seguridad")
            end_turn(accesos_turnos_api, {
                "location": "Planta Monterrey",
                "area": "Caseta Principal",
                "checkin_id": checkin_id,
                "guards": [],
                "forzar": True,
                "comments": "Cleanup automático por fallo de test"
            })

def test_multiple_guards_same_booth_sequential_checkout(accesos_turnos_api, accesos_turnos_api_15864):
    """
    Test de apertura y cierre de caseta con varios guardias. 
    
    Detalles:
        1. Inicia turno guardia con user_id = 10 en Planta Monterrey - Caseta Principal
        2. Inicia turno guardia con user_id = 15864 en la misma caseta
        3. Cierra el turno del guardia con user_id = 10
        4. Cierra el turno del guardia con user_id = 15864
    """
    logging.info('================> Arranca TEST #2: Multiple Guards Same Booth Sequential Checkout')
    checkin_id_1 = None
    checkin_id_2 = None
    turn_closed_1 = False
    turn_closed_2 = False

    try:
        start_turn_data_10 = start_turn(accesos_turnos_api, {
            "location": "Planta Monterrey",
            "area": "Caseta Principal",
            "employee_list": [],
            "fotografia": [{
                "file_name": "evidencia.jpeg", 
                "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/116852/660459dde2b2d414bce9cf8f/6962b6d8c8deee17fb7843f8.jpeg"
            }],
            "nombre_suplente": "",
            "checkin_id": ""
        })
        assert start_turn_data_10.get("status_code") in [200, 201, 202], "Error al iniciar turno - usuario 10: status code != [200, 201, 202]"
        assert start_turn_data_10.get("registro_de_asistencia") == "Correcto", "Error al iniciar turno - usuario 10: registro_de_asistencia != Correcto"
        assert "json" in start_turn_data_10, "Error al iniciar turno - usuario 10: json no encontrado"
        assert "id" in start_turn_data_10["json"], "Error al iniciar turno - usuario 10: id no encontrado"

        checkin_id_1 = start_turn_data_10["json"]["id"]
        assert isinstance(checkin_id_1, str), "Error al iniciar turno - usuario 10: checkin_id no es string"
        assert checkin_id_1 != "", "Error al iniciar turno - usuario 10: checkin_id es vacio"
        logging.info('================> Paso 1: COMPLETADO')

        start_turn_data_15864 = start_turn(accesos_turnos_api_15864, {
            "location": "Planta Monterrey",
            "area": "Caseta Principal",
            "employee_list": [],
            "fotografia": [{
                "file_name": "evidencia.jpeg", 
                "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/116852/660459dde2b2d414bce9cf8f/6962b6d8c8deee17fb7843f8.jpeg"
            }],
            "nombre_suplente": "",
            "checkin_id": checkin_id_1 # <--- Obligatorio para iniciar turno en una caseta abierta
        })
        assert start_turn_data_15864.get("status_code") in [200, 201, 202], "Error al iniciar turno - usuario 15864: status code != [200, 201, 202]"
        # TODO: Agregar registro de asistencias para guardias que inician turno en una caseta abierta
        # assert start_turn_data_15864.get("registro_de_asistencia") == "Correcto", "Error al iniciar turno - usuario 15864: registro_de_asistencia != Correcto"
        logging.info('================> Paso 2: COMPLETADO')

        end_turn_data_10 = end_turn(accesos_turnos_api, {
            "location": "Planta Monterrey", 
            "area": "Caseta Principal",
            "checkin_id": checkin_id_1, # <--- Obligatorio para cerrar turno abierto
            "fotografia": [{
                "file_name": "evidencia.jpeg",
                "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/116852/660459dde2b2d414bce9cf8f/6962dc4237ad31d382c20714.jpeg"
            }],
            "guards": [],
            "forzar": False,
            "comments": ""
        })
        assert end_turn_data_10.get("status_code") in [200, 201, 202], "Error al finalizar turno - usuario 10: status code != [200, 201, 202]"
        assert end_turn_data_10.get("registro_de_asistencia") == "Correcto", "Error al finalizar turno - usuario 10: registro_de_asistencia != Correcto"
        turn_closed_1 = True
        logging.info('================> Paso 3: COMPLETADO')

        end_turn_data_15864 = end_turn(accesos_turnos_api_15864, {
            "location": "Planta Monterrey", 
            "area": "Caseta Principal",
            "checkin_id": checkin_id_1, # <--- Obligatorio para cerrar turno abierto
            "fotografia": [{
                "file_name": "evidencia.jpeg",
                "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/116852/660459dde2b2d414bce9cf8f/6962dc4237ad31d382c20714.jpeg"
            }],
            "guards": [],
            "forzar": False,
            "comments": ""
        })
        assert end_turn_data_15864.get("status_code") in [200, 201, 202], "Error al finalizar turno - usuario 15864: status code != [200, 201, 202]"
        # TODO: Agregar registro de asistencias para guardias que cierran turno abierto
        # assert end_turn_data_15864.get("registro_de_asistencia") == "Correcto", "Error al finalizar turno - usuario 15864: registro_de_asistencia != Correcto"
        turn_closed_2 = True
        logging.info('================> Paso 4: COMPLETADO')
    finally:
        if checkin_id_1 and not turn_closed_1:
            logging.info("Cleanup: cerrando turno por seguridad")
            end_turn(accesos_turnos_api, {
                "location": "Planta Monterrey",
                "area": "Caseta Principal",
                "checkin_id": checkin_id_1,
                "guards": [],
                "forzar": True,
                "comments": "Cleanup automático por fallo de test"
            })
        if checkin_id_1 and not turn_closed_2:
            logging.info("Cleanup: cerrando turno por seguridad")
            end_turn(accesos_turnos_api_15864, {
                "location": "Planta Monterrey",
                "area": "Caseta Principal",
                "checkin_id": checkin_id_1,
                "guards": [],
                "forzar": True,
                "comments": "Cleanup automático por fallo de test"
            })