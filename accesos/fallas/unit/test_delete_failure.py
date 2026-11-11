# coding: utf-8

"""
Eliminar fallas (delete_failure, delete-falla-modal): se simulan la búsqueda
del folio y el borrado, y se revisa qué registros se mandan a borrar.
Notion: TB-214 a TB-216.
"""

import pytest

from ..data.fallas_data import FOLIO_FALLA


@pytest.mark.unit
def test_folio_que_no_existe_da_error_y_no_borra(accesos_no_api, mocker):
    """
    TB-214: si el folio no se encuentra, delete_failure debe detenerse con
    el error de folio no encontrado y no mandar a borrar nada. Si borra, el
    guardia no se entera de que la falla que quería quitar no existía.
    """
    mocker.patch.object(accesos_no_api, "get_record_by_folio", return_value={})
    borrar = mocker.patch.object(accesos_no_api.lkf_api, "patch_record_list")

    with pytest.raises(Exception, match="No se encontro el folio correspondiente"):
        accesos_no_api.delete_failure([FOLIO_FALLA])
    borrar.assert_not_called()


@pytest.mark.unit
def test_sin_folios_da_error_y_no_borra(accesos_no_api, mocker):
    """
    TB-215: con la lista de folios vacía, delete_failure debe detenerse con
    el error de lista vacía y no mandar a borrar nada.
    """
    borrar = mocker.patch.object(accesos_no_api.lkf_api, "patch_record_list")

    with pytest.raises(Exception, match="Lista de folios vacia"):
        accesos_no_api.delete_failure([])
    borrar.assert_not_called()
