# coding: utf-8

"""
Validaciones al crear un pase (create_access_pass, + Nuevo Pase y auto
registro) sin tocar preprod: se simula todo lo que la función consulta fuera
y se revisa que el pase no se guarde cuando no debe.
Notion: TB-202 a TB-206.
"""

import pytest

from .helpers import crear_pase_simulado, pase_nuevo
from ..data.pases_entrada_data import CAMPOS_REQUERIDOS


@pytest.mark.unit
def test_pase_sin_ubicacion_perfil_ni_visita_a_responde_que_falta(accesos_no_api, mocker):
    """
    TB-202: un pase sin ubicaciones, perfil ni a quién visita debe detenerse
    con el error "Faltan campos requeridos" que nombra los tres, y no
    guardarse. Si se guarda, queda un pase que ninguna caseta puede validar.
    """
    guardar = crear_pase_simulado(accesos_no_api, mocker)
    pase = pase_nuevo(accesos_no_api, **{campo: [] for campo in CAMPOS_REQUERIDOS})

    with pytest.raises(Exception, match="Faltan campos requeridos") as error:
        accesos_no_api.create_access_pass(pase)
    for campo in CAMPOS_REQUERIDOS:
        assert campo in str(error.value), f"El error no nombra '{campo}': {error.value}"
    guardar.assert_not_called()
