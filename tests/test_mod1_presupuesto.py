"""
Pruebas unitarias exhaustivas del Módulo 1:
Radiografía del Sueldo, Presupuesto Personal y Gastos Hormiga (Nidia Velásquez).
Compatible tanto con `pytest` como con ejecución directa en Python estándar.
"""

from src.finance import cargar_configuracion
from src.mod1_presupuesto import (
    calcular_fsp_porcentaje,
    comparar_modalidades_laborales,
    cuantificar_gastos_hormiga_y_fugas,
    diagnosticar_presupuesto_y_flujo_caja,
    ejecutar_modulo_1_perfil_usuario,
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


def test_interfaz_grafica_local_endpoints():
    import json
    import threading
    import urllib.request
    from http.server import ThreadingHTTPServer

    from app_mod1_local import Mod1RequestHandler

    server = ThreadingHTTPServer(("127.0.0.1", 0), Mod1RequestHandler)
    port = server.server_address[1]
    hilo = threading.Thread(target=server.serve_forever, daemon=True)
    hilo.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/") as resp_html:
            html = resp_html.read().decode("utf-8")
            assert resp_html.status == 200
            assert "Radiografía del Sueldo" in html

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
    finally:
        server.shutdown()
        server.server_close()


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
        test_interfaz_grafica_local_endpoints,
    ]
    for fn in pruebas:
        fn()
        print(f"[OK] {fn.__name__}")
    print(f"\nTodas las {len(pruebas)} pruebas del Módulo 1 pasaron exitosamente.")
