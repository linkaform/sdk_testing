# -*- coding: utf-8 -*-
import sys, simplejson, copy, time, random, string
from datetime import datetime ,timedelta

from lkf_modules.stock_lab.items.scripts.Lab.lab_stock_utils import Stock

from account_settings import *


print('starting test')
stock_obj = Stock(settings, use_api=True)

stock_obj.load(module='Product', **stock_obj.kwargs)
stock_obj.load(module='Product', module_class='Warehouse', import_as='WH', **stock_obj.kwargs)
stock_obj.load(module='Employee', **stock_obj.kwargs)


fecha = datetime.now()
prod_year = fecha.isocalendar().year
prod_week = fecha.isocalendar().week
fecha_salida = fecha + timedelta(days=1)
fecha_str = fecha.strftime('%Y-%m-%d')
fecha_salida = fecha_salida.strftime('%Y-%m-%d')
hours_in = '10:00:00'
hours_out = '11:00:00'

product_code_1 = 'LNAFP'
product_name_1 = 'Nandina domestica nana Firepower'
product_department = 'LAB'

product_code_2 = 'LAGBG'
product_name_2 = 'Blue Glow Agave'


letra1 = random.choice(string.ascii_uppercase)
numero1 = random.randint(1, 9)

letra2 = random.choice(string.ascii_uppercase)
numero2 = random.randint(1, 9)

working_group_1 = random.randint(1, 9)
working_cycle_1 = f"{letra1}{numero1}"
working_group_2 = random.randint(1, 9)
working_cycle_2 = f"{letra2}{numero2}"


class TestStock:


    def create_warehouse(self, warehouse_name):
        print('create warehouse')
        print('TODO CREAR WAREHOUSE Y SI EXISTE REGRESAR NOMBRE')
        return warehouse_name

    def create_warehouse_location(self, location_name):
        print('create_warehouse_location')
        print('TODO CREAR LOCATION Y SI EXISTE REGRESAR NOMBRE')
        return location_name

    def get_warehouses(self):
        warehouse_from = self.create_warehouse('Proveedores')
        warehouse_from_location = self.create_warehouse_location('CONDUMEX')
        
        warehouse_in = self.create_warehouse('Almacen Auxiliar')
        warehouse_in_location = self.create_warehouse_location('Refacciones Mantenimiento')
        return warehouse_in, warehouse_in_location, warehouse_from, warehouse_from_location

    def production_metadata(self, product_code, product_name):
        form_stage = 'S2'
        to_stage = 'S2'
        recipe_type = 'Main'
        growth_weeks = '8'
        sku_package = 'Baby Jar'
        per_container = '10'
        reicpe_soil_type = 'NII'
        print('entra aq test_crea_recepcion_materiales')
        warehouse_in, warehouse_in_location, warehouse_from, warehouse_from_location = self.get_warehouses()
        metadata = {
            "form_id": stock_obj.PRODUCTION_FORM_ID, "geolocation": [], "start_timestamp": 1715787608.475, "end_timestamp": 1715788138.316,
            "answers": {
                stock_obj.f['production_year']: prod_year,
                stock_obj.f['production_week']: prod_week,
                stock_obj.Product.SKU_OBJ_ID: {
                    ###### Catalog Select ######
                    stock_obj.Product.f['product_code']: product_code,
                    # From Stage
                    stock_obj.Product.f['sku_color']: form_stage,
                    stock_obj.Product.f['sku_size']: to_stage,  # To Stage
                    stock_obj.f['recipe_type']: recipe_type,  # Recipe Type
                    # Grow Weeks
                    stock_obj.f['reicpe_growth_weeks']: growth_weeks,
                    stock_obj.Product.f['sku_package']: sku_package,
                    stock_obj.Product.f['sku_percontainer']: per_container,
                    ###### Catalog Details ######
                    stock_obj.Product.f['product_name']: [product_name,],
                    # Grow Weeks
                    stock_obj.f['reicpe_soil_type']: [reicpe_soil_type,],
                    stock_obj.Product.f['product_department']: [
                        product_department,]
                },
                stock_obj.f['production_requier_containers']: 80,
                stock_obj.Employee.TEAM_OBJ_ID: {stock_obj.Employee.f['team_name']: 'Team 1'},
                stock_obj.WH.WAREHOUSE_OBJ_ID: {stock_obj.WH.f['warehouse']: 'Team 1'},
                stock_obj.f['production_left_overs']: 'next_day',
                stock_obj.f['production_order_status']: 'programed',
            },
            "folio": None,
            "properties": {"device_properties": {"system": "Testing"}}
        }
        return metadata

    def test_production(self):
        metadata = self.production_metadata(product_code_1, product_name_1)
        print('metadata', simplejson.dumps(metadata, indent=3))
        res_create = stock_obj.lkf_api.post_forms_answers(metadata)
        print('res_create', res_create)
        assert res_create['status_code'] == 201
        stock_obj.prod_folio = res_create.get('json', {}).get('folio')
        stock_obj.prod_id = res_create.get('json', {}).get('id')
        metadata['folio'] = stock_obj.prod_folio
        metadata['id'] = stock_obj.prod_id
        prod_answers = {
            stock_obj.f['production_per_container_in']: 10,
            stock_obj.f['product_container_type']: 'clean',
            stock_obj.f['production_working_cycle']: working_cycle_1,
            stock_obj.f['production_working_group']: working_group_1,
            stock_obj.MEDIA_LOT_OBJ_ID: {
                stock_obj.f['media_name']: 'AG II',
                stock_obj.f['media_lot']: '16 C',
            },
            stock_obj.f['use_clorox']: 'no',
            stock_obj.f['production_group']: [
                {
                    stock_obj.Employee.EMPLOYEE_OBJ_ID: {stock_obj.Employee.f['worker_name']: "Elizabeth Guevara"},
                    stock_obj.f['production_containers_in']: 50,
                    stock_obj.f['set_total_produced']: 10,
                    stock_obj.f['set_production_date']: fecha_str,
                    stock_obj.f['time_in']: hours_in,
                    stock_obj.f['set_production_date_out']: fecha_str,
                    stock_obj.f['time_out']: hours_out,
                    stock_obj.f['set_lunch_brake']: 'no',
                    stock_obj.f['production_status']: 'progress',
                },
                {
                    stock_obj.Employee.EMPLOYEE_OBJ_ID: {stock_obj.Employee.f['worker_name']: "Blanca Guevara"},
                    stock_obj.f['production_containers_in']: 50,
                    stock_obj.f['set_total_produced']: 100,
                    stock_obj.f['set_production_date']: fecha_str,
                    stock_obj.f['time_in']: hours_in,
                    stock_obj.f['set_production_date_out']: fecha_str,
                    stock_obj.f['time_out']: hours_out,
                    stock_obj.f['set_lunch_brake']: 'no',
                    stock_obj.f['production_status']: 'progress',
                },
                {
                    stock_obj.Employee.EMPLOYEE_OBJ_ID: {stock_obj.Employee.f['worker_name']: "Anayeli Bautista"},
                    stock_obj.f['production_containers_in']: 50,
                    stock_obj.f['set_total_produced']: 1000,
                    stock_obj.f['set_production_date']: fecha_str,
                    stock_obj.f['time_in']: hours_in,
                    stock_obj.f['set_production_date_out']: fecha_str,
                    stock_obj.f['time_out']: hours_out,
                    stock_obj.f['set_lunch_brake']: 'no',
                    stock_obj.f['production_status']: 'progress',
                }
            ],
        }
        metadata['answers'].update(prod_answers)
        res = stock_obj.lkf_api.patch_record(metadata, stock_obj.prod_id)
        assert res['status_code'] == 202
        record = stock_obj.get_record_by_id(stock_obj.prod_id)
        print('record_id=', record)
        answers = record['answers']
        production_group = answers[stock_obj.f['production_group']]
        stock_obj.total_produced_1 = answers.get(stock_obj.f['total_produced'])
        assert stock_obj.total_produced_1  == 1110

    def test_production_2(self):
        metadata = self.production_metadata(product_code_2, product_name_2)
        print('metadata', simplejson.dumps(metadata, indent=3))
        res_create = stock_obj.lkf_api.post_forms_answers(metadata)
        print('res_create', res_create)
        assert res_create['status_code'] == 201
        stock_obj.prod_folio_2 = res_create.get('json', {}).get('folio')
        stock_obj.prod_id_2 = res_create.get('json', {}).get('id')
        metadata['folio'] = stock_obj.prod_folio_2 
        metadata['id'] = stock_obj.prod_id_2
        prod_answers = {
            stock_obj.f['production_per_container_in']: 10,
            stock_obj.f['product_container_type']: 'clean',
            stock_obj.f['production_working_cycle']: working_cycle_2,
            stock_obj.f['production_working_group']: working_group_2,
            stock_obj.MEDIA_LOT_OBJ_ID: {
                stock_obj.f['media_name']: 'AG II',
                stock_obj.f['media_lot']: '207 A',
            },
            stock_obj.f['use_clorox']: 'no',
            stock_obj.f['production_group']: [
                {
                    stock_obj.Employee.EMPLOYEE_OBJ_ID: {stock_obj.Employee.f['worker_name']: "Elizabeth Guevara"},
                    stock_obj.f['production_containers_in']: 50,
                    stock_obj.f['set_total_produced']: 20,
                    stock_obj.f['set_production_date']: fecha_str,
                    stock_obj.f['time_in']: hours_in,
                    stock_obj.f['set_production_date_out']: fecha_str,
                    stock_obj.f['time_out']: hours_out,
                    stock_obj.f['set_lunch_brake']: 'no',
                    stock_obj.f['production_status']: 'progress',
                },
                {
                    stock_obj.Employee.EMPLOYEE_OBJ_ID: {stock_obj.Employee.f['worker_name']: "Blanca Guevara"},
                    stock_obj.f['production_containers_in']: 50,
                    stock_obj.f['set_total_produced']: 200,
                    stock_obj.f['set_production_date']: fecha_str,
                    stock_obj.f['time_in']: hours_in,
                    stock_obj.f['set_production_date_out']: fecha_str,
                    stock_obj.f['time_out']: hours_out,
                    stock_obj.f['set_lunch_brake']: 'no',
                    stock_obj.f['production_status']: 'progress',
                },
                {
                    stock_obj.Employee.EMPLOYEE_OBJ_ID: {stock_obj.Employee.f['worker_name']: "Anayeli Bautista"},
                    stock_obj.f['production_containers_in']: 50,
                    stock_obj.f['set_total_produced']: 2000,
                    stock_obj.f['set_production_date']: fecha_str,
                    stock_obj.f['time_in']: hours_in,
                    stock_obj.f['set_production_date_out']: fecha_str,
                    stock_obj.f['time_out']: hours_out,
                    stock_obj.f['set_lunch_brake']: 'no',
                    stock_obj.f['production_status']: 'progress',
                }
            ],
        }
        metadata['answers'].update(prod_answers)
        res = stock_obj.lkf_api.patch_record(metadata, stock_obj.prod_id_2)
        assert res['status_code'] == 202
        record = stock_obj.get_record_by_id(stock_obj.prod_id_2)
        print('record_id=', record)
        answers = record['answers']
        production_group = answers[stock_obj.f['production_group']]
        stock_obj.total_produced_2 = answers.get(stock_obj.f['total_produced'])
        assert stock_obj.total_produced_2  == 2220

    def test_production_3(self):
        metadata = self.production_metadata(product_code_1, product_name_1)
        print('metadata', simplejson.dumps(metadata, indent=3))
        res_create = stock_obj.lkf_api.post_forms_answers(metadata)
        print('res_create', res_create)
        assert res_create['status_code'] == 201
        stock_obj.prod_folio_3 = res_create.get('json', {}).get('folio')
        stock_obj.prod_id_3 = res_create.get('json', {}).get('id')
        metadata['folio'] = stock_obj.prod_folio_3
        metadata['id'] = stock_obj.prod_id_3
        prod_answers = {
            stock_obj.f['production_per_container_in']: 10,
            stock_obj.f['product_container_type']: 'clean',
            stock_obj.f['production_working_cycle']: working_cycle_1,
            stock_obj.f['production_working_group']: working_group_1,
            stock_obj.MEDIA_LOT_OBJ_ID: {
                stock_obj.f['media_name']: 'AG II',
                stock_obj.f['media_lot']: '16 C',
            },
            stock_obj.f['use_clorox']: 'no',
            stock_obj.f['production_group']: [
                {
                    stock_obj.Employee.EMPLOYEE_OBJ_ID: {stock_obj.Employee.f['worker_name']: "Elizabeth Guevara"},
                    stock_obj.f['production_containers_in']: 50,
                    stock_obj.f['set_total_produced']: 30,
                    stock_obj.f['set_production_date']: fecha_str,
                    stock_obj.f['time_in']: hours_in,
                    stock_obj.f['set_production_date_out']: fecha_str,
                    stock_obj.f['time_out']: hours_out,
                    stock_obj.f['set_lunch_brake']: 'no',
                    stock_obj.f['production_status']: 'progress',
                },
                {
                    stock_obj.Employee.EMPLOYEE_OBJ_ID: {stock_obj.Employee.f['worker_name']: "Blanca Guevara"},
                    stock_obj.f['production_containers_in']: 50,
                    stock_obj.f['set_total_produced']: 300,
                    stock_obj.f['set_production_date']: fecha_str,
                    stock_obj.f['time_in']: hours_in,
                    stock_obj.f['set_production_date_out']: fecha_str,
                    stock_obj.f['time_out']: hours_out,
                    stock_obj.f['set_lunch_brake']: 'no',
                    stock_obj.f['production_status']: 'progress',
                },
                {
                    stock_obj.Employee.EMPLOYEE_OBJ_ID: {stock_obj.Employee.f['worker_name']: "Anayeli Bautista"},
                    stock_obj.f['production_containers_in']: 50,
                    stock_obj.f['set_total_produced']: 3000,
                    stock_obj.f['set_production_date']: fecha_str,
                    stock_obj.f['time_in']: hours_in,
                    stock_obj.f['set_production_date_out']: fecha_str,
                    stock_obj.f['time_out']: hours_out,
                    stock_obj.f['set_lunch_brake']: 'no',
                    stock_obj.f['production_status']: 'progress',
                }
            ],
        }
        metadata['answers'].update(prod_answers)
        res = stock_obj.lkf_api.patch_record(metadata, stock_obj.prod_id_3)
        assert res['status_code'] == 202
        record = stock_obj.get_record_by_id(stock_obj.prod_id_3)
        print('record_id=', record)
        answers = record['answers']
        production_group = answers[stock_obj.f['production_group']]
        stock_obj.total_produced_3 = answers.get(stock_obj.f['total_produced'])
        assert stock_obj.total_produced_3 == 3330

    def test_move_stock_in(self):
        mongo_query = {
            "form_id" : stock_obj.MOVE_NEW_PRODUCTION_ID,
            f"answers.{stock_obj.f['production_folio']}": stock_obj.prod_folio
        }
        #se obtiene registro con query de folio de prudccion
        print('mongo_query', mongo_query)
        new_lot_rec = stock_obj.cr.find(mongo_query)
        new_lot_rec = new_lot_rec.next()
        stock_obj.new_lot_id = new_lot_rec.get('_id')
        stock_obj.new_lot_folio = new_lot_rec.get('folio')
        # se selecciona almacen destino y location
        warehouse = self.create_warehouse('Lab A')
        warehouse_in_location = self.create_warehouse_location('10')
        # se arma el set de movimiento
        new_location = {
            stock_obj.WH.WAREHOUSE_DEST_OBJ_ID: {
                stock_obj.WH.f['warehouse'] : warehouse,
                stock_obj.WH.f['warehouse_location']: warehouse_in_location

            },
            stock_obj.f['new_location_racks']: 0 ,
            stock_obj.f['new_location_containers']: 100 
        }
        # se pon dentro de la variable grupo el set1
        new_location_group = [new_location]
        # se anexa al registro completo el grupo
        new_lot_rec['answers'][stock_obj.f['new_location_group']] = new_location_group

        # se edita el registr y se verifica que regrese un 400 debido a mala cantidad
        res = stock_obj.lkf_api.patch_record(new_lot_rec, new_lot_rec['_id'])
        assert res['status_code'] == 400
        warehouse_in_location = self.create_warehouse_location('11')
        # se prepara set 2
        new_location_2 = {
            stock_obj.WH.WAREHOUSE_DEST_OBJ_ID: {
                stock_obj.WH.f['warehouse'] : warehouse,
                stock_obj.WH.f['warehouse_location']: warehouse_in_location
            },
            stock_obj.f['new_location_racks']: 0 ,
            stock_obj.f['new_location_containers']: stock_obj.total_produced_1  - 100 
        }
        # se se anexa al grupo
        new_location_group.append(new_location_2)

        # se acutaliza el registro y se hace patch
        new_lot_rec['answers'][stock_obj.f['new_location_group']] = new_location_group

        res = stock_obj.lkf_api.patch_record(new_lot_rec, stock_obj.new_lot_id )
        print('res=',res)
        assert res['status_code'] == 202
  