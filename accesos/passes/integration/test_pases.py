# coding: utf-8

import logging, simplejson
from urllib.parse import urlparse

from .fixtures import *
from lkf_modules.accesos.items.scripts.Accesos.accesos_testing import *


def test_setup_account(acceso_obj):
    response_location = acceso_obj.catalogos_pase_location()
    ubicaciones_user = response_location['ubicaciones_user']
    res = {}
    for location in ubicaciones_user:
        areas = acceso_obj.catalogos_pase_area(location)
        res[location] = areas['areas_by_location']
    assert len(res) > 1
    
def get_assets(acceso_obj, mock_location_areas):
    logging.info('=== GETTING LOCATIONS ===')
    response_location = acceso_obj.catalogos_pase_location()
    location_uno = response_location['ubicaciones_default'][0]
    len_locations = len(response_location['ubicaciones_default'])
    if len_locations > 1:
        location_dos = response_location['ubicaciones_default'][1]
    logging.info('=== GETTING LOCATIONS AREAS ===')
    response_area_uno = acceso_obj.catalogos_pase_area(location_uno)
    if len_locations > 1:
        response_area_dos = acceso_obj.catalogos_pase_area(location_dos)
    assert mock_location_areas[location_uno] == response_area_uno['areas_by_location']
    if len_locations > 1:
        assert mock_location_areas[location_dos] == response_area_dos['areas_by_location']
    assets_access_pass = acceso_obj.assets_access_pass(location_uno)
    print('assets = ', simplejson.dumps(assets_access_pass, indent=3))
    assert 'Visita General' in assets_access_pass['Perfiles']
    assert 'Candidatos' in assets_access_pass['Perfiles']
    assert 'correo' in assets_access_pass['envios']
    assert 'identificacion' in assets_access_pass['requerimientos']
    return response_area_uno


def test_create_pase(acceso_obj, mock_pase, mock_location_areas):
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
    location = get_assets(acceso_obj, mock_location_areas)
    acceso_obj.use_api = False
    res = acceso_obj.create_access_pass(mock_pase)
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

def completar_pase(acceso_obj, res, mock_completar_pase_usaurio_actual):
    access_pass = mock_completar_pase_usaurio_actual.get('access_pass')
    folio = res['json'].get('id')
    mock_completar_pase_usaurio_actual['folio'] = folio
    response = acceso_obj.update_pass(access_pass, folio)
    assert response['status_code'] == 202

def test_create_pase_fecha_fija(acceso_obj, mock_pase_fecha_fija):
    """
    Crea un articulo concesionado con varios equipos. 
    
    Detalles:
        1. Se obtiene informacion del turno
        2. Se inicia el turno
        3. Se obtiene informacion del turno
        4. Se finaliza el turno
    """
    logging.info('Test: test_create_pase_fecha_fija')
    acceso_obj.use_api = False
    access_pass = mock_pase_fecha_fija['access_pass']
    res = acceso_obj.create_access_pass(access_pass)
    assert res['status_code'] == 201
    qr_code = res.get('json',{}).get('id')
    assert len(qr_code) == 24
    data = acceso_obj.catalagos_pase_no_jwt(qr_code)
    check_catalog_pase_response(data)

def test_create_pase_nueva_visita(acceso_obj, mock_pase_nueva_vista):
    """
    Crea un articulo concesionado con varios equipos. 
    
    Detalles:
        1. Se obtiene informacion del turno
        2. Se inicia el turno
        3. Se obtiene informacion del turno
        4. Se finaliza el turno
    """
    logging.info('================> Arranca TEST AUTOREGISRO SIN VISTA A#3: ...')
    res = acceso_obj.create_access_pass(mock_pase_nueva_vista)
    print('res=',res)
    assert res['status_code'] == 201

def test_create_pase_app(acceso_obj, mock_pase_app, mock_pase_app_update):
    """
    Creacion de pase con datos desde app
    """
    def verify_completar_pase(res):
        res = completar_pase(acceso_obj, res, mock_pase_app_update )
    logging.info('================> Arranca Crea pase desde app #4: ....')
    res = acceso_obj.create_access_pass(mock_pase_app)
    assert res['status_code'] == 201
    verify_completar_pase(res)

  
def test_create_pase_auto_registro(acceso_obj, mock_pase_auto_registro):
    """
    Crea un articulo concesionado con varios equipos. 
    
    Detalles:
        1. Se obtiene informacion del turno
        2. Se inicia el turno
        3. Se obtiene informacion del turno
        4. Se finaliza el turno
    """
    logging.info('================> Arranca TEST AUTOREGISRO #2: ...')
    res = acceso_obj.create_access_pass(mock_pase_auto_registro)
    assert res['status_code'] == 201
  
def test_create_pase_auto_registro_sin_vista(acceso_obj, \
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
        record = acceso_obj.get_record_by_id(record_id, select_columns=['answers'])
        answers = record['answers']
        motivo = answers[acceso_obj.pase_entrada_fields['tema_cita']]
        assert mock_pase_auto_registro_sin_vista_a['motivo'] == motivo

    def verify_answers_visita():
        visita_a = mock_completar_pase_usaurio_actual['access_pass']['visita_a'][0]
        record = acceso_obj.get_record_by_id(record_id, select_columns=['answers'])
        answers = record['answers']
        visita_a_pase = answers[acceso_obj.pase_entrada_fields['visita_a']]
        if visita_a == 'Usuario Actual':
            assert len(visita_a_pase) > 0
        else:
            vista_catalog = visita_a_pase[0]
            vista = vista_catalog[acceso_obj.CONF_AREA_EMPLEADOS_CAT_OBJ_ID ]
            assert visita_a == vista[acceso_obj.mf['nombre_empleado']]

    logging.info('> Arranca TEST AUTOREGISRO SIN VISTA A : ...')
    res = acceso_obj.create_access_pass(mock_pase_auto_registro_sin_vista_a)
    assert res['status_code'] == 201
    record_id = res['json']['id']
    verify_answers_pase()
    if res['status_code'] == 201:
        completar_pase(acceso_obj, res, mock_completar_pase_usaurio_actual)
        verify_answers_visita()


