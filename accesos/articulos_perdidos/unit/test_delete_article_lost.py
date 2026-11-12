# coding: utf-8

"""
Eliminar artículos perdidos (delete_article_lost): se simulan la búsqueda
del folio y el borrado, y se revisa qué registros se mandan a borrar.
Notion: TB-226 a TB-228.
"""

import pytest

from ..data.perdidos_data import (
    FOLIO_ARTICULO,
    FOLIOS_ARTICULO,
    REGISTROS_ARTICULO,
    URL_REGISTRO,
    BORRADO_OK,
)


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


@pytest.mark.unit
def test_varios_articulos_manda_a_borrar_cada_registro(accesos_no_api, mocker):
    """
    TB-228: con dos folios, delete_article_lost debe mandar a borrar en una
    sola llamada el registro de cada uno, y ninguno más. Si falta uno, el
    artículo sigue en la lista; si sobra, se borra uno que el guardia no
    eligió.
    """
    mocker.patch.object(
        accesos_no_api, "get_record_by_folio", side_effect=lambda folio, *a, **k: {"_id": REGISTROS_ARTICULO[folio]}
    )
    borrar = mocker.patch.object(accesos_no_api.lkf_api, "patch_record_list")
    mocker.patch.object(accesos_no_api, "check_status_code", return_value=dict(BORRADO_OK))

    res = accesos_no_api.delete_article_lost(list(FOLIOS_ARTICULO))

    assert res == BORRADO_OK
    borrar.assert_called_once()
    esperados = [URL_REGISTRO.format(REGISTROS_ARTICULO[folio]) for folio in FOLIOS_ARTICULO]
    assert borrar.call_args.args[0] == {"deleted_objects": esperados}, f"Mandó a borrar {borrar.call_args.args[0]}"
