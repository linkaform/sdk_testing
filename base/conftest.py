"""
Fixtures de las pruebas del módulo Base (Usuarios y Logs).

Las pantallas de Usuarios, Script Log y Workflow Log las sirve Sanic
(users_sdk.py, script_logs_sdk.py y workflow_logs_sdk.py ->
lkf_addons.base.app de lkf-sanic-apps) y sus clases no existen en addons. Por
eso aquí no se usa lkf_back.activar(): con --back=sanic (o LKF_BACK=sanic) se
importa la clase de Sanic directo y en addons los tests salen SKIPPED por su
marker back("sanic"). En addons no se carga nada: account_settings y las
clases solo se importan con Sanic.
"""

import copy
import os
import sys

import pytest

# marker target + --target= para ./lkf test (ver ../lkf_target.py)
# marker back("sanic") (ver ../lkf_back.py)
import lkf_back
pytest_plugins = ["lkf_target", "lkf_back"]
if lkf_back.back() == "sanic":
    for ruta in (lkf_back.SANIC_APP, os.path.join(lkf_back.SANIC_APP, "config")):
        if ruta not in sys.path:
            sys.path.insert(0, ruta)
    from lkf_addons.base.app import UsersAdmin
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
def _usuarios_base():
    """La instancia se crea una sola vez por corrida, como en la ruta de Sanic."""
    return UsersAdmin(settings)


@pytest.fixture
def usuarios_admin(_usuarios_base):
    """Copia de la instancia de la corrida con el usuario de la cuenta activa.
    Mockear siempre con mocker."""
    admin = copy.copy(_usuarios_base)
    admin.user = _usuario_cuenta_activa()
    return admin
