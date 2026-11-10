"""
MÓDULO 4: Inversión Patrimonial en Finca Raíz Colombiana.
Responsable OED: Jesi (Administradora de Empresas - Magíster en Analítica).

Implementa:
- Clasificación regulatoria VIS / VIP vs. No VIS en SMMLV.
- Plan de pago de Cuota Inicial sobre planos (encargo fiduciario 18-36 meses) integrando cesantías, primas y AFC.
- Validación de la Regla del 30% de la Ley 546 de 1999 (Ley de Vivienda: Primera cuota <= 30% del ingreso familiar).
- Comparación entre Crédito en Pesos Cuota Fija vs. Crédito en UVR indexado a la inflación IPC DANE.
- Evaluación analítica de inversión inmobiliaria (Cap Rate Neto, Cash-on-Cash, VPN y TIR bajo el tope del 1%
  mensual de canon de arrendamiento de la Ley 820 de 2003).
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.finance import calcular_tir, calcular_vpn, cargar_configuracion, cuota_fija_francesa, ea_a_em


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
    config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Ejecuta el Caso de Uso CU-04 (Módulo 4 - Jesi):
    Evalúa la viabilidad legal y financiera de adquirir finca raíz en Colombia (vivienda o renta).
    """
    cfg = config or cargar_configuracion()
    macro = cfg["parametros_macro_colombia"]
    viv = cfg["parametros_vivienda_ley_546"]

    smmlv = float(macro["smmlv_cop"])
    ipc_anual = float(macro["ipc_anual_dane"])
    valor_en_smmlv = valor_inmueble_cop / smmlv

    if valor_en_smmlv <= float(viv["tope_vip_smmlv"]):
        segmento = "VIP (Vivienda de Interés Prioritario <= 90 SMMLV)"
    elif valor_en_smmlv <= float(viv["tope_vis_smmlv"]):
        segmento = "VIS (Vivienda de Interés Social <= 150 SMMLV)"
    else:
        segmento = "No VIS (> 150 SMMLV)"

    cuota_inicial_total_cop = valor_inmueble_cop * porcentaje_cuota_inicial
    monto_credito_cop = valor_inmueble_cop - cuota_inicial_total_cop
    gastos_escrituracion_cop = valor_inmueble_cop * float(viv["gastos_escrituracion_registro_pct"])

    # Plan sobre planos (encargo fiduciario)
    aporte_cesantias_total = (plazo_entrega_planos_meses / 12.0) * cesantias_y_primas_anuales_cop
    saldo_cuota_inicial_con_salario = max(0.0, cuota_inicial_total_cop - aporte_cesantias_total)
    cuota_inicial_mensual_cop = (
        saldo_cuota_inicial_con_salario / plazo_entrega_planos_meses if plazo_entrega_planos_meses > 0 else 0.0
    )

    # Crédito en Pesos vs UVR (Ley 546 de 1999)
    plazo_meses = plazo_credito_anios * 12
    tasa_em_pesos = ea_a_em(tasa_ea_pesos)
    seguros_hipoteca_mensual_cop = monto_credito_cop * 0.00065  # ~0.065% mensual seguro vida + incendio/terremoto
    primera_cuota_pesos_sin_seguro = cuota_fija_francesa(monto_credito_cop, tasa_em_pesos, plazo_meses)
    primera_cuota_pesos_total = primera_cuota_pesos_sin_seguro + seguros_hipoteca_mensual_cop

    # Primera cuota en UVR (tasa real + inflación IPC)
    tasa_em_uvr_real = ea_a_em(tasa_ea_uvr_mas_spread)
    primera_cuota_uvr_en_pesos = cuota_fija_francesa(monto_credito_cop, tasa_em_uvr_real, plazo_meses) + seguros_hipoteca_mensual_cop
    # Proyección cuota UVR al año 5 ajustada por inflación acumulada
    cuota_uvr_anio_5_cop = primera_cuota_uvr_en_pesos * ((1.0 + ipc_anual) ** 5)

    # Validación Ley 546 de 1999 (Regla del 30%)
    tope_cuota_ley_546_cop = ingreso_familiar_neto_cop * float(viv["relacion_max_cuota_ingreso"])
    cumple_ley_546_pesos = primera_cuota_pesos_total <= tope_cuota_ley_546_cop
    cumple_ley_546_uvr = primera_cuota_uvr_en_pesos <= tope_cuota_ley_546_cop
    ingreso_familiar_minimo_pesos = primera_cuota_pesos_total / float(viv["relacion_max_cuota_ingreso"])

    # Analítica de Rentabilidad Inmobiliaria (Ley 820 de 2003: Canon <= 1% del valor comercial)
    tope_canon_ley_820 = valor_inmueble_cop * float(viv["canon_max_ley_820_mensual_pct"])
    canon_mensual = min(
        canon_arriendo_mensual_estimado_cop if canon_arriendo_mensual_estimado_cop is not None else valor_inmueble_cop * 0.0065,
        tope_canon_ley_820,
    )

    ingreso_bruto_anual_renta = canon_mensual * 12.0 * (1.0 - 0.05)  # 5% vacancia técnica
    costos_operativos_anuales = (
        valor_inmueble_cop * 0.008  # Impuesto predial + mantenimiento (~0.8% anual)
        + (canon_mensual * 12.0 * 0.12)  # Administración / gestión inmobiliaria
    )
    noi_ingreso_operativo_neto_anual = max(0.0, ingreso_bruto_anual_renta - costos_operativos_anuales)
    cap_rate_neto = noi_ingreso_operativo_neto_anual / valor_inmueble_cop if valor_inmueble_cop > 0 else 0.0

    # Flujo de caja a 10 años para VPN y TIR del inversionista
    desembolso_inicial = cuota_inicial_total_cop + gastos_escrituracion_cop
    flujos_anuales: List[float] = [-desembolso_inicial]
    servicio_deuda_anual = primera_cuota_pesos_total * 12.0
    valorizacion_anual = ipc_anual + 0.015  # IPC + 1.5% real

    for anio in range(1, 11):
        noi_t = noi_ingreso_operativo_neto_anual * ((1.0 + ipc_anual) ** (anio - 1))
        flujo_neto_t = noi_t - servicio_deuda_anual
        if anio == 10:
            valor_venta_anio_10 = valor_inmueble_cop * ((1.0 + valorizacion_anual) ** 10)
            ganancia_ocasional_impuesto = max(0.0, (valor_venta_anio_10 - valor_inmueble_cop) * 0.15)
            saldo_deuda_aprox_anio_10 = monto_credito_cop * 0.45
            flujo_neto_t += valor_venta_anio_10 - ganancia_ocasional_impuesto - saldo_deuda_aprox_anio_10
        flujos_anuales.append(round(flujo_neto_t, 2))

    vpn_inmobiliario = calcular_vpn(costo_oportunidad_ea, flujos_anuales)
    tir_inmobiliaria = calcular_tir(flujos_anuales)

    return {
        "segmento_vivienda": segmento,
        "valor_inmueble_smmlv": round(valor_en_smmlv, 2),
        "cuota_inicial_total_cop": round(cuota_inicial_total_cop, 2),
        "gastos_escrituracion_registro_cop": round(gastos_escrituracion_cop, 2),
        "cuota_inicial_mensual_cop": round(cuota_inicial_mensual_cop, 2),
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
    }
