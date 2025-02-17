# -*- coding: utf-8 -*-
import sys, simplejson, copy, time
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
product_department_1 = 'LAB'



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

    def test_production(self):
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
            "form_id": stock_obj.PRODUCTION_FORM_ID,"geolocation": [],"start_timestamp": 1715787608.475,"end_timestamp": 1715788138.316,
            "answers": {
                stock_obj.f['production_year']: prod_year,
                stock_obj.f['production_week']: prod_week,
                stock_obj.Product.SKU_OBJ_ID: {
                    ###### Catalog Select ######
                    stock_obj.Product.f['product_code']: product_code_1,
                    stock_obj.Product.f['sku_color']: form_stage, # From Stage
                    stock_obj.Product.f['sku_size']: to_stage, # To Stage
                    stock_obj.f['recipe_type']: recipe_type, # Recipe Type
                    stock_obj.f['reicpe_growth_weeks']: growth_weeks, # Grow Weeks
                    stock_obj.Product.f['sku_package']: sku_package,
                    stock_obj.Product.f['sku_percontainer']: per_container,
                    ###### Catalog Details ######
                    stock_obj.Product.f['product_name']: [product_name_1,],
                    stock_obj.f['reicpe_soil_type']: [reicpe_soil_type,], # Grow Weeks
                    stock_obj.Product.f['product_department']:[ product_department_1,]
                },
                stock_obj.f['production_requier_containers']: 100,
                stock_obj.Employee.TEAM_OBJ_ID: {stock_obj.Employee.f['team_name']:'Team 1'},
                stock_obj.WH.WAREHOUSE_OBJ_ID: {stock_obj.WH.f['warehouse']:'Team 1'},
                stock_obj.f['production_left_overs']: 'next_day',
                stock_obj.f['production_order_status']: 'programed',
                # stock_obj.WH.WAREHOUSE_LOCATION_OBJ_ID: {
                #     stock_obj.WH.f['warehouse']: warehouse_from,
                #     stock_obj.WH.f['warehouse_location']: warehouse_from_location
                # },
                # stock_obj.WH.WAREHOUSE_LOCATION_DEST_OBJ_ID: {
                #     stock_obj.WH.f['warehouse_dest']: warehouse_in,
                #     stock_obj.WH.f['warehouse_location_dest']: warehouse_in_location
                # },
                # stock_obj.f['move_group']: [
                #     {
                #         stock_obj.Product.SKU_OBJ_ID: {
                #             stock_obj.Product.f['product_code']: "1000887",
                #             stock_obj.Product.f['product_sku']: "R1000887",
                #             stock_obj.Product.f['product_name']: [
                #                 "VALVULA DE PRUEBA"
                #             ],
                #             stock_obj.Product.f['sku_percontainer']: [
                #                 1
                #             ]
                #         },
                #         stock_obj.f['product_lot']: "TEST002",
                #         stock_obj.f['inv_adjust_grp_status']: "todo",
                #         stock_obj.f['move_group_qty']: 20,
                #     }
                # ],
                #  stock_obj.f['stock_status']: "to_do",
            },
            "folio":None, 
            "properties":{ "device_properties":{"system":"Testing"} }
        }

        print('metadata', simplejson.dumps(metadata, indent=3))
        res_create =  stock_obj.lkf_api.post_forms_answers(metadata)
        print('res_create',res_create)
        assert res_create['status_code'] == 201
        prod_folio = res_create.get('json',{}).get('folio')
        prod_id = res_create.get('json',{}).get('id')
        metadata['folio'] = prod_folio
        metadata['id'] = prod_id
        prod_answers = {
            stock_obj.f['production_per_container_in']: 10,
            stock_obj.f['product_container_type']: 'clean',
            stock_obj.f['production_working_cycle']: 'C1',
            stock_obj.f['production_working_group']: 1,
            stock_obj.f['production_working_group']: 1,
            stock_obj.MEDIA_LOT_OBJ_ID: {
                stock_obj.f['media_name']: 'AG II',
                stock_obj.f['media_lot']: '16 C',
            },
            stock_obj.f['use_clorox']: 'no',
            stock_obj.f['production_group']: [
                {
                    stock_obj.Employee.EMPLOYEE_OBJ_ID:{stock_obj.Employee.f['worker_name']: "Elizabeth Guevara"},
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
                    stock_obj.Employee.EMPLOYEE_OBJ_ID:{stock_obj.Employee.f['worker_name']: "Blanca Guevara"},
                    stock_obj.f['production_containers_in']: 50,
                    stock_obj.f['set_total_produced']: 201,
                    stock_obj.f['set_production_date']: fecha_str,
                    stock_obj.f['time_in']: hours_in,
                    stock_obj.f['set_production_date_out']: fecha_str,
                    stock_obj.f['time_out']: hours_out,
                    stock_obj.f['set_lunch_brake']: 'no',
                    stock_obj.f['production_status']: 'progress',
                },
                {
                    stock_obj.Employee.EMPLOYEE_OBJ_ID:{stock_obj.Employee.f['worker_name']: "Anayeli Bautista"},
                    stock_obj.f['production_containers_in']: 50,
                    stock_obj.f['set_total_produced']: 302,
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
        res = stock_obj.lkf_api.patch_record(metadata, prod_id)
        assert res['status_code'] == 202
        record = stock_obj.get_record_by_id(prod_id)
        print('record_id=',record)
        answers = record['answers']
        production_group = answers[stock_obj.f['production_group']]
        total_produced = answers.get(stock_obj.f['total_produced'])
        assert total_produced == 603
        print('total_produced=',total_produced)

        print('TERMINO ----test_crea_recepcion_materiales---')
    
  #   def test_crea_recepcion_materiales(self):
  #       print('entra aq test_crea_recepcion_materiales')
  #       warehouse_in, warehouse_in_location, warehouse_from, warehouse_from_location = self.get_warehouses()
  #       metadata = {
  #           "form_id": stock_obj.STOCK_IN_ONE_MANY_ONE,"geolocation": [],"start_timestamp": 1715787608.475,"end_timestamp": 1715788138.316,
  #           "answers": {
  #               stock_obj.f['grading_date']: fecha,
  #               stock_obj.WH.WAREHOUSE_LOCATION_OBJ_ID: {
  #                   stock_obj.WH.f['warehouse']: warehouse_from,
  #                   stock_obj.WH.f['warehouse_location']: warehouse_from_location
  #               },
  #               stock_obj.WH.WAREHOUSE_LOCATION_DEST_OBJ_ID: {
  #                   stock_obj.WH.f['warehouse_dest']: warehouse_in,
  #                   stock_obj.WH.f['warehouse_location_dest']: warehouse_in_location
  #               },
  #               stock_obj.f['move_group']: [
  #                   {
  #                       stock_obj.Product.SKU_OBJ_ID: {
  #                           stock_obj.Product.f['product_code']: "1000887",
  #                           stock_obj.Product.f['product_sku']: "R1000887",
  #                           stock_obj.Product.f['product_name']: [
  #                               "VALVULA DE PRUEBA"
  #                           ],
  #                           stock_obj.Product.f['sku_percontainer']: [
  #                               1
  #                           ]
  #                       },
  #                       stock_obj.f['product_lot']: "TEST002",
  #                       stock_obj.f['inv_adjust_grp_status']: "todo",
  #                       stock_obj.f['move_group_qty']: 20,
  #                   }
  #               ],
  #                stock_obj.f['stock_status']: "to_do",
  #           },
  #           "folio":None, 
  #           "properties":{ "device_properties":{"system":"Testing"} }
  #       }
  #       # print('metadata', simplejson.dumps(metadata, indent=3))
  #       res_create =  stock_obj.lkf_api.post_forms_answers(metadata)
  #       print('res_create',res_create)
  #       assert res_create['status_code'] == 201
  #       time.sleep(1)
  #       print('TERMINO ----test_crea_recepcion_materiales---')
    
  # 