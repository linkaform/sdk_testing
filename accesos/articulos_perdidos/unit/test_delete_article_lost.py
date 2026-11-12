# coding: utf-8

"""
Eliminar artículos perdidos (delete_article_lost): se simulan la búsqueda
del folio y el borrado, y se revisa qué registros se mandan a borrar.
Notion: TB-226 a TB-228.
"""

import pytest

from ..data.perdidos_data import FOLIO_ARTICULO


@pytest.mark.unit
def test_folio_que_no_existe_da_error_y_no_borra(accesos_no_api, mocker):
    """
    TB-226: si el folio no se encuentra, delete_article_lost debe detenerse
    con el error de folio no encontrado y no mandar a borrar nada. Si borra,
    el guardia no se entera de que el artículo que quería quitar no existía.
    """
    mocker.patch.object(accesos_no_api, "get_record_by_folio", return_value={})
    borrar = mocker.patch.object(accesos_no_api.lkf_api, "patch_record_list")

    with pytest.raises(Exception, match="No se encontro el folio correspondiente"):
        accesos_no_api.delete_article_lost([FOLIO_ARTICULO])
    borrar.assert_not_called()


@pytest.mark.unit
def test_sin_folios_da_error_y_no_borra(accesos_no_api, mocker):
    """
    TB-227: con la lista de folios vacía, delete_article_lost debe detenerse
    con el error de lista vacía y no mandar a borrar nada.
    """
    borrar = mocker.patch.object(accesos_no_api.lkf_api, "patch_record_list")

    with pytest.raises(Exception, match="Lista de folios vacia"):
        accesos_no_api.delete_article_lost([])
    borrar.assert_not_called()
