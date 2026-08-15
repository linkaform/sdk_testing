"""
Módulo de Configuración de Pruebas (Accesos)
===========================================

Este archivo define las fixtures de pytest compartidas para todas las pruebas
del módulo de Accesos. Proporciona diferentes contextos de autenticación y 
objetos de conexión configurados para facilitar el testing.

Uso de `use_api`:
----------------
* `use_api=True`: Autenticación mediante **API Key**.
* `use_api=False`: Autenticación mediante **JWT** (Token de sesión).

Fixtures disponibles:
--------------------
1. `accesos_no_api`: Contexto de seguridad usando JWT.
2. `accesos_api`: Contexto de seguridad usando API Key.
3. `accesos_api_15864`: Contexto de usuario específico (Juan Escutia) usando API Key.
"""

import pytest
from lkf_modules.accesos.items.scripts.Accesos.accesos_utils import Accesos
from account_settings import settings

PREPROD_HOST = 'preprod.linkaform.com'

def pytest_addoption(parser):
    parser.addoption(
        '--allow-prod-integration',
        action='store_true',
        default=False,
        help='Permite correr tests integration/e2e contra el entorno activo aunque no sea preprod.',
    )

@pytest.fixture(autouse=True)
def _requiere_entorno_preprod(request):
    """
    Los tests integration/e2e escriben datos reales (sin teardown). Si el
    ENV activo no es preprod, se abortan antes de tocar la red para no
    crear/mutar datos en una cuenta de producción por accidente.

    Para correr a propósito contra el entorno activo (incluyendo prod), pasar
    --allow-prod-integration al comando de pytest.
    """
    marks = {m.name for m in request.node.iter_markers()}
    if marks & {'integration', 'e2e'}:
        if request.config.getoption('--allow-prod-integration'):
            return
        host = settings.config.get('HOST')
        assert host == PREPROD_HOST, (
            f"Entorno activo apunta a '{host}', se esperaba '{PREPROD_HOST}'. "
            "Verifica ENV en config/enviorment.py antes de correr integration/e2e, "
            "o pasa --allow-prod-integration para correr a propósito contra el entorno activo."
        )

def _usuario_cuenta_activa():
    """
    Arma el dict de usuario a partir de la cuenta activa en settings.config
    (USERNAME/ACCOUNT_ID de config/local_settings.py), en vez de un usuario
    fijo. Así las fixtures corren contra cualquier cuenta que tengas activa
    localmente (ej. una cuenta de testing nueva) sin tener que editar este
    archivo cada vez.
    """
    username = settings.config.get('USERNAME')
    account_id = int(settings.config.get('ACCOUNT_ID'))
    return {
        'username': username,
        'parent_id': account_id,
        'user_id': account_id,
        'timezone': 'America/Monterrey',
        'email': username,
    }

@pytest.fixture
def accesos_no_api():
    """Retorna una instancia de Accesos configurada para autenticarse vía JWT (use_api=False), con el usuario de la cuenta activa."""
    acc = Accesos(settings, use_api=False)
    acc.user = _usuario_cuenta_activa()
    return acc

@pytest.fixture
def accesos_api():
    """Retorna una instancia de Accesos configurada para autenticarse vía API Key (use_api=True), con el usuario de la cuenta activa."""
    acc = Accesos(settings, use_api=True)
    acc.user = _usuario_cuenta_activa()
    return acc

@pytest.fixture
def accesos_api_15864():
    """Retorna una instancia de Accesos configurada para autenticarse vía API Key bajo el contexto de Juan Escutia (ID 15864)."""
    acc = Accesos(settings, use_api=True)
    acc.user = {
        'username': 'juan.escutia@linkaform.com', 
        'parent_id': 10, 
        'user_id': 15864, 
        'timezone': 'America/Monterrey', 
        'email': 'juan.escutia@linkaform.com'
    }
    return acc