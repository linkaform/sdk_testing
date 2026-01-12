import pytest
from lkf_modules.accesos.items.scripts.Accesos.accesos_utils import Accesos
from account_settings import settings

@pytest.fixture
def accesos_no_api():
    acc = Accesos(settings, use_api=False)
    acc.user = {"user_id": 10, "email": "seguridad@linkaform.com"}
    return acc

@pytest.fixture
def accesos_api():
    acc = Accesos(settings, use_api=True)
    acc.user = {"user_id": 10, "email": "seguridad@linkaform.com"}
    return acc

@pytest.fixture
def accesos_api_15864():
    acc = Accesos(settings, use_api=True)
    acc.user = {"user_id": 15864, "email": "juan.escutia@linkaform.com"}
    return acc