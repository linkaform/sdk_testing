# coding: utf-8

"""
Cerrar y editar una nota (update_notes) sin tocar preprod: se simulan el
empleado, la fecha y el guardado, y se revisa lo que update_notes manda a
guardar.
Notion: TB-163 a TB-167.
"""

import pytest
from lkf_back import de

from ..data.notas_data import (
    EMPLEADO_NOTA,
    FECHA_SERVIDOR,
    FOLIO_NOTA,
    CERRAR_NOTA,
    ESTATUS_CERRADO,
    NOTA_EDITADA,
)


@pytest.mark.bug(1515)
def test_cerrar_nota_guarda_quien_la_cerro_donde_la_lista_lo_lee(accesos_no_api, mocker):
    """
    TB-164: al cerrar, el nombre del empleado que la cierra debe quedar en el
    catálogo del que get_list_notes lee note_guard_close. Si se guarda en otro
    lado, la lista de Cerradas no dice quién cerró la nota (ticket 2610-1515).
    """
    mocker.patch.object(de(accesos_no_api, "get_employee_data"), "get_employee_data", return_value=dict(EMPLEADO_NOTA))
    mocker.patch.object(accesos_no_api, "today_str", return_value=FECHA_SERVIDOR)
    guardar = mocker.patch.object(accesos_no_api.lkf_api, "patch_multi_record", return_value={"status_code": 202})

    accesos_no_api.update_notes(dict(CERRAR_NOTA), FOLIO_NOTA)

    nf = accesos_no_api.notes_fields
    answers = guardar.call_args.kwargs["answers"]
    cerro = answers.get(nf["note_catalog_guard_close"], {}).get(nf["note_guard_close"])
    assert cerro == EMPLEADO_NOTA["worker_name"], (
        f"Quién cerró quedó {cerro!r} en el catálogo que lee la lista; se guardó en {sorted(answers)}"
    )


@pytest.mark.bug(1516)
def test_editar_nota_agrega_el_comentario_como_texto(accesos_no_api, mocker):
    """
    TB-165: edit-note-modal manda el comentario nuevo como lista de un texto.
    El renglón que se agrega al grupo de comentarios debe guardar el texto,
    no la lista; si guarda la lista, el comentario se ve como ['...'] o no se
    muestra (ticket 2610-1516).
    """
    guardar = mocker.patch.object(accesos_no_api.lkf_api, "patch_multi_record", return_value={"status_code": 202})

    accesos_no_api.update_notes(dict(NOTA_EDITADA), FOLIO_NOTA)

    nf = accesos_no_api.notes_fields
    grupo = guardar.call_args.kwargs["answers"][nf["note_comments_group"]]
    renglon = list(grupo.values())[0]
    assert renglon[nf["note_comments"]] == NOTA_EDITADA["note_comments"][0], (
        f"El comentario nuevo quedó {renglon[nf['note_comments']]!r}"
    )
