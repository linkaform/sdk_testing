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

COMPLETA_PASE_APP = {
   "script_name":"pase_de_acceso_use_api.py",
   "option":"update_pass",
   "access_pass":{
      "grupo_vehiculos":[
         
      ],
      "grupo_equipos":[
         {
            "color":"Gris",
            "marca":"HP",
            "modelo":"PavilonA1",
            "nombre":"",
            "serie":"ABCV123",
            "tipo":"Computo"
         }
      ],
      "status_pase":"Activo",
      "walkin_fotografia":[
         {
            "file_url":"https://f001.backblazeb2.com/file/app-linkaform/public-client-126/116852/660459dde2b2d414bce9cf8f/698cbd5a47fa1a68268199be.jpeg",
            "file_name":"fotografia.jpeg"
         }
      ],
      "walkin_identificacion":[
         {
            "file_url":"https://f001.backblazeb2.com/file/app-linkaform/public-client-126/116852/660459dde2b2d414bce9cf8f/698cbd5ebad873a7387b9606.jpeg",
            "file_name":"identificacion.jpeg"
         }
      ],
      "acepto_aviso_privacidad":"sí",
      "conservar_datos_por":"3 meses"
   },
   "folio":"699caa78adf811c70d483609",
   "account_id":29909
}

LOCATION_AREAS_LKF = {
    'Linkaform Ciudad de México':['Caseta Ciudad de México', 'Centro de Control', 'Cocina de Empleados', 'Lavandería', 'Recepción'],
    'Linkaform Yucatán':['Antenas', 'Caseta Yucatán', 'Piscina', 'Recepción', 'Restaurante', 'Salón de Eventos', 'Spa Unisex'],
    'Linkaform Tamaulipas':['Almacén de Materia Prima', 'Canchas de Voleibol', 'Caseta Tamaulipas', 'Comedor de empleados', 'Departamento RH', 'Estacionamiento', 'Estacionamiento de Estadio Marte R. Gomez', 'Lobby'],
    'Linkaform Puebla': ['Auditorio de Eventos', 'Caseta Puebla', 'Lobby', 'Recursos de Agua Potable'],
    'Linkaform Mty':['Almacén de Equipos', 'Avispones', 'Bar Pared Sur Ventana A', 'Bar Parted Sur ventana B', 'Baño Hombres', 'Baño Mujeres', 'Baño Officina', 'Bodega Herramienta ', 'Bodega Herramientas Codigo B', 'Boiler Maria', 'Bolier Principal', 'Buzon', 'Caja Himel Boiler', 'Carpinteria', 'Casa del Arbol', 'Caseta Monterrey', 'Centeo de Carga Bomba', 'Centro de Carga A', 'Centro de Carga Puerta B', 'Clima Central', 'Clima Cuarto de Servicio', 'Control de Riego', 'Cuarto Herramientas Puera', 'Dado Cara 5', 'Dado Lado 1', 'Dado Lado 2', 'Demo Calentador', 'Demo Lamina', 'Entrada Principal', 'Estacionamiento', 'Estación Meteorológica', 'Huerto Aguacate', 'Lado 4 de dado', 'Medidor de Agua', 'Medidor de Luz', 'Oficina JP', 'Oficina Principal', 'Porton de Entrada Principal puerta A', 'Porton de Entrada Puerta B', 'Pruebas Madera', 'Recepción', 'Restaurante', 'Sala de Conferencias', 'Señalamiento', 'Sink - Boiler Puerta A', 'Sink - Boiler Puerta B', 'Subestacion', 'Tinaco Tortugas'],
    'Linkaform Jalisco':['Caseta Jalisco', 'Recepción', 'Restaurante'],
    'Linkaform Oaxaca': ['Bar Luces', 'Baño de Mujeres', 'Biblioteca', 'Caseta Oaxaca', 'Lobby']
}

LOCATION_AREAS = {
    'Edificio CDMX':['Caseta seguridad principal', 'Comedor empleados 2', 'Estacionamiento A', 'Estacionamiento A'],
    'Planta Guadalajara': [],
    'Planta Monterrey': ['Almacén de inventario', 'Antenas', 'Caseta 1 - Mty', 'Caseta 2 - Mty', 'Caseta 6 Poniente', 'Caseta Principal', 'Cuarto MC', 'Recursos de agua potable', 'Recursos eléctricos', 'Sala de Juntas Planta Baja'],
    'Litoprocess': ['Sala de Juntas'],
    'Planta Durango':  ['Caseta 2 - Dro', 'Caseta Principal -Dro', 'Cuarto de servidoress'],
}

LOCATION_AREAS = {
    'Corporativo Tiendas 3B':['Entrada caseta principal', 'Estacionamiento', 'Lobby', 'Oficinas Administrativas', 'Recepción', 'Sala de juntas planta baja'], 'Visita_a': ['Administración Tiendas 3B', 'Andrea Bustos Carranza', 'Enrique Iván Delgado Ayala', 'Giselle Jocelyn Mayorga Ruiz', 'Janeth Itzel Carbajal Estrella', 'Jessica Marsha Meza Vargas', 'Martín de Jesús Romero Chávez', 'Rolando Muñiz Campos', 'Zurisadai Camacho Contreras'],
}

PASE = {
    "selected_visita_a": "",
    "nombre": "Pruebas Juan",
    "empresa": "Empresa de Pruebas",
    "email": "email@pruebas.com",
    "telefono": "+521234567890",
    "ubicacion": "Planta Monterrey",
    "ubicaciones": [
      "Planta Monterrey",
      "Planta Durango"
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

PASE_FECHA_FIJA_OLD = {
    "selected_visita_a": "",
    "nombre": "Pruebas Fecha Fija",
    "empresa": "Empresa de Pruebas",
    "email": "pruebas@clave10.com",
    "telefono": "+521234567890",
    "ubicacion": "Planta Monterrey",
    "ubicaciones": [
      "Planta Monterrey",
      "Planta Durango"
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
    "tipo_visita_pase": "fecha_fija",
    "fechaFija": "",
    "fecha_desde_visita": "2026-02-06 00:00:00",
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
    # "selected_visita_a":"",
    "nombre":f"Pruebas Fecha Fija {current_time}",
    "empresa":"Clave10",
    "email":"pruebas@clave10.com",
    "telefono":"+52811500000",
    # "ubicacion":"Corporativo Tiendas 3B",
    "ubicaciones":["Corporativo Tiendas 3B"],
    "tema_cita":"Pruebas",
    "descripcion":"Descripcion Pruebas",
    "perfil_pase":"Visita General",
    "status_pase":"Proceso",
    "visita_a":["Usuario Actual"],
    # "custom":True,
    "link":{"link":"https://web.clave10.com/dashboard/pase-update",
    "docs":["agregarIdentificacion","agregarFoto"],
    "creado_por_id":29909,
    "creado_por_email":"jme@tiendas3b.com"},
    "enviar_correo_pre_registro":["enviar_sms_pre_registro","enviar_correo_pre_registro"],
    "tipo_visita_pase":"fecha_fija",
    # "fechaFija":"2026-02-17 20:00:00",
    "fecha_desde_visita":today,
    "fecha_desde_hasta":"",
    "config_dia_de_acceso":"cualquier_día",
    "config_dias_acceso":[],
    "config_limitar_acceso":1,
    "areas":[],
    "comentarios":[],
    "enviar_pre_sms":{"from":"enviar_pre_sms","mensaje":"SOY UN MENSAJE","numero":"+528115778605"},
    "todas_las_areas":False},
    # "location":"Corporativo Tiendas 3B",
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
      "Planta Monterrey",
      "Planta Durango"
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

PASE_APP_SALA = {
    "script_name": "pase_de_acceso.py",
    "option": "create_access_pass",
    "access_pass": {
      "empresa": "Clave 10",
      "config_dia_de_acceso": "cualquier_día",
      "created_from": "app",
      "descripcion": "",
      "config_dias_acceso": [],
      "ubicaciones": [
        "Corporativo Tiendas 3B"
      ],
      "tipo_visita_pase": "fecha_fija",
      "comentarioArea": "",
      "custom": True,
      "fecha_desde_hasta": "",
      "status_pase": "Proceso",
      "nombre": "Pruebas Invitado",
      "telefono": "+528115778605",
      "email": "josepato@clave10.com",
      "enviar_correo_pre_registro": [
        "enviar_correo_pre_registro",
        "enviar_sms_pre_registro"
      ],
      "fecha_desde_visita": "2026-02-23 13:00:00",
      "link": {
        "docs": [
          "agregarIdentificacion",
          "agregarFoto"
        ],
        "creado_por_email": "jme@tiendas3b.com",
        "link": "https://web.clave10.com/dashboard/pase-update",
        "creado_por_id": 29909
      },
      "perfil_pase": "Proveedores",
      "config_limitar_acceso": 1,
      "visita_a": [
        "Tiendas 3B",
        "Administración Tiendas 3B"
      ],
      "areas": [
        {
          "nombre_area": "Administración y Finanzas",
          "commentario_area": ""
        },
        {
          "nombre_area": "Caseta Principal",
          "commentario_area": ""
        },
        {
          "nombre_area": "Compras",
          "commentario_area": ""
        }
      ],
      "tema_cita": "Motivo",
      "todas_las_areas": False,
      "sala": "Sala Canela P4 (2p)",
      "comentarios": [
        {
          "tipo_comentario": "Pase",
          "comentario_pase": "Descripcion\n"
        }
      ]
    },
    "enviar_pre_sms": {
      "mensaje": "",
      "from": "enviar_pre_sms",
      "numero": "+528115778605"
    },
    "location": ""
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
    "ubicaciones": ["Planta Monterrey",],
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

PASE_AUTO_REGISTRO_SIN_VISTA_A ={"script_name":"pase_de_acceso_use_api.py","option":"create_access_pass",
        "access_pass":{"ubicaciones":["Corporativo Tiendas 3B"],
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
        "account_id":"29909"}

COMPLETAR_PASE_USAURIO_ACTUAL = {"script_name":"pase_de_acceso_use_api.py","option":"update_pass",
    "access_pass":{
        "visita_a":["Usuario Actual"]
    },
    "folio":"69935f45364424902060f464",
    "account_id":29909}


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