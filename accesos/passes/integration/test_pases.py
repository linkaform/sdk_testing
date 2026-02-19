# coding: utf-8

import logging, simplejson

from urllib.parse import urlparse


from .fixtures import *
from lkf_modules.accesos.items.scripts.Accesos.accesos_testing import *


def test_setup_account(accesos_obj):
    response_location = accesos_obj.catalogos_pase_location()
    ubicaciones_user = response_location['ubicaciones_user']
    res = {}
    for location in ubicaciones_user:
        areas = accesos_obj.catalogos_pase_area(location)
        res[location] = areas['areas_by_location']
    print('LOCATION_AREAS = ', res)
    return True

def get_assets(accesos_obj, mock_location_areas):
    logging.info('=== GETTING LOCATIONS ===')
    response_location = accesos_obj.catalogos_pase_location()
    breakpoint()
    location_uno = response_location['ubicaciones_default'][0]
    len_locations = len(response_location['ubicaciones_default'])
    if len_locations > 1:
        location_dos = response_location['ubicaciones_default'][1]
    logging.info('=== GETTING LOCATIONS AREAS ===')
    response_area_uno = accesos_obj.catalogos_pase_area(location_uno)
    if len_locations > 1:
        response_area_dos = accesos_obj.catalogos_pase_area(location_dos)
    assert mock_location_areas[location_uno] == response_area_uno['areas_by_location']
    if len_locations > 1:
        assert mock_location_areas[location_dos] == response_area_dos['areas_by_location']
    assets_access_pass = accesos_obj.assets_access_pass(location_uno)
    assert 'Visita General' in assets_access_pass['Perfiles']
    assert 'Candidatos' in assets_access_pass['Perfiles']
    return response_area_uno


def test_create_pase(accesos_obj, mock_pase, mock_location_areas):
    """
    Crea un articulo concesionado con varios equipos. 
    
    Detalles:
        1. Se obtiene informacion del turno
        2. Se inicia el turno
        3. Se obtiene informacion del turno
        4. Se finaliza el turno
    """
    logging.info('================> Arranca TEST #1: ...')
    logging.info('================> Load assets:')
    location = get_assets(accesos_obj, mock_location_areas)
    accesos_obj.use_api = False
    res = accesos_obj.create_access_pass(mock_pase)
    print('res=',res)
    assert res['status_code'] == 201
    logging.info('================> Arranca TEST #1: Creando Articulo concesionado2...')
    #TODO
    #1. Obtener pase y revisar que el status este ok
    #2. Obtener status de pase

def check_catalog_pase_response(data):
    pase = data['pass_selected'] 
    assert isinstance(pase['ubicacion'], list)
    assert isinstance(pase['nombre'], str)
    assert isinstance(pase['empresa'], str)
    assert isinstance(pase['email'], str)
    assert isinstance(pase['qr_pase'][0], dict)
    parsed = urlparse(pase['qr_pase'][0]['file_url'])
    assert parsed.scheme in ("http", "https")
    assert parsed.netloc
    assert isinstance(pase['visita_a'], list)
    # breakpoint()
    # assert isinstance(pase['visita_a'][0]['nombre'], str)

def completar_pase(accesos_obj, res, mock_completar_pase_usaurio_actual):
    access_pass = mock_completar_pase_usaurio_actual.get('access_pass')
    folio = res['json'].get('id')
    mock_completar_pase_usaurio_actual['folio'] = folio
    response = accesos_obj.update_pass(access_pass, folio)
    assert response['status_code'] == 202

def test_create_pase_fecha_fija(accesos_obj, mock_pase_fecha_fija):
    """
    Crea un articulo concesionado con varios equipos. 
    
    Detalles:
        1. Se obtiene informacion del turno
        2. Se inicia el turno
        3. Se obtiene informacion del turno
        4. Se finaliza el turno
    """
    logging.info('Test: test_create_pase_fecha_fija')
    accesos_obj.use_api = False
    access_pass = mock_pase_fecha_fija['access_pass']
    res = accesos_obj.create_access_pass(access_pass)
    print('res=',res)
    assert res['status_code'] == 201
    qr_code = res.get('json',{}).get('id')
    assert len(qr_code) == 24
    data = accesos_obj.catalagos_pase_no_jwt(qr_code)
    print('response', data)
    check_catalog_pase_response(data)

def test_create_pase_nueva_visita(accesos_obj, mock_pase_nueva_vista):
    """
    Crea un articulo concesionado con varios equipos. 
    
    Detalles:
        1. Se obtiene informacion del turno
        2. Se inicia el turno
        3. Se obtiene informacion del turno
        4. Se finaliza el turno
    """
    logging.info('================> Arranca TEST AUTOREGISRO SIN VISTA A#3: ...')
    res = accesos_obj.create_access_pass(mock_pase_nueva_vista)
    print('res=',res)
    assert res['status_code'] == 201
  
def test_create_pase_auto_registro(accesos_obj, mock_pase_auto_registro):
    """
    Crea un articulo concesionado con varios equipos. 
    
    Detalles:
        1. Se obtiene informacion del turno
        2. Se inicia el turno
        3. Se obtiene informacion del turno
        4. Se finaliza el turno
    """
    logging.info('================> Arranca TEST AUTOREGISRO #2: ...')
    res = accesos_obj.create_access_pass(mock_pase_auto_registro)
    print('res=',res)
    assert res['status_code'] == 201
  
def test_create_pase_auto_registro_sin_vista(accesos_obj, \
    mock_pase_auto_registro_sin_vista_a, mock_completar_pase_usaurio_actual):
    """
    Crea un articulo concesionado con varios equipos. 
    
    Detalles:
        1. Se obtiene informacion del turno
        2. Se inicia el turno
        3. Se obtiene informacion del turno
        4. Se finaliza el turno
    """

    def verify_answers_pase():
        record = accesos_obj.get_record_by_id(record_id, select_columns=['answers'])
        answers = record['answers']
        motivo = answers[accesos_obj.pase_entrada_fields['tema_cita']]
        assert mock_pase_auto_registro_sin_vista_a['motivo'] == motivo

    def verify_answers_visita():
        visita_a = mock_completar_pase_usaurio_actual['access_pass']['visita_a'][0]
        record = accesos_obj.get_record_by_id(record_id, select_columns=['answers'])
        answers = record['answers']
        visita_a_pase = answers[accesos_obj.pase_entrada_fields['visita_a']]
        if visita_a == 'Usuario Actual':
            assert len(visita_a_pase) > 0
        else:
            vista_catalog = visita_a_pase[0]
            vista = vista_catalog[accesos_obj.CONF_AREA_EMPLEADOS_CAT_OBJ_ID ]
            assert visita_a == vista[accesos_obj.mf['nombre_empleado']]

    logging.info('> Arranca TEST AUTOREGISRO SIN VISTA A : ...')
    res = accesos_obj.create_access_pass(mock_pase_auto_registro_sin_vista_a)
    assert res['status_code'] == 201
    record_id = res['json']['id']
    verify_answers_pase()
    if res['status_code'] == 201:
        completar_pase(accesos_obj, res, mock_completar_pase_usaurio_actual)
        verify_answers_visita()


