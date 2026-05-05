# coding: utf-8
# test_rondines.py

import logging, simplejson
import sys, os,time
from bson import ObjectId

from urllib.parse import urlparse

from .fixtures import *
from lkf_modules.accesos.items.scripts.Accesos.accesos_testing import *


# print('startoing...')
# def test_account_locations(acceso_obj):
#     response_location = acceso_obj.catalogos_pase_location()
#     ubicaciones_user = response_location['ubicaciones_user']
#     res = {}
#     for location in ubicaciones_user:
#         areas = acceso_obj.catalogos_pase_area(location)
#         res[location] = areas['areas_by_location']
#     print('rse=',res)
#     return res


@pytest.fixture
def mock_rondin():
    data = copy.deepcopy(RONDIN_EJEMPLO)
    return data


# def get_rondin_areas(rondin):



# def test_creat_rondin(acceso_obj, mock_rondin):
#     print('mock_rondin', mock_rondin)
#     print('mock_rondin id', mock_rondin['_id'])
#     rondin_id = mock_rondin['_id']
#     acceso_obj.cr_db.save(mock_rondin)

def get_couch_doc(cr_db, doc_id, retries=5, delay=4.0):
    """
    Reintenta obtener un doc de CouchDB hasta `retries` veces
    esperando `delay` segundos entre intentos.
    """
    logging.warning(f'  CouchDB get una breve pausa entes del 1er intento...')
    time.sleep(delay)
    for attempt in range(1, retries + 1):
        doc = cr_db.get(doc_id)
        if doc is not None:
            logging.info(f'  CouchDB get OK en intento {attempt} — id={doc_id}')
            return doc
        logging.warning(f'  CouchDB get intento {attempt}/{retries} — doc aún no disponible, esperando {delay}s')
        time.sleep(delay)
    return None

def execute(acceso_obj, params):
    message = "Hello script name: {}".format(acceso_obj.name)
    metadata = acceso_obj.lkf_api.get_metadata(form_id = params.get('form_id'))
    metadata.update({"answers":params.get('answers')})
    print('metadata=', metadata)
    response = acceso_obj.lkf_api.post_forms_answers(metadata)
    print('response', response)
    return response

def crear_rondin(acceso_obj):
    """
    Helper (no es test): guarda un rondín en CouchDB y verifica que quedó.
    """
    logging.info('=== HELPER: crear_rondin ===')
    params =  mock_airflow_params(acceso_obj.BITACORA_RONDINES)
    res = execute(acceso_obj, params)
    rondin_id = res['json']['id']
    print('rondin_id= ', rondin_id)
    saved = get_couch_doc(acceso_obj.cr_db, rondin_id)
    assert saved is not None, f'Rondín {rondin_id} no apareció en CouchDB después de 5 intentos'
    logging.info(f'Guardando rondín id={rondin_id}')
    print('saved = ', saved)
    assert saved is not None
    assert saved['status'] == 'synced'
    assert saved['status_user'] == 'new'
    assert saved['_id'] == rondin_id
    assert saved['type'] == 'rondin'
 
    logging.info(f'Rondín guardado OK — {len(saved["record"]["check_areas"])} áreas pendientes')
    return saved
 
 
def _crear_check_areas(acceso_obj, mock_rondin, mock_check_basic):
    """
    Helper (no es test): itera check_areas del rondín, crea un doc por área
    en CouchDB y actualiza area['check_area_id'] + area['checked_at'] en el mock.
    Retorna la lista de check_ids creados.
    """
    rondin_id   = mock_rondin['_id']
    check_areas = mock_rondin['record']['check_areas']
    check_ids   = []
 
    for idx, area in enumerate(check_areas):
        check_doc = copy.deepcopy(mock_check_basic)
        check_doc['_id']                   = str(ObjectId())
        check_doc['rondin_id']             = rondin_id
        check_doc['record']['tag_id']      = area['tag_id']
        check_doc['record']['area']        = area['area']
        check_doc['record']['ubicacion']   = area['ubicacion']
        check_doc['record']['checked']     = True
        check_doc['record']['status_user'] = 'completed'
        check_doc['record']['checked_at']  = acceso_obj.date_operation(
            date_value=today,
            operator='add',
            qty=5 * idx,
            unit='minutes',
            date_format='%Y-%m-%d %H:%M:%S',
        )
 
        acceso_obj.cr_db.save(check_doc)
 
        # Reflejar el check en el mock del rondín
        area['check_area_id'] = check_doc['_id']
        area['checked_at']    = check_doc['record']['checked_at']
 
        check_ids.append(check_doc['_id'])
        logging.info(f"  check guardado [{area['area']}] id={check_doc['_id']}")
 
    # Guardar el rondín actualizado con los check_area_id
    mock_rondin['status_user'] = 'completed'
    acceso_obj.cr_db.save(mock_rondin)
 
    return check_ids
 
 
# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
 
def do_crear_check_areas(acceso_obj, mock_check_basic):
    """
    Por cada área en record.check_areas del rondín:
      - Crea un doc check_area con su tag_id, area y rondin_id
      - Lo guarda en CouchDB marcado como completado
      - Verifica estructura y valores del doc guardado
    """
    logging.info('=== TEST: test_crear_check_areas ===')
 
    mock_rondin = crear_rondin(acceso_obj)
    rondin_id   = mock_rondin['_id']
    check_areas = mock_rondin['record']['check_areas']
    logging.info(f'Áreas a chequear: {len(check_areas)}')
 
    check_ids = _crear_check_areas(acceso_obj, mock_rondin, mock_check_basic)
 
    # Verificar cada check en CouchDB
    for check_id, area in zip(check_ids, check_areas):
        saved_check = acceso_obj.cr_db.get(check_id)
 
        assert saved_check is not None
        assert saved_check['rondin_id']          == rondin_id
        assert saved_check['record']['tag_id']   == area['tag_id']
        assert saved_check['record']['area']     == area['area']
        assert saved_check['record']['checked']  is True
        assert saved_check['type']               == 'check_area'
 
    logging.info(f'Total checks guardados: {len(check_ids)}')
    assert len(check_ids) == len(check_areas)
    
    return mock_rondin, check_ids
 

def test_sync_rondin_to_lkf(acceso_obj,  mock_check_basic):
    """
    Con el rondín y sus check_areas ya en CouchDB,
    llama sync_records([]) para que el script procese los docs
    pendientes y cree el rondín + áreas en MongoDB (LinkaForm).
    """
    logging.info('=== TEST: test_sync_rondin_to_lkf ===')
    acceso_obj.clean_db(status='all')
    # 1. Dejar CouchDB listo
    mock_rondin, check_ids = do_crear_check_areas(acceso_obj, mock_check_basic)
    # check_ids = _crear_check_areas(acceso_obj, mock_rondin, mock_check_basic)
    rondin_id = mock_rondin['_id']
    logging.info(f'CouchDB listo — rondín {rondin_id} + {len(check_ids)} áreas')
 
    # 2. Sincronizar a LinkaForm / MongoDB
    response = acceso_obj.sync_records(app_records=[])
    print('response sync =', simplejson.dumps(response, indent=2))
    assert response is not None

    errors = response.get('results', {}).get('errors', [])
    assert errors == [], f"sync_records tuvo errores:\n{simplejson.dumps(errors, indent=2)}"
