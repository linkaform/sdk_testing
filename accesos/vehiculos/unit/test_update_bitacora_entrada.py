# coding: utf-8

"""
Agregar un vehículo a una entrada ya registrada (update_bitacora_entrada:
add-local-vehicule) sin tocar preprod: se simula el guardado y se revisa qué
se manda a guardar en el registro de la bitácora.
Notion: TB-310.
"""

import pytest

from ..data.vehiculos_data import (
    VEHICULO_AGREGADO_CON_FOTO,
    REGISTRO_BITACORA,
)


@pytest.mark.bug(1578)
def test_agregar_vehiculo_a_una_entrada_guarda_su_foto(accesos_no_api, mocker):
    """
    TB-310: el modal Nuevo Vehículo manda la foto del vehículo
    (foto_vehiculo); update_bitacora_entrada debe guardarla en el renglón
    nuevo, igual que al registrar la entrada. Si no, el vehículo agregado
    queda sin foto aunque el guardia la haya tomado. Ticket 2610-1578: el
    renglón se arma sin la foto.
    """
    acc = accesos_no_api
    mf = acc.mf
    guardar = mocker.patch.object(acc.lkf_api, "patch_multi_record", return_value={"status_code": 202})

    acc.update_bitacora_entrada({"vehiculo": dict(VEHICULO_AGREGADO_CON_FOTO)}, record_id=REGISTRO_BITACORA)

    guardar.assert_called_once()
    vehiculo = guardar.call_args.kwargs["answers"][mf["grupo_vehiculos"]][-1]
    foto = vehiculo.get(mf["foto_vehiculo"])
    assert foto == VEHICULO_AGREGADO_CON_FOTO["foto_vehiculo"], f"La foto del vehículo quedó {foto!r}"
