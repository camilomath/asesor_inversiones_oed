"""
MÓDULO 1: Presupuesto Personal e Ingeniería del Flujo de Caja Salarial.
Responsable OED: Nidia Velásquez (Ingeniera Mecánica - Especialista en Presupuestos).

Implementa:
- Liquidación de nómina colombiana (Empleado Ordinario, Salario Integral y Contratista OPS con IBC 40%).
- Descuentos de ley: Salud (4%), Pensión (4%), Fondo de Solidaridad Pensional (FSP 1%-2% si >= 4 SMMLV)
  y estimación de Retención en la Fuente en UVT (Art. 383 Estatuto Tributario con 25% renta exenta).
- Balance de flujos 50/30/20 adaptado a Colombia, cuantificación de "fugas de presión" (gastos hormiga + 4x1000)
  y su costo de oportunidad capitalizado a 5 y 10 años.
- Termómetro de Fondo de Emergencia (meta 3 meses empleados, 6 meses independientes).
"""

from __future__ import annotations

from typing import Any, Dict

from src.finance import cargar_configuracion, cop_a_uvt, uvt_a_cop, valor_futuro_aportes_periodicos


def calcular_fsp_porcentaje(ingreso_en_smmlv: float) -> float:
    """
    Calcula el porcentaje de aporte al Fondo de Solidaridad Pensional (Ley 100 de 1993 / Ley 797 de 2003):
    - Menos de 4 SMMLV: 0%
    - De 4 a 16 SMMLV: 1.0%
    - De 16 a 17 SMMLV: 1.2%
    - De 17 a 18 SMMLV: 1.4%
    - De 18 a 19 SMMLV: 1.6%
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


def estimar_retefuente_mensual_art_383(base_depurada_antes_exenta_cop: float, uvt_cop: float) -> float:
    """
    Calcula la Retención en la Fuente mensual para rentas de trabajo (Art. 383 Estatuto Tributario - Ley 2277 de 2022):
    - Aplica el 25% de renta exenta laboral (con tope mensual referencial de 790/12 UVT).
    - Aplica la tabla progresiva en UVT (0%, 19%, 28%, 33%...).
    """
    if base_depurada_antes_exenta_cop <= 0:
        return 0.0
    tope_mensual_exenta_cop = uvt_a_cop(790.0 / 12.0, uvt_cop)
    renta_exenta_25 = min(base_depurada_antes_exenta_cop * 0.25, tope_mensual_exenta_cop)
    base_gravable_cop = max(0.0, base_depurada_antes_exenta_cop - renta_exenta_25)
    base_uvt = cop_a_uvt(base_gravable_cop, uvt_cop)

    if base_uvt <= 95.0:
        impuesto_uvt = 0.0
    elif base_uvt <= 150.0:
        impuesto_uvt = (base_uvt - 95.0) * 0.19
    elif base_uvt <= 360.0:
        impuesto_uvt = (base_uvt - 150.0) * 0.28 + 10.45
    elif base_uvt <= 640.0:
        impuesto_uvt = (base_uvt - 360.0) * 0.33 + 69.25
    else:
        impuesto_uvt = (base_uvt - 640.0) * 0.35 + 161.65

    return round(uvt_a_cop(impuesto_uvt, uvt_cop), 2)


def liquidar_ingreso_neto_colombia(
    ingreso_bruto_mensual_cop: float,
    modalidad_laboral: str = "Empleado",
    aporte_voluntario_afc_fpv_cop: float = 0.0,
    config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Liquida el Ingreso Disponible Neto (IDN) mensual en Colombia según la modalidad contractual:
    - 'Empleado': Salario ordinario (Salud 4%, Pensión 4%, FSP, Auxilio Transporte <= 2 SMMLV, Retefuente).
    - 'Integral': Salario integral (>= 13 SMMLV, cotiza sobre el 70%).
    - 'Independiente': Contratista por prestación de servicios OPS (IBC = 40%, Salud 12.5%, Pensión 16%, ARL 0.522%).
    """
    cfg = config or cargar_configuracion()
    macro = cfg["parametros_macro_colombia"]
    lab = cfg["parametros_laborales_y_tributarios"]

    smmlv = float(macro["smmlv_cop"])
    aux_transporte_legal = float(macro["auxilio_transporte_cop"])
    uvt = float(macro["uvt_cop"])

    modalidad = modalidad_laboral.strip().capitalize()
    salarios_minimos = ingreso_bruto_mensual_cop / smmlv

    if modalidad == "Independiente":
        ibc_cop = max(smmlv, ingreso_bruto_mensual_cop * float(lab["ibc_independiente_pct"]))
        salud_cop = ibc_cop * float(lab["salud_independiente_pct"])
        pension_cop = ibc_cop * float(lab["pension_independiente_pct"])
        arl_cop = ibc_cop * float(lab["arl_riesgo_i_pct"])
        fsp_cop = ibc_cop * calcular_fsp_porcentaje(ibc_cop / smmlv)
        auxilio_transporte_cop = 0.0
    elif modalidad == "Integral":
        ibc_cop = ingreso_bruto_mensual_cop * float(lab["factor_prestacional_integral"])
        salud_cop = ibc_cop * float(lab["salud_empleado_pct"])
        pension_cop = ibc_cop * float(lab["pension_empleado_pct"])
        arl_cop = 0.0
        fsp_cop = ibc_cop * calcular_fsp_porcentaje(ibc_cop / smmlv)
        auxilio_transporte_cop = 0.0
    else:
        ibc_cop = max(smmlv, ingreso_bruto_mensual_cop)
        salud_cop = ibc_cop * float(lab["salud_empleado_pct"])
        pension_cop = ibc_cop * float(lab["pension_empleado_pct"])
        arl_cop = 0.0
        fsp_cop = ibc_cop * calcular_fsp_porcentaje(salarios_minimos)
        auxilio_transporte_cop = aux_transporte_legal if salarios_minimos <= 2.0 else 0.0

    ingresos_no_constitutivos = salud_cop + pension_cop + fsp_cop
    tope_afc = ingreso_bruto_mensual_cop * float(lab["beneficio_max_afc_fpv_pct"])
    deduccion_afc_efectiva = min(max(0.0, aporte_voluntario_afc_fpv_cop), tope_afc)

    base_antes_exenta = max(0.0, ingreso_bruto_mensual_cop - ingresos_no_constitutivos - deduccion_afc_efectiva)
    retefuente_con_afc = estimar_retefuente_mensual_art_383(base_antes_exenta, uvt)
    retefuente_sin_afc = estimar_retefuente_mensual_art_383(
        max(0.0, ingreso_bruto_mensual_cop - ingresos_no_constitutivos), uvt
    )

    total_descuentos_ley = salud_cop + pension_cop + arl_cop + fsp_cop + retefuente_con_afc
    ingreso_neto_mensual_cop = ingreso_bruto_mensual_cop + auxilio_transporte_cop - total_descuentos_ley

    return {
        "modalidad_laboral": modalidad,
        "ingreso_bruto_mensual_cop": round(ingreso_bruto_mensual_cop, 2),
        "auxilio_transporte_cop": round(auxilio_transporte_cop, 2),
        "ibc_cotizacion_cop": round(ibc_cop, 2),
        "salud_obligatoria_cop": round(salud_cop, 2),
        "pension_obligatoria_cop": round(pension_cop, 2),
        "fondo_solidaridad_pensional_cop": round(fsp_cop, 2),
        "arl_cop": round(arl_cop, 2),
        "retencion_fuente_cop": round(retefuente_con_afc, 2),
        "ahorro_tributario_afc_mensual_cop": round(max(0.0, retefuente_sin_afc - retefuente_con_afc), 2),
        "total_descuentos_ley_cop": round(total_descuentos_ley, 2),
        "ingreso_neto_mensual_cop": round(ingreso_neto_mensual_cop, 2),
    }


def diagnosticar_presupuesto_y_flujo_caja(
    ingreso_bruto_mensual_cop: float,
    gastos_fijos_vitales_cop: float,
    gastos_variables_estilo_vida_cop: float,
    gastos_hormiga_mensual_cop: float,
    cuotas_deuda_mensual_cop: float = 0.0,
    liquidez_actual_fondo_emergencia_cop: float = 0.0,
    modalidad_laboral: str = "Empleado",
    config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Ejecuta el Caso de Uso CU-01 (Módulo 1 - Nidia):
    Calcula el balance de flujos, el excedente mensual disponible para deuda/inversión,
    el costo de oportunidad a 5 y 10 años de los gastos hormiga y la cobertura del fondo de emergencia.
    """
    nomina = liquidar_ingreso_neto_colombia(
        ingreso_bruto_mensual_cop=ingreso_bruto_mensual_cop,
        modalidad_laboral=modalidad_laboral,
        config=config,
    )
    idn = nomina["ingreso_neto_mensual_cop"]
    egresos_totales = (
        gastos_fijos_vitales_cop
        + gastos_variables_estilo_vida_cop
        + gastos_hormiga_mensual_cop
        + cuotas_deuda_mensual_cop
    )
    excedente_mensual_cop = idn - egresos_totales

    meses_meta_emergencia = 6.0 if nomina["modalidad_laboral"] == "Independiente" else 3.0
    meses_cobertura_actual = (
        liquidez_actual_fondo_emergencia_cop / gastos_fijos_vitales_cop if gastos_fijos_vitales_cop > 0 else 0.0
    )

    # Costo de oportunidad de los gastos hormiga si se invirtieran al 10% EA durante 5 y 10 años
    op_5a = valor_futuro_aportes_periodicos(gastos_hormiga_mensual_cop, tasa_ea=0.10, meses=60)
    op_10a = valor_futuro_aportes_periodicos(gastos_hormiga_mensual_cop, tasa_ea=0.10, meses=120)

    eficiencia_presupuestal_pct = max(0.0, (excedente_mensual_cop / idn) * 100.0) if idn > 0 else 0.0

    return {
        "liquidacion_nomina": nomina,
        "ingreso_neto_mensual_cop": round(idn, 2),
        "gastos_fijos_vitales_cop": round(gastos_fijos_vitales_cop, 2),
        "gastos_variables_estilo_vida_cop": round(gastos_variables_estilo_vida_cop, 2),
        "gastos_hormiga_mensual_cop": round(gastos_hormiga_mensual_cop, 2),
        "cuotas_deuda_mensual_cop": round(cuotas_deuda_mensual_cop, 2),
        "excedente_mensual_cop": round(excedente_mensual_cop, 2),
        "eficiencia_presupuestal_pct": round(eficiencia_presupuestal_pct, 2),
        "meses_fondo_emergencia": round(meses_cobertura_actual, 2),
        "meta_meses_fondo_emergencia": meses_meta_emergencia,
        "fondo_emergencia_completo": meses_cobertura_actual >= meses_meta_emergencia,
        "costo_oportunidad_hormiga_5a_cop": op_5a["valor_futuro_nominal_cop"],
        "costo_oportunidad_hormiga_10a_cop": op_10a["valor_futuro_nominal_cop"],
        "estado_flujo_caja": (
            "DEFICIT_CRITICO"
            if excedente_mensual_cop < 0
            else ("CONSTRUIR_FONDO_EMERGENCIA" if meses_cobertura_actual < meses_meta_emergencia else "LISTO_PARA_INVERTIR")
        ),
    }
