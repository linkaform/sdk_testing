# coding: utf-8

"""Contratistas: reglas de negocio del back de Sanic (F0-16), sin tocar la
cuenta. Notion: TB-401 a TB-410.

Cubre lo que decide estatus y porcentajes en las pantallas de contratistas:
periodos y % del motor de cumplimiento (ME-15), qué documento cubre a qué
cliente (MX-02), estatus de contrato (ME-14) y de documento (ME-06-B),
subcontratación (R-03), validación del registro público (RG-01), similitud
del mapeo (ME-13) y resultado de una sesión de capacitación (CF-04-B).

Unitarios principales de la sección (máximo 10) y sus C10_TRIGGERS:
./lkf test corre este archivo cuando cambia alguna función de C10_TRIGGERS.
Contratistas solo existe en Sanic: los tests llevan back("sanic") y en
addons salen SKIPPED. Las funciones sueltas de los módulos se importan
dentro de cada test porque en addons esos módulos no existen.
"""

from datetime import date

import pytest
import simplejson

from ..data.contratistas_data import (
    HOY,
    CLIENTE,
    OTRO_CLIENTE,
    CONTRATISTA,
    SUBCONTRATISTA,
    REQUERIMIENTO_ID,
    RELACION_PADRE_ID,
    REQ_BIMESTRAL_ICSOE,
    REQ_MENSUAL,
    REQ_VIGENCIA,
    REGISTRO_MORAL,
    CATALOGO_MAESTRO,
)

pytestmark = pytest.mark.back("sanic")

C10_TRIGGERS = [
    "_cum_estado", "_doc_estatus", "_map_mejor", "_reg_validar", "_rel_cadena", "_rel_validar_subcontratacion",
    "_ses_resultado", "ctr_calcular_estatus", "normalizar_dominio", "periodos", "porcentaje", "similitud",
]


def mensaje(exc):
    """Texto del error que lanza LKFException (JSON con los acentos escapados)."""
    try:
        return " ".join(simplejson.loads(str(exc.value))["exception"]["msg"])
    except (ValueError, KeyError, TypeError):
        return str(exc.value)


def hoy_fijo(acc, mocker):
    mocker.patch.object(acc, "_ctr_hoy", return_value=HOY)


# ------------------------------------------------------------ motor ME-15


@pytest.mark.unit
@pytest.mark.target("periodos")
def test_periodos_de_un_requerimiento_salen_del_anio_con_su_fecha_de_vencimiento():
    """
    TB-401: el motor crea una fila de cumplimiento por periodo. Un bimestral
    con meses de entrega (ICSOE: ene, may, sep) vence el día 17 del primer
    mes de entrega después del periodo; un mensual con día límite 10 vence el
    10 del mes siguiente; solo salen los periodos que tocan la vigencia del
    contrato, y un requerimiento por vigencia es una sola fila "unico".
    Si falla, la matriz pide documentos de periodos que no aplican o con la
    fecha límite equivocada.
    """
    from lkf_addons.accesos.contratistas_cumplimiento import periodos

    bim = periodos(REQ_BIMESTRAL_ICSOE, 2026, date(2026, 3, 1), date(2026, 8, 31))
    assert [p["clave"] for p in bim] == ["2026-B2", "2026-B3", "2026-B4"]
    assert [p["vence"] for p in bim] == ["2026-05-17", "2026-09-17", "2026-09-17"]
    assert bim[0]["inicio"] == "2026-03-01" and bim[0]["fin"] == "2026-04-30"

    dic = periodos(REQ_BIMESTRAL_ICSOE, 2026, date(2026, 11, 1), date(2026, 12, 31))
    assert dic[-1]["clave"] == "2026-B6" and dic[-1]["vence"] == "2027-01-17", \
        "El último bimestre debe vencer en el primer mes de entrega del año siguiente"

    men = periodos(REQ_MENSUAL, 2026, date(2026, 1, 15), date(2026, 2, 10))
    assert [(p["clave"], p["vence"]) for p in men] == [("2026-01", "2026-02-10"), ("2026-02", "2026-03-10")]

    unico = periodos(REQ_VIGENCIA, 2026, date(2026, 1, 1), date(2026, 12, 31))
    assert [p["clave"] for p in unico] == ["unico"]


@pytest.mark.unit
@pytest.mark.target("porcentaje")
def test_porcentaje_de_cumplimiento_solo_cuenta_lo_que_ya_es_exigible():
    """
    TB-402: el % de cumplimiento de contrato y relación cuenta Cumplido y En
    ceros como cumplidos y deja fuera No aplica, Por transcurrir y En plazo
    (todavía no se pueden exigir). Sin nada exigible es 100 %. Si falla, un
    contratista al día sale con % bajo o uno atrasado sale completo.
    """
    from lkf_addons.accesos.contratistas_cumplimiento import porcentaje

    assert porcentaje(["Cumplido", "En ceros", "Por subir", "Rechazado"]) == 50
    assert porcentaje(["Cumplido", "No aplica", "Por transcurrir", "En plazo"]) == 100
    assert porcentaje(["Por revisar", "Vencido", "Cumplido"]) == 33
    assert porcentaje(["No aplica", "En plazo"]) == 100
    assert porcentaje([]) == 100


def fila_empresa(periodo):
    return {
        "periodo": periodo,
        "sujeto": {"tipo": "Empresa", "empresa": {"id": CONTRATISTA}},
        "requerimiento": {"id": REQUERIMIENTO_ID},
    }


def documento(acc, compartido_con, decisiones=None, vigencia_fin=None):
    """Documento del contratista para REQUERIMIENTO_ID, con su decisión por cliente."""
    f = acc.ctr_f["documentos_de_cumplimiento"]
    a = {
        f["requerimiento_id"]: REQUERIMIENTO_ID,
        f["compartido_con"]: [{f["compartido_con_id"]: c} for c in compartido_con],
        f["aprobaciones"]: [{f["aprobacion_cliente_id"]: c, f["aprobacion_decision"]: d}
                            for c, d in (decisiones or {}).items()],
    }
    if vigencia_fin:
        a[f["vigencia_fin"]] = vigencia_fin
    return {"_id": "doc", "answers": a}


@pytest.mark.unit
@pytest.mark.target("_cum_estado")
def test_un_documento_solo_cubre_al_cliente_con_quien_se_compartio(accesos_no_api, mocker):
    """
    TB-403 (MX-02): el mismo documento puede estar compartido con varios
    clientes y cada uno decide por su cuenta. Para el cliente con quien NO se
    compartió la fila sigue sin documento (Por subir si ya venció, En plazo
    si no); para el que sí, cuenta como entregado. Si falla, un cliente ve
    cumplido algo que el contratista nunca le mandó.
    """
    acc = accesos_no_api
    hoy_fijo(acc, mocker)
    vencida = fila_empresa({"clave": "unico", "inicio": "2026-01-01", "fin": "2026-12-31", "vence": "2026-01-01"})
    a_tiempo = fila_empresa({"clave": "unico", "inicio": "2026-01-01", "fin": "2026-12-31", "vence": "2026-07-01"})
    cache = {f"docs:{CONTRATISTA}": [documento(acc, [CLIENTE], {CLIENTE: "aprobado"})]}

    assert acc._cum_estado(vencida, CLIENTE, cache)[0] == "Cumplido"
    estado, doc = acc._cum_estado(vencida, OTRO_CLIENTE, cache)
    assert (estado, doc) == ("Por subir", None), "El documento cubrió a un cliente con quien no se compartió"
    assert acc._cum_estado(a_tiempo, OTRO_CLIENTE, cache)[0] == "En plazo"

    futuro = fila_empresa({"clave": "2026-B5", "inicio": "2026-09-01", "fin": "2026-10-31", "vence": "2027-01-17"})
    assert acc._cum_estado(futuro, CLIENTE, cache)[0] == "Por transcurrir"


@pytest.mark.unit
@pytest.mark.target("_cum_estado")
@pytest.mark.parametrize("decision, vigencia_fin, esperado", [
    ("rechazado", None, "Rechazado"),
    ("aprobado", "2026-06-14", "Vencido"),
    ("aprobado", "2026-12-31", "Cumplido"),
    ("pendiente", None, "Por revisar"),
])
def test_estado_de_la_fila_sale_de_la_decision_de_ese_cliente(accesos_no_api, mocker, decision, vigencia_fin, esperado):
    """
    TB-404: con el documento ya entregado, el estado de la fila es la
    decisión de ESE cliente: rechazado = Rechazado, aprobado con vigencia
    pasada = Vencido, aprobado vigente = Cumplido, sin decidir = Por revisar.
    Lo que haya decidido otro cliente no cuenta. Si falla, la matriz de
    cumplimiento muestra el estado de otro cliente.
    """
    acc = accesos_no_api
    hoy_fijo(acc, mocker)
    fila = fila_empresa({"clave": "unico", "inicio": "2026-01-01", "fin": "2026-12-31", "vence": "2026-01-01"})
    doc = documento(acc, [CLIENTE, OTRO_CLIENTE], {OTRO_CLIENTE: "aprobado", CLIENTE: decision}, vigencia_fin)

    assert acc._cum_estado(fila, CLIENTE, {f"docs:{CONTRATISTA}": [doc]})[0] == esperado


# ------------------------------------------------------------- contratos


@pytest.mark.unit
@pytest.mark.target("ctr_calcular_estatus")
@pytest.mark.parametrize("manual, fin, limitantes_pendientes, esperado", [
    ("pausado", "2026-01-01", True, "Pausado"),       # el manual gana a todo
    ("cancelado", None, False, "Cancelado"),
    (None, "2026-06-14", False, "Vencido"),           # vencido gana a documentación
    (None, "2026-06-20", True, "En documentación"),   # documentación gana a por vencer
    (None, "2026-07-15", False, "Por vencer"),        # 30 días o menos
    (None, "2026-07-16", False, "Activo"),
])
def test_estatus_del_contrato_sigue_el_orden_de_la_spec(accesos_no_api, mocker, manual, fin, limitantes_pendientes, esperado):
    """
    TB-405 (ME-14): el back calcula el estatus del contrato en este orden:
    manual (Pausado/Cancelado) > Vencido > En documentación (algún
    requerimiento limitante sin cumplir) > Por vencer (30 días o menos) >
    Activo. Si falla, la lista de contratos filtra mal y un contrato con
    documentos pendientes se ve Activo.
    """
    acc = accesos_no_api
    hoy_fijo(acc, mocker)
    mocker.patch.object(acc, "_ctr_limitantes_pendientes", return_value=limitantes_pendientes)
    f = acc.ctr_f["contratos_de_servicio"]
    a = {f["estatus_manual"]: manual, f["fin"]: fin}

    assert acc.ctr_calcular_estatus(a, "contrato") == esperado


# ------------------------------------------------------------ documentos


@pytest.mark.unit
@pytest.mark.target("_doc_estatus")
@pytest.mark.parametrize("decisiones, vigencia_fin, esperado", [
    (["aprobado", "rechazado", "aprobado"], None, "Rechazado"),  # basta un rechazo
    (["aprobado", "aprobado"], "2026-12-31", "Aceptado"),         # todos aprobaron
    (["aprobado", "aprobado"], "2026-06-14", "Vencido"),          # vencido gana a aceptado
    (["aprobado", "pendiente"], None, "Por revisar"),             # "1 de 2 aprobaron"
    ([], None, "Por revisar"),
])
def test_estatus_del_documento_exige_que_aprueben_todos_los_clientes(accesos_no_api, mocker, decisiones, vigencia_fin, esperado):
    """
    TB-406 (ME-06-B / MX-02): el estatus global de un documento compartido
    con varios clientes es Rechazado si cualquiera rechazó, Aceptado solo si
    todos aprobaron (Vencido si su vigencia ya pasó) y si no, Por revisar.
    Si falla, un documento que solo aprobó un cliente se ve Aceptado.
    """
    acc = accesos_no_api
    hoy_fijo(acc, mocker)
    f = acc.ctr_f["documentos_de_cumplimiento"]
    a = {f["aprobaciones"]: [{f["aprobacion_decision"]: d} for d in decisiones], f["vigencia_fin"]: vigencia_fin}

    assert acc._doc_estatus(a) == esperado


# ------------------------------------------------------ subcontratación R-03


def relacion_padre(acc, estatus="activo", nivel=1, cliente=CLIENTE, contratista=CONTRATISTA):
    f = acc.ctr_f["relaciones_entre_empresas"]
    return {"_id": RELACION_PADRE_ID, "answers": {
        f["estatus"]: estatus, f["nivel"]: nivel, f["cliente_id"]: cliente, f["contratista_id"]: contratista}}


@pytest.mark.unit
@pytest.mark.target("_rel_validar_subcontratacion", "_rel_cadena")
@pytest.mark.parametrize("caso, padre_kw, cliente, contratista, contrato_vigente, error", [
    ("ok", {}, CONTRATISTA, SUBCONTRATISTA, True, None),
    ("padre inactivo", {"estatus": "inactivo"}, CONTRATISTA, SUBCONTRATISTA, True, "padre est"),
    ("cliente equivocado", {}, OTRO_CLIENTE, SUBCONTRATISTA, True, "debe ser el contratista"),
    ("nivel máximo", {"nivel": 3}, CONTRATISTA, SUBCONTRATISTA, True, "nivel m"),
    ("ciclo", {}, CONTRATISTA, CLIENTE, True, "ciclo"),
    ("sin contrato que lo permita", {}, CONTRATISTA, SUBCONTRATISTA, False, "permite subcontrataci"),
])
def test_subcontratacion_valida_padre_ciclos_nivel_y_contrato(accesos_no_api, mocker, caso, padre_kw, cliente,
                                                               contratista, contrato_vigente, error):
    """
    TB-407 (R-03): una subcontratación solo se crea si la relación padre está
    activa, el cliente de la hija es el contratista del padre, no se pasa del
    nivel 3, el subcontratista no está ya en la cadena (ciclo) y algún
    contrato vigente del padre permite subcontratar. Si pasa, regresa el
    nivel de la hija. Si falla, se arman cadenas circulares o sin contrato
    que las respalde.
    """
    acc = accesos_no_api
    mocker.patch.object(acc, "CONTRATOS_FORM", 1)
    mocker.patch.object(acc, "_ctr_find", return_value=[{"_id": "c1", "answers": {}}])
    mocker.patch.object(acc, "ctr_calcular_estatus", return_value="Activo" if contrato_vigente else "Pausado")
    padre = relacion_padre(acc, **padre_kw)

    if error is None:
        assert acc._rel_validar_subcontratacion(padre, cliente, contratista) == 2
        return
    with pytest.raises(Exception) as exc:
        acc._rel_validar_subcontratacion(padre, cliente, contratista)
    assert error in mensaje(exc), f"{caso}: {mensaje(exc)}"


# ------------------------------------------------------ registro público RG-01


@pytest.mark.unit
@pytest.mark.target("_reg_validar", "normalizar_dominio")
def test_registro_normaliza_datos_validos_y_junta_todos_los_errores(accesos_no_api):
    """
    TB-408 (RG-01): el registro público normaliza lo que captura el usuario
    (RFC en mayúsculas sin espacios, correo en minúsculas, teléfono a 10
    dígitos sin el 52, dominio sin acentos ni ñ y con guiones) y, si hay
    errores, los regresa todos juntos: RFC inválido, contraseña débil,
    dominio reservado, contraseñas distintas, términos sin aceptar. Si falla,
    se crean empresas con RFC o dominio basura o el usuario corrige un error
    a la vez.
    """
    acc = accesos_no_api

    v = acc._reg_validar(dict(REGISTRO_MORAL))
    assert v["rfc"] == "LIN010203AB1"
    assert v["email"] == "contacto@limpieza.mx"
    assert v["tel"] == "8112345678"
    assert v["dominio"] == "limpieza-industrial-norte"
    assert v["razon"] == "Limpieza Industrial del Norte"
    assert v["tipo"] == "Moral"

    malo = {**REGISTRO_MORAL, "rfc": "LIN019999AB1", "password": "debil", "password2": "otra",
            "dominio": "Admin", "terminos": False}
    with pytest.raises(Exception) as exc:
        acc._reg_validar(malo)
    texto = mensaje(exc)
    for parte in ("RFC", "contrase", "reservado", "no coinciden", "rminos"):
        assert parte in texto, f"Falta el error de '{parte}': {texto}"


# ------------------------------------------------------------ mapeo ME-13


@pytest.mark.unit
@pytest.mark.target("similitud", "_map_mejor")
def test_mapeo_sugiere_el_requerimiento_parecido_y_prefiere_su_nivel(accesos_no_api):
    """
    TB-409 (ME-13): la similitud ignora acentos, mayúsculas y símbolos y
    compara contra nombre y código; el mejor match se busca primero en el
    nivel de la fila (Empresa/Persona/Equipo) y un texto sin parecido no
    sugiere nada (por debajo de 40 %). Si falla, el auto-mapeo homologa
    requerimientos que no tienen que ver.
    """
    from lkf_addons.accesos.contratistas_mapeo import similitud, SUGIERE, HOMOLOGA

    acc = accesos_no_api
    assert similitud("Opinión de Cumplimiento IMSS", "opinion de cumplimiento imss") == 1.0
    assert similitud("", "CSF") == 0.0

    req, s = acc._map_mejor("DC 3", CATALOGO_MAESTRO, "Persona")
    assert req["id"] == "r2" and s >= HOMOLOGA, "El código DC3 debía homologar"

    req, s = acc._map_mejor("Constancia de situacion fiscal SAT", CATALOGO_MAESTRO, "Empresa")
    assert req["id"] == "r1" and s >= SUGIERE

    req, s = acc._map_mejor("Póliza de seguro de vehículos", CATALOGO_MAESTRO, "Empresa")
    assert s < SUGIERE, f"Sugirió {req and req['nombre']} con {s:.0%}"


# ------------------------------------------------------- sesiones CF-04-B


@pytest.mark.unit
@pytest.mark.target("_ses_resultado")
def test_resultado_de_sesion_por_examenes_o_por_asistencia_completa(accesos_no_api):
    """
    TB-410 (CF-04-B): con exámenes, el participante aprueba solo si tiene
    todas las calificaciones y cada una alcanza su mínima; si falta alguna,
    aún no hay resultado. Sin exámenes, aprueba con asistencia en todos los
    días y no hay resultado mientras falte registrar un día. Al aprobar se
    otorga el documento del requerimiento, así que si falla se dan
    constancias a quien no las ganó.
    """
    acc = accesos_no_api
    f = acc.ctr_f["sesiones_de_capacitacion"]

    def p(asistencia=None, calificaciones=None):
        return {f["participante_asistencia"]: simplejson.dumps(asistencia or {}),
                f["participante_calificaciones"]: simplejson.dumps(calificaciones or {})}

    minimas = {"ex1": 80, "ex2": 70}
    assert acc._ses_resultado(p(calificaciones={"ex1": 80, "ex2": 70}), [], minimas) == "Aprobado"
    assert acc._ses_resultado(p(calificaciones={"ex1": 95, "ex2": 69}), [], minimas) == "No aprobado"
    assert acc._ses_resultado(p(calificaciones={"ex1": 95}), [], minimas) is None

    dias = [date(2026, 6, 1), date(2026, 6, 2)]
    completa = {"2026-06-01": "Asistió", "2026-06-02": "Asistió"}
    assert acc._ses_resultado(p(asistencia=completa), dias, {}) == "Aprobado"
    assert acc._ses_resultado(p(asistencia={**completa, "2026-06-02": "Faltó"}), dias, {}) == "No aprobado"
    assert acc._ses_resultado(p(asistencia={"2026-06-01": "Asistió"}), dias, {}) is None
