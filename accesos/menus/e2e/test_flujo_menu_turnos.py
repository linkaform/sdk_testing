import pytest, logging

from menus.data.expected_menu_data import VALID_MENUS

LOCATION = "Planta Monterrey"
AREA = "Caseta Principal"
FOTOGRAFIA = [
    {
        "file_name": "evidencia.jpeg",
        "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/116852/660459dde2b2d414bce9cf8f/69e902cfcd137717f26908e7.jpeg"
    }
]

@pytest.mark.e2e
def test_flujo_turno_completo(accesos_api):
    """
    Flujo completo de un guardia:
    1. Obtiene su menú y valida que tiene acceso a turnos
    2. Obtiene la información del turno
    3. Hace checkin
    4. Hace checkout con el checkin_id obtenido

    Si cualquier paso falla, el flujo se detiene — cada paso depende del anterior.
    """

    # -- Paso 1: Validar que el usuario tiene turnos en su menú
    menu = accesos_api.get_config_accesos()
    assert isinstance(menu, dict), "get_config_accesos no retornó un dict"
    assert "menus" in menu, "La respuesta no tiene la clave 'menus'"
    assert "turnos" in menu["menus"], "El usuario no tiene acceso al módulo de turnos"
    assert all(m in VALID_MENUS for m in menu["menus"]), (
        f"Menús inesperados: {set(menu['menus']) - set(VALID_MENUS)}"
    )
    logging.info(f"Menús disponibles: {menu['menus']}")

    # -- Paso 2: Obtener información del turno
    turno = accesos_api.get_shift_data(booth_location=LOCATION, booth_area=AREA)
    assert isinstance(turno, dict), "get_shift_data no retornó un dict"
    assert "guard" in turno, "La respuesta del turno no tiene la clave 'guard'"
    logging.info(f"Turno obtenido: {turno.get('location')}")

    # -- Paso 3: Hacer checkin
    checkin_resp = accesos_api.do_checkin(
        location=LOCATION,
        area=AREA,
        fotografia=FOTOGRAFIA
    )
    assert isinstance(checkin_resp, dict), "do_checkin no retornó un dict"
    assert checkin_resp.get("status_code") == 201, (
        f"Checkin falló con status {checkin_resp.get('status_code')}: {checkin_resp.get('json')}"
    )
    checkin_id = checkin_resp.get("json", {}).get("id")
    assert checkin_id, "No se obtuvo checkin_id del resultado del checkin"
    logging.info(f"Checkin exitoso, checkin_id: {checkin_id}")

    # -- Paso 4: Hacer checkout con el checkin_id obtenido
    checkout_resp = accesos_api.do_checkout(
        checkin_id=checkin_id,
        location=LOCATION,
        area=AREA,
        fotografia=FOTOGRAFIA
    )
    assert isinstance(checkout_resp, dict), "do_checkout no retornó un dict"
    assert checkout_resp.get("status_code") in [200, 201, 202], (
        f"Checkout falló con status {checkout_resp.get('status_code')}: {checkout_resp.get('json')}"
    )
    logging.info(f"Checkout exitoso para checkin_id: {checkin_id}")