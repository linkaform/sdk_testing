# coding: utf-8

import copy
import sys
import pytest

from account_settings import settings
from passes.integration.helpers import fecha_str
from ..data.control_patio_data import PASE_TRANSPORTISTA

# Los métodos de Control de patio (get_bitac_transportista_record,
# save_bitac_transportista_record, ...) viven en el script transportistas.py,
# no en accesos_utils. Mismo patrón que flujo_guardia/e2e/fixtures.py: el
# directorio del script va en la posición 0 de sys.path solo durante el
# import, porque la carpeta de tests accesos/transportistas/ se llama igual
# que el script.
_ACCESOS_SCRIPTS_DIR = "/usr/local/lib/python3.12/site-packages/lkf_modules/accesos/items/scripts/Accesos"


def _import_script_accesos_class(module_name):
    original_path = list(sys.path)
    if _ACCESOS_SCRIPTS_DIR in sys.path:
        sys.path.remove(_ACCESOS_SCRIPTS_DIR)
    sys.path.insert(0, _ACCESOS_SCRIPTS_DIR)
    try:
        module = __import__(module_name)
        return module.Accesos
    finally:
        sys.path[:] = original_path
        for leaked in (module_name, "accesos_utils"):
            sys.modules.pop(leaked, None)


TransportistasAccesos = _import_script_accesos_class("transportistas")


@pytest.fixture
def patio_obj(accesos_api):
    """Cliente de transportistas.py con API Key y el usuario de la cuenta activa (ver conftest)."""
    acc = TransportistasAccesos(settings, use_api=True)
    acc.user = accesos_api.user
    return acc


@pytest.fixture
def mock_pase_transportista(patio_obj):
    """Pase de transportista para hoy, en el primer andén de la cuenta (get_andenes)."""
    andenes = patio_obj.get_andenes()
    assert andenes, "La cuenta no tiene andenes para programar el pase"

    pase = copy.deepcopy(PASE_TRANSPORTISTA)
    pase["lugar_entrega_recepcion"]["fecha_pase_transportista_desde"] = fecha_str(0)[:10]
    pase["lugar_entrega_recepcion"]["anden"] = andenes[0]
    return pase
