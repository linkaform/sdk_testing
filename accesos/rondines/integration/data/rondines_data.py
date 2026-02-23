# coding: utf-8
from datetime import datetime
from pytz import timezone



def today_str(tz_name='America/Monterrey', date_format='date'):
    today = datetime.now()
    today = today.astimezone(timezone(tz_name))
    if date_format == 'datetime':
        str_today = datetime.strftime(today, '%Y-%m-%d %H:%M:%S')
    else:
        str_today = datetime.strftime(today, '%Y-%m-%d')
    return str_today

current_time = datetime.now().strftime("%H:%M")
today = today_str(date_format='datetime')



LOCATIONS = {'Planta Guadalajara': ['Caseta 1', 'Caseta 2', 'Caseta 2', 'Cortinas B3', 'Cuarto de maquinas', 'Cuarto limpios', 'Estacionamiento piso 1', 'Estacionamiento piso 2', 'Estacionamiento piso 3', 'Estacionamiento piso 4', 'Estacionamiento piso 5', 'Ingreso B3', 'Lobby B1', 'Lobby B3', 'Perímetro frontal', 'Perímetro lateral derecho', 'Perímetro lateral izquierdo', 'Perímetro trasero', 'Planta de emergencia', 'Planta de emergencia de luz', 'Reciclado', 'Scrap', 'Sub- estación eléctrica ', 'Sub-estación eléctrica', 'Taller de mantenimiento', 'Área de gas, nitrógeno e hidrógeno', 'Área de químicos y residuos peligrosos'], 'Planta Iidea': ['Almacén de producto terminado ', 'Archivo muerto ', 'Baños de comedor', 'Baños de producción ', 'Caseta principal ', 'Envasado de tequila ', 'Envasado jarabe ', 'Evaporador cuatro efectos ', 'Evaporador de efectos ', 'Evaporador de efectos (planta baja)', 'Evaporador de efectos (planta baja)', 'Evaporador de efectos (planta baja)', 'Evaporador de efectos (planta baja)', 'Evaporador de efectos (planta baja)', 'Evaporador de efectos (planta baja)', 'Evaporador de efectos (planta baja)', 'Evaporador de efectos (planta baja)', 'Exterior de graneles ', 'Grabado de botella ', 'Interior Alambiques ', 'Molienda jarabe ', 'Molienda tequila ', 'Predio 3', 'Predio dos', 'Predio uno', 'Prensa de filtración ', 'Prueba nueva area', 'Pruebas', 'Racks de producto terminado ', 'Tanque 5600', 'Tanques de 100 (parte alta)', 'Tanques de 100ml (parte alta)', 'Tanques de 100ml planta alta', 'Tanques de 13000 (parte alta)', 'Tanques de 13000 (parte alta)', 'Tanques de 13000 (parte alta)', 'Tanques de jugo procesos ', 'Torre de destilación ', 'Área de bomba y estacionamiento ', 'Área de calderas ', 'Área de lockers', 'Área de oficinas administrativas ']}


CREATE_RONDIN = {
  "rondin_data": {
    "nombre_rondin": "Rondin General Iidea",
    "duracion_estimada": "45 minutos",
    "ubicacion": "Planta Iidea",
    "areas": [
      "Área de gas, nitrógeno e hidrógeno",
      "Área de químicos y residuos peligrosos",
      "Caseta 1",
      "Caseta 2",
      "Cortinas B3",
      "Cuarto de maquinas",
      "Cuarto limpios",
      "Estacionamiento piso 1",
      "Estacionamiento piso 2",
      "Estacionamiento piso 3",
      "Estacionamiento piso 4",
      "Estacionamiento piso 5",
      "Ingreso B3",
      "Lobby B1",
      "Lobby B3",
      "Perímetro frontal",
      "Perímetro lateral derecho",
      "Perímetro lateral izquierdo",
      "Perímetro trasero",
      "Planta de emergencia",
      "Planta de emergencia de luz",
      "Reciclado",
      "Scrap",
      "Sub-estación eléctrica",
      "Sub- estación eléctrica ",
      "Taller de mantenimiento"
    ],
    "grupo_asignado": "",
    "fecha_hora_programada": "2026-02-19 00:00:00",
    "programar_anticipacion": "no",
    "cuanto_tiempo_de_anticipacion": 0,
    "cuanto_tiempo_de_anticipacion_expresado_en": "",
    "tiempo_para_ejecutar_tarea": 30,
    "tiempo_para_ejecutar_tarea_expresado_en": "minutos",
    "la_tarea_es_de": "cuenta_con_una_recurrencia",
    "la_recurrencia_cuenta_con_fecha_final": "no",
    "fecha_final_recurrencia": "",
    "accion_recurrencia": "programar",
    "se_repite_cada": "diario",
    "cron_conf": "",
    "que_dias_de_la_semana": [
      "domingo",
      "martes",
      "miercoles",
      "jueves",
      "viernes",
      "sabado",
      "lunes"
    ],
    "en_que_semana_sucede": "todas_las_semanas",
    "sucede_recurrencia": [
      "dia_de_la_semana"
    ],
    "cada_cuantas_horas_se_repite": "3"
  },
  "option": "create_rondin",
  "script_name": "rondines.py"
}