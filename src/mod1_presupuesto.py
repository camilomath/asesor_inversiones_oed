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

# Catálogo estandarizado de microgastos cotidianos en Colombia para lista desplegable de asesoría
CATALOGO_MICROGASTOS_SUGERIDOS: List[Dict[str, Any]] = [
    {
        "id": "cafe_calle",
        "categoria": "Bebidas y Antojos Diarios",
        "concepto": "Café / tinto / capuchino en calle",
        "monto_unitario_cop": 6500,
        "frecuencia_mensual": 20,
        "sustituto_ahorro": "Llevar termo de café preparado en casa y limitar compras a 1 vez por semana.",
    },
    {
        "id": "empanada_panaderia",
        "categoria": "Bebidas y Antojos Diarios",
        "concepto": "Empanada / panadería / mecato media mañana",
        "monto_unitario_cop": 5500,
        "frecuencia_mensual": 20,
        "sustituto_ahorro": "Comprar fruta o frutos secos al por mayor en el mercado mensual.",
    },
    {
        "id": "postres_bebidas",
        "categoria": "Bebidas y Antojos Diarios",
        "concepto": "Postres, helados o bebidas azucaradas",
        "monto_unitario_cop": 9500,
        "frecuencia_mensual": 10,
        "sustituto_ahorro": "Reemplazar bebidas individuales en tienda por botella reutilizable.",
    },
    {
        "id": "agua_gaseosa",
        "categoria": "Bebidas y Antojos Diarios",
        "concepto": "Botellas de agua / gaseosas al detal",
        "monto_unitario_cop": 4000,
        "frecuencia_mensual": 15,
        "sustituto_ahorro": "Portar termo personal recargable todos los días.",
    },
    {
        "id": "cigarrillos_vapeo",
        "categoria": "Bebidas y Antojos Diarios",
        "concepto": "Cigarrillos / vapeadores / tabaco",
        "monto_unitario_cop": 12000,
        "frecuencia_mensual": 12,
        "sustituto_ahorro": "Reducir progresivamente hasta eliminar por salud física y financiera.",
    },
    {
        "id": "domicilios_apps",
        "categoria": "Comidas Fuera y Domicilios",
        "concepto": "Domicilios por apps (recargos + propinas)",
        "monto_unitario_cop": 18000,
        "frecuencia_mensual": 8,
        "sustituto_ahorro": "Cocinar porciones extra (meal-prep) para evitar pedir por cansancio entre semana.",
    },
    {
        "id": "almuerzo_fuera",
        "categoria": "Comidas Fuera y Domicilios",
        "concepto": "Almuerzos fuera en lugar de llevar de casa",
        "monto_unitario_cop": 18500,
        "frecuencia_mensual": 15,
        "sustituto_ahorro": "Llevar almuerzo casero al menos 3 o 4 días hábiles por semana.",
    },
    {
        "id": "comidas_rapidas_fds",
        "categoria": "Comidas Fuera y Domicilios",
        "concepto": "Comidas rápidas / salidas de fin de semana",
        "monto_unitario_cop": 38000,
        "frecuencia_mensual": 4,
        "sustituto_ahorro": "Definir un tope mensual fijo de ocio gastronómico en efectivo.",
    },
    {
        "id": "licores_rumbas",
        "categoria": "Comidas Fuera y Domicilios",
        "concepto": "Cervezas / licores / salidas nocturnas",
        "monto_unitario_cop": 45000,
        "frecuencia_mensual": 4,
        "sustituto_ahorro": "Espaciar salidas nocturnas a máximo 1 o 2 veces al mes con presupuesto cerrado.",
    },
    {
        "id": "streaming_extra",
        "categoria": "Suscripciones, Apps y Juegos",
        "concepto": "Plataforma de streaming sin uso frecuente",
        "monto_unitario_cop": 38900,
        "frecuencia_mensual": 1,
        "sustituto_ahorro": "Cancelar suscripciones simultáneas y rotar máximo 1 plataforma por mes.",
    },
    {
        "id": "apps_premium",
        "categoria": "Suscripciones, Apps y Juegos",
        "concepto": "Música / almacenamiento / apps premium duplicadas",
        "monto_unitario_cop": 24900,
        "frecuencia_mensual": 1,
        "sustituto_ahorro": "Auditar cobros automáticos en tarjeta y usar planes familiares o gratuitos.",
    },
    {
        "id": "videojuegos_micro",
        "categoria": "Suscripciones, Apps y Juegos",
        "concepto": "Videojuegos / microtransacciones en línea",
        "monto_unitario_cop": 30000,
        "frecuencia_mensual": 3,
        "sustituto_ahorro": "Desvincular la tarjeta de crédito de tiendas de juegos y apps móviles.",
    },
    {
        "id": "apuestas_azar",
        "categoria": "Suscripciones, Apps y Juegos",
        "concepto": "Apuestas deportivas / casino online / chance",
        "monto_unitario_cop": 15000,
        "frecuencia_mensual": 8,
        "sustituto_ahorro": "Suspender totalmente apuestas de esperanza matemática negativa y redirigir a FIC.",
    },
    {
        "id": "taxi_apps_prisa",
        "categoria": "Transporte y Compras Impulsivas",
        "concepto": "Taxi / app de transporte por salir tarde",
        "monto_unitario_cop": 16500,
        "frecuencia_mensual": 8,
        "sustituto_ahorro": "Salir 15 minutos antes usando transporte público o ruta programada.",
    },
    {
        "id": "parqueaderos_propinas",
        "categoria": "Transporte y Compras Impulsivas",
        "concepto": "Parqueaderos ocasionales / propinas varias",
        "monto_unitario_cop": 8000,
        "frecuencia_mensual": 10,
        "sustituto_ahorro": "Planificar diligencias en una sola salida semanal.",
    },
    {
        "id": "retiros_cajero_costo",
        "categoria": "Transporte y Compras Impulsivas",
        "concepto": "Retiros en cajeros no propios / transferencias con costo",
        "monto_unitario_cop": 6500,
        "frecuencia_mensual": 4,
        "sustituto_ahorro": "Usar transferencias gratuitas (Transfiya / PSE) y cajeros de su propia red.",
    },
    {
        "id": "compras_impulsivas",
        "categoria": "Transporte y Compras Impulsivas",
        "concepto": "Compras impulsivas / ofertas relámpago online",
        "monto_unitario_cop": 55000,
        "frecuencia_mensual": 2,
        "sustituto_ahorro": "Aplicar la regla de espera de 72 horas antes de pagar cualquier oferta no vital.",
    },
    {
        "id": "otro_personalizado",
        "categoria": "Personalizado",
        "concepto": "Otro microgasto personalizado",
        "monto_unitario_cop": 10000,
        "frecuencia_mensual": 1,
        "sustituto_ahorro": "Registrar y fijar un tope mensual estricto para gastos varios.",
    },
]

_CONFIG_CACHE: Dict[str, Any] | None = None


def _obtener_config_rapida(config: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Retorna la configuración en memoria evitando lecturas repetitivas de disco en cada cálculo."""
    global _CONFIG_CACHE
    if config is not None:
        return config
    if _CONFIG_CACHE is None:
        _CONFIG_CACHE = cargar_configuracion()
    return _CONFIG_CACHE


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

    cfg = _obtener_config_rapida(config)
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
        if 0 < salarios_minimos < min_integral_smmlv:
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
    cfg = _obtener_config_rapida(config)
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
    tasa_oportunidad_ea: float = 0.10,
    recorte_hormiga_simulacion_pct: float = 50.0,
    config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Ejecuta el Caso de Uso CU-01 (Módulo 1 - Nidia Velásquez):
    - Liquida la Radiografía del Sueldo Colombiano (Empleado, Integral o Independiente OPS).
    - Ejecuta el Balance Termodinámico de Caja y evalúa la Regla 50/30/20.
    - Cuantifica gastos hormiga + fugas financieras (4x1000, cuotas de manejo) y su costo de
      oportunidad a 5 y 10 años a la tasa `tasa_oportunidad_ea` (por defecto 10% EA).
    - Ejecuta el Optimizador Ingenieril de Tributos (AFC/FPV), Ranking Pareto 80/20 de Fugas
      y Simulación Interactiva "¿Qué pasa si...?".
    - Evalúa el Termómetro de Fondo de Emergencia (3 meses empleados / 6 meses independientes)
      y aplica los flujos alternativos FA-01 (Déficit Crítico) y FA-02 (Asignación 80/20).
    - Respeta íntegramente el Contrato de Integración OED hacia los Módulos 2, 3, 4 y 5.
    """
    cfg = _obtener_config_rapida(config)
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
        tasa_oportunidad_ea=tasa_oportunidad_ea,
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

    # Reglas de decisión CU-01 (Sesión en Ceros vs. Camino Feliz vs. FA-01 vs. FA-02)
    if idn <= 0 and egresos_totales <= 0 and liquidez_actual_fondo_emergencia_cop <= 0:
        estado_flujo_caja = "SESION_EN_CEROS"
        plan_accion = {
            "codigo_flujo": "CU-01-INIT",
            "bloquea_inversion_riesgo": False,
            "aporte_recomendado_fondo_emergencia_cop": 0.0,
            "aporte_disponible_portafolio_mod2_cop": 0.0,
            "meses_estimados_completar_fondo": None,
            "recorte_inmediato_fugas_cop": 0.0,
            "recorte_adicional_variables_cop": 0.0,
            "recomendacion_ejecutiva": (
                "Sesión de asesoría iniciada en ceros ($0 COP). Ingrese el salario, la modalidad contractual "
                "y los gastos mensuales del asesorado para generar su radiografía y plan de acción."
            ),
        }
    elif excedente_mensual_cop < 0:
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
        plazo_txt = f"durante ~{meses_para_meta} meses " if meses_para_meta is not None else ""
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
                f"(Bolsillo remunerado Fogafín / FIC a la vista) {plazo_txt}y el 20% "
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
    resultado["optimizacion_ingenieril"] = optimizar_presupuesto_y_tributos(
        diagnostico_actual=resultado,
        monto_movimientos_gmf_mensual_cop=monto_movimientos_gmf_mensual_cop,
        clase_riesgo_arl=clase_riesgo_arl,
        recorte_hormiga_pct=recorte_hormiga_simulacion_pct,
        tasa_oportunidad_ea=tasa_oportunidad_ea,
        config=cfg,
    )
    resultado["guia_asesoria"] = generar_guia_ahorro_y_abstencion(
        diagnostico_actual=resultado,
        optimizacion=resultado["optimizacion_ingenieril"],
        tasa_oportunidad_ea=tasa_oportunidad_ea,
    )
    return resultado


def generar_guia_ahorro_y_abstencion(
    diagnostico_actual: Dict[str, Any],
    optimizacion: Dict[str, Any],
    tasa_oportunidad_ea: float = 0.10,
) -> Dict[str, Any]:
    """
    Genera recomendaciones accionables de asesoría financiera personalizada:
    1. `consejos_ahorro`: Estrategias cuantificadas en COP para incrementar ahorro, blindar liquidez
       y optimizar impuestos/costos bancarios según la modalidad laboral del asesorado.
    2. `en_que_abstenerse`: Lista priorizada de hábitos, productos y compromisos financieros de los
       cuales el asesorado debe abstenerse de inmediato según su flujo de caja y microgastos reales.
    """
    idn = float(diagnostico_actual["ingreso_neto_mensual_cop"])
    egresos = float(diagnostico_actual["egresos_totales_mensuales_cop"])
    excedente = float(diagnostico_actual["excedente_mensual_cop"])
    estado = str(diagnostico_actual["estado_flujo_caja"])

    if estado == "SESION_EN_CEROS" or (idn <= 0 and egresos <= 0):
        return {
            "sesion_activa": False,
            "meta_ahorro_mensual_sugerida_cop": 0.0,
            "resumen_orientacion": (
                "Sesión limpia en ceros ($0 COP). Complete los datos del asesorado para obtener "
                "los consejos personalizados de ahorro y la guía de abstención financiera."
            ),
            "consejos_ahorro": [],
            "en_que_abstenerse": [],
        }

    nom = diagnostico_actual["liquidacion_nomina"]
    modalidad = str(nom["modalidad_laboral"])
    fugas = diagnostico_actual["radiografia_fugas"]
    bal = diagnostico_actual["balance_50_30_20"]
    afc_opt = optimizacion["tributaria_afc"]
    pareto = optimizacion["ranking_pareto_fugas"]

    meta_20_cop = round(max(0.0, idn * 0.20), 2)
    consejos: List[Dict[str, Any]] = []
    abstenciones: List[Dict[str, Any]] = []

    # --- A. CONSEJOS PERSONALIZADOS DE AHORRO ---
    monto_auto = round(max(0.0, min(excedente, meta_20_cop) if excedente > 0 else meta_20_cop * 0.5), 2)
    vf_auto_10a = valor_futuro_aportes_periodicos(monto_auto, tasa_ea=tasa_oportunidad_ea, meses=120)[
        "valor_futuro_nominal_cop"
    ]
    if excedente > 0:
        consejos.append(
            {
                "titulo": "Automatizar el 'Páguese Primero' el mismo día de nómina",
                "accion": (
                    f"Programe un débito automático mensual de ${monto_auto:,.0f} COP hacia un bolsillo remunerado "
                    f"o FIC a la vista apenas reciba su ingreso, antes de iniciar gastos corrientes."
                ),
                "impacto_mensual_cop": monto_auto,
                "impacto_10a_cop": vf_auto_10a,
                "prioridad": "ALTA",
            }
        )
    else:
        brecha = abs(excedente)
        consejos.append(
            {
                "titulo": "Plan de Choque de Caja (Presupuesto Base Cero por 60 días)",
                "accion": (
                    f"Congele gastos no vitales para cerrar el déficit de ${brecha:,.0f} COP/mes y liberar "
                    f"gradualmente su meta saludable de ahorro del 20% (${meta_20_cop:,.0f} COP/mes)."
                ),
                "impacto_mensual_cop": round(brecha, 2),
                "impacto_10a_cop": 0.0,
                "prioridad": "CRITICA",
            }
        )

    # Consejo de Fondo de Emergencia
    faltante_em = float(diagnostico_actual["faltante_fondo_emergencia_cop"])
    meta_meses = float(diagnostico_actual["meta_meses_fondo_emergencia"])
    if not diagnostico_actual["fondo_emergencia_completo"] and faltante_em > 0:
        aporte_80 = round(max(0.0, excedente * 0.80), 2)
        consejos.append(
            {
                "titulo": f"Blindar Fondo de Emergencia ({meta_meses:.0f} meses — {modalidad})",
                "accion": (
                    f"Le faltan ${faltante_em:,.0f} COP para cubrir {meta_meses:.0f} meses de costos fijos vitales. "
                    "Alójelo en cuenta de alto rendimiento con seguro Fogafín o FIC líquido sin pacto de permanencia."
                ),
                "impacto_mensual_cop": aporte_80,
                "impacto_10a_cop": 0.0,
                "prioridad": "ALTA",
            }
        )
    elif diagnostico_actual["fondo_emergencia_completo"] and idn > 0:
        consejos.append(
            {
                "titulo": "Fondo de Emergencia Completo: migrar excedentes a inversión productiva",
                "accion": (
                    "Su colchón de liquidez ya cumple la meta. Evite dejar dinero ocioso perdiendo poder adquisitivo "
                    f"frente al IPC y direccione sus ${max(0.0, excedente):,.0f} COP/mes hacia portafolios del Módulo 2."
                ),
                "impacto_mensual_cop": round(max(0.0, excedente), 2),
                "impacto_10a_cop": valor_futuro_aportes_periodicos(
                    max(0.0, excedente), tasa_ea=tasa_oportunidad_ea, meses=120
                )["valor_futuro_nominal_cop"],
                "prioridad": "MEDIA",
            }
        )

    # Consejo de rescate del 50% de microgastos
    hormiga_mes = float(fugas["gastos_hormiga_mensual_cop"])
    if hormiga_mes > 0:
        rescate_50 = round(hormiga_mes * 0.50, 2)
        vf_50 = valor_futuro_aportes_periodicos(rescate_50, tasa_ea=tasa_oportunidad_ea, meses=120)[
            "valor_futuro_nominal_cop"
        ]
        consejos.append(
            {
                "titulo": "Regla 50/50 sobre Microgastos Cotidianos",
                "accion": (
                    f"Sin eliminar todos sus gustos, reducir a la mitad sus microgastos libera ${rescate_50:,.0f} COP/mes "
                    f"que invertidos al {tasa_oportunidad_ea * 100:.1f}% EA construyen ${vf_50:,.0f} COP en 10 años."
                ),
                "impacto_mensual_cop": rescate_50,
                "impacto_10a_cop": vf_50,
                "prioridad": "ALTA" if fugas["alerta_fuga_presion"] else "MEDIA",
            }
        )

    # Consejo tributario AFC / FPV
    if afc_opt["aplica_optimizacion_afc"] and float(afc_opt["ahorro_tributario_mensual_cop"]) > 0:
        ahorro_trib = float(afc_opt["ahorro_tributario_mensual_cop"])
        consejos.append(
            {
                "titulo": "Capturar subsidio tributario legal vía cuenta AFC o FPV",
                "accion": (
                    f"Canalizar ${afc_opt['aporte_afc_optimo_mensual_cop']:,.0f} COP/mes de su ahorro hacia AFC (vivienda) "
                    f"o Pensión Voluntaria reduce su Retefuente en ${ahorro_trib:,.0f} COP cada mes (Ley 2277/2022)."
                ),
                "impacto_mensual_cop": round(ahorro_trib, 2),
                "impacto_10a_cop": valor_futuro_aportes_periodicos(
                    ahorro_trib, tasa_ea=tasa_oportunidad_ea, meses=120
                )["valor_futuro_nominal_cop"],
                "prioridad": "ALTA",
            }
        )

    # Consejo bancario (4x1000 + cuotas manejo)
    friccion_bancos = float(fugas["friccion_bancaria_mensual_cop"])
    if friccion_bancos > 0:
        consejos.append(
            {
                "titulo": "Eliminar costos bancarios invisibles (Cuotas de Manejo y 4x1000)",
                "accion": (
                    f"Marque su cuenta principal como exenta del 4x1000 (hasta 350 UVT/mes) y migre a cuentas/tarjetas "
                    f"con $0 cuota de manejo para recuperar ${friccion_bancos:,.0f} COP mensuales."
                ),
                "impacto_mensual_cop": round(friccion_bancos, 2),
                "impacto_10a_cop": valor_futuro_aportes_periodicos(
                    friccion_bancos, tasa_ea=tasa_oportunidad_ea, meses=120
                )["valor_futuro_nominal_cop"],
                "prioridad": "MEDIA",
            }
        )

    # Consejo según modalidad laboral
    prov = nom["provisiones_prestacionales_informativas"]
    if modalidad == "Empleado" and float(prov["prima_servicios_mensualizada_cop"]) > 0:
        prima_anual = round(float(prov["prima_servicios_mensualizada_cop"]) * 12.0, 2)
        consejos.append(
            {
                "titulo": "Blindar el 100% de las Primas de Junio y Diciembre",
                "accion": (
                    f"Como empleado ordinario, usted acumula ~${prima_anual:,.0f} COP/año en primas legales. "
                    "Comprométase a invertirlas o abonarlas a capital de deuda en lugar de gastarlas en temporada."
                ),
                "impacto_mensual_cop": round(float(prov["prima_servicios_mensualizada_cop"]), 2),
                "impacto_10a_cop": 0.0,
                "prioridad": "MEDIA",
            }
        )
    elif modalidad == "Independiente":
        ss_ops = round(
            float(nom["salud_obligatoria_cop"]) + float(nom["pension_obligatoria_cop"]) + float(nom["arl_cop"]), 2
        )
        consejos.append(
            {
                "titulo": "Separar provisión intocable de Seguridad Social PILA e Impuestos",
                "accion": (
                    f"Como contratista OPS, aparte inmediatamente ${ss_ops:,.0f} COP/mes para PILA apenas cobre cada "
                    "cuenta de cobro; nunca mezcle el dinero de seguridad social con la caja de gastos personales."
                ),
                "impacto_mensual_cop": ss_ops,
                "impacto_10a_cop": 0.0,
                "prioridad": "ALTA",
            }
        )

    # --- B. EN QUÉ DEBE ABSTENERSE EL ASESORADO ---
    if excedente < 0:
        abstenciones.append(
            {
                "habito_o_rubro": "Endeudamiento con tarjeta de crédito, avances y compras a cuotas",
                "motivo": f"Su flujo actual presenta un déficit de -${abs(excedente):,.0f} COP/mes.",
                "accion_inmediata": (
                    "Abstenerse por completo de diferir compras corrientes (mercado, ropa, restaurantes) con tasas "
                    "cercanas a la usura (~28%-32% EA) y de tomar créditos rotativos para cubrir el mes."
                ),
                "ahorro_estimado_mensual_cop": round(abs(excedente), 2),
                "severidad": "CRITICA",
            }
        )

    if not diagnostico_actual["fondo_emergencia_completo"]:
        abstenciones.append(
            {
                "habito_o_rubro": "Inversiones ilíquidas, criptoactivos volátiles o préstamos a familiares/terceros",
                "motivo": (
                    f"Su fondo de emergencia cubre solo {diagnostico_actual['meses_fondo_emergencia']:.2f} "
                    f"de los {meta_meses:.0f} meses requeridos."
                ),
                "accion_inmediata": (
                    "Abstenerse de inmovilizar capital a largo plazo o asumir riesgos sin colchón de liquidez, "
                    "así como de adquirir nuevos compromisos fijos mensuales."
                ),
                "ahorro_estimado_mensual_cop": 0.0,
                "severidad": "ALTA",
            }
        )

    deuda_pct = float(bal.get("servicio_deuda_pct", 0.0))
    if deuda_pct > 25.0:
        abstenciones.append(
            {
                "habito_o_rubro": "Nuevos créditos, leasing vehicular o ser codeudor/fiador",
                "motivo": f"El servicio de deuda ya absorbe el {deuda_pct:.1f}% de su ingreso disponible neto.",
                "accion_inmediata": (
                    "Abstenerse de adquirir cualquier obligación financiera adicional hasta bajar la carga de deuda "
                    "por debajo del 20% del ingreso neto (apóyese en bola de nieve/avalancha del Módulo 3)."
                ),
                "ahorro_estimado_mensual_cop": round(float(diagnostico_actual["cuotas_deuda_mensual_cop"]) * 0.25, 2),
                "severidad": "ALTA",
            }
        )

    if idn > 0 and not bal["necesidades_50"]["cumple"]:
        exceso_fijos = max(0.0, float(bal["necesidades_50"].get("desviacion_cop", 0.0)))
        abstenciones.append(
            {
                "habito_o_rubro": "Incrementar costos fijos (mudarse a arriendo más caro o subir planes fijos)",
                "motivo": f"Sus costos vitales ocupan el {bal['necesidades_50']['real_pct']:.1f}% del sueldo neto (tope sano: 50%).",
                "accion_inmediata": (
                    "Abstenerse de asumir contratos fijos más altos y renegociar planes de internet, telefonía, "
                    "seguros o vivienda."
                ),
                "ahorro_estimado_mensual_cop": round(exceso_fijos, 2),
                "severidad": "MEDIA",
            }
        )

    if idn > 0 and not bal["estilo_vida_30"]["cumple"]:
        exceso_est = max(0.0, float(bal["estilo_vida_30"].get("desviacion_cop", 0.0)))
        abstenciones.append(
            {
                "habito_o_rubro": "Gastos emocionales de quincena y salidas sociales fuera de presupuesto",
                "motivo": f"Estilo de vida + fugas alcanzan el {bal['estilo_vida_30']['real_pct']:.1f}% del IDN (límite: 30%).",
                "accion_inmediata": (
                    "Abstenerse de gastar sin tope semanal; asigne un monto cerrado para ocio y deténgase al agotarlo."
                ),
                "ahorro_estimado_mensual_cop": round(exceso_est, 2),
                "severidad": "MEDIA",
            }
        )

    # Abstenciones específicas según los microgastos reales registrados por el usuario
    for item_p in pareto[:4]:
        nombre_low = item_p["origen"].lower()
        monto_m = float(item_p["monto_mensual_cop"])
        if monto_m <= 0:
            continue

        if any(k in nombre_low for k in ("apuesta", "casino", "chance", "loter", "juego", "azar")):
            abstenciones.append(
                {
                    "habito_o_rubro": f"Apuestas y juegos de azar ({item_p['origen']})",
                    "motivo": f"Drena ${monto_m:,.0f} COP/mes con esperanza matemática negativa.",
                    "accion_inmediata": "Abstenerse al 100% de apuestas deportivas, casinos en línea y juegos de azar.",
                    "ahorro_estimado_mensual_cop": round(monto_m, 2),
                    "severidad": "CRITICA",
                }
            )
        elif any(k in nombre_low for k in ("cigarr", "vape", "tabaco", "licor", "cervez", "rumba")):
            abstenciones.append(
                {
                    "habito_o_rubro": f"Consumo recurrente de tabaco/vapeo o licor ({item_p['origen']})",
                    "motivo": f"Consume ${monto_m:,.0f} COP/mes (${monto_m * 12:,.0f} COP/año) deteriorando salud y caja.",
                    "accion_inmediata": "Abstenerse de compras habituales y restringir salidas nocturnas a presupuesto fijo.",
                    "ahorro_estimado_mensual_cop": round(monto_m * 0.75, 2),
                    "severidad": "ALTA",
                }
            )
        elif any(k in nombre_low for k in ("domicili", "rappi", "almuerz", "restauran", "comida")):
            abstenciones.append(
                {
                    "habito_o_rubro": f"Domicilios y comidas fuera por falta de planeación ({item_p['origen']})",
                    "motivo": f"Representa ${monto_m:,.0f} COP/mes ({item_p['participacion_pct']}% de sus fugas).",
                    "accion_inmediata": "Abstenerse de pedir domicilios entre semana; los recargos y propinas encarecen hasta 40% cada plato.",
                    "ahorro_estimado_mensual_cop": round(monto_m * 0.60, 2),
                    "severidad": "ALTA" if item_p["impacto_pareto_80"] else "MEDIA",
                }
            )
        elif any(k in nombre_low for k in ("stream", "suscrip", "premium", "app", "musica", "videojueg")):
            abstenciones.append(
                {
                    "habito_o_rubro": f"Suscripciones pasivas y microtransacciones ({item_p['origen']})",
                    "motivo": f"Cargo automático recurrente de ${monto_m:,.0f} COP/mes.",
                    "accion_inmediata": "Abstenerse de pagar plataformas simultáneas que no use cada semana; cancele cobros automáticos hoy.",
                    "ahorro_estimado_mensual_cop": round(monto_m * 0.70, 2),
                    "severidad": "MEDIA",
                }
            )
        elif any(k in nombre_low for k in ("impuls", "promo", "oferta", "compra")):
            abstenciones.append(
                {
                    "habito_o_rubro": f"Compras impulsivas y 'descuentos relámpago' ({item_p['origen']})",
                    "motivo": f"Fuga mensual de ${monto_m:,.0f} COP en artículos no presupuestados.",
                    "accion_inmediata": "Abstenerse de comprar en caliente: aplique la Regla de las 72 Horas y borre tarjetas guardadas en navegadores.",
                    "ahorro_estimado_mensual_cop": round(monto_m * 0.80, 2),
                    "severidad": "ALTA",
                }
            )
        elif any(k in nombre_low for k in ("taxi", "movilidad", "uber", "didi", "parquead")):
            abstenciones.append(
                {
                    "habito_o_rubro": f"Transporte individual por urgencia ({item_p['origen']})",
                    "motivo": f"Gasto evitable de ${monto_m:,.0f} COP/mes.",
                    "accion_inmediata": "Abstenerse de pedir apps de transporte en tarifa dinámica por salir sobre el tiempo.",
                    "ahorro_estimado_mensual_cop": round(monto_m * 0.50, 2),
                    "severidad": "MEDIA",
                }
            )
        elif item_p["impacto_pareto_80"]:
            abstenciones.append(
                {
                    "habito_o_rubro": f"Microgasto reiterativo en «{item_p['origen']}»",
                    "motivo": f"Concentra ${monto_m:,.0f} COP/mes ({item_p['participacion_pct']}% del drenaje hormiga).",
                    "accion_inmediata": "Abstenerse del consumo diario automático al detal y sustituirlo por planeación mensual.",
                    "ahorro_estimado_mensual_cop": round(monto_m * 0.50, 2),
                    "severidad": "MEDIA",
                }
            )

    if not abstenciones:
        abstenciones.append(
            {
                "habito_o_rubro": "Inflación de estilo de vida (Lifestyle Creep) e inversiones no reguladas",
                "motivo": "Su presupuesto actual está sano y equilibrado.",
                "accion_inmediata": (
                    "Abstenerse de elevar sus gastos fijos cuando reciba aumentos salariales y de invertir en "
                    "esquemas no vigilados por la Superfinanciera de Colombia."
                ),
                "ahorro_estimado_mensual_cop": 0.0,
                "severidad": "PREVENTIVA",
            }
        )

    return {
        "sesion_activa": True,
        "meta_ahorro_mensual_sugerida_cop": meta_20_cop,
        "resumen_orientacion": (
            f"Meta saludable de ahorro (20% IDN): ${meta_20_cop:,.0f} COP/mes · "
            f"Se identificaron {len(consejos)} acciones de ahorro y {len(abstenciones)} alertas de abstención."
        ),
        "consejos_ahorro": consejos,
        "en_que_abstenerse": abstenciones,
    }


def optimizar_presupuesto_y_tributos(
    diagnostico_actual: Dict[str, Any],
    monto_movimientos_gmf_mensual_cop: float = 0.0,
    clase_riesgo_arl: int = 1,
    recorte_hormiga_pct: float = 50.0,
    tasa_oportunidad_ea: float = 0.10,
    config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Motor de Optimización Presupuestal y Tributaria (Sello Ingenieril Mód. 1):
    1. Búsqueda del punto óptimo (knee-point) de Aporte AFC / FPV bajo Ley 2277 de 2022
       que maximiza el ahorro mensual en Retención en la Fuente sin aportar pesos ociosos
       por encima del tope global del 40% / 1340 UVT ni comprometer la liquidez disponible.
    2. Análisis de Pareto (80/20) sobre todas las fugas presupuestales y bancarias.
    3. Simulación interactiva "¿Qué pasa si...?" recortando `recorte_hormiga_pct`% de gastos
       hormiga y eliminando costos bancarios evitables (cuotas de manejo y marcación 4x1000).
    """
    cfg = _obtener_config_rapida(config)
    macro = cfg["parametros_macro_colombia"]
    lab = cfg["parametros_laborales_y_tributarios"]
    uvt = float(macro["uvt_cop"])

    nom = diagnostico_actual["liquidacion_nomina"]
    bruto = float(nom["ingreso_bruto_mensual_cop"])
    modalidad = str(nom["modalidad_laboral"])

    # 1. Optimización Tributaria AFC / FPV (comparada contra escenario base con $0 AFC)
    nom_base = liquidar_ingreso_neto_colombia(
        ingreso_bruto_mensual_cop=bruto,
        modalidad_laboral=modalidad,
        aporte_voluntario_afc_fpv_cop=0.0,
        clase_riesgo_arl=clase_riesgo_arl,
        config=cfg,
    )
    rete_base = float(nom_base["retencion_fuente_cop"])
    egresos_sin_afc = float(diagnostico_actual["egresos_totales_mensuales_cop"])
    idn_base = float(nom_base["ingreso_neto_mensual_cop"]) + float(
        diagnostico_actual.get("otros_ingresos_mensuales_cop", 0.0)
    )
    capacidad_caja = max(0.0, idn_base - egresos_sin_afc)
    tope_legal_afc = bruto * float(lab["beneficio_max_afc_fpv_pct"])
    limite_busqueda = min(tope_legal_afc, max(capacidad_caja, bruto * 0.15))

    aporte_afc_optimo = 0.0
    max_ahorro_rete = 0.0
    if rete_base > 0 and limite_busqueda >= 25_000.0:
        paso = 25_000.0
        candidato = paso
        while candidato <= limite_busqueda + 1.0:
            nom_cand = liquidar_ingreso_neto_colombia(
                ingreso_bruto_mensual_cop=bruto,
                modalidad_laboral=modalidad,
                aporte_voluntario_afc_fpv_cop=candidato,
                clase_riesgo_arl=clase_riesgo_arl,
                config=cfg,
            )
            ahorro = max(0.0, rete_base - float(nom_cand["retencion_fuente_cop"]))
            # Solo avanzar si el incremento sigue produciendo ahorro marginal real (> $500 COP)
            if ahorro > max_ahorro_rete + 500.0:
                max_ahorro_rete = ahorro
                aporte_afc_optimo = candidato
            if float(nom_cand["retencion_fuente_cop"]) <= 0.01:
                break
            candidato += paso

    retorno_fiscal_pct = (max_ahorro_rete / aporte_afc_optimo * 100.0) if aporte_afc_optimo > 0 else 0.0

    # 2. Ranking de Pareto (80/20) de Fugas
    fugas = diagnostico_actual["radiografia_fugas"]
    fuentes_fuga: List[Dict[str, Any]] = []
    for item in fugas.get("detalle_items", []):
        if float(item["gasto_mensual_cop"]) > 0:
            fuentes_fuga.append(
                {
                    "origen": item["concepto"],
                    "categoria": "Gasto Hormiga",
                    "monto_mensual_cop": float(item["gasto_mensual_cop"]),
                }
            )
    if not fuentes_fuga and float(fugas["gastos_hormiga_mensual_cop"]) > 0:
        fuentes_fuga.append(
            {
                "origen": "Gastos hormiga consolidados",
                "categoria": "Gasto Hormiga",
                "monto_mensual_cop": float(fugas["gastos_hormiga_mensual_cop"]),
            }
        )
    if float(fugas["cuotas_manejo_mensual_cop"]) > 0:
        fuentes_fuga.append(
            {
                "origen": "Cuotas de manejo y comisiones bancarias",
                "categoria": "Fricción Bancaria",
                "monto_mensual_cop": float(fugas["cuotas_manejo_mensual_cop"]),
            }
        )
    gmf_con_exencion = calcular_gmf_4x1000(
        monto_retiro_mensual_cop=max(0.0, monto_movimientos_gmf_mensual_cop),
        cuenta_exenta_marcada=True,
        valor_uvt_cop=uvt,
    )
    gmf_evitable = max(0.0, float(fugas["gmf_4x1000_mensual_cop"]) - gmf_con_exencion)
    if float(fugas["gmf_4x1000_mensual_cop"]) > 0:
        fuentes_fuga.append(
            {
                "origen": "GMF 4x1000",
                "categoria": "Impuesto Financiero",
                "monto_mensual_cop": float(fugas["gmf_4x1000_mensual_cop"]),
            }
        )

    fuentes_fuga.sort(key=lambda x: x["monto_mensual_cop"], reverse=True)
    total_fugas_pareto = sum(x["monto_mensual_cop"] for x in fuentes_fuga) or 1.0
    acum_pct = 0.0
    ranking_pareto: List[Dict[str, Any]] = []
    for idx, f_item in enumerate(fuentes_fuga):
        peso = (f_item["monto_mensual_cop"] / total_fugas_pareto) * 100.0
        es_vital_80 = acum_pct < 80.0 or idx == 0
        acum_pct += peso
        ranking_pareto.append(
            {
                "origen": f_item["origen"],
                "categoria": f_item["categoria"],
                "monto_mensual_cop": round(f_item["monto_mensual_cop"], 2),
                "participacion_pct": round(peso, 1),
                "acumulado_pct": round(min(100.0, acum_pct), 1),
                "impacto_pareto_80": es_vital_80,
            }
        )

    # 3. Simulación Interactiva "¿Qué pasa si...?"
    pct_recorte = min(100.0, max(0.0, float(recorte_hormiga_pct))) / 100.0
    ahorro_hormiga_mes = float(fugas["gastos_hormiga_mensual_cop"]) * pct_recorte
    ahorro_bancos_mes = float(fugas["cuotas_manejo_mensual_cop"]) + gmf_evitable
    flujo_rescatado_mes = ahorro_hormiga_mes + ahorro_bancos_mes

    excedente_actual = float(diagnostico_actual["excedente_mensual_cop"])
    excedente_optimizado = excedente_actual + flujo_rescatado_mes + max_ahorro_rete
    idn_actual = float(diagnostico_actual["ingreso_neto_mensual_cop"])
    eficiencia_opt_pct = max(0.0, (excedente_optimizado / (idn_actual + max_ahorro_rete)) * 100.0) if idn_actual > 0 else 0.0

    vf_rescatado_5a = valor_futuro_aportes_periodicos(flujo_rescatado_mes, tasa_ea=tasa_oportunidad_ea, meses=60)
    vf_rescatado_10a = valor_futuro_aportes_periodicos(flujo_rescatado_mes, tasa_ea=tasa_oportunidad_ea, meses=120)

    faltante_em = float(diagnostico_actual["faltante_fondo_emergencia_cop"])
    meses_actual_em = (
        faltante_em / (excedente_actual * 0.80) if (faltante_em > 0 and excedente_actual > 0) else 0.0
    )
    meses_opt_em = (
        faltante_em / (excedente_optimizado * 0.80) if (faltante_em > 0 and excedente_optimizado > 0) else 0.0
    )
    meses_ganados_emergencia = max(0.0, meses_actual_em - meses_opt_em)

    return {
        "tributaria_afc": {
            "aplica_optimizacion_afc": aporte_afc_optimo > 0,
            "retefuente_sin_afc_cop": round(rete_base, 2),
            "aporte_afc_optimo_mensual_cop": round(aporte_afc_optimo, 2),
            "ahorro_tributario_mensual_cop": round(max_ahorro_rete, 2),
            "ahorro_tributario_anual_cop": round(max_ahorro_rete * 12.0, 2),
            "retorno_fiscal_inmediato_pct": round(retorno_fiscal_pct, 2),
        },
        "simulacion_que_pasa_si": {
            "recorte_hormiga_aplicado_pct": round(pct_recorte * 100.0, 1),
            "tasa_ea_simulada_pct": round(tasa_oportunidad_ea * 100.0, 2),
            "ahorro_recorte_hormiga_mensual_cop": round(ahorro_hormiga_mes, 2),
            "ahorro_eliminar_friccion_bancaria_cop": round(ahorro_bancos_mes, 2),
            "flujo_mensual_rescatado_total_cop": round(flujo_rescatado_mes, 2),
            "excedente_actual_cop": round(excedente_actual, 2),
            "excedente_optimizado_cop": round(excedente_optimizado, 2),
            "eficiencia_optimizada_pct": round(eficiencia_opt_pct, 2),
            "patrimonio_rescatado_5a_cop": vf_rescatado_5a["valor_futuro_nominal_cop"],
            "patrimonio_rescatado_10a_cop": vf_rescatado_10a["valor_futuro_nominal_cop"],
            "meses_aceleracion_fondo_emergencia": round(meses_ganados_emergencia, 1),
        },
        "ranking_pareto_fugas": ranking_pareto,
    }


def ejecutar_modulo_1_perfil_usuario(
    perfil_usuario: Dict[str, Any] | None = None,
    config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Adaptador directo para el Contrato de Integración OED (`PLAN_EJECUCION_TALLER_OED.md`):
    Toma un diccionario `perfil_usuario` (o carga `perfil_semilla_taller` de `config.yaml`)
    y retorna el perfil enriquecido con las llaves oficiales del Módulo 1.
    """
    cfg = _obtener_config_rapida(config)
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
    cfg = _obtener_config_rapida(config)
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
        "detalle_gastos_hormiga": (
            datos_entrada["detalle_gastos_hormiga"]
            if "detalle_gastos_hormiga" in datos_entrada and datos_entrada["detalle_gastos_hormiga"] is not None
            else diag["radiografia_fugas"]["detalle_items"]
        ),
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
        "catalogo_microgastos": CATALOGO_MICROGASTOS_SUGERIDOS,
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


def obtener_plantilla_ceros_mod1() -> Dict[str, Any]:
    """Retorna un formulario limpio en ceros ($0 COP) para iniciar una nueva sesión de asesoría."""
    return {
        "modalidad_laboral": "Empleado",
        "clase_riesgo_arl": 1,
        "ingreso_bruto_mensual_cop": 0.0,
        "otros_ingresos_mensuales_cop": 0.0,
        "aporte_voluntario_afc_fpv_cop": 0.0,
        "gastos_fijos_vitales_cop": 0.0,
        "gastos_variables_estilo_vida_cop": 0.0,
        "gastos_hormiga_mensual_cop": 0.0,
        "cuotas_deuda_mensual_cop": 0.0,
        "liquidez_actual_fondo_emergencia_cop": 0.0,
        "cuotas_manejo_mensual_cop": 0.0,
        "monto_movimientos_gmf_mensual_cop": 0.0,
        "cuenta_exenta_4x1000": True,
        "detalle_gastos_hormiga": [],
    }


def culminar_asesoria_y_reiniciar(
    datos_cierre: Dict[str, Any] | None = None,
    nombre_asesorado: str | None = None,
    guardar_cierre_en_historial: bool = True,
    ruta_activo: str | Path | None = None,
    ruta_historial: str | Path | None = None,
    config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Culmina la sesión de asesoría actual y deja la herramienta iniciada en ceros ($0 COP):
    1. Si `guardar_cierre_en_historial=True` y la asesoría tiene valores mayores a cero,
       archiva el expediente culminado en `historial_simulaciones_mod1.json`.
    2. Sobrescribe `perfil_mod1_activo.json` con la plantilla en ceros para que la siguiente
       atención inicie completamente limpia (incluso tras recargar o reiniciar el navegador).
    """
    cfg = _obtener_config_rapida(config)
    item_archivado: Dict[str, Any] | None = None

    if guardar_cierre_en_historial and datos_cierre:
        bruto_cierre = float(datos_cierre.get("ingreso_bruto_mensual_cop", 0.0))
        fijos_cierre = float(datos_cierre.get("gastos_fijos_vitales_cop", 0.0))
        vars_cierre = float(datos_cierre.get("gastos_variables_estilo_vida_cop", 0.0))
        items_cierre = datos_cierre.get("detalle_gastos_hormiga") or []
        tiene_datos = (bruto_cierre > 0) or (fijos_cierre > 0) or (vars_cierre > 0) or (len(items_cierre) > 0)
        if tiene_datos:
            etiqueta_cierre = (nombre_asesorado or "").strip()
            if not etiqueta_cierre:
                mod_txt = str(datos_cierre.get("modalidad_laboral", "Empleado"))
                etiqueta_cierre = f"Asesoría culminada — {mod_txt} (${bruto_cierre:,.0f} COP)"
            guardado_cierre = guardar_simulacion_presupuesto(
                datos_entrada=datos_cierre,
                nombre_escenario=etiqueta_cierre,
                guardar_en_historial=True,
                ruta_activo=ruta_activo,
                ruta_historial=ruta_historial,
                config=cfg,
            )
            item_archivado = guardado_cierre.get("item_historial_creado")

    plantilla_ceros = obtener_plantilla_ceros_mod1()
    reinicio = guardar_simulacion_presupuesto(
        datos_entrada=plantilla_ceros,
        nombre_escenario="Nueva Asesoría (En Ceros)",
        guardar_en_historial=False,
        ruta_activo=ruta_activo,
        ruta_historial=ruta_historial,
        config=cfg,
    )

    return {
        "asesoria_culminada": True,
        "reiniciado_en_ceros": True,
        "parametros_ceros": plantilla_ceros,
        "asesoria_archivada": item_archivado,
        "perfil_activo": reinicio["perfil_activo"],
        "historial": reinicio["historial"],
    }


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
