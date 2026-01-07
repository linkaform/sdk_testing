def test_dummy_menu(accesos_no_api):
    """
    Test simple para validar que el objeto Accesos
    se puede usar sin API
    """
    assert accesos_no_api is not None

def test_get_user_menu_mockeado(accesos_no_api, mocker):
    mocker.patch.object(
        accesos_no_api,
        "get_config_accesos",
        return_value=["Turnos", "Rondines", "Incidencias"]
    )

    menu = accesos_no_api.get_config_accesos()

    assert "Turnos" in menu
    assert len(menu) == 3

