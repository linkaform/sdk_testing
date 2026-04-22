import pytest, logging

from menus.integration.data.expected_menu_data import EXPECTED_MENU_KEYS, VALID_MENUS

@pytest.mark.integration
def test_get_config_accesos_api(accesos_api):
    """
    Smoke test: la API responde y retorna un dict.
    Si este falla, los demás no tienen sentido.
    """
    menu = accesos_api.get_config_accesos()
    assert isinstance(menu, dict)

@pytest.mark.integration
def test_get_config_accesos_tiene_claves_requeridas(accesos_api):
    """
    El dict debe contener las claves que la UI necesita para funcionar.
    Si falta alguna, el frontend falla silenciosamente.
    """
    menu = accesos_api.get_config_accesos()

    for clave in EXPECTED_MENU_KEYS:
        assert clave in menu, f"Falta la clave: {clave}"

@pytest.mark.integration
def test_get_config_accesos_menus_es_lista_no_vacia(accesos_api):
    """
    'menus' debe ser una lista con al menos un elemento.
    Un guardia sin menús no puede operar en el sistema.
    """
    menu = accesos_api.get_config_accesos()

    assert isinstance(menu["menus"], list)
    assert len(menu["menus"]) > 0
    assert all(m in VALID_MENUS for m in menu["menus"]), (
        f"Menús inesperados: {set(menu['menus']) - set(VALID_MENUS)}"
    )

@pytest.mark.integration
def test_get_config_accesos_alertas_estructura_correcta(accesos_api):
    """
    Cada alerta debe ser un dict con exactamente una clave (el nombre)
    y un valor que contenga 'accion'.
    """
    menu = accesos_api.get_config_accesos()

    for alerta in menu["alertas"]:
        assert isinstance(alerta, dict)
        nombre = list(alerta.keys())[0]
        assert "accion" in alerta[nombre], f"Alerta '{nombre}' no tiene 'accion'"