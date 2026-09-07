import pytest
 
from .fixtures import *
from .helpers import crear_pase, completar_pase_activo
 
 
@pytest.mark.integration
@pytest.mark.prod_test
def test_update_pass_completar_con_foto_e_identificacion(acceso_obj, mock_pase_do_access):
    """
    T-C10-034: Completar un pase con identificacion y fotografia.
 
    Un pase recien creado (sin foto/identificacion) queda en 'proceso'.
    Al completarlo via update_pass con walkin_fotografia +
    walkin_identificacion + visita_a, access_pass_set_status debe
    evaluar los requisitos como cumplidos y el pase debe quedar 'activo'.
    """
    folio = crear_pase(acceso_obj, mock_pase_do_access)
 
    detalle_inicial = acceso_obj.get_detail_access_pass(folio)
    assert detalle_inicial.get('estatus') == 'proceso', (
        f"Se esperaba que el pase recien creado quedara en 'proceso' antes "
        f"de completarlo, se obtuvo: {detalle_inicial.get('estatus')!r}"
    )
 
    detalle = completar_pase_activo(acceso_obj, folio)
 
    assert detalle.get('estatus') == 'activo', (
        f"Se esperaba que el pase quedara 'activo' tras completar foto e "
        f"identificacion, se obtuvo: {detalle.get('estatus')!r} "
        f"(detalle completo: {detalle})"
    )