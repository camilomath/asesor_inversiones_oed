"""
Pruebas unitarias exhaustivas del Módulo 1:
Radiografía del Sueldo, Presupuesto Personal y Gastos Hormiga (Nidia Velásquez).
Compatible tanto con `pytest` como con ejecución directa en Python estándar.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.finance import cargar_configuracion
from src.mod1_presupuesto import (
    CATALOGO_MICROGASTOS_SUGERIDOS,
    calcular_fsp_porcentaje,
    cargar_simulacion_presupuesto,
    comparar_modalidades_laborales,
    cuantificar_gastos_hormiga_y_fugas,
    culminar_asesoria_y_reiniciar,
    diagnosticar_presupuesto_y_flujo_caja,
    ejecutar_modulo_1_perfil_usuario,
    eliminar_simulacion_historial,
    guardar_simulacion_presupuesto,
    liquidar_ingreso_neto_colombia,
)


def test_paso4_verificacion_salario_6_5m_empleado():
    """
    Checklist Paso 4 (Nidia):
    Comprobar que un salario bruto de $6.500.000 COP liquide Salud (4%),
    Pensión (4%) y el 1% de Fondo de Solidaridad Pensional (> 4 SMMLV).
    """
    cfg = cargar_configuracion()
    res = liquidar_ingreso_neto_colombia(6_500_000.0, modalidad_laboral="Empleado", config=cfg)

    assert res["modalidad_laboral"] == "Empleado"
    assert res["auxilio_transporte_cop"] == 0.0
    assert res["salud_obligatoria_cop"] == 260_000.0
    assert res["pension_obligatoria_cop"] == 260_000.0
    assert res["porcentaje_fsp_aplicado"] == 1.0
    assert res["fondo_solidaridad_pensional_cop"] == 65_000.0
    assert res["retencion_fuente_cop"] == 0.0  # Base gravable ~89.08 UVT <= 95 UVT
    assert res["ingreso_neto_mensual_cop"] == 5_915_000.0


def test_auxilio_transporte_menor_o_igual_2_smmlv():
    cfg = cargar_configuracion()
    smmlv = cfg["parametros_macro_colombia"]["smmlv_cop"]
    aux = cfg["parametros_macro_colombia"]["auxilio_transporte_cop"]

    res_con_aux = liquidar_ingreso_neto_colombia(smmlv * 2.0, modalidad_laboral="Empleado", config=cfg)
    res_sin_aux = liquidar_ingreso_neto_colombia(smmlv * 2.1, modalidad_laboral="Empleado", config=cfg)

    assert res_con_aux["auxilio_transporte_cop"] == aux
    assert res_sin_aux["auxilio_transporte_cop"] == 0.0


def test_modalidades_integral_e_independiente_ops():
    cfg = cargar_configuracion()
    smmlv = cfg["parametros_macro_colombia"]["smmlv_cop"]

    # Salario Integral >= 13 SMMLV cotiza sobre el 70%
    bruto_integral = 20_000_000.0
    res_int = liquidar_ingreso_neto_colombia(bruto_integral, modalidad_laboral="Integral", config=cfg)
    assert res_int["ibc_cotizacion_cop"] == round(bruto_integral * 0.70, 2)
    assert res_int["salud_obligatoria_cop"] == round(bruto_integral * 0.70 * 0.04, 2)
    assert res_int["alerta_normativa"] is None

    # Alerta si se intenta salario integral < 13 SMMLV
    res_int_bajo = liquidar_ingreso_neto_colombia(10_000_000.0, modalidad_laboral="Integral", config=cfg)
    assert res_int_bajo["alerta_normativa"] is not None

    # Contratista Independiente OPS: IBC = 40% (piso 1 SMMLV), Salud 12.5%, Pensión 16%, ARL Riesgo I (0.522%)
    honorarios = 8_000_000.0
    res_ind = liquidar_ingreso_neto_colombia(
        honorarios, modalidad_laboral="Independiente", clase_riesgo_arl=1, config=cfg
    )
    ibc_esperado = honorarios * 0.40
    assert res_ind["ibc_cotizacion_cop"] == ibc_esperado
    assert res_ind["salud_obligatoria_cop"] == round(ibc_esperado * 0.125, 2)
    assert res_ind["pension_obligatoria_cop"] == round(ibc_esperado * 0.16, 2)
    assert res_ind["arl_cop"] == round(ibc_esperado * 0.00522, 2)

    # Piso de 1 SMMLV en IBC de independiente con honorarios bajos
    res_ind_piso = liquidar_ingreso_neto_colombia(2_000_000.0, modalidad_laboral="OPS", config=cfg)
    assert res_ind_piso["ibc_cotizacion_cop"] == smmlv


def test_retefuente_art_383_y_beneficio_afc():
    cfg = cargar_configuracion()
    res_sin_afc = liquidar_ingreso_neto_colombia(12_000_000.0, modalidad_laboral="Empleado", config=cfg)
    res_con_afc = liquidar_ingreso_neto_colombia(
        12_000_000.0,
        modalidad_laboral="Empleado",
        aporte_voluntario_afc_fpv_cop=1_500_000.0,
        config=cfg,
    )
    assert res_sin_afc["retencion_fuente_cop"] > 0
    assert res_con_afc["retencion_fuente_cop"] < res_sin_afc["retencion_fuente_cop"]
    assert res_con_afc["ahorro_tributario_afc_mensual_cop"] > 0


def test_escalones_fsp():
    assert calcular_fsp_porcentaje(3.9) == 0.0
    assert calcular_fsp_porcentaje(4.0) == 0.010
    assert calcular_fsp_porcentaje(16.5) == 0.012
    assert calcular_fsp_porcentaje(17.5) == 0.014
    assert calcular_fsp_porcentaje(18.5) == 0.016
    assert calcular_fsp_porcentaje(19.5) == 0.018
    assert calcular_fsp_porcentaje(21.0) == 0.020


def test_gastos_hormiga_4x1000_y_costo_oportunidad():
    detalle = [
        {"concepto": "Café diario", "monto_unitario_cop": 5_000, "frecuencia_mensual": 20},
        {"concepto": "Domicilios", "monto_unitario_cop": 15_000, "frecuencia_mensual": 6},
    ]  # $190.000/mes
    fugas = cuantificar_gastos_hormiga_y_fugas(
        detalle_gastos_hormiga=detalle,
        cuotas_manejo_mensual_cop=20_000.0,
        monto_movimientos_gmf_mensual_cop=2_500_000.0,
        cuenta_exenta_4x1000=False,  # 4x1000 = $10.000
        ingreso_neto_mensual_cop=4_000_000.0,
    )
    assert fugas["gastos_hormiga_mensual_cop"] == 190_000.0
    assert fugas["gmf_4x1000_mensual_cop"] == 10_000.0
    assert fugas["fuga_total_mensual_cop"] == 220_000.0
    assert fugas["costo_oportunidad_hormiga_10a_cop"] > fugas["costo_oportunidad_hormiga_5a_cop"]
    assert fugas["costo_oportunidad_hormiga_5a_cop"] > 190_000.0 * 60


def test_flujos_cu01_camino_feliz_fa01_y_fa02():
    # FA-02: Excedente > 0 pero fondo de emergencia < 3 meses (6M / 2.8M = 2.14 meses)
    diag_fa02 = diagnosticar_presupuesto_y_flujo_caja(
        ingreso_bruto_mensual_cop=6_500_000.0,
        gastos_fijos_vitales_cop=2_800_000.0,
        gastos_variables_estilo_vida_cop=950_000.0,
        gastos_hormiga_mensual_cop=320_000.0,
        liquidez_actual_fondo_emergencia_cop=6_000_000.0,
    )
    assert diag_fa02["estado_flujo_caja"] == "CONSTRUIR_FONDO_EMERGENCIA"
    assert diag_fa02["plan_accion_flujo_caja"]["codigo_flujo"] == "FA-02"
    esperado_80 = round(diag_fa02["excedente_mensual_cop"] * 0.80, 2)
    assert abs(diag_fa02["plan_accion_flujo_caja"]["aporte_recomendado_fondo_emergencia_cop"] - esperado_80) < 0.02

    # FA-01: Déficit crítico (egresos > IDN)
    diag_fa01 = diagnosticar_presupuesto_y_flujo_caja(
        ingreso_bruto_mensual_cop=3_000_000.0,
        gastos_fijos_vitales_cop=2_200_000.0,
        gastos_variables_estilo_vida_cop=800_000.0,
        gastos_hormiga_mensual_cop=300_000.0,
    )
    assert diag_fa01["excedente_mensual_cop"] < 0
    assert diag_fa01["estado_flujo_caja"] == "DEFICIT_CRITICO"
    assert diag_fa01["plan_accion_flujo_caja"]["bloquea_inversion_riesgo"] is True

    # Camino feliz: Independiente requiere 6 meses de fondo de emergencia
    diag_ok = diagnosticar_presupuesto_y_flujo_caja(
        ingreso_bruto_mensual_cop=9_000_000.0,
        gastos_fijos_vitales_cop=2_500_000.0,
        gastos_variables_estilo_vida_cop=1_000_000.0,
        gastos_hormiga_mensual_cop=150_000.0,
        liquidez_actual_fondo_emergencia_cop=16_000_000.0,
        modalidad_laboral="Independiente",
    )
    assert diag_ok["meta_meses_fondo_emergencia"] == 6.0
    assert diag_ok["fondo_emergencia_completo"] is True
    assert diag_ok["estado_flujo_caja"] == "LISTO_PARA_INVERTIR"


def test_contrato_integracion_oed_y_comparador():
    salida = ejecutar_modulo_1_perfil_usuario()
    for key in (
        "ingreso_neto_mensual_cop",
        "excedente_mensual_cop",
        "meses_fondo_emergencia",
        "costo_oportunidad_hormiga_10a_cop",
    ):
        assert key in salida

    comp = comparar_modalidades_laborales(18_500_000.0)
    assert len(comp) == 3
    assert [c["modalidad_laboral"] for c in comp] == ["Empleado", "Integral", "Independiente"]


def test_persistencia_cambio_salario_y_modalidad():
    """
    Verifica que al cambiar el salario y la modalidad (Empleado -> Independiente -> Integral)
    la información se guarde y recupere íntegramente desde disco (perfil activo e historial).
    """
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        ruta_act = Path(tmpdir) / "perfil_activo.json"
        ruta_hist = Path(tmpdir) / "historial.json"

        # 1. Guardar cambio inicial como Empleado ($7.200.000)
        g1 = guardar_simulacion_presupuesto(
            datos_entrada={
                "modalidad_laboral": "Empleado",
                "ingreso_bruto_mensual_cop": 7_200_000.0,
                "gastos_fijos_vitales_cop": 2_800_000.0,
                "gastos_variables_estilo_vida_cop": 900_000.0,
                "gastos_hormiga_mensual_cop": 250_000.0,
            },
            nombre_escenario="Cambio Sueldo Empleado",
            guardar_en_historial=True,
            ruta_activo=ruta_act,
            ruta_historial=ruta_hist,
        )
        assert g1["guardado_exitoso"] is True
        assert len(g1["historial"]) == 1

        # 2. Cambiar modalidad a Independiente OPS ($9.500.000, ARL Clase II) y guardar
        g2 = guardar_simulacion_presupuesto(
            datos_entrada={
                "modalidad_laboral": "Independiente",
                "clase_riesgo_arl": 2,
                "ingreso_bruto_mensual_cop": 9_500_000.0,
                "gastos_fijos_vitales_cop": 3_000_000.0,
                "gastos_variables_estilo_vida_cop": 1_000_000.0,
                "gastos_hormiga_mensual_cop": 200_000.0,
            },
            nombre_escenario="Oferta OPS Independiente",
            guardar_en_historial=True,
            ruta_activo=ruta_act,
            ruta_historial=ruta_hist,
        )
        assert g2["perfil_activo"]["parametros_entrada"]["modalidad_laboral"] == "Independiente"
        assert g2["perfil_activo"]["parametros_entrada"]["ingreso_bruto_mensual_cop"] == 9_500_000.0
        assert len(g2["historial"]) == 2

        # 3. Recuperar desde disco simulando reinicio de la aplicación
        recuperado = cargar_simulacion_presupuesto(ruta_activo=ruta_act, ruta_historial=ruta_hist)
        assert recuperado["existe_perfil_guardado"] is True
        assert recuperado["perfil_activo"]["parametros_entrada"]["ingreso_bruto_mensual_cop"] == 9_500_000.0
        assert recuperado["perfil_activo"]["parametros_entrada"]["clase_riesgo_arl"] == 2
        assert len(recuperado["historial"]) == 2

        # 4. Eliminar el primer registro del historial
        id_borrar = g1["item_historial_creado"]["id_registro"]
        restante = eliminar_simulacion_historial(id_borrar, ruta_historial=ruta_hist)
        assert len(restante) == 1
        assert restante[0]["nombre_escenario"] == "Oferta OPS Independiente"


def test_interfaz_grafica_local_endpoints():
    import json
    import tempfile
    import threading
    import urllib.request
    from http.server import ThreadingHTTPServer
    from pathlib import Path

    from app_mod1_local import Mod1RequestHandler

    with tempfile.TemporaryDirectory() as tmpdir:

        class TestHandler(Mod1RequestHandler):
            ruta_activo = Path(tmpdir) / "ui_activo.json"
            ruta_historial = Path(tmpdir) / "ui_historial.json"

        server = ThreadingHTTPServer(("127.0.0.1", 0), TestHandler)
        port = server.server_address[1]
        hilo = threading.Thread(target=server.serve_forever, daemon=True)
        hilo.start()
        try:
            # 1. Verificar UI HTML y presencia del símbolo de ahorro de fondo
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/") as resp_html:
                html = resp_html.read().decode("utf-8")
                assert resp_html.status == 200
                assert "Radiografía del Sueldo" in html
                assert "watermark-ahorro" in html
                assert "background-image: url(\"data:image/svg+xml" in html

            # 2. Probar guardado al cambiar salario y modalidad vía POST /api/guardar
            req_save = urllib.request.Request(
                f"http://127.0.0.1:{port}/api/guardar",
                data=json.dumps(
                    {
                        "nombre_escenario": "Prueba Salario Integral",
                        "guardar_en_historial": True,
                        "parametros": {
                            "modalidad_laboral": "Integral",
                            "ingreso_bruto_mensual_cop": 20_000_000.0,
                            "aporte_voluntario_afc_fpv_cop": 1_500_000.0,
                            "gastos_fijos_vitales_cop": 5_500_000.0,
                            "gastos_variables_estilo_vida_cop": 2_000_000.0,
                            "gastos_hormiga_mensual_cop": 300_000.0,
                            "liquidez_actual_fondo_emergencia_cop": 20_000_000.0,
                        },
                    }
                ).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req_save) as resp_save:
                saved = json.loads(resp_save.read().decode("utf-8"))
                assert saved["guardado_exitoso"] is True
                assert saved["perfil_activo"]["parametros_entrada"]["modalidad_laboral"] == "Integral"
                assert saved["perfil_activo"]["parametros_entrada"]["ingreso_bruto_mensual_cop"] == 20_000_000.0
                id_creado = saved["item_historial_creado"]["id_registro"]

            # 3. Verificar restauración vía GET /api/estado_guardado
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/estado_guardado") as resp_est:
                estado = json.loads(resp_est.read().decode("utf-8"))
                assert estado["existe_perfil_guardado"] is True
                assert estado["perfil_activo"]["parametros_entrada"]["ingreso_bruto_mensual_cop"] == 20_000_000.0
                assert len(estado["historial"]) == 1

            # 4. Probar eliminación de escenario guardado vía POST /api/eliminar_guardado
            req_del = urllib.request.Request(
                f"http://127.0.0.1:{port}/api/eliminar_guardado",
                data=json.dumps({"id_registro": id_creado}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req_del) as resp_del:
                borrado = json.loads(resp_del.read().decode("utf-8"))
                assert borrado["eliminado"] is True
                assert len(borrado["historial"]) == 0

            # 5. Probar diagnóstico estándar vía POST /api/diagnostico
            req = urllib.request.Request(
                f"http://127.0.0.1:{port}/api/diagnostico",
                data=json.dumps(
                    {
                        "modalidad_laboral": "Empleado",
                        "ingreso_bruto_mensual_cop": 6_500_000.0,
                        "gastos_fijos_vitales_cop": 2_800_000.0,
                        "gastos_variables_estilo_vida_cop": 950_000.0,
                        "gastos_hormiga_mensual_cop": 320_000.0,
                        "liquidez_actual_fondo_emergencia_cop": 6_000_000.0,
                    }
                ).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req) as resp_api:
                data = json.loads(resp_api.read().decode("utf-8"))
                assert data["diagnostico"]["ingreso_neto_mensual_cop"] == 5_915_000.0
                assert data["contrato_oed"]["excedente_mensual_cop"] == 1_845_000.0
                assert len(data["comparativa_modalidades"]) == 3
                assert "optimizacion_ingenieril" in data["diagnostico"]
                assert "guia_asesoria" in data["diagnostico"]

            # 6. Probar culminación de asesoría y reinicio en ceros vía POST /api/culminar_asesoria
            req_fin = urllib.request.Request(
                f"http://127.0.0.1:{port}/api/culminar_asesoria",
                data=json.dumps(
                    {
                        "nombre_asesorado": "Cliente Prueba Cierre",
                        "guardar_cierre_en_historial": True,
                        "datos_cierre": {
                            "modalidad_laboral": "Empleado",
                            "ingreso_bruto_mensual_cop": 6_500_000.0,
                            "gastos_fijos_vitales_cop": 2_800_000.0,
                            "gastos_variables_estilo_vida_cop": 950_000.0,
                            "detalle_gastos_hormiga": [
                                {"concepto": "Café", "monto_unitario_cop": 6500, "frecuencia_mensual": 20}
                            ],
                        },
                    }
                ).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req_fin) as resp_fin:
                cierre = json.loads(resp_fin.read().decode("utf-8"))
                assert cierre["asesoria_culminada"] is True
                assert cierre["reiniciado_en_ceros"] is True
                assert cierre["parametros_ceros"]["ingreso_bruto_mensual_cop"] == 0.0
                assert cierre["parametros_ceros"]["detalle_gastos_hormiga"] == []
                assert len(cierre["historial"]) == 1
                assert cierre["historial"][0]["nombre_escenario"] == "Cliente Prueba Cierre"

            # 7. Verificar que al recargar la página después de culminar asesoría inicie en ceros ($0)
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/estado_guardado") as resp_ceros:
                est_ceros = json.loads(resp_ceros.read().decode("utf-8"))
                assert est_ceros["perfil_activo"]["parametros_entrada"]["ingreso_bruto_mensual_cop"] == 0.0
                assert est_ceros["perfil_activo"]["parametros_entrada"]["detalle_gastos_hormiga"] == []
                assert len(est_ceros["catalogo_microgastos"]) >= 15
        finally:
            server.shutdown()
            server.server_close()


def test_optimizador_presupuesto_tributos_y_pareto():
    """Verifica el motor de optimización tributaria AFC, Pareto 80/20 y simulador interactivo."""
    diag = diagnosticar_presupuesto_y_flujo_caja(
        ingreso_bruto_mensual_cop=14_000_000.0,
        gastos_fijos_vitales_cop=4_200_000.0,
        gastos_variables_estilo_vida_cop=1_800_000.0,
        gastos_hormiga_mensual_cop=0.0,
        detalle_gastos_hormiga=[
            {"concepto": "Domicilios premium", "monto_unitario_cop": 35_000, "frecuencia_mensual": 10},
            {"concepto": "Cafés", "monto_unitario_cop": 8_000, "frecuencia_mensual": 10},
        ],
        cuotas_manejo_mensual_cop=30_000.0,
        monto_movimientos_gmf_mensual_cop=5_000_000.0,
        cuenta_exenta_4x1000=False,
        liquidez_actual_fondo_emergencia_cop=8_000_000.0,
        tasa_oportunidad_ea=0.12,
        recorte_hormiga_simulacion_pct=60.0,
    )
    opt = diag["optimizacion_ingenieril"]
    assert opt["tributaria_afc"]["aplica_optimizacion_afc"] is True
    assert opt["tributaria_afc"]["aporte_afc_optimo_mensual_cop"] > 0
    assert opt["tributaria_afc"]["ahorro_tributario_mensual_cop"] > 0

    pareto = opt["ranking_pareto_fugas"]
    assert len(pareto) == 4
    assert pareto[0]["origen"] == "Domicilios premium"
    assert pareto[0]["impacto_pareto_80"] is True

    sim = opt["simulacion_que_pasa_si"]
    assert sim["recorte_hormiga_aplicado_pct"] == 60.0
    assert sim["tasa_ea_simulada_pct"] == 12.0
    assert sim["excedente_optimizado_cop"] > sim["excedente_actual_cop"]
    assert sim["meses_aceleracion_fondo_emergencia"] > 0


def test_culminar_asesoria_en_ceros_microgastos_y_guia_abstencion():
    """
    Verifica:
    1. Catálogo desplegable de microgastos sugeridos.
    2. Consejos personalizados de ahorro y sugerencias de en qué abstenerse.
    3. Reinicio limpio en ceros ($0) al culminar una asesoría.
    """
    import tempfile
    from pathlib import Path

    from app_mod1_local import HTML_DASHBOARD

    assert len(CATALOGO_MICROGASTOS_SUGERIDOS) >= 15
    assert "select_microgasto" in HTML_DASHBOARD
    assert "imprimirAsesoria()" in HTML_DASHBOARD
    assert "guardarInformeHTML()" in HTML_DASHBOARD
    assert "confirmarCulminarAsesoria()" in HTML_DASHBOARD
    assert "contenedor_consejos_ahorro" in HTML_DASHBOARD
    assert "contenedor_abstenciones" in HTML_DASHBOARD

    # Caso con déficit, apuestas y domicilios -> debe emitir consejos de ahorro y abstenciones críticas
    diag_riesgo = diagnosticar_presupuesto_y_flujo_caja(
        ingreso_bruto_mensual_cop=4_000_000.0,
        gastos_fijos_vitales_cop=2_500_000.0,
        gastos_variables_estilo_vida_cop=1_100_000.0,
        gastos_hormiga_mensual_cop=0.0,
        cuotas_deuda_mensual_cop=500_000.0,
        detalle_gastos_hormiga=[
            {"concepto": "Apuestas deportivas online", "monto_unitario_cop": 25_000, "frecuencia_mensual": 8},
            {"concepto": "Domicilios por apps", "monto_unitario_cop": 20_000, "frecuencia_mensual": 8},
        ],
    )
    guia = diag_riesgo["guia_asesoria"]
    assert guia["sesion_activa"] is True
    assert len(guia["consejos_ahorro"]) >= 2
    assert len(guia["en_que_abstenerse"]) >= 3
    severidades = {a["severidad"] for a in guia["en_que_abstenerse"]}
    assert "CRITICA" in severidades

    # Diagnóstico totalmente en ceros -> estado SESION_EN_CEROS sin errores ni divisiones por cero
    diag_ceros = diagnosticar_presupuesto_y_flujo_caja(
        ingreso_bruto_mensual_cop=0.0,
        gastos_fijos_vitales_cop=0.0,
        gastos_variables_estilo_vida_cop=0.0,
        gastos_hormiga_mensual_cop=0.0,
        detalle_gastos_hormiga=[],
    )
    assert diag_ceros["estado_flujo_caja"] == "SESION_EN_CEROS"
    assert diag_ceros["guia_asesoria"]["sesion_activa"] is False

    with tempfile.TemporaryDirectory() as tmpdir:
        r_act = Path(tmpdir) / "activo.json"
        r_hist = Path(tmpdir) / "hist.json"
        res_cierre = culminar_asesoria_y_reiniciar(
            datos_cierre={"modalidad_laboral": "Independiente", "ingreso_bruto_mensual_cop": 8_000_000.0},
            nombre_asesorado="Asesoría Carlos Ruiz",
            guardar_cierre_en_historial=True,
            ruta_activo=r_act,
            ruta_historial=r_hist,
        )
        assert res_cierre["reiniciado_en_ceros"] is True
        assert res_cierre["perfil_activo"]["parametros_entrada"]["ingreso_bruto_mensual_cop"] == 0.0
        assert res_cierre["perfil_activo"]["resumen_resultados"]["estado_flujo_caja"] == "SESION_EN_CEROS"
        assert len(res_cierre["historial"]) == 1


if __name__ == "__main__":
    pruebas = [
        test_paso4_verificacion_salario_6_5m_empleado,
        test_auxilio_transporte_menor_o_igual_2_smmlv,
        test_modalidades_integral_e_independiente_ops,
        test_retefuente_art_383_y_beneficio_afc,
        test_escalones_fsp,
        test_gastos_hormiga_4x1000_y_costo_oportunidad,
        test_flujos_cu01_camino_feliz_fa01_y_fa02,
        test_contrato_integracion_oed_y_comparador,
        test_persistencia_cambio_salario_y_modalidad,
        test_interfaz_grafica_local_endpoints,
        test_optimizador_presupuesto_tributos_y_pareto,
        test_culminar_asesoria_en_ceros_microgastos_y_guia_abstencion,
    ]
    for fn in pruebas:
        fn()
        print(f"[OK] {fn.__name__}")
    print(f"\nTodas las {len(pruebas)} pruebas del Módulo 1 pasaron exitosamente.")
