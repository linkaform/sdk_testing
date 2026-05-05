# coding: utf-8
# fixtures.py

import pytest
import copy
import logging
from datetime import datetime
from pytz import timezone

###
from lkf_modules.accesos.items.scripts.Accesos.accesos_testing import Accesos
from account_settings import settings
from .data.rondines_data import *


print('loading fixtures....')

def today_str(tz_name='America/Monterrey', date_format='date'):
    today = datetime.now()
    today = today.astimezone(timezone(tz_name))
    if date_format == 'datetime':
        str_today = datetime.strftime(today, '%Y-%m-%d %H:%M:%S')
    else:
        str_today = datetime.strftime(today, '%Y-%m-%d')
    return str_today

def mock_airflow_params(form_id):
    """
    utiliza exactamente como dejaria los parametros en airflow.
    """
    params =  {'form_id': form_id, 
            'answers': {
                '66a83ad2e004a874a4a08d7f': {'663e5c57f5b8a7ce8211ed0b': 'Planta Monterrey', '6645050d873fc2d733961eba': 'NFC Rondin Oficina JP'}, 
                '6760a8e68cef14ecd7f8b6fe': today, 
                '6639b2744bb44059fc59eb62': 'programado', 
                '69b9b98d2a02f4a0dd35f5c1': 'nfc'}
            }
    return params

@pytest.fixture
def acceso_obj():
    acc = Accesos(settings, use_api=True)
    db_name = f"clave_{acc.user['user_id']}"
    print('db_name', db_name)
    acc.cr_db = acc.get_couch_user_db(db_name)
    acc.test = True
    return acc

# @pytest.fixture
# def mock_rondin():
#     data = copy.deepcopy(RONDIN_EJEMPLO)
#     return data




@pytest.fixture
def mock_check_basic():
    data = copy.deepcopy(CHECK_BASIC)
    return data