"""
Pruebas unitarias e integrales exhaustivas del Módulo 4 (Finca Raíz Colombiana - Jesi).

Cubre:
1. Contrato de Integración OED (llaves y tipos obligatorios para conectar con los demás módulos).
2. Clasificación regulatoria VIP / VIS / No VIS (150 SMMLV aglomeración CONPES vs. 135 SMMLV).
3. Elegibilidad y aplicación efectiva del Subsidio de Caja de Compensación Familiar (CCF <= 4 SMMLV).
4. Plan de pago de Cuota Inicial sobre planos (encargo fiduciario + cesantías/primas + Cuenta AFC Art. 126-4 E.T.).
5. Sistemas de amortización SFC (Cuota Fija en Pesos, Abono Constante a Capital y UVR Cíclica),
   verificando extinción exacta de deuda y alerta de riesgo inflacionario UVR (FA-01).
6. Validación estricta de la Regla del 30% de la Ley 546 de 1999 y exactitud matemática del cálculo
   de brecha de ingreso o cuota inicial extra requerida.
7. Diferencias regulatorias entre Crédito Hipotecario tradicional y Leasing Habitacional, y alerta LTV.
8. Tope legal del 1% mensual de canon de arriendo (Ley 820 de 2003), Cap Rate Neto, Cash-on-Cash,
   VPN, TIR neta de Ganancia Ocasional (15% Ley 2277/2022) y comparativa a 10 años frente a FIC Inmobiliario.
"""

import json
import sys
from pathlib import Path

# Permite ejecutar `py tests/test_mod4_finca_raiz_jesi.py` directamente incluso sin tener pytest instalado
if __package__ in (None, ""):
    _PROJECT_ROOT = Path(__file__).resolve().parent.parent
    if str(_PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(_PROJECT_ROOT))

from src.mod4_finca_raiz import (
    clasificar_segmento_vivienda_colombia,
    evaluar_inversion_finca_raiz,
    simular_plan_cuota_inicial_planos,
    simular_sistemas_amortizacion_ley_546,
)
from src.ui_mod4_finca_raiz import (
    _filas_a_csv_bytes,
    extraer_valores_iniciales_desde_estado,
    generar_resumen_ejecutivo_ciudadano,
    procesar_simulacion_api_local,
)


def test_contrato_integracion_oed_llaves_obligatorias():
    """Verifica que el diccionario de salida respete al 100% el Contrato de Integración del equipo OED."""
    res = evaluar_inversion_finca_raiz(
        valor_inmueble_cop=200_000_000.0,
        ingreso_familiar_neto_cop=9_415_000.0,
    )
    llaves_contrato = [
        "segmento_vivienda",
        "valor_inmueble_smmlv",
        "cuota_inicial_total_cop",
        "gastos_escrituracion_registro_cop",
        "cuota_inicial_mensual_cop",
        "monto_credito_hipotecario_cop",
        "primera_cuota_credito_cop",
        "primera_cuota_uvr_cop",
        "cuota_uvr_proyectada_anio_5_cop",
        "tope_cuota_ley_546_30pct_cop",
        "cumple_ley_546_30pct",
        "cumple_ley_546_en_uvr",
        "ingreso_familiar_minimo_requerido_cop",
        "cap_rate_neto_pct",
        "vpn_inmobiliario_cop",
        "tir_inmobiliaria_ea_pct",
    ]
    for llave in llaves_contrato:
        assert llave in res, f"Falta la llave obligatoria del contrato OED: {llave}"
    assert isinstance(res["cumple_ley_546_30pct"], bool)
    assert res["cumple_ley_546_30pct"] is True


def test_clasificacion_vip_vis_no_vis_y_subsidio_ccf():
    """Valida topes VIP (<=90 SMMLV), VIS (<=150 SMMLV), No VIS (>150 SMMLV) y subsidios CCF."""
    # VIP <= 90 SMMLV con ingreso <= 2 SMMLV -> elegible a 30 SMMLV de subsidio CCF
    vip = clasificar_segmento_vivienda_colombia(
        valor_inmueble_cop=120_000_000.0,
        ingreso_familiar_neto_cop=2_500_000.0,
    )
    assert vip["codigo_segmento"] == "VIP"
    assert vip["elegible_subsidio_ccf"] is True
    assert vip["subsidio_ccf_smmlv"] == 30.0

    # VIS entre 90 y 150 SMMLV con ingreso entre 2 y 4 SMMLV -> elegible a 20 SMMLV
    vis = clasificar_segmento_vivienda_colombia(
        valor_inmueble_cop=200_000_000.0,
        ingreso_familiar_neto_cop=5_000_000.0,
    )
    assert vis["codigo_segmento"] == "VIS"
    assert vis["elegible_subsidio_ccf"] is True
    assert vis["subsidio_ccf_smmlv"] == 20.0

    # No VIS > 150 SMMLV -> sin subsidio CCF y cuota inicial mínima del 30%
    no_vis = clasificar_segmento_vivienda_colombia(
        valor_inmueble_cop=350_000_000.0,
        ingreso_familiar_neto_cop=12_000_000.0,
    )
    assert no_vis["codigo_segmento"] == "NO_VIS"
    assert no_vis["elegible_subsidio_ccf"] is False
    assert no_vis["cuota_inicial_min_legal_pct"] == 0.30


def test_tope_vis_aglomeracion_urbana_vs_municipio_general():
    """Un inmueble de ~140 SMMLV ($200M) es VIS en aglomeración CONPES (<=150), pero No VIS fuera de ella (<=135)."""
    en_aglomeracion = clasificar_segmento_vivienda_colombia(
        valor_inmueble_cop=200_000_000.0,
        ingreso_familiar_neto_cop=6_000_000.0,
        aglomeracion_urbana=True,
    )
    fuera_aglomeracion = clasificar_segmento_vivienda_colombia(
        valor_inmueble_cop=200_000_000.0,
        ingreso_familiar_neto_cop=6_000_000.0,
        aglomeracion_urbana=False,
    )
    assert en_aglomeracion["codigo_segmento"] == "VIS"
    assert fuera_aglomeracion["codigo_segmento"] == "NO_VIS"


def test_plan_cuota_inicial_sobre_planos_con_afc_y_subsidio():
    """Verifica el descuento de ahorro previo AFC, cesantías/primas y subsidio CCF en el plan sobre planos."""
    plan = simular_plan_cuota_inicial_planos(
        valor_inmueble_cop=200_000_000.0,
        ingreso_familiar_neto_cop=8_500_000.0,
        porcentaje_cuota_inicial=0.30,
        plazo_entrega_planos_meses=24,
        cesantias_y_primas_anuales_cop=5_000_000.0,
        ahorro_previo_afc_cop=10_000_000.0,
    )
    # Cuota inicial total = 60M; menos 10M previos y 10M cesantías/primas (2 años) = 40M / 24 meses
    assert plan["cuota_inicial_total_cop"] == 60_000_000.0
    assert abs(plan["cuota_inicial_mensual_cop"] - (40_000_000.0 / 24.0)) < 1.0
    assert len(plan["cronograma_fiduciario_mensual"]) == 24
    assert plan["ahorro_tributario_afc_total_cop"] > 0.0
    assert plan["rendimientos_encargo_fiduciario_cop"] > 0.0

    # Para hogar elegible (<= 4 SMMLV en VIS), aplicar subsidio CCF reduce la cuota mensual sobre planos
    plan_sin_sub = simular_plan_cuota_inicial_planos(
        valor_inmueble_cop=180_000_000.0,
        ingreso_familiar_neto_cop=4_800_000.0,
        aplicar_subsidio_ccf=False,
    )
    plan_con_sub = simular_plan_cuota_inicial_planos(
        valor_inmueble_cop=180_000_000.0,
        ingreso_familiar_neto_cop=4_800_000.0,
        aplicar_subsidio_ccf=True,
    )
    assert plan_con_sub["subsidio_ccf_aplicado_cop"] > 0.0
    assert plan_con_sub["cuota_inicial_mensual_cop"] < plan_sin_sub["cuota_inicial_mensual_cop"]


def test_sistemas_amortizacion_extincion_deuda_y_alerta_uvr_fa01():
    """Valida que los 3 sistemas SFC extingan el saldo a cero, ordenen intereses y activen alerta UVR FA-01."""
    amort = simular_sistemas_amortizacion_ley_546(
        monto_credito_cop=150_000_000.0,
        plazo_credito_anios=15,
        tasa_ea_pesos=0.115,
        tasa_ea_uvr_mas_spread=0.065,
        ipc_anual_proyectado=0.06,
    )
    assert amort["primera_cuota_uvr_cop"] < amort["primera_cuota_pesos_fija_cop"]
    assert amort["primera_cuota_abono_constante_cop"] > amort["primera_cuota_pesos_fija_cop"]
    assert amort["total_intereses_abono_constante_cop"] < amort["total_intereses_pesos_fija_cop"]
    assert amort["alerta_riesgo_uvr_fa01"] is True

    # Los tres sistemas deben extinguir completamente la deuda en el último mes
    assert amort["tabla_pesos_cuota_fija"][-1]["saldo_capital_cop"] < 1.0
    assert amort["tabla_pesos_abono_constante"][-1]["saldo_capital_cop"] < 1.0
    assert amort["tabla_uvr_ciclica"][-1]["saldo_capital_cop"] < 1.0

    # Sensibilidad coherente ante choques de inflación IPC
    sens = amort["sensibilidad_cuota_uvr_anio_5"]
    assert sens["ipc_bajo_3_5pct_cop"] < sens["ipc_base_dane_cop"] < sens["ipc_alto_choque_8_5pct_cop"]


def test_regla_30pct_ley_546_y_tope_canon_ley_820():
    """Valida que cuando se incumple la Ley 546, la cuota inicial extra calculada resuelve exactamente la brecha."""
    res_no_cumple = evaluar_inversion_finca_raiz(
        valor_inmueble_cop=320_000_000.0,
        ingreso_familiar_neto_cop=5_500_000.0,
        porcentaje_cuota_inicial=0.30,
        canon_arriendo_mensual_estimado_cop=4_500_000.0,  # > 1% del valor comercial ($3.2M)
    )
    assert res_no_cumple["cumple_ley_546_30pct"] is False
    assert res_no_cumple["deficit_ingreso_familiar_cop"] > 0.0
    assert res_no_cumple["cuota_inicial_extra_requerida_ley_546_cop"] > 0.0
    # Ley 820 de 2003 recorta el canon al 1% mensual ($3.200.000)
    assert res_no_cumple["recortado_por_ley_820"] is True
    assert res_no_cumple["canon_mensual_aplicado_cop"] == 3_200_000.0

    # Si el usuario aporta exactamente la cuota inicial extra sugerida, ya cumple el 30% de la Ley 546
    nueva_inicial_pct = (
        res_no_cumple["cuota_inicial_total_cop"]
        + res_no_cumple["cuota_inicial_extra_requerida_ley_546_cop"]
    ) / 320_000_000.0
    res_ajustado = evaluar_inversion_finca_raiz(
        valor_inmueble_cop=320_000_000.0,
        ingreso_familiar_neto_cop=5_500_000.0,
        porcentaje_cuota_inicial=nueva_inicial_pct,
    )
    assert res_ajustado["cumple_ley_546_30pct"] is True


def test_leasing_habitacional_vs_hipotecario_y_alerta_ltv():
    """Verifica el tratamiento diferencial de gastos de escrituración y LTV entre Hipotecario y Leasing."""
    hipotecario = evaluar_inversion_finca_raiz(
        valor_inmueble_cop=300_000_000.0,
        ingreso_familiar_neto_cop=11_000_000.0,
        porcentaje_cuota_inicial=0.20,  # Inferior al 30% mínimo legal de Hipotecario No VIS
        modalidad_financiacion="HIPOTECARIO",
        incluir_tablas_detalle=True,
    )
    leasing = evaluar_inversion_finca_raiz(
        valor_inmueble_cop=300_000_000.0,
        ingreso_familiar_neto_cop=11_000_000.0,
        porcentaje_cuota_inicial=0.20,  # Sí cumple el 20% mínimo de Leasing No VIS
        modalidad_financiacion="LEASING",
    )
    assert hipotecario["gastos_escrituracion_registro_cop"] == 9_000_000.0
    assert any("Alerta LTV" in a for a in hipotecario["alertas_regulatorias"])
    assert "plan_cuota_inicial_detalle" in hipotecario and "amortizacion_detalle" in hipotecario

    assert leasing["gastos_escrituracion_registro_cop"] == 0.0
    assert not any("Alerta LTV" in a for a in leasing["alertas_regulatorias"])
    assert len(leasing["flujos_anuales_inversionista_cop"]) == 11
    assert leasing["comparativa_estrategias_10a"]["comprar_pesos_patrimonio_10a_cop"] > 0.0
    assert leasing["comparativa_estrategias_10a"]["arrendar_e_invertir_fic_patrimonio_10a_cop"] > 0.0


def test_estructura_notebook_jesi_valida():
    """Verifica que el notebook interactivo de Jesi exista, sea JSON nbformat v4 válido y contenga código y gráficas."""
    ruta_nb = Path(__file__).resolve().parent.parent / "notebooks" / "04_inversion_finca_raiz_jesi.ipynb"
    assert ruta_nb.exists(), "No existe notebooks/04_inversion_finca_raiz_jesi.ipynb"
    contenido = json.loads(ruta_nb.read_text(encoding="utf-8"))
    assert contenido.get("nbformat") == 4
    celdas_codigo = [c for c in contenido.get("cells", []) if c.get("cell_type") == "code"]
    assert len(celdas_codigo) >= 5


def test_adaptador_interaccion_ui_mod4():
    """Valida el módulo de interacción visual en modo autónomo (semilla) y conectado (Módulos 1 y 2)."""
    # Modo autónomo (sin datos previos)
    base = extraer_valores_iniciales_desde_estado()
    assert base["conectado_con_modulos_previos"] is False
    assert base["valor_inmueble_cop"] == 200_000_000.0

    # Modo conectado recibiendo salidas de Nidia (Módulo 1) y Camilo (Módulo 2)
    conectado = extraer_valores_iniciales_desde_estado(
        {"ingreso_neto_mensual_cop": 5_900_000.0, "ahorro_previo_afc_cop": 15_000_000.0}
    )
    assert conectado["conectado_con_modulos_previos"] is True
    assert conectado["ingreso_titular_neto_cop"] == 5_900_000.0
    assert conectado["ahorro_previo_afc_cop"] == 15_000_000.0

    # Semáforo ciudadano, API web local sin dependencias y exportación CSV
    res_ok = evaluar_inversion_finca_raiz(200_000_000.0, 9_500_000.0)
    res_fail = evaluar_inversion_finca_raiz(380_000_000.0, 4_500_000.0)
    assert generar_resumen_ejecutivo_ciudadano(res_ok)["nivel"] in ("success", "info")
    assert generar_resumen_ejecutivo_ciudadano(res_fail)["nivel"] == "error"
    api_resp = procesar_simulacion_api_local({"valor_inmueble_cop": 210_000_000, "ingreso_titular_cop": 6_000_000})
    assert "resultado" in api_resp and "semaforo" in api_resp
    assert len(_filas_a_csv_bytes([{"mes": 1, "cuota": 1500000}])) > 10


if __name__ == "__main__":
    from tests.test_asesor_oed import test_flujo_integrado_6_modulos_oed

    pruebas = [
        test_contrato_integracion_oed_llaves_obligatorias,
        test_clasificacion_vip_vis_no_vis_y_subsidio_ccf,
        test_tope_vis_aglomeracion_urbana_vs_municipio_general,
        test_plan_cuota_inicial_sobre_planos_con_afc_y_subsidio,
        test_sistemas_amortizacion_extincion_deuda_y_alerta_uvr_fa01,
        test_regla_30pct_ley_546_y_tope_canon_ley_820,
        test_leasing_habitacional_vs_hipotecario_y_alerta_ltv,
        test_estructura_notebook_jesi_valida,
        test_adaptador_interaccion_ui_mod4,
        test_flujo_integrado_6_modulos_oed,
    ]

    print("=" * 72)
    print("EJECUTANDO SUITE DE PRUEBAS DEL MÓDULO 4 (JESI) + INTEGRACIÓN OED")
    print("=" * 72)
    for fn in pruebas:
        fn()
        print(f"  [OK] {fn.__name__}")
    print("=" * 72)
    print(f"RESULTADO: {len(pruebas)}/{len(pruebas)} PRUEBAS SUPERADAS CON ÉXITO.")
