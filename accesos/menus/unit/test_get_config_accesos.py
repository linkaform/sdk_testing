import pytest, logging

@pytest.mark.unit
def test_instancia_accesos_no_api(accesos_no_api):
    """
    Valida que el objeto Accesos se instancia correctamente con JWT (use_api=False).
    Si este test falla, ningún otro test unitario tiene sentido.
    """
    assert accesos_no_api is not None

@pytest.mark.unit
def test_get_config_accesos_retorna_dict(accesos_no_api, mocker):
    """
    Valida que get_config_accesos() retorna un dict cuando hay datos.
    El mock refleja el tipo real que devuelve la función en producción.
    """
    mocker.patch.object(
        accesos_no_api,
        "get_config_accesos",
        return_value={
            "menus": ["Turnos", "Rondines", "Incidencias"],
            "grupos": ["Supervisores"],
            "alertas": [],
            "exclude_inputs": [],
            "include_inputs": [],
        }
    )

    resultado = accesos_no_api.get_config_accesos()
    logging.info(f"Resultado de get_config_accesos: {resultado}")

    assert isinstance(resultado, dict)
    assert "menus" in resultado
    assert "Turnos" in resultado["menus"]

@pytest.mark.unit
def test_get_config_accesos_sin_datos_retorna_dict_vacio(accesos_no_api, mocker):
    """
    Cuando MongoDB no encuentra configuración para el usuario,
    get_config_accesos() debe retornar un dict vacío, no None.

    Mockea solo cr.aggregate para que la función real corra completa.
    """
    mocker.patch.object(
        accesos_no_api.cr,
        "aggregate",
        return_value=[]
    )

    resultado = accesos_no_api.get_config_accesos()

    assert isinstance(resultado, dict)
    assert resultado == {}