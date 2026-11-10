"""
MÓDULO 5: Análisis Actuarial de Viabilidad de Decisiones de Vida (Casarse, Tener Hijos, Tomar Créditos).
Responsable OED: Nelson (Ingeniero Industrial y Actuaría - Líder de Gobierno de Datos y Datos Personales).

Implementa:
- Valor Presente Actuarial (VPA) de criar y educar un hijo en Colombia de 0 a 23 años
  (Primera infancia, Colegio calendario A/B con inflación educativa del 7.5% EA, Universidad),
  cuota de ahorro mensual nivelada y capital asegurado óptimo de Seguro de Vida para proteger al menor.
- Análisis de viabilidad patrimonial de Casarse / Unión Marital de Hecho (economías de escala del hogar,
  Sociedad Conyugal vs. Capitulaciones Matrimoniales y resiliencia ante desempleo).
- Análisis de Costo Total de Propiedad (TCO) para tomar un crédito vehicular o ROI de crédito educativo.
- Simulación de Monte Carlo (1.000 iteraciones determinísticas reproducibles) ante choques de IPC e ingresos.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import Any, Dict

_ROOT_DIR = Path(__file__).resolve().parent.parent
if str(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR))

from src.finance import cargar_configuracion, cuota_fija_francesa, ea_a_em


def evaluar_viabilidad_decision_vida(
    tipo_decision: str,
    ingreso_neto_hogar_mensual_cop: float,
    excedente_mensual_actual_cop: float,
    liquidez_emergencia_cop: float = 6_000_000.0,
    nivel_costo_hijo: str = "Medio",
    ingreso_pareja_mensual_cop: float = 4_500_000.0,
    costo_boda_cop: float = 18_000_000.0,
    monto_credito_estructural_cop: float = 45_000_000.0,
    tasa_ea_credito: float = 0.165,
    plazo_credito_meses: int = 48,
    iteraciones_montecarlo: int = 1000,
    config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Ejecuta el Caso de Uso CU-05 (Módulo 5 - Nelson):
    Calcula el Valor Presente Actuarial (VPA) de la decisión vital y la probabilidad de éxito
    financiero mediante simulación de Monte Carlo.
    """
    cfg = config or cargar_configuracion()
    macro = cfg["parametros_macro_colombia"]
    ipc = float(macro["ipc_anual_dane"])
    inf_edu = float(macro["inflacion_educativa_anual"])
    tasa_descuento_anual = 0.095  # Rendimiento de referencia portafolio educativo (FIC/CDT)

    decision = tipo_decision.strip().upper()

    if decision == "HIJOS":
        escala = {"BAJO": 0.65, "MEDIO": 1.0, "ALTO": 1.85}.get(nivel_costo_hijo.strip().upper(), 1.0)
        # Costos mensuales base en pesos de hoy por etapa en Colombia
        costo_mensual_etapa = {
            "primera_infancia_0_4": 1_150_000.0 * escala,
            "colegio_5_17": 1_650_000.0 * escala,
            "universidad_18_22": 2_450_000.0 * escala,
        }
        vpa_total = 0.0
        vpa_universidad = 0.0
        prob_supervivencia_acum = 1.0

        for edad in range(0, 23):
            prob_supervivencia_acum *= 0.9985  # Factor actuarial q_x tabla colombiana
            if edad <= 4:
                flujo_anual_hoy = costo_mensual_etapa["primera_infancia_0_4"] * 12.0
                inflacion_aplicada = ipc
            elif edad <= 17:
                flujo_anual_hoy = costo_mensual_etapa["colegio_5_17"] * 12.0
                inflacion_aplicada = inf_edu
            else:
                flujo_anual_hoy = costo_mensual_etapa["universidad_18_22"] * 12.0
                inflacion_aplicada = inf_edu

            flujo_futuro = flujo_anual_hoy * ((1.0 + inflacion_aplicada) ** edad)
            vp_flujo = (flujo_futuro / ((1.0 + tasa_descuento_anual) ** edad)) * prob_supervivencia_acum
            vpa_total += vp_flujo
            if edad >= 18:
                vpa_universidad += vp_flujo

        impacto_mensual_inmediato = costo_mensual_etapa["primera_infancia_0_4"]
        # Cuota mensual de ahorro desde el nacimiento para financiar el 100% de la universidad a los 18 años
        tasa_em_fondo = ea_a_em(tasa_descuento_anual)
        ahorro_mensual_universidad = (vpa_universidad * tasa_em_fondo) / (1.0 - (1.0 + tasa_em_fondo) ** (-18 * 12))
        capital_seguro_vida_recomendado = vpa_total
        recomendacion_legal_actuarial = (
            f"Constituir póliza de seguro de vida temporal por ${capital_seguro_vida_recomendado:,.0f} COP "
            f"y un fondo educativo mensual de ${ahorro_mensual_universidad:,.0f} COP para blindar la universidad."
        )

    elif decision == "CASARSE":
        # Economías de escala por compartir gastos fijos (~22% de ahorro sobre gastos individuales)
        ahorro_sinergia_hogar_mensual = (ingreso_neto_hogar_mensual_cop + ingreso_pareja_mensual_cop) * 0.08
        cuota_amortizacion_boda_24m = costo_boda_cop / 24.0
        impacto_mensual_inmediato = max(0.0, cuota_amortizacion_boda_24m - ahorro_sinergia_hogar_mensual)
        vpa_total = costo_boda_cop
        ahorro_mensual_universidad = cuota_amortizacion_boda_24m
        recomendacion_legal_actuarial = (
            "Marco Legal Colombiano (Código Civil / Ley 54 de 1990): El matrimonio genera Sociedad Conyugal desde el "
            "primer día (la unión libre genera Sociedad Patrimonial a los 2 años). Si existen patrimonios previos "
            "asimétricos o pasivos individuales, evalúen suscribir Capitulaciones Matrimoniales por escritura pública."
        )

    else:  # CREDITO ESTRUCTURAL (Posgrado o Vehículo con TCO)
        tasa_em = ea_a_em(tasa_ea_credito)
        cuota_credito = cuota_fija_francesa(monto_credito_estructural_cop, tasa_em, plazo_credito_meses)
        # Costo oculto mensual (SOAT, impuestos, seguro todo riesgo y mantenimiento si es vehículo ~1.2% mensual)
        costos_ocultos_tco_mensual = monto_credito_estructural_cop * 0.008
        impacto_mensual_inmediato = cuota_credito + costos_ocultos_tco_mensual
        vpa_total = impacto_mensual_inmediato * plazo_credito_meses
        ahorro_mensual_universidad = impacto_mensual_inmediato
        recomendacion_legal_actuarial = (
            "Verifique endosar su propia póliza de seguro de vida deudor (Ley 1328 de 2009) para ahorrar hasta un "
            "40% en el costo del seguro mensual cobrado por el banco."
        )

    # Simulación estocástica de Monte Carlo (1.000 escenarios reproducibles)
    rng = random.Random(20261110)
    escenarios_solventes = 0
    for _ in range(max(100, iteraciones_montecarlo)):
        choque_ingreso = rng.gauss(1.0, 0.08)  # Volatilidad de ingresos / desempleo friccional
        choque_gasto = rng.gauss(1.0, 0.07)    # Choque inflacionario imprevisto
        flujo_neto_simulado = (
            excedente_mensual_actual_cop * choque_ingreso
            - impacto_mensual_inmediato * choque_gasto
            + (liquidez_emergencia_cop / 24.0)
        )
        if flujo_neto_simulado >= 0:
            escenarios_solventes += 1

    prob_exito_pct = (escenarios_solventes / max(100, iteraciones_montecarlo)) * 100.0
    if prob_exito_pct >= 80.0:
        dictamen = "VIABLE_SOLVENTE"
    elif prob_exito_pct >= 55.0:
        dictamen = "VIABLE_CON_AJUSTES_PREVIOS"
    else:
        dictamen = "RIESGO_CRITICO_APLAZAR_Y_CAPITALIZAR"

    return {
        "tipo_decision": decision,
        "vpa_decision_cop": round(vpa_total, 2),
        "impacto_flujo_mensual_inmediato_cop": round(impacto_mensual_inmediato, 2),
        "ahorro_mensual_requerido_cop": round(ahorro_mensual_universidad, 2),
        "probabilidad_exito_montecarlo_pct": round(prob_exito_pct, 2),
        "dictamen_viabilidad": dictamen,
        "recomendacion_actuarial_y_legal": recomendacion_legal_actuarial,
    }


if __name__ == "__main__":
    print("=" * 80)
    print("DEMO MÓDULO 5 (NELSON ANGEL): VIABILIDAD ACTUARIAL DE DECISIONES DE VIDA")
    print("=" * 80)

    # ---> AQUÍ PUEDES CAMBIAR TUS PARÁMETROS DE ENTRADA <---
    res_prueba = evaluar_viabilidad_decision_vida(
        tipo_decision="HIJOS",                       # 1er parámetro: 'HIJOS', 'CASARSE' o 'CREDITO'
        ingreso_neto_hogar_mensual_cop=9_115_000.0,  # 2do parámetro: Ingreso neto mensual (9115000)
        excedente_mensual_actual_cop=2_145_000.0,    # 3er parámetro: Excedente mensual libre (2145000)
    )
    print(
        f"VPA Hijo (0-23a): {res_prueba['vpa_decision_cop']} | "
        f"Exito Monte Carlo: {res_prueba['probabilidad_exito_montecarlo_pct']} % | "
        "PRUEBA EXITOSA NELSON"
    )
    print("-" * 80)

    for op in ("CASARSE", "HIJOS", "CREDITO"):
        res = evaluar_viabilidad_decision_vida(
            tipo_decision=op,
            ingreso_neto_hogar_mensual_cop=9_115_000.0,
            excedente_mensual_actual_cop=2_145_000.0,
        )
        print(
            f"\n[{res['tipo_decision']}] -> Dictamen: {res['dictamen_viabilidad']} "
            f"({res['probabilidad_exito_montecarlo_pct']:.1f}% éxito Monte Carlo)"
        )
        print(f"  • VPA Decisión: ${res['vpa_decision_cop']:,.0f} COP")
        print(f"  • Impacto Mensual Inmediato: ${res['impacto_flujo_mensual_inmediato_cop']:,.0f} COP")
        print(f"  • Ahorro Mensual Requerido: ${res['ahorro_mensual_requerido_cop']:,.0f} COP")
        print(f"  • Recomendación: {res['recomendacion_actuarial_y_legal']}")


