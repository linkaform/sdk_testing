# coding: utf-8

import pytest
import copy
import logging

###
from lkf_modules.accesos.items.scripts.Accesos.accesos_testing import Accesos
from account_settings import settings
from .data.concesiones_data import CONCESION_BASE

@pytest.fixture
def accesos_obj():
    acc = Accesos(settings, use_api=True)
    return acc

@pytest.fixture
def mock_crea_consecion():
    return copy.deepcopy(CONCESION_BASE)

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

