# coding: utf-8

"""
Toggles de foto e identificación de + Nuevo Pase (apply_habilitar_overrides):
lo que manda el pase gana sobre lo que pide la ubicación. Función pura, sin
preprod.
Notion: TB-196.
"""

import pytest

from ..data.pases_entrada_data import HABILITAR_SI, HABILITAR_NO, REQUIERE_IDENTIFICACION


@pytest.mark.unit
def test_toggles_ganan_sobre_la_configuracion_de_la_ubicacion(accesos_no_api):
    """
    TB-196: en una ubicación que pide solo identificación, habilitar_fotografia
    "sí" debe agregar la foto y habilitar_identificacion "no" debe quitar la
    identificación. Sin los toggles se respeta lo que pide la ubicación. Si
    no, el pase pide (o se salta) datos que el admin decidió al crearlo.
    """
    toggles = {"habilitar_fotografia": HABILITAR_SI, "habilitar_identificacion": HABILITAR_NO}
    con_toggles = accesos_no_api.apply_habilitar_overrides(toggles, list(REQUIERE_IDENTIFICACION))
    assert sorted(con_toggles) == ["fotografia"], f"Con los toggles quedó {con_toggles}"

    sin_toggles = accesos_no_api.apply_habilitar_overrides({}, list(REQUIERE_IDENTIFICACION))
    assert sorted(sin_toggles) == REQUIERE_IDENTIFICACION, f"Sin los toggles quedó {sin_toggles}"
