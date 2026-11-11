# coding: utf-8

"""
Eliminar fallas (delete_failure, delete-falla-modal): se simulan la búsqueda
del folio y el borrado, y se revisa qué registros se mandan a borrar.
Notion: TB-214 a TB-216.
"""

import pytest

from ..data.fallas_data import FOLIO_FALLA, FOLIOS_FALLA, REGISTROS_FALLA, URL_REGISTRO, BORRADO_OK


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


@pytest.mark.unit
def test_varias_fallas_manda_a_borrar_cada_registro(accesos_no_api, mocker):
    """
    TB-216: con dos folios, delete_failure debe mandar a borrar en una sola
    llamada el registro de cada uno, y ninguno más. Si falta uno, la falla
    sigue en la lista; si sobra, se borra una que el guardia no eligió.
    """
    mocker.patch.object(
        accesos_no_api, "get_record_by_folio", side_effect=lambda folio, *a, **k: {"_id": REGISTROS_FALLA[folio]}
    )
    borrar = mocker.patch.object(accesos_no_api.lkf_api, "patch_record_list")
    mocker.patch.object(accesos_no_api, "check_status_code", return_value=dict(BORRADO_OK))

    res = accesos_no_api.delete_failure(list(FOLIOS_FALLA))

    assert res == BORRADO_OK
    borrar.assert_called_once()
    esperados = [URL_REGISTRO.format(REGISTROS_FALLA[folio]) for folio in FOLIOS_FALLA]
    assert borrar.call_args.args[0] == {"deleted_objects": esperados}, f"Mandó a borrar {borrar.call_args.args[0]}"
