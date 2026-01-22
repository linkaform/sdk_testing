import pytest
from lkf_modules.accesos.items.scripts.Accesos.accesos_testing import Accesos
from account_settings import settings

@pytest.fixture
def accesos_turnos_api():
    acc = Accesos(settings, use_api=True)
    acc.user = {
        'username': 'seguridad@linkaform.com', 
        'parent_id': 10, 
        'user_id': 10, 
        'exp': 1768694174, 
        'timezone': 'America/Monterrey', 
        'is_mobile': False, 
        'device_os': 'web', 
        'email': 'seguridad@linkaform.com'
    }
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