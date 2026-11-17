"""
MÓDULO 4: Inversión Patrimonial en Finca Raíz Colombiana.
Responsable OED: Jesi (Administradora de Empresas - Magíster en Analítica).

Implementa de extremo a extremo el Caso de Uso CU-04 y la Guía de Jesi:
1. Clasificación regulatoria VIP (<= 90 SMMLV), VIS (<= 150 o 135 SMMLV) y No VIS (> 150 SMMLV),
   validación de topes de financiación LTV (Ley 546 de 1999) y elegibilidad de Subsidio de Caja de
   Compensación Familiar (CCF <= 4 SMMLV).
2. Plan mensual de pago de Cuota Inicial sobre planos (encargo fiduciario 18-36 meses) integrando
   ahorro previo, aportes mensuales en Cuenta AFC (con beneficio tributario Art. 126-4 E.T.),
   cesantías y primas legales.
3. Validación estricta de la Regla del 30% de la Ley 546 de 1999 (Primera cuota + seguros <= 30%
   del ingreso familiar) con cálculo exacto de brecha de ingreso o cuota inicial extra requerida.
4. Simulación comparativa mes a mes de los 3 sistemas de amortización SFC:
   - Cuota Fija en Pesos (Francés)
   - Abono Constante a Capital en Pesos (Alemán / cuota decreciente)
   - Cuota Constante en UVR indexada al IPC DANE (con sensibilidad a 3 escenarios de inflación y
     alerta FA-01 de amortización lenta en pesos), además de comparativa Hipotecario vs. Leasing Habitacional.
5. Analítica inmobiliaria nivel maestría (Buy-to-Rent bajo Ley 820 de 2003 - canon <= 1% mensual):
   NOI, Cap Rate Bruto y Neto, Cash-on-Cash Return, VPN, TIR neta de Ganancia Ocasional (15% Ley 2277/2022)
   y matriz comparativa a 10 años frente a Arrendar + Invertir en FIC Inmobiliario / Portafolio Financiero.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any, Dict, List

# Garantiza que ejecutar `python src/mod4_finca_raiz.py` funcione directamente desde cualquier consola
if __package__ in (None, ""):
    _PROJECT_ROOT = Path(__file__).resolve().parent.parent
    if str(_PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(_PROJECT_ROOT))

from src.finance import (
    calcular_tir,
    calcular_vpn,
    cargar_configuracion,
    cuota_fija_francesa,
    ea_a_em,
    valor_futuro_aportes_periodicos,
)


# ==============================================================================
# PASO 1: CLASIFICACIÓN VIS/VIP VS. NO VIS, SUBSIDIOS Y PLAN SOBRE PLANOS
# ==============================================================================


def clasificar_segmento_vivienda_colombia(
    valor_inmueble_cop: float,
    ingreso_familiar_neto_cop: float,
    aglomeracion_urbana: bool = True,
    modalidad_financiacion: str = "HIPOTECARIO",
    config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Clasifica el inmueble según los topes legales en SMMLV en Colombia, determina el porcentaje
    mínimo de cuota inicial según modalidad (Crédito Hipotecario vs. Leasing Habitacional)
    y calcula el Subsidio Familiar de Vivienda de Caja de Compensación Familiar (si aplica).
    """
    cfg = config or cargar_configuracion()
    macro = cfg["parametros_macro_colombia"]
    viv = cfg["parametros_vivienda_ley_546"]

    smmlv = float(macro["smmlv_cop"])
    tope_vip_smmlv = float(viv["tope_vip_smmlv"])
    tope_vis_smmlv = float(viv["tope_vis_smmlv"]) if aglomeracion_urbana else 135.0

    valor_en_smmlv = valor_inmueble_cop / smmlv if smmlv > 0 else 0.0
    ingreso_en_smmlv = ingreso_familiar_neto_cop / smmlv if smmlv > 0 else 0.0

    es_vis_o_vip = valor_en_smmlv <= tope_vis_smmlv
    if valor_en_smmlv <= tope_vip_smmlv:
        codigo_segmento = "VIP"
        segmento = f"VIP (Vivienda de Interés Prioritario <= {int(tope_vip_smmlv)} SMMLV)"
    elif valor_en_smmlv <= tope_vis_smmlv:
        codigo_segmento = "VIS"
        segmento = f"VIS (Vivienda de Interés Social <= {int(tope_vis_smmlv)} SMMLV)"
    else:
        codigo_segmento = "NO_VIS"
        segmento = f"No VIS (> {int(tope_vis_smmlv)} SMMLV)"

    modalidad_norm = modalidad_financiacion.strip().upper()
    if modalidad_norm == "LEASING":
        cuota_inicial_min_legal_pct = 0.15 if es_vis_o_vip else 0.20
    else:
        cuota_inicial_min_legal_pct = (
            float(viv["cuota_inicial_min_vis_pct"])
            if es_vis_o_vip
            else float(viv["cuota_inicial_min_no_vis_pct"])
        )

    # Subsidio de Caja de Compensación Familiar (CCF): aplica para VIS/VIP e ingresos <= 4 SMMLV
    if es_vis_o_vip and ingreso_en_smmlv <= 2.0:
        subsidio_ccf_smmlv = 30.0
    elif es_vis_o_vip and ingreso_en_smmlv <= 4.0:
        subsidio_ccf_smmlv = 20.0
    else:
        subsidio_ccf_smmlv = 0.0

    subsidio_ccf_potencial_cop = subsidio_ccf_smmlv * smmlv

    return {
        "codigo_segmento": codigo_segmento,
        "segmento_vivienda": segmento,
        "es_vis_o_vip": es_vis_o_vip,
        "valor_inmueble_smmlv": round(valor_en_smmlv, 2),
        "ingreso_familiar_smmlv": round(ingreso_en_smmlv, 2),
        "cuota_inicial_min_legal_pct": round(cuota_inicial_min_legal_pct, 4),
        "financiacion_max_ltv_pct": round((1.0 - cuota_inicial_min_legal_pct) * 100.0, 2),
        "elegible_subsidio_ccf": subsidio_ccf_smmlv > 0,
        "subsidio_ccf_smmlv": subsidio_ccf_smmlv,
        "subsidio_ccf_potencial_cop": round(subsidio_ccf_potencial_cop, 2),
    }


def simular_plan_cuota_inicial_planos(
    valor_inmueble_cop: float,
    ingreso_familiar_neto_cop: float,
    porcentaje_cuota_inicial: float = 0.30,
    plazo_entrega_planos_meses: int = 24,
    cesantias_y_primas_anuales_cop: float = 4_000_000.0,
    ahorro_previo_afc_cop: float = 0.0,
    aplicar_subsidio_ccf: bool = False,
    tasa_ea_encargo_fiduciario: float = 0.075,
    config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Modela el plan de pago de la Cuota Inicial sobre planos (18 a 36 meses en encargo fiduciario),
    integrando ahorro previo AFC, subsidio de Caja de Compensación Familiar (si se solicita y aplica),
    abonos extraordinarios anuales de cesantías y primas, y beneficio tributario AFC (Art. 126-4 E.T.).
    """
    cfg = config or cargar_configuracion()
    macro = cfg["parametros_macro_colombia"]
    trib = cfg["parametros_laborales_y_tributarios"]

    clasificacion = clasificar_segmento_vivienda_colombia(
        valor_inmueble_cop=valor_inmueble_cop,
        ingreso_familiar_neto_cop=ingreso_familiar_neto_cop,
        config=cfg,
    )

    cuota_inicial_total_cop = valor_inmueble_cop * porcentaje_cuota_inicial
    subsidio_aplicado_cop = (
        clasificacion["subsidio_ccf_potencial_cop"] if aplicar_subsidio_ccf else 0.0
    )

    aporte_cesantias_primas_total = (
        (plazo_entrega_planos_meses / 12.0) * cesantias_y_primas_anuales_cop
        if plazo_entrega_planos_meses > 0
        else 0.0
    )

    saldo_a_cubrir_con_salario = max(
        0.0,
        cuota_inicial_total_cop
        - ahorro_previo_afc_cop
        - subsidio_aplicado_cop
        - aporte_cesantias_primas_total,
    )
    cuota_inicial_mensual_cop = (
        saldo_a_cubrir_con_salario / plazo_entrega_planos_meses
        if plazo_entrega_planos_meses > 0
        else saldo_a_cubrir_con_salario
    )

    # Estimación de beneficio tributario por canalizar cuota mensual vía Cuenta AFC (Art. 126-4 E.T.)
    uvt_cop = float(macro["uvt_cop"])
    tope_mensual_afc_cop = min(
        ingreso_familiar_neto_cop * float(trib["beneficio_max_afc_fpv_pct"]),
        (3_800.0 * uvt_cop) / 12.0,
    )
    aporte_afc_con_beneficio = min(cuota_inicial_mensual_cop, tope_mensual_afc_cop)
    # Tarifa marginal referencial de retención para salarios medios/altos en Colombia (> 95 UVT/mes)
    aplica_retefuente_salarial = (ingreso_familiar_neto_cop / uvt_cop) > 95.0
    tasa_ahorro_tributario_estimada = 0.10 if aplica_retefuente_salarial else 0.0
    ahorro_tributario_afc_mensual_cop = aporte_afc_con_beneficio * tasa_ahorro_tributario_estimada
    ahorro_tributario_afc_total_cop = ahorro_tributario_afc_mensual_cop * max(0, plazo_entrega_planos_meses)

    # Construcción del cronograma mensual del encargo fiduciario
    tasa_em_fiducia = ea_a_em(tasa_ea_encargo_fiduciario)
    saldo_fiducia = float(ahorro_previo_afc_cop)
    rendimientos_fiducia_acumulados = 0.0
    cronograma: List[Dict[str, float]] = []

    abono_semestral_prima = (cesantias_y_primas_anuales_cop * 0.50) / 2.0
    abono_anual_cesantias = cesantias_y_primas_anuales_cop * 0.50

    for mes in range(1, max(0, plazo_entrega_planos_meses) + 1):
        extra_mes = 0.0
        if mes % 6 == 0:
            extra_mes += abono_semestral_prima
        if mes % 12 == 0:
            extra_mes += abono_anual_cesantias
        if mes == plazo_entrega_planos_meses and subsidio_aplicado_cop > 0:
            extra_mes += subsidio_aplicado_cop

        rendimiento_mes = saldo_fiducia * tasa_em_fiducia
        rendimientos_fiducia_acumulados += rendimiento_mes
        saldo_fiducia += rendimiento_mes + cuota_inicial_mensual_cop + extra_mes

        cronograma.append(
            {
                "mes": float(mes),
                "cuota_mensual_afc_cop": round(cuota_inicial_mensual_cop, 2),
                "abono_extra_cesantias_primas_subsidio_cop": round(extra_mes, 2),
                "rendimiento_fiduciario_mes_cop": round(rendimiento_mes, 2),
                "saldo_acumulado_encargo_cop": round(saldo_fiducia, 2),
            }
        )

    esfuerzo_mensual_pct_ingreso = (
        (cuota_inicial_mensual_cop / ingreso_familiar_neto_cop) * 100.0
        if ingreso_familiar_neto_cop > 0
        else 0.0
    )

    return {
        "cuota_inicial_total_cop": round(cuota_inicial_total_cop, 2),
        "porcentaje_cuota_inicial_pct": round(porcentaje_cuota_inicial * 100.0, 2),
        "cumple_cuota_inicial_minima_legal": porcentaje_cuota_inicial + 1e-9 >= clasificacion["cuota_inicial_min_legal_pct"],
        "ahorro_previo_afc_cop": round(ahorro_previo_afc_cop, 2),
        "subsidio_ccf_aplicado_cop": round(subsidio_aplicado_cop, 2),
        "aporte_cesantias_y_primas_total_cop": round(aporte_cesantias_primas_total, 2),
        "cuota_inicial_mensual_cop": round(cuota_inicial_mensual_cop, 2),
        "esfuerzo_mensual_cuota_inicial_pct": round(esfuerzo_mensual_pct_ingreso, 2),
        "ahorro_tributario_afc_mensual_cop": round(ahorro_tributario_afc_mensual_cop, 2),
        "ahorro_tributario_afc_total_cop": round(ahorro_tributario_afc_total_cop, 2),
        "rendimientos_encargo_fiduciario_cop": round(rendimientos_fiducia_acumulados, 2),
        "cronograma_fiduciario_mensual": cronograma,
    }


# ==============================================================================
# PASO 2: SIMULADOR LEY 546 DE 1999 — PESOS FIJOS VS. ABONO CAPITAL VS. UVR
# ==============================================================================


def simular_sistemas_amortizacion_ley_546(
    monto_credito_cop: float,
    plazo_credito_anios: int = 15,
    tasa_ea_pesos: float = 0.115,
    tasa_ea_uvr_mas_spread: float = 0.065,
    ipc_anual_proyectado: float | None = None,
    tasa_seguros_mensual_pct: float = 0.00065,
    config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Simula mes a mes los 3 sistemas de amortización hipotecaria vigilados por la SFC en Colombia:
    1. Cuota Fija en Pesos (Francés).
    2. Abono Constante a Capital en Pesos (Cuota decreciente).
    3. Cuota Constante en UVR (Sistema Cíclico indexado a la inflación IPC DANE),
       incluyendo análisis de sensibilidad inflacionaria y alerta FA-01 de amortización lenta en pesos.
    """
    cfg = config or cargar_configuracion()
    macro = cfg["parametros_macro_colombia"]
    ipc_base = float(ipc_anual_proyectado if ipc_anual_proyectado is not None else macro["ipc_anual_dane"])
    uvr_inicial = float(macro["uvr_valor_cop"])

    plazo_meses = max(1, int(plazo_credito_anios * 12))
    tasa_em_pesos = ea_a_em(tasa_ea_pesos)
    tasa_em_uvr_real = ea_a_em(tasa_ea_uvr_mas_spread)
    inflacion_mensual = ea_a_em(ipc_base)

    seguro_mensual_inicial_cop = monto_credito_cop * tasa_seguros_mensual_pct

    # --- 1. Sistema Francés: Cuota Fija en Pesos ---
    cuota_pesos_fija_sin_seguro = cuota_fija_francesa(monto_credito_cop, tasa_em_pesos, plazo_meses)
    saldo_pesos_fija = float(monto_credito_cop)
    total_intereses_pesos_fija = 0.0
    total_pagado_pesos_fija = 0.0
    tabla_pesos_fija: List[Dict[str, float]] = []

    for mes in range(1, plazo_meses + 1):
        interes_mes = saldo_pesos_fija * tasa_em_pesos
        abono_capital = min(saldo_pesos_fija, cuota_pesos_fija_sin_seguro - interes_mes)
        seguro_mes = seguro_mensual_inicial_cop  # Seguro referencial nivelado para comparabilidad con Ley 546
        cuota_total_mes = abono_capital + interes_mes + seguro_mes
        saldo_pesos_fija = max(0.0, saldo_pesos_fija - abono_capital)
        total_intereses_pesos_fija += interes_mes
        total_pagado_pesos_fija += cuota_total_mes

        tabla_pesos_fija.append(
            {
                "mes": float(mes),
                "anio": round(mes / 12.0, 2),
                "cuota_total_cop": round(cuota_total_mes, 2),
                "interes_cop": round(interes_mes, 2),
                "abono_capital_cop": round(abono_capital, 2),
                "seguros_cop": round(seguro_mes, 2),
                "saldo_capital_cop": round(saldo_pesos_fija, 2),
            }
        )

    # --- 2. Sistema Alemán: Abono Constante a Capital en Pesos ---
    abono_constante_capital = monto_credito_cop / plazo_meses if monto_credito_cop > 0 else 0.0
    saldo_pesos_constante = float(monto_credito_cop)
    total_intereses_abono_constante = 0.0
    total_pagado_abono_constante = 0.0
    primera_cuota_abono_constante_cop = 0.0
    tabla_abono_constante: List[Dict[str, float]] = []

    for mes in range(1, plazo_meses + 1):
        interes_mes = saldo_pesos_constante * tasa_em_pesos
        abono_cap = min(saldo_pesos_constante, abono_constante_capital)
        seguro_mes = seguro_mensual_inicial_cop
        cuota_total_mes = abono_cap + interes_mes + seguro_mes
        if mes == 1:
            primera_cuota_abono_constante_cop = cuota_total_mes
        saldo_pesos_constante = max(0.0, saldo_pesos_constante - abono_cap)
        total_intereses_abono_constante += interes_mes
        total_pagado_abono_constante += cuota_total_mes

        tabla_abono_constante.append(
            {
                "mes": float(mes),
                "anio": round(mes / 12.0, 2),
                "cuota_total_cop": round(cuota_total_mes, 2),
                "interes_cop": round(interes_mes, 2),
                "abono_capital_cop": round(abono_cap, 2),
                "saldo_capital_cop": round(saldo_pesos_constante, 2),
            }
        )

    # --- 3. Sistema Cuota Constante en UVR (indexado a IPC DANE) ---
    monto_inicial_uvr = monto_credito_cop / uvr_inicial if uvr_inicial > 0 else 0.0
    cuota_constante_en_uvr = cuota_fija_francesa(monto_inicial_uvr, tasa_em_uvr_real, plazo_meses)
    primera_cuota_uvr_sin_seguro_cop = cuota_fija_francesa(monto_credito_cop, tasa_em_uvr_real, plazo_meses)
    primera_cuota_uvr_total_cop = primera_cuota_uvr_sin_seguro_cop + seguro_mensual_inicial_cop

    saldo_uvr = float(monto_inicial_uvr)
    uvr_actual = float(uvr_inicial)
    total_intereses_uvr_cop = 0.0
    total_pagado_uvr_cop = 0.0
    max_saldo_pesos_uvr = float(monto_credito_cop)
    mes_pico_saldo_pesos_uvr = 0
    tabla_uvr: List[Dict[str, float]] = []

    for mes in range(1, plazo_meses + 1):
        uvr_actual *= 1.0 + inflacion_mensual
        interes_uvr = saldo_uvr * tasa_em_uvr_real
        abono_capital_uvr = min(saldo_uvr, cuota_constante_en_uvr - interes_uvr)
        saldo_uvr = max(0.0, saldo_uvr - abono_capital_uvr)

        interes_cop = interes_uvr * uvr_actual
        abono_capital_cop = abono_capital_uvr * uvr_actual
        seguro_mes_uvr = seguro_mensual_inicial_cop * ((1.0 + inflacion_mensual) ** (mes - 1))
        cuota_total_uvr_mes_cop = interes_cop + abono_capital_cop + seguro_mes_uvr
        saldo_uvr_en_pesos = saldo_uvr * uvr_actual

        if saldo_uvr_en_pesos > max_saldo_pesos_uvr + 1.0:
            max_saldo_pesos_uvr = saldo_uvr_en_pesos
            mes_pico_saldo_pesos_uvr = mes

        total_intereses_uvr_cop += interes_cop
        total_pagado_uvr_cop += cuota_total_uvr_mes_cop

        tabla_uvr.append(
            {
                "mes": float(mes),
                "anio": round(mes / 12.0, 2),
                "valor_uvr_cop": round(uvr_actual, 4),
                "cuota_total_cop": round(cuota_total_uvr_mes_cop, 2),
                "interes_cop": round(interes_cop, 2),
                "abono_capital_cop": round(abono_capital_cop, 2),
                "saldo_uvr": round(saldo_uvr, 4),
                "saldo_capital_cop": round(saldo_uvr_en_pesos, 2),
            }
        )

    # Sensibilidad de la cuota UVR al Año 5 bajo 3 escenarios de inflación IPC
    escenarios_ipc = {
        "ipc_bajo_3_5pct_cop": round(primera_cuota_uvr_total_cop * ((1.0 + 0.035) ** 5), 2),
        "ipc_base_dane_cop": round(primera_cuota_uvr_total_cop * ((1.0 + ipc_base) ** 5), 2),
        "ipc_alto_choque_8_5pct_cop": round(primera_cuota_uvr_total_cop * ((1.0 + 0.085) ** 5), 2),
    }

    crece_saldo_nominal_pesos = mes_pico_saldo_pesos_uvr > 0

    return {
        "plazo_meses": plazo_meses,
        "primera_cuota_pesos_fija_cop": round(cuota_pesos_fija_sin_seguro + seguro_mensual_inicial_cop, 2),
        "primera_cuota_abono_constante_cop": round(primera_cuota_abono_constante_cop, 2),
        "primera_cuota_uvr_cop": round(primera_cuota_uvr_total_cop, 2),
        "cuota_uvr_proyectada_anio_5_cop": round(primera_cuota_uvr_total_cop * ((1.0 + ipc_base) ** 5), 2),
        "cuota_uvr_proyectada_anio_10_cop": round(primera_cuota_uvr_total_cop * ((1.0 + ipc_base) ** 10), 2),
        "sensibilidad_cuota_uvr_anio_5": escenarios_ipc,
        "total_intereses_pesos_fija_cop": round(total_intereses_pesos_fija, 2),
        "total_intereses_abono_constante_cop": round(total_intereses_abono_constante, 2),
        "total_intereses_uvr_cop": round(total_intereses_uvr_cop, 2),
        "total_pagado_pesos_fija_cop": round(total_pagado_pesos_fija, 2),
        "total_pagado_abono_constante_cop": round(total_pagado_abono_constante, 2),
        "total_pagado_uvr_cop": round(total_pagado_uvr_cop, 2),
        "ahorro_intereses_abono_constante_vs_fija_cop": round(
            total_intereses_pesos_fija - total_intereses_abono_constante, 2
        ),
        "alerta_riesgo_uvr_fa01": crece_saldo_nominal_pesos,
        "mes_pico_saldo_pesos_uvr": mes_pico_saldo_pesos_uvr,
        "pico_saldo_pesos_uvr_cop": round(max_saldo_pesos_uvr, 2),
        "tabla_pesos_cuota_fija": tabla_pesos_fija,
        "tabla_pesos_abono_constante": tabla_abono_constante,
        "tabla_uvr_ciclica": tabla_uvr,
    }


# ==============================================================================
# PASO 3 Y FUNCIÓN INTEGRADA CU-04: EVALUACIÓN INTEGRAL DE FINCA RAÍZ
# ==============================================================================


def evaluar_inversion_finca_raiz(
    valor_inmueble_cop: float,
    ingreso_familiar_neto_cop: float,
    porcentaje_cuota_inicial: float = 0.30,
    plazo_entrega_planos_meses: int = 24,
    cesantias_y_primas_anuales_cop: float = 4_000_000.0,
    plazo_credito_anios: int = 15,
    tasa_ea_pesos: float = 0.115,
    tasa_ea_uvr_mas_spread: float = 0.065,
    canon_arriendo_mensual_estimado_cop: float | None = None,
    costo_oportunidad_ea: float = 0.105,
    ahorro_previo_afc_cop: float = 0.0,
    aplicar_subsidio_ccf: bool = False,
    modalidad_financiacion: str = "HIPOTECARIO",
    incluir_tablas_detalle: bool = False,
    config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Ejecuta el Caso de Uso CU-04 (Módulo 4 - Jesi):
    Evalúa de forma integral la viabilidad regulatoria, crediticia y financiera de adquirir
    finca raíz en Colombia (vivienda propia o inversión para renta) frente a alternativas financieras.
    """
    cfg = config or cargar_configuracion()
    macro = cfg["parametros_macro_colombia"]
    viv = cfg["parametros_vivienda_ley_546"]
    trib = cfg["parametros_laborales_y_tributarios"]

    ipc_anual = float(macro["ipc_anual_dane"])
    tasa_ganancia_ocasional = float(trib.get("ganancia_ocasional_pct", 0.15))
    tasa_seguros_mensual = 0.00065  # ~0.065% mensual seguro de vida deudor + incendio y terremoto

    alertas: List[str] = []

    # 1. Clasificación regulatoria VIS / VIP / No VIS y Subsidios
    clasificacion = clasificar_segmento_vivienda_colombia(
        valor_inmueble_cop=valor_inmueble_cop,
        ingreso_familiar_neto_cop=ingreso_familiar_neto_cop,
        modalidad_financiacion=modalidad_financiacion,
        config=cfg,
    )

    if porcentaje_cuota_inicial + 1e-9 < clasificacion["cuota_inicial_min_legal_pct"]:
        alertas.append(
            f"Alerta LTV Ley 546/1999: Para {clasificacion['codigo_segmento']} bajo modalidad "
            f"{modalidad_financiacion.upper()}, la cuota inicial mínima regulatoria es "
            f"{clasificacion['cuota_inicial_min_legal_pct'] * 100:.0f}%."
        )

    # 2. Plan de Cuota Inicial sobre planos (Encargo Fiduciario + Cesantías + AFC + Subsidio CCF)
    plan_inicial = simular_plan_cuota_inicial_planos(
        valor_inmueble_cop=valor_inmueble_cop,
        ingreso_familiar_neto_cop=ingreso_familiar_neto_cop,
        porcentaje_cuota_inicial=porcentaje_cuota_inicial,
        plazo_entrega_planos_meses=plazo_entrega_planos_meses,
        cesantias_y_primas_anuales_cop=cesantias_y_primas_anuales_cop,
        ahorro_previo_afc_cop=ahorro_previo_afc_cop,
        aplicar_subsidio_ccf=aplicar_subsidio_ccf,
        config=cfg,
    )

    cuota_inicial_total_cop = plan_inicial["cuota_inicial_total_cop"]
    monto_credito_cop = max(0.0, valor_inmueble_cop - cuota_inicial_total_cop)

    # En Leasing Habitacional los gastos de escrituración ocurren al ejercer la opción de compra al final
    modalidad_norm = modalidad_financiacion.strip().upper()
    gastos_escrituracion_cop = (
        0.0
        if modalidad_norm == "LEASING"
        else valor_inmueble_cop * float(viv["gastos_escrituracion_registro_pct"])
    )

    # 3. Simulación de Sistemas de Amortización y Validación de Ley 546 de 1999 (Regla del 30%)
    amortizacion = simular_sistemas_amortizacion_ley_546(
        monto_credito_cop=monto_credito_cop,
        plazo_credito_anios=plazo_credito_anios,
        tasa_ea_pesos=tasa_ea_pesos,
        tasa_ea_uvr_mas_spread=tasa_ea_uvr_mas_spread,
        ipc_anual_proyectado=ipc_anual,
        tasa_seguros_mensual_pct=tasa_seguros_mensual,
        config=cfg,
    )

    primera_cuota_pesos_total = amortizacion["primera_cuota_pesos_fija_cop"]
    primera_cuota_uvr_en_pesos = amortizacion["primera_cuota_uvr_cop"]
    cuota_uvr_anio_5_cop = amortizacion["cuota_uvr_proyectada_anio_5_cop"]

    relacion_max = float(viv["relacion_max_cuota_ingreso"])
    tope_cuota_ley_546_cop = ingreso_familiar_neto_cop * relacion_max
    cumple_ley_546_pesos = primera_cuota_pesos_total <= (tope_cuota_ley_546_cop + 1e-6)
    cumple_ley_546_uvr = primera_cuota_uvr_en_pesos <= (tope_cuota_ley_546_cop + 1e-6)
    ingreso_familiar_minimo_pesos = (
        primera_cuota_pesos_total / relacion_max if relacion_max > 0 else 0.0
    )
    deficit_ingreso_familiar_cop = (
        float(math.ceil(max(0.0, ingreso_familiar_minimo_pesos - ingreso_familiar_neto_cop)))
        if not cumple_ley_546_pesos
        else 0.0
    )

    # Cálculo exacto de cuánta cuota inicial extra se requiere si supera el 30% en Pesos
    plazo_meses = plazo_credito_anios * 12
    tasa_em_pesos = ea_a_em(tasa_ea_pesos)
    factor_unitario_cuota_pesos = cuota_fija_francesa(1.0, tasa_em_pesos, plazo_meses) + tasa_seguros_mensual
    credito_maximo_ley_546_pesos = (
        tope_cuota_ley_546_cop / factor_unitario_cuota_pesos if factor_unitario_cuota_pesos > 0 else 0.0
    )
    cuota_inicial_extra_requerida_cop = (
        float(math.ceil(max(0.0, monto_credito_cop - credito_maximo_ley_546_pesos)))
        if not cumple_ley_546_pesos
        else 0.0
    )

    if not cumple_ley_546_pesos:
        alertas.append(
            f"Restricción Ley 546 de 1999: La primera cuota en Pesos (${primera_cuota_pesos_total:,.0f} COP) "
            f"supera el 30% del ingreso familiar (${tope_cuota_ley_546_cop:,.0f} COP). "
            f"Requiere acreditar ${deficit_ingreso_familiar_cop:,.0f} COP adicionales de ingreso familiar "
            f"o aportar ${cuota_inicial_extra_requerida_cop:,.0f} COP extra en la cuota inicial."
        )

    if amortizacion["alerta_riesgo_uvr_fa01"]:
        alertas.append(
            f"Alerta FA-01 Riesgo UVR: Con inflación anual del {ipc_anual * 100:.1f}%, el saldo expresado en pesos "
            f"crece durante los primeros {amortizacion['mes_pico_saldo_pesos_uvr']} meses hasta "
            f"${amortizacion['pico_saldo_pesos_uvr_cop']:,.0f} COP por indexación inflacionaria."
        )

    # 4. Analítica de Rentabilidad Inmobiliaria (Ley 820 de 2003: Canon <= 1% del valor comercial)
    tope_canon_ley_820 = valor_inmueble_cop * float(viv["canon_max_ley_820_mensual_pct"])
    canon_estimado_usuario = (
        canon_arriendo_mensual_estimado_cop
        if canon_arriendo_mensual_estimado_cop is not None
        else valor_inmueble_cop * 0.0065
    )
    recortado_por_ley_820 = canon_estimado_usuario > (tope_canon_ley_820 + 1e-6)
    canon_mensual = min(canon_estimado_usuario, tope_canon_ley_820)

    if recortado_por_ley_820:
        alertas.append(
            f"Tope Legal Ley 820 de 2003 (Art. 18): El canon mensual estimado (${canon_estimado_usuario:,.0f} COP) "
            f"se ajustó al límite legal del 1% del valor comercial (${tope_canon_ley_820:,.0f} COP)."
        )

    ingreso_bruto_anual_renta = canon_mensual * 12.0 * (1.0 - 0.05)  # 5% vacancia técnica
    costos_operativos_anuales = (
        valor_inmueble_cop * 0.008  # Impuesto predial (~0.45%) + provisión mantenimiento (~0.35%)
        + (canon_mensual * 12.0 * 0.12)  # Administración / comisión gestión inmobiliaria
    )
    noi_ingreso_operativo_neto_anual = max(0.0, ingreso_bruto_anual_renta - costos_operativos_anuales)
    cap_rate_bruto = (canon_mensual * 12.0) / valor_inmueble_cop if valor_inmueble_cop > 0 else 0.0
    cap_rate_neto = noi_ingreso_operativo_neto_anual / valor_inmueble_cop if valor_inmueble_cop > 0 else 0.0

    # 5. Flujo de Caja a 10 años, Cash-on-Cash, VPN, TIR y Comparativa Patrimonial vs. FIC Inmobiliario
    desembolso_inicial = cuota_inicial_total_cop + gastos_escrituracion_cop
    servicio_deuda_anual_pesos = primera_cuota_pesos_total * 12.0
    flujo_caja_neto_anio_1 = noi_ingreso_operativo_neto_anual - servicio_deuda_anual_pesos
    cash_on_cash_pct = (
        (flujo_caja_neto_anio_1 / desembolso_inicial) * 100.0 if desembolso_inicial > 0 else 0.0
    )

    flujos_anuales_pesos: List[float] = [-desembolso_inicial]
    valorizacion_anual = ipc_anual + 0.015  # IPC + 1.5% de valorización real urbana

    # Saldo real exacto de la tabla de amortización en el mes 120 (o 0 si el plazo es <= 10 años)
    mes_corte_10a = min(120, len(amortizacion["tabla_pesos_cuota_fija"]))
    saldo_deuda_pesos_anio_10 = (
        amortizacion["tabla_pesos_cuota_fija"][mes_corte_10a - 1]["saldo_capital_cop"]
        if plazo_credito_anios > 10 and mes_corte_10a > 0
        else 0.0
    )
    saldo_deuda_uvr_anio_10 = (
        amortizacion["tabla_uvr_ciclica"][mes_corte_10a - 1]["saldo_capital_cop"]
        if plazo_credito_anios > 10 and mes_corte_10a > 0
        else 0.0
    )

    valor_venta_anio_10 = valor_inmueble_cop * ((1.0 + valorizacion_anual) ** 10)
    ganancia_ocasional_impuesto = max(
        0.0, (valor_venta_anio_10 - valor_inmueble_cop) * tasa_ganancia_ocasional
    )

    for anio in range(1, 11):
        noi_t = noi_ingreso_operativo_neto_anual * ((1.0 + ipc_anual) ** (anio - 1))
        servicio_t = servicio_deuda_anual_pesos if anio <= plazo_credito_anios else 0.0
        flujo_neto_t = noi_t - servicio_t
        if anio == 10:
            flujo_neto_t += valor_venta_anio_10 - ganancia_ocasional_impuesto - saldo_deuda_pesos_anio_10
        flujos_anuales_pesos.append(round(flujo_neto_t, 2))

    vpn_inmobiliario = calcular_vpn(costo_oportunidad_ea, flujos_anuales_pesos)
    tir_inmobiliaria = calcular_tir(flujos_anuales_pesos)

    # Comparativa Estratégica a 10 años (CU-04 paso 5):
    # Opción 1: Patrimonio neto comprando en Pesos Fijos
    patrimonio_neto_10a_pesos = valor_venta_anio_10 - ganancia_ocasional_impuesto - saldo_deuda_pesos_anio_10
    # Opción 2: Patrimonio neto comprando en UVR
    patrimonio_neto_10a_uvr = valor_venta_anio_10 - ganancia_ocasional_impuesto - saldo_deuda_uvr_anio_10
    # Opción 3: Arrendar vivienda equivalente e invertir el desembolso inicial + ahorro mensual de cuota en FIC/CDT
    diferencial_mensual_vs_arriendo = max(0.0, primera_cuota_pesos_total - canon_mensual)
    proyeccion_fic_alternativo = valor_futuro_aportes_periodicos(
        aporte_mensual_cop=diferencial_mensual_vs_arriendo,
        tasa_ea=costo_oportunidad_ea,
        meses=120,
        capital_inicial_cop=desembolso_inicial,
    )
    patrimonio_neto_10a_fic = proyeccion_fic_alternativo["valor_futuro_nominal_cop"]

    # Semáforo Ejecutivo de Decisión Inmobiliaria
    if cumple_ley_546_pesos and vpn_inmobiliario >= 0:
        dictamen = "VIABLE_COMPRA_EN_PESOS_OPTIMA"
    elif cumple_ley_546_pesos and vpn_inmobiliario < 0:
        dictamen = "VIABLE_VIVIENDA_PROPIA_PERO_FIC_SUPERA_RENTA"
    elif cumple_ley_546_uvr and not cumple_ley_546_pesos:
        dictamen = "SOLO_CUMPLE_EN_UVR_CON_RIESGO_INFLACIONARIO"
    else:
        dictamen = "REQUIERE_MAYOR_CUOTA_INICIAL_O_INGRESO_LEY_546"

    resultado: Dict[str, Any] = {
        # --- Llaves del Contrato de Integración OED (100% compatibles) ---
        "segmento_vivienda": clasificacion["segmento_vivienda"],
        "valor_inmueble_smmlv": clasificacion["valor_inmueble_smmlv"],
        "cuota_inicial_total_cop": round(cuota_inicial_total_cop, 2),
        "gastos_escrituracion_registro_cop": round(gastos_escrituracion_cop, 2),
        "cuota_inicial_mensual_cop": plan_inicial["cuota_inicial_mensual_cop"],
        "monto_credito_hipotecario_cop": round(monto_credito_cop, 2),
        "primera_cuota_credito_cop": round(primera_cuota_pesos_total, 2),
        "primera_cuota_uvr_cop": round(primera_cuota_uvr_en_pesos, 2),
        "cuota_uvr_proyectada_anio_5_cop": round(cuota_uvr_anio_5_cop, 2),
        "tope_cuota_ley_546_30pct_cop": round(tope_cuota_ley_546_cop, 2),
        "cumple_ley_546_30pct": cumple_ley_546_pesos,
        "cumple_ley_546_en_uvr": cumple_ley_546_uvr,
        "ingreso_familiar_minimo_requerido_cop": round(ingreso_familiar_minimo_pesos, 2),
        "cap_rate_neto_pct": round(cap_rate_neto * 100.0, 2),
        "vpn_inmobiliario_cop": round(vpn_inmobiliario, 2),
        "tir_inmobiliaria_ea_pct": round(tir_inmobiliaria * 100.0, 2),
        # --- Analítica Extendida de Jesi (Maestría en Analítica) ---
        "codigo_segmento": clasificacion["codigo_segmento"],
        "modalidad_financiacion": modalidad_norm,
        "elegible_subsidio_ccf": clasificacion["elegible_subsidio_ccf"],
        "subsidio_ccf_potencial_cop": clasificacion["subsidio_ccf_potencial_cop"],
        "subsidio_ccf_aplicado_cop": plan_inicial["subsidio_ccf_aplicado_cop"],
        "ahorro_tributario_afc_total_cop": plan_inicial["ahorro_tributario_afc_total_cop"],
        "deficit_ingreso_familiar_cop": round(deficit_ingreso_familiar_cop, 2),
        "cuota_inicial_extra_requerida_ley_546_cop": round(cuota_inicial_extra_requerida_cop, 2),
        "primera_cuota_abono_constante_cop": amortizacion["primera_cuota_abono_constante_cop"],
        "sensibilidad_cuota_uvr_anio_5": amortizacion["sensibilidad_cuota_uvr_anio_5"],
        "alerta_riesgo_uvr_fa01": amortizacion["alerta_riesgo_uvr_fa01"],
        "canon_mensual_aplicado_cop": round(canon_mensual, 2),
        "tope_canon_ley_820_cop": round(tope_canon_ley_820, 2),
        "recortado_por_ley_820": recortado_por_ley_820,
        "noi_anual_cop": round(noi_ingreso_operativo_neto_anual, 2),
        "cap_rate_bruto_pct": round(cap_rate_bruto * 100.0, 2),
        "cash_on_cash_anual_pct": round(cash_on_cash_pct, 2),
        "flujos_anuales_inversionista_cop": flujos_anuales_pesos,
        "comparativa_estrategias_10a": {
            "comprar_pesos_patrimonio_10a_cop": round(patrimonio_neto_10a_pesos, 2),
            "comprar_uvr_patrimonio_10a_cop": round(patrimonio_neto_10a_uvr, 2),
            "arrendar_e_invertir_fic_patrimonio_10a_cop": round(patrimonio_neto_10a_fic, 2),
            "total_intereses_pesos_fija_cop": amortizacion["total_intereses_pesos_fija_cop"],
            "total_intereses_abono_constante_cop": amortizacion["total_intereses_abono_constante_cop"],
            "total_intereses_uvr_cop": amortizacion["total_intereses_uvr_cop"],
        },
        "dictamen_viabilidad_inmobiliaria": dictamen,
        "alertas_regulatorias": alertas,
    }

    if incluir_tablas_detalle:
        resultado["plan_cuota_inicial_detalle"] = plan_inicial
        resultado["amortizacion_detalle"] = amortizacion

    return resultado


# ==============================================================================
# ZONA DE PRUEBAS AUTÓNOMA DE JESI (CORRE SIN DEPENDER DE LOS OTROS MÓDULOS)
# ==============================================================================
if __name__ == "__main__":
    print("=" * 72)
    print("SIMULADOR MÓDULO 4: INVERSIÓN PATRIMONIAL EN FINCA RAÍZ (JESI - OED)")
    print("=" * 72)

    escenarios_demo = [
        {
            "titulo": "ESCENARIO A — Caso Maestro OED (Apartamento VIS sobre planos $200M)",
            "valor_inmueble_cop": 200_000_000.0,
            "ingreso_familiar_neto_cop": 9_415_000.0,  # Usuario semilla + pareja
            "porcentaje_cuota_inicial": 0.30,
            "cesantias_y_primas_anuales_cop": 5_500_000.0,
            "ahorro_previo_afc_cop": 8_000_000.0,
        },
        {
            "titulo": "ESCENARIO B — Apartamento No VIS ($320M) con un solo salario ($6.5M)",
            "valor_inmueble_cop": 320_000_000.0,
            "ingreso_familiar_neto_cop": 5_915_000.0,
            "porcentaje_cuota_inicial": 0.30,
            "cesantias_y_primas_anuales_cop": 4_000_000.0,
            "ahorro_previo_afc_cop": 0.0,
        },
    ]

    for esc in escenarios_demo:
        print(f"\n>>> {esc['titulo']}")
        res = evaluar_inversion_finca_raiz(
            valor_inmueble_cop=esc["valor_inmueble_cop"],
            ingreso_familiar_neto_cop=esc["ingreso_familiar_neto_cop"],
            porcentaje_cuota_inicial=esc["porcentaje_cuota_inicial"],
            cesantias_y_primas_anuales_cop=esc["cesantias_y_primas_anuales_cop"],
            ahorro_previo_afc_cop=esc["ahorro_previo_afc_cop"],
        )
        print(f"  • Clasificación: {res['segmento_vivienda']} ({res['valor_inmueble_smmlv']} SMMLV)")
        print(
            f"  • Cuota Inicial (30%): ${res['cuota_inicial_total_cop']:,.0f} COP "
            f"| Aporte mensual sobre planos (24m): ${res['cuota_inicial_mensual_cop']:,.0f} COP"
        )
        print(
            f"  • Ley 546 (Tope 30% ingreso = ${res['tope_cuota_ley_546_30pct_cop']:,.0f} COP):"
        )
        print(
            f"      - 1ra Cuota Pesos Fija: ${res['primera_cuota_credito_cop']:,.0f} COP "
            f"-> {'CUMPLE' if res['cumple_ley_546_30pct'] else 'NO CUMPLE'}"
        )
        print(
            f"      - 1ra Cuota UVR:        ${res['primera_cuota_uvr_cop']:,.0f} COP "
            f"(Año 5 proyectada: ${res['cuota_uvr_proyectada_anio_5_cop']:,.0f} COP)"
        )
        if not res["cumple_ley_546_30pct"]:
            print(
                f"      - Ajuste requerido Ley 546: +${res['deficit_ingreso_familiar_cop']:,.0f} COP de ingreso "
                f"o +${res['cuota_inicial_extra_requerida_ley_546_cop']:,.0f} COP de cuota inicial extra."
            )
        print(
            f"  • Rentabilidad Renta (Ley 820): Cap Rate Neto = {res['cap_rate_neto_pct']}% | "
            f"TIR = {res['tir_inmobiliaria_ea_pct']}% EA | VPN = ${res['vpn_inmobiliario_cop']:,.0f} COP"
        )
        print(f"  • Dictamen Ejecutivo: {res['dictamen_viabilidad_inmobiliaria']}")
