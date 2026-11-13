"""Plugin de pytest: correr la misma suite contra addons o contra Sanic.

Los tests importan la clase del modulo desde addons:

    from lkf_modules.accesos.items.scripts.Accesos.accesos_utils import Accesos

Con `--back=sanic` (o LKF_BACK=sanic) ese mismo import entrega la clase de
Sanic (`accesos_service.Accesos` de sdk-modules-sanic, que hereda de
`lkf_addons.accesos.service`), sin tocar ningun test. El default es addons,
asi que una corrida normal no cambia.

Se activa desde el conftest de cada suite, ANTES de importar la clase:

    import lkf_back
    lkf_back.activar("accesos")
    pytest_plugins = ["lkf_target", "lkf_back"]

En Sanic, un test que llama (o mockea) un metodo que la clase de Sanic no
tiene sale como SKIPPED "falta en sanic: <metodo>", no como fallo: es una
diferencia entre los dos backs que ./lkf test reporta como aviso.

Rutas (las arma ./lkf test, bin/lkf_test.py de addons, con los montajes del
docker-compose de clave10-sdk):
  /srv/lkf-sanic-app/app           repo lkf-sanic-apps (app/)
  /srv/lkf-sanic-app/app/modules   repo sdk-modules-sanic
  site-packages/lkf_addons         lkf-sanic-apps/addons (clases de Sanic)
  /srv/repo/modules                repo modules de addons (accesos_testing.py)
"""
import os
import re
import sys
import types

import pytest

SANIC_APP = "/srv/lkf-sanic-app/app"
ADDONS_MODULES = "/srv/repo/modules"

# suite -> (carpeta de scripts, modulo de addons, modulo de Sanic)
MODULOS = {
    "accesos": ("accesos/items/scripts/Accesos", "accesos_utils", "accesos_service"),
}


def back():
    """addons | sanic. Se lee de argv porque el conftest importa la clase
    antes de que pytest termine de parsear las opciones."""
    for i, arg in enumerate(sys.argv):
        if arg.startswith("--back="):
            return arg.split("=", 1)[1]
        if arg == "--back" and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return os.environ.get("LKF_BACK", "addons")


def activar(suite):
    """En Sanic, hace que lkf_modules.<suite>...<modulo addons> sea la clase de Sanic."""
    b = back()
    if b == "addons":
        return
    if b != "sanic":
        raise pytest.UsageError(f"--back={b}: usa addons o sanic")
    carpeta, mod_addons, mod_sanic = MODULOS[suite]
    for p in (SANIC_APP, os.path.join(SANIC_APP, "config"), os.path.join(SANIC_APP, "modules", carpeta)):
        if p not in sys.path:
            sys.path.insert(0, p)
    sanic = __import__(mod_sanic)
    # Paquetes padre vacios: el __init__ de items/scripts de addons importa
    # lkf_addons.items.script_resource, que en Sanic no es el mismo.
    nombre = "lkf_modules"
    sys.modules.setdefault(nombre, _paquete(nombre, []))
    for parte in carpeta.split("/"):
        nombre = f"{nombre}.{parte}"
        sys.modules.setdefault(nombre, _paquete(nombre, []))
    # La carpeta de scripts apunta al repo modules de addons: ahi viven los
    # helpers de pruebas (accesos_testing.py), que heredan de mod_addons.
    sys.modules[nombre].__path__ = [os.path.join(ADDONS_MODULES, carpeta)]
    sys.modules[f"{nombre}.{mod_addons}"] = sanic
    sys.modules[mod_addons] = sanic


# En addons, AccesosModel HEREDA de Employee, Location y Vehiculo; en Sanic los
# COMPONE (self.Employee, self.Location, self.AF) y llama, p. ej.,
# self.Employee.get_employee_data. Un test que mockea o lee algo de esas clases
# lo pide con de():  mocker.patch.object(de(acc, "get_employee_data"), "get_employee_data", ...)
COMPONENTES = ("Employee", "Location", "AF")


def de(obj, nombre):
    """El objeto donde vive `nombre`: obj (addons) o su componente (Sanic)."""
    if hasattr(obj, nombre):
        return obj
    for comp in COMPONENTES:
        sub = getattr(obj, comp, None)
        if sub is not None and hasattr(sub, nombre):
            return sub
    return obj


def _paquete(nombre, path):
    m = types.ModuleType(nombre)
    m.__path__ = path
    return m


def pytest_addoption(parser):
    parser.addoption("--back", default=None, choices=["addons", "sanic"],
                     help="Clase contra la que corren los tests (default addons; tambien LKF_BACK).")


def pytest_report_header(config):
    return f"lkf back: {back()}"


@pytest.hookimpl(hookwrapper=True)
def pytest_make_collect_report(collector):
    """En Sanic, un archivo que ni siquiera se puede importar (fixtures que cargan
    scripts de addons por nombre: update_area, transportistas...) sale SKIPPED
    "no aplica en sanic" en vez de tumbar la corrida con un error de coleccion."""
    outcome = yield
    rep = outcome.get_result()
    if back() != "sanic" or not rep.failed:
        return
    err = str(rep.longrepr).strip().splitlines()
    rep.outcome = "skipped"
    rep.longrepr = (str(collector.path), 0, f"Skipped: no aplica en sanic: {err[-1] if err else '?'}")


FALTA = re.compile(r"(?:object has no attribute|does not have the attribute) '(\w+)'")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if back() != "sanic" or not rep.failed or call.excinfo is None:
        return
    if not call.excinfo.errisinstance(AttributeError):
        return
    m = FALTA.search(str(call.excinfo.value))
    if not m:
        return
    rep.outcome = "skipped"
    rep.longrepr = (str(item.path), item.location[1] or 0, f"falta en sanic: {m[1]}")
