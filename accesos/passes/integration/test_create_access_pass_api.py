import copy
import re
from datetime import datetime, timedelta

import pytest
import simplejson
from pytz import timezone

from passes.data.pase_entrada_data import PASE_ENTRADA


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
def test_create_access_pass_status_code_201(accesos_api):
    """
    create_access_pass() debe responder 201 al crear un pase de entrada
    con datos validos. Si falla, ningun visitante puede pre-registrarse.
    """
    accesos_api.use_api = False  # create_access_pass requiere el contexto JWT interno aunque el fixture autentique por API key
    res = accesos_api.create_access_pass(_build_pase())

    assert res['status_code'] == 201


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
def test_create_access_pass_fecha_pasado_deberia_fallar(accesos_api):
    """
    Un pase con fecha de visita en el pasado NO deberia poder crearse.
    """
    accesos_api.use_api = False
    pase = copy.deepcopy(PASE_ENTRADA)
    ayer = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d 00:00:00')
    pase['fecha_desde_visita'] = ayer
    pase['fecha_desde_hasta'] = ayer

    with pytest.raises(Exception) as exc_info:
        accesos_api.create_access_pass(pase)

    error = simplejson.loads(str(exc_info.value)).get("exception", {})
    assert error.get("status") == 400, (
        f"Se esperaba rechazo por fecha pasada con status 400, se obtuvo: {error}"
    )

@pytest.mark.integration
@pytest.mark.parametrize("campo, label_esperado", [
    ("email", "Email"),
    ("telefono", "Telefono"),
    ("ubicacion", "Ubicacion"),
    ("perfil_pase", "Tipo de Visita"),
    ("visita_a", "Responsable (Visita A)"),
])
@pytest.mark.xfail(reason="Bug confirmado: backend no valida estos campos como requeridos en create_access_pass.", strict=True)
def test_create_access_pass_campo_requerido_falla(accesos_api, campo, label_esperado):
    """
    Un pase sin '{campo}' NO deberia poder crearse (campo obligatorio
    confirmado con el equipo). Al dia de hoy la API lo permite y
    responde 201 en vez de rechazarlo.
    """
    accesos_api.use_api = False
    pase = _build_pase()
    pase.pop(campo, None)
    res = accesos_api.create_access_pass(pase)

    assert res['status_code'] in (400, 422), (
        f"Se esperaba rechazo por falta de '{campo}', pero la API "
        f"respondio {res['status_code']} y creo el pase igual: {res.get('json')}"
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
@pytest.mark.xfail(reason="Bug confirmado: backend no valida formato/longitud de 'telefono' en create_access_pass, a pesar de que se esperaban 10 digitos.", strict=True)
def test_create_access_pass_telefono_invalido_falla(accesos_api, telefono_invalido):
    """
    Un pase con 'telefono' que no cumple el formato esperado (10 digitos
    numericos) NO deberia poder crearse. Al dia de hoy la API lo permite
    y responde 201 en vez de rechazarlo, incluso con telefono vacio.
    """
    accesos_api.use_api = False
    pase = _build_pase()
    pase['telefono'] = telefono_invalido
    res = accesos_api.create_access_pass(pase)

    assert res['status_code'] in (400, 422), (
        f"Se esperaba rechazo por telefono invalido '{telefono_invalido}', pero "
        f"la API respondio {res['status_code']} y creo el pase igual: {res.get('json')}"
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