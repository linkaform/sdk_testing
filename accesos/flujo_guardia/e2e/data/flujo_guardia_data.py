# coding: utf-8

"""
Datos de prueba para el flujo completo de guardia: checkin/checkout de
turno y creación de áreas nuevas (usadas después para configurar un rondín).
"""

LOCATION = "Planta Monterrey"
AREA = "Caseta Principal"

FOTOGRAFIA_TURNO = [{
    "file_name": "evidencia.jpeg",
    "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/116852/660459dde2b2d414bce9cf8f/6962b6d8c8deee17fb7843f8.jpeg",
}]

# Punto base (30.2248202,-97.6221229) + 3 puntos movidos ~5-10m mediante
# pequeños offsets de lat/lng (a esta latitud, ~0.0000629 grados lat y
# ~0.0000727 grados lng equivalen aprox. a 7 metros cada uno).
GEOLOCATION_BASE = (30.2248202, -97.6221229)

AREAS_NUEVAS = [
    {
        "foto_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/71202/60b81349bde5588acca320e1/6a602f2b70408ab2c466145d.png",
        "lat_offset": 0.0,
        "lng_offset": 0.0,
    },
    {
        "foto_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/71202/60b81349bde5588acca320e1/6a602f2a70408ab2c466145c.png",
        "lat_offset": 0.0000629,
        "lng_offset": 0.0,
    },
    {
        "foto_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/71202/60b81349bde5588acca320e1/6a602f2c70408ab2c466145e.png",
        "lat_offset": 0.0,
        "lng_offset": 0.0000727,
    },
    {
        "foto_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/71202/60b81349bde5588acca320e1/6a602f2870408ab2c466145b.png",
        "lat_offset": 0.0000629,
        "lng_offset": 0.0000727,
    },
]
