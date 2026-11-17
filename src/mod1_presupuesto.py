"""
MÓDULO 1: Radiografía del Sueldo, Presupuesto Personal, Ingeniería del Flujo de Caja y Gastos Hormiga.
Responsable OED: Nidia Velásquez (Ingeniera Mecánica - Especialista en Presupuestos).

Enfoque de Ingeniería (Balance Termodinámico / Hidráulico de Flujo de Caja):
- Modela el salario como un fluido de entrada sometido a pérdidas de carga obligatorias (descuentos de ley),
  consumo operativo vital (costos fijos), consumo discrecional (estilo de vida) y "fugas de presión"
  (gastos hormiga cotidianos + fricciones bancarias como 4x1000 GMF y cuotas de manejo).
- Implementa:
  1. Radiografía del Sueldo Colombiano: Empleado Ordinario, Salario Integral (>= 13 SMMLV, IBC 70%)
     y Contratista Independiente OPS (IBC 40%, mínimo 1 SMMLV, ARL Clases I a V), incluyendo Salud,
     Pensión, Fondo de Solidaridad Pensional (FSP 1%-2%), Retención en la Fuente en UVT (Art. 383 y 336 E.T.
     - Ley 2277 de 2022), optimización tributaria vía cuentas AFC/FPV y provisiones prestacionales reales.
  2. Matriz de Balance 50/30/20 adaptada a Colombia.
  3. Detector y cuantificador de Gastos Hormiga y Fugas Financieras (4x1000 + cuotas de manejo) con
     proyección de Costo de Oportunidad compuesto a 5 y 10 años (nominal y real neto de IPC).
  4. Termómetro de Fondo de Emergencia (meta 3 meses empleados, 6 meses independientes) y flujos
     alternativos CU-01 (FA-01 Déficit Crítico y FA-02 Construcción Prioritaria de Liquidez 80/20).
  5. Generadores de estructuras y visualizaciones interactivas en Plotly (Sankey, Waterfall,
     Costo de Oportunidad y Diagnóstico 50/30/20).
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from src.finance import (
    calcular_gmf_4x1000,
    calcular_tasa_real_neta,
    cargar_configuracion,
    cop_a_uvt,
    uvt_a_cop,
    valor_futuro_aportes_periodicos,
)

# Tarifas legales de ARL en Colombia por Clase de Riesgo (Decreto 1607 de 2002 / MinTrabajo)
TARIFAS_ARL_COLOMBIA: Dict[int, float] = {
    1: 0.00522,  # Clase I: Riesgo mínimo (financiero, oficina, consultoría) - 0.522%
    2: 0.01044,  # Clase II: Riesgo bajo (comercial, manufactura liviana) - 1.044%
    3: 0.02436,  # Clase III: Riesgo medio (talleres, procesos mecánicos) - 2.436%
    4: 0.04350,  # Clase IV: Riesgo alto (transporte, construcción liviana) - 4.350%
    5: 0.06960,  # Clase V: Riesgo máximo (minería, trabajo en alturas/pesado) - 6.960%
}


# ==============================================================================
# 1. RADIOGRAFÍA DEL SUELDO Y MOTOR DE NÓMINA COLOMBIANA
# ==============================================================================


def calcular_fsp_porcentaje(ingreso_en_smmlv: float) -> float:
    """
    Calcula el porcentaje de aporte al Fondo de Solidaridad Pensional (Ley 100 de 1993 / Ley 797 de 2003):
    - Menos de 4 SMMLV: 0%
    - De 4 a <16 SMMLV: 1.0% (0.5% solidaridad + 0.5% subsistencia)
    - De 16 a <17 SMMLV: 1.2%
    - De 17 a <18 SMMLV: 1.4%
    - De 18 a <19 SMMLV: 1.6%
    - De 19 a 20 SMMLV: 1.8%
    - Más de 20 SMMLV: 2.0%
    """
    if ingreso_en_smmlv < 4.0:
        return 0.0
    if ingreso_en_smmlv < 16.0:
        return 0.010
    if ingreso_en_smmlv < 17.0:
        return 0.012
    if ingreso_en_smmlv < 18.0:
        return 0.014
    if ingreso_en_smmlv < 19.0:
        return 0.016
    if ingreso_en_smmlv <= 20.0:
        return 0.018
    return 0.020


def estimar_retefuente_mensual_art_383(
    ingreso_neto_tributario_cop: float,
    uvt_cop: float,
    aporte_afc_fpv_cop: float = 0.0,
) -> float:
    """
    Calcula la Retención en la Fuente mensual para rentas de trabajo
    (Art. 383 y Art. 336 Estatuto Tributario - Reforma Ley 2277 de 2022):
    - Parte del ingreso neto tributario (Ingreso bruto - INCRNGO Salud/Pensión/FSP).
    - Descuenta aportes voluntarios AFC/FPV y aplica el 25% de renta exenta laboral
      (Art. 206 num. 10, con tope mensual de 790/12 UVT).
    - Aplica el límite global del 40% del ingreso neto tributario y 1.340/12 UVT mensuales
      a la suma de rentas exentas (AFC/FPV + 25%).
    - Aplica la tabla progresiva completa del Art. 383 E.T. (0%, 19%, 28%, 33%, 35%, 37%, 39%).
    """
    if ingreso_neto_tributario_cop <= 0:
        return 0.0

    afc_aplicable = max(0.0, min(aporte_afc_fpv_cop, ingreso_neto_tributario_cop))
    base_para_25 = max(0.0, ingreso_neto_tributario_cop - afc_aplicable)

    tope_mensual_exenta_25_cop = uvt_a_cop(790.0 / 12.0, uvt_cop)
    renta_exenta_25 = min(base_para_25 * 0.25, tope_mensual_exenta_25_cop)

    # Tope global cédula general Ley 2277 de 2022: mín(40% ingreso neto tributario, 1340/12 UVT)
    tope_global_40_pct = ingreso_neto_tributario_cop * 0.40
    tope_global_uvt_cop = uvt_a_cop(1340.0 / 12.0, uvt_cop)
    beneficios_totales = min(afc_aplicable + renta_exenta_25, tope_global_40_pct, tope_global_uvt_cop)

    base_gravable_cop = max(0.0, ingreso_neto_tributario_cop - beneficios_totales)
    base_uvt = cop_a_uvt(base_gravable_cop, uvt_cop)

    if base_uvt <= 95.0:
        impuesto_uvt = 0.0
    elif base_uvt <= 150.0:
        impuesto_uvt = (base_uvt - 95.0) * 0.19
    elif base_uvt <= 360.0:
        impuesto_uvt = (base_uvt - 150.0) * 0.28 + 10.45
    elif base_uvt <= 640.0:
        impuesto_uvt = (base_uvt - 360.0) * 0.33 + 69.25
    elif base_uvt <= 945.0:
        impuesto_uvt = (base_uvt - 640.0) * 0.35 + 161.65
    elif base_uvt <= 2300.0:
        impuesto_uvt = (base_uvt - 945.0) * 0.37 + 268.40
    else:
        impuesto_uvt = (base_uvt - 2300.0) * 0.39 + 769.75

    return round(uvt_a_cop(impuesto_uvt, uvt_cop), 2)


def liquidar_ingreso_neto_colombia(
    ingreso_bruto_mensual_cop: float,
    modalidad_laboral: str = "Empleado",
    aporte_voluntario_afc_fpv_cop: float = 0.0,
    clase_riesgo_arl: int = 1,
    config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Liquida el Ingreso Disponible Neto (IDN) mensual en Colombia según la modalidad contractual:
    - 'Empleado': Salario ordinario (Salud 4%, Pensión 4%, FSP si >= 4 SMMLV, Auxilio Transporte <= 2 SMMLV,
      Retefuente Art. 383 y cálculo informativo de provisiones reales de Prima y Cesantías).
    - 'Integral': Salario integral (>= 13 SMMLV, cotiza sobre el factor base del 70%).
    - 'Independiente': Contratista por prestación de servicios OPS (IBC = 40% con piso de 1 SMMLV,
      Salud 12.5%, Pensión 16%, ARL según clase de riesgo I a V y FSP sobre IBC).
    """
    if ingreso_bruto_mensual_cop < 0:
        raise ValueError("El ingreso bruto mensual no puede ser negativo.")

    cfg = config or cargar_configuracion()
    macro = cfg["parametros_macro_colombia"]
    lab = cfg["parametros_laborales_y_tributarios"]

    smmlv = float(macro["smmlv_cop"])
    aux_transporte_legal = float(macro["auxilio_transporte_cop"])
    uvt = float(macro["uvt_cop"])

    modalidad_norm = modalidad_laboral.strip().lower()
    if modalidad_norm in ("independiente", "contratista", "ops"):
        modalidad = "Independiente"
    elif modalidad_norm in ("integral", "salario integral"):
        modalidad = "Integral"
    else:
        modalidad = "Empleado"

    salarios_minimos = ingreso_bruto_mensual_cop / smmlv if smmlv > 0 else 0.0
    alerta_normativa: str | None = None

    if modalidad == "Independiente":
        ibc_cop = max(smmlv, ingreso_bruto_mensual_cop * float(lab["ibc_independiente_pct"]))
        if ingreso_bruto_mensual_cop < smmlv:
            ibc_cop = smmlv if ingreso_bruto_mensual_cop > 0 else 0.0
        salud_cop = ibc_cop * float(lab["salud_independiente_pct"])
        pension_cop = ibc_cop * float(lab["pension_independiente_pct"])
        tarifa_arl = TARIFAS_ARL_COLOMBIA.get(clase_riesgo_arl, float(lab["arl_riesgo_i_pct"]))
        arl_cop = ibc_cop * tarifa_arl
        fsp_pct = calcular_fsp_porcentaje(ibc_cop / smmlv) if smmlv > 0 else 0.0
        fsp_cop = ibc_cop * fsp_pct
        auxilio_transporte_cop = 0.0
        provision_prima_mensual_cop = 0.0
        provision_cesantias_mensual_cop = 0.0
        provision_intereses_cesantias_mensual_cop = 0.0
    elif modalidad == "Integral":
        min_integral_smmlv = float(lab.get("salario_integral_min_smmlv", 13.0))
        if salarios_minimos < min_integral_smmlv:
            alerta_normativa = (
                f"En Colombia el Salario Integral exige al menos {min_integral_smmlv:.0f} SMMLV "
                f"(${min_integral_smmlv * smmlv:,.0f} COP vigentes)."
            )
        ibc_cop = ingreso_bruto_mensual_cop * float(lab["factor_prestacional_integral"])
        salud_cop = ibc_cop * float(lab["salud_empleado_pct"])
        pension_cop = ibc_cop * float(lab["pension_empleado_pct"])
        arl_cop = 0.0
        fsp_pct = calcular_fsp_porcentaje(ibc_cop / smmlv) if smmlv > 0 else 0.0
        fsp_cop = ibc_cop * fsp_pct
        auxilio_transporte_cop = 0.0
        # En salario integral el 30% prestacional ya incluye primas y cesantías (excepto vacaciones)
        provision_prima_mensual_cop = 0.0
        provision_cesantias_mensual_cop = 0.0
        provision_intereses_cesantias_mensual_cop = 0.0
    else:
        ibc_cop = max(smmlv, ingreso_bruto_mensual_cop) if ingreso_bruto_mensual_cop > 0 else 0.0
        salud_cop = ibc_cop * float(lab["salud_empleado_pct"])
        pension_cop = ibc_cop * float(lab["pension_empleado_pct"])
        arl_cop = 0.0
        fsp_pct = calcular_fsp_porcentaje(salarios_minimos)
        fsp_cop = ibc_cop * fsp_pct
        auxilio_transporte_cop = (
            aux_transporte_legal if (0 < salarios_minimos <= 2.0) else 0.0
        )
        base_prestacional = ingreso_bruto_mensual_cop + auxilio_transporte_cop
        provision_prima_mensual_cop = base_prestacional / 12.0
        provision_cesantias_mensual_cop = base_prestacional / 12.0
        provision_intereses_cesantias_mensual_cop = provision_cesantias_mensual_cop * 0.12

    ingresos_no_constitutivos = salud_cop + pension_cop + fsp_cop
    ingreso_neto_tributario = max(0.0, ingreso_bruto_mensual_cop - ingresos_no_constitutivos)

    tope_afc = ingreso_bruto_mensual_cop * float(lab["beneficio_max_afc_fpv_pct"])
    deduccion_afc_efectiva = min(max(0.0, aporte_voluntario_afc_fpv_cop), tope_afc)

    retefuente_con_afc = estimar_retefuente_mensual_art_383(
        ingreso_neto_tributario_cop=ingreso_neto_tributario,
        uvt_cop=uvt,
        aporte_afc_fpv_cop=deduccion_afc_efectiva,
    )
    retefuente_sin_afc = estimar_retefuente_mensual_art_383(
        ingreso_neto_tributario_cop=ingreso_neto_tributario,
        uvt_cop=uvt,
        aporte_afc_fpv_cop=0.0,
    )

    total_descuentos_ley = salud_cop + pension_cop + arl_cop + fsp_cop + retefuente_con_afc
    ingreso_total_devengado = ingreso_bruto_mensual_cop + auxilio_transporte_cop
    ingreso_neto_mensual_cop = ingreso_total_devengado - total_descuentos_ley
    tasa_descuento_efectiva_pct = (
        (total_descuentos_ley / ingreso_total_devengado) * 100.0 if ingreso_total_devengado > 0 else 0.0
    )

    return {
        "modalidad_laboral": modalidad,
        "ingreso_bruto_mensual_cop": round(ingreso_bruto_mensual_cop, 2),
        "ingreso_en_smmlv": round(salarios_minimos, 2),
        "auxilio_transporte_cop": round(auxilio_transporte_cop, 2),
        "ibc_cotizacion_cop": round(ibc_cop, 2),
        "salud_obligatoria_cop": round(salud_cop, 2),
        "pension_obligatoria_cop": round(pension_cop, 2),
        "porcentaje_fsp_aplicado": round(fsp_pct * 100.0, 2),
        "fondo_solidaridad_pensional_cop": round(fsp_cop, 2),
        "arl_cop": round(arl_cop, 2),
        "retencion_fuente_cop": round(retefuente_con_afc, 2),
        "ahorro_tributario_afc_mensual_cop": round(max(0.0, retefuente_sin_afc - retefuente_con_afc), 2),
        "total_descuentos_ley_cop": round(total_descuentos_ley, 2),
        "tasa_descuento_efectiva_pct": round(tasa_descuento_efectiva_pct, 2),
        "ingreso_neto_mensual_cop": round(ingreso_neto_mensual_cop, 2),
        "provisiones_prestacionales_informativas": {
            "prima_servicios_mensualizada_cop": round(provision_prima_mensual_cop, 2),
            "cesantias_mensualizadas_cop": round(provision_cesantias_mensual_cop, 2),
            "intereses_cesantias_mensualizados_cop": round(provision_intereses_cesantias_mensual_cop, 2),
            "compensacion_total_real_mensual_cop": round(
                ingreso_neto_mensual_cop
                + provision_prima_mensual_cop
                + provision_cesantias_mensual_cop
                + provision_intereses_cesantias_mensual_cop,
                2,
            ),
        },
        "alerta_normativa": alerta_normativa,
    }


def comparar_modalidades_laborales(
    ingreso_bruto_mensual_cop: float,
    aporte_voluntario_afc_fpv_cop: float = 0.0,
    clase_riesgo_arl: int = 1,
    config: Dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    """
    Compara la radiografía salarial de un mismo ingreso bruto bajo las tres modalidades
    contractuales de Colombia: Empleado Ordinario, Salario Integral e Independiente (OPS).
    """
    modalidades = ["Empleado", "Integral", "Independiente"]
    return [
        liquidar_ingreso_neto_colombia(
            ingreso_bruto_mensual_cop=ingreso_bruto_mensual_cop,
            modalidad_laboral=mod,
            aporte_voluntario_afc_fpv_cop=aporte_voluntario_afc_fpv_cop,
            clase_riesgo_arl=clase_riesgo_arl,
            config=config,
        )
        for mod in modalidades
    ]


# ==============================================================================
# 2. GASTOS HORMIGA, FUGAS FINANCIERAS (4x1000) Y REGLA 50/30/20
# ==============================================================================


def cuantificar_gastos_hormiga_y_fugas(
    gastos_hormiga_mensual_cop: float = 0.0,
    detalle_gastos_hormiga: List[Dict[str, Any]] | None = None,
    cuotas_manejo_mensual_cop: float = 0.0,
    monto_movimientos_gmf_mensual_cop: float = 0.0,
    cuenta_exenta_4x1000: bool = True,
    ingreso_neto_mensual_cop: float = 0.0,
    tasa_oportunidad_ea: float = 0.10,
    config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Cuantifica las "fugas de presión" del flujo de caja personal:
    1. Gastos hormiga cotidianos (directos o calculados desde un listado detallado de micro-gastos
       con `concepto`, `monto_unitario_cop` y `frecuencia_mensual`).
    2. Fricciones bancarias en Colombia: Gravamen a los Movimientos Financieros (4x1000 GMF,
       respetando exención de 350 UVT si la cuenta está marcada) y cuotas de manejo/comisiones.
    3. Costo de oportunidad capitalizado a 5 años (60 meses) y 10 años (120 meses) tanto en
       pesos corrientes (nominal) como en poder adquisitivo constante (real neto de IPC y retefuente).
    """
    cfg = config or cargar_configuracion()
    macro = cfg["parametros_macro_colombia"]
    lab = cfg["parametros_laborales_y_tributarios"]
    uvt = float(macro["uvt_cop"])
    ipc = float(macro["ipc_anual_dane"])
    retefuente_fija = float(lab["retefuente_rendimientos_fijos"])

    items_normalizados: List[Dict[str, Any]] = []
    if detalle_gastos_hormiga:
        suma_detalle = 0.0
        for item in detalle_gastos_hormiga:
            monto_unit = float(item.get("monto_unitario_cop", 0.0))
            frecuencia_mes = float(item.get("frecuencia_mensual", 1.0))
            subtotal = max(0.0, monto_unit * frecuencia_mes)
            suma_detalle += subtotal
            items_normalizados.append(
                {
                    "concepto": str(item.get("concepto", "Micro-gasto")),
                    "monto_unitario_cop": round(monto_unit, 2),
                    "frecuencia_mensual": round(frecuencia_mes, 2),
                    "gasto_mensual_cop": round(subtotal, 2),
                    "gasto_anual_cop": round(subtotal * 12.0, 2),
                }
            )
        hormiga_base_mensual = suma_detalle if gastos_hormiga_mensual_cop <= 0 else float(gastos_hormiga_mensual_cop)
    else:
        hormiga_base_mensual = max(0.0, float(gastos_hormiga_mensual_cop))

    gmf_4x1000_mensual = calcular_gmf_4x1000(
        monto_retiro_mensual_cop=max(0.0, monto_movimientos_gmf_mensual_cop),
        cuenta_exenta_marcada=cuenta_exenta_4x1000,
        valor_uvt_cop=uvt,
    )
    friccion_bancaria_mensual = max(0.0, cuotas_manejo_mensual_cop) + gmf_4x1000_mensual
    fuga_total_mensual = hormiga_base_mensual + friccion_bancaria_mensual

    # Costo de oportunidad sobre gastos hormiga puros y sobre fugas totales (5 y 10 años)
    op_hormiga_5a = valor_futuro_aportes_periodicos(hormiga_base_mensual, tasa_ea=tasa_oportunidad_ea, meses=60)
    op_hormiga_10a = valor_futuro_aportes_periodicos(hormiga_base_mensual, tasa_ea=tasa_oportunidad_ea, meses=120)

    op_total_5a = valor_futuro_aportes_periodicos(fuga_total_mensual, tasa_ea=tasa_oportunidad_ea, meses=60)
    op_total_10a = valor_futuro_aportes_periodicos(fuga_total_mensual, tasa_ea=tasa_oportunidad_ea, meses=120)

    tasa_real_neta = calcular_tasa_real_neta(
        tasa_ea_bruta=tasa_oportunidad_ea,
        inflacion_anual_ipc=ipc,
        retefuente_pct=retefuente_fija,
    )
    op_total_real_5a = valor_futuro_aportes_periodicos(fuga_total_mensual, tasa_ea=tasa_real_neta, meses=60)
    op_total_real_10a = valor_futuro_aportes_periodicos(fuga_total_mensual, tasa_ea=tasa_real_neta, meses=120)

    peso_sobre_ingreso_neto_pct = (
        (fuga_total_mensual / ingreso_neto_mensual_cop) * 100.0 if ingreso_neto_mensual_cop > 0 else 0.0
    )

    return {
        "gastos_hormiga_mensual_cop": round(hormiga_base_mensual, 2),
        "gmf_4x1000_mensual_cop": round(gmf_4x1000_mensual, 2),
        "cuotas_manejo_mensual_cop": round(max(0.0, cuotas_manejo_mensual_cop), 2),
        "friccion_bancaria_mensual_cop": round(friccion_bancaria_mensual, 2),
        "fuga_total_mensual_cop": round(fuga_total_mensual, 2),
        "fuga_total_anual_cop": round(fuga_total_mensual * 12.0, 2),
        "peso_sobre_ingreso_neto_pct": round(peso_sobre_ingreso_neto_pct, 2),
        "alerta_fuga_presion": peso_sobre_ingreso_neto_pct > 5.0,
        "tasa_oportunidad_ea": round(tasa_oportunidad_ea, 4),
        "tasa_real_neta_ea": round(tasa_real_neta, 4),
        "costo_oportunidad_hormiga_5a_cop": op_hormiga_5a["valor_futuro_nominal_cop"],
        "costo_oportunidad_hormiga_10a_cop": op_hormiga_10a["valor_futuro_nominal_cop"],
        "costo_oportunidad_fuga_total_5a_nominal_cop": op_total_5a["valor_futuro_nominal_cop"],
        "costo_oportunidad_fuga_total_10a_nominal_cop": op_total_10a["valor_futuro_nominal_cop"],
        "costo_oportunidad_fuga_total_5a_real_cop": op_total_real_5a["valor_futuro_nominal_cop"],
        "costo_oportunidad_fuga_total_10a_real_cop": op_total_real_10a["valor_futuro_nominal_cop"],
        "intereses_dejados_de_ganar_10a_cop": op_total_10a["intereses_compuestos_ganados_cop"],
        "historial_capitalizacion_10a": op_total_10a["historial_mensual"],
        "detalle_items": items_normalizados,
    }


def evaluar_regla_50_30_20(
    ingreso_neto_mensual_cop: float,
    gastos_fijos_vitales_cop: float,
    gastos_variables_estilo_vida_cop: float,
    fugas_totales_mensuales_cop: float,
    cuotas_deuda_mensual_cop: float = 0.0,
) -> Dict[str, Any]:
    """
    Evalúa el balance presupuestal frente a la Regla 50/30/20 adaptada a Colombia:
    - 50% Necesidades Vitales (arriendo/vivienda, mercado, servicios públicos, transporte, salud/educación).
    - 30% Estilo de Vida y Discrecionales (ocio, salidas, suscripciones + fugas/gastos hormiga).
    - 20% Futuro Financiero (ahorro, fondo de emergencia, inversión y amortización de deuda).
    Nota: Se reporta tanto el ahorro/inversión libre puro (`excedente_mensual_cop`) como la
    carga destinada a deuda para visibilizar si las deudas están absorbiendo el bloque del 20%.
    """
    if ingreso_neto_mensual_cop <= 0:
        return {
            "ingreso_neto_base_cop": 0.0,
            "necesidades_50": {"real_cop": 0.0, "meta_cop": 0.0, "real_pct": 0.0, "meta_pct": 50.0, "cumple": False},
            "estilo_vida_30": {"real_cop": 0.0, "meta_cop": 0.0, "real_pct": 0.0, "meta_pct": 30.0, "cumple": False},
            "ahorro_patrimonio_20": {
                "real_cop": 0.0,
                "meta_cop": 0.0,
                "real_pct": 0.0,
                "meta_pct": 20.0,
                "cumple": False,
            },
            "servicio_deuda_pct": 0.0,
            "diagnostico_50_30_20": "Sin ingreso neto disponible para evaluar.",
        }

    discrecional_total = gastos_variables_estilo_vida_cop + fugas_totales_mensuales_cop
    excedente_libre = (
        ingreso_neto_mensual_cop - gastos_fijos_vitales_cop - discrecional_total - cuotas_deuda_mensual_cop
    )

    nec_pct = (gastos_fijos_vitales_cop / ingreso_neto_mensual_cop) * 100.0
    est_pct = (discrecional_total / ingreso_neto_mensual_cop) * 100.0
    deuda_pct = (cuotas_deuda_mensual_cop / ingreso_neto_mensual_cop) * 100.0
    aho_pct = (excedente_libre / ingreso_neto_mensual_cop) * 100.0

    cumple_50 = nec_pct <= 50.0 + 1e-6
    cumple_30 = est_pct <= 30.0 + 1e-6
    cumple_20 = aho_pct >= 20.0 - 1e-6

    observaciones: List[str] = []
    if not cumple_50:
        observaciones.append(
            f"Los costos fijos vitales absorben el {nec_pct:.1f}% del ingreso neto (meta <= 50%)."
        )
    if not cumple_30:
        observaciones.append(
            f"Estilo de vida + fugas hormiga representan el {est_pct:.1f}% (meta <= 30%)."
        )
    if not cumple_20:
        observaciones.append(
            f"El excedente libre de ahorro/inversión es {aho_pct:.1f}% (meta >= 20%)."
        )
    if not observaciones:
        observaciones.append("Equilibrio óptimo: cumple simultáneamente los umbrales 50/30/20.")

    return {
        "ingreso_neto_base_cop": round(ingreso_neto_mensual_cop, 2),
        "necesidades_50": {
            "real_cop": round(gastos_fijos_vitales_cop, 2),
            "meta_cop": round(ingreso_neto_mensual_cop * 0.50, 2),
            "desviacion_cop": round(gastos_fijos_vitales_cop - ingreso_neto_mensual_cop * 0.50, 2),
            "real_pct": round(nec_pct, 2),
            "meta_pct": 50.0,
            "cumple": cumple_50,
        },
        "estilo_vida_30": {
            "real_cop": round(discrecional_total, 2),
            "meta_cop": round(ingreso_neto_mensual_cop * 0.30, 2),
            "desviacion_cop": round(discrecional_total - ingreso_neto_mensual_cop * 0.30, 2),
            "real_pct": round(est_pct, 2),
            "meta_pct": 30.0,
            "cumple": cumple_30,
        },
        "ahorro_patrimonio_20": {
            "real_cop": round(excedente_libre, 2),
            "meta_cop": round(ingreso_neto_mensual_cop * 0.20, 2),
            "brecha_meta_cop": round(max(0.0, ingreso_neto_mensual_cop * 0.20 - excedente_libre), 2),
            "real_pct": round(aho_pct, 2),
            "meta_pct": 20.0,
            "cumple": cumple_20,
        },
        "servicio_deuda_cop": round(cuotas_deuda_mensual_cop, 2),
        "servicio_deuda_pct": round(deuda_pct, 2),
        "diagnostico_50_30_20": " ".join(observaciones),
    }


# ==============================================================================
# 3. DIAGNÓSTICO INTEGRAL CU-01 Y CONTRATO DE INTEGRACIÓN OED
# ==============================================================================


def construir_estructura_sankey(diagnostico: Dict[str, Any]) -> Dict[str, Any]:
    """
    Construye los nodos y enlaces conservativos (Ley de Conservación de Masa/Flujo) para
    graficar el Diagrama de Sankey desde el Ingreso Bruto hasta el Excedente Mensual.
    """
    nom = diagnostico["liquidacion_nomina"]
    bruto = float(nom["ingreso_bruto_mensual_cop"])
    aux = float(nom["auxilio_transporte_cop"])
    otros = float(diagnostico.get("otros_ingresos_mensuales_cop", 0.0))

    salud = float(nom["salud_obligatoria_cop"])
    pension = float(nom["pension_obligatoria_cop"])
    fsp = float(nom["fondo_solidaridad_pensional_cop"])
    arl = float(nom["arl_cop"])
    rete = float(nom["retencion_fuente_cop"])
    idn = float(diagnostico["ingreso_neto_mensual_cop"])

    fijos = float(diagnostico["gastos_fijos_vitales_cop"])
    variables = float(diagnostico["gastos_variables_estilo_vida_cop"])
    fugas = float(diagnostico["fuga_total_mensual_cop"])
    deudas = float(diagnostico["cuotas_deuda_mensual_cop"])
    excedente = float(diagnostico["excedente_mensual_cop"])

    labels = [
        "0. Ingreso Bruto Mensual",
        "1. Auxilio / Otros Ingresos",
        "2. Total Devengado",
        "3. Seguridad Social (Salud + Pensión + FSP + ARL)",
        "4. Retención en la Fuente (DIAN)",
        "5. Ingreso Disponible Neto (IDN)",
        "6. Costos Fijos Vitales",
        "7. Estilo de Vida y Variables",
        "8. Fugas (Gastos Hormiga + 4x1000/Bancos)",
        "9. Servicio de Deuda Actual",
        "10. Excedente Libre Inversible",
        "11. Déficit de Caja a Cubrir",
    ]

    sources: List[int] = []
    targets: List[int] = []
    values: List[float] = []

    def _add_link(src: int, tgt: int, val: float) -> None:
        if val > 0.01:
            sources.append(src)
            targets.append(tgt)
            values.append(round(val, 2))

    # Entradas -> Total Devengado
    _add_link(0, 2, bruto)
    _add_link(1, 2, aux + otros)

    # Total Devengado -> Deducciones de Ley e IDN
    _add_link(2, 3, salud + pension + fsp + arl)
    _add_link(2, 4, rete)
    _add_link(2, 5, idn)

    # Si hay déficit, entra flujo de financiamiento/desahorro al nodo IDN para cuadrar salidas
    if excedente < 0:
        _add_link(11, 5, abs(excedente))

    # IDN -> Destinos del gasto y ahorro
    _add_link(5, 6, fijos)
    _add_link(5, 7, variables)
    _add_link(5, 8, fugas)
    _add_link(5, 9, deudas)
    if excedente > 0:
        _add_link(5, 10, excedente)

    return {
        "labels": labels,
        "sources": sources,
        "targets": targets,
        "values": values,
    }


def diagnosticar_presupuesto_y_flujo_caja(
    ingreso_bruto_mensual_cop: float,
    gastos_fijos_vitales_cop: float,
    gastos_variables_estilo_vida_cop: float,
    gastos_hormiga_mensual_cop: float,
    cuotas_deuda_mensual_cop: float = 0.0,
    liquidez_actual_fondo_emergencia_cop: float = 0.0,
    modalidad_laboral: str = "Empleado",
    aporte_voluntario_afc_fpv_cop: float = 0.0,
    clase_riesgo_arl: int = 1,
    otros_ingresos_mensuales_cop: float = 0.0,
    cuotas_manejo_mensual_cop: float = 0.0,
    monto_movimientos_gmf_mensual_cop: float = 0.0,
    cuenta_exenta_4x1000: bool = True,
    detalle_gastos_hormiga: List[Dict[str, Any]] | None = None,
    config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Ejecuta el Caso de Uso CU-01 (Módulo 1 - Nidia Velásquez):
    - Liquida la Radiografía del Sueldo Colombiano (Empleado, Integral o Independiente OPS).
    - Ejecuta el Balance Termodinámico de Caja y evalúa la Regla 50/30/20.
    - Cuantifica gastos hormiga + fugas financieras (4x1000, cuotas de manejo) y su costo de
      oportunidad a 5 y 10 años al 10% EA.
    - Evalúa el Termómetro de Fondo de Emergencia (3 meses empleados / 6 meses independientes)
      y aplica los flujos alternativos FA-01 (Déficit Crítico) y FA-02 (Asignación 80/20).
    - Respeta íntegramente el Contrato de Integración OED hacia los Módulos 2, 3, 4 y 5.
    """
    cfg = config or cargar_configuracion()
    nomina = liquidar_ingreso_neto_colombia(
        ingreso_bruto_mensual_cop=ingreso_bruto_mensual_cop,
        modalidad_laboral=modalidad_laboral,
        aporte_voluntario_afc_fpv_cop=aporte_voluntario_afc_fpv_cop,
        clase_riesgo_arl=clase_riesgo_arl,
        config=cfg,
    )
    idn = nomina["ingreso_neto_mensual_cop"] + max(0.0, otros_ingresos_mensuales_cop)

    radiografia_fugas = cuantificar_gastos_hormiga_y_fugas(
        gastos_hormiga_mensual_cop=gastos_hormiga_mensual_cop,
        detalle_gastos_hormiga=detalle_gastos_hormiga,
        cuotas_manejo_mensual_cop=cuotas_manejo_mensual_cop,
        monto_movimientos_gmf_mensual_cop=monto_movimientos_gmf_mensual_cop,
        cuenta_exenta_4x1000=cuenta_exenta_4x1000,
        ingreso_neto_mensual_cop=idn,
        tasa_oportunidad_ea=0.10,
        config=cfg,
    )
    fuga_total_mensual = radiografia_fugas["fuga_total_mensual_cop"]
    hormiga_efectivo = radiografia_fugas["gastos_hormiga_mensual_cop"]

    egresos_totales = (
        gastos_fijos_vitales_cop
        + gastos_variables_estilo_vida_cop
        + fuga_total_mensual
        + cuotas_deuda_mensual_cop
    )
    excedente_mensual_cop = idn - egresos_totales

    # Termómetro de Fondo de Emergencia
    meses_meta_emergencia = 6.0 if nomina["modalidad_laboral"] == "Independiente" else 3.0
    monto_meta_fondo_emergencia = gastos_fijos_vitales_cop * meses_meta_emergencia
    faltante_fondo_emergencia = max(0.0, monto_meta_fondo_emergencia - liquidez_actual_fondo_emergencia_cop)
    meses_cobertura_actual = (
        liquidez_actual_fondo_emergencia_cop / gastos_fijos_vitales_cop if gastos_fijos_vitales_cop > 0 else 0.0
    )
    fondo_completo = meses_cobertura_actual >= meses_meta_emergencia - 1e-9

    eficiencia_presupuestal_pct = max(0.0, (excedente_mensual_cop / idn) * 100.0) if idn > 0 else 0.0

    balance_50_30_20 = evaluar_regla_50_30_20(
        ingreso_neto_mensual_cop=idn,
        gastos_fijos_vitales_cop=gastos_fijos_vitales_cop,
        gastos_variables_estilo_vida_cop=gastos_variables_estilo_vida_cop,
        fugas_totales_mensuales_cop=fuga_total_mensual,
        cuotas_deuda_mensual_cop=cuotas_deuda_mensual_cop,
    )

    # Reglas de decisión CU-01 (Camino Feliz vs. FA-01 vs. FA-02)
    if excedente_mensual_cop < 0:
        estado_flujo_caja = "DEFICIT_CRITICO"
        deficit_abs = abs(excedente_mensual_cop)
        recorte_sugerido_fugas = min(fuga_total_mensual, deficit_abs)
        recorte_sugerido_variables = max(0.0, deficit_abs - recorte_sugerido_fugas)
        plan_accion = {
            "codigo_flujo": "FA-01",
            "bloquea_inversion_riesgo": True,
            "aporte_recomendado_fondo_emergencia_cop": 0.0,
            "aporte_disponible_portafolio_mod2_cop": 0.0,
            "meses_estimados_completar_fondo": None,
            "recorte_inmediato_fugas_cop": round(recorte_sugerido_fugas, 2),
            "recorte_adicional_variables_cop": round(recorte_sugerido_variables, 2),
            "recomendacion_ejecutiva": (
                f"ALERTA ROJA DE DÉFICIT ESTRUCTURAL (-${deficit_abs:,.0f} COP/mes): "
                "Se bloquean inversiones de riesgo. Priorice eliminar fugas hormiga y gastos variables, "
                "y remita sus obligaciones al Módulo 3 (Gestión de Deudas - Catalina)."
            ),
        }
    elif not fondo_completo:
        estado_flujo_caja = "CONSTRUIR_FONDO_EMERGENCIA"
        aporte_emergencia_80 = excedente_mensual_cop * 0.80
        aporte_portafolio_20 = excedente_mensual_cop * 0.20
        meses_para_meta = (
            round(faltante_fondo_emergencia / aporte_emergencia_80, 1)
            if aporte_emergencia_80 > 0
            else None
        )
        plan_accion = {
            "codigo_flujo": "FA-02",
            "bloquea_inversion_riesgo": False,
            "aporte_recomendado_fondo_emergencia_cop": round(aporte_emergencia_80, 2),
            "aporte_disponible_portafolio_mod2_cop": round(aporte_portafolio_20, 2),
            "meses_estimados_completar_fondo": meses_para_meta,
            "recorte_inmediato_fugas_cop": 0.0,
            "recorte_adicional_variables_cop": 0.0,
            "recomendacion_ejecutiva": (
                f"Fondo de emergencia en construcción ({meses_cobertura_actual:.2f} de {meses_meta_emergencia:.0f} meses). "
                f"Destine el 80% del excedente (${aporte_emergencia_80:,.0f} COP/mes) a liquidez inmediata "
                f"(Bolsillo remunerado Fogafín / FIC a la vista) durante ~{meses_para_meta} meses y el 20% "
                f"(${aporte_portafolio_20:,.0f} COP/mes) al Módulo 2."
            ),
        }
    else:
        estado_flujo_caja = "LISTO_PARA_INVERTIR"
        plan_accion = {
            "codigo_flujo": "CU-01-OK",
            "bloquea_inversion_riesgo": False,
            "aporte_recomendado_fondo_emergencia_cop": 0.0,
            "aporte_disponible_portafolio_mod2_cop": round(excedente_mensual_cop, 2),
            "meses_estimados_completar_fondo": 0.0,
            "recorte_inmediato_fugas_cop": 0.0,
            "recorte_adicional_variables_cop": 0.0,
            "recomendacion_ejecutiva": (
                f"Flujo de caja saludable y fondo de emergencia completo ({meses_cobertura_actual:.2f} meses). "
                f"Dispone de ${excedente_mensual_cop:,.0f} COP/mes libres para optimizar deudas (Módulo 3) "
                "o estructurar su portafolio de inversión (Módulo 2)."
            ),
        }

    resultado: Dict[str, Any] = {
        "liquidacion_nomina": nomina,
        "otros_ingresos_mensuales_cop": round(max(0.0, otros_ingresos_mensuales_cop), 2),
        "ingreso_neto_mensual_cop": round(idn, 2),
        "gastos_fijos_vitales_cop": round(gastos_fijos_vitales_cop, 2),
        "gastos_variables_estilo_vida_cop": round(gastos_variables_estilo_vida_cop, 2),
        "gastos_hormiga_mensual_cop": round(hormiga_efectivo, 2),
        "fuga_total_mensual_cop": round(fuga_total_mensual, 2),
        "cuotas_deuda_mensual_cop": round(cuotas_deuda_mensual_cop, 2),
        "egresos_totales_mensuales_cop": round(egresos_totales, 2),
        "excedente_mensual_cop": round(excedente_mensual_cop, 2),
        "eficiencia_presupuestal_pct": round(eficiencia_presupuestal_pct, 2),
        "meses_fondo_emergencia": round(meses_cobertura_actual, 2),
        "meta_meses_fondo_emergencia": meses_meta_emergencia,
        "monto_meta_fondo_emergencia_cop": round(monto_meta_fondo_emergencia, 2),
        "faltante_fondo_emergencia_cop": round(faltante_fondo_emergencia, 2),
        "fondo_emergencia_completo": fondo_completo,
        "costo_oportunidad_hormiga_5a_cop": radiografia_fugas["costo_oportunidad_hormiga_5a_cop"],
        "costo_oportunidad_hormiga_10a_cop": radiografia_fugas["costo_oportunidad_hormiga_10a_cop"],
        "radiografia_fugas": radiografia_fugas,
        "balance_50_30_20": balance_50_30_20,
        "plan_accion_flujo_caja": plan_accion,
        "estado_flujo_caja": estado_flujo_caja,
    }
    resultado["flujo_sankey"] = construir_estructura_sankey(resultado)
    return resultado


def ejecutar_modulo_1_perfil_usuario(
    perfil_usuario: Dict[str, Any] | None = None,
    config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Adaptador directo para el Contrato de Integración OED (`PLAN_EJECUCION_TALLER_OED.md`):
    Toma un diccionario `perfil_usuario` (o carga `perfil_semilla_taller` de `config.yaml`)
    y retorna el perfil enriquecido con las llaves oficiales del Módulo 1.
    """
    cfg = config or cargar_configuracion()
    semilla = dict(cfg.get("perfil_semilla_taller", {}))
    if perfil_usuario:
        semilla.update(perfil_usuario)

    diagnostico = diagnosticar_presupuesto_y_flujo_caja(
        ingreso_bruto_mensual_cop=float(semilla.get("ingreso_bruto_mensual_cop", 0.0)),
        gastos_fijos_vitales_cop=float(semilla.get("gastos_fijos_vitales_cop", 0.0)),
        gastos_variables_estilo_vida_cop=float(semilla.get("gastos_variables_estilo_vida_cop", 0.0)),
        gastos_hormiga_mensual_cop=float(semilla.get("gastos_hormiga_mensual_cop", 0.0)),
        cuotas_deuda_mensual_cop=float(semilla.get("cuotas_deuda_mensual_cop", 0.0)),
        liquidez_actual_fondo_emergencia_cop=float(semilla.get("liquidez_actual_fondo_emergencia_cop", 0.0)),
        modalidad_laboral=str(semilla.get("modalidad_laboral", "Empleado")),
        aporte_voluntario_afc_fpv_cop=float(semilla.get("aporte_voluntario_afc_fpv_cop", 0.0)),
        clase_riesgo_arl=int(semilla.get("clase_riesgo_arl", 1)),
        otros_ingresos_mensuales_cop=float(semilla.get("otros_ingresos_mensuales_cop", 0.0)),
        cuotas_manejo_mensual_cop=float(semilla.get("cuotas_manejo_mensual_cop", 0.0)),
        monto_movimientos_gmf_mensual_cop=float(semilla.get("monto_movimientos_gmf_mensual_cop", 0.0)),
        cuenta_exenta_4x1000=bool(semilla.get("cuenta_exenta_4x1000", True)),
        detalle_gastos_hormiga=semilla.get("detalle_gastos_hormiga"),
        config=cfg,
    )

    salida_contrato = dict(semilla)
    salida_contrato.update(
        {
            "ingreso_neto_mensual_cop": diagnostico["ingreso_neto_mensual_cop"],
            "excedente_mensual_cop": diagnostico["excedente_mensual_cop"],
            "meses_fondo_emergencia": diagnostico["meses_fondo_emergencia"],
            "costo_oportunidad_hormiga_10a_cop": diagnostico["costo_oportunidad_hormiga_10a_cop"],
            "diagnostico_mod1": diagnostico,
        }
    )
    return salida_contrato


# ==============================================================================
# 3B. PERSISTENCIA LOCAL DE NÓMINA, MODALIDAD Y ESCENARIOS (data/processed/)
# ==============================================================================

RUTA_PERFIL_ACTIVO_MOD1 = Path(__file__).resolve().parent.parent / "data" / "processed" / "perfil_mod1_activo.json"
RUTA_HISTORIAL_MOD1 = (
    Path(__file__).resolve().parent.parent / "data" / "processed" / "historial_simulaciones_mod1.json"
)


def guardar_simulacion_presupuesto(
    datos_entrada: Dict[str, Any],
    nombre_escenario: str | None = None,
    guardar_en_historial: bool = False,
    ruta_activo: str | Path | None = None,
    ruta_historial: str | Path | None = None,
    config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Persiste localmente en `data/processed/` la configuración actual cuando el usuario cambia
    el salario, la modalidad contractual o sus parámetros presupuestales:
    - Siempre actualiza `perfil_mod1_activo.json` (estado activo persistente entre sesiones).
    - Si `guardar_en_historial=True`, registra además una instantánea identificable en
      `historial_simulaciones_mod1.json` para consultar o restaurar distintos salarios/modalidades.
    """
    cfg = config or cargar_configuracion()
    contrato_full = ejecutar_modulo_1_perfil_usuario(datos_entrada, config=cfg)
    diag = contrato_full["diagnostico_mod1"]
    nom = diag["liquidacion_nomina"]

    ahora_iso = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    etiqueta = (nombre_escenario or "").strip()
    if not etiqueta:
        etiqueta = f"{nom['modalidad_laboral']} — ${nom['ingreso_bruto_mensual_cop']:,.0f} COP"

    parametros_limpios = {
        "modalidad_laboral": nom["modalidad_laboral"],
        "clase_riesgo_arl": int(datos_entrada.get("clase_riesgo_arl", 1)),
        "ingreso_bruto_mensual_cop": nom["ingreso_bruto_mensual_cop"],
        "otros_ingresos_mensuales_cop": diag["otros_ingresos_mensuales_cop"],
        "aporte_voluntario_afc_fpv_cop": float(datos_entrada.get("aporte_voluntario_afc_fpv_cop", 0.0)),
        "gastos_fijos_vitales_cop": diag["gastos_fijos_vitales_cop"],
        "gastos_variables_estilo_vida_cop": diag["gastos_variables_estilo_vida_cop"],
        "gastos_hormiga_mensual_cop": diag["gastos_hormiga_mensual_cop"],
        "cuotas_deuda_mensual_cop": diag["cuotas_deuda_mensual_cop"],
        "liquidez_actual_fondo_emergencia_cop": float(
            datos_entrada.get("liquidez_actual_fondo_emergencia_cop", 0.0)
        ),
        "cuotas_manejo_mensual_cop": diag["radiografia_fugas"]["cuotas_manejo_mensual_cop"],
        "monto_movimientos_gmf_mensual_cop": float(
            datos_entrada.get("monto_movimientos_gmf_mensual_cop", 0.0)
        ),
        "cuenta_exenta_4x1000": bool(datos_entrada.get("cuenta_exenta_4x1000", True)),
        "detalle_gastos_hormiga": datos_entrada.get("detalle_gastos_hormiga")
        or diag["radiografia_fugas"]["detalle_items"],
    }

    registro_activo = {
        "nombre_escenario": etiqueta,
        "fecha_guardado_iso": ahora_iso,
        "parametros_entrada": parametros_limpios,
        "resumen_resultados": {
            "modalidad_laboral": nom["modalidad_laboral"],
            "ingreso_bruto_mensual_cop": nom["ingreso_bruto_mensual_cop"],
            "total_descuentos_ley_cop": nom["total_descuentos_ley_cop"],
            "ingreso_neto_mensual_cop": diag["ingreso_neto_mensual_cop"],
            "excedente_mensual_cop": diag["excedente_mensual_cop"],
            "meses_fondo_emergencia": diag["meses_fondo_emergencia"],
            "costo_oportunidad_hormiga_10a_cop": diag["costo_oportunidad_hormiga_10a_cop"],
            "estado_flujo_caja": diag["estado_flujo_caja"],
        },
    }

    target_activo = Path(ruta_activo) if ruta_activo else RUTA_PERFIL_ACTIVO_MOD1
    target_activo.parent.mkdir(parents=True, exist_ok=True)
    with open(target_activo, "w", encoding="utf-8") as f_act:
        json.dump(registro_activo, f_act, ensure_ascii=False, indent=2)

    target_hist = Path(ruta_historial) if ruta_historial else RUTA_HISTORIAL_MOD1
    historial = listar_historial_simulaciones(target_hist)

    nuevo_item_historial: Dict[str, Any] | None = None
    if guardar_en_historial:
        nuevo_item_historial = {
            "id_registro": f"mod1_{uuid.uuid4().hex[:8]}",
            **registro_activo,
        }
        historial.insert(0, nuevo_item_historial)
        historial = historial[:50]  # Conservar hasta las 50 simulaciones más recientes
        target_hist.parent.mkdir(parents=True, exist_ok=True)
        with open(target_hist, "w", encoding="utf-8") as f_hist:
            json.dump(historial, f_hist, ensure_ascii=False, indent=2)

    return {
        "guardado_exitoso": True,
        "ruta_perfil_activo": str(target_activo),
        "fecha_guardado_iso": ahora_iso,
        "perfil_activo": registro_activo,
        "item_historial_creado": nuevo_item_historial,
        "historial": historial,
    }


def listar_historial_simulaciones(ruta_historial: str | Path | None = None) -> List[Dict[str, Any]]:
    """Lee el listado de escenarios de nómina/presupuesto guardados localmente."""
    target_hist = Path(ruta_historial) if ruta_historial else RUTA_HISTORIAL_MOD1
    if not target_hist.exists():
        return []
    try:
        with open(target_hist, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def cargar_simulacion_presupuesto(
    ruta_activo: str | Path | None = None,
    ruta_historial: str | Path | None = None,
) -> Dict[str, Any]:
    """Recupera el último perfil activo guardado en disco junto con el historial de escenarios."""
    target_activo = Path(ruta_activo) if ruta_activo else RUTA_PERFIL_ACTIVO_MOD1
    perfil_activo = None
    if target_activo.exists():
        try:
            with open(target_activo, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict) and "parametros_entrada" in loaded:
                    perfil_activo = loaded
        except Exception:
            perfil_activo = None

    return {
        "existe_perfil_guardado": perfil_activo is not None,
        "perfil_activo": perfil_activo,
        "historial": listar_historial_simulaciones(ruta_historial),
    }


def eliminar_simulacion_historial(
    id_registro: str,
    ruta_historial: str | Path | None = None,
) -> List[Dict[str, Any]]:
    """Elimina un escenario específico del historial local por su `id_registro`."""
    target_hist = Path(ruta_historial) if ruta_historial else RUTA_HISTORIAL_MOD1
    actuales = listar_historial_simulaciones(target_hist)
    filtrados = [item for item in actuales if item.get("id_registro") != id_registro]
    target_hist.parent.mkdir(parents=True, exist_ok=True)
    with open(target_hist, "w", encoding="utf-8") as f:
        json.dump(filtrados, f, ensure_ascii=False, indent=2)
    return filtrados


# ==============================================================================
# 4. VISUALIZACIONES INTERACTIVAS EN PLOTLY (PARA NOTEBOOK Y STREAMLIT APP)
# ==============================================================================


def crear_figura_sankey_presupuesto(diagnostico: Dict[str, Any]) -> Any:
    """Genera en Plotly el Diagrama de Sankey del balance termodinámico de flujos salariales."""
    import plotly.graph_objects as go  # type: ignore

    sk = diagnostico["flujo_sankey"]
    colores_nodos = [
        "#1f4e78",  # 0 Ingreso Bruto
        "#2e75b6",  # 1 Auxilio / Otros
        "#0f2c59",  # 2 Total Devengado
        "#c55a11",  # 3 Seguridad Social
        "#843c0c",  # 4 Retefuente
        "#1b7f5c",  # 5 IDN
        "#4472c4",  # 6 Costos Fijos
        "#7030a0",  # 7 Estilo de Vida
        "#d9534f",  # 8 Fugas / Hormiga
        "#f0ad4e",  # 9 Deuda
        "#2ca02c",  # 10 Excedente Libre
        "#b30000",  # 11 Déficit
    ]

    fig = go.Figure(
        data=[
            go.Sankey(
                valueformat=",.0f",
                valuesuffix=" COP",
                node=dict(
                    pad=18,
                    thickness=22,
                    line=dict(color="#1e293b", width=0.8),
                    label=sk["labels"],
                    color=colores_nodos,
                ),
                link=dict(
                    source=sk["sources"],
                    target=sk["targets"],
                    value=sk["values"],
                    color="rgba(100, 116, 139, 0.28)",
                ),
            )
        ]
    )
    fig.update_layout(
        title=(
            "Diagrama de Sankey — Balance Termodinámico del Sueldo al Excedente Libre "
            f"({diagnostico['liquidacion_nomina']['modalidad_laboral']})"
        ),
        font=dict(size=12, family="Arial"),
        height=500,
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return fig


def crear_figura_waterfall_sueldo(diagnostico: Dict[str, Any]) -> Any:
    """Genera en Plotly un gráfico Waterfall (Cascada) paso a paso desde el sueldo bruto hasta el excedente."""
    import plotly.graph_objects as go  # type: ignore

    nom = diagnostico["liquidacion_nomina"]
    medidas = ["absolute"]
    etiquetas = ["Salario Bruto"]
    valores = [nom["ingreso_bruto_mensual_cop"]]

    if nom["auxilio_transporte_cop"] > 0 or diagnostico.get("otros_ingresos_mensuales_cop", 0.0) > 0:
        medidas.append("relative")
        etiquetas.append("Auxilio / Otros")
        valores.append(nom["auxilio_transporte_cop"] + diagnostico.get("otros_ingresos_mensuales_cop", 0.0))

    medidas.extend(["relative", "total", "relative", "relative", "relative"])
    etiquetas.extend(
        [
            "Descuentos de Ley",
            "Ingreso Neto (IDN)",
            "Costos Fijos Vitales",
            "Estilo de Vida",
            "Fugas + Hormiga",
        ]
    )
    valores.extend(
        [
            -nom["total_descuentos_ley_cop"],
            0.0,
            -diagnostico["gastos_fijos_vitales_cop"],
            -diagnostico["gastos_variables_estilo_vida_cop"],
            -diagnostico["fuga_total_mensual_cop"],
        ]
    )

    if diagnostico["cuotas_deuda_mensual_cop"] > 0:
        medidas.append("relative")
        etiquetas.append("Cuotas Deuda")
        valores.append(-diagnostico["cuotas_deuda_mensual_cop"])

    medidas.append("total")
    etiquetas.append("Excedente Mensual")
    valores.append(0.0)

    fig = go.Figure(
        go.Waterfall(
            name="Flujo de Caja",
            orientation="v",
            measure=medidas,
            x=etiquetas,
            y=valores,
            text=[f"${v:,.0f}" if m != "total" else "" for v, m in zip(valores, medidas)],
            textposition="outside",
            connector={"line": {"color": "#64748b"}},
            decreasing={"marker": {"color": "#dc2626"}},
            increasing={"marker": {"color": "#2563eb"}},
            totals={"marker": {"color": "#16a34a"}},
        )
    )
    fig.update_layout(
        title="Radiografía en Cascada (Waterfall) — Del Salario Bruto al Excedente Mensual (COP)",
        yaxis_title="Pesos Colombianos (COP)",
        height=460,
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig


def crear_figura_costo_oportunidad_hormiga(diagnostico: Dict[str, Any]) -> Any:
    """
    Grafica la curva de crecimiento exponencial (1 a 120 meses) de invertir las fugas y gastos
    hormiga al 10% EA vs. el dinero acumulado gastado sin retorno.
    """
    import plotly.graph_objects as go  # type: ignore

    fugas = diagnostico["radiografia_fugas"]
    hist = fugas["historial_capitalizacion_10a"]
    meses = [int(h["mes"]) for h in hist]
    gasto_acumulado = [h["capital_acumulado_cop"] for h in hist]
    patrimonio_potencial = [h["saldo_final_cop"] for h in hist]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=meses,
            y=gasto_acumulado,
            mode="lines",
            name="Dinero drenado en Fugas / Hormiga (Sin invertir)",
            line=dict(color="#ef4444", width=2.5, dash="dash"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=meses,
            y=patrimonio_potencial,
            mode="lines",
            name=f"Patrimonio si se invierte al {fugas['tasa_oportunidad_ea'] * 100:.1f}% EA",
            fill="tonexty",
            fillcolor="rgba(16, 185, 129, 0.18)",
            line=dict(color="#059669", width=3),
        )
    )
    # Marcadores clave a 5 años (mes 60) y 10 años (mes 120)
    if len(hist) >= 120:
        fig.add_trace(
            go.Scatter(
                x=[60, 120],
                y=[hist[59]["saldo_final_cop"], hist[119]["saldo_final_cop"]],
                mode="markers+text",
                name="Hitos 5 y 10 años",
                text=[
                    f"5 años: ${hist[59]['saldo_final_cop']:,.0f}",
                    f"10 años: ${hist[119]['saldo_final_cop']:,.0f}",
                ],
                textposition="top left",
                marker=dict(size=10, color="#047857"),
            )
        )

    fig.update_layout(
        title="Costo de Oportunidad de las Fugas Presupuestales (Horizonte 5 y 10 Años)",
        xaxis_title="Meses",
        yaxis_title="Pesos Colombianos (COP)",
        hovermode="x unified",
        height=440,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig
