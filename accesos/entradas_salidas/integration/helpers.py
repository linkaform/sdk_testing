# coding: utf-8

"""
Helpers para las pruebas de integración de Entradas & Salidas.
Pegan contra la API/BD real (preprod) a través de `acceso_obj`.

Para crear y activar pases se reutilizan los helpers de passes/integration.
"""

from passes.integration.helpers import crear_pase, completar_pase_activo  # noqa: F401


def ultima_visita(acceso_obj, qr_code):
    """
    Última visita del pase según get_list_last_user_move. Falla con un mensaje
    claro si el pase no tiene visitas, en vez de un IndexError al hacer [0].
    """
    visitas = acceso_obj.get_list_last_user_move(qr_code, limit=1)
    assert visitas, f"El pase {qr_code} no tiene visitas en la bitácora"
    return visitas[0]


def dar_entrada(acceso_obj, qr_code, location, area):
    """Registra la entrada (do_access) y regresa el registro de bitácora creado."""
    res = acceso_obj.do_access(qr_code, location, area, {})
    assert res.get("status_code") in (200, 201, 202), f"No se pudo dar entrada a {qr_code}: {res}"
    registro = ultima_visita(acceso_obj, qr_code)
    assert registro["status_visita"] == "entrada", f"La entrada no quedó registrada: {registro}"
    return registro


def salida_silenciosa(acceso_obj, qr_code, location, area, record_id=None):
    """
    Limpieza: intenta registrar la salida e ignora el error si la persona ya
    no está dentro. Evita dejar entradas abiertas en preprod que bloqueen
    otros tests (validate_access_pass_location). Con `record_id` apunta a
    una visita específica.
    """
    try:
        acceso_obj.do_out(qr_code, location, area, record_id=record_id)
    except Exception:
        pass


def gafete_y_locker_disponibles(acceso_obj, location, area):
    """
    Busca un gafete y un locker de identificaciones 'Disponible' en la caseta.
    Regresa (gafete_id, locker_id) o (None, None) si la cuenta no tiene.
    """
    gafetes = acceso_obj.get_gafetes(status="Disponible", location=location, area=area, limit=1)
    lockers = acceso_obj.get_lockers(
        status="Disponible", location=location, area=area, tipo_locker="Identificaciones", limit=1
    )
    if not gafetes or not lockers:
        return None, None
    return gafetes[0]["gafete_id"], lockers[0]["locker_id"]
