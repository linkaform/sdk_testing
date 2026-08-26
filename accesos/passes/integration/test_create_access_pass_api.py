import copy, pytest, simplejson
from datetime import datetime, timedelta
from pytz import timezone
from account_settings import settings
from passes.data.pase_entrada_data import PASE_ENTRADA

PREPROD_HOST = 'preprod.linkaform.com'
_es_preprod = settings.config.get('HOST') == PREPROD_HOST

def _hoy(tz_name='America/Monterrey'):
    return datetime.now().astimezone(timezone(tz_name)).strftime('%Y-%m-%d')


def _build_pase():
    pase = copy.deepcopy(PASE_ENTRADA)
    hoy = f"{_hoy()} 00:00:00"
    pase['fecha_desde_visita'] = hoy
    pase['fecha_desde_hasta'] = hoy
    return pase

@pytest.mark.integration
def test_create_access_pass_status_code_201(accesos_api):
    """
    T-C10-001: create_access_pass() debe responder 201 al crear un pase
    de entrada con datos validos. Si falla, ningun visitante puede
    pre-registrarse.
    """
    accesos_api.use_api = False  # create_access_pass requiere el contexto JWT interno aunque el fixture autentique por API key
    res = accesos_api.create_access_pass(_build_pase())

    assert res['status_code'] == 201


@pytest.mark.integration
def test_create_access_pass_fecha_pasado_deberia_fallar(accesos_api):
    """
    T-C10-006: Un pase con fecha de visita en el pasado NO deberia poder
    crearse.
    """
    accesos_api.use_api = False
    pase = copy.deepcopy(PASE_ENTRADA)
    hace_2_dias = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d 00:00:00')
    pase['fecha_desde_visita'] = hace_2_dias
    pase['fecha_desde_hasta'] = hace_2_dias

    with pytest.raises(Exception) as exc_info:
        accesos_api.create_access_pass(pase)

    error = simplejson.loads(str(exc_info.value)).get("exception", {})
    assert error.get("status") == 400, (
        f"Se esperaba rechazo por fecha pasada con status 400, se obtuvo: {error}"
    )


@pytest.mark.integration
@pytest.mark.xfail(
    _es_preprod,
    reason="Bug confirmado (T-C10-023 / T-C10-027): en preprod, create_qr.py usa "
           "'generar_qr' sin importarlo (NameError), este bug NO se reproduce en produccion "
           "(create_qr.py si funciona ahi), por eso el xfail solo aplica en preprod.",
    strict=True,
)
def test_update_full_pass_link_vacio_causa_unbound_local_error(accesos_api):
    """
    T-C10-023: confirma que update_full_pass no truena cuando el campo
    'link' llega vacio o None.
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

@pytest.mark.integration
def test_create_access_pass_link_docs_completos_permite_crear(accesos_api):
    """
    T-C10-026 (caso valido): un pase con 'link.docs' incluyendo tanto
    'agregarIdentificacion' como 'agregarFoto' SI deberia poder crearse.
    """
    accesos_api.use_api = False
    pase = _build_pase()
    pase['link'] = {
        'link': 'https://web.clave10.com/dashboard/pase-entrada',
        'docs': ['agregarIdentificacion', 'agregarFoto'],
    }
    res = accesos_api.create_access_pass(pase)

    assert res['status_code'] == 201, (
        f"Se esperaba que un pase con link.docs completo (identificacion "
        f"y fotografia) se creara sin problema, pero la API respondio "
        f"{res['status_code']}: {res.get('json')}"
    )


@pytest.mark.integration
@pytest.mark.parametrize("link_pase, id_caso", [
    ({'link': 'https://web.clave10.com/dashboard/pase-entrada', 'docs': []}, "sin_docs"),
    ({'link': 'https://web.clave10.com/dashboard/pase-entrada', 'docs': ["agregarIdentificacion"]}, "solo_identificacion"),
    ({'link': 'https://web.clave10.com/dashboard/pase-entrada', 'docs': ["agregarFoto"]}, "solo_foto"),
    (None, "sin_link"),
])
@pytest.mark.xfail(reason="Bug confirmado: create_access_pass no valida el campo 'link' antes de crear el pase (ni su ausencia total, ni que 'docs' incluya agregarIdentificacion y agregarFoto).", strict=True)
def test_create_access_pass_link_invalido_falla(accesos_api, link_pase, id_caso):
    """
    T-C10-026 (casos invalidos, fusionados): un pase NO deberia poder
    crearse si el campo 'link' esta ausente, o si 'link.docs' no incluye
    ambos documentos requeridos (identificacion y fotografia).
    """
    accesos_api.use_api = False
    pase = _build_pase()
    if link_pase is None:
        pase.pop('link', None)
    else:
        pase['link'] = link_pase
    res = accesos_api.create_access_pass(pase)

    assert res['status_code'] in (400, 422), (
        f"Se esperaba rechazo por 'link' invalido ({id_caso}), pero la API "
        f"respondio {res['status_code']} y creo el pase igual: {res.get('json')}"
    )