# coding: utf-8

import pytest
import copy
import logging
from datetime import datetime
from pytz import timezone

###
from lkf_modules.accesos.items.scripts.Accesos.rondines import Accesos
from account_settings import settings
from .data.rondines_data import *

def today_str(tz_name='America/Monterrey', date_format='date'):
    today = datetime.now()
    today = today.astimezone(timezone(tz_name))
    if date_format == 'datetime':
        str_today = datetime.strftime(today, '%Y-%m-%d %H:%M:%S')
    else:
        str_today = datetime.strftime(today, '%Y-%m-%d')
    return str_today

@pytest.fixture
def accesos_obj():
    acc = Accesos(settings, use_api=True)
    return acc

@pytest.fixture
def mock_pase():
    # acc_obj = accesos_obj()
    # today = acc_obj.get_today_format()
    # print('today=', today)
    pase = copy.deepcopy(PASE)
    today = today_str()
    pase["fecha_desde_visita"] = f"{today} 00:00:00"
    pase["fecha_desde_hasta"] = f"{today} 00:00:00"
    return pase

@pytest.fixture
def mock_pase_fecha_fija():
    # acc_obj = accesos_obj()
    # today = acc_obj.get_today_format()
    # print('today=', today)
    pase = copy.deepcopy(PASE_FECHA_FIJA)
    today = today_str()
    pase["fecha_desde_visita"] = f"{today} 00:00:00"
    return pase

@pytest.fixture
def mock_pase_auto_registro():
    return copy.deepcopy(PASE_AUTO_REGISTRO)


@pytest.fixture
def mock_locations():
    return copy.deepcopy(LOCATIONS)

@pytest.fixture
def mock_pase_auto_registro_sin_vista_a():
    data = copy.deepcopy(PASE_AUTO_REGISTRO_SIN_VISTA_A)
    data = data['access_pass']
    return data

@pytest.fixture
def mock_pase_nueva_vista():
    return copy.deepcopy(PASE_NUEVA_VISTA)

@pytest.fixture
def mock_update_pass_app():
    return copy.deepcopy(PASE_NUEVA_VISTA)
    
@pytest.fixture
def mock_location_areas():
    return copy.deepcopy(LOCATION_AREAS)

@pytest.fixture
def mock_completar_pase_usaurio_actual():
    return copy.deepcopy(COMPLETAR_PASE_USAURIO_ACTUAL)

@pytest.fixture
def mock_crear_rondin():
    return copy.deepcopy(CREATE_RONDIN)

# @pytest.fixture
# def accesos_turnos_api_15864():
#     acc = Accesos(settings, use_api=True)
#     acc.user = {
#         'username': 'juan.escutia@linkaform.com', 
#         'parent_id': 15864, 
#         'user_id': 15864, 
#         'exp': 1768694174, 
#         'timezone': 'America/Monterrey', 
#         'is_mobile': False, 
#         'device_os': 'web', 
#         'email': 'juan.escutia@linkaform.com'
#     }
#     return acc

