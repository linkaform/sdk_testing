import copy
from datetime import datetime

import pytest
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
