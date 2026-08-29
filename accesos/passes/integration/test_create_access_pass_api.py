import copy, pytest, simplejson
from datetime import datetime, timedelta
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
