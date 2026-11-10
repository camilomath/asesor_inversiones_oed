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
  eligiendo entre Reducción de Plazo vs. Reducción de Cuota).
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

    return {
        "estrategia": criterio_orden,
        "meses_totales_para_cero_deuda": mes,
        "total_intereses_pagados_cop": round(total_intereses_pagados, 2),
        "total_seguros_y_manejo_pagados_cop": round(total_seguros_pagados, 2),
        "costo_financiero_total_cop": round(total_intereses_pagados + total_seguros_pagados, 2),
        "cronograma_extincion": [
            {"obligacion": d["nombre"], "mes_extincion": d["mes_extincion"], "tasa_ea_pct": round(d["tasa_ea"] * 100, 2)}
            for d in deudas
        ],
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
        "ahorro_intereses_cop": round(ahorro_avalancha, 2),
        "meses_ahorrados_con_avalancha": max(
            0, sim_base["meses_totales_para_cero_deuda"] - sim_avalancha["meses_totales_para_cero_deuda"]
        ),
        "flujo_caja_liberado_cop": round(cuotas_totales, 2),
    }
