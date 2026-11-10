"""
Motor Matemático y Financiero Transversal Colombiano (Fase 0).
Líder Responsable: Camilo Matson (Matemático - Líder de Estrategia OED).

Implementa las mejores prácticas financieras y regulatorias en Colombia:
- Conversión exacta de tasas por interés compuesto (EA <-> EM <-> NMV) según Circular Básica SFC.
- Deflactación por IPC DANE y cálculo de Tasa Efectiva Real Neta de impuestos (Retefuente y GMF 4x1000).
- Conversión Pesos Colombianos (COP) <-> UVT (DIAN) y UVR (Banco de la República).
- Validación de límites legales de Tasa de Usura (1.5 x IBC certificado por la SFC).
- Cálculo de Valor Presente Neto (VPN), Tasa Interna de Retorno (TIR) por método de Newton-Raphson/Bisección,
  Valor Futuro con aportes periódicos salariales y Tablas de Amortización en Pesos y UVR.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, List

DEFAULT_CONFIG: Dict[str, Any] = {
    "parametros_macro_colombia": {
        "anio_vigencia": 2026,
        "smmlv_cop": 1_423_500.0,
        "auxilio_transporte_cop": 200_000.0,
        "uvt_cop": 49_799.0,
        "uvr_valor_cop": 382.45,
        "ipc_anual_dane": 0.052,
        "inflacion_educativa_anual": 0.075,
        "tasa_usura_ea_consumo": 0.2650,
        "ibc_ea_consumo": 0.1767,
        "tope_fogafin_cop": 50_000_000.0,
        "gmf_tasa": 0.004,
        "gmf_exencion_uvt_mensual": 350.0,
        "deposito_bajo_monto_tope_uvt": 210.5,
    },
    "parametros_laborales_y_tributarios": {
        "salud_empleado_pct": 0.04,
        "pension_empleado_pct": 0.04,
        "ibc_independiente_pct": 0.40,
        "salud_independiente_pct": 0.125,
        "pension_independiente_pct": 0.16,
        "arl_riesgo_i_pct": 0.00522,
        "salario_integral_min_smmlv": 13.0,
        "factor_prestacional_integral": 0.70,
        "retefuente_rendimientos_fijos": 0.04,
        "retefuente_fics_variable": 0.07,
        "ganancia_ocasional_pct": 0.15,
        "beneficio_max_afc_fpv_pct": 0.30,
    },
    "parametros_vivienda_ley_546": {
        "relacion_max_cuota_ingreso": 0.30,
        "tope_vis_smmlv": 150.0,
        "tope_vip_smmlv": 90.0,
        "cuota_inicial_min_vis_pct": 0.20,
        "cuota_inicial_min_no_vis_pct": 0.30,
        "gastos_escrituracion_registro_pct": 0.03,
        "canon_max_ley_820_mensual_pct": 0.01,
    },
    "catalogo_vehiculos_inversion_colombia": [
        {
            "id": "neobanco_alto_rendimiento",
            "nombre": "Cuenta de Alto Rendimiento / Bolsillo Remunerado (Nu, Lulo, Pibank, Ualá)",
            "tipo": "Liquidez / Renta Fija",
            "monto_minimo_cop": 10_000.0,
            "tasa_ea_esperada": 0.100,
            "volatilidad_anual": 0.005,
            "comision_admin_anual": 0.0,
            "comision_fija_transaccion_cop": 0.0,
            "retefuente_pct": 0.04,
            "cubierto_fogafin": True,
            "perfil_minimo": "Conservador",
        },
        {
            "id": "cdt_digital_sfc",
            "nombre": "CDT Digital Tasa Fija (Vigilado SFC)",
            "tipo": "Renta Fija",
            "monto_minimo_cop": 50_000.0,
            "tasa_ea_esperada": 0.105,
            "volatilidad_anual": 0.008,
            "comision_admin_anual": 0.0,
            "comision_fija_transaccion_cop": 0.0,
            "retefuente_pct": 0.04,
            "cubierto_fogafin": True,
            "perfil_minimo": "Conservador",
        },
        {
            "id": "fic_renta_fija_liquidez",
            "nombre": "Fondo de Inversión Colectiva (FIC) Renta Fija a la Vista",
            "tipo": "FIC Renta Fija",
            "monto_minimo_cop": 20_000.0,
            "tasa_ea_esperada": 0.098,
            "volatilidad_anual": 0.015,
            "comision_admin_anual": 0.012,
            "comision_fija_transaccion_cop": 0.0,
            "retefuente_pct": 0.04,
            "cubierto_fogafin": False,
            "perfil_minimo": "Conservador",
        },
        {
            "id": "cuenta_afc_vivienda",
            "nombre": "Cuenta AFC / Fondo de Pensión Voluntaria (Beneficio Tributario)",
            "tipo": "Optimización Tributaria / Vivienda",
            "monto_minimo_cop": 50_000.0,
            "tasa_ea_esperada": 0.095,
            "volatilidad_anual": 0.020,
            "comision_admin_anual": 0.015,
            "comision_fija_transaccion_cop": 0.0,
            "retefuente_pct": 0.0,
            "cubierto_fogafin": False,
            "perfil_minimo": "Moderado",
        },
        {
            "id": "fic_balanceado_global",
            "nombre": "FIC Balanceado / Deuda Corporativa y Multiactivo",
            "tipo": "FIC Moderado",
            "monto_minimo_cop": 50_000.0,
            "tasa_ea_esperada": 0.122,
            "volatilidad_anual": 0.065,
            "comision_admin_anual": 0.018,
            "comision_fija_transaccion_cop": 0.0,
            "retefuente_pct": 0.04,
            "cubierto_fogafin": False,
            "perfil_minimo": "Moderado",
        },
        {
            "id": "acciones_etf_bvc_mgc",
            "nombre": "Acciones y ETFs en BVC / Mercado Global Colombiano (Art. 36-1 E.T.)",
            "tipo": "Renta Variable",
            "monto_minimo_cop": 50_000.0,
            "tasa_ea_esperada": 0.148,
            "volatilidad_anual": 0.160,
            "comision_admin_anual": 0.005,
            "comision_fija_transaccion_cop": 14_875.0,
            "retefuente_pct": 0.0,
            "cubierto_fogafin": False,
            "perfil_minimo": "Agresivo",
        },
    ],
    "perfil_semilla_taller": {
        "usuario_id": "usr_oed_demo_001",
        "nombre_alias": "Participante Taller OED",
        "modalidad_laboral": "Empleado",
        "ingreso_bruto_mensual_cop": 6_500_000.0,
        "gastos_fijos_vitales_cop": 2_800_000.0,
        "gastos_variables_estilo_vida_cop": 950_000.0,
        "gastos_hormiga_mensual_cop": 320_000.0,
        "liquidez_actual_fondo_emergencia_cop": 6_000_000.0,
        "perfil_riesgo": "Moderado",
    },
}


def cargar_configuracion(ruta_config: str | Path | None = None) -> Dict[str, Any]:
    """Carga config/config.yaml o retorna la configuración base por defecto si no está disponible."""
    if ruta_config is None:
        ruta_config = Path(__file__).resolve().parent.parent / "config" / "config.yaml"
    else:
        ruta_config = Path(ruta_config)

    if ruta_config.exists():
        try:
            import yaml  # type: ignore

            with open(ruta_config, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
    return json.loads(json.dumps(DEFAULT_CONFIG))


# ==============================================================================
# 1. CONVERSIÓN RIGUROSA DE TASAS DE INTERÉS (ESTÁNDAR SFC COLOMBIA)
# ==============================================================================


def ea_a_em(tasa_ea: float) -> float:
    """
    Convierte una tasa Efectiva Anual (EA) a Efectiva Mensual (EM) usando interés compuesto:
    i_EM = (1 + i_EA)^(1/12) - 1.
    En Colombia NUNCA se divide la tasa EA entre 12.
    """
    if tasa_ea <= -1.0:
        raise ValueError("La tasa Efectiva Anual (EA) debe ser mayor a -100%.")
    return (1.0 + tasa_ea) ** (1.0 / 12.0) - 1.0


def em_a_ea(tasa_em: float) -> float:
    """Convierte una tasa Efectiva Mensual (EM) a Efectiva Anual (EA): i_EA = (1 + i_EM)^12 - 1."""
    if tasa_em <= -1.0:
        raise ValueError("La tasa Efectiva Mensual (EM) debe ser mayor a -100%.")
    return (1.0 + tasa_em) ** 12.0 - 1.0


def nmv_a_ea(tasa_nmv: float) -> float:
    """Convierte una tasa Nominal Mes Vencido (NMV) a Efectiva Anual (EA)."""
    tasa_em = tasa_nmv / 12.0
    return em_a_ea(tasa_em)


def ea_a_nmv(tasa_ea: float) -> float:
    """Convierte una tasa Efectiva Anual (EA) a Nominal Mes Vencido (NMV)."""
    return 12.0 * ea_a_em(tasa_ea)


def calcular_tasa_real_neta(
    tasa_ea_bruta: float,
    inflacion_anual_ipc: float = 0.052,
    retefuente_pct: float = 0.04,
    comision_admin_anual: float = 0.0,
) -> float:
    """
    Calcula la rentabilidad efectiva anual REAL y NETA de impuestos y comisiones en Colombia:
    1. Descuenta retención en la fuente sobre rendimientos y comisión de administración.
    2. Deflacta por la inflación (IPC DANE) usando la ecuación de Fisher exacta:
       i_real = (1 + i_neta) / (1 + IPC) - 1.
    """
    tasa_neta_impuestos = max(0.0, tasa_ea_bruta * (1.0 - retefuente_pct)) - comision_admin_anual
    return (1.0 + tasa_neta_impuestos) / (1.0 + inflacion_anual_ipc) - 1.0


def validar_usura_sfc(tasa_ea: float, tasa_usura_vigente_ea: float = 0.2650) -> Dict[str, Any]:
    """
    Verifica si una tasa de interés supera el límite legal de Usura certificado por la
    Superintendencia Financiera de Colombia (Art. 884 Código de Comercio / Art. 305 Código Penal).
    """
    excede_usura = tasa_ea > (tasa_usura_vigente_ea + 1e-6)
    exceso_puntos_basicos = max(0.0, (tasa_ea - tasa_usura_vigente_ea) * 10_000.0)
    return {
        "tasa_ea_evaluada": round(tasa_ea, 6),
        "tasa_usura_sfc_ea": round(tasa_usura_vigente_ea, 6),
        "excede_usura": excede_usura,
        "exceso_puntos_basicos": round(exceso_puntos_basicos, 1),
        "mensaje_legal": (
            "ALERTA LEGAL SFC: La tasa supera el límite de usura vigente en Colombia."
            if excede_usura
            else "Cumple con el límite legal de tasas en Colombia (SFC)."
        ),
    }


# ==============================================================================
# 2. UNIDADES REGULATORIAS COLOMBIANAS (UVT, UVR, SMMLV, 4x1000)
# ==============================================================================


def cop_a_uvt(monto_cop: float, valor_uvt_cop: float = 49_799.0) -> float:
    """Convierte Pesos Colombianos (COP) a Unidades de Valor Tributario (UVT - DIAN)."""
    return monto_cop / valor_uvt_cop


def uvt_a_cop(monto_uvt: float, valor_uvt_cop: float = 49_799.0) -> float:
    """Convierte Unidades de Valor Tributario (UVT) a Pesos Colombianos (COP)."""
    return monto_uvt * valor_uvt_cop


def calcular_gmf_4x1000(
    monto_retiro_mensual_cop: float,
    cuenta_exenta_marcada: bool = True,
    valor_uvt_cop: float = 49_799.0,
) -> float:
    """
    Calcula el Gravamen a los Movimientos Financieros (GMF - 4x1000).
    En Colombia las cuentas marcadas están exentas hasta 350 UVT mensuales.
    """
    if cuenta_exenta_marcada:
        tope_exento_cop = 350.0 * valor_uvt_cop
        base_gravable = max(0.0, monto_retiro_mensual_cop - tope_exento_cop)
    else:
        base_gravable = max(0.0, monto_retiro_mensual_cop)
    return base_gravable * 0.004


# ==============================================================================
# 3. VALOR FUTURO, VPN, TIR Y AMORTIZACIÓN (PESOS Y UVR)
# ==============================================================================


def valor_futuro_aportes_periodicos(
    aporte_mensual_cop: float,
    tasa_ea: float,
    meses: int,
    capital_inicial_cop: float = 0.0,
    crecimiento_anual_aporte_ipc: float = 0.0,
) -> Dict[str, Any]:
    """
    Calcula la evolución mes a mes de un plan de ahorro/inversión salarial con interés compuesto.
    Permite indexar el aporte mensual cada 12 meses con el IPC (protección del poder adquisitivo).
    """
    tasa_em = ea_a_em(tasa_ea)
    saldo = float(capital_inicial_cop)
    capital_aportado = float(capital_inicial_cop)
    aporte_actual = float(aporte_mensual_cop)
    historial: List[Dict[str, float]] = []

    for mes in range(1, meses + 1):
        if mes > 1 and (mes - 1) % 12 == 0 and crecimiento_anual_aporte_ipc > 0:
            aporte_actual *= 1.0 + crecimiento_anual_aporte_ipc

        interes_mes = saldo * tasa_em
        saldo += interes_mes + aporte_actual
        capital_aportado += aporte_actual
        historial.append(
            {
                "mes": float(mes),
                "aporte_mes_cop": round(aporte_actual, 2),
                "interes_mes_cop": round(interes_mes, 2),
                "capital_acumulado_cop": round(capital_aportado, 2),
                "saldo_final_cop": round(saldo, 2),
            }
        )

    return {
        "capital_total_aportado_cop": round(capital_aportado, 2),
        "intereses_compuestos_ganados_cop": round(saldo - capital_aportado, 2),
        "valor_futuro_nominal_cop": round(saldo, 2),
        "tasa_em_aplicada": round(tasa_em, 6),
        "historial_mensual": historial,
    }


def cuota_fija_francesa(saldo_capital_cop: float, tasa_em: float, plazo_meses: int) -> float:
    """Calcula la cuota fija mensual (sistema francés) dado el capital, tasa efectiva mensual y plazo."""
    if plazo_meses <= 0 or saldo_capital_cop <= 0:
        return 0.0
    if abs(tasa_em) < 1e-9:
        return saldo_capital_cop / plazo_meses
    factor = (1.0 + tasa_em) ** plazo_meses
    return saldo_capital_cop * (tasa_em * factor) / (factor - 1.0)


def calcular_vpn(tasa_descuento_periodica: float, flujos_caja: List[float]) -> float:
    """
    Calcula el Valor Presente Neto (VPN) de una serie de flujos de caja [FC_0, FC_1, ..., FC_n].
    FC_0 suele ser negativo (inversión inicial).
    """
    return sum(fc / ((1.0 + tasa_descuento_periodica) ** t) for t, fc in enumerate(flujos_caja))


def calcular_tir(flujos_caja: List[float], precision: float = 1e-6) -> float:
    """
    Calcula la Tasa Interna de Retorno (TIR) periódica mediante bisección robusta en [-0.95, 5.0].
    """
    if not flujos_caja or not (any(f < 0 for f in flujos_caja) and any(f > 0 for f in flujos_caja)):
        return 0.0

    low, high = -0.90, 5.0
    vpn_low = calcular_vpn(low, flujos_caja)
    for _ in range(120):
        mid = (low + high) / 2.0
        vpn_mid = calcular_vpn(mid, flujos_caja)
        if abs(vpn_mid) < precision:
            return mid
        if vpn_low * vpn_mid < 0:
            high = mid
        else:
            low = mid
            vpn_low = vpn_mid
    return (low + high) / 2.0
