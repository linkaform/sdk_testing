"""
Fixtures de las pruebas del módulo Location (Ubicaciones).

La pantalla de Ubicaciones la sirve Sanic (location_sdk.py ->
lkf_addons.location.service). Con --back=sanic (o LKF_BACK=sanic) lkf_back
entrega la clase de Sanic en el mismo import de addons, igual que en accesos.
"""

import copy
import pytest

# marker target + --target= para ./lkf test (ver ../lkf_target.py)
# --back=addons|sanic (ver ../lkf_back.py): activar() va antes de importar Location.
import lkf_back
lkf_back.activar("location")
pytest_plugins = ["lkf_target", "lkf_back"]
from lkf_modules.location.items.scripts.Locations.location_util import Location
from account_settings import settings


def pytest_addoption(parser):
    parser.addoption(
        '--bug',
        action='store',
        type=int,
        default=None,
        help='Corre solo los tests marcados con @pytest.mark.bug(<folio>) de ese ticket.',
    )


def pytest_collection_modifyitems(config, items):
    """Con --bug <folio> deja solo los tests que traen ese folio en su marker bug(...)."""
    folio = config.getoption('--bug')
    if folio is None:
        return
    seleccionados, descartados = [], []
    for item in items:
        folios = {f for m in item.iter_markers('bug') for f in m.args}
        (seleccionados if folio in folios else descartados).append(item)
    if descartados:
        config.hook.pytest_deselected(items=descartados)
        items[:] = seleccionados


def _usuario_cuenta_activa():
    """Usuario de la cuenta activa en settings.config (ver accesos/conftest.py)."""
    username = settings.config.get('USERNAME')
    account_id = int(settings.config.get('ACCOUNT_ID'))
    return {
        'username': username,
        'parent_id': account_id,
        'user_id': account_id,
        'timezone': 'America/Monterrey',
        'email': username,
    }


@pytest.fixture(scope='session')
def _location_no_api_base():
    """La instancia se crea una sola vez por corrida."""
    return Location(settings, use_api=False)


@pytest.fixture
def location_no_api(_location_no_api_base):
    """Copia de la instancia de la corrida con el usuario de la cuenta activa
    (JWT, use_api=False). Mockear siempre con mocker."""
    loc = copy.copy(_location_no_api_base)
    loc.user = _usuario_cuenta_activa()
    return loc
