"""
MÓDULO 2: Inversiones de Bajo Monto con el Salario y Estrategia de Portafolio.
Responsable OED: Camilo Matson (Matemático - Líder de Estrategia).

Implementa:
- Asignación estratégica de portafolio (Asset Allocation) según el perfil de riesgo del Decreto 2555 de 2010
  ('Conservador', 'Moderado', 'Agresivo') para excedentes salariales desde $10.000 COP.
- Cálculo de rentabilidad efectiva real neta (descontando retención en la fuente 4%/7%, comisión e inflación IPC).
- Verificación de eficiencia por costos de transacción fijos en compra de acciones/ETFs en BVC.
- Verificación de límite de cobertura del Seguro de Depósitos Fogafín ($50.000.000 COP por entidad).
- Simulación de proyección patrimonial en 3 escenarios estocásticos (P10 Pesimista, P50 Esperado, P90 Optimista).
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.finance import (
    calcular_tasa_real_neta,
    cargar_configuracion,
    valor_futuro_aportes_periodicos,
)


PESOS_MODELO_POR_PERFIL: Dict[str, Dict[str, float]] = {
    "Conservador": {
        "neobanco_alto_rendimiento": 0.40,
        "cdt_digital_sfc": 0.35,
        "fic_renta_fija_liquidez": 0.25,
    },
    "Moderado": {
        "neobanco_alto_rendimiento": 0.20,
        "cdt_digital_sfc": 0.20,
        "cuenta_afc_vivienda": 0.25,
        "fic_balanceado_global": 0.35,
    },
    "Agresivo": {
        "neobanco_alto_rendimiento": 0.10,
        "cuenta_afc_vivienda": 0.20,
        "fic_balanceado_global": 0.30,
        "acciones_etf_bvc_mgc": 0.40,
    },
}


def estructurar_portafolio_salario(
    excedente_mensual_cop: float,
    perfil_riesgo: str = "Moderado",
    horizonte_meses: int = 60,
    capital_semilla_cop: float = 0.0,
    config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Ejecuta el Caso de Uso CU-02 (Módulo 2 - Camilo):
    Construye el portafolio óptimo de micro-inversión salarial en Colombia y proyecta el patrimonio
    nominal y real en escenarios P10, P50 y P90.
    """
    cfg = config or cargar_configuracion()
    macro = cfg["parametros_macro_colombia"]
    ipc_anual = float(macro["ipc_anual_dane"])
    tope_fogafin = float(macro["tope_fogafin_cop"])
    catalogo = {v["id"]: v for v in cfg["catalogo_vehiculos_inversion_colombia"]}

    perfil_norm = perfil_riesgo.strip().capitalize()
    if perfil_norm not in PESOS_MODELO_POR_PERFIL:
        perfil_norm = "Moderado"

    if excedente_mensual_cop <= 0:
        return {
            "viable_invertir": False,
            "perfil_riesgo": perfil_norm,
            "mensaje": "No hay excedente mensual positivo para invertir. Priorice el Módulo 1 (Presupuesto) y Módulo 3 (Deudas).",
            "asignacion_portafolio": [],
        }

    pesos_objetivo = dict(PESOS_MODELO_POR_PERFIL[perfil_norm])
    alertas_estrategia: List[str] = []

    # Regla matemática de eficiencia en costos de transacción (Acciones BVC)
    if "acciones_etf_bvc_mgc" in pesos_objetivo:
        aporte_bvc = excedente_mensual_cop * pesos_objetivo["acciones_etf_bvc_mgc"]
        comision_fija = float(catalogo["acciones_etf_bvc_mgc"]["comision_fija_transaccion_cop"])
        if comision_fija > 0 and (comision_fija / max(1.0, aporte_bvc)) > 0.015:
            alertas_estrategia.append(
                f"Alerta de Eficiencia por Comisión Bursátil: Con un aporte mensual a BVC de ${aporte_bvc:,.0f} COP, "
                f"la comisión fija (${comision_fija:,.0f} COP) consume más del 1.5%. Se redirige automáticamente "
                "al FIC Balanceado sin comisión de entrada (acumular para compras trimestrales/semestrales)."
            )
            pesos_objetivo["fic_balanceado_global"] = (
                pesos_objetivo.get("fic_balanceado_global", 0.0) + pesos_objetivo.pop("acciones_etf_bvc_mgc")
            )

    asignacion: List[Dict[str, Any]] = []
    tasa_ea_ponderada_bruta = 0.0
    tasa_real_neta_ponderada = 0.0
    volatilidad_ponderada = 0.0

    for vehiculo_id, peso in pesos_objetivo.items():
        v = catalogo[vehiculo_id]
        monto_mensual = excedente_mensual_cop * peso
        tasa_real_v = calcular_tasa_real_neta(
            tasa_ea_bruta=float(v["tasa_ea_esperada"]),
            inflacion_anual_ipc=ipc_anual,
            retefuente_pct=float(v["retefuente_pct"]),
            comision_admin_anual=float(v["comision_admin_anual"]),
        )
        tasa_ea_ponderada_bruta += peso * float(v["tasa_ea_esperada"])
        tasa_real_neta_ponderada += peso * tasa_real_v
        volatilidad_ponderada += peso * float(v["volatilidad_anual"])

        asignacion.append(
            {
                "id": vehiculo_id,
                "nombre": v["nombre"],
                "peso_pct": round(peso * 100.0, 2),
                "aporte_mensual_cop": round(monto_mensual, 2),
                "tasa_ea_bruta_pct": round(float(v["tasa_ea_esperada"]) * 100.0, 2),
                "tasa_real_neta_ea_pct": round(tasa_real_v * 100.0, 2),
                "cubierto_fogafin": bool(v["cubierto_fogafin"]),
            }
        )

    proyeccion_nominal_p50 = valor_futuro_aportes_periodicos(
        aporte_mensual_cop=excedente_mensual_cop,
        tasa_ea=tasa_ea_ponderada_bruta,
        meses=horizonte_meses,
        capital_inicial_cop=capital_semilla_cop,
    )
    proyeccion_real_p50 = valor_futuro_aportes_periodicos(
        aporte_mensual_cop=excedente_mensual_cop,
        tasa_ea=tasa_real_neta_ponderada,
        meses=horizonte_meses,
        capital_inicial_cop=capital_semilla_cop,
    )
    proyeccion_real_p10 = valor_futuro_aportes_periodicos(
        aporte_mensual_cop=excedente_mensual_cop,
        tasa_ea=max(-0.05, tasa_real_neta_ponderada - 1.28 * volatilidad_ponderada),
        meses=horizonte_meses,
        capital_inicial_cop=capital_semilla_cop,
    )
    proyeccion_real_p90 = valor_futuro_aportes_periodicos(
        aporte_mensual_cop=excedente_mensual_cop,
        tasa_ea=tasa_real_neta_ponderada + 1.28 * volatilidad_ponderada,
        meses=horizonte_meses,
        capital_inicial_cop=capital_semilla_cop,
    )

    if proyeccion_nominal_p50["valor_futuro_nominal_cop"] > tope_fogafin:
        alertas_estrategia.append(
            f"Alerta Fogafín: El patrimonio proyectado supera ${tope_fogafin:,.0f} COP. Diversifique entre "
            "dos o más entidades vigiladas por la SFC para mantener el 100% cubierto por el seguro de depósito."
        )

    return {
        "viable_invertir": True,
        "perfil_riesgo": perfil_norm,
        "horizonte_meses": horizonte_meses,
        "aporte_mensual_total_cop": round(excedente_mensual_cop, 2),
        "tasa_ea_bruta_portafolio_pct": round(tasa_ea_ponderada_bruta * 100.0, 2),
        "tasa_real_neta_portafolio_pct": round(tasa_real_neta_ponderada * 100.0, 2),
        "capital_total_aportado_cop": proyeccion_nominal_p50["capital_total_aportado_cop"],
        "patrimonio_proyectado_nominal_cop": proyeccion_nominal_p50["valor_futuro_nominal_cop"],
        "patrimonio_proyectado_real_cop": proyeccion_real_p50["valor_futuro_nominal_cop"],
        "bandas_confianza_real_cop": {
            "pesimista_p10_cop": proyeccion_real_p10["valor_futuro_nominal_cop"],
            "esperado_p50_cop": proyeccion_real_p50["valor_futuro_nominal_cop"],
            "optimista_p90_cop": proyeccion_real_p90["valor_futuro_nominal_cop"],
        },
        "asignacion_portafolio": asignacion,
        "alertas_estrategia": alertas_estrategia,
        "historial_mensual_nominal": proyeccion_nominal_p50["historial_mensual"],
    }
