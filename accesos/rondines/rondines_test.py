# Notas importantes:
# Arrancar pruebas unitarias
# ./lkf start test
# hay que checar que esten en modulos y test en ramas iguales
# en test debes de tener una rama por cliente

# -*- coding: utf-8 -*-
import sys, simplejson, copy, random, string, math, json, time, pytz, pytest, logging
from datetime import datetime ,timedelta
from bson import ObjectId
import concurrent.futures

from lkf_modules.accesos.items.scripts.Accesos.accesos_utils import Accesos
# from lkf_addons.addons.accesos.app import Accesos

from account_settings import *

# Configuracion del logging para los logs al ejecutar pytest
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)

# accesos_obj = Accesos(settings, use_api=True)

class TestAccesos:
    
    def setup_method(self):
        # Aquí creas el objeto para cada test
        self.accesos = Accesos(settings, use_api=True)
        
    def create_bitacora(self, winner, recorridos, check_area, location, closed=False):
        """
        Create a bitacora entry from cache data.
        """
        nombre_del_recorrido = ""
        ubicacion_del_recorrido = ""
        id_del_recorrido = ""
        print('Recorridos encontrados:', recorridos)
        for recorrido in recorridos:
            nombre_del_recorrido = recorrido.get('nombre_recorrido')
            ubicacion_del_recorrido = recorrido.get('ubicacion_recorrido')
            id_del_recorrido = recorrido.get('_id')

        if id_del_recorrido:
            areas_recorrido = self.accesos.get_areas_recorrido(id_del_recorrido)
            print('Áreas del recorrido:', areas_recorrido)
        else:
            areas_recorrido = []
            nombre_del_recorrido = 'Recorrido Automático'
            ubicacion_del_recorrido = winner.get('location', location)

        metadata = self.accesos.lkf_api.get_metadata(form_id=self.accesos.BITACORA_RONDINES)
        metadata.update({
            "properties": {
                "device_properties":{
                    "System": "Script",
                    "Module": "Accesos",
                    "Process": "Creación de Rondin",
                    "Action": "check_ubicacion_rondin",
                    "File": "accesos/check_ubicacion_rondin.py"
                }
            },
        })
        answers = {}

        tz = pytz.timezone('America/Mexico_City')

        print('winner in bitacora:', winner)
        answers[self.accesos.f['fecha_programacion']] = winner.get('timestamp') and datetime.fromtimestamp(winner.get('timestamp'), tz).strftime('%Y-%m-%d %H:%M:%S')
        answers[self.accesos.f['fecha_inicio_rondin']] = winner.get('timestamp') and datetime.fromtimestamp(winner.get('timestamp'), tz).strftime('%Y-%m-%d %H:%M:%S')

        answers[self.accesos.CONFIGURACION_RECORRIDOS_OBJ_ID] = {
            self.accesos.f['ubicacion_recorrido']: ubicacion_del_recorrido,
            self.accesos.f['nombre_del_recorrido']: nombre_del_recorrido
        }
        answers[self.accesos.f['estatus_del_recorrido']] = 'cerrado' if closed else 'en_proceso'
        check_areas_list = []
        for area in winner.get('checks', []):
            area_record_id = str(area.get('_id'))
            tag_value = area['check_data'].get(self.accesos.Location.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID, {}).get(self.accesos.f['tag_id_area_ubicacion'], '')
            if isinstance(tag_value, list):
                area_tag_id = tag_value
            else:
                area_tag_id = [tag_value] if tag_value else []
            format_area = {
                self.accesos.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID: {
                    self.accesos.f['nombre_area']: self.accesos.unlist(area['check_data'].get(self.accesos.Location.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID, {}).get(self.accesos.Location.f['area'], [])),
                    self.accesos.f['tag_id_area_ubicacion']: area_tag_id
                },
                self.accesos.f['fecha_hora_inspeccion_area']: area.get('timestamp') and datetime.fromtimestamp(area.get('timestamp'), tz).strftime('%Y-%m-%d %H:%M:%S'),
                self.accesos.f['foto_evidencia_area_rondin']: area['check_data'].get(self.accesos.f['foto_evidencia_area'], []),
                self.accesos.f['comentario_area_rondin']: area['check_data'].get(self.accesos.f['comentario_check_area'], ''),
                self.accesos.f['url_registro_rondin']: f"https://app.linkaform.com/#/records/detail/{area_record_id}",
            }
            check_areas_list.append(format_area)
            
        check_areas_list.sort(key=lambda x: self.accesos.parse_date_for_sorting(x.get(self.accesos.f['fecha_hora_inspeccion_area'], '')))
        answers[self.accesos.f['areas_del_rondin']] = check_areas_list

        # Recolecta los nombres de áreas que ya están en check_areas_list con información
        areas_con_info = set()
        for area in check_areas_list:
            area_name = area.get(self.accesos.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID, {}).get(self.accesos.f['nombre_area'], '')
            fecha = area.get(self.accesos.f['fecha_hora_inspeccion_area'], '')
            if area_name and fecha:  # Solo considerar áreas con fecha (que tienen información completa)
                areas_con_info.add(area_name)

        # Solo agregar áreas del recorrido que no estén ya en la lista con información
        for area in areas_recorrido:
            area_name = area.get('incidente_area', '')
            if area_name and area_name != check_area and area_name not in areas_con_info:
                answers[self.accesos.f['areas_del_rondin']].append({
                    self.accesos.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID: {
                        self.accesos.f['nombre_area']: area_name
                    },
                })

        # answers[self.accesos.f['bitacora_rondin_incidencias']] = self.accesos.answers.get(self.accesos.f['grupo_incidencias_check'], [])

        metadata.update({'answers':answers})
        print(simplejson.dumps(metadata, indent=3))

        res = self.accesos.lkf_api.post_forms_answers(metadata)
        return res
        
    def update_bitacora(self, cache, rondin, answers):
        """
        Recibe: Las answers del check de ubicacion, el area que se hice check de ubicacion y el registro de rondin
        Retorna: La respuesta de la api al hacer el patch de un registro
        Error: La respuesta de la api al hacer el patch de un registro
        """
        tz = pytz.timezone('America/Mexico_City')
        today = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
        rondin = self.accesos.unlist(rondin)
        rondin_en_progreso = True
        answers={}
        areas_list = []

        # print('rondinnnnnnnnnnnnnnnnn', simplejson.dumps(rondin, indent=3))

        if not rondin.get('fecha_inicio_rondin'):
            rondin['fecha_inicio_rondin'] = self.accesos.timestamp and datetime.fromtimestamp(self.accesos.timestamp, tz).strftime('%Y-%m-%d %H:%M:%S')

        conf_recorrido = {}
        for key, value in rondin.items():
            if key == 'fecha_programacion':
                answers[self.accesos.f['fecha_programacion']] = value
            elif key == 'fecha_inicio_rondin':
                answers[self.accesos.f['fecha_inicio_rondin']] = value
            elif key == 'fecha_fin_rondin':
                answers[self.accesos.f['fecha_fin_rondin']] = value
            elif key == 'estatus_del_recorrido' and value:
                answers[self.accesos.f['estatus_del_recorrido']] = value
            elif key == 'incidente_location':
                conf_recorrido.update({
                    self.accesos.f['ubicacion_recorrido']: value
                })
            elif key == 'nombre_del_recorrido':
                conf_recorrido.update({
                    self.accesos.f['nombre_del_recorrido']: value
                })
            elif key == 'estatus_del_recorrido':
                answers[self.accesos.f['estatus_del_recorrido']] = value
            elif key == 'areas_del_rondin':
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            area_name = (
                                item.get('incidente_area') or 
                                item.get(self.accesos.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID, {}).get(self.accesos.f['nombre_area'], '')
                            )
                            tag_value = (
                                item.get('tag_id_area_ubicacion') or 
                                item.get(self.accesos.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID, {}).get(self.accesos.f['tag_id_area_ubicacion'], '')
                            )
                            if isinstance(tag_value, list):
                                area_tag_id = tag_value
                            else:
                                area_tag_id = [tag_value] if tag_value else []
                            if area_name:
                                areas_list.append({
                                    self.accesos.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID: {
                                        self.accesos.f['nombre_area']: area_name,
                                        self.accesos.f['tag_id_area_ubicacion']: area_tag_id
                                    },
                                    self.accesos.f['fecha_hora_inspeccion_area']: item.get('fecha_hora_inspeccion_area', ''),
                                    self.accesos.f['foto_evidencia_area_rondin']: item.get('foto_evidencia_area_rondin', []),
                                    self.accesos.f['comentario_area_rondin']: item.get('comentario_area_rondin', ''),
                                    self.accesos.f['url_registro_rondin']: item.get('url_registro_rondin', '')
                                })
                
                for cache_item in cache:
                    data_cache = cache_item.get('check_data', {})
                    area_name = self.accesos.unlist(
                        data_cache.get(self.accesos.Location.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID, {})
                        .get(self.accesos.Location.f['area'], '')
                    )
                    tag_value = data_cache.get(self.accesos.Location.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID, {}).get(self.accesos.f['tag_id_area_ubicacion'], '')
                    if isinstance(tag_value, list):
                        area_tag_id = tag_value
                    else:
                        area_tag_id = [tag_value] if tag_value else []
                    
                    if area_name:
                        area_record_id = str(cache_item.get('_id'))
                        nueva_area = {
                            self.accesos.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID: {
                                self.accesos.f['nombre_area']: area_name,
                                self.accesos.f['tag_id_area_ubicacion']: area_tag_id
                            },
                            self.accesos.f['fecha_hora_inspeccion_area']: cache_item.get('timestamp') and datetime.fromtimestamp(cache_item['timestamp'], tz).strftime('%Y-%m-%d %H:%M:%S'),
                            self.accesos.f['foto_evidencia_area_rondin']: data_cache.get(self.accesos.f['foto_evidencia_area'], []),
                            self.accesos.f['comentario_area_rondin']: data_cache.get(self.accesos.f['comentario_check_area'], ''),
                            self.accesos.f['url_registro_rondin']: f"https://app.linkaform.com/#/records/detail/{area_record_id}",
                        }

                        reemplazado = False
                        for idx, area_existente in enumerate(areas_list):
                            nombre_existente = area_existente.get(self.accesos.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID, {}).get(self.accesos.f['nombre_area'], '')
                            fecha_existente = area_existente.get(self.accesos.f['fecha_hora_inspeccion_area'], '')
                            
                            # Si encontramos el mismo nombre de área
                            if nombre_existente == area_name:
                                # Si el área existente no tiene fecha pero la nueva sí, reemplazamos
                                if not fecha_existente and cache_item.get('timestamp'):
                                    areas_list[idx] = nueva_area
                                    reemplazado = True
                                    break
                                # Si ambas tienen fecha, nos quedamos con la que ya está
                                elif fecha_existente and cache_item.get('timestamp'):
                                    reemplazado = True
                                    break

                        if not reemplazado:
                            areas_list.append(nueva_area)
            
            all_areas_sorted = sorted(
                areas_list,
                key=lambda x: self.accesos.parse_date_for_sorting(x.get(self.accesos.f['fecha_hora_inspeccion_area'], ''))
            )
            
            answers[self.accesos.f['areas_del_rondin']] = all_areas_sorted
        else:
            pass

        answers[self.accesos.CONFIGURACION_RECORRIDOS_OBJ_ID] = conf_recorrido
        answers[self.accesos.f['fecha_fin_rondin']] = today if answers.get(self.accesos.f['check_status'], '') == ['finalizado', 'realizado', 'cerrado'] else ''
        
        format_list_incidencias = []
        for incidencia in rondin.get('bitacora_rondin_incidencias', []):
            inc = incidencia.get(self.accesos.f['tipo_de_incidencia'])
            if inc:
                incidencia.pop(self.accesos.f['tipo_de_incidencia'], None)
                incidencia.update({
                    self.accesos.LISTA_INCIDENCIAS_CAT_OBJ_ID: {
                        self.accesos.f['tipo_de_incidencia']: inc
                    }
                })
                format_list_incidencias.append(incidencia)
            
        rondin['bitacora_rondin_incidencias'] = format_list_incidencias
             
        # for incidencia in data_rondin.get(self.accesos.f['grupo_incidencias_check'], []):
        #     rondin['bitacora_rondin_incidencias'].append(incidencia)
        
        incidencias_list = rondin['bitacora_rondin_incidencias']
        incidencias_dict = {str(idx): incidencia for idx, incidencia in enumerate(incidencias_list)}
        answers[self.accesos.f['bitacora_rondin_incidencias']] = incidencias_dict
        
        if answers.get(self.accesos.f['check_status']) == 'finalizado':
            answers[self.accesos.f['estatus_del_recorrido']] = 'realizado'

        # print("ans", simplejson.dumps(answers, indent=4))

        if answers:
            metadata = self.accesos.lkf_api.get_metadata(form_id=self.accesos.BITACORA_RONDINES)
            metadata.update(self.accesos.get_record_by_folio(rondin.get('folio'), self.accesos.BITACORA_RONDINES, select_columns={'_id': 1}, limit=1))

            metadata.update({
                'properties': {
                    "device_properties": {
                        "system": "Addons",
                        "process":"Actualizacion de Bitacora", 
                        "accion":'rondines_cache', 
                        "folio": rondin.get('folio'), 
                        "archive": "rondines_cache.py"
                    }
                },
                'answers': answers,
                '_id': rondin.get('_id')
            })
            res = self.accesos.net.patch_forms_answers(metadata)
            if res.get('status_code') == 201 or res.get('status_code') == 202:
                return res
            else: 
                return res
          
    def create_cache(self, record_id, location, folio, timestamp, answers):
        """
        Create a cache entry for a rondin.
        """
        data = {}
        data.update({
            '_id': ObjectId(record_id),
            'location': location,
            'folio': folio,
            'timestamp': timestamp,
            'random': random.random(),
            'check_data': answers,
        })
        return self.accesos.create(data, collection='rondin_caches')
    
    def search_active_bitacora_by_rondin(self, recorridos, location):
        """
        Search for a bitacora by rondin name in form Bitacora Rondines.
        """
        format_names = []
        for recorrido in recorridos:
            format_names.append(recorrido.get('nombre_recorrido', ''))
        
        query = [
            {'$match': {
                "deleted_at": {"$exists": False},
                "form_id": self.accesos.BITACORA_RONDINES,
                f"answers.{self.accesos.CONFIGURACION_RECORRIDOS_OBJ_ID}.{self.accesos.Location.f['location']}": location,
                # f"answers.{self.accesos.CONFIGURACION_RECORRIDOS_OBJ_ID}.{self.accesos.f['nombre_del_recorrido']}": {"$in": format_names},
                f"answers.{self.accesos.f['estatus_del_recorrido']}": 'en_proceso',
            }},
            {'$sort': {'created_at': -1}},
            {'$limit': 1},
            {'$project': {
                '_id': 1,
                'folio': 1,
                'fecha_programacion': f"$answers.{self.accesos.f['fecha_programacion']}",
                'answers': f"$answers"
            }},
        ]
        resp = self.accesos.format_cr(self.accesos.cr.aggregate(query))
        return resp
    
    def search_rondin_by_area(self, location, check_area):
        """
        Search for a rondin by location and check_area in form Configuracion de Recorridos.
        """
        query = [
            {'$match': {
                'deleted_at': {'$exists': False},
                'form_id': self.accesos.CONFIGURACION_DE_RECORRIDOS_FORM,
                f"answers.{self.accesos.UBICACIONES_CAT_OBJ_ID}.{self.accesos.Location.f['location']}": location,
                f"answers.{self.accesos.f['grupo_de_areas_recorrido']}": {'$exists': True}
            }},
            {'$unwind': f"$answers.{self.accesos.f['grupo_de_areas_recorrido']}"},
            {'$project': {
                '_id': 1,
                'match_area': f"$answers.{self.accesos.f['grupo_de_areas_recorrido']}.{self.accesos.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID}.{self.accesos.f['nombre_area']}",
                'nombre_recorrido': f"$answers.{self.accesos.f['nombre_del_recorrido']}",
                'ubicacion_recorrido': f"$answers.{self.accesos.UBICACIONES_CAT_OBJ_ID}.{self.accesos.f['ubicacion_recorrido']}"
            }},
            {'$match': {
                'match_area': check_area
            }},
            {"$project": {
                "_id": 1,
                "nombre_recorrido": 1,
                "ubicacion_recorrido": 1
            }}
        ]
        resp = self.accesos.cr.aggregate(query)
        resp = list(resp)
        if not resp:
            query = [
                {'$match': {
                    'deleted_at': {'$exists': False},
                    'form_id': self.accesos.CONFIGURACION_DE_RECORRIDOS_FORM,
                    f"answers.{self.accesos.UBICACIONES_CAT_OBJ_ID}.{self.accesos.Location.f['location']}": location,
                    f"answers.{self.accesos.f['grupo_de_areas_recorrido']}": {'$exists': True}
                }},
                {'$project': {
                    '_id': 1,
                    'nombre_recorrido': f"$answers.{self.accesos.f['nombre_del_recorrido']}",
                    'ubicacion_recorrido': f"$answers.{self.accesos.UBICACIONES_CAT_OBJ_ID}.{self.accesos.f['ubicacion_recorrido']}"
                }},
            ]
            resp = self.accesos.cr.aggregate(query)
            resp = list(resp)
        return resp
    
    def rondines_cache(self, timestamp, answers, record_id, folio):
        self.accesos.cr_cache = self.accesos.net.get_collections(collection='rondin_caches')
        # print(simplejson.dumps(self.accesos.answers, indent=3))
        # data_rondin = json.loads(sys.argv[1])
        self.accesos.timestamp = timestamp
        tz = pytz.timezone('America/Mexico_City')
        # cache = self.accesos.search_cache()
        # print('cache', cache)
        # self.accesos.clear_cache()
        # breakpoint()

        location = answers.get(self.accesos.Location.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID, {})
        location = self.accesos.unlist(location.get(self.accesos.Location.f['location'], ''))
        check_area = answers.get(self.accesos.Location.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID, {})
        check_area = self.accesos.unlist(check_area.get(self.accesos.Location.f['area'], ''))
        
        #! 1. Obtener los recorridos existentes para el area ejecutada
        recorridos = self.search_rondin_by_area(location=location, check_area=check_area)

        #! 2. Se crea un cache con la informacion de el check
        self.create_cache(record_id, location, folio, timestamp, answers)
        time.sleep(5)
        cache = self.accesos.search_cache()

        #! 4. Se verifica si ya hay ganadores y si no se buscan por ubicacion y si ya tiene tiempo el check
        winners = self.accesos.select_winner(cache)
        winners_ids = [winner.get('winner_id') for winner in winners]
        self.accesos.set_winners(winners_ids)
        cache = self.accesos.search_cache()

        #! 5. Verificar si eres un ganador
        if record_id in winners_ids:
            selected_winner = [winner for winner in winners if winner.get('winner_id') == record_id]
            winner = selected_winner[0] if selected_winner else None
            if winner:
                winner_timestamp = winner.get('winner_record', {}).get('timestamp')
                winner_date = winner_timestamp and datetime.fromtimestamp(winner_timestamp, tz).strftime('%Y-%m-%d %H:%M:%S')
                now = datetime.now(tz)
                if winner_date:
                    winner_dt = datetime.strptime(winner_date, '%Y-%m-%d %H:%M:%S').replace(tzinfo=tz)
                    diff = now - winner_dt
                    winner_hour = winner_dt.strftime('%Y-%m-%d %H')
                    
                    #! Verificar si hay rondines que cerrar
                    rondines = self.accesos.get_rondines_by_status()
                    response = self.accesos.close_rondines(rondines)
                    if response:
                        print("response", response)
                    else:
                        print("No hay rondines que cerrar")

                    #! 7. Verificamos si ha pasado mas de 1 hora de este check pasado
                    if diff.total_seconds() > 3600 and winner.get('type') == 'closed_winner':
                        print('Ha pasado más de 1 hora desde el winner_date.')
                        #! 7-1 Se busca una bitacora cerrada para la hora en que se hizo este check
                        bitacora = self.accesos.search_closed_bitacora_by_hour(winner.get('location'), winner_hour)
                        time.sleep(5)
                        winner_checks = self.accesos.search_cache(winner_id=winner.get('winner_id'), location=winner.get('location'))
                        print('winner_checks:============', len(winner_checks))
                        #! 7-1-1 Se filtran los checks que pertenezcan a la hora del check ganador
                        filter_winner_checks = []
                        for check in winner_checks:
                            check_timestamp = check.get('timestamp')
                            if check_timestamp:
                                check_dt = datetime.fromtimestamp(check_timestamp, tz)
                                if check_dt.strftime('%Y-%m-%d %H') == winner_hour:
                                    filter_winner_checks.append(check)
                        winner_checks = filter_winner_checks
                        winner_checks.append(winner.get('winner_record', {}))
                        if bitacora:
                            #! 7-1-2. Actualizar una bitacora ya cerrada con los checks perdidos
                            response = self.update_bitacora(winner_checks, bitacora, answers)
                            print('response:', response)
                        else:
                            #! 7-1-3. Crea una bitacora ya cerrada con los checks perdidos
                            winner_record = winner.get('winner_record', {})
                            winner_record.update({
                                'checks': winner_checks
                            })
                            response = self.create_bitacora(winner=winner_record, recorridos=recorridos, check_area=check_area, location=location, closed=True)
                            print('response:', response)
                        clear_ids = [check.get('_id') for check in winner_checks]
                        clear_res = self.accesos.clear_cache(list_ids=clear_ids)
                    else:
                        #! 7-2-1 Se busca una bitacora activa para la hora en que se hizo este check
                        print('No ha pasado más de 1 hora desde el winner_date.')
                        bitacora = self.search_active_bitacora_by_rondin(recorridos=recorridos, location=location)
                        time.sleep(5)
                        winner_checks = self.accesos.search_cache(winner_id=winner.get('winner_id'), location=winner.get('location'))
                        winner_checks.append(winner.get('winner_record', {}))
                        if bitacora:
                            #! 7-2-2. Actualizar una bitacora con los checks realizados
                            response = self.update_bitacora(winner_checks, bitacora, answers)
                            print('response:', response)
                        else:
                            #! 7-2-3. Crea una bitacora con los checks realizados
                            print('No se encontró una bitácora activa por rondín.')
                            winner_record = winner.get('winner_record', {})
                            winner_record.update({
                                'checks': winner_checks
                            })
                            response = self.create_bitacora(winner=winner_record, recorridos=recorridos, check_area=check_area, location=location)
                            print('response:', response)
                        clear_ids = [check.get('_id') for check in winner_checks]
                        clear_res = self.accesos.clear_cache(list_ids=clear_ids)
                            
            #! Ver cache final
            response = self.accesos.search_cache()
            print('cache_final:', response)
        else:
            print('No eres ganador.')

    def test_number_one(self):
        logging.info('Arranca test #1: Se simula un recorrido completo en offline con 5 checks que se realizaron hace mas de una hora.')
        
        checks = [
            {
                "answers": {
                    "681144fb0d423e25b42818d3": [], 
                    "681fa6a8d916c74b691e174b": "continuar_siguiente_punto_de_inspecci\u00f3n", 
                    "66a83a77cfed7f342775c161": {
                        "663e5c57f5b8a7ce8211ed0b": ["Planta Monterrey"], 
                        "663e5e68f5b8a7ce8211ed18": ["Almacen"], 
                        "663e5d44f5b8a7ce8211ed0f": ["Almac\u00e9n de inventario"], 
                        "6762f7b0922cc2a2f57d4044": "687e899c3c2cab8e6307f679", 
                        "6763096aa99cee046ba766ad": []
                    }
                },
                "folio": '4154-10',
                "record_id": '68b7680e7639b94428a38725',
                "timestamp": 1756849947.372
            },  
            {
                "answers": {
                    "681144fb0d423e25b42818d3": [], 
                    "681fa6a8d916c74b691e174b": "continuar_siguiente_punto_de_inspecci\u00f3n", 
                    "66a83a77cfed7f342775c161": {
                        "663e5c57f5b8a7ce8211ed0b": ["Planta Monterrey"], 
                        "663e5e68f5b8a7ce8211ed18": ["Sala"], 
                        "663e5d44f5b8a7ce8211ed0f": ["Sala de Juntas Planta Baja"], 
                        "6762f7b0922cc2a2f57d4044": "68b7674e24ef22c4b60177ad", 
                        "6763096aa99cee046ba766ad": []
                    }
                },
                "folio": '4154-11',
                "record_id": '68b7680e7639b94428a38726',
                "timestamp": 1756849948.372
            },  
            {
                "answers": {
                    "681144fb0d423e25b42818d3": [], 
                    "681fa6a8d916c74b691e174b": "continuar_siguiente_punto_de_inspecci\u00f3n", 
                    "66a83a77cfed7f342775c161": {
                        "663e5c57f5b8a7ce8211ed0b": ["Planta Monterrey"], 
                        "663e5e68f5b8a7ce8211ed18": ["Caseta"], 
                        "663e5d44f5b8a7ce8211ed0f": ["Caseta 6 Poniente"], 
                        "6762f7b0922cc2a2f57d4044": "68b775bb24ef22c4b60177b0", 
                        "6763096aa99cee046ba766ad": []
                    }
                },
                "folio": '4154-12',
                "record_id": '68b7680e7639b94428a38727',
                "timestamp": 1756849949.372
            },  
            {
                "answers": {
                    "681144fb0d423e25b42818d3": [], 
                    "681fa6a8d916c74b691e174b": "continuar_siguiente_punto_de_inspecci\u00f3n", 
                    "66a83a77cfed7f342775c161": {
                        "663e5c57f5b8a7ce8211ed0b": ["Planta Monterrey"], 
                        "663e5e68f5b8a7ce8211ed18": ["Caseta"], 
                        "663e5d44f5b8a7ce8211ed0f": ["Caseta 2 - Mty"], 
                        "6762f7b0922cc2a2f57d4044": "68a4f5a588d1a1f78c011fcd", 
                        "6763096aa99cee046ba766ad": []
                    }
                },
                "folio": '4154-13',
                "record_id": '68b7680e7639b94428a38728',
                "timestamp": 1756849950.372
            },  
            {
                "answers": {
                    "681144fb0d423e25b42818d3": [], 
                    "681fa6a8d916c74b691e174b": "continuar_siguiente_punto_de_inspecci\u00f3n", 
                    "66a83a77cfed7f342775c161": {
                        "663e5c57f5b8a7ce8211ed0b": ["Planta Monterrey"], 
                        "663e5e68f5b8a7ce8211ed18": ["Asotea"], 
                        "663e5d44f5b8a7ce8211ed0f": ["Recursos eléctricos"], 
                        "6762f7b0922cc2a2f57d4044": "6887b826ba6042677e03fd01", 
                        "6763096aa99cee046ba766ad": []
                    }
                },
                "folio": '4154-14',
                "record_id": '68b7680e7639b94428a38729',
                "timestamp": 1756849951.372
            },            
        ]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for item in checks:
                record_id = item.get('record_id')
                folio = item.get('folio')
                timestamp = item.get('timestamp')
                answers = item.get('answers')
                logging.info(f'Procesando check con record_id: {record_id}, folio: {folio}, timestamp: {timestamp}')
                futures.append(
                    executor.submit(self.rondines_cache, timestamp, answers, record_id, folio)
                )
            # Esperar a que todos terminen (opcional)
            concurrent.futures.wait(futures)

    def test_number_two(self):
        logging.info('Arranca test #2: Se hace un check posterior a un recorrido que ya tiene mas de una hora de su ultimo check.')
        answers = {
            "681144fb0d423e25b42818d3": [], 
            "681fa6a8d916c74b691e174b": "continuar_siguiente_punto_de_inspecci\u00f3n", 
            "66a83a77cfed7f342775c161": {
                "663e5c57f5b8a7ce8211ed0b": ["Planta Monterrey"], 
                "663e5e68f5b8a7ce8211ed18": ["Almacen"], 
                "663e5d44f5b8a7ce8211ed0f": ["Almac\u00e9n de inventario"], 
                "6762f7b0922cc2a2f57d4044": "687e899c3c2cab8e6307f679", 
                "6763096aa99cee046ba766ad": []
            }
        }
        folio = "4159-10"
        record_id = "68b77e094d3341150d152f21"
        timestamp = 1756853534.814
        self.rondines_cache(timestamp, answers, record_id, folio)