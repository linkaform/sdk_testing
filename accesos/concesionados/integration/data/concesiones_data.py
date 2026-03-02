# coding: utf-8
from datetime import datetime
from pytz import timezone
from bson import ObjectId


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


CONCESION_BASE = {
            "option":"new_article",
            "script_name":"articulos_consecionados.py",
            "data_artilce": {
                "ubicacion_concesion":"Planta Monterrey",
                "area_concesion":"Almacén de inventario",
                "caseta_concesion":"Almacén de inventario",#legacy
                "status_concesion":"abierto",
                "persona_nombre_concesion": f"Carlos Santiago {current_time}",
                "persona_email_concesion":"email@emplado.com", # str or list ["email..."]
                "persona_id_concesion":126, #int or list [126]
                "persona_identificacion_otro":[
                    {"file_name":"identificacion.jpg",
                    "file_url":"https://b2.linkaform.com/file/app-linkaform/public-client-126/68600/6076166dfd84fa7ea446b917/2026-02-12T15:14:15_2.png"
                }],
                "fecha_concesion":today,
                "equipos":[
{
                    "categoria_equipo_concesion":"Artiuclos de Oficina",
                    "nombre_equipo":"Linterna",
                    "costo_equipo_concesion":300.00, # int or list [300,]
                    "imagen_equipo_concesion":[{
                        "file_name":"Libreta.jpg",
                        "file_url":"https://f001.backblazeb2.com/file/app-linkaform/public-client-126/68600/6076166dfd84fa7ea446b917/2026-02-24T23:08:05.png", 
                    }],
                    "cantidad_equipo_concesion":12,
                    "evidencia_entrega":[{
                    "file_name":"Articulo.jpg",
                    "file_url":"https://b2.linkaform.com/file/app-linkaform/public-client-126/68600/6076166dfd84fa7ea446b917/2026-02-24T23:08:05.png"
                    }],
                    "comentario_entrega":"Comentario de la Entrega",
                },
                    {
                    "categoria_equipo_concesion":"Artiuclos de Oficina",
                    "nombre_equipo":"Radio",
                    "costo_equipo_concesion":5000.00, # int or list [300,]
                    "imagen_equipo_concesion":[{
                        "file_name":"drangosito.jpg",
                        "file_url":"https://f001.backblazeb2.com/file/app-linkaform/public-client-126/68600/6076166dfd84fa7ea446b917/2026-02-24T23:08:24_3.png", 
                    }],
                    "cantidad_equipo_concesion":15,
                    "evidencia_entrega":[{
                    "file_name":"Articulo.jpg",
                    "file_url":"https://f001.backblazeb2.com/file/app-linkaform/public-client-126/68600/6076166dfd84fa7ea446b917/2026-02-24T23:08:24_3.png"
                    }],
                    "comentario_entrega":"Comentario de la Entrega",
                },
                {
                    "categoria_equipo_concesion":"Artiuclos de Oficina",
                    "nombre_equipo":"Llaves",
                    "costo_equipo_concesion":300.00, # int or list [300,]
                    "imagen_equipo_concesion":[{
                        "file_name":"llaves.jpg",
                        "file_url":"https://b2.linkaform.com/file/app-linkaform/public-client-126/68600/6076166dfd84fa7ea446b917/2026-02-24T23:08:14_2.png", 
                    }],
                    "cantidad_equipo_concesion":3,
                    "evidencia_entrega":[{
                    "file_name":"Articulo.jpg",
                    "file_url":"https://b2.linkaform.com/file/app-linkaform/public-client-126/68600/6076166dfd84fa7ea446b917/2026-02-24T23:08:14_2.png"
                    }],
                    "comentario_entrega":"Comentario de la Entrega",
                },
                    {
                    "categoria_equipo_concesion":"Artiuclos de Oficina",
                    "nombre_equipo":"Equipos",
                    "costo_equipo_concesion":5000.00, # int or list [300,]
                    "imagen_equipo_concesion":[{
                        "file_name":"drangosito.jpg",
                        "file_url":"https://f001.backblazeb2.com/file/app-linkaform/public-client-126/68600/6076166dfd84fa7ea446b917/2026-02-24T23:08:10_1.png", 
                    }],
                    "cantidad_equipo_concesion":1,
                    "evidencia_entrega":[{
                    "file_name":"Articulo.jpg",
                    "file_url":"https://f001.backblazeb2.com/file/app-linkaform/public-client-126/68600/6076166dfd84fa7ea446b917/2026-02-24T23:08:10_1.png"
                    }],
                    "comentario_entrega":"Comentario de la Entrega",
                }
                ],
                "observacion_concesion":"observacion",
                "evidencia":[],
                "firma":
                    {"file_name":"Nombre de la Fimra.png", 
                    "file_url":"https://f001.backblazeb2.com/file/app-linkaform/public-client-126/561/573e09e523d3fd5a35bbd9ef/a3ca395cde2343ac9eef5f9239b48344.jpg"
                    },
                }
            }

CONCESION_BASE_OTRO = {
            "option":"new_article",
            "script_name":"articulos_consecionados.py",
            "data_artilce": {
                "ubicacion_concesion":"Planta Monterrey",
                "area_concesion":"Almacén de inventario",
                "caseta_concesion":"Almacén de inventario",#legacy
                "status_concesion":"abierto",
                "persona_nombre_otro":f"Jose Chavez Otro {current_time}",
                "persona_email_otro":"email@otro.com",
                "persona_identificacion_otro":[
                    {"file_name":"identificacion.jpg",
                    "file_url":"https://b2.linkaform.com/file/app-linkaform/public-client-126/68600/6076166dfd84fa7ea446b917/2026-02-12T15:18:36_2.png"
                }],
                "fecha_concesion":today,
                "equipos":[{
                    "id_movimiento": str(ObjectId()),
                    "categoria_equipo_concesion":"Artiuclos de Oficina",
                    "nombre_equipo":"Linterna",
                    "costo_equipo_concesion":300.00, # int or list [300,]
                    "imagen_equipo_concesion":[{
                        "file_name":"Libreta.jpg",
                        "file_url":"https://f001.backblazeb2.com/file/app-linkaform/public-client-126/68600/6076166dfd84fa7ea446b917/2026-02-24T23:08:05.png", 
                    }],
                    "cantidad_equipo_concesion":12,
                    "evidencia_entrega":[{
                    "file_name":"Articulo.jpg",
                    "file_url":"https://b2.linkaform.com/file/app-linkaform/public-client-126/68600/6076166dfd84fa7ea446b917/2026-02-24T23:08:05.png"
                    }],
                    "comentario_entrega":"Comentario de la Entrega",
                },
                    {
                    "id_movimiento": str(ObjectId()),
                    "categoria_equipo_concesion":"Artiuclos de Oficina",
                    "nombre_equipo":"Radio",
                    "costo_equipo_concesion":5000.00, # int or list [300,]
                    "imagen_equipo_concesion":[{
                        "file_name":"drangosito.jpg",
                        "file_url":"https://f001.backblazeb2.com/file/app-linkaform/public-client-126/68600/6076166dfd84fa7ea446b917/2026-02-24T23:08:24_3.png", 
                    }],
                    "cantidad_equipo_concesion":15,
                    "evidencia_entrega":[{
                    "file_name":"Articulo.jpg",
                    "file_url":"https://f001.backblazeb2.com/file/app-linkaform/public-client-126/68600/6076166dfd84fa7ea446b917/2026-02-24T23:08:24_3.png"
                    }],
                    "comentario_entrega":"Comentario de la Entrega",
                }
                ],
                "observacion_concesion":"observacion",
                "evidencia":[],
                "firma":
                    {"file_name":"Nombre de la Fimra.png", 
                    "file_url":"https://f001.backblazeb2.com/file/app-linkaform/public-client-126/561/573e09e523d3fd5a35bbd9ef/a3ca395cde2343ac9eef5f9239b48344.jpg"
                    },
                }
            }