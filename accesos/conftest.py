import pytest
from lkf_modules.accesos.items.scripts.Accesos.accesos_utils import Accesos
from account_settings import settings

@pytest.fixture
def accesos_no_api():
    """
    Accesos SIN pegar a API / prod
    """
    return Accesos(settings, use_api=False)

@pytest.fixture
def accesos_api():
    """
    Accesos con llamadas reales a API
    """
    acc = Accesos(settings, use_api=True)
    acc.user = {"user_id": 10}
    # acc.employee_fields = {"user_id_id": "user_id"}
    return acc