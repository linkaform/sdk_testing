"""Plugin de pytest: marker `target` y opcion `--target=`.

`@pytest.mark.target("create_access_pass", ...)` va en los tests que PRUEBAN
esa funcion, no en los que solo la usan de preparacion. Un test puede tener
varios targets. El nombre es el del metodo/funcion, sin clase.

`./lkf test` saca las funciones cambiadas (bin/lkf_changes.py de addons) y
corre:  pytest --target=get_shift_data,do_checkin

  - Se quedan solo los tests cuyo target coincide; el resto sale deseleccionado.
  - Si no queda ninguno, pytest termina con codigo 5 (no tests collected):
    ./lkf test lo toma como "funcion sin tests", no como fallo.
  - Se combina con -m: `--target=x -m unit` corre solo los unit de x.

Se carga desde el conftest.py de cada modulo con `pytest_plugins = ["lkf_target"]`
(el pytest.ini del modulo agrega `..` al pythonpath para encontrarlo).
"""


def pytest_addoption(parser):
    parser.addoption(
        "--target",
        action="append",
        default=[],
        metavar="FUNC[,FUNC...]",
        help="Corre solo los tests marcados con @pytest.mark.target de esas funciones.",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "target(*funciones): funciones que este test prueba (para ./lkf test --target=)",
    )


def targets_of(item):
    return {arg for mark in item.iter_markers("target") for arg in mark.args}


def pytest_collection_modifyitems(config, items):
    wanted = {t.strip() for opt in config.getoption("--target") for t in opt.split(",") if t.strip()}
    if not wanted:
        return
    keep, drop = [], []
    for item in items:
        (keep if targets_of(item) & wanted else drop).append(item)
    if drop:
        config.hook.pytest_deselected(items=drop)
    items[:] = keep
    config._lkf_cubiertos = sorted({t for item in keep for t in targets_of(item)} & wanted)


def pytest_terminal_summary(terminalreporter, config):
    """Linea que lee ./lkf test para saber que funciones tienen tests (tras -m)."""
    if config.getoption("--target"):
        terminalreporter.write_line("LKF_TARGETS_CUBIERTOS=" + ",".join(getattr(config, "_lkf_cubiertos", [])))
