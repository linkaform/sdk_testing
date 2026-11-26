# coding: utf-8

"""Usuarios: dar de alta un usuario (create_user), la lista (list_users) y
editarlo (update_user) y restaurar su contraseña (reset_password), sin
tocar la cuenta.
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
    ESTATUS_ACTIVADO,
    BUSQUEDA,
    TOTAL_USUARIOS,
    POR_PAGINA,
    REGISTRO_USUARIO,
    USER_ID_LKF,
    CAMBIO_TELEFONO,
    RECHAZO_LKF,
    CAMBIO_TELEFONO_Y_ROL,
    ACTUALIZADO_LKF,
    EDITADO_OK,
    ESTATUS_CREADO,
    ESTATUS_RESTAURAR,
)

pytestmark = pytest.mark.back("sanic")

C10_TRIGGERS = ["_build_match", "_valid_language", "_valid_timezone", "create_user", "list_users", "reset_password", "update_user"]


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


@pytest.mark.unit
@pytest.mark.target("list_users", "_build_match")
def test_la_lista_de_usuarios_filtra_por_estatus_y_por_texto(usuarios_admin, mocker):
    """
    TB-365: la lista de Usuarios filtra por los estatus elegidos y busca el
    texto del buscador en nombre, username y email sin importar mayúsculas.
    El total y las páginas salen del conteo con ese mismo filtro.
    """
    admin = usuarios_admin
    f = admin.user_fields
    mocker.patch.object(type(admin), "usuarios_form", new_callable=mocker.PropertyMock, return_value=USUARIOS_FORM)
    cr = mocker.MagicMock()
    cr.count_documents.return_value = TOTAL_USUARIOS
    cr.find.return_value.sort.return_value.skip.return_value.limit.return_value = []
    mocker.patch.object(admin, "cr", cr, create=True)

    res = admin.list_users(limit=POR_PAGINA, skip=0, status=[ESTATUS_ACTIVADO], search=BUSQUEDA)

    match = cr.count_documents.call_args.args[0]
    assert match["form_id"] == USUARIOS_FORM
    assert match[f"answers.{f['status']}"] == {"$in": [ESTATUS_ACTIVADO]}
    buscados = [campo for condicion in match["$or"] for campo in condicion]
    assert buscados == [f"answers.{f[k]}" for k in ("name", "username", "email")]
    assert all(c[campo]["$options"] == "i" for c in match["$or"] for campo in c)
    assert (res["total_records"], res["total_pages"]) == (TOTAL_USUARIOS, 2)


def usuario_guardado(admin, mocker, estatus):
    """Simula el registro de Usuarios que se edita, con su Id de Usuario de
    LinkaForm y el estatus dado; regresa los mocks de los dos guardados."""
    f = admin.user_fields
    mocker.patch.object(type(admin), "usuarios_form", new_callable=mocker.PropertyMock, return_value=USUARIOS_FORM)
    cr = mocker.MagicMock()
    cr.find_one.return_value = {
        "_id": REGISTRO_USUARIO,
        "form_id": USUARIOS_FORM,
        "answers": {f["user_id"]: [USER_ID_LKF], f["status"]: estatus},
    }
    mocker.patch.object(admin, "cr", cr, create=True)
    return {
        "linkaform": mocker.patch.object(admin, "_patch_lkf_user"),
        "registro": mocker.patch.object(admin.lkf_api, "patch_multi_record"),
    }


@pytest.mark.unit
@pytest.mark.target("update_user")
def test_editar_un_usuario_sin_cambios_da_error_y_no_toca_linkaform(usuarios_admin, mocker):
    """
    TB-366: si el panel de edición se guarda sin cambiar nada, update_user
    debe responder "No hay cambios que guardar" sin actualizar el usuario de
    LinkaForm ni el registro de Usuarios.
    """
    admin = usuarios_admin
    guardados = usuario_guardado(admin, mocker, ESTATUS_ACTIVADO)

    with pytest.raises(Exception, match="No hay cambios"):
        admin.update_user(record_id=REGISTRO_USUARIO)

    guardados["linkaform"].assert_not_called()
    guardados["registro"].assert_not_called()


@pytest.mark.unit
@pytest.mark.target("update_user")
def test_si_linkaform_rechaza_la_edicion_no_se_guarda_el_registro(usuarios_admin, mocker):
    """
    TB-367: update_user actualiza primero el usuario de LinkaForm y solo si
    responde bien guarda el registro de Usuarios. Si LinkaForm rechaza el
    cambio, debe responder error sin guardar el registro, para que los dos no
    queden con datos distintos.
    """
    admin = usuarios_admin
    guardados = usuario_guardado(admin, mocker, ESTATUS_ACTIVADO)
    guardados["linkaform"].return_value = dict(RECHAZO_LKF)

    with pytest.raises(Exception, match="No se pudo actualizar el usuario en LinkaForm"):
        admin.update_user(record_id=REGISTRO_USUARIO, **CAMBIO_TELEFONO)

    guardados["linkaform"].assert_called_once()
    guardados["registro"].assert_not_called()


@pytest.mark.unit
@pytest.mark.target("update_user")
def test_editar_un_usuario_guarda_solo_los_campos_que_cambiaron(usuarios_admin, mocker):
    """
    TB-368: al cambiar el teléfono y el rol, update_user manda a LinkaForm
    solo esos dos campos con sus nombres de allá (phone y position) y guarda
    en el registro solo esos mismos campos. Si mandara los demás vacíos,
    borraría el nombre o el email del usuario.
    """
    admin = usuarios_admin
    f = admin.user_fields
    guardados = usuario_guardado(admin, mocker, ESTATUS_ACTIVADO)
    guardados["linkaform"].return_value = dict(ACTUALIZADO_LKF)
    guardados["registro"].return_value = dict(EDITADO_OK)

    res = admin.update_user(record_id=REGISTRO_USUARIO, **CAMBIO_TELEFONO_Y_ROL)

    assert guardados["linkaform"].call_args.args == (
        USER_ID_LKF, {"phone": CAMBIO_TELEFONO_Y_ROL["phone"], "position": CAMBIO_TELEFONO_Y_ROL["role"]},
    )
    assert guardados["registro"].call_args.kwargs["answers"] == {
        f["phone"]: CAMBIO_TELEFONO_Y_ROL["phone"],
        f["role"]: CAMBIO_TELEFONO_Y_ROL["role"],
    }
    assert guardados["registro"].call_args.kwargs["record_id"] == [REGISTRO_USUARIO]
    assert res == {"updated": ["phone", "role"]}


@pytest.mark.unit
@pytest.mark.target("reset_password")
def test_restaurar_la_contrasena_de_un_usuario_no_activado_da_error(usuarios_admin, mocker):
    """
    TB-369: solo se restaura la contraseña de un usuario que ya activó su
    cuenta. Si todavía está en "creado", su liga de activación sigue vigente:
    reset_password debe responder error sin generar otra liga.
    """
    admin = usuarios_admin
    guardados = usuario_guardado(admin, mocker, ESTATUS_CREADO)

    with pytest.raises(Exception, match="no admite esta acci"):
        admin.reset_password(record_id=REGISTRO_USUARIO)

    guardados["registro"].assert_not_called()


@pytest.mark.unit
@pytest.mark.target("reset_password")
def test_restaurar_la_contrasena_genera_una_liga_nueva_y_deja_el_usuario_en_restaurar(usuarios_admin, mocker):
    """
    TB-370: para un usuario activado, reset_password guarda un token nuevo,
    la liga para fijar contraseña con ese token, el record_id y la cuenta, y
    el estatus "restaurar", que es lo que dispara el correo con la liga.
    """
    admin = usuarios_admin
    f = admin.user_fields
    guardados = usuario_guardado(admin, mocker, ESTATUS_ACTIVADO)
    guardados["registro"].return_value = dict(EDITADO_OK)

    res = admin.reset_password(record_id=REGISTRO_USUARIO)

    assert res == {"status": ESTATUS_RESTAURAR}
    answers = guardados["registro"].call_args.kwargs["answers"]
    token = answers[f["token"]]
    assert token, "No se generó el token"
    liga = answers[f["link"]]
    assert f"record_id={REGISTRO_USUARIO}" in liga
    assert f"user={admin.user['parent_id']}" in liga
    assert f"token={token}" in liga
    assert answers[f["status"]] == ESTATUS_RESTAURAR
