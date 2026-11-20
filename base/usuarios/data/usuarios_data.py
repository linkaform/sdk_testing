# coding: utf-8

"""
Datos de prueba para la sección Usuarios (Nuevo usuario y lista; script
users_sdk.py de Sanic).
"""

# Alta con lo que manda el modal Nuevo usuario (UserFormModal.tsx).
USUARIO_NUEVO = {
    "name": "Usuario prueba QA",
    "username": "usuario.qa",
    "email": "usuario.qa@clave10.com",
    "phone": "8112345678",
    "role": "Guardia",
}
# El mismo alta sin el rol (campo obligatorio).
USUARIO_SIN_ROL = dict(USUARIO_NUEVO, role="")
