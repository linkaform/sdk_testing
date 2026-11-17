# coding: utf-8

"""
Catálogo de vehículos por tipo y marca (vehiculo_marca y vehiculo_modelo, que
llaman los scripts get_vehiculos.py, pase_de_acceso.py y script_turnos.py con
la opción catalago_vehiculo) sin tocar la cuenta: se simula el catálogo y se
revisa qué se le pide.
Notion: TB-314 y TB-315.
"""

from ..data.vehiculos_data import VEHICULO_VISITA


def test_marcas_de_un_tipo_de_vehiculo_se_piden_al_catalogo_por_ese_tipo(accesos_no_api, mocker):
    """
    TB-314: vehiculo_marca debe pedir al catálogo de vehículos solo las
    marcas del tipo elegido (startkey con el tipo, group_level 2). Si truena o
    pide otra cosa, el selector de marca sale vacío o con marcas de otros
    tipos.
    """
    acc = accesos_no_api
    consultar = mocker.patch.object(acc.lkf_api, "catalog_view", return_value=[])

    acc.vehiculo_marca(VEHICULO_VISITA["tipo"])

    consultar.assert_called_once()
    opciones = consultar.call_args.args[2]
    assert opciones["startkey"] == [VEHICULO_VISITA["tipo"]]
    assert opciones["group_level"] == 2
