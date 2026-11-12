# coding: utf-8

"""
Eliminar concesiones (delete_article_concessioned): se simula la búsqueda del
folio y se revisa que no se borre nada si el folio no existe.
Notion: TB-235.
"""

import pytest

from ..data.concesionados_data import FOLIO_CONCESION


@pytest.mark.unit
def test_folio_que_no_existe_da_error_y_no_borra(accesos_no_api, mocker):
    """
    TB-235: si el folio no se encuentra, delete_article_concessioned debe
    detenerse con el error de folio no encontrado y no mandar a borrar nada.
    Si borra, el guardia no se entera de que la concesión que quería quitar
    no existía.
    """
    mocker.patch.object(accesos_no_api, "get_record_by_folio", return_value={})
    borrar = mocker.patch.object(accesos_no_api.lkf_api, "patch_record_list")

    with pytest.raises(Exception, match="No se encontro el folio correspondiente"):
        accesos_no_api.delete_article_concessioned([FOLIO_CONCESION])
    borrar.assert_not_called()
