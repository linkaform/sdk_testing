# coding: utf-8

from ..data.logs_data import (
    SCRIPTS_VISIBLES,
    USUARIOS_CUENTA,
)


def script_logs_simulados(logs, mocker, registros=()):
    """Simula los nombres que resuelve _name_maps y la colección script_log;
    regresa el mock de la colección para revisar la consulta."""
    mocker.patch.object(logs, "_name_maps", return_value={"users": dict(USUARIOS_CUENTA), "scripts": dict(SCRIPTS_VISIBLES)})
    coleccion = mocker.MagicMock()
    coleccion.find.return_value.sort.return_value.skip.return_value.limit.return_value = list(registros)
    mocker.patch.object(type(logs), "script_log_cr", new_callable=mocker.PropertyMock, return_value=coleccion)
    return coleccion
