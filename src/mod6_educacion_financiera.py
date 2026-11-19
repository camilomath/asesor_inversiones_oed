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
POBLACION_MUNDIAL = 8_050_000_000

# Catálogo oficial de las 8 preguntas cuantitativas y conductuales del Decreto 2555 de 2010
CUESTIONARIO_SUITABILITY_SFC = [
    {
        "id": "p1_horizonte",
        "pregunta": "¿Por cuánto tiempo planea mantener sus recursos invertidos antes de necesitarlos?",
        "tipo": "horizonte",
        "opciones": [
            {"texto": "Menos de 1 año (Corto plazo / Necesito liquidez inmediata)", "puntaje": 5, "horizonte_anios": 0.5},
            {"texto": "Entre 1 y 3 años (Mediano plazo)", "puntaje": 15, "horizonte_anios": 2.0},
            {"texto": "Entre 3 y 5 años (Mediano-largo plazo)", "puntaje": 25, "horizonte_anios": 4.0},
            {"texto": "Más de 5 años (Largo plazo / Pensión o patrimonio)", "puntaje": 35, "horizonte_anios": 7.0},
        ],
    },
    {
        "id": "p2_reaccion_caida",
        "pregunta": "Si su inversión experimenta una caída temporal del 10% en un mes debido a volatilidad de mercado, ¿qué haría?",
        "tipo": "conductual_riesgo",
        "opciones": [
            {"texto": "Entro en pánico, retiro todo inmediatamente y asumo la pérdida", "puntaje": 5, "tolerancia_pct": 0.0},
            {"texto": "Me angustio y llamo a consultar, pero espero un mes antes de retirar", "puntaje": 12, "tolerancia_pct": 5.0},
            {"texto": "Mantengo la calma, entiendo que es volatilidad de mediano plazo", "puntaje": 22, "tolerancia_pct": 12.0},
            {"texto": "Aprovecho los precios bajos y compro más unidades para promediar", "puntaje": 30, "tolerancia_pct": 25.0},
        ],
    },
    {
        "id": "p3_objetivo_inversion",
        "pregunta": "¿Cuál es su objetivo financiero primordial con este capital?",
        "tipo": "objetivo",
        "opciones": [
            {"texto": "Preservar el capital nominal a toda costa, sin importar que gane menos que la inflación", "puntaje": 5, "alta_rentabilidad": False},
            {"texto": "Proteger el poder adquisitivo ganándole levemente a la inflación (IPC) con bajo riesgo", "puntaje": 15, "alta_rentabilidad": False},
            {"texto": "Crecimiento patrimonial balanceado aceptando fluctuaciones moderadas", "puntaje": 25, "alta_rentabilidad": True},
            {"texto": "Maximizar rentabilidad y multiplicar capital asumiendo riesgo significativo", "puntaje": 35, "alta_rentabilidad": True},
        ],
    },
    {
        "id": "p4_conocimiento_financiero",
        "pregunta": "¿Cuál es su nivel de experiencia y conocimiento sobre productos financieros colombianos?",
        "tipo": "conocimiento",
        "opciones": [
            {"texto": "Bajo: Solo conozco cuentas de ahorros tradicionales y efectivo", "puntaje": 5, "nivel": 1},
            {"texto": "Básico: Conozco CDTs y bolsillos remunerados de neobancos", "puntaje": 10, "nivel": 2},
            {"texto": "Intermedio: He invertido en Fondos de Inversión Colectiva (FICs) y Cuentas AFC", "puntaje": 18, "nivel": 3},
            {"texto": "Avanzado: Conozco acciones en BVC, ETFs, derivados o renta fija UVR", "puntaje": 25, "nivel": 5},
        ],
    },
    {
        "id": "p5_dependencia_ingresos",
        "pregunta": "¿Qué porcentaje de su sustento mensual depende de los rendimientos de este dinero?",
        "tipo": "estabilidad",
        "opciones": [
            {"texto": "Totalmente: Si pierdo rendimientos no puedo pagar mis gastos básicos", "puntaje": 2, "estabilidad": 1},
            {"texto": "Parcialmente: Ayuda a complementar mis ingresos de subsistencia", "puntaje": 8, "estabilidad": 2},
            {"texto": "Poco: Tengo ingresos laborales estables que cubren el 100% de mis gastos", "puntaje": 16, "estabilidad": 4},
            {"texto": "Nada: Es excedente puro que no necesito para mi vida cotidiana", "puntaje": 20, "estabilidad": 5},
        ],
    },
    {
        "id": "p6_porcentaje_patrimonio",
        "pregunta": "¿Qué proporción representa este monto respecto a su patrimonio líquido total?",
        "tipo": "patrimonio",
        "opciones": [
            {"texto": "Más del 75% (Casi todo mi patrimonio acumulado)", "puntaje": 5},
            {"texto": "Entre el 40% y el 75% de mi patrimonio", "puntaje": 12},
            {"texto": "Entre el 15% y el 40% de mi patrimonio", "puntaje": 20},
            {"texto": "Menos del 15% (Es una fracción menor diversificada)", "puntaje": 25},
        ],
    },
    {
        "id": "p7_fondo_emergencia",
        "pregunta": "¿Tiene usted un fondo de emergencias separado en cuenta líquida?",
        "tipo": "reserva",
        "opciones": [
            {"texto": "No tengo fondo de emergencias", "puntaje": 3},
            {"texto": "Tengo menos de 1 mes de gastos fijos", "puntaje": 8},
            {"texto": "Tengo entre 2 y 3 meses de gastos fijos", "puntaje": 15},
            {"texto": "Tengo más de 6 meses de gastos fijos reservados", "puntaje": 20},
        ],
    },
    {
        "id": "p8_educacion_tributaria",
        "pregunta": "¿Conoce el impacto tributario de sus inversiones en Colombia (Retefuente, GMF 4x1000, Cuentas AFC)?",
        "tipo": "tributario",
        "opciones": [
            {"texto": "Desconozco completamente el tema tributario", "puntaje": 4},
            {"texto": "He escuchado del 4x1000 pero no sé cómo optimizarlo", "puntaje": 8},
            {"texto": "Conozco cómo me retienen en CDTs y qué cuentas puedo exentar", "puntaje": 14},
            {"texto": "Aprovecho activamente beneficios tributarios de FPV/AFC y componente inflacionario", "puntaje": 20},
        ],
    },
]


def obtener_cuestionario_suitability() -> List[Dict[str, Any]]:
    """Retorna las 8 preguntas oficiales del test de idoneidad según el Decreto 2555 de 2010."""
    return CUESTIONARIO_SUITABILITY_SFC


def evaluar_cuestionario_suitability_completo(respuestas_usuario: Dict[str, int]) -> Dict[str, Any]:
    """
    Evalúa las 8 respuestas seleccionadas (índice 0-3 por cada pregunta)
    y genera el diagnóstico de idoneidad completo con alertas conductuales.
    """
    puntaje_total = 0.0
    puntaje_maximo = sum(max(opt["puntaje"] for opt in p["opciones"]) for p in CUESTIONARIO_SUITABILITY_SFC)
    
    idx_p1 = respuestas_usuario.get("p1_horizonte", 0)
    idx_p2 = respuestas_usuario.get("p2_reaccion_caida", 0)
    idx_p3 = respuestas_usuario.get("p3_objetivo_inversion", 0)
    idx_p4 = respuestas_usuario.get("p4_conocimiento_financiero", 0)
    idx_p5 = respuestas_usuario.get("p5_dependencia_ingresos", 0)

    for preg in CUESTIONARIO_SUITABILITY_SFC:
        pid = preg["id"]
        opc_idx = min(len(preg["opciones"]) - 1, max(0, respuestas_usuario.get(pid, 0)))
        puntaje_total += preg["opciones"][opc_idx]["puntaje"]

    puntaje_normalizado_100 = round((puntaje_total / puntaje_maximo) * 100.0, 1)

    opt_p2 = CUESTIONARIO_SUITABILITY_SFC[1]["opciones"][min(3, idx_p2)]
    opt_p3 = CUESTIONARIO_SUITABILITY_SFC[2]["opciones"][min(3, idx_p3)]

    # Detección de inconsistencia conductual
    alerta_conductual = None
    if opt_p2["tolerancia_pct"] < 5.0 and opt_p3.get("alta_rentabilidad", False):
        alerta_conductual = (
            "Inconsistencia Conductual Detectada (Decreto 2555 de 2010): Usted declaró como objetivo maximizar rentabilidad "
            "o crecimiento alto, pero ante una fluctuación del mercado optaría por retirar de inmediato con pánico. "
            "Por mandato del Deber de Asesoría Financiera SFC, su perfil ha sido reclasificado preventivamente a Conservador/Moderado."
        )
        puntaje_normalizado_100 = min(puntaje_normalizado_100, 48.0)

    if puntaje_normalizado_100 < 45.0:
        perfil = "Conservador"
        distribucion_sugerida = {"renta_fija_liquida_pct": 70, "renta_fija_plazo_pct": 25, "renta_variable_pct": 5}
    elif puntaje_normalizado_100 < 72.0:
        perfil = "Moderado"
        distribucion_sugerida = {"renta_fija_liquida_pct": 40, "renta_fija_plazo_pct": 40, "renta_variable_pct": 20}
    else:
        perfil = "Agresivo"
        distribucion_sugerida = {"renta_fija_liquida_pct": 15, "renta_fija_plazo_pct": 35, "renta_variable_pct": 50}

    return {
        "perfil_riesgo": perfil,
        "puntaje_idoneidad_100": puntaje_normalizado_100,
        "alerta_conductual_suitability": alerta_conductual,
        "distribucion_activos_sugerida": distribucion_sugerida,
        "recomendacion_normativa": (
            f"Perfil asignado: {perfil}. Cumple con la Circular Básica Jurídica de la SFC y Decreto 2555 de 2010. "
            "Los recursos sugeridos deben dirigirse a entidades vigiladas por la Superintendencia Financiera."
        ),
    }


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
            "⚠️ Revisión preventiva de tu perfil (Decreto 2555 de 2010): Quieres buscar la mayor rentabilidad bursátil, "
            "pero declaras que no toleras variaciones temporales del 5%. Como tu Asesor Financiero de Confianza, calibramos "
            "preventivamente tu perfil a Moderado para cuidar tu tranquilidad y evitar que vendas con pérdidas ante cualquier ajuste de mercado."
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


def simular_trayectoria_mensual_azar_vs_inversion(
    monto_mensual_cop: float,
    anios: int = 10,
    tasa_ea_inversion: float = 0.11,
) -> List[Dict[str, Any]]:
    """
    Genera serie cronológica mes a mes (útil para graficación interactiva en Plotly) comparando:
    1. Capital acumulado aportado
    2. Valor Esperado acumulado de juegos de azar (E[X] < 0)
    3. Patrimonio acumulado con interés compuesto (vehículos vigilados SFC)
    """
    tasa_em = (1.0 + tasa_ea_inversion) ** (1.0 / 12.0) - 1.0
    retorno_esperado_azar_pct = 0.48

    serie: List[Dict[str, Any]] = []
    saldo_inversion = 0.0

    for mes in range(1, anios * 12 + 1):
        saldo_inversion = (saldo_inversion + monto_mensual_cop) * (1.0 + tasa_em)
        total_desembolsado = monto_mensual_cop * mes
        valor_esperado_azar = total_desembolsado * retorno_esperado_azar_pct

        if mes % 6 == 0 or mes == 1 or mes == anios * 12:
            serie.append({
                "mes": mes,
                "anio": round(mes / 12.0, 1),
                "total_aportado_cop": round(total_desembolsado, 2),
                "valor_esperado_azar_cop": round(valor_esperado_azar, 2),
                "patrimonio_inversion_cop": round(saldo_inversion, 2),
                "brecha_patrimonial_cop": round(saldo_inversion - valor_esperado_azar, 2),
            })

    return serie


TRIVIAS_EDUCACION_FINANCIERA_COLOMBIA = [
    {
        "id": "t1_interes_compuesto",
        "pregunta": "¿Por qué en Colombia una tasa del 1% Efectivo Mensual (EM) NO es igual a una tasa del 12% Efectivo Anual (EA)?",
        "opciones": [
            "Porque la Dian cobra una retención adicional del 2% al año",
            "Porque en interés compuesto, los intereses devengados cada mes generan nuevos intereses ( (1+0.01)^12 - 1 = 12.68% EA )",
            "Porque los bancos dividen entre 360 días en vez de 365 días",
            "Porque el 4x1000 disminuye la rentabilidad anual",
        ],
        "respuesta_correcta_idx": 1,
        "explicacion": "En Colombia la Circular Básica Jurídica de la SFC exige capitalización compuesta: (1 + 0.01)^12 - 1 = 12.68% EA, mayor al 12% nominal simple.",
    },
    {
        "id": "t2_ilusion_monetaria",
        "pregunta": "Si un CDT le ofrece 10% EA y la inflación del año (IPC DANE) es del 6%, ¿cuál es su rentabilidad real aproximada antes de impuestos?",
        "opciones": [
            "Aproximadamente 4% real ( (1+0.10)/(1+0.06) - 1 ≈ 3.77% real )",
            "16% real sumando ambas tasas",
            "10% real porque el capital nominal no disminuye",
            "0% porque la inflación anula cualquier inversión",
        ],
        "respuesta_correcta_idx": 0,
        "explicacion": "La rentabilidad real descuenta la pérdida de poder adquisitivo del IPC. La fórmula de Fisher en Colombia es: (1 + i) / (1 + IPC) - 1.",
    },
    {
        "id": "t3_fogafin",
        "pregunta": "¿Qué monto máximo asegura FOGAFÍN por depositante en una entidad bancaria vigilada en Colombia en caso de liquidación?",
        "opciones": [
            "$20.000.000 COP",
            "$50.000.000 COP",
            "$100.000.000 COP",
            "El 100% del saldo sin ningún límite",
        ],
        "respuesta_correcta_idx": 1,
        "explicacion": "El Seguro de Depósitos de Fogafín cubre automáticamente hasta $50.000.000 COP por persona y por entidad bancaria vigilada.",
    },
    {
        "id": "t4_gmf_exencion",
        "pregunta": "¿Hasta cuántas UVT mensuales está exenta del Gravamen a los Movimientos Financieros (4x1000) una cuenta de ahorros marcada en Colombia?",
        "opciones": [
            "Hasta 100 UVT",
            "Hasta 350 UVT mensuales",
            "No existe ninguna exención",
            "Hasta 1.000 UVT",
        ],
        "respuesta_correcta_idx": 1,
        "explicacion": "Según el Estatuto Tributario colombiano, una sola cuenta bancaria por persona puede marcarse exenta de 4x1000 hasta por 350 UVT mensuales.",
    },
]


def obtener_trivias_cultura_financiera() -> List[Dict[str, Any]]:
    """Retorna micro-cápsulas educativas y preguntas de cultura financiera colombiana."""
    return TRIVIAS_EDUCACION_FINANCIERA_COLOMBIA


# ==============================================================================
# CATÁLOGO DE ACTIVOS COLOMBIA: RENTA FIJA Y RENTA VARIABLE (ETFs / ACCIONES)
# ==============================================================================

CATALOGO_ACTIVOS_COLOMBIA = {
    "renta_fija": [
        {
            "id": "cdts_digitales",
            "categoria": "Renta Fija Plazo",
            "nombre": "CDTs Digitales y Cuentas Remuneradas",
            "ejemplos": "Nu, Pibank, Bancolombia, Davivienda, Banco Finandina",
            "tasa_ea_referencial_pct": 11.0,
            "horizonte_minimo_meses": 6,
            "riesgo": "Bajo (Vigilado SFC)",
            "seguro_deposito": "Fogafín hasta $50.000.000 COP por entidad bancaria",
            "fuente": "Superintendencia Financiera de Colombia (SFC) - Tasas Semanales de Captación CDT 360 días (Promedio sistema 10.2% - 11.5% EA)",
        },
        {
            "id": "fics_liquidez",
            "categoria": "Renta Fija Líquida",
            "nombre": "Fondos de Inversión Colectiva (FICs) a la Vista",
            "ejemplos": "Fiducuenta (Fiduciaria Bancolombia), Fiduciaria Davivienda, Tyba Liquidez",
            "tasa_ea_referencial_pct": 9.8,
            "horizonte_minimo_meses": 1,
            "riesgo": "Bajo - Muy Líquido (D+0 / D+1)",
            "seguro_deposito": "Patrimonio autónomo separado del balance de la fiduciaria",
            "fuente": "Boletín Diario de Fiduciarias - Superintendencia Financiera de Colombia (SFC)",
        },
        {
            "id": "tes_deuda_publica",
            "categoria": "Renta Fija Soberana",
            "nombre": "Títulos de Deuda Pública de Colombia (TES Tasa Fija y UVR)",
            "ejemplos": "TES COP Tasa Fija 2032/2034, TES UVR (protegidos contra inflación)",
            "tasa_ea_referencial_pct": 10.5,
            "horizonte_minimo_meses": 36,
            "riesgo": "Riesgo Soberano de la República de Colombia",
            "seguro_deposito": "Garantía de la Nación",
            "fuente": "Ministerio de Hacienda y Crédito Público / Banco de la República de Colombia",
        },
    ],
    "renta_variable": [
        {
            "id": "etfs_globales_sp500",
            "categoria": "ETFs Indexados Internacionales",
            "nombre": "ETFs Globales Indexados al S&P 500 (500 mayores empresas de EE.UU.)",
            "tickers": "CSPX (acumulación en USD/COP), VOO, IVV",
            "acceso_colombia": "Mercado Global Colombiano (MGC) de la BVC mediante Trii o Comisionistas locales",
            "tasa_ea_referencial_pct": 12.8,
            "volatilidad_anual_pct": 16.0,
            "riesgo": "Moderado-Alto (Renta Variable Bursátil)",
            "fuente": "S&P Dow Jones Indices / BVC - Rendimiento histórico anualizado compuesto S&P 500 (~10-11% USD + efecto cambiario TRM histórico largo plazo)",
        },
        {
            "id": "etfs_globales_diversificados",
            "categoria": "ETFs Globales Todo Mundo",
            "nombre": "ETFs Globales Diversificados (Mundo Desarrollado + Emergentes)",
            "tickers": "VT (Vanguard Total World Stock), EIMI (iShares Emerging Markets)",
            "acceso_colombia": "Brokers internacionales regulados / Mercado Global Colombiano BVC",
            "tasa_ea_referencial_pct": 11.5,
            "volatilidad_anual_pct": 15.0,
            "riesgo": "Alto (Diversificación mundial en más de 40 países)",
            "fuente": "Vanguard / BlackRock iShares / Índices MSCI All Country World Index (ACWI)",
        },
        {
            "id": "etf_local_hcolsel",
            "categoria": "ETFs Renta Variable Colombia",
            "nombre": "ETF HCOLSEL (Índice MSCI Colcap - 20 principales empresas de Colombia)",
            "tickers": "HCOLSEL (Bolsa de Valores de Colombia)",
            "acceso_colombia": "BVC directa a través de Trii, Valores Bancolombia, Corredores Davivienda",
            "tasa_ea_referencial_pct": 12.2,
            "dividend_yield_estimado_pct": 8.0,
            "volatilidad_anual_pct": 18.0,
            "riesgo": "Alto (Mercado bursátil emergente local)",
            "fuente": "Bolsa de Valores de Colombia (BVC) / MSCI Colcap Index (Alto dividendo recurrente en COP)",
        },
        {
            "id": "acciones_libres_colombia_exterior",
            "categoria": "Acciones Libres y Títulos Corporativos",
            "nombre": "Acciones Individuales Seleccionadas (Locales e Internacionales)",
            "tickers": "Bancolombia (PFBCOLOM), Ecopetrol, GEB, Nu Holdings (NU), Apple (AAPL), Microsoft (MSFT)",
            "acceso_colombia": "BVC / Mercado Global Colombiano / Trii / Hapi / eToro regulado",
            "tasa_ea_referencial_pct": 13.5,
            "volatilidad_anual_pct": 22.0,
            "riesgo": "Muy Alto (Riesgo específico no diversificado por empresa)",
            "fuente": "Bolsa de Valores de Colombia (BVC) / FactSet - Tasas históricas de crecimiento y dividendos",
        },
    ],
}


def simular_portafolio_realista_segun_perfil(
    perfil_riesgo: str = "Moderado",
    capacidad_inversion_mensual_cop: float = 1_000_000.0,
    capital_inicial_cop: float = 2_000_000.0,
    horizonte_anios: int = 10,
    gasto_recreativo_azar_cop: float = 50_000.0,
) -> Dict[str, Any]:
    """
    Construye un portafolio de inversión realista ajustado al Perfil de Riesgo y Capacidad Financiera,
    integrando Renta Fija (CDTs, FICs, TES) y Renta Variable (ETFs indexados y acciones libres),
    junto con el dimensionamiento del ocio/azar y recomendaciones normativas y de ejecución para Colombia.
    """
    perfil_norm = perfil_riesgo.capitalize()
    if perfil_norm not in ["Conservador", "Moderado", "Agresivo"]:
        perfil_norm = "Moderado"

    meses = max(12, int(horizonte_anios * 12))

    # Definición de pesos de asignación estratégica de activos (Asset Allocation)
    if perfil_norm == "Conservador":
        pesos = {
            "renta_fija_total_pct": 80.0,
            "renta_variable_total_pct": 20.0,
            "desglose": [
                {"activo": "CDTs Digitales (Nu/Pibank/Davivienda)", "clase": "Renta Fija Plazo", "pct": 45.0, "tasa_ea": 0.110},
                {"activo": "FICs Liquidez a la Vista (Fiducuenta)", "clase": "Renta Fija Líquida", "pct": 25.0, "tasa_ea": 0.098},
                {"activo": "Bonos TES Colombia Tasa Fija / UVR", "clase": "Renta Fija Soberana", "pct": 10.0, "tasa_ea": 0.105},
                {"activo": "ETFs S&P 500 (CSPX / VOO)", "clase": "ETFs Renta Variable Global", "pct": 15.0, "tasa_ea": 0.128},
                {"activo": "ETF Local HCOLSEL (MSCI Colcap)", "clase": "ETFs Acciones Colombia", "pct": 5.0, "tasa_ea": 0.122},
            ],
        }
    elif perfil_norm == "Moderado":
        pesos = {
            "renta_fija_total_pct": 55.0,
            "renta_variable_total_pct": 45.0,
            "desglose": [
                {"activo": "CDTs Digitales (Nu/Pibank/Bancolombia)", "clase": "Renta Fija Plazo", "pct": 30.0, "tasa_ea": 0.110},
                {"activo": "FICs Liquidez a la Vista (Fiducuenta)", "clase": "Renta Fija Líquida", "pct": 15.0, "tasa_ea": 0.098},
                {"activo": "Bonos TES Colombia Tasa Fija / UVR", "clase": "Renta Fija Soberana", "pct": 10.0, "tasa_ea": 0.105},
                {"activo": "ETFs S&P 500 (CSPX / VOO en MGC)", "clase": "ETFs Renta Variable Global", "pct": 25.0, "tasa_ea": 0.128},
                {"activo": "ETF Global / Emergente (VT / EIMI)", "clase": "ETFs Globales", "pct": 10.0, "tasa_ea": 0.115},
                {"activo": "ETF Local HCOLSEL + Acciones Libres", "clase": "Acciones Libres / Local", "pct": 10.0, "tasa_ea": 0.128},
            ],
        }
    else:  # Agresivo
        pesos = {
            "renta_fija_total_pct": 25.0,
            "renta_variable_total_pct": 75.0,
            "desglose": [
                {"activo": "CDTs Digitales / FICs Liquidez", "clase": "Renta Fija Base", "pct": 15.0, "tasa_ea": 0.105},
                {"activo": "Bonos TES Colombia Tasa Fija / UVR", "clase": "Renta Fija Soberana", "pct": 10.0, "tasa_ea": 0.105},
                {"activo": "ETFs S&P 500 (CSPX / VOO)", "clase": "ETFs Renta Variable Global", "pct": 40.0, "tasa_ea": 0.128},
                {"activo": "ETFs Emergentes / Globales (VT / EIMI)", "clase": "ETFs Globales", "pct": 15.0, "tasa_ea": 0.115},
                {"activo": "Acciones Libres Seleccionadas (BVC / Tech)", "clase": "Acciones Libres", "pct": 20.0, "tasa_ea": 0.135},
            ],
        }

    # Tasa ponderada del portafolio
    tasa_ponderada_ea = sum((item["pct"] / 100.0) * item["tasa_ea"] for item in pesos["desglose"])

    # Proyección con aportes periódicos + capital inicial compuesto
    def proyectar_con_tasa(tasa_ea: float) -> Dict[str, float]:
        tasa_em = (1.0 + tasa_ea) ** (1.0 / 12.0) - 1.0
        vf_capital_inicial = capital_inicial_cop * ((1.0 + tasa_em) ** meses)
        if tasa_em > 0:
            vf_aportes = capacidad_inversion_mensual_cop * (((1.0 + tasa_em) ** meses - 1.0) / tasa_em)
        else:
            vf_aportes = capacidad_inversion_mensual_cop * meses
        total_aportado = capital_inicial_cop + (capacidad_inversion_mensual_cop * meses)
        patrimonio_final = vf_capital_inicial + vf_aportes
        intereses = patrimonio_final - total_aportado
        return {
            "patrimonio_final_cop": round(patrimonio_final, 2),
            "total_aportado_cop": round(total_aportado, 2),
            "intereses_ganados_cop": round(intereses, 2),
            "tasa_ea_pct": round(tasa_ea * 100.0, 2),
        }

    proy_esperada = proyectar_con_tasa(tasa_ponderada_ea)
    proy_pesimista = proyectar_con_tasa(max(0.06, tasa_ponderada_ea - 0.035))
    proy_optimista = proyectar_con_tasa(tasa_ponderada_ea + 0.035)

    # Detalle de distribución mensual en COP
    distribucion_mensual_detalle = []
    for item in pesos["desglose"]:
        monto_item_cop = round(capacidad_inversion_mensual_cop * (item["pct"] / 100.0), 2)
        distribucion_mensual_detalle.append({
            "activo": item["activo"],
            "clase": item["clase"],
            "porcentaje_pct": item["pct"],
            "monto_mensual_cop": monto_item_cop,
            "tasa_ea_esperada_pct": round(item["tasa_ea"] * 100.0, 1),
        })

    # Análisis del gasto recreativo en azar (costo de oportunidad vs realidad)
    total_disponible = capacidad_inversion_mensual_cop + gasto_recreativo_azar_cop
    pct_azar_sobre_ahorro = (gasto_recreativo_azar_cop / total_disponible * 100.0) if total_disponible > 0 else 0.0
    desembolso_azar_horizonte = gasto_recreativo_azar_cop * meses
    perdida_esperada_azar = desembolso_azar_horizonte * 0.52  # E[X] negativo ~52% de pérdida promedio

    # Recomendaciones finales de inversión profesional y estructurada
    recomendaciones_finales = [
        {
            "titulo": "1. Estrategia DCA (Dollar-Cost Averaging) Automática",
            "detalle": (
                f"Invierta sus ${capacidad_inversion_mensual_cop:,.0f} COP mensuales de manera automática y constante "
                "el mismo día de cada mes (ej. día de pago). Esto elimina el estrés de intentar adivinar los picos o valles "
                "del mercado ('market timing') y promedia favorablemente los precios de compra de los ETFs y acciones."
            ),
        },
        {
            "titulo": "2. Regla de Oro: Fondo de Emergencia Blindado en Renta Fija",
            "detalle": (
                "Antes de expandir su inversión en Renta Variable, asegure que la porción de FICs de Liquidez y Cuentas "
                "Remuneradas cubra entre 3 y 6 meses de sus gastos fijos indispensables. Esto evita que ante un imprevisto "
                "deba vender sus ETFs o acciones con pérdidas temporales."
            ),
        },
        {
            "titulo": "3. Vehículos e Infraestructura Regulada en Colombia",
            "detalle": (
                "• Renta Fija: Aproveche CDTs digitales y cuentas de neobancos vigilados con seguro FOGAFÍN (hasta $50M COP).\n"
                "• Renta Variable (ETFs y Acciones): Utilice comisionistas de bolsa vigiladas por la SFC como Trii o comisionistas "
                "tradicionales para acceder al Mercado Global Colombiano (MGC de la BVC), invirtiendo en ETFs como CSPX o VOO en pesos sin comisiones abusivas."
            ),
        },
        {
            "titulo": "4. Optimización Tributaria Colombiana (Estatuto Tributario)",
            "detalle": (
                "• Marque su cuenta principal de ahorro exenta del Gravamen a los Movimientos Financieros (4x1000) hasta 350 UVT/mes.\n"
                "• Si declara renta, evalúe aportes a Fondos de Pensiones Voluntarias (FPV) o Cuentas AFC para disminuir la base gravable "
                "(hasta el 30% del ingreso laboral, tope de 3.800 UVT según Art. 126-1 E.T.)."
            ),
        },
        {
            "titulo": "5. Rebalanceo Periódico de Portafolio",
            "detalle": (
                f"Cada 12 meses revise la proporción de su portafolio. Si la Renta Variable tuvo un año excelente y superó el "
                f"{pesos['renta_variable_total_pct']}% objetivo de su perfil {perfil_norm}, venda una fracción para consolidar ganancias "
                "en Renta Fija y mantener su nivel de riesgo calibrado."
            ),
        },
        {
            "titulo": "6. Presupuesto Realista de Ocio y Azar (Sin Fuga de Riqueza)",
            "detalle": (
                f"Usted destina ${gasto_recreativo_azar_cop:,.0f} COP/mes a azar/apuestas ({pct_azar_sobre_ahorro:.1f}% del flujo total). "
                "Nuestra recomendación realista no es prohibir el entretenimiento, sino catalogarlo estrictamente como 'Gasto de Ocio' "
                "(máximo 2% a 5% del presupuesto), asegurando que el 95% restante construya su libertad financiera con interés compuesto."
            ),
        },
    ]

    plan_de_accion_mes = (
        f"Destina este mismo mes ${round(capacidad_inversion_mensual_cop * (pesos['renta_fija_total_pct'] / 100.0)):,.0f} COP "
        f"a Renta Fija protegida por Fogafín (CDT digital o FIC de liquidez) y ${round(capacidad_inversion_mensual_cop * (pesos['renta_variable_total_pct'] / 100.0)):,.0f} COP "
        f"a ETFs indexados globales (S&P 500 vía MGC) programando una transferencia automática el día que recibes tu sueldo. "
        f"Mantén tu presupuesto de recreación/azar en un tope de ${round(gasto_recreativo_azar_cop):,.0f} COP/mes sin tocar tus ahorros."
    )

    diagnostico_asesor_confianza = {
        "nivel": "verde" if pct_azar_sobre_ahorro <= 10.0 else "ambar",
        "titulo_claro": f"Portafolio equilibrado para tu perfil {perfil_norm} ({pesos['renta_fija_total_pct']}% Renta Fija / {pesos['renta_variable_total_pct']}% Renta Variable)",
        "explicacion_humana": (
            f"Con tu capacidad de ahorro de ${capacidad_inversion_mensual_cop:,.0f} COP al mes y un capital inicial de ${capital_inicial_cop:,.0f} COP, "
            f"tu portafolio proyecta alcanzar en {horizonte_anios} años un patrimonio estimado de ${proy_esperada['patrimonio_final_cop']:,.0f} COP "
            f"(con ${proy_esperada['intereses_ganados_cop']:,.0f} COP generados puramente por interés compuesto a una tasa ponderada del {round(tasa_ponderada_ea*100, 2)}% EA)."
        ),
        "plan_accion_mes": plan_de_accion_mes,
    }

    return {
        "perfil_riesgo": perfil_norm,
        "horizonte_anios": horizonte_anios,
        "capacidad_inversion_mensual_cop": capacidad_inversion_mensual_cop,
        "capital_inicial_cop": capital_inicial_cop,
        "gasto_recreativo_azar_cop": gasto_recreativo_azar_cop,
        "diagnostico_asesor_confianza": diagnostico_asesor_confianza,
        "plan_de_accion_mes": plan_de_accion_mes,
        "asignacion_macro": {
            "renta_fija_pct": pesos["renta_fija_total_pct"],
            "renta_variable_pct": pesos["renta_variable_total_pct"],
            "monto_mensual_renta_fija_cop": round(capacidad_inversion_mensual_cop * (pesos["renta_fija_total_pct"] / 100.0), 2),
            "monto_mensual_renta_variable_cop": round(capacidad_inversion_mensual_cop * (pesos["renta_variable_total_pct"] / 100.0), 2),
        },
        "distribucion_mensual_detalle": distribucion_mensual_detalle,
        "tasa_ponderada_esperada_ea_pct": round(tasa_ponderada_ea * 100.0, 2),
        "proyeccion_escenarios": {
            "esperado": proy_esperada,
            "pesimista": proy_pesimista,
            "optimista": proy_optimista,
        },
        "analisis_recreativo_azar": {
            "gasto_mensual_azar_cop": gasto_recreativo_azar_cop,
            "porcentaje_sobre_flujo_pct": round(pct_azar_sobre_ahorro, 1),
            "desembolso_acumulado_azar_cop": round(desembolso_azar_horizonte, 2),
            "perdida_matematica_esperada_cop": round(perdida_esperada_azar, 2),
        },
        "catalogo_fuentes_referencia": CATALOGO_ACTIVOS_COLOMBIA,
        "recomendaciones_inversion": recomendaciones_finales,
    }


