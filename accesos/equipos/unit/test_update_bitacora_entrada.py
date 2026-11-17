# coding: utf-8

"""
Agregar un equipo a una entrada ya registrada (update_bitacora_entrada:
add-local-equipo) sin tocar preprod: se simula el guardado y se revisa qué
se manda a guardar en el registro de la bitácora.
Notion: TB-317.
"""

import pytest

from ..data.equipos_data import (
    EQUIPO_TIPO_CATALOGO,
    REGISTRO_BITACORA,
)


def equipo_agregado(acceso_obj, mocker, equipo):
    """Agrega el equipo con el guardado simulado y regresa el renglón que se mandó."""
    guardar = mocker.patch.object(acceso_obj.lkf_api, "patch_multi_record", return_value={"status_code": 202})
    acceso_obj.update_bitacora_entrada({"equipo": dict(equipo)}, record_id=REGISTRO_BITACORA)
    guardar.assert_called_once()
    return guardar.call_args.kwargs["answers"][acceso_obj.mf["grupo_equipos"]][-1]


@pytest.mark.bug(1512)
def test_agregar_equipo_con_tipo_del_catalogo_lo_guarda_con_tipo_valido(accesos_no_api, mocker):
    """
    TB-317: el modal de agregar equipo manda el tipo tal como viene del
    catálogo de la cuenta ('Laptop'); update_bitacora_entrada debe guardarlo
    con la opción del radio de la bitácora ('computo'), igual que al registrar
    la entrada. Ticket 2610-1512: lo guarda en minúsculas sin convertir
    ('laptop'), que no es opción de la bitácora.
    """
    acc = accesos_no_api

    equipo = equipo_agregado(acc, mocker, EQUIPO_TIPO_CATALOGO)

    tipo = equipo[acc.mf["tipo_equipo"]]
    assert tipo == "computo", f"Con tipo '{EQUIPO_TIPO_CATALOGO['tipo']}' el equipo quedó como {tipo!r}"
