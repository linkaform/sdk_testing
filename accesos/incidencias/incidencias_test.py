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

class TestAccesos:

    def test_number_one(self):
        logging.info('Arranca test #1: Se crea una incidencia con toda la informacion rellenada')
        
        data_incidence = {
            "incidencia": "Estafa o intento de estafa", 
            "responsable_que_recibe": "", 
            "reporta_incidencia": "Emiliano Zapata", 
            "color_cabello": "", 
            "nombre_completo_persona_extraviada": "", 
            "color": "", 
            "notificacion_incidencia": "no", 
            "num_doc_identidad": "", 
            "pertenencias_sustraidas": "", 
            "dano_incidencia": "", 
            "personas_involucradas_incidencia": [
                {
                    "retenido": "no", 
                    "rol": "testigo", 
                    "grupo_etario": "adultez temprana", 
                    "nombre_completo": "Paco Soto", 
                    "sexo": "masculino", 
                    "atencion_medica": "no", 
                    "comentarios": "comentariopersonainvolucrada"
                }
            ], 
            "prioridad_incidencia": "Moderada", 
            "area_incidencia": "Recursos el\u00e9ctricos", 
            "info_coincide_con_videos": "", 
            "afectacion_patrimonial_incidencia": [
                {
                    "duracion_estimada": "2", 
                    "tipo_afectacion": "Da\u00f1o a infraestructura", 
                    "monto_estimado": "10000"
                }
            ], 
            "valor_estimado": "", 
            "responsable_que_entrega": "", 
            "telefono": "", 
            "tipo_dano_incidencia": "", 
            "categoria": "Fraude y extorsi\u00f3n", 
            "tags": ["tag1"], 
            "estatura_aproximada": 0, 
            "marca": "", 
            "comentario_incidencia": "comentariossss", 
            "nombre_completo_responsable": "", 
            "modelo": "", 
            "documento_incidencia": [
                {
                    "file_name": "documento area qr 1244 10.pdf", 
                    "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/116852/660459dde2b2d414bce9cf8f/68b73b7b1c07140f160264ef.pdf"
                }
            ], 
            "acciones_tomadas_incidencia": [
                {
                    "llamo_a_policia": "s\u00ed", 
                    "acciones_tomadas": "acciontomada1", 
                    "responsable": "Soto", 
                    "autoridad": "Bomberos", 
                    "numero_folio_referencia": "3213123"
                }
            ], 
            "datos_deposito_incidencia": [], 
            "edad": 0, 
            "incidente": "Estafa o intento de estafa", 
            "tipo": "", 
            "fecha_hora_incidencia": "2025-09-02 12:44:00", 
            "placas": "", 
            "sub_categoria": "", 
            "descripcion_fisica_vestimenta": "", 
            "seguimientos_incidencia": [
                {
                    "incidencia_evidencia_solucion": [], 
                    "incidencia_documento_solucion": [], 
                    "incidencia_personas_involucradas": "Juan Soto", 
                    "accion_correctiva_incidencia": "accionrealizada", 
                    "tiempo_transcurrido": "8 hora(s), 16 minuto(s).", 
                    "fecha_inicio_seg": "2025-09-02 21:00:00"
                }
            ], 
            "ubicacion_incidencia": "Planta Monterrey", 
            "color_piel": "", 
            "evidencia_incidencia": [
                {
                    "file_name": "evidencia.jpeg", 
                    "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/116852/660459dde2b2d414bce9cf8f/68b73b464a4d23ba929ab227.jpeg"
                }
            ], 
            "parentesco": ""
        }

        response = accesos_obj.create_incidence(data_incidence)
        assert response['status_code'] in [200, 201, 202], 'No se creo correctamente la incidencia'
        if response['status_code'] not in [200, 201, 202]:
            print('==========> error response:', response)
            
    def test_number_two(self):
        pass