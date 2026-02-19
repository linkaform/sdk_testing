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

LOCATION_AREAS =  {'Planta Guadalajara': ['Caseta 1', 'Caseta 2', 'Caseta 2', 'Cortinas B3', 'Cuarto de maquinas', 'Cuarto limpios', 'Estacionamiento piso 1', 'Estacionamiento piso 2', 'Estacionamiento piso 3', 'Estacionamiento piso 4', 'Estacionamiento piso 5', 'Ingreso B3', 'Lobby B1', 'Lobby B3', 'Perímetro frontal', 'Perímetro lateral derecho', 'Perímetro lateral izquierdo', 'Perímetro trasero', 'Planta de emergencia', 'Planta de emergencia de luz', 'Reciclado', 'Scrap', 'Sub- estación eléctrica ', 'Sub-estación eléctrica', 'Taller de mantenimiento', 'Área de gas, nitrógeno e hidrógeno', 'Área de químicos y residuos peligrosos'], 'Planta Iidea': ['Almacén de producto terminado ', 'Archivo muerto ', 'Baños de comedor', 'Baños de producción ', 'Caseta principal ', 'Envasado de tequila ', 'Envasado jarabe ', 'Evaporador cuatro efectos ', 'Evaporador de efectos ', 'Evaporador de efectos (planta baja)', 'Evaporador de efectos (planta baja)', 'Evaporador de efectos (planta baja)', 'Evaporador de efectos (planta baja)', 'Evaporador de efectos (planta baja)', 'Evaporador de efectos (planta baja)', 'Evaporador de efectos (planta baja)', 'Evaporador de efectos (planta baja)', 'Exterior de graneles ', 'Grabado de botella ', 'Interior Alambiques ', 'Molienda jarabe ', 'Molienda tequila ', 'Predio 3', 'Predio dos', 'Predio uno', 'Prensa de filtración ', 'Prueba nueva area', 'Pruebas', 'Racks de producto terminado ', 'Tanque 5600', 'Tanques de 100 (parte alta)', 'Tanques de 100ml (parte alta)', 'Tanques de 100ml planta alta', 'Tanques de 13000 (parte alta)', 'Tanques de 13000 (parte alta)', 'Tanques de 13000 (parte alta)', 'Tanques de jugo procesos ', 'Torre de destilación ', 'Área de bomba y estacionamiento ', 'Área de calderas ', 'Área de lockers', 'Área de oficinas administrativas ']}


ubicacion = list(LOCATION_AREAS.keys())[0]

account_id = 29572

PASE = {
    "selected_visita_a": "",
    "nombre": "Pruebas Juan",
    "empresa": "Empresa de Pruebas",
    "email": "email@pruebas.com",
    "telefono": "+521234567890",
    "ubicacion": "Planta Monterrey",
    "ubicaciones": [
      ubicacion,
    ],
    "tema_cita": "Pruebas Automaticas",
    "descripcion": "Comenatrio de Pruebas",
    "perfil_pase": "Visita General",
    "status_pase": "Proceso",
    "visita_a": ["Emiliano Zapata",],
    "custom": True,
    "link": {
      "link": "https://web.clave10.com/dashboard/pase-update",
      "docs": [
        "agregarFoto",
        "agregarIdentificacion"
      ],
      "creado_por_id": 10,
      "creado_por_email": "seguridad@linkaform.com"
    },
    "enviar_correo_pre_registro": [
      "enviar_correo_pre_registro",
      "enviar_sms_pre_registro"
    ],
    "tipo_visita_pase": "rango_de_fechas",
    "fechaFija": "",
    "fecha_desde_visita": "2026-02-06 00:00:00",
    "fecha_desde_hasta": "2026-02-06 00:00:00",
    "config_dia_de_acceso": "cualquier_día",
    "config_dias_acceso": [],
    "config_limitar_acceso": 3,
    "areas": [],
    "comentarios": [],
    "enviar_pre_sms": {
      "from": "enviar_pre_sms",
      "mensaje": "SOY UN MENSAJE",
      "numero": "+521234567890"
    },
    "todas_las_areas": False,
    "created_from": "web"
  }

PASE_FECHA_FIJA = {"access_pass": 
    {"created_from":"web",
    "nombre":f"Pruebas Fecha Fija {current_time}",
    "empresa":"Clave10",
    "email":"pruebas@clave10.com",
    "telefono":"+52811500000",
    "ubicaciones":[ubicacion],
    "tema_cita":"Pruebas",
    "descripcion":"Descripcion Pruebas",
    "perfil_pase":"Visita General",
    "status_pase":"Proceso",
    "visita_a":["Usuario Actual"],
    "link":{"link":"https://web.clave10.com/dashboard/pase-update",
    "docs":["agregarIdentificacion","agregarFoto"],
    "creado_por_id":29909,
    "creado_por_email":"jme@tiendas3b.com"},
    "enviar_correo_pre_registro":["enviar_sms_pre_registro","enviar_correo_pre_registro"],
    "tipo_visita_pase":"fecha_fija",
    "fecha_desde_visita":today,
    "fecha_desde_hasta":"",
    "config_dia_de_acceso":"cualquier_día",
    "config_dias_acceso":[],
    "config_limitar_acceso":1,
    "areas":[],
    "comentarios":[],
    "enviar_pre_sms":{"from":"enviar_pre_sms","mensaje":"SOY UN MENSAJE","numero":"+528115778605"},
    "todas_las_areas":False},
    "enviar_pre_sms":{"from":"enviar_pre_sms","mensaje":"SOY UN MENSAJE","numero":"+528115778605"},
    "option":"create_access_pass",
    "script_name":"pase_de_acceso.py"}

PASE_APP = {
    "selected_visita_a": "",
    "nombre": "Pruebas Juan",
    "empresa": "Empresa de Pruebas",
    "email": "email@pruebas.com",
    "telefono": "+521234567890",
    "ubicacion": "Planta Monterrey",
    "ubicaciones": [
      ubicacion
    ],
    "tema_cita": "Pruebas Automaticas",
    "descripcion": "Comenatrio de Pruebas",
    "perfil_pase": "Visita General",
    "status_pase": "Proceso",
    "visita_a": ["Emiliano Zapata",],
    "custom": True,
    "link": {
      "link": "https://web.clave10.com/dashboard/pase-update",
      "docs": [
        "agregarFoto",
        "agregarIdentificacion"
      ],
      "creado_por_id": 10,
      "creado_por_email": "seguridad@linkaform.com"
    },
    "enviar_correo_pre_registro": [
      "enviar_correo_pre_registro",
      "enviar_sms_pre_registro"
    ],
    "tipo_visita_pase": "rango_de_fechas",
    "fechaFija": "",
    "fecha_desde_visita": "2026-02-11 00:00:00",
    "fecha_desde_hasta": "2026-02-21 00:00:00",
    "config_dia_de_acceso": "cualquier_día",
    "config_dias_acceso": [],
    "config_limitar_acceso": 3,
    "areas": [],
    "comentarios": [],
    "enviar_pre_sms": {
      "from": "enviar_pre_sms",
      "mensaje": "SOY UN MENSAJE",
      "numero": "+521234567890"
    },
    "todas_las_areas": False,
    "created_from": "app"
  }

PASE_AUTO_REGISTRO = {
        "email": "",
        "nombre": "Marta Garza",
        "empresa": "Pruebas Clave 10",
        "foto": [ {
                "file_name": "imageUser.png",
                "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/68600/6076166dfd84fa7ea446b917/2026-02-10T18:45:23_1.png"
            }],
        "identificacion": [
           
            {
                "file_name": "imageCard.png",
                "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/68600/6076166dfd84fa7ea446b917/2026-02-10T18:45:25_2.png"
            }
        ],
        "perfil_pase": "Walkin",
        "telefono": "",
        "email": "",
        "visita_a": {"nombre":"lkf", "email":'josepato@hotmail.com', 'telefono':"88605"},
    "account_id": "10",
    "ubicaciones": [ubicacion,],
    "option": "create_access_pass",
    "script_name": "pase_de_acceso_use_api.py",
    "created_from": "auto_registro"
    }


PASE_NUEVA_VISTA =   {
    "foto": {
      "file_name": "7e2cb0e6-e789-40e3-a356-aee9fbe0a32c.jpeg",
      "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/116852/660459dde2b2d414bce9cf8f/698cbd5a47fa1a68268199be.jpeg"
    },
    "identificacion": {
      "file_name": "8ec2fb61-7f6c-4fe6-8f06-d642d5b1ac5d.jpeg",
      "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/116852/660459dde2b2d414bce9cf8f/698cbd5ebad873a7387b9606.jpeg"
    },
    "empresa": "Pruebas Clave 10",
    "site": "accesos",
    "created_from": "nueva_visita",
    "status_pase": "activo",
    "perfil_pase": "Visita General",
    "nombre": "Nueva Vista",
    "visita_a": "Emiliano Zapata",
    "telefono": "",
    "email": ""
  }

UPDATE_PASS_APP = {
  "access_pass": {
    "account_id": 29909,
    "folio": "698f41bc5a5cf33dcae8bce8",
    "option": "update_pass",
    "script_name": "pase_de_acceso_use_api.py",
    "access_pass": {
      "acepto_aviso_privacidad": "sí",
      "conservar_datos_por": "3 meses",
      "walkin_fotografia": [
        {
          "file_name": "imageUser.png",
          "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/116852/660459dde2b2d414bce9cf8f/698f418a55839de9834650ea.png"
        }
      ],
      "grupo_equipos": [],
      "email": "josepato@hotmail.com",
      "status_pase": "activo",
      "ubicacion": [
        ubicacion
      ],
      "nombre": "Jose Pruebas",
      "visita_a": [
        "Martín de Jesús Romero Chávez",
        "Jessica Marsha Meza Vargas"
      ],
      "walkin_identificacion": [
        {
          "file_name": "imageCard.png",
          "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/116852/660459dde2b2d414bce9cf8f/698f418f496537548215bf96.png"
        }
      ],
      "telefono": "8115778605",
      "grupo_vehiculos": []
    }
  },
  "account_id": 29909,
  "docker_image": "linkaform/addons:latest",
  "script_name": "pase_de_acceso_use_api.py",
  "option": "update_pass",
  "folio": "698e3d64c2f5cda61092084e"
}

PASE_AUTO_REGISTRO_SIN_VISTA_A ={"script_name":"pase_de_acceso_use_api.py","option":"create_access_pass",
        "access_pass":{"ubicaciones":[ubicacion],
        "nombre":f"Prueba {current_time}",
        "perfil_pase":"Walkin",
        "telefono":"811-500-0000",
        "email":"pruebas@linkaform.com",
        "empresa":"Clave10",
        "visita_a":{"nombre":"No se","email":"","telefono":""},
        "foto":[{
            "file_name":"imageUser.png",
            "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/68600/6076166dfd84fa7ea446b917/2026-02-10T18:36:13_2.png"}],
        "identificacion":[{
            "file_name":"imageCard.png",
            "file_url":"https://f001.backblazeb2.com/file/app-linkaform/public-client-126/68600/6076166dfd84fa7ea446b917/2026-02-10T18:36:11_1.png"}],
        "equipos":[],
        "motivo":"Motivo 1",
        "created_from":"auto_registro"},
        "account_id":f"{account_id}"}

COMPLETAR_PASE_USAURIO_ACTUAL = {"script_name":"pase_de_acceso_use_api.py","option":"update_pass",
    "access_pass":{
        "visita_a":["Usuario Actual"]
    },
    "folio":"69935f45364424902060f464",
    "account_id":account_id}


# pase de entrada web
# {"access_pass":
# {"created_from":"web","selected_visita_a":"","nombre":"Purebas Pase d eEntrada","empresa":"Clave10",
# "email":"josepato@linkaform.com","telefono":"+528115778605","ubicacion":"Corporativo Tiendas 3B",
# "ubicaciones":["Corporativo Tiendas 3B"],"tema_cita":"Prueba","descripcion":"Demo","perfil_pase":"Visita General",
# "status_pase":"Proceso","visita_a":["Usuario Actual"],"custom":true,
# "link":{"link":"https://web.clave10.com/dashboard/pase-update","docs":["agregarFoto","agregarIdentificacion"],
# "creado_por_id":29909,"creado_por_email":"jme@tiendas3b.com"},
# "enviar_correo_pre_registro":["enviar_sms_pre_registro","enviar_correo_pre_registro"],
# "tipo_visita_pase":"rango_de_fechas","fechaFija":"","fecha_desde_visita":"2026-02-16 00:00:00",
# "fecha_desde_hasta":"2026-02-16 23:59:59","config_dia_de_acceso":"cualquier_día","config_dias_acceso":[],
# "config_limitar_acceso":1,"areas":[],"comentarios":[],
# "enviar_pre_sms":{"from":"enviar_pre_sms","mensaje":"SOY UN MENSAJE","numero":"+528115778605"},
# "todas_las_areas":false},
# "location":"Corporativo Tiendas 3B",
# "enviar_pre_sms":{"from":"enviar_pre_sms","mensaje":"SOY UN MENSAJE","numero":"+528115778605"},
# "option":"create_access_pass","script_name":"pase_de_acceso.py"}



# COMPLETAR_PASE_USAURIO_ACTUAL = {"script_name":"pase_de_acceso_use_api.py","option":"update_pass",
# "access_pass":{"grupo_vehiculos":[],"grupo_equipos":[],"status_pase":"activo","walkin_fotografia":[],
# "walkin_identificacion":[],"account_id":10,"nombre":"Jose Pruebas",
# "ubicacion":["Corporativo Tiendas 3B"],"email":"josepato@hotmail.com","telefono":"8115778605","visita_a":["Usuario Actual"]},
# "folio":"698f41bc5a5cf33dcae8bce8","account_id":10}

# COMPLETAR_PASE_USAURIO_ACTUAL = {"script_name":"pase_de_acceso_use_api.py","option":"update_pass",
# "access_pass":{"visita_a":["Usuario Actual"]},
# "folio":"698f41bc5a5cf33dcae8bce8","account_id":10}

# COMPLETAR_PASE = {"script_name":"pase_de_acceso_use_api.py","option":"update_pass",
# "access_pass":{"grupo_vehiculos":[],"grupo_equipos":[],"status_pase":"activo","walkin_fotografia":[],
# "walkin_identificacion":[],"account_id":10,"nombre":"Jose Pruebas",
# "ubicacion":["Corporativo Tiendas 3B"],"email":"josepato@hotmail.com","telefono":"8115778605",
# "visita_a":["Jessica Marsha Meza Vargas"]},"folio":"698f41bc5a5cf33dcae8bce8","account_id":10}