# coding: utf-8

import sys
import pytest

from lkf_modules.accesos.items.scripts.Accesos.accesos_testing import Accesos
from account_settings import settings

# update_area.py y rondines.py (scripts de producción, no de testing) hacen
# `from accesos_utils import Accesos` -- un import bare que solo resuelve si
# su propio directorio está en sys.path. Eso pasa automáticamente cuando
# pytest corre con el pythonpath explícito de accesos/pytest.ini (rootdir =
# sdk_testing/accesos), pero NO en una corrida global (rootdir =
# sdk_testing/, ej. `./lkf test` sin argumentos), donde tumbaría TODA la
# colección con ModuleNotFoundError.
#
# Además, cuando SÍ está en sys.path (vía pytest.ini), queda DESPUÉS de "."
# en el orden -- y "." también resuelve "rondines" porque existe la carpeta
# de tests sdk_testing/accesos/rondines/ (paquete con __init__.py) con el
# mismo nombre que el script real. Por eso no basta con "insertar si no
# está": hay que forzar la posición 0 durante el import puntual y restaurar
# el sys.path original después, para no contaminar la resolución de otros
# archivos de test en la misma sesión de pytest.
_ACCESOS_SCRIPTS_DIR = "/usr/local/lib/python3.10/site-packages/lkf_modules/accesos/items/scripts/Accesos"


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
        for leaked in ("update_area", "rondines", "accesos_utils"):
            sys.modules.pop(leaked, None)


AreaAccesos = _import_script_accesos_class("update_area")
RondinesAccesos = _import_script_accesos_class("rondines")

GUARDIA_USER = {
    'username': 'seguridad@linkaform.com',
    'parent_id': 10,
    'user_id': 10,
    'timezone': 'America/Monterrey',
    'email': 'seguridad@linkaform.com',
}


@pytest.fixture
def acceso_obj():
    """Instancia usada para el flujo de turno (load_shift/checkin/checkout)."""
    acc = Accesos(settings, use_api=True)
    acc.user = dict(GUARDIA_USER)
    return acc


@pytest.fixture
def area_obj():
    """
    Instancia usada para crear áreas. `create_new_area` solo existe en la
    subclase local de update_area.py, no en la clase Accesos base.
    """
    acc = AreaAccesos(settings, use_api=True)
    acc.user = dict(GUARDIA_USER)
    return acc


@pytest.fixture
def rondines_obj():
    """
    Instancia usada para verificar que un área ya sea visible para
    configurar un rondín. `get_catalog_areas` solo existe en la subclase
    local de rondines.py, no en la clase Accesos base.
    """
    acc = RondinesAccesos(settings, use_api=True)
    acc.user = dict(GUARDIA_USER)
    return acc
