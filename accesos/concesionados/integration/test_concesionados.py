# coding: utf-8

from .fixtures import *
from lkf_modules.accesos.items.scripts.Accesos.accesos_testing import *
import logging




def test_get_articulos_list(acceso_obj, mock_lista_concesionados, mock_crea_consecion_otro, mock_crea_consecion):
    """
    Provamos que la lista nos regres un numero de articulos concesionados, luego agreagmos 2 y vemos q la lista regrese 2 mas
    """
    def create_concesionado(acceso_obj, mock_crea_consecion, mock_crea_consecion_otro ):
        """
        Crea un articulo concesionado con varios equipos. 
        
        Detalles:
            1. Se obtiene informacion del turno
            2. Se inicia el turno
            3. Se obtiene informacion del turno
            4. Se finaliza el turno
        """
        logging.info('================> Arranca TEST #1: Creando Articulo concesionado2...')
        articulo = create_article_concessioned(acceso_obj, mock_crea_consecion)
        assert articulo.get("status_code") == 201
        articulo_otro = create_article_concessioned(acceso_obj, mock_crea_consecion_otro)
        assert articulo_otro.get("status_code") == 201
        logging.info(f'articulo {articulo}')
        record_id = articulo.get('id')
        return articulo, articulo_otro
    
    
    def partial_return(articulo, data_concesion):
        equipos = data_concesion['equipos']
        data = {
            'record_id' : articulo['id'],
            'status' : 'partial',
            'quien_entrega' :  data_concesion['persona_nombre_otro'],
            'identificacion_entrega' : data_concesion['persona_identificacion_otro'],
            'comentarios' : "Devolucion de Parical: partial_return",
            'entregado_por': "otro",
            'equipos' : []
            }
        for equipo in equipos:
            row = {}
            row['id_movimiento'] = equipo['id_movimiento']
            row['cantidad_devuelta'] = round(equipo['cantidad_equipo_concesion']/3)
            row['state'] = "complete"
            row['evidencia'] = [{
                'file_name':'equipo_total.png',
                'file_url':'https://f001.backblazeb2.com/file/app-linkaform/public-client-126/68600/6076166dfd84fa7ea446b917/2026-02-25T11:44:39_5.png'}]
            data['equipos'].append(row)
        response = acceso_obj.update_article_concessioned(data, articulo['id'])
        return True

    def complete_return_empleado(articulo, data_concesion):
        data = {
            'record_id' : articulo['id'],
            'status' : 'total',
            'state' : 'complete',
            'quien_entrega' :  data_concesion['persona_nombre_concesion'],
            'identificacion_entrega' : data_concesion['persona_identificacion_otro'],
            'comentarios' : "Devolucion de Pruebas: complete_return_empleado",
            'evidencia' : [{
                'file_name':'equipo_total.png',
                'file_url':'https://f001.backblazeb2.com/file/app-linkaform/public-client-126/68600/6076166dfd84fa7ea446b917/2026-02-25T11:44:39_5.png'}]
            }
        response = acceso_obj.update_article_concessioned(data, articulo['id'])
        return response

    def one_article_return():
        return True

    location = mock_lista_concesionados['location']
    area = ""
    consecion_otro = copy.deepcopy(mock_crea_consecion_otro)
    consecion_otro2 = copy.deepcopy(mock_crea_consecion_otro)
    consecion_otro3 = copy.deepcopy(mock_crea_consecion_otro)
    status = mock_lista_concesionados.get("dateFrom", "")
    dateFrom = mock_lista_concesionados.get("dateFrom", "")
    dateTo = mock_lista_concesionados.get("dateTo", "")
    filterDate = mock_lista_concesionados.get("filterDate", "")
    response = acceso_obj.get_list_articulos_concesionados(location, area, status, dateFrom=dateFrom, dateTo=dateTo, filterDate=filterDate)
    cantidad_inicial = len(response)
    assert isinstance(response, list)
    articulo, articulo_otro = create_concesionado(acceso_obj, mock_crea_consecion, mock_crea_consecion_otro )
    response_despues = acceso_obj.get_list_articulos_concesionados(location, area, status, dateFrom=dateFrom, dateTo=dateTo, filterDate=filterDate)
    assert len(response_despues) == cantidad_inicial + 2
    assert response_despues[0]['folio'] == articulo_otro['json']['folio']
    assert response_despues[1]['folio'] == articulo['json']['folio']
    devolucion = complete_return_empleado(articulo['json'], mock_crea_consecion)
    if isinstance(devolucion, list):
        assert devolucion[0]['status_code'] == 202
    devolucion = partial_return(articulo_otro['json'], consecion_otro)
    devolucion = partial_return(articulo_otro['json'], consecion_otro2)
    devolucion = partial_return(articulo_otro['json'], consecion_otro3)
    articulos = acceso_obj.get_list_articulos_concesionados(location)


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

