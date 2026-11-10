"""
Suite de pruebas unitarias e integración de los 6 módulos del Asesor Financiero OED.
"""

from src.data_governance import (
    calcular_permanencia_centrales_riesgo_ley_1266,
    cifrar_payload_local,
    descifrar_payload_local,
    registrar_consentimiento_habeas_data,
)
from src.finance import ea_a_em, em_a_ea, validar_usura_sfc
from src.mod1_presupuesto import diagnosticar_presupuesto_y_flujo_caja
from src.mod2_inversiones_salario import estructurar_portafolio_salario
from src.mod3_gestion_deudas import optimizar_portafolio_deudas
from src.mod4_finca_raiz import evaluar_inversion_finca_raiz
from src.mod5_decisiones_vida import evaluar_viabilidad_decision_vida
from src.mod6_educacion_financiera import (
    comparar_azar_vs_inversion_compuesta,
    detectar_esquema_piramidal_ponzi,
    perfilar_inversionista_decreto_2555,
)


def test_conversion_tasas_y_usura_camilo():
    tasa_ea = 0.12
    tasa_em = ea_a_em(tasa_ea)
    assert abs(em_a_ea(tasa_em) - tasa_ea) < 1e-9
    assert validar_usura_sfc(0.32, 0.265)["excede_usura"] is True


def test_gobierno_datos_ley_1581_y_1266_nelson():
    cons = registrar_consentimiento_habeas_data("1032390306", True)
    assert cons["consentimiento_valido"] is True
    token = cifrar_payload_local({"saldo": 1500000})
    recuperado = descifrar_payload_local(token)
    assert recuperado["saldo"] == 1500000
    regla_mora = calcular_permanencia_centrales_riesgo_ley_1266(meses_en_mora=10, obligacion_pagada=True)
    assert regla_mora["meses_permanencia_post_pago"] == 20


def test_flujo_integrado_6_modulos_oed():
    # 1. Módulo 6 (Salin)
    perfil = perfilar_inversionista_decreto_2555(5, 12.0, 4, 3)
    assert perfil["perfil_riesgo"] in ("Conservador", "Moderado", "Agresivo")
    azar = comparar_azar_vs_inversion_compuesta(200_000.0, 10)
    assert azar["patrimonio_inversion_compuesta_cop"] > azar["valor_esperado_azar_cop"]
    piramide = detectar_esquema_piramidal_ponzi(10.0, 3)
    assert piramide["alerta_piramide"] is True

    # 2. Módulo 1 (Nidia)
    pres = diagnosticar_presupuesto_y_flujo_caja(
        ingreso_bruto_mensual_cop=6_500_000.0,
        gastos_fijos_vitales_cop=2_800_000.0,
        gastos_variables_estilo_vida_cop=950_000.0,
        gastos_hormiga_mensual_cop=320_000.0,
        cuotas_deuda_mensual_cop=600_000.0,
        liquidez_actual_fondo_emergencia_cop=9_000_000.0,
    )
    assert pres["excedente_mensual_cop"] > 0

    # 3. Módulo 3 (Catalina)
    deudas = optimizar_portafolio_deudas(
        ingreso_neto_mensual_cop=pres["ingreso_neto_mensual_cop"],
        abono_extra_mensual_cop=300_000.0,
        lista_deudas=[
            {"nombre": "Tarjeta Crédito", "saldo_cop": 4_500_000.0, "tasa_ea": 0.255, "cuota_mensual_cop": 350_000.0},
            {"nombre": "Libre Inversión", "saldo_cop": 8_000_000.0, "tasa_ea": 0.165, "cuota_mensual_cop": 250_000.0},
        ],
    )
    assert deudas["ahorro_intereses_cop"] > 0

    # 4. Módulo 2 (Camilo)
    inv = estructurar_portafolio_salario(
        excedente_mensual_cop=pres["excedente_mensual_cop"],
        perfil_riesgo=perfil["perfil_riesgo"],
        horizonte_meses=60,
    )
    assert inv["viable_invertir"] is True
    assert inv["patrimonio_proyectado_nominal_cop"] > inv["capital_total_aportado_cop"]

    # 5. Módulo 4 (Jesi)
    finca = evaluar_inversion_finca_raiz(
        valor_inmueble_cop=200_000_000.0,
        ingreso_familiar_neto_cop=pres["ingreso_neto_mensual_cop"] + 3_500_000.0,
    )
    assert finca["cumple_ley_546_30pct"] is True

    # 6. Módulo 5 (Nelson)
    vida = evaluar_viabilidad_decision_vida(
        tipo_decision="HIJOS",
        ingreso_neto_hogar_mensual_cop=pres["ingreso_neto_mensual_cop"] + 3_500_000.0,
        excedente_mensual_actual_cop=pres["excedente_mensual_cop"] + 1_200_000.0,
    )
    assert vida["vpa_decision_cop"] > 0
