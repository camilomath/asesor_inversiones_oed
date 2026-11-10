"""
MÓDULO 6: Educación Financiera Interactiva, Psicología del Riesgo y Probabilidad Aplicada.
Responsable OED: Salin Avellaneda (Matemático - Líder de Rifas, Juegos y Espectáculos).

Implementa:
- Perfilador Regulatorio de Riesgo del Inversionista (Decreto 2555 de 2010 - SFC) con detector
  de inconsistencia conductual (Suitability).
- Laboratorio Matemático "Azar vs. Inversión Compuesta": Cálculo de probabilidad combinatoria exacta
  y Valor Esperado (E[X] < 0) de loterías/Baloto, chance de 4 cifras y apuestas frente a la esperanza
  matemática positiva del interés compuesto en vehículos vigilados por la SFC.
- Detector Matemático de Esquemas Ponzi / Pirámides (Art. 316 del Código Penal - Captación Masiva y Habitual)
  mediante progresión geométrica hasta agotar la población adulta de Colombia.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List

from src.finance import valor_futuro_aportes_periodicos


POBLACION_ADULTA_COLOMBIA = 39_500_000


def perfilar_inversionista_decreto_2555(
    horizonte_anios: int,
    tolerancia_caida_pct: float,
    estabilidad_ingresos_1_a_5: int,
    experiencia_financiera_1_a_5: int,
    objetivo_alta_rentabilidad: bool = False,
) -> Dict[str, Any]:
    """
    Determina el perfil de riesgo del inversionista según el deber de idoneidad (Suitability)
    del Decreto 2555 de 2010 en Colombia ('Conservador', 'Moderado' o 'Agresivo').
    """
    puntaje = 0.0
    puntaje += min(30.0, max(0.0, horizonte_anios * 3.5))
    puntaje += min(35.0, max(0.0, tolerancia_caida_pct * 1.5))
    puntaje += min(20.0, max(4.0, estabilidad_ingresos_1_a_5 * 4.0))
    puntaje += min(15.0, max(3.0, experiencia_financiera_1_a_5 * 3.0))

    alerta_conductual = None
    if tolerancia_caida_pct < 5.0 and objetivo_alta_rentabilidad:
        alerta_conductual = (
            "Inconsistencia Conductual Detectada (Decreto 2555 de 2010): Usted desea alta rentabilidad bursátil "
            "pero declara no tolerar fluctuaciones temporales del 5%. Por protección al consumidor financiero, "
            "su perfil se ajusta preventivamente."
        )
        puntaje = min(puntaje, 52.0)

    if puntaje < 45.0:
        perfil = "Conservador"
    elif puntaje < 72.0:
        perfil = "Moderado"
    else:
        perfil = "Agresivo"

    return {
        "perfil_riesgo": perfil,
        "puntaje_idoneidad_100": round(puntaje, 1),
        "alerta_conductual_suitability": alerta_conductual,
    }


def comparar_azar_vs_inversion_compuesta(
    gasto_mensual_juegos_azar_cop: float,
    horizonte_anios: int = 10,
    tasa_ea_inversion_regulada: float = 0.11,
) -> Dict[str, Any]:
    """
    Compara matemáticamente el Valor Esperado E[X] de destinar un monto mensual a juegos de suerte y azar
    (Baloto / Lotería / Chance / Apuestas) frente a invertir ese mismo flujo con interés compuesto.
    """
    meses = horizonte_anios * 12
    gasto_total_acumulado = gasto_mensual_juegos_azar_cop * meses

    # Probabilidades combinatorias exactas en Colombia
    combinaciones_baloto = math.comb(43, 5) * 16  # 15,401,568 combinaciones
    prob_baloto = 1.0 / combinaciones_baloto
    prob_chance_4_cifras = 1.0 / 10_000.0

    # En juegos de azar regulados el retorno teórico al público (RTP / Payout neto de impuestos de ganadores)
    # oscila entre el 40% y el 55% en loterías/chance (Esperanza matemática neta negativa por cada peso apostado)
    retorno_esperado_azar_pct = 0.48
    valor_esperado_acumulado_azar = gasto_total_acumulado * retorno_esperado_azar_pct
    perdida_esperada_neta_azar = gasto_total_acumulado - valor_esperado_acumulado_azar

    proyeccion_inversion = valor_futuro_aportes_periodicos(
        aporte_mensual_cop=gasto_mensual_juegos_azar_cop,
        tasa_ea=tasa_ea_inversion_regulada,
        meses=meses,
    )

    diferencia_patrimonial = proyeccion_inversion["valor_futuro_nominal_cop"] - valor_esperado_acumulado_azar

    return {
        "gasto_mensual_evaluado_cop": round(gasto_mensual_juegos_azar_cop, 2),
        "horizonte_anios": horizonte_anios,
        "total_desembolsado_cop": round(gasto_total_acumulado, 2),
        "probabilidad_combinatoria_baloto": f"1 en {combinaciones_baloto:,} ({prob_baloto:.8%})",
        "probabilidad_chance_4_cifras": f"1 en 10,000 ({prob_chance_4_cifras:.4%})",
        "valor_esperado_azar_cop": round(valor_esperado_acumulado_azar, 2),
        "perdida_matematica_esperada_azar_cop": round(perdida_esperada_neta_azar, 2),
        "patrimonio_inversion_compuesta_cop": proyeccion_inversion["valor_futuro_nominal_cop"],
        "ganancia_intereses_compuestos_cop": proyeccion_inversion["intereses_compuestos_ganados_cop"],
        "brecha_riqueza_inversion_vs_azar_cop": round(diferencia_patrimonial, 2),
        "mensaje_pedagogico": (
            "Los juegos de suerte y azar tienen Esperanza Matemática Negativa (E[X] - Costo < 0) y deben "
            "asumirse únicamente como recreación con presupuesto controlado, jamás como inversión."
        ),
    }


def detectar_esquema_piramidal_ponzi(
    rentabilidad_mensual_prometida_pct: float,
    personas_reclutadas_por_ciclo: int = 3,
    tasa_usura_sfc_ea: float = 0.2650,
) -> Dict[str, Any]:
    """
    Evalúa matemáticamente una promesa de inversión "garantizada" para detectar esquemas Ponzi o
    captación masiva y habitual no autorizada (Art. 316 del Código Penal Colombiano).
    """
    tasa_em = rentabilidad_mensual_prometida_pct / 100.0
    tasa_ea_equivalente = (1.0 + tasa_em) ** 12.0 - 1.0
    r = max(2, int(personas_reclutadas_por_ciclo))

    ciclos_hasta_colapso_colombia = math.ceil(math.log(POBLACION_ADULTA_COLOMBIA, r))
    progresion_ciclos: List[Dict[str, int]] = [
        {"nivel_piramide": k, "personas_requeridas": r**k}
        for k in range(1, min(ciclos_hasta_colapso_colombia + 1, 18))
    ]

    alerta_piramide = tasa_ea_equivalente > tasa_usura_sfc_ea
    return {
        "tasa_mensual_prometida_pct": round(rentabilidad_mensual_prometida_pct, 2),
        "tasa_ea_equivalente_pct": round(tasa_ea_equivalente * 100.0, 2),
        "alerta_piramide": alerta_piramide,
        "ciclos_para_agotar_poblacion_colombia": ciclos_hasta_colapso_colombia,
        "progresion_geometrica": progresion_ciclos,
        "advertencia_legal_sfc": (
            "ALERTA ROJA (Art. 316 Código Penal Colombiano - Captación Ilegal / Esquema Ponzi): "
            f"Una promesa fija del {rentabilidad_mensual_prometida_pct:.1f}% mensual equivale al "
            f"{tasa_ea_equivalente * 100:,.1f}% Efectivo Anual, superando la tasa de mercado y la usura. "
            f"Con factor de reclutamiento {r}, en solo {ciclos_hasta_colapso_colombia} niveles supera la "
            "población adulta de Colombia y colapsa matemáticamente."
            if alerta_piramide
            else "La tasa se encuentra dentro de rangos financieros normales; verifique siempre que la entidad esté vigilada por la SFC."
        ),
    }
