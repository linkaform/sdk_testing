import copy, pytest, simplejson
from datetime import datetime, timedelta
from pytz import timezone

from passes.data.pase_entrada_data import PASE_ENTRADA
from account_settings import settings

# T-C10-027: el bug de 'generar_qr' no definido en create_qr.py (ver Notion)
# solo existe en preprod; en produccion create_qr.py funciona correctamente.
# Usamos esto para que el xfail de ese bug aplique unicamente cuando se
# corre contra preprod, y no marque un falso "failed" al correr en prod.
PREPROD_HOST = 'preprod.linkaform.com'
_es_preprod = settings.config.get('HOST') == PREPROD_HOST

# La cuenta de pruebas (account_10) opera en zona horaria 'America/Santo_Domingo'
# (confirmado en el 'timezone' que regresa la API en cada creacion de pase).
ACCOUNT_TIMEZONE = 'America/Santo_Domingo'

def _hoy(tz_name=ACCOUNT_TIMEZONE):
    return datetime.now().astimezone(timezone(tz_name)).strftime('%Y-%m-%d')

def _build_pase():
    pase = copy.deepcopy(PASE_ENTRADA)
    hoy = f"{_hoy()} 00:00:00"
    pase['fecha_desde_visita'] = hoy
    pase['fecha_desde_hasta'] = hoy
    return pase

@pytest.mark.integration
@pytest.mark.prod_test
@pytest.mark.xfail(
    _es_preprod,
    reason="Bug confirmado (T-C10-023 / T-C10-027): en preprod, create_qr.py usa "
           "'generar_qr' sin importarlo (NameError), lo que hace que 'link_pass' nunca "
           "se asigne dentro del bloque 'if link_info:' de update_full_pass, causando "
           "UnboundLocalError. Confirmado que este bug NO reproduce en produccion "
           "(create_qr.py si funciona ahi), por eso el xfail solo aplica en preprod.",
    strict=True,
)
def test_update_full_pass_link_vacio_causa_unbound_local_error(accesos_api):
    """
    T-C10-023: confirma que update_full_pass no truena cuando el campo
    'link' llega vacio o None.
    Reutiliza los mismos valores de '_build_pase()' para no depender de
    catalogos/empleados especificos que solo existan en un ambiente en particular.
    """
    accesos_api.use_api = False
    pase = _build_pase()
    creado = accesos_api.create_access_pass(pase)
    assert creado['status_code'] == 201, f"No se pudo crear el pase base: {creado}"

    folio = creado['json']['folio']
    qr_code = creado['json']['id']
    hoy = _hoy()

    ubicacion = pase.get('ubicacion')
    visita_a = pase.get('visita_a')

    access_pass_update = {
        "created_from": "web",
        "nombre_pase": pase.get('nombre'),
        "email_pase": pase.get('email'),
        "empresa_pase": pase.get('empresa'),
        "telefono_pase": pase.get('telefono'),
        "ubicacion": ubicacion if isinstance(ubicacion, list) else [ubicacion],
        "tema_cita": "Test de regresion link vacio",
        "descripcion": "Descripcion actualizada por test de regresion",
        "perfil_pase": pase.get('perfil_pase'),
        "status_pase": "activo",
        "visita_a": visita_a if isinstance(visita_a, list) else [visita_a],
        # Caso de prueba: 'link' vacio, dispara el bug de link_pass no inicializado
        "link": {},
        "tipo_visita": "alta_de_nuevo_visitante",
        "enviar_correo_pre_registro": [],
        "tipo_visita_pase": "rango_de_fechas",
        "fecha_desde_visita": f"{hoy} 00:00:00",
        "fecha_desde_hasta": f"{hoy} 23:59:59",
        "config_dia_de_acceso": "cualquier_día",
        "config_dias_acceso": [],
        "config_limitar_acceso": 1,
        "grupo_areas_acceso": [],
        "grupo_instrucciones_pase": [{"tipo_comentario": "pase", "comentario_pase": ""}],
        "grupo_vehiculos": [],
        "grupo_equipos": [],
        "autorizado_por": pase.get('email'),
        "enviar_correo": [],
        "habilitar_vehiculo": "no",
        "acompanantes": 0,
        "acompanantes_grupo": [],
    }

    res = accesos_api.update_full_pass(
        access_pass_update, folio=folio, qr_code=qr_code,
        location=ubicacion if isinstance(ubicacion, list) else [ubicacion]
    )

    assert res['status_code'] in (200, 201, 202, 204), (
        f"Se esperaba que update_full_pass actualizara el pase {folio} "
        f"con 'link' vacio sin problema, pero respondio {res['status_code']}: {res.get('json')}"
    )