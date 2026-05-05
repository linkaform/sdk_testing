# coding: utf-8
# rondines_data.py
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



LOCATIONS = {"ubicacion":"Planta Guadalajara","option":"get_catalog_areas","script_name":"rondines.py"}

RONDIN_ID = str(ObjectId())

RONDIN_EJEMPLO = {
  "_id": RONDIN_ID,
  "type": "rondin",
  "inbox": True,
  "status": "synced",
  "folio": "66525790-10",
  "status_user": "new",
  "created_at": 1777784196,
  "updated_at": today,
  "created_by_id": 10,
  "created_by_name": "Emiliano Zapata",
  "geolocation": {
    "lat": -100.3862645,
    "long": 25.644885499999997
  },
  "record": {
    "user_name": "Emiliano Zapata",
    "nombre_rondin": "NFC Rondin Oficina JP",
    "ubicacion_rondin": "Planta Monterrey",
    "tipo_rondin": "nfc",
    "duracion_estimada": "5 minutos",
    "fecha_programada": today,
    "fecha_inicio": "",
    "fecha_finalizacion": "",
    "fecha_pausa": "",
    "fecha_reanudacion": "",
    "ultimo_check_area_id": "",
    "check_areas": [
      {
        "tag_id": "EQUIPMENT:53:4C:37:47:41:00:01",
        "ubicacion": "Planta Monterrey",
        "area": "Escritorio",
        "tipo_de_area": "Área Pública",
        "foto_del_area": [
          {
            "file_name": "3a9d8a6e-c89f-42db-9117-ddc820bced1e.jpeg",
            "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-10/137161/681144fb0d423e25b42818d2/69dbe57bc4551dd6be896705.jpeg",
            "file_path": "file:///data/user/0/com.linkaform.soter/cache/ImagePicker/a03c8396-e64d-4c45-b3af-ad62d276d9c5.jpeg"
          }
        ],
        "inspeccion": [],
        "checked": False,
        "checked_at": "",
        "check_area_id": ""
      },
      {
        "tag_id": "clave10.com/eq/53:0F:37:47:41:00:01",
        "ubicacion": "Planta Monterrey",
        "area": "Stand",
        "tipo_de_area": "Área Pública",
        "foto_del_area": [
          {
            "file_name": "db2f0d02-1790-4f68-b651-d71a123f4cf6.jpeg",
            "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-10/137161/681144fb0d423e25b42818d2/69dbe57cd1efabad6d1ba54f.jpeg",
            "file_path": "file:///data/user/0/com.linkaform.soter/cache/ImagePicker/e3d21a2c-1f23-4c6a-bb90-2b2835a3f28b.jpeg"
          }
        ],
        "inspeccion": [],
        "checked": False,
        "checked_at": "",
        "check_area_id": ""
      },
      {
        "tag_id": "clave10.com/eq/53:0D:37:47:41:00:01",
        "ubicacion": "Planta Monterrey",
        "area": "Bocina",
        "tipo_de_area": "Área Pública",
        "foto_del_area": 
[          {
            "file_name": "d1266d54-7176-49d1-b629-58a63795696f.jpeg",
            "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-10/137161/681144fb0d423e25b42818d2/69dbe57cb867aaa33d896702.jpeg",
            "file_path": "file:///data/user/0/com.linkaform.soter/cache/ImagePicker/aabd8094-371a-4c60-94b3-895d48937ba4.jpeg"
          }
        ],
        "inspeccion": [],
        "checked": False,
        "checked_at": "",
        "check_area_id": ""
      },
      {
        "tag_id": "clave10.com/eq/53:0E:37:47:41:00:01",
        "ubicacion": "Planta Monterrey",
        "area": "Tableta",
        "tipo_de_area": "Área Pública",
        "foto_del_area": [
          {
            "file_name": "e17a8782-26bb-435b-9911-88a59f192f2b.jpeg",
            "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-10/137161/681144fb0d423e25b42818d2/69dbe57c1d4fe22c56896705.jpeg",
            "file_path": "file:///data/user/0/com.linkaform.soter/cache/ImagePicker/deb83c19-caad-46b1-8db4-c99464c3afc2.jpeg"
          }
        ],
        "inspeccion": [],
        "checked": False,
        "checked_at": "",
        "check_area_id": ""
      }
    ]
  }
}


CHECK_BASIC = {
  "type": "check_area",
  "status_check": "completed",
  "status_user": "completed",
  "created_at": 1777784969,
  "updated_at": 1777784985,
  "timezone": "America/Mexico_City",
  "created_by_id": 10,
  "created_by_name": "Emiliano Zapata",
  "geolocation": {
    "lat": 25.6460591,
    "long": -100.3909594
  },
  "record": {
    "tag_id": "EQUIPMENT:53:4C:37:47:41:00:01",
    "ubicacion": "Planta Monterrey",
    "area": "Escritorio",
    "tipo_de_area": "Área Pública",
    "foto_del_area": [
      {
        "file_name": "3a9d8a6e-c89f-42db-9117-ddc820bced1e.jpeg",
        "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-10/137161/681144fb0d423e25b42818d2/69dbe57bc4551dd6be896705.jpeg",
        "file_path": "file:///data/user/0/com.linkaform.soter/cache/ImagePicker/a03c8396-e64d-4c45-b3af-ad62d276d9c5.jpeg"
      }
    ],
    "inspeccion": [],
    "checked": True,
    "checked_at": "2026-05-02 23:09:29",
    "check_area_id": "",
    "evidencia_incidencia": [
      {
        "file_name": "2d7ce775-0fb1-45ab-bc1e-5d1b63d40509.jpeg",
        "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/116852/660459dde2b2d414bce9cf8f/69f6d897b666be80236d0a7a.jpeg"
      }
    ],
    "documento_incidencia": [],
    "incidencias": [],
    "comentario_check_area": "Primer scann",
    "inspeccion_respuestas": []
  },
  "status": "synced"
}
