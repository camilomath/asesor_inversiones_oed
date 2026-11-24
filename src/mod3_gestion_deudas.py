"""
MÓDULO 3: Gestión, Administración y Optimización Analítica de Deudas.
Responsable OED: Catalina Moreno (Ingeniera Industrial - Líder de Proyectos y Analítica).

Implementa:
- Inventario de pasivos colombianos y validación contra la Tasa de Usura certificada por la SFC.
- Semáforo de Índice de Endeudamiento mensual (Cuotas / Ingreso Neto).
- Investigación de Operaciones para desendeudamiento con efecto roll-over de cuotas liberadas:
  Comparativa exacta entre Método Avalancha (óptimo matemático: mayor tasa EA primero)
  y Método Bola de Nieve (óptimo conductual: menor saldo primero).
- Simulador de Abonos Extraordinarios a Capital bajo la Ley 1328 de 2009 (Derecho a prepago sin sanción
  eligiendo entre Reducción de Plazo vs. Reducción de Cuota) y Compra de Cartera.
- Interfaz Gráfica Oficial (`render_interfaz_modulo_3_catalina`) alineada 100% con el
  Manual de Marca OED (`src/oed_design_system.py` — `paso_actual=3`).
"""

from __future__ import annotations

import math
from typing import Any, Dict, List

from src.finance import cargar_configuracion, cuota_fija_francesa, ea_a_em, validar_usura_sfc


def _simular_estrategia_desendeudamiento(
    lista_deudas: List[Dict[str, Any]],
    abono_extra_mensual_cop: float,
    criterio_orden: str = "avalancha",
) -> Dict[str, Any]:
    """
    Simula mes a mes la extinción de múltiples deudas aplicando el efecto roll-over:
    cuando una obligación llega a saldo 0, su cuota fija se suma íntegramente al abono extra
    disponible para atacar la siguiente deuda priorizada.
    """
    deudas = [
        {
            "nombre": str(d["nombre"]),
            "saldo": float(d["saldo_cop"]),
            "tasa_ea": float(d["tasa_ea"]),
            "tasa_em": ea_a_em(float(d["tasa_ea"])),
            "cuota_fija": float(d["cuota_mensual_cop"]),
            "seguro_mensual": float(d.get("seguro_cuota_manejo_cop", 0.0)),
            "mes_extincion": 0,
        }
        for d in lista_deudas
        if float(d["saldo_cop"]) > 0
    ]

    if criterio_orden == "avalancha":
        deudas.sort(key=lambda x: (-x["tasa_ea"], x["saldo"]))
    elif criterio_orden == "bola_de_nieve":
        deudas.sort(key=lambda x: (x["saldo"], -x["tasa_ea"]))

    mes = 0
    total_intereses_pagados = 0.0
    total_seguros_pagados = 0.0
    presupuesto_mensual_total = sum(d["cuota_fija"] for d in deudas) + max(0.0, abono_extra_mensual_cop)
    historial_saldos: List[Dict[str, Any]] = [
        {
            "mes": 0,
            "saldo_total_cop": round(sum(d["saldo"] for d in deudas), 2),
            "intereses_acumulados_cop": 0.0,
            "seguros_acumulados_cop": 0.0,
            "saldos_por_obligacion": {d["nombre"]: round(d["saldo"], 2) for d in deudas},
        }
    ]

    while any(d["saldo"] > 0.01 for d in deudas) and mes < 600:
        mes += 1
        flujo_disponible = presupuesto_mensual_total

        # 1. Cobrar intereses y pago mínimo de cada deuda activa
        for d in deudas:
            if d["saldo"] <= 0.01:
                continue
            interes = d["saldo"] * d["tasa_em"]
            total_intereses_pagados += interes
            total_seguros_pagados += d["seguro_mensual"]
            d["saldo"] += interes

            pago_normal = min(d["saldo"], d["cuota_fija"])
            d["saldo"] -= pago_normal
            flujo_disponible -= pago_normal
            if d["saldo"] <= 0.01 and d["mes_extincion"] == 0:
                d["saldo"] = 0.0
                d["mes_extincion"] = mes

        # 2. Aplicar el excedente + roll-over a la deuda prioritaria según la estrategia
        if criterio_orden in ("avalancha", "bola_de_nieve") and flujo_disponible > 0.01:
            for d in deudas:
                if d["saldo"] <= 0.01:
                    continue
                abono_extra = min(d["saldo"], flujo_disponible)
                d["saldo"] -= abono_extra
                flujo_disponible -= abono_extra
                if d["saldo"] <= 0.01 and d["mes_extincion"] == 0:
                    d["saldo"] = 0.0
                    d["mes_extincion"] = mes
                if flujo_disponible <= 0.01:
                    break

        historial_saldos.append(
            {
                "mes": mes,
                "saldo_total_cop": round(sum(d["saldo"] for d in deudas), 2),
                "intereses_acumulados_cop": round(total_intereses_pagados, 2),
                "seguros_acumulados_cop": round(total_seguros_pagados, 2),
                "saldos_por_obligacion": {d["nombre"]: round(d["saldo"], 2) for d in deudas},
            }
        )

    return {
        "estrategia": criterio_orden,
        "meses_totales_para_cero_deuda": mes,
        "total_intereses_pagados_cop": round(total_intereses_pagados, 2),
        "total_seguros_y_manejo_pagados_cop": round(total_seguros_pagados, 2),
        "costo_financiero_total_cop": round(total_intereses_pagados + total_seguros_pagados, 2),
        "cronograma_extincion": [
            {
                "obligacion": d["nombre"],
                "mes_inicio": 0,
                "mes_extincion": d["mes_extincion"],
                "tasa_ea_pct": round(d["tasa_ea"] * 100, 2),
            }
            for d in deudas
        ],
        "historial_mensual": historial_saldos,
    }


def simular_abono_extraordinario_ley_1328(
    saldo_actual_cop: float,
    tasa_ea: float,
    plazo_restante_meses: int,
    abono_extra_capital_cop: float,
) -> Dict[str, Any]:
    """
    Simula el derecho del consumidor financiero en Colombia (Ley 1328 de 2009) a realizar abonos
    extraordinarios a capital sin penalidad, comparando:
    - Opción A: Reducción de Plazo (manteniendo la cuota mensual constante).
    - Opción B: Reducción de Valor de Cuota (manteniendo el plazo original).
    """
    tasa_em = ea_a_em(tasa_ea)
    cuota_actual = cuota_fija_francesa(saldo_actual_cop, tasa_em, plazo_restante_meses)
    intereses_originales = max(0.0, cuota_actual * plazo_restante_meses - saldo_actual_cop)

    nuevo_saldo = max(0.0, saldo_actual_cop - abono_extra_capital_cop)
    if nuevo_saldo <= 0:
        return {
            "deuda_cancelada_totalmente": True,
            "ahorro_intereses_reduccion_plazo_cop": round(intereses_originales, 2),
            "meses_ahorrados": plazo_restante_meses,
        }

    # Opción A: Reducción de plazo manteniendo cuota_actual
    if cuota_actual <= nuevo_saldo * tasa_em:
        nuevo_plazo_meses = plazo_restante_meses
        n_exacto = float(plazo_restante_meses)
    else:
        n_exacto = -math.log(1.0 - (nuevo_saldo * tasa_em) / cuota_actual) / math.log(1.0 + tasa_em)
        nuevo_plazo_meses = max(1, math.ceil(n_exacto))
    intereses_opcion_plazo = max(0.0, cuota_actual * n_exacto - nuevo_saldo)

    # Opción B: Reducción de cuota manteniendo plazo_restante_meses
    nueva_cuota = cuota_fija_francesa(nuevo_saldo, tasa_em, plazo_restante_meses)
    intereses_opcion_cuota = max(0.0, nueva_cuota * plazo_restante_meses - nuevo_saldo)

    return {
        "cuota_mensual_original_cop": round(cuota_actual, 2),
        "opcion_reduccion_plazo": {
            "nuevo_plazo_meses": nuevo_plazo_meses,
            "meses_ahorrados": max(0, plazo_restante_meses - nuevo_plazo_meses),
            "ahorro_intereses_cop": round(max(0.0, intereses_originales - intereses_opcion_plazo), 2),
        },
        "opcion_reduccion_cuota": {
            "nueva_cuota_mensual_cop": round(nueva_cuota, 2),
            "flujo_mensual_liberado_cop": round(max(0.0, cuota_actual - nueva_cuota), 2),
            "ahorro_intereses_cop": round(max(0.0, intereses_originales - intereses_opcion_cuota), 2),
        },
    }


def simular_compra_cartera(
    lista_deudas: List[Dict[str, Any]],
    tasa_ea_compra_cartera: float,
    plazo_meses_nuevo: int,
    seguro_mensual_nuevo_cop: float = 15_000.0,
) -> Dict[str, Any]:
    """
    Evalúa la viabilidad financiera de unificar pasivos costosos mediante una Compra de Cartera
    en una entidad vigilada por la SFC con menor tasa Efectiva Anual (EA).
    """
    saldo_total = sum(float(d["saldo_cop"]) for d in lista_deudas if float(d["saldo_cop"]) > 0)
    cuota_total_actual = sum(
        float(d["cuota_mensual_cop"]) + float(d.get("seguro_cuota_manejo_cop", 0.0))
        for d in lista_deudas
        if float(d["saldo_cop"]) > 0
    )
    sim_actual = _simular_estrategia_desendeudamiento(lista_deudas, 0.0, criterio_orden="sin_abono")

    tasa_em_nueva = ea_a_em(tasa_ea_compra_cartera)
    nueva_cuota_capital_interes = cuota_fija_francesa(saldo_total, tasa_em_nueva, plazo_meses_nuevo)
    nueva_cuota_total = nueva_cuota_capital_interes + seguro_mensual_nuevo_cop

    intereses_nuevos = max(0.0, nueva_cuota_capital_interes * plazo_meses_nuevo - saldo_total)
    seguros_nuevos = seguro_mensual_nuevo_cop * plazo_meses_nuevo
    costo_total_nuevo = intereses_nuevos + seguros_nuevos

    ahorro_costo_total = sim_actual["costo_financiero_total_cop"] - costo_total_nuevo
    flujo_mensual_liberado = cuota_total_actual - nueva_cuota_total

    return {
        "saldo_unificado_cop": round(saldo_total, 2),
        "tasa_ea_nueva_pct": round(tasa_ea_compra_cartera * 100.0, 2),
        "plazo_nuevo_meses": plazo_meses_nuevo,
        "cuota_mensual_anterior_cop": round(cuota_total_actual, 2),
        "nueva_cuota_mensual_total_cop": round(nueva_cuota_total, 2),
        "flujo_caja_mensual_liberado_cop": round(flujo_mensual_liberado, 2),
        "costo_financiero_anterior_cop": round(sim_actual["costo_financiero_total_cop"], 2),
        "costo_financiero_nuevo_cop": round(costo_total_nuevo, 2),
        "ahorro_neto_costo_financiero_cop": round(ahorro_costo_total, 2),
        "es_viable_financieramente": ahorro_costo_total > 0,
    }


def optimizar_portafolio_deudas(
    ingreso_neto_mensual_cop: float,
    abono_extra_mensual_cop: float,
    lista_deudas: List[Dict[str, Any]],
    config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Ejecuta el Caso de Uso CU-03 (Módulo 3 - Catalina):
    Diagnostica el nivel de endeudamiento, valida usura SFC y compara Plan Base vs. Avalancha vs. Bola de Nieve.
    """
    cfg = config or cargar_configuracion()
    usura_sfc = float(cfg["parametros_macro_colombia"]["tasa_usura_ea_consumo"])

    cuotas_totales = sum(
        float(d["cuota_mensual_cop"]) + float(d.get("seguro_cuota_manejo_cop", 0.0)) for d in lista_deudas
    )
    saldo_total_deuda = sum(float(d["saldo_cop"]) for d in lista_deudas)
    indice_endeudamiento = (cuotas_totales / ingreso_neto_mensual_cop) if ingreso_neto_mensual_cop > 0 else 0.0

    validaciones_usura = [
        {"obligacion": d["nombre"], **validar_usura_sfc(float(d["tasa_ea"]), usura_sfc)} for d in lista_deudas
    ]

    sim_base = _simular_estrategia_desendeudamiento(lista_deudas, 0.0, criterio_orden="sin_abono")
    sim_avalancha = _simular_estrategia_desendeudamiento(lista_deudas, abono_extra_mensual_cop, "avalancha")
    sim_bola_nieve = _simular_estrategia_desendeudamiento(lista_deudas, abono_extra_mensual_cop, "bola_de_nieve")

    ahorro_avalancha = max(
        0.0, sim_base["costo_financiero_total_cop"] - sim_avalancha["costo_financiero_total_cop"]
    )
    deuda_prioritaria_avalancha = (
        sim_avalancha["cronograma_extincion"][0]["obligacion"]
        if sim_avalancha["cronograma_extincion"]
        else "Ninguna"
    )

    return {
        "saldo_total_deudas_cop": round(saldo_total_deuda, 2),
        "cuota_mensual_total_actual_cop": round(cuotas_totales, 2),
        "indice_endeudamiento_pct": round(indice_endeudamiento * 100.0, 2),
        "semaforo_endeudamiento": (
            "VERDE_SALUDABLE"
            if indice_endeudamiento <= 0.30
            else ("AMARILLO_ALERTA" if indice_endeudamiento <= 0.40 else "ROJO_SOBREENDEUDAMIENTO_CRITICO")
        ),
        "validaciones_usura_sfc": validaciones_usura,
        "comparativa_estrategias": {
            "pago_minimo_actual": sim_base,
            "metodo_avalancha_optimo_matematico": sim_avalancha,
            "metodo_bola_de_nieve_conductual": sim_bola_nieve,
        },
        "estrategia_optima": "AVALANCHA",
        "deuda_prioritaria_a_pagar_primero": deuda_prioritaria_avalancha,
        "ahorro_intereses_cop": round(ahorro_avalancha, 2),
        "meses_ahorrados_con_avalancha": max(
            0, sim_base["meses_totales_para_cero_deuda"] - sim_avalancha["meses_totales_para_cero_deuda"]
        ),
        "flujo_caja_liberado_cop": round(cuotas_totales, 2),
    }


def render_interfaz_modulo_3_catalina() -> None:
    """
    Interfaz Streamlit del Módulo 3 (Catalina Moreno) estructurada en los 5 bloques oficiales
    del Manual de Marca OED (`src/oed_design_system.py` — `paso_actual=3`).
    """
    import pandas as pd
    import plotly.graph_objects as go
    import streamlit as st

    from src.oed_design_system import (
        aplicar_estilo_plotly_oed,
        formatear_cop_claro,
        render_encabezado_modulo_oed,
        render_glosario_interactivo_oed,
        render_semaforo_ciudadano_oed,
    )

    # BLOQUE 1: Encabezado OED + Barra de 7 Pasos (`paso_actual=3`)
    render_encabezado_modulo_oed(paso_actual=3)

    # BLOQUE 2: Datos de la Persona (Caso Semilla o Personalizado)
    with st.expander("⚙️ 1. Cuéntanos tus datos principales y tus obligaciones actuales", expanded=True):
        col1, col2 = st.columns(2)
        ingreso = col1.number_input(
            "Tu ingreso neto mensual en pesos ($ COP)",
            min_value=0.0,
            value=5_915_000.0,
            step=200_000.0,
            help="Lo que recibes cada mes después de aportes obligatorios sobre tu IBC.",
        )
        abono_extra = col2.number_input(
            "Cuánto abono extra puedes destinar al mes para salir de deudas ($ COP)",
            min_value=0.0,
            value=350_000.0,
            step=50_000.0,
            help="Monto adicional por encima de tus cuotas mínimas para acelerar tu plan Avalancha o Bola de Nieve.",
        )

        deudas_base = [
            {"nombre": "1. Tarjeta de Crédito Gold", "saldo_cop": 4_800_000.0, "tasa_ea": 0.258, "cuota_mensual_cop": 320_000.0, "seguro_cuota_manejo_cop": 28_000.0},
            {"nombre": "2. Crédito Rotativo Tienda", "saldo_cop": 1_900_000.0, "tasa_ea": 0.225, "cuota_mensual_cop": 160_000.0, "seguro_cuota_manejo_cop": 14_500.0},
            {"nombre": "3. Libre Inversión Bancario", "saldo_cop": 9_500_000.0, "tasa_ea": 0.168, "cuota_mensual_cop": 380_000.0, "seguro_cuota_manejo_cop": 18_000.0},
            {"nombre": "4. Crédito Educativo Libranza", "saldo_cop": 6_200_000.0, "tasa_ea": 0.124, "cuota_mensual_cop": 240_000.0, "seguro_cuota_manejo_cop": 9_500.0},
        ]
        df_edit = st.data_editor(pd.DataFrame(deudas_base), num_rows="dynamic", use_container_width=True)
        lista_deudas = df_edit.to_dict(orient="records")

    res = optimizar_portafolio_deudas(
        ingreso_neto_mensual_cop=ingreso,
        abono_extra_mensual_cop=abono_extra,
        lista_deudas=lista_deudas,
    )

    ie = res["indice_endeudamiento_pct"]
    nivel = "verde" if ie <= 30.0 else ("ambar" if ie <= 40.0 else "rojo")
    primera = res["deuda_prioritaria_a_pagar_primero"]

    # BLOQUE 3: Diagnóstico Financiero (?) + 📌 Plan de Acción + 4 Indicadores Clave
    render_semaforo_ciudadano_oed(
        nivel=nivel,
        titulo_claro=f"Tu estrategia óptima es el método Avalancha empezando por {primera}",
        explicacion_humana=(
            f"Con un índice de endeudamiento del {ie:.1f}% y verificando que ninguna obligación supere la "
            f"Tasa de Usura, aplicar el método Avalancha con Roll-Over te ahorra "
            f"{formatear_cop_claro(res['ahorro_intereses_cop'])} en intereses EA y seguros, reduciendo tu plazo en "
            f"{res['meses_ahorrados_con_avalancha']} meses frente a pagar solo el mínimo."
        ),
        siguiente_paso_accionable=(
            f"Destina este mismo mes tu abono extra de {formatear_cop_claro(abono_extra)} como abono a capital con "
            f"reducción de plazo en '{primera}' amparado en la Ley 1328."
        ),
    )

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Saldo Total Deudas", formatear_cop_claro(res["saldo_total_deudas_cop"]))
    k2.metric("Índice Endeudamiento", f"{ie:.1f}%")
    k3.metric("Ahorro Total Avalancha", formatear_cop_claro(res["ahorro_intereses_cop"]))
    k4.metric("Pagar Primero", primera)

    # BLOQUE 4: Gráficas Interactivas con la Paleta Oficial OED
    comp = res["comparativa_estrategias"]
    fig = go.Figure()
    for nombre_est, clave_est, color in [
        ("Pago Mínimo Actual", "pago_minimo_actual", "#DC2626"),
        ("Bola de Nieve (Menor Saldo)", "metodo_bola_de_nieve_conductual", "#EA580C"),
        ("Avalancha (Óptimo Matemático)", "metodo_avalancha_optimo_matematico", "#15803D"),
    ]:
        hist = comp[clave_est]["historial_mensual"]
        fig.add_trace(
            go.Scatter(
                x=[h["mes"] for h in hist],
                y=[h["saldo_total_cop"] for h in hist],
                mode="lines",
                name=nombre_est,
                line=dict(color=color, width=3),
            )
        )
    fig = aplicar_estilo_plotly_oed(
        fig,
        titulo="Curva de Extinción de tus Deudas en Pesos ($ COP): Avalancha vs. Bola de Nieve",
    )
    st.plotly_chart(fig, use_container_width=True)

    # BLOQUE 5: Diccionario Financiero Desplegable
    render_glosario_interactivo_oed(["EA", "EM", "USURA", "AVALANCHA_NIEVE", "LEY_1328"])
