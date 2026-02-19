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



LOCATIONS = {"ubicacion":"Planta Guadalajara","option":"get_catalog_areas","script_name":"rondines.py"}