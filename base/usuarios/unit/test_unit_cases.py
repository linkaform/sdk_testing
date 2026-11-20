# coding: utf-8

"""Usuarios: dar de alta un usuario (create_user) y la lista (list_users),
sin tocar la cuenta.
Notion: TB-361 a TB-370.

Unitarios principales de la seccion (maximo 10) y sus C10_TRIGGERS:
./lkf test corre este archivo cuando cambia alguna funcion de C10_TRIGGERS.
La seccion solo existe en Sanic: los tests llevan back("sanic") y en addons
salen SKIPPED.
"""

import pytest

from ..data.usuarios_data import (
    USUARIO_SIN_ROL,
    USUARIO_EMAIL_INVALIDO,
    USUARIO_USERNAME_INVALIDO,
    USUARIO_NUEVO,
    USUARIOS_FORM,
    CREADO_OK,
    ESTATUS_CREAR,
    LIGAR_EMPLEADO_SIN_NOMBRE,
)

pytestmark = pytest.mark.back("sanic")

C10_TRIGGERS = ["_valid_language", "_valid_timezone", "create_user"]


@pytest.mark.unit
@pytest.mark.target("create_user")
def test_dar_de_alta_un_usuario_sin_un_dato_obligatorio_da_error_y_no_guarda(usuarios_admin, mocker):
    """
    TB-361: nombre, username, email, teléfono y rol son obligatorios para
    crear el usuario en LinkaForm. Si falta uno (aquí el rol), create_user
    debe responder error sin guardar el registro de Usuarios; si lo guardara,
    el workflow de creación fallaría sin avisar al administrador.
    """
    admin = usuarios_admin
    guardar = mocker.patch.object(admin.lkf_api, "post_forms_answers")

    with pytest.raises(Exception, match="son obligatorios"):
        admin.create_user(**USUARIO_SIN_ROL)

    guardar.assert_not_called()


@pytest.mark.unit
@pytest.mark.target("create_user")
def test_dar_de_alta_un_usuario_con_email_o_username_invalido_da_error(usuarios_admin, mocker):
    """
    TB-362: el email recibe la liga de activación y el username se usa sin
    codificar en la URL de LinkaForm. Un email mal formado o un username con
    espacios debe responder error sin guardar el registro.
    """
    admin = usuarios_admin
    guardar = mocker.patch.object(admin.lkf_api, "post_forms_answers")

    with pytest.raises(Exception, match="email no es v"):
        admin.create_user(**USUARIO_EMAIL_INVALIDO)
    with pytest.raises(Exception, match="username solo puede llevar"):
        admin.create_user(**USUARIO_USERNAME_INVALIDO)

    guardar.assert_not_called()


@pytest.mark.unit
@pytest.mark.target("create_user", "_valid_timezone", "_valid_language")
def test_un_usuario_nuevo_se_guarda_en_estatus_crear_con_zona_e_idioma_por_defecto(usuarios_admin, mocker):
    """
    TB-363: el alta guarda el registro de Usuarios en estatus "crear", que es
    lo que dispara el workflow que crea el usuario en LinkaForm. Si el modal no
    manda zona horaria ni idioma, se guardan los de por defecto; sin ellos el
    usuario nace con la hora o el idioma equivocados.
    """
    admin = usuarios_admin
    f = admin.user_fields
    mocker.patch.object(type(admin), "usuarios_form", new_callable=mocker.PropertyMock, return_value=USUARIOS_FORM)
    mocker.patch.object(admin.lkf_api, "get_metadata", return_value={})
    guardar = mocker.patch.object(admin.lkf_api, "post_forms_answers", return_value=dict(CREADO_OK))

    res = admin.create_user(**USUARIO_NUEVO)

    assert res == {"created": True}
    answers = guardar.call_args.args[0]["answers"]
    assert answers[f["status"]] == ESTATUS_CREAR
    assert answers[f["username"]] == USUARIO_NUEVO["username"]
    assert answers[f["timezone"]] == admin.TIMEZONE_DEFAULT
    assert answers[f["language"]] == admin.LANGUAGE_DEFAULT


@pytest.mark.unit
@pytest.mark.target("create_user")
def test_ligar_un_empleado_sin_su_nombre_da_error(usuarios_admin, mocker):
    """
    TB-364: al ligar el usuario a un empleado existente, el workflow lo busca
    por su nombre completo. Si se elige "ligar" sin escribir el nombre,
    create_user debe responder error sin guardar el registro.
    """
    admin = usuarios_admin
    guardar = mocker.patch.object(admin.lkf_api, "post_forms_answers")

    with pytest.raises(Exception, match="nombre completo del empleado"):
        admin.create_user(**USUARIO_NUEVO, **LIGAR_EMPLEADO_SIN_NOMBRE)

    guardar.assert_not_called()
