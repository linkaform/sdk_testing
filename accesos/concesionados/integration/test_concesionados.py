# coding: utf-8

from .fixtures import accesos_obj, mock_crea_consecion
from lkf_modules.accesos.items.scripts.Accesos.accesos_testing import *
import logging

def test_create_concesionado(accesos_obj, mock_crea_consecion):
    """
    Crea un articulo concesionado con varios equipos. 
    
    Detalles:
        1. Se obtiene informacion del turno
        2. Se inicia el turno
        3. Se obtiene informacion del turno
        4. Se finaliza el turno
    """
    logging.info('================> Arranca TEST #1: Creando Articulo concesionado2...')
    articulo = create_article_concessioned(accesos_obj, mock_crea_consecion)
    assert articulo.get("status_code") == 201
    logging.info(f'articulo {articulo}')
    print('articulo', articulo)
    record_id = articulo.get('id')
    get_list_articulos_concesionados
    # logging.info('================> Arranca TEST #1: Happy Path')
    # checkin_id = None
    # turn_closed = False

    # turn_data = get_shift_data(accesos_turnos_api, {
    #     "location": "Planta Monterrey", 
    #     "area": "Caseta Principal"
    # })
    # assert isinstance(turn_data, dict), "Error al obtener turno: no es un diccionario"
    # logging.info('================> Paso 1: COMPLETADO')

    # try:
    #     start_turn_data = do_checkin(accesos_turnos_api, {
    #         "location": "Planta Monterrey",
    #         "area": "Caseta Principal",
    #         "employee_list": [],
    #         "fotografia": [{
    #             "file_name": "evidencia.jpeg", 
    #             "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/116852/660459dde2b2d414bce9cf8f/6962b6d8c8deee17fb7843f8.jpeg"
    #         }],
    #         "nombre_suplente": "",
    #         "checkin_id": ""
    #     })
    #     assert start_turn_data.get("status_code") in [200, 201, 202], "Error al iniciar turno: status code != [200, 201, 202]"
    #     assert start_turn_data.get("registro_de_asistencia") == "Correcto", "Error al iniciar turno: registro_de_asistencia != Correcto"
    #     assert "json" in start_turn_data, "Error al iniciar turno: json no encontrado"
    #     assert "id" in start_turn_data["json"], "Error al iniciar turno: id no encontrado"

    #     checkin_id = start_turn_data["json"]["id"]
    #     assert isinstance(checkin_id, str), "Error al iniciar turno: checkin_id no es string"
    #     assert checkin_id != "", "Error al iniciar turno: checkin_id es vacio"
    #     logging.info('================> Paso 2: COMPLETADO')

    #     turn_data = get_shift_data(accesos_turnos_api, {
    #         "location": "Planta Monterrey",
    #         "area": "Caseta Principal",
    #     })
    #     assert isinstance(turn_data, dict), "Error al obtener turno: no es un diccionario"
    #     logging.info('================> Paso 3: COMPLETADO')

    #     end_turn_data = do_checkout(accesos_turnos_api, {
    #         "location": "Planta Monterrey", 
    #         "area": "Caseta Principal",
    #         "checkin_id": checkin_id, # <--- Obligatorio
    #         "fotografia": [{
    #             "file_name": "evidencia.jpeg",
    #             "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/116852/660459dde2b2d414bce9cf8f/6962dc4237ad31d382c20714.jpeg"
    #         }],
    #         "guards": [],
    #         "forzar": False,
    #         "comments": ""
    #     })
    #     assert end_turn_data.get("status_code") in [200, 201, 202], "Error al finalizar turno: status code != [200, 201, 202]"
    #     assert end_turn_data.get("registro_de_asistencia") == "Correcto", "Error al finalizar turno: registro_de_asistencia != Correcto"
    #     turn_closed = True
    #     logging.info('================> Paso 4: COMPLETADO')
    # finally:
    #     if checkin_id and not turn_closed:
    #         logging.info("Cleanup: cerrando turno por seguridad")
    #         do_checkout(accesos_turnos_api, {
    #             "location": "Planta Monterrey",
    #             "area": "Caseta Principal",
    #             "checkin_id": checkin_id,
    #             "guards": [],
    #             "forzar": True,
    #             "comments": "Cleanup automático por fallo de test"
    #         })

