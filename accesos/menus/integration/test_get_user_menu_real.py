def test_get_user_menu_real(accesos_api):
    menu = accesos_api.get_config_accesos()
    assert isinstance(menu, dict)
