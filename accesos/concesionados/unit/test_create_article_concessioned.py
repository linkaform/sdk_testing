# coding: utf-8

"""
Crear una concesión (create_article_concessioned, + Nueva Concesión) sin
tocar preprod: se simula el guardado y se revisan los answers que se mandan
a la forma.
Notion: TB-236 a TB-238.
"""

import pytest

from ..data.concesionados_data import CONCESION_EMPLEADO


@pytest.mark.unit
def test_crear_concesion_sin_equipos_da_error_y_no_la_guarda(accesos_no_api, mocker):
    """
    TB-236: una concesión sin equipos debe detenerse con el error de que se
    requiere la lista de equipos y no guardarse. Si se guarda, queda una
    concesión que no presta nada y no se puede devolver.
    """
    guardar = mocker.patch.object(accesos_no_api.lkf_api, "post_forms_answers")

    with pytest.raises(Exception, match="Se requiere enviar lista de equipos concesionados"):
        accesos_no_api.create_article_concessioned(dict(CONCESION_EMPLEADO))
    guardar.assert_not_called()
