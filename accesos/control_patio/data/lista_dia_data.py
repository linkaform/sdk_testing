# coding: utf-8

"""
Datos de la lista del día de Control de patio que pide la app
(ControlPatioCard.tsx → fetchBitacoraTransportistaRecords). TB-094.
"""

# Petición de la app: solo la fecha del día ("AAAA-MM-DD"), sin date_from ni
# date_to. La fecha se llena en el test con el día del usuario.
PETICION_LISTA_DIA_APP = {
    "script_name": "transportistas.py",
    "option": "get_bitac_transportista_records",
}
