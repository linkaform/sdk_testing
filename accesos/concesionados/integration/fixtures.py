# coding: utf-8

import pytest
import copy
import logging

###
from lkf_modules.accesos.items.scripts.Accesos.accesos_testing import Accesos
from account_settings import settings
from .data.concesiones_data import *

@pytest.fixture
def acceso_obj():
    acc = Accesos(settings, use_api=True)
    return acc

@pytest.fixture
def accesos_turnos_api_15864():
    acc = Accesos(settings, use_api=True)
    acc.user = {
        'username': 'juan.escutia@linkaform.com', 
        'parent_id': 15864, 
        'user_id': 15864, 
        'exp': 1768694174, 
        'timezone': 'America/Monterrey', 
        'is_mobile': False, 
        'device_os': 'web', 
        'email': 'juan.escutia@linkaform.com'
    }
    return acc

@pytest.fixture
def mock_crea_consecion():
    data = copy.deepcopy(CONCESION_BASE)
    return data['data_artilce']

@pytest.fixture
def mock_crea_consecion_otro():
    data = copy.deepcopy(CONCESION_BASE_OTRO)
    return data['data_artilce']

@pytest.fixture
def mock_lista_concesionados():
    res = {}
    data = copy.deepcopy(CONCESION_BASE)
    res['location'] = data['data_artilce']['ubicacion_concesion']
    res['area'] = data['data_artilce']['area_concesion']
    res['filterDate'] = None #data['fecha_concesion'] #crear rango
    return res
