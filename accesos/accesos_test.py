# Notas importantes:
# Arrancar pruebas unitarias
# ./lkf start test
# hay que checar que esten en modulos y test en ramas iguales
# en test debes de tener una rama por cliente

# -*- coding: utf-8 -*-
import sys, simplejson, copy, random, string, math, json, time, pytz, pytest, logging
from datetime import datetime ,timedelta
from bson import ObjectId

# from lkf_modules.accesos.items.scripts.Accesos.accesos_utils import Accesos
from lkf_addons.addons.accesos.app import Accesos

from account_settings import *

# Configuracion del logging para los logs al ejecutar pytest
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)

accesos_obj = Accesos(settings, use_api=True)

access_pass = {
    "empresa": "LkfTesting",
    "tipo_visita_pase": "fecha_fija",
    "tema_cita": "Tema de la cita",
    # "enviar_correo_pre_registro": ["enviar_correo_pre_registro", "enviar_sms_pre_registro"],
    "enviar_correo_pre_registro": [],
    "config_dia_de_acceso": "limitar_d\u00edas_de_acceso",
    "perfil_pase": "Visita General",
    "custom": True,
    "descripcion": "Descripcion de la cita",
    "fecha_desde_visita": "2025-04-23 13:00:00",
    "status_pase": "Proceso",
    "link": {
        "docs": ["agregarIdentificacion", "agregarFoto"],
        "creado_por_email": "seguridad@linkaform.com",
        "link": "https://app.soter.mx/pase.html",
        "creado_por_id": "10"
    },
    "config_limitar_acceso": None,
    "ubicacion": "Planta Monterrey",
    "nombre": "Pase de Testing",
    "visita_a": "Emiliano Zapata",
    "telefono": "+528341227834",
    "email": "paco@linkaform.com",
    "comentarios": [
        {"tipo_comentario": "Pase", "comentario_pase": "Comentario"}
    ]
}

access_pass_with_3_access = {
    "empresa": "Testing Lkf",
    "tipo_visita_pase": "rango_de_fechas",
    "tema_cita": "Testing de la cita",
    "config_dia_de_acceso": "cualquier_d\u00eda",
    "perfil_pase": "Visita General",
    "fecha_desde_hasta": "2025-04-27 00:00:00",
    "custom": True,
    "descripcion": "Descripcion de la cita",
    "fecha_desde_visita": "2025-04-23 00:00:00",
    "status_pase": "Proceso",
    "link": {
        "docs": ["agregarIdentificacion", "agregarFoto"],
        "creado_por_email": "seguridad@linkaform.com",
        "link": "https://app.soter.mx/pase.html",
        "creado_por_id": "10"
    },
    "config_limitar_acceso": 3,
    "ubicacion": "Planta Monterrey",
    "nombre": "Pase con 3 Accesos",
    "visita_a": "Emiliano Zapata",
    "telefono": "+528341227834",
    "email": "paco@linkaform.com",
    "comentarios": [{
        "tipo_comentario": "Pase",
        "comentario_pase": "Comentario de testing"
    }]
}

access_pass_caducated = {
    "empresa": "LkfTesting",
    "tipo_visita_pase": "fecha_fija",
    "tema_cita": "Tema de la cita",
    # "enviar_correo_pre_registro": ["enviar_correo_pre_registro", "enviar_sms_pre_registro"],
    "enviar_correo_pre_registro": [],
    "config_dia_de_acceso": "limitar_d\u00edas_de_acceso",
    "perfil_pase": "Visita General",
    "custom": True,
    "descripcion": "Descripcion de la cita",
    "fecha_desde_visita": "2025-04-20 13:00:00",
    "status_pase": "Proceso",
    "link": {
        "docs": ["agregarIdentificacion", "agregarFoto"],
        "creado_por_email": "seguridad@linkaform.com",
        "link": "https://app.soter.mx/pase.html",
        "creado_por_id": "10"
    },
    "config_limitar_acceso": None,
    "ubicacion": "Planta Monterrey",
    "nombre": "Pase de Testing Vencido",
    "visita_a": "Emiliano Zapata",
    "telefono": "+528341227834",
    "email": "paco@linkaform.com",
    "comentarios": [
        {"tipo_comentario": "Pase", "comentario_pase": "Comentario"}
    ]
}

access_pass_days_selected = {
    "empresa": "Lkf Testing",
    "tipo_visita_pase": "rango_de_fechas",
    "tema_cita": "Testing de la cita",
    "config_dia_de_acceso": "limitar_d\u00edas_de_acceso",
    "perfil_pase": "Visita General",
    "fecha_desde_hasta": "2025-04-28 00:00:00",
    "custom": True,
    "descripcion": "Descripcion de la cita",
    "fecha_desde_visita": "2025-04-23 00:00:00",
    "status_pase": "Proceso",
    "link": {
        "docs": ["agregarIdentificacion", "agregarFoto"],
        "creado_por_email": "seguridad@linkaform.com",
        "link": "https://app.soter.mx/pase.html",
        "creado_por_id": "10"
    },
    "config_limitar_acceso": None,
    "ubicacion": "Planta Monterrey",
    "nombre": "Pase de Dias Seleccionados",
    "visita_a": "Emiliano Zapata",
    "config_dias_acceso": [
        "lunes", "mi\u00e9rcoles", "viernes", "s\u00e1bado"
    ],
    "telefono": "+528341227834",
    "email": "paco@linkaform.com",
    "comentarios": [
        {"tipo_comentario": "Pase", "comentario_pase": "Comentario de test"}
    ]
}

access_pass_no_completed = {
    "empresa": "LkfTesting",
    "tipo_visita_pase": "fecha_fija",
    "tema_cita": "Tema de la cita",
    # "enviar_correo_pre_registro": ["enviar_correo_pre_registro", "enviar_sms_pre_registro"],
    "enviar_correo_pre_registro": [],
    "config_dia_de_acceso": "limitar_d\u00edas_de_acceso",
    "perfil_pase": "Visita General",
    "custom": True,
    "descripcion": "Descripcion de la cita",
    "fecha_desde_visita": "2025-04-23 13:00:00",
    "status_pase": "Proceso",
    "link": {
        "docs": ["agregarIdentificacion", "agregarFoto"],
        "creado_por_email": "seguridad@linkaform.com",
        "link": "https://app.soter.mx/pase.html",
        "creado_por_id": "10"
    },
    "config_limitar_acceso": None,
    "ubicacion": "Planta Monterrey",
    "nombre": "Pase de No Completado",
    "visita_a": "Emiliano Zapata",
    "telefono": "+528341227834",
    "email": "paco@linkaform.com",
    "comentarios": [
        {"tipo_comentario": "Pase", "comentario_pase": "Comentario"}
    ]
}

complete_access_pass = {
    "walkin_identificacion": [{
        "file_name": "indentificacion.png",
        "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/116852/660459dde2b2d414bce9cf8f/6806c367a6f263109c2818d2.png"
    }],
    "status_pase": "Activo",
    "grupo_vehiculos": [],
    "walkin_fotografia": [{
        "file_name": "foto.png", 
        "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/116852/660459dde2b2d414bce9cf8f/6806c3617ee1dd400c51bc2d.png"
    }],
    "grupo_equipos": []
}

data_access = {
    "vehiculo": [],
    "area": "Caseta Principal",
    "comentario_pase": [],
    "qr_code": "6806d784109cf378aa2a764e",
    "script_name": "script_turnos.py",
    "location": "Planta Monterrey",
    "gafete": {},
    "visita_a": [{
        "puesto": ["Jefe de Seguridad"],
        "nombre": "Emiliano Zapata",
        "user_id": [10],
        "email": ["seguridad@linkaform.com"],
        "departamento": ["Seguridad"]
    }],
    "comentario_acceso": [],
    "equipo": [],
    "option": "do_access"
}

user_id = 10
user_email = 'seguridad@linkaform.com'
location = 'Planta Monterrey'
area = 'Caseta Principal'

class TestAccesos:

    folio = ''
    complete_access_pass_folio = ''
    qr_code = ''

    def create_access_pass(self, location, access_pass):
        #---Define Metadata
        metadata = accesos_obj.lkf_api.get_metadata(form_id=accesos_obj.PASE_ENTRADA)
        assert metadata, 'No se recibio metadata'

        metadata.update({
            "properties": {
                "device_properties":{
                    "System": "Script",
                    "Module": "Accesos",
                    "Process": "Creación de pase",
                    "Action": "create_access_pass",
                    "File": "accesos/app.py"
                }
            },
        })

        #---Define Answers
        answers = {}
        perfil_pase = access_pass.get('perfil_pase')
        location_name = access_pass.get('ubicacion')
        if not location:
            location = location_name
        address = accesos_obj.get_location_address(location_name=location_name)
        assert 'address' in address, 'La address no contiene la key necesitada'

        access_pass['direccion'] = [address.get('address', '')]
        user_data = accesos_obj.lkf_api.get_user_by_id(user_id=user_id)
        assert user_data, 'NO hay user_data'

        timezone = user_data.get('timezone','America/Monterrey')
        now_datetime = accesos_obj.today_str(timezone, date_format='datetime')
        employee = accesos_obj.get_employee_data(email=user_email, get_one=True)
        assert employee, 'No se recibio el empleado data'

        nombre_visita_a = employee.get('worker_name')

        if(access_pass.get('site', '') == 'accesos'):
            nombre_visita_a = access_pass.get('visita_a')

        answers[accesos_obj.UBICACIONES_CAT_OBJ_ID] = {}
        answers[accesos_obj.UBICACIONES_CAT_OBJ_ID][accesos_obj.f['location']] = location
        if access_pass.get('custom') == True :
            answers[accesos_obj.pase_entrada_fields['tipo_visita_pase']] = access_pass.get('tipo_visita_pase',"")
            answers[accesos_obj.pase_entrada_fields['fecha_desde_visita']] = access_pass.get('fecha_desde_visita',"")
            answers[accesos_obj.pase_entrada_fields['fecha_desde_hasta']] = access_pass.get('fecha_desde_hasta',"")
            answers[accesos_obj.pase_entrada_fields['config_dia_de_acceso']] = access_pass.get('config_dia_de_acceso',"")
            answers[accesos_obj.pase_entrada_fields['config_dias_acceso']] = access_pass.get('config_dias_acceso',"")
            answers[accesos_obj.pase_entrada_fields['catalago_autorizado_por']] =  {accesos_obj.pase_entrada_fields['autorizado_por']:nombre_visita_a}
            answers[accesos_obj.pase_entrada_fields['status_pase']] = access_pass.get('status_pase',"").lower()
            answers[accesos_obj.pase_entrada_fields['empresa_pase']] = access_pass.get('empresa',"")
            answers[accesos_obj.pase_entrada_fields['ubicacion_cat']] = {accesos_obj.mf['ubicacion']:access_pass['ubicacion'], accesos_obj.mf['direccion']:access_pass.get('direccion',"")}
            answers[accesos_obj.pase_entrada_fields['tema_cita']] = access_pass.get('tema_cita',"") 
            answers[accesos_obj.pase_entrada_fields['descripcion']] = access_pass.get('descripcion',"") 
            answers[accesos_obj.pase_entrada_fields['config_limitar_acceso']] = access_pass.get('config_limitar_acceso',"") 

        else:
            answers[accesos_obj.mf['fecha_desde_visita']] = now_datetime
            answers[accesos_obj.mf['tipo_visita_pase']] = 'fecha_fija'
        answers[accesos_obj.pase_entrada_fields['tipo_visita']] = 'alta_de_nuevo_visitante'
        answers[accesos_obj.pase_entrada_fields['walkin_nombre']] = access_pass.get('nombre')
        answers[accesos_obj.pase_entrada_fields['walkin_email']] = access_pass.get('email', '')
        answers[accesos_obj.pase_entrada_fields['walkin_empresa']] = access_pass.get('empresa')
        answers[accesos_obj.pase_entrada_fields['walkin_fotografia']] = access_pass.get('foto')
        answers[accesos_obj.pase_entrada_fields['walkin_identificacion']] = access_pass.get('identificacion')
        answers[accesos_obj.pase_entrada_fields['walkin_telefono']] = access_pass.get('telefono', '')
        
        if access_pass.get('comentarios'):
            comm = access_pass.get('comentarios',[])
            if comm:
                comm_list = []
                for c in comm:
                    comm_list.append(
                        {
                            accesos_obj.pase_entrada_fields['comentario_pase']:c.get('comentario_pase'),
                            accesos_obj.pase_entrada_fields['tipo_comentario'] :c.get('tipo_comentario').lower()
                        }
                    )
                answers.update({accesos_obj.pase_entrada_fields['grupo_instrucciones_pase']:comm_list})

        if access_pass.get('areas'):
            areas = access_pass.get('areas',[])
            if areas:
                areas_list = []
                for c in areas:
                    areas_list.append(
                        {
                            accesos_obj.pase_entrada_fields['commentario_area']:c.get('commentario_area'),
                            accesos_obj.pase_entrada_fields['area_catalog_normal'] :{accesos_obj.mf['nombre_area']: c.get('nombre_area')}
                        }
                    )
                answers.update({accesos_obj.pase_entrada_fields['grupo_areas_acceso']:areas_list})
        #Visita A
        answers[accesos_obj.mf['grupo_visitados']] = []
        visita_a = access_pass.get('visita_a')
        visita_set = {
            accesos_obj.CONF_AREA_EMPLEADOS_CAT_OBJ_ID:{
                accesos_obj.mf['nombre_empleado'] : nombre_visita_a,
                }
            }
        options_vistia = {
              "group_level": 3,
              "startkey": [location, nombre_visita_a],
              "endkey": [location, f"{nombre_visita_a}\n",{}],
            }
        cat_visita = accesos_obj.catalogo_view(accesos_obj.CONF_AREA_EMPLEADOS_CAT_ID, accesos_obj.PASE_ENTRADA, options_vistia)
        if len(cat_visita) > 0:
            cat_visita =  {key: [value,] for key, value in cat_visita[0].items() if value}
        else:
            selector = {}
            selector.update({f"answers.{accesos_obj.mf['nombre_empleado']}": nombre_visita_a})
            fields = ["_id", f"answers.{accesos_obj.mf['nombre_empleado']}", f"answers.{accesos_obj.mf['email_visita_a']}", f"answers.{accesos_obj.mf['id_usuario']}"]

            mango_query = {
                "selector": selector,
                "fields": fields,
                "limit": 1
            }

            row_catalog = accesos_obj.lkf_api.search_catalog(accesos_obj.CONF_AREA_EMPLEADOS_CAT_ID, mango_query)
            if row_catalog:
                visita_set[accesos_obj.CONF_AREA_EMPLEADOS_CAT_OBJ_ID].update({
                    accesos_obj.mf['nombre_empleado']: nombre_visita_a,
                    accesos_obj.mf['email_visita_a']: [row_catalog[0].get(accesos_obj.mf['email_visita_a'], "")],
                    accesos_obj.mf['id_usuario']: [row_catalog[0].get(accesos_obj.mf['id_usuario'], "")],
                })

        visita_set[accesos_obj.CONF_AREA_EMPLEADOS_CAT_OBJ_ID].update(cat_visita)
        answers[accesos_obj.mf['grupo_visitados']].append(visita_set)

        # Perfil de Pase
        answers[accesos_obj.CONFIG_PERFILES_OBJ_ID] = {
            accesos_obj.mf['nombre_perfil'] : perfil_pase,
        }
        options = {
              "group_level": 2,
              "startkey": [perfil_pase],
              "endkey": [f"{perfil_pase}\n",{}],
            }
        cat_perfil = accesos_obj.catalogo_view(accesos_obj.CONFIG_PERFILES_ID, accesos_obj.PASE_ENTRADA, options)
        if len(cat_perfil) > 0:
            if access_pass.get('custom') == True :
                cat_perfil[0][accesos_obj.mf['motivo']]= [cat_perfil[0].get(accesos_obj.mf['motivo'])]
            else:
                cat_perfil[0][accesos_obj.mf['motivo']]= ["Reunión"]
            cat_perfil = cat_perfil[0]
        answers[accesos_obj.CONFIG_PERFILES_OBJ_ID].update(cat_perfil)
        if answers[accesos_obj.CONFIG_PERFILES_OBJ_ID].get(accesos_obj.mf['nombre_permiso']) and \
           type(answers[accesos_obj.CONFIG_PERFILES_OBJ_ID][accesos_obj.mf['nombre_permiso']]) == str:
            answers[accesos_obj.CONFIG_PERFILES_OBJ_ID][accesos_obj.mf['nombre_permiso']] = [answers[accesos_obj.CONFIG_PERFILES_OBJ_ID][accesos_obj.mf['nombre_permiso']],]

        #---Valor
        metadata.update({'answers':answers})
        res = accesos_obj.lkf_api.post_forms_answers(metadata)
        assert res['status_code'] in (200, 201), 'No se recibio respuesta correcta'

        if res.get("status_code") ==200 or res.get("status_code")==201:
            TestAccesos.folio = res.get("json")["id"]
            TestAccesos.complete_access_pass_folio = res.get("json")["id"]

            link_info=access_pass.get('link', "")
            docs=""
            
            if link_info:
                for index, d in enumerate(link_info["docs"]): 
                    if(d == "agregarIdentificacion"):
                        docs+="iden"
                    elif(d == "agregarFoto"):
                        docs+="foto"
                    if index==0 :
                        docs+="-"
                link_pass= f"{link_info['link']}?id={res.get('json')['id']}&user={link_info['creado_por_id']}&docs={docs}"
                # TODO Modularizar id forma y id campo
                id_forma = 121736
                id_campo = '673773741b2adb2d05d99d63'

                tema_cita = access_pass.get("tema_cita")
                descripcion = access_pass.get("descripcion")
                fecha_desde_visita = access_pass.get("fecha_desde_visita")
                fecha_desde_hasta = access_pass.get("fecha_desde_hasta")
                creado_por_email = access_pass.get("link", {}).get("creado_por_email")
                ubicacion = access_pass.get("ubicacion")
                nombre = access_pass.get("nombre")
                visita_a = access_pass.get("visita_a")
                email = access_pass.get("email")

                start_datetime = datetime.strptime(fecha_desde_visita, "%Y-%m-%d %H:%M:%S")

                if not fecha_desde_hasta:
                    stop_datetime = start_datetime + timedelta(hours=1)
                    meeting = [
                        {
                            "id": 1,
                            "start": start_datetime,
                            "stop": stop_datetime,
                            "name": tema_cita,
                            "description": descripcion,
                            "location": ubicacion,
                            "allday": False,
                            "rrule": None,
                            "alarm_ids": [{"interval": "minutes", "duration": 10, "name": "Reminder"}],
                            'organizer_name': visita_a,
                            'organizer_email': creado_por_email,
                            "attendee_ids": [{"email": email, "nombre": nombre}, {"email": creado_por_email, "nombre": visita_a}],
                        }
                    ]
                    respuesta_ics = accesos_obj.upload_ics(id_forma, id_campo, meetings=meeting)
                    file_name = respuesta_ics.get('file_name', '')
                    file_url = respuesta_ics.get('file_url', '')

                    access_pass_custom={"link":link_pass, "enviar_correo_pre_registro": access_pass.get("enviar_correo_pre_registro",[]),
                    "archivo_invitacion": [
                        {
                            "file_name": f"{file_name}",
                            "file_url": f"{file_url}"
                        }
                    ]}
                else:
                    access_pass_custom={"link":link_pass, "enviar_correo_pre_registro": access_pass.get("enviar_correo_pre_registro",[])}
                resUp= self.update_pass(access_pass=access_pass_custom, folio=res.get("json")["id"])
            else:
                link_pass=""
        
        return res

    def update_pass(self, access_pass,folio=None):
        pass_selected = accesos_obj.get_detail_access_pass(qr_code=folio)
        assert 'folio' in pass_selected, 'El pase seleccionado no tiene folio'
        
        qr_code = folio
        _folio = pass_selected.get("folio")
        answers={}
        for key, value in access_pass.items():
            if key == 'grupo_vehiculos':
                answers[accesos_obj.mf['grupo_vehiculos']]={}
                index=1
                for index, item in enumerate(access_pass.get('grupo_vehiculos',[])):
                    tipo = item.get('tipo','')
                    marca = item.get('marca','')
                    modelo = item.get('modelo','')
                    estado = item.get('estado','')
                    placas = item.get('placas','')
                    color = item.get('color','')
                    obj={
                        accesos_obj.TIPO_DE_VEHICULO_OBJ_ID:{
                            accesos_obj.mf['tipo_vehiculo']:tipo,
                            accesos_obj.mf['marca_vehiculo']:marca,
                            accesos_obj.mf['modelo_vehiculo']:modelo,
                        },
                        accesos_obj.ESTADO_OBJ_ID:{
                            accesos_obj.mf['nombre_estado']:estado,
                        },
                        accesos_obj.mf['placas_vehiculo']:placas,
                        accesos_obj.mf['color_vehiculo']:color,
                    }
                    answers[accesos_obj.mf['grupo_vehiculos']][-index]=obj
            elif key == 'grupo_equipos':
                answers[accesos_obj.mf['grupo_equipos']]={}
                index=1
                for index, item in enumerate(access_pass.get('grupo_equipos',[])):
                    nombre = item.get('nombre','')
                    marca = item.get('marca','')
                    color = item.get('color','')
                    tipo = item.get('tipo','')
                    serie = item.get('serie','')
                    modelo = item.get('modelo','')
                    obj={
                        accesos_obj.mf['tipo_equipo']:tipo.lower(),
                        accesos_obj.mf['nombre_articulo']:nombre,
                        accesos_obj.mf['marca_articulo']:marca,
                        accesos_obj.mf['numero_serie']:serie,
                        accesos_obj.mf['color_articulo']:color,
                        accesos_obj.mf['modelo_articulo']:modelo,
                    }
                    answers[accesos_obj.mf['grupo_equipos']][-index]=obj
            elif key == 'status_pase':
                answers.update({f"{accesos_obj.pase_entrada_fields[key]}":value.lower()})
            elif key == 'archivo_invitacion':
                answers.update({f"{accesos_obj.pase_entrada_fields[key]}": value})
            elif key == 'favoritos':
                answers.update({f"{accesos_obj.pase_entrada_fields[key]}": [value]})    
            else:
                answers.update({f"{accesos_obj.pase_entrada_fields[key]}":value})
        employee = accesos_obj.get_employee_data(email=user_email, get_one=True)
        assert employee, 'No se recibio el empleado en la actualizacion'

        if answers:
            res = accesos_obj.lkf_api.patch_multi_record( answers = answers, form_id=accesos_obj.PASE_ENTRADA, record_id=[qr_code])
            assert res['status_code'] in (201, 202), 'No se hizo la actualizacion del pase correctamente'

            if res.get('status_code') == 201 or res.get('status_code') == 202 and folio:
                if employee.get('usuario_id', [])[0] == 7742:
                    pdf = accesos_obj.lkf_api.get_pdf_record(qr_code, template_id = 553, name_pdf='Pase de Entrada', send_url=True)
                else:
                    pdf = accesos_obj.lkf_api.get_pdf_record(qr_code, template_id = 491, name_pdf='Pase de Entrada', send_url=True)
                assert pdf, 'No se obtuvo el pdf del pase correctamente en la actualizacion'

                res['json'].update({'qr_pase':pass_selected.get("qr_pase")})
                res['json'].update({'telefono':pass_selected.get("telefono")})
                res['json'].update({'enviar_a':pass_selected.get("nombre")})
                res['json'].update({'enviar_de':employee.get('worker_name')})
                res['json'].update({'enviar_de_correo':employee.get('email')})
                res['json'].update({'ubicacion':pass_selected.get('ubicacion')})
                res['json'].update({'fecha_desde':pass_selected.get('fecha_de_expedicion')})
                res['json'].update({'fecha_hasta':pass_selected.get('fecha_de_caducidad')})
                res['json'].update({'asunto':pass_selected.get('tema_cita')})
                res['json'].update({'descripcion':pass_selected.get('descripcion')})
                res['json'].update({'pdf': pdf})
                return res
            else: 
                return res
        else:
            self.LKFException('No se mandarón parametros para actualizar')

    def do_access(self, qr_code, location, area, data):
        access_pass = accesos_obj.get_detail_access_pass(qr_code)
        if not qr_code and not location and not area:
            return False
        total_entradas = accesos_obj.get_count_ingresos(qr_code)
        
        diasDisponibles = access_pass.get("limitado_a_dias", [])
        dias_semana = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        hoy = datetime.now()
        dia_semana = hoy.weekday()
        nombre_dia = dias_semana[dia_semana]

        if access_pass.get('estatus',"") == 'vencido':
            accesos_obj.LKFException({'msg':"El pase esta vencido, edita la información o genera uno nuevo.","title":'Revisa la Configuración'})
        elif access_pass.get('estatus', '') == 'proceso':
            accesos_obj.LKFException({'msg':"El pase no se ha sido completado aun, informa al usuario que debe completarlo primero.","title":'Requisitos faltantes'})

        if diasDisponibles:
            if nombre_dia not in diasDisponibles:
                accesos_obj.LKFException({'msg':"No se permite realizar ingresos este día.","title":'Revisa la Configuración'})
        
        limite_acceso = access_pass.get('limite_de_acceso')
        if len(total_entradas) > 0 and limite_acceso and int(limite_acceso) > 0:
            if total_entradas['total_records']>= int(limite_acceso) :
                accesos_obj.LKFException({'msg':"Se ha completado el limite de entradas disponibles para este pase, edita el pase o crea uno nuevo.","title":'Revisa la Configuración'})
        
        timezone = pytz.timezone('America/Mexico_City')
        fecha_actual = datetime.now(timezone).replace(microsecond=0)
        fecha_caducidad = access_pass.get('fecha_de_caducidad')
        fecha_obj_caducidad = datetime.strptime(fecha_caducidad, "%Y-%m-%d %H:%M:%S")
        fecha_caducidad = timezone.localize(fecha_obj_caducidad)

        fecha_caducidad_con_margen = fecha_caducidad + timedelta(minutes=15)

        if fecha_caducidad_con_margen < fecha_actual:
            accesos_obj.LKFException({'msg':"El pase esta vencido, ya paso su fecha de vigencia.","title":'Advertencia'})
        
        if access_pass.get("ubicacion") != location:
            accesos_obj.LKFException({'msg':"No se puede realizar un ingreso en una ubicación diferente.","title":'Revisa la Configuración'})
        
        if accesos_obj.validate_access_pass_location(qr_code, location):
            accesos_obj.LKFException("En usuario ya se encuentra dentro de una ubicacion")
        val_certificados = accesos_obj.validate_certificados(qr_code, location)

        
        pass_dates = accesos_obj.validate_pass_dates(access_pass)
        comentario_pase =  data.get('comentario_pase',[])
        if comentario_pase:
            values = {accesos_obj.pase_entrada_fields['grupo_instrucciones_pase']:{
                -1:{
                accesos_obj.pase_entrada_fields['comentario_pase']:comentario_pase,
                accesos_obj.mf['tipo_de_comentario']:'caseta'
                }
            }
            }
        res = self._do_access(access_pass, location, area, data)

    def do_access_mutated(self, qr_code, location, area, data, hoy_parameter):
        access_pass = accesos_obj.get_detail_access_pass(qr_code)
        if not qr_code and not location and not area:
            return False
        total_entradas = accesos_obj.get_count_ingresos(qr_code)
        
        diasDisponibles = access_pass.get("limitado_a_dias", [])
        dias_semana = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        nombre_dia = dias_semana[hoy_parameter]

        if access_pass.get('estatus',"") == 'vencido':
            accesos_obj.LKFException({'msg':"El pase esta vencido, edita la información o genera uno nuevo.","title":'Revisa la Configuración'})
        elif access_pass.get('estatus', '') == 'proceso':
            accesos_obj.LKFException({'msg':"El pase no se ha sido completado aun, informa al usuario que debe completarlo primero.","title":'Requisitos faltantes'})

        if diasDisponibles:
            if nombre_dia not in diasDisponibles:
                accesos_obj.LKFException({'msg':"No se permite realizar ingresos este día.","title":'Revisa la Configuración'})
        
        limite_acceso = access_pass.get('limite_de_acceso')
        if len(total_entradas) > 0 and limite_acceso and int(limite_acceso) > 0:
            if total_entradas['total_records']>= int(limite_acceso) :
                accesos_obj.LKFException({'msg':"Se ha completado el limite de entradas disponibles para este pase, edita el pase o crea uno nuevo.","title":'Revisa la Configuración'})
        
        timezone = pytz.timezone('America/Mexico_City')
        fecha_actual = datetime.now(timezone).replace(microsecond=0)
        fecha_caducidad = access_pass.get('fecha_de_caducidad')
        fecha_obj_caducidad = datetime.strptime(fecha_caducidad, "%Y-%m-%d %H:%M:%S")
        fecha_caducidad = timezone.localize(fecha_obj_caducidad)

        fecha_caducidad_con_margen = fecha_caducidad + timedelta(minutes=15)

        if fecha_caducidad_con_margen < fecha_actual:
            accesos_obj.LKFException({'msg':"El pase esta vencido, ya paso su fecha de vigencia.","title":'Advertencia'})
        
        if access_pass.get("ubicacion") != location:
            accesos_obj.LKFException({'msg':"No se puede realizar un ingreso en una ubicación diferente.","title":'Revisa la Configuración'})
        
        if accesos_obj.validate_access_pass_location(qr_code, location):
            accesos_obj.LKFException("En usuario ya se encuentra dentro de una ubicacion")
        val_certificados = accesos_obj.validate_certificados(qr_code, location)

        
        pass_dates = accesos_obj.validate_pass_dates(access_pass)
        comentario_pase =  data.get('comentario_pase',[])
        if comentario_pase:
            values = {accesos_obj.pase_entrada_fields['grupo_instrucciones_pase']:{
                -1:{
                accesos_obj.pase_entrada_fields['comentario_pase']:comentario_pase,
                accesos_obj.mf['tipo_de_comentario']:'caseta'
                }
            }
            }

        # De momento no retorna nada
        # res = self._do_access(access_pass, location, area, data)

    def _do_access(self, access_pass, location, area, data):
        employee = accesos_obj.get_employee_data(email=user_email, get_one=True)
        assert employee, 'No se recibio el empleado en el acceso'
        
        metadata = accesos_obj.lkf_api.get_metadata(form_id=accesos_obj.BITACORA_ACCESOS)
        assert metadata, 'No se recibio metadata al hacer el acceso'

        metadata.update({
            'properties': {
                "device_properties":{
                    "System": "Script",
                    "Module": "Accesos",
                    "Process": "Ingreso de Personal",
                    "Action": 'Do Access',
                    "File": "accesos/app.py"
                }
            },
        })

        try:
            pase = {
                    f"{accesos_obj.mf['nombre_visita']}": access_pass['nombre'],
                    f"{accesos_obj.mf['curp']}":access_pass['curp'],
                    f"{accesos_obj.mf['empresa']}":[access_pass.get('empresa'),],
                    f"{accesos_obj.pase_entrada_fields['perfil_pase_id']}": [access_pass['tipo_de_pase'],],
                    f"{accesos_obj.pase_entrada_fields['status_pase']}":['Activo',],
                    f"{accesos_obj.pase_entrada_fields['foto_pase_id']}": access_pass.get("foto",[]),
                    f"{accesos_obj.pase_entrada_fields['identificacion_pase_id']}": access_pass.get("identificacion",[])
                    }
        except Exception as e:
            accesos_obj.LKFException({"msg":f"Error al crear registro ingreso, no se encontro: {e}"}) 

        answers = {
            f"{accesos_obj.mf['tipo_registro']}": 'entrada',
            f"{accesos_obj.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID}":{
                f"{accesos_obj.f['location']}":location,
                f"{accesos_obj.f['area']}":area
                },
            f"{accesos_obj.PASE_ENTRADA_OBJ_ID}":pase,
            f"{accesos_obj.mf['codigo_qr']}": str(access_pass['_id']),
            f"{accesos_obj.mf['fecha_entrada']}":accesos_obj.today_str(employee.get('timezone', 'America/Monterrey'), date_format='datetime'),
        }
        vehiculos = data.get('vehiculo',[])
        if vehiculos:
            list_vehiculos = []
            for item in vehiculos:
                tipo = item.get('tipo_vehiculo','')
                marca = item.get('marca_vehiculo','')
                modelo = item.get('modelo_vehiculo','')
                estado = item.get('nombre_estado','')
                placas = item.get('placas_vehiculo','')
                color = item.get('color_vehiculo','')
                list_vehiculos.append({
                    accesos_obj.TIPO_DE_VEHICULO_OBJ_ID:{
                        accesos_obj.mf['tipo_vehiculo']:tipo,
                        accesos_obj.mf['marca_vehiculo']:marca,
                        accesos_obj.mf['modelo_vehiculo']:modelo,
                    },
                    accesos_obj.ESTADO_OBJ_ID:{
                        accesos_obj.mf['nombre_estado']:estado,
                    },
                    accesos_obj.mf['placas_vehiculo']:placas,
                    accesos_obj.mf['color_vehiculo']:color,
                })
            answers[accesos_obj.mf['grupo_vehiculos']] = list_vehiculos  

        equipos = data.get('equipo',[])

        if equipos:
            list_equipos = []
            for item in equipos:
                tipo = item.get('tipo_equipo','').lower().replace(' ', '_')
                nombre = item.get('nombre_articulo','')
                marca = item.get('marca_articulo','')
                modelo = item.get('modelo_articulo','')
                color = item.get('color_articulo','')
                serie = item.get('numero_serie','')
                list_equipos.append({
                    accesos_obj.mf['tipo_equipo']:tipo,
                    accesos_obj.mf['nombre_articulo']:nombre,
                    accesos_obj.mf['marca_articulo']:marca,
                    accesos_obj.mf['modelo_articulo']:modelo,
                    accesos_obj.mf['color_articulo']:color,
                    accesos_obj.mf['numero_serie']:serie,
                })
            answers[accesos_obj.mf['grupo_equipos']] = list_equipos

        gafete = data.get('gafete',{})
        if gafete:
            gafete_ans = {}
            gafete_ans[accesos_obj.GAFETES_CAT_OBJ_ID] = {accesos_obj.gafetes_fields['gafete_id']:gafete.get('gafete_id')}
            gafete_ans[accesos_obj.LOCKERS_CAT_OBJ_ID] = {accesos_obj.mf['locker_id']:gafete.get('locker_id')}
            gafete_ans[accesos_obj.mf['documento']] = gafete.get('documento_garantia')
            answers.update(gafete_ans)
            self.update_gafet_status(answers)


        comment = data.get('comentario_acceso',[])
        if comment:
            comment_list = []
            for c in comment:
                comment_list.append(
                    {
                        accesos_obj.bitacora_fields['comentario']:c.get('comentario_pase'),
                        accesos_obj.bitacora_fields['tipo_comentario'] :c.get('tipo_de_comentario').lower().replace(' ', '_')
                    }
                )
            answers.update({accesos_obj.bitacora_fields['grupo_comentario']:comment_list})

        visit_list = data.get('visita_a',[])
        if visit_list:
            visit_list2 = []
            for c in visit_list:
                visit_list2.append(
                   { f"{accesos_obj.bitacora_fields['visita']}":{ 
                       accesos_obj.bitacora_fields['visita_nombre_empleado']:c.get('nombre'),
                       accesos_obj.mf['id_usuario'] :[c.get('user_id')],
                       accesos_obj.bitacora_fields['visita_departamento_empleado']:[c.get('departamento')],
                       accesos_obj.bitacora_fields['puesto_empleado']:[c.get('puesto')],
                       accesos_obj.mf['email_visita_a']:[c.get('email')]
                   }}
                )
            answers.update({accesos_obj.bitacora_fields['visita_a']:visit_list2})

        metadata.update({'answers':answers})
        response_create = accesos_obj.lkf_api.post_forms_answers(metadata)
        assert response_create['status_code'] in (201, 202), 'No se hizo el acceso correctamente'

        return response_create
    
    def update_gafet_status(self, answers={}):
        if not answers:
            answers = self.answers

        status = None
        tipo_movimiento=None
        tipo_movimiento = answers.get(accesos_obj.mf['tipo_registro'])
        res = {}
        location=""
        area=""
        if tipo_movimiento == "entrada":
            status = "En Uso"
        elif tipo_movimiento == 'salida':
            status = "Disponible"
        if status :
            gafete_id = answers[accesos_obj.GAFETES_CAT_OBJ_ID][accesos_obj.gafetes_fields['gafete_id']]
            locker_id = answers[accesos_obj.LOCKERS_CAT_OBJ_ID][accesos_obj.mf['locker_id']]
            if accesos_obj.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID in answers:
                if accesos_obj.f['area'] in answers[accesos_obj.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID]:
                    area = answers[accesos_obj.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID][accesos_obj.f['area']]
                if accesos_obj.f['location'] in answers[accesos_obj.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID]:
                    location = answers[accesos_obj.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID][accesos_obj.f['location']]
            
            gafete = accesos_obj.get_gafetes(status=None, location=location, area=area, gafete_id=gafete_id)

            print("heloooo", gafete, gafete_id, status,tipo_movimiento)

            if len(gafete) > 0 :
                gafete = gafete[0]
                res = accesos_obj.lkf_api.update_catalog_multi_record({accesos_obj.mf['status_gafete']: status}, accesos_obj.GAFETES_CAT_ID, record_id=[gafete['_id']])
                assert res['status_code'] in (200, 201, 202), 'No se hizo la actualizacion del gafete correctamente'
            self.update_locker_status(tipo_movimiento, location, area, tipo_locker='Identificaciones', locker_id=locker_id)

        return res

    def update_locker_status(self, tipo_movimiento, location, area, tipo_locker, locker_id):
        res = {}
        if tipo_movimiento == "entrada":
            status = "En Uso"
        elif tipo_movimiento == 'salida':
            status = "Disponible"

        locker = accesos_obj.get_lockers(status=None, location=location, area=area, tipo_locker=tipo_locker, locker_id=locker_id)
        if len(locker) > 0 :
            locker = locker[0]
            res = accesos_obj.lkf_api.update_catalog_multi_record({accesos_obj.mf['status_locker']: status}, accesos_obj.LOCKERS_CAT_ID, record_id=[locker['_id']])
            assert res['status_code'] in (200, 201, 202), 'No se hizo la actualizacion del status gafete correctamente'
        return res
    
    def do_out(self, qr, location, area, gafete_id=None):
        response = False
        last_check_out = accesos_obj.get_last_user_move(qr, location)
        assert last_check_out, 'No se recibio el ultimo movimiento del usuario'

        if last_check_out.get('gafete_id') and not gafete_id:
            accesos_obj.LKFException({"status_code":400, "msg":f"Se necesita liberar el gafete antes de regitrar la salida"})
        if not location:
            accesos_obj.LKFException({"status_code":400, "msg":f"Se requiere especificar una ubicacion de donde se realizara la salida."})
        if not area:
            accesos_obj.LKFException({"status_code":400, "msg":f"Se requiere especificar el area de donde se realizara la salida."})
        if last_check_out.get('folio'):
            folio = last_check_out.get('folio',0)
            checkin_date_str = last_check_out.get('checkin_date')
            checkin_date = accesos_obj.date_from_str(checkin_date_str)
            tz_mexico = pytz.timezone('America/Mexico_City')
            now = datetime.now(tz_mexico)
            fecha_hora_str = now.strftime("%Y-%m-%d %H:%M:%S")
            duration = time.strftime('%H:%M:%S', time.gmtime( accesos_obj.date_2_epoch(fecha_hora_str) - accesos_obj.date_2_epoch(checkin_date_str)))
            if accesos_obj.user_in_facility(status_visita=last_check_out.get('status_visita')):
                answers = {
                    f"{accesos_obj.mf['tipo_registro']}":'salida',
                    f"{accesos_obj.mf['fecha_salida']}":fecha_hora_str,
                    f"{accesos_obj.mf['duracion']}":duration,
                    f"{accesos_obj.AREAS_DE_LAS_UBICACIONES_SALIDA_OBJ_ID}": {
                        f"{accesos_obj.mf['nombre_area_salida']}": area,
                    },

                }
                response = accesos_obj.lkf_api.patch_multi_record( answers=answers, form_id=accesos_obj.BITACORA_ACCESOS, folios=[folio])
                assert response['status_code'] in (200, 201, 202), 'No se hizo la actualizacion de la bitacora correctamente'

        if not response:
            accesos_obj.LKFException({"status_code":400, "msg":f"El usuario no se encuentra dentro de la Ubicacion: {location}."})
        return response 
    
    ################################################### TESTS ####################################################
    # def test_number_one / 1. Haga un pase fecha fija, se le da acceso y salida posteriormente
    # def test_number_two / 2. Haga un pase de 3 accesos, validar hasta 4 veces (sleep 10seg)
    # def test_number_three / 3. Pase vigencia vencida, validar acceso
    # def test_number_four / 4. Pase con rango de fechas, dias seleccionados, validar dias que no tiene acceso
    # def test_number_five / 5. Pase sin completar, validar acceso

    def test_number_one(self):
        logging.info('Arranca test #1: Se crea pase, se completa, se le da entrada y posteriormente salida')
        # -- Se crea el pase nuevo
        self.create_access_pass(location=location, access_pass=access_pass)
        logging.info('================> Ya paso la creacion del pase')
        # -- El pase es completado
        time.sleep(5)
        self.update_pass(access_pass=complete_access_pass, folio=TestAccesos.complete_access_pass_folio)
        logging.info('================> Ya paso el completar del pase')
        # -- Se da el acceso con el pase completado
        self.do_access(qr_code=TestAccesos.folio, location=location, area=area, data=data_access)
        logging.info('================> Ya paso el acceso del pase')
        # -- Se da la salida con el pase completado
        time.sleep(5)
        self.do_out(TestAccesos.folio, location=location, area=area)
        logging.info('================> Ya paso la salida del pase')
        logging.info('================> TEST #1 FINALIZADO')

    def test_number_two(self):
        logging.info('Arranca test #2: Se crea pase con 3 accesos, se completa, se le da entrada y posteriormente salida 4 veces')
        # -- Se crea el pase nuevo con 3 accesos
        self.create_access_pass(location=location, access_pass=access_pass_with_3_access)
        logging.info('================> Ya paso la creacion del pase')
        # -- El pase es completado
        time.sleep(5)
        self.update_pass(access_pass=complete_access_pass, folio=TestAccesos.complete_access_pass_folio)
        logging.info('================> Ya paso el completar del pase')
        for i in range(4):
            if i < 3:
                # -- Se da el acceso con el pase completado
                self.do_access(qr_code=TestAccesos.folio, location=location, area=area, data=data_access)
                # -- Se da la salida con el pase completado
                time.sleep(5)
                self.do_out(TestAccesos.folio, location=location, area=area)
                logging.info(f"================> Ciclo: {i+1} de Entrada y Salida completado")
                time.sleep(5)
            else:
                with pytest.raises(Exception) as exc_info:
                    self.do_access(qr_code=TestAccesos.folio, location=location, area=area, data=data_access)
                logging.info(f"================> Excepción esperada capturada: {exc_info.value}")
        logging.info('================> TEST #2 FINALIZADO')

    def test_number_three(self):
        logging.info('Arranca test #3: Se crea un pase con fecha vencida, se completa y se le da entrada para validar que no tenga acceso')
        # -- Se crea el pase nuevo
        self.create_access_pass(location=location, access_pass=access_pass_caducated)
        logging.info('================> Ya paso la creacion del pase')
        # -- El pase es completado
        time.sleep(5)
        self.update_pass(access_pass=complete_access_pass, folio=TestAccesos.complete_access_pass_folio)
        logging.info('================> Ya paso el completar del pase')
        # -- Se da el acceso con el pase completado
        with pytest.raises(Exception) as exc_info:
            self.do_access(qr_code=TestAccesos.folio, location=location, area=area, data=data_access)
        logging.info(f"================> Excepción esperada capturada: {exc_info.value}")
        logging.info('================> TEST #3 FINALIZADO')

    def test_number_four(self):
        logging.info('Arranca test #4: Se crea un pase con dias seleccionados, se completa y se le da entrada para validar los dias que no tiene acceso')
        # -- Se crea el pase nuevo
        self.create_access_pass(location=location, access_pass=access_pass_days_selected)
        logging.info('================> Ya paso la creacion del pase')
        # -- El pase es completado
        time.sleep(5)
        self.update_pass(access_pass=complete_access_pass, folio=TestAccesos.complete_access_pass_folio)
        logging.info('================> Ya paso el completar del pase')

        # -- Se obtienen los indices de los dias no permitidos
        dias_semana = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        dias_validos = access_pass_days_selected.get('config_dias_acceso', [])
        dias_invalidos_indices = [i for i, dia in enumerate(dias_semana) if dia not in dias_validos]

        for i in dias_invalidos_indices:
            with pytest.raises(Exception) as exc_info:
                # -- Se da el acceso con el pase completado para validar
                self.do_access_mutated(qr_code=TestAccesos.folio, location=location, area=area, data=data_access, hoy_parameter=i)
            logging.info(f"================> Excepción esperada capturada: {exc_info.value}")
            time.sleep(5)
            logging.info(f"================> Dia no permitido validado: {dias_semana[i]}")
        logging.info('================> TEST #4 FINALIZADO')

    def test_number_five(self):
        logging.info('Arranca test #5: Se crea un pase, no se completa y se le da entrada para validar que no tenga acceso')
        # -- Se crea el pase nuevo
        self.create_access_pass(location=location, access_pass=access_pass_no_completed)
        logging.info('================> Ya paso la creacion del pase')
        time.sleep(5)
        # -- Se da el acceso con el pase completado
        with pytest.raises(Exception) as exc_info:
            self.do_access(qr_code=TestAccesos.folio, location=location, area=area, data=data_access)
        logging.info(f"================> Excepción esperada capturada: {exc_info.value}")
        logging.info('================> TEST #5 FINALIZADO')