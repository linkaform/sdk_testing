import copy, re, pytest, simplejson
from datetime import datetime, timedelta
from pytz import timezone

from passes.data.pase_entrada_data import PASE_ENTRADA

FOTO_VALIDA = [{
    'file_name': 'fotografia.jpeg',
    'file_url': 'https://f001.backblazeb2.com/file/app-linkaform/public-client-126/116852/660459dde2b2d414bce9cf8f/6a99bdcfd3c33eb08528d9a6.jpeg',
}]
IDENTIFICACION_VALIDA = [{
    'file_name': 'identificacion.png',
    'file_url': 'https://f001.backblazeb2.com/file/app-linkaform/public-client-126/116852/660459dde2b2d414bce9cf8f/6a99bde95b642b0dc79057b6.png',
}]


def _hoy(tz_name='America/Monterrey'):
    return datetime.now().astimezone(timezone(tz_name)).strftime('%Y-%m-%d')


def _build_pase():
    pase = copy.deepcopy(PASE_ENTRADA)
    hoy = f"{_hoy()} 00:00:00"
    pase['fecha_desde_visita'] = hoy
    pase['fecha_desde_hasta'] = hoy
    return pase


@pytest.mark.integration
def test_create_access_pass_fecha_hoy_permite_crear(accesos_api):
    """
    Un pase con fecha de visita igual al dia actual (caso borde frente
    a T-C10-006, que prueba fecha en el pasado) SI deberia poder crearse.
    """
    accesos_api.use_api = False
    hoy = f"{_hoy()} 00:00:00"
    pase = copy.deepcopy(PASE_ENTRADA)
    pase['fecha_desde_visita'] = hoy
    pase['fecha_desde_hasta'] = hoy

    res = accesos_api.create_access_pass(pase)

    assert res['status_code'] == 201, (
        f"Se esperaba que un pase con fecha de visita igual a hoy ({hoy}) "
        f"se creara sin problema, pero la API respondio {res['status_code']}: {res.get('json')}"
    )


@pytest.mark.integration
def test_create_access_pass_retorna_folio_valido(accesos_api):
    """
    El folio (ObjectId de Mongo) debe venir en la respuesta para poder
    completar el pase o generar el QR despues. Un folio ausente o mal
    formado rompe cualquier flujo posterior que dependa de el.
    """
    accesos_api.use_api = False  # create_access_pass requiere el contexto JWT interno aunque el fixture autentique por API key
    res = accesos_api.create_access_pass(_build_pase())

    folio = res.get('json', {}).get('id')
    assert isinstance(folio, str)
    assert len(folio) == 24


@pytest.mark.integration
def test_create_access_pass_folio_formato_valido(accesos_api):
    """
    El campo 'folio' (identificador legible) debe venir con un formato
    valido. Un folio mal formado rompe la impresion del pase o su
    busqueda posterior.
    """
    accesos_api.use_api = False
    res = accesos_api.create_access_pass(_build_pase())
    folio = res.get('json', {}).get('folio')
    assert isinstance(folio, str)
    assert re.match(r'^\d+(-\d+)?$', folio), f"Folio con formato inesperado: {folio}"


@pytest.mark.integration
def test_create_access_pass_timestamps_coherentes(accesos_api):
    """
    'created_at' y 'updated_at' deben ser numericos y, al momento de
    la creacion, updated_at debe ser mayor o igual a created_at.
    """
    accesos_api.use_api = False
    res = accesos_api.create_access_pass(_build_pase())
    data = res.get('json', {})
    assert isinstance(data.get('created_at'), (int, float))
    assert isinstance(data.get('updated_at'), (int, float))
    assert data['updated_at'] >= data['created_at']


@pytest.mark.integration
def test_create_access_pass_sin_nombre_falla(accesos_api):
    """
    Un pase sin 'nombre' (Nombre Completo) no debe poder crearse.
    Confirmado con la API: responde 400 con un mensaje de campo requerido.
    """
    accesos_api.use_api = False
    pase = _build_pase()
    pase.pop('nombre', None)
    res = accesos_api.create_access_pass(pase)

    assert res['status_code'] == 400

    errores = res.get('json', {})
    mensajes = [v for v in errores.values() if isinstance(v, dict)]
    assert any(
        e.get('label') == 'Nombre Completo' and 'requerido' in ' '.join(e.get('msg', []))
        for e in mensajes
    ), f"No se encontro el error esperado para 'Nombre Completo': {errores}"


@pytest.mark.integration
@pytest.mark.parametrize("campo, label_esperado", [
    ("email", "Email"),
    ("telefono", "Telefono"),
    ("ubicaciones", "Ubicacion"),
    ("perfil_pase", "Tipo de Visita"),
    ("visita_a", "Responsable (Visita A)"),
])
def test_create_access_pass_campo_requerido_falla(accesos_api, campo, label_esperado):
    """
    Un pase sin '{campo}' NO deberia poder crearse (campo obligatorio).

    NOTA: se corrigio en app.py que SOLO 'ubicaciones, 'ubicaciones', 'perfil_pase' 
    y 'visita_a' es obligatorio; los demas campos de este parametrize ya no deben fallar. 
    """
    accesos_api.use_api = False
    pase = _build_pase()
    pase.pop(campo, None)

    try:
        res = accesos_api.create_access_pass(pase)
        assert res['status_code'] in (400, 422), (
            f"Se esperaba rechazo por falta de '{campo}', pero la API "
            f"respondio {res['status_code']} y creo el pase igual: {res.get('json')}"
        )
    except Exception as exc_info:
        error = simplejson.loads(str(exc_info)).get("exception", {})
        assert error.get("status") == 400, (
            f"Se esperaba rechazo con status 400 por falta de '{campo}', "
            f"se obtuvo: {error}"
        )


@pytest.mark.integration
def test_create_access_pass_empresa_opcional_no_bloquea(accesos_api):
    """
    'empresa' es un campo opcional: un visitante no siempre pertenece a
    una empresa. Un pase sin 'empresa' SI deberia poder crearse.
    """
    accesos_api.use_api = False
    pase = _build_pase()
    pase.pop('empresa', None)
    res = accesos_api.create_access_pass(pase)

    assert res['status_code'] == 201, (
        f"Se esperaba que un pase sin 'empresa' se creara sin problema "
        f"(campo opcional), pero la API respondio {res['status_code']}: {res.get('json')}"
    )


@pytest.mark.integration
@pytest.mark.parametrize("campo, valor_invalido", [
    ("ubicacion", "Planta Marte"),
    ("perfil_pase", "Perfil Inventado"),
])
@pytest.mark.xfail(reason="Bug confirmado: backend no valida valores de catalogo en create_access_pass.", strict=True)
def test_create_access_pass_valor_catalogo_invalido_falla(accesos_api, campo, valor_invalido):
    """
    Un pase con '{campo}' fuera del catalogo valido NO deberia poder
    crearse. Al dia de hoy la API lo permite y responde 201 con
    cualquier valor, incluso inexistente en el catalogo.
    """
    accesos_api.use_api = False
    pase = _build_pase()
    pase[campo] = valor_invalido
    res = accesos_api.create_access_pass(pase)

    assert res['status_code'] in (400, 422), (
        f"Se esperaba rechazo por '{campo}'='{valor_invalido}' fuera de "
        f"catalogo, pero la API respondio {res['status_code']} y creo "
        f"el pase igual: {res.get('json')}"
    )


@pytest.mark.integration
@pytest.mark.parametrize("email_invalido", [
    "sin-arroba.com",
    "usuario@",
    "usuario@dominio",
    "usuario@@dominio.com",
    "usuario dominio.com",
    "usuario@dominio,com",
])
def test_create_access_pass_email_invalido_falla(accesos_api, email_invalido):
    """
    Un pase con 'email' en formato invalido (sin @, sin dominio, con
    espacios, doble @, etc.) NO deberia poder crearse.
    """
    accesos_api.use_api = False
    pase = _build_pase()
    pase['email'] = email_invalido
    res = accesos_api.create_access_pass(pase)

    assert res['status_code'] in (400, 422), (
        f"Se esperaba rechazo por email invalido '{email_invalido}', pero "
        f"la API respondio {res['status_code']} y creo el pase igual: {res.get('json')}"
    )


@pytest.mark.integration
@pytest.mark.parametrize("telefono_invalido", [
    "12345",           # menos de 10 digitos
    "123456789012",    # mas de 10 digitos
    "555abc4321",      # contiene letras
    "555-444-333!",    # contiene simbolos
    "",                # vacio
])
def test_create_access_pass_telefono_invalido_falla(accesos_api, telefono_invalido):
    """
    Un pase con telefono que no tenga exactamente 10 digitos numericos
    NO deberia poder crearse.
    """
    accesos_api.use_api = False
    pase = _build_pase()
    pase['telefono'] = telefono_invalido

    try:
        res = accesos_api.create_access_pass(pase)
        assert res['status_code'] in (400, 422), (
            f"Se esperaba rechazo por telefono invalido '{telefono_invalido}', "
            f"pero la API respondio {res['status_code']} y creo el pase igual: {res.get('json')}"
        )
    except Exception as exc_info:
        error = simplejson.loads(str(exc_info)).get("exception", {})
        assert error.get("status") == 400, (
            f"Se esperaba rechazo con status 400 por telefono invalido '{telefono_invalido}', "
            f"se obtuvo: {error}"
        )


@pytest.mark.integration
@pytest.mark.parametrize("nombre_especial", [
    "<script>alert(1)</script>",           # XSS
    "'; DROP TABLE users; --",             # SQL injection
    '{"$ne": null}',                       # NoSQL injection
    "Ñoño & Cía. <O'Brien> \"Test\"",      # acentos, ampersand, comillas
    "😀🎉👍 Test Emoji",                   # emojis
    "A" * 1000,                            # string muy largo
])
def test_create_access_pass_nombre_caracteres_especiales(accesos_api, nombre_especial):
    """
    El backend NO debe romperse (error 500) ni comportarse de forma
    insegura al recibir caracteres especiales, payloads de inyeccion
    (XSS, SQL, NoSQL) o strings muy largos en el campo 'nombre'.
    Se acepta que el pase se cree (200/201) o se rechace por validacion
    (400/422), pero nunca debe producir un error no controlado.
    """
    accesos_api.use_api = False
    pase = _build_pase()
    pase['nombre'] = nombre_especial
    res = accesos_api.create_access_pass(pase)

    assert res['status_code'] != 500, (
        f"El backend fallo con error de servidor al recibir nombre "
        f"'{nombre_especial[:50]}...': {res.get('json') or res.get('data')}"
    )
    assert res['status_code'] in (200, 201, 400, 422), (
        f"Codigo de respuesta inesperado ({res['status_code']}) para "
        f"nombre '{nombre_especial[:50]}...': {res.get('json') or res.get('data')}"
    )


@pytest.mark.integration
@pytest.mark.xfail(reason="Bug confirmado: backend no previene pases duplicados para el mismo visitante en la misma fecha en create_access_pass.", strict=True)
def test_create_access_pass_duplicado_misma_persona_fecha_falla(accesos_api):
    """
    No deberia poder crearse un segundo pase activo para el mismo
    visitante (mismo email) en la misma fecha de visita. Al dia de hoy
    la API lo permite y crea ambos pases con 201.
    """
    accesos_api.use_api = False
    pase = _build_pase()

    primer_res = accesos_api.create_access_pass(pase)
    assert primer_res['status_code'] == 201, (
        f"El primer pase deberia crearse sin problema: {primer_res.get('json')}"
    )

    segundo_res = accesos_api.create_access_pass(pase)
    assert segundo_res['status_code'] in (400, 409, 422), (
        f"Se esperaba rechazo por pase duplicado (mismo visitante, misma "
        f"fecha), pero la API respondio {segundo_res['status_code']} y "
        f"creo el pase igual: {segundo_res.get('json')}"
    )


@pytest.mark.integration
@pytest.mark.parametrize("visita_a_invalido", [
    "000000000000000000000000",   # ObjectId con formato valido pero inexistente
    "usuario_que_no_existe",      # valor claramente invalido
])
@pytest.mark.xfail(reason="Bug confirmado: backend no valida que 'visita_a' referencie un usuario existente en create_access_pass.", strict=True)
def test_create_access_pass_visita_a_usuario_inexistente_falla(accesos_api, visita_a_invalido):
    """
    Un pase con 'visita_a' (Responsable) que referencia un usuario
    inexistente NO deberia poder crearse. Al dia de hoy la API lo
    permite y responde 201 en vez de rechazarlo.
    """
    accesos_api.use_api = False
    pase = _build_pase()
    pase['visita_a'] = visita_a_invalido
    res = accesos_api.create_access_pass(pase)

    assert res['status_code'] in (400, 404, 422), (
        f"Se esperaba rechazo por 'visita_a' inexistente '{visita_a_invalido}', "
        f"pero la API respondio {res['status_code']} y creo el pase igual: {res.get('json')}"
    )


@pytest.mark.integration
def test_update_full_pass_regresion_actualiza_correctamente(accesos_api):
    """
    Prueba de regresion: confirma que update_full_pass existe y permite
    actualizar un pase existente.

    Reutiliza los mismos valores de '_build_pase()', en vez de datos nuevos
    inventados, para no depender de catalogos/empleados especificos
    que solo existan en un ambiente en particular.
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
        "tema_cita": "Test de regresion update_full_pass",
        "descripcion": "Descripcion actualizada por test de regresion",
        "perfil_pase": pase.get('perfil_pase'),
        "status_pase": "activo",
        "visita_a": visita_a if isinstance(visita_a, list) else [visita_a],
        "link": {
            "link": "https://web.clave10.com/dashboard/pase-update",
            "docs": [],
            "qr_code": qr_code,
            "creado_por_id": 10,
            "creado_por_email": pase.get('email')
        },
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
        f"sin problema, pero respondio {res['status_code']}: {res.get('json')}"
    )


@pytest.mark.integration
def test_create_access_pass_acompanantes_excede_limite_falla(accesos_api):
    """
    Si 'acompanantes_grupo' trae mas nombres que el numero declarado en
    'acompanantes', NO deberia poder crearse el pase.
    """
    accesos_api.use_api = False
    pase = _build_pase()
    pase['acompanantes'] = 1
    pase['acompanantes_grupo'] = ['Acompanante Uno', 'Acompanante Dos', 'Acompanante Tres']

    try:
        res = accesos_api.create_access_pass(pase)
        assert res['status_code'] in (400, 422), (
            f"Se esperaba rechazo por exceso de acompanantes, pero la API "
            f"respondio {res['status_code']} y creo el pase igual: {res.get('json')}"
        )
    except Exception as exc_info:
        error = simplejson.loads(str(exc_info)).get("exception", {})
        assert error.get("status") == 400, (
            f"Se esperaba rechazo con status 400 por exceso de acompanantes, "
            f"se obtuvo: {error}"
        )
 
@pytest.mark.integration
def test_create_access_pass_nueva_visita_falta_foto_no_activa(accesos_api):
    """
    created_from='nueva_visita' siempre evalua los requerimientos de la
    ubicacion. 'Planta Monterrey' pide foto e identificacion via config.
    Un pase sin 'foto' NO deberia quedar 'activo' (se queda 'proceso').
    """
    accesos_api.use_api = False
    pase = _build_pase()
    pase['ubicaciones'] = ['Planta Monterrey']
    pase['created_from'] = 'nueva_visita'
    pase.pop('foto', None)
    pase['identificacion'] = IDENTIFICACION_VALIDA
 
    res = accesos_api.create_access_pass(pase)
    assert res['status_code'] == 201, (
        f"Se esperaba que el pase se creara (201) aunque falte la foto, "
        f"pero la API respondio {res['status_code']}: {res.get('json')}"
    )
 
    folio = res['json']['folio']
    consulta = accesos_api.get_my_pases(
        tab_status="en_proceso",
        search_name=pase.get('nombre'),
        limit=10,
    )
    registros = consulta.get('records', [])
    pase_encontrado = next((r for r in registros if r.get('folio') == folio), None)
 
    assert pase_encontrado is not None, (
        f"No se encontro el pase con folio {folio} en get_my_pases "
        f"(tab_status='en_proceso'). Registros obtenidos: {registros}"
    )
    assert pase_encontrado.get('status_pase') == 'proceso', (
        f"Se esperaba status_pase='proceso' por falta de foto obligatoria "
        f"(created_from='nueva_visita'), se obtuvo: "
        f"{pase_encontrado.get('status_pase')!r} (registro completo: {pase_encontrado})"
    )
 
 
@pytest.mark.integration
def test_create_access_pass_auto_registro_falta_identificacion_no_activa(accesos_api):
    """
    created_from='auto_registro' siempre evalua los requerimientos de la
    ubicacion. 'Planta Monterrey' pide foto e identificacion via config.
    Un pase sin 'identificacion' NO deberia quedar 'activo' (se queda
    'proceso').
    """
    accesos_api.use_api = False
    pase = _build_pase()
    pase['ubicaciones'] = ['Planta Monterrey']
    pase['created_from'] = 'auto_registro'
    pase['foto'] = FOTO_VALIDA
    pase.pop('identificacion', None)
 
    res = accesos_api.create_access_pass(pase)
    assert res['status_code'] == 201, (
        f"Se esperaba que el pase se creara (201) aunque falte la "
        f"identificacion, pero la API respondio {res['status_code']}: "
        f"{res.get('json')}"
    )
 
    folio = res['json']['folio']
    consulta = accesos_api.get_my_pases(
        tab_status="en_proceso",
        search_name=pase.get('nombre'),
        limit=10,
    )
    registros = consulta.get('records', [])
    pase_encontrado = next((r for r in registros if r.get('folio') == folio), None)
 
    assert pase_encontrado is not None, (
        f"No se encontro el pase con folio {folio} en get_my_pases "
        f"(tab_status='en_proceso'). Registros obtenidos: {registros}"
    )
    assert pase_encontrado.get('status_pase') == 'proceso', (
        f"Se esperaba status_pase='proceso' por falta de identificacion "
        f"obligatoria (created_from='auto_registro'), se obtuvo: "
        f"{pase_encontrado.get('status_pase')!r} (registro completo: {pase_encontrado})"
    )
 
 
@pytest.mark.integration
def test_create_access_pass_app_created_from_siempre_proceso(accesos_api):
    """
    created_from='pase_de_entrada_app' SOLO evalua los requerimientos de
    obligatoriedad si el pase manda explicito 'habilitar_identificacion'/
    'habilitar_fotografia' (admin_override_habilitar). Sin ese override,
    NUNCA se evalua: el pase queda en 'proceso' sin importar si faltan
    foto/identificacion (a diferencia de nueva_visita/auto_registro, que
    siempre evaluan). Se omiten ambos campos para dejar esto claro.
 
    NOTA: se descarto forzar el override via 'habilitar_identificacion'/
    'habilitar_fotografia' porque ese campo es un catalogo con opciones
    que no logramos determinar (la API responde 400 "Respuesta
    incorrecta" con 'si'/'Si'/True); pendiente investigar el catalogo
    real si se quiere cubrir ese escenario en el futuro.
    """
    accesos_api.use_api = False
    pase = _build_pase()
    pase['created_from'] = 'pase_de_entrada_app'
    pase.pop('foto', None)
    pase.pop('identificacion', None)
 
    res = accesos_api.create_access_pass(pase)
    assert res['status_code'] == 201, (
        f"Se esperaba que el pase se creara (201) aunque falten foto e "
        f"identificacion, pero la API respondio {res['status_code']}: "
        f"{res.get('json')}"
    )
 
    folio = res['json']['folio']
    consulta = accesos_api.get_my_pases(
        tab_status="en_proceso",
        search_name=pase.get('nombre'),
        limit=10,
    )
    registros = consulta.get('records', [])
    pase_encontrado = next((r for r in registros if r.get('folio') == folio), None)
 
    assert pase_encontrado is not None, (
        f"No se encontro el pase con folio {folio} en get_my_pases "
        f"(tab_status='en_proceso'). Registros obtenidos: {registros}"
    )
    assert pase_encontrado.get('status_pase') == 'proceso', (
        f"Se esperaba status_pase='proceso' (created_from='pase_de_entrada_app' "
        f"sin override nunca evalua obligatoriedad), se obtuvo: "
        f"{pase_encontrado.get('status_pase')!r} (registro completo: {pase_encontrado})"
    )
 
 
@pytest.mark.integration
def test_create_access_pass_web_created_from_siempre_proceso(accesos_api):
    """
    Mismo caso que test_create_access_pass_app_created_from_siempre_proceso
    pero con created_from='pase_de_entrada_web'.
    """
    accesos_api.use_api = False
    pase = _build_pase()
    pase['created_from'] = 'pase_de_entrada_web'
    pase.pop('foto', None)
    pase.pop('identificacion', None)
 
    res = accesos_api.create_access_pass(pase)
    assert res['status_code'] == 201, (
        f"Se esperaba que el pase se creara (201) aunque falten foto e "
        f"identificacion, pero la API respondio {res['status_code']}: "
        f"{res.get('json')}"
    )
 
    folio = res['json']['folio']
    consulta = accesos_api.get_my_pases(
        tab_status="en_proceso",
        search_name=pase.get('nombre'),
        limit=10,
    )
    registros = consulta.get('records', [])
    pase_encontrado = next((r for r in registros if r.get('folio') == folio), None)
 
    assert pase_encontrado is not None, (
        f"No se encontro el pase con folio {folio} en get_my_pases "
        f"(tab_status='en_proceso'). Registros obtenidos: {registros}"
    )
    assert pase_encontrado.get('status_pase') == 'proceso', (
        f"Se esperaba status_pase='proceso' (created_from='pase_de_entrada_web' "
        f"sin override nunca evalua obligatoriedad), se obtuvo: "
        f"{pase_encontrado.get('status_pase')!r} (registro completo: {pase_encontrado})"
    )

@pytest.mark.integration
@pytest.mark.xfail(
    reason=(
        "auto_registro valida el telefono contra r'\\d{10}' (sin '+' ni "
        "codigo de pais), pero el front siempre manda el telefono CON "
        "prefijo (igual que los demas flujos)."
        ),
    strict=False,
)
def test_create_access_pass_status_code_201_auto_registro(accesos_api):
    """
    create_access_pass() debe responder 201 al crear un pase con
    created_from='auto_registro' y datos validos (flujo de autoregistro).
 
    Usa el telefono en el formato real que manda el front (con prefijo,
    igual que PASE_ENTRADA por default), no el formato de 10 digitos
    pelones que exige la validacion actual de auto_registro. Ver xfail.
    """
    accesos_api.use_api = False
    pase = _build_pase()
    pase['created_from'] = 'auto_registro'
    res = accesos_api.create_access_pass(pase)
 
    assert res['status_code'] == 201
 
@pytest.mark.integration
def test_create_access_pass_status_code_201_nueva_visita(accesos_api):
    """
    create_access_pass() debe responder 201 al crear un pase con
    created_from='nueva_visita' y datos validos (flujo de nueva visita).
    """
    accesos_api.use_api = False
    pase = _build_pase()
    pase['created_from'] = 'nueva_visita'
    res = accesos_api.create_access_pass(pase)
 
    assert res['status_code'] == 201