# coding: utf-8
import pytest, logging, copy

from .fixtures import acceso_transportista
from .data.pases_transportista_data import (
    PASE_ANDEN_1_COMPLETO,
    PASE_ANDEN_2_SIN_FECHA_HASTA,
    PASE_ANDEN_3_SIN_HORARIO,
    PASE_ANDEN_1_SIN_FECHA_HASTA_SIN_HORARIO,
    PASE_ANDEN_2_MULTIPLES_DOCUMENTOS,
    PASE_ANDEN_3_SIN_DOCUMENTOS,
)

log = logging.getLogger(__name__)


@pytest.mark.integration
def test_create_pase_transportista_anden_1_completo(acceso_transportista):
    """Crea un pase con todos los campos: fecha_desde, fecha_hasta, horario y andén 1."""
    res = acceso_transportista.create_pass_transportista(copy.deepcopy(PASE_ANDEN_1_COMPLETO))
    assert res.get("status_code") in [200, 201, 202], res
    assert res.get("json", {}).get("id"), res


@pytest.mark.integration
def test_create_pase_transportista_anden_2_sin_fecha_hasta(acceso_transportista):
    """Crea un pase sin fecha_hasta en andén 2."""
    res = acceso_transportista.create_pass_transportista(copy.deepcopy(PASE_ANDEN_2_SIN_FECHA_HASTA))
    assert res.get("status_code") in [200, 201, 202], res
    assert res.get("json", {}).get("id"), res


@pytest.mark.integration
def test_create_pase_transportista_anden_3_sin_horario(acceso_transportista):
    """Crea un pase sin horario_disponible en andén 3."""
    res = acceso_transportista.create_pass_transportista(copy.deepcopy(PASE_ANDEN_3_SIN_HORARIO))
    assert res.get("status_code") in [200, 201, 202], res
    assert res.get("json", {}).get("id"), res


@pytest.mark.integration
def test_create_pase_transportista_anden_1_sin_fecha_hasta_sin_horario(acceso_transportista):
    """Crea un pase sin fecha_hasta ni horario, con múltiples documentos en andén 1."""
    res = acceso_transportista.create_pass_transportista(copy.deepcopy(PASE_ANDEN_1_SIN_FECHA_HASTA_SIN_HORARIO))
    assert res.get("status_code") in [200, 201, 202], res
    assert res.get("json", {}).get("id"), res


@pytest.mark.integration
def test_create_pase_transportista_anden_2_multiples_documentos(acceso_transportista):
    """Crea un pase con 3 documentos distintos en andén 2."""
    res = acceso_transportista.create_pass_transportista(copy.deepcopy(PASE_ANDEN_2_MULTIPLES_DOCUMENTOS))
    assert res.get("status_code") in [200, 201, 202], res
    assert res.get("json", {}).get("id"), res


@pytest.mark.integration
def test_create_pase_transportista_anden_3_sin_documentos(acceso_transportista):
    """Crea un pase sin documentos en andén 3."""
    res = acceso_transportista.create_pass_transportista(copy.deepcopy(PASE_ANDEN_3_SIN_DOCUMENTOS))
    assert res.get("status_code") in [200, 201, 202], res
    assert res.get("json", {}).get("id"), res
