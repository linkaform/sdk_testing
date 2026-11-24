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
# Email sin dominio y username con espacio (no pasan EMAIL_RE ni USERNAME_RE).
USUARIO_EMAIL_INVALIDO = dict(USUARIO_NUEVO, email="usuario.qa@clave10")
USUARIO_USERNAME_INVALIDO = dict(USUARIO_NUEVO, username="usuario qa")
# form_id del form Usuarios (en la cuenta sale de lkm.form_id) y respuesta del guardado.
USUARIOS_FORM = 130001
CREADO_OK = {"status_code": 201}
ESTATUS_CREAR = "crear"
# Opción "ligar a un empleado existente" del modal, sin escribir el nombre.
LIGAR_EMPLEADO_SIN_NOMBRE = {"empleado": "ligar_empleado", "empleado_nombre": ""}
# Buscador de la lista: estatus elegido, texto y total de registros que hay.
ESTATUS_ACTIVADO = "activado"
BUSQUEDA = "usuario.qa"
TOTAL_USUARIOS = 30
POR_PAGINA = 25

# Editar y restaurar contraseña: _id del registro de Usuarios y el Id de
# Usuario de LinkaForm que ya tiene (el workflow de alta lo llena).
REGISTRO_USUARIO = "6a0000000000000000000366"
USER_ID_LKF = 99366
