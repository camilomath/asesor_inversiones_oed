"""
===============================================================================
SUITE DE PRUEBAS UNITARIAS Y ANALÍTICAS: "Test Modulo 3"
MÓDULO 3: Gestión, Administración y Optimización Analítica de Deudas
Responsable OED: Catalina Moreno (Ingeniera Industrial - Líder de Proyectos y Analítica)
===============================================================================

Este archivo implementa y documenta exhaustivamente las pruebas de verificación y
validación matemática, financiera y regulatoria colombiana del Módulo 3
(`src/mod3_gestion_deudas.py`), incluyendo:
- Entradas detalladas (Inputs)
- Salidas esperadas (Outputs)
- Criterios de Éxito (Pass Criteria) y Criterios de Rechazo (Fail Criteria)
"""

from __future__ import annotations

from src.mod3_gestion_deudas import (
    _simular_estrategia_desendeudamiento,
    optimizar_portafolio_deudas,
    simular_abono_extraordinario_ley_1328,
    simular_compra_cartera,
)


def test_01_semaforo_indice_endeudamiento_y_alertas():
    """
    PRUEBA 01 (Test Modulo 3): Clasificación del Semáforo de Índice de Endeudamiento (IE).
    -----------------------------------------------------------------------------------
    * Objetivo: Verificar que el cálculo IE = (Cuotas + Seguros) / Ingreso Neto clasifique
      correctamente al hogar en los tres umbrales de riesgo financiero.
    * Entradas (Inputs):
      - Escenario Saludable: Ingreso Neto = $6.000.000 COP, Cuota Total = $1.500.000 COP (IE = 25.0%).
      - Escenario Alerta:    Ingreso Neto = $6.000.000 COP, Cuota Total = $2.100.000 COP (IE = 35.0%).
      - Escenario Crítico:   Ingreso Neto = $6.000.000 COP, Cuota Total = $2.700.000 COP (IE = 45.0%).
    * Salidas Esperadas (Outputs):
      - `indice_endeudamiento_pct`: 25.0, 35.0 y 45.0 respectivamente.
      - `semaforo_endeudamiento`: "VERDE_SALUDABLE", "AMARILLO_ALERTA" y "ROJO_SOBREENDEUDAMIENTO_CRITICO".
    * Parámetros de Éxito (Pass):
      - IE <= 30% -> "VERDE_SALUDABLE"
      - 30% < IE <= 40% -> "AMARILLO_ALERTA"
      - IE > 40% -> "ROJO_SOBREENDEUDAMIENTO_CRITICO"
    * Parámetros de Rechazo (Fail):
      - Error de redondeo mayor a 0.01% en el IE o asignación errónea de categoría de semáforo.
    """
    # 1. Caso Saludable (25%)
    res_verde = optimizar_portafolio_deudas(
        ingreso_neto_mensual_cop=6_000_000.0,
        abono_extra_mensual_cop=0.0,
        lista_deudas=[
            {
                "nombre": "Crédito Vehículo",
                "saldo_cop": 15_000_000.0,
                "tasa_ea": 0.15,
                "cuota_mensual_cop": 1_450_000.0,
                "seguro_cuota_manejo_cop": 50_000.0,
            }
        ],
    )
    assert res_verde["indice_endeudamiento_pct"] == 25.0
    assert res_verde["semaforo_endeudamiento"] == "VERDE_SALUDABLE"

    # 2. Caso Alerta (35%)
    res_amarillo = optimizar_portafolio_deudas(
        ingreso_neto_mensual_cop=6_000_000.0,
        abono_extra_mensual_cop=0.0,
        lista_deudas=[
            {
                "nombre": "Libre Inversión",
                "saldo_cop": 25_000_000.0,
                "tasa_ea": 0.18,
                "cuota_mensual_cop": 2_050_000.0,
                "seguro_cuota_manejo_cop": 50_000.0,
            }
        ],
    )
    assert res_amarillo["indice_endeudamiento_pct"] == 35.0
    assert res_amarillo["semaforo_endeudamiento"] == "AMARILLO_ALERTA"

    # 3. Caso Sobreendeudamiento Crítico (45%)
    res_rojo = optimizar_portafolio_deudas(
        ingreso_neto_mensual_cop=6_000_000.0,
        abono_extra_mensual_cop=0.0,
        lista_deudas=[
            {
                "nombre": "Portafolio Crítico",
                "saldo_cop": 35_000_000.0,
                "tasa_ea": 0.22,
                "cuota_mensual_cop": 2_600_000.0,
                "seguro_cuota_manejo_cop": 100_000.0,
            }
        ],
    )
    assert res_rojo["indice_endeudamiento_pct"] == 45.0
    assert res_rojo["semaforo_endeudamiento"] == "ROJO_SOBREENDEUDAMIENTO_CRITICO"


def test_02_validador_usura_sfc_en_portafolio():
    """
    PRUEBA 02 (Test Modulo 3): Detección Legal de Tasas que Superan el Límite de Usura SFC.
    ---------------------------------------------------------------------------------------
    * Objetivo: Garantizar el cumplimiento del Art. 884 del Código de Comercio y Art. 305 del
      Código Penal identificando obligaciones que excedan la Tasa de Usura certificada por la SFC (26.50% EA).
    * Entradas (Inputs):
      - Deuda Legal: Tarjeta de Crédito al 25.50% EA (<= 26.50% EA).
      - Deuda Usurera: Préstamo informal / Gota a gota al 42.00% EA (> 26.50% EA).
    * Salidas Esperadas (Outputs):
      - Lista `validaciones_usura_sfc` con `excede_usura = False` para la primera y `True` para la segunda,
        con un exceso de 1.550 puntos básicos (15.50% EA por encima del tope legal).
    * Parámetros de Éxito (Pass):
      - `validaciones_usura_sfc[0]["excede_usura"] is False`
      - `validaciones_usura_sfc[1]["excede_usura"] is True` y `exceso_puntos_basicos == 1550.0`
    * Parámetros de Rechazo (Fail):
      - No detectar una tasa superior al límite de usura o emitir falsos positivos en tasas legales.
    """
    res = optimizar_portafolio_deudas(
        ingreso_neto_mensual_cop=5_000_000.0,
        abono_extra_mensual_cop=200_000.0,
        lista_deudas=[
            {"nombre": "Tarjeta Vigilada SFC", "saldo_cop": 3_000_000.0, "tasa_ea": 0.2550, "cuota_mensual_cop": 200_000.0},
            {"nombre": "Crédito Extrabancario Usura", "saldo_cop": 2_000_000.0, "tasa_ea": 0.4200, "cuota_mensual_cop": 200_000.0},
        ],
    )
    val_legal = res["validaciones_usura_sfc"][0]
    val_usura = res["validaciones_usura_sfc"][1]

    assert val_legal["excede_usura"] is False
    assert val_usura["excede_usura"] is True
    assert val_usura["exceso_puntos_basicos"] == 1550.0
    assert "ALERTA LEGAL SFC" in val_usura["mensaje_legal"]


def test_03_optimalidad_avalancha_vs_bola_de_nieve_y_pago_minimo():
    """
    PRUEBA 03 (Test Modulo 3): Investigación de Operaciones — Avalancha vs. Bola de Nieve con Roll-Over.
    ----------------------------------------------------------------------------------------------------
    * Objetivo: Demostrar matemáticamente que el Método Avalancha (priorizar mayor tasa EA) minimiza
      el costo financiero total frente al Pago Mínimo y frente al Método Bola de Nieve, mientras que
      Bola de Nieve extingue primero la obligación de menor saldo.
    * Entradas (Inputs):
      - Deuda 1 (Menor Saldo, Tasa Baja): $1.500.000 COP al 12.0% EA, cuota $100.000 COP.
      - Deuda 2 (Mayor Saldo, Tasa Alta): $6.000.000 COP al 26.0% EA, cuota $250.000 COP.
      - Abono Extra Mensual: $350.000 COP/mes con efecto roll-over.
    * Salidas Esperadas (Outputs):
      - `costo_financiero_total_cop` (Avalancha) <= `costo_financiero_total_cop` (Bola de Nieve) < `costo_financiero_total_cop` (Pago Mínimo).
      - `meses_totales_para_cero_deuda` con abono extra sustancialmente menor que sin abono extra.
      - Historial mensual con saldo final exactamente igual a $0.0 COP.
    * Parámetros de Éxito (Pass):
      - Ahorro positivo de intereses con Avalancha respecto a Pago Mínimo y respecto a Bola de Nieve.
      - En Bola de Nieve la "Deuda Pequeña Tasa Baja" se extingue en menor o igual cantidad de meses que en Avalancha.
    * Parámetros de Rechazo (Fail):
      - Que Avalancha pague más intereses que Bola de Nieve o que el saldo final no converja a 0.
    """
    portafolio = [
        {
            "nombre": "Deuda Pequeña Tasa Baja",
            "saldo_cop": 1_500_000.0,
            "tasa_ea": 0.120,
            "cuota_mensual_cop": 100_000.0,
            "seguro_cuota_manejo_cop": 5_000.0,
        },
        {
            "nombre": "Deuda Grande Tasa Alta",
            "saldo_cop": 6_000_000.0,
            "tasa_ea": 0.260,
            "cuota_mensual_cop": 250_000.0,
            "seguro_cuota_manejo_cop": 20_000.0,
        },
    ]

    res = optimizar_portafolio_deudas(
        ingreso_neto_mensual_cop=5_500_000.0,
        abono_extra_mensual_cop=350_000.0,
        lista_deudas=portafolio,
    )

    sim_base = res["comparativa_estrategias"]["pago_minimo_actual"]
    sim_aval = res["comparativa_estrategias"]["metodo_avalancha_optimo_matematico"]
    sim_nieve = res["comparativa_estrategias"]["metodo_bola_de_nieve_conductual"]

    # 1. Optimalidad matemática de Avalancha en intereses pagados
    assert sim_aval["total_intereses_pagados_cop"] < sim_nieve["total_intereses_pagados_cop"]
    assert sim_nieve["total_intereses_pagados_cop"] < sim_base["total_intereses_pagados_cop"]
    assert res["ahorro_intereses_cop"] > 0
    assert res["meses_ahorrados_con_avalancha"] > 0

    # 2. Victoria temprana conductual en Bola de Nieve (extingue primero la deuda pequeña)
    mes_pequena_nieve = next(
        d["mes_extincion"] for d in sim_nieve["cronograma_extincion"] if d["obligacion"] == "Deuda Pequeña Tasa Baja"
    )
    mes_pequena_aval = next(
        d["mes_extincion"] for d in sim_aval["cronograma_extincion"] if d["obligacion"] == "Deuda Pequeña Tasa Baja"
    )
    assert mes_pequena_nieve < mes_pequena_aval

    # 3. Convergencia a saldo cero en el historial mensual
    assert sim_aval["historial_mensual"][-1]["saldo_total_cop"] == 0.0


def test_04_simulador_abono_extraordinario_ley_1328():
    """
    PRUEBA 04 (Test Modulo 3): Simulador de Prepago a Capital bajo Ley 1328 de 2009.
    --------------------------------------------------------------------------------
    * Objetivo: Verificar el derecho legal a realizar abonos extraordinarios a capital sin penalidad,
      comprobando que la Opción A (Reducción de Plazo) ahorra más intereses que la Opción B
      (Reducción de Cuota), mientras que la Opción B libera flujo de caja mensual inmediato.
    * Entradas (Inputs):
      - Saldo Actual: $9.500.000 COP
      - Tasa Efectiva Anual: 16.80% EA
      - Plazo Restante: 36 meses
      - Abono Extraordinario a Capital: $2.500.000 COP (Caso 1: Abono Parcial) y $10.000.000 COP (Caso 2: Pago Total).
    * Salidas Esperadas (Outputs):
      - Caso 1 (Parcial): `meses_ahorrados` > 0 en Reducción de Plazo; `flujo_mensual_liberado_cop` > 0 en Reducción de Cuota;
        Ahorro Intereses Plazo > Ahorro Intereses Cuota.
      - Caso 2 (Total): `deuda_cancelada_totalmente = True` y `meses_ahorrados = 36`.
    * Parámetros de Éxito (Pass):
      - Cumplimiento estricto de las desigualdades financieras de amortización francesa.
    * Parámetros de Rechazo (Fail):
      - Que reducir cuota reporte mayor ahorro de intereses que reducir plazo, o fallo al cancelar el 100% del saldo.
    """
    # Caso 1: Abono parcial de $2.500.000 COP
    parcial = simular_abono_extraordinario_ley_1328(
        saldo_actual_cop=9_500_000.0,
        tasa_ea=0.1680,
        plazo_restante_meses=36,
        abono_extra_capital_cop=2_500_000.0,
    )
    assert parcial["opcion_reduccion_plazo"]["nuevo_plazo_meses"] < 36
    assert parcial["opcion_reduccion_plazo"]["meses_ahorrados"] >= 10
    assert parcial["opcion_reduccion_cuota"]["flujo_mensual_liberado_cop"] > 80_000.0
    assert (
        parcial["opcion_reduccion_plazo"]["ahorro_intereses_cop"]
        > parcial["opcion_reduccion_cuota"]["ahorro_intereses_cop"]
    )

    # Caso 2: Abono que cubre el 100% del saldo
    total = simular_abono_extraordinario_ley_1328(
        saldo_actual_cop=9_500_000.0,
        tasa_ea=0.1680,
        plazo_restante_meses=36,
        abono_extra_capital_cop=10_000_000.0,
    )
    assert total["deuda_cancelada_totalmente"] is True
    assert total["meses_ahorrados"] == 36
    assert total["ahorro_intereses_reduccion_plazo_cop"] > 0


def test_05_evaluacion_compra_cartera_viable_vs_no_viable():
    """
    PRUEBA 05 (Test Modulo 3): Viabilidad Financiera de Compra de Cartera Consolidada.
    ----------------------------------------------------------------------------------
    * Objetivo: Evaluar cuándo una oferta de Compra de Cartera realmente ahorra dinero al deudor
      (escenario viable) y cuándo una tasa alta o plazo excesivo encarece el costo total (escenario rechazado).
    * Entradas (Inputs):
      - Portafolio Actual: Tarjeta $4.800.000 al 25.8% EA + Libre Inversión $9.500.000 al 16.8% EA.
      - Oferta Viable: Tasa 12.5% EA a 24 meses.
      - Oferta Inconveniente: Tasa 24.0% EA a 60 meses (alarga plazo y sube costo total).
    * Salidas Esperadas (Outputs):
      - Oferta Viable: `es_viable_financieramente = True` y `ahorro_neto_costo_financiero_cop > 0`.
      - Oferta Inconveniente: `es_viable_financieramente = False` y `ahorro_neto_costo_financiero_cop < 0`.
    * Parámetros de Éxito (Pass):
      - Identificación exacta de viabilidad positiva en el primer caso y rechazo financiero en el segundo.
    * Parámetros de Rechazo (Fail):
      - Recomendar una compra de cartera cuyo costo financiero total supere el costo actual de las deudas.
    """
    deudas_actuales = [
        {
            "nombre": "Tarjeta de Crédito Gold",
            "saldo_cop": 4_800_000.0,
            "tasa_ea": 0.2580,
            "cuota_mensual_cop": 320_000.0,
            "seguro_cuota_manejo_cop": 28_000.0,
        },
        {
            "nombre": "Libre Inversión",
            "saldo_cop": 9_500_000.0,
            "tasa_ea": 0.1680,
            "cuota_mensual_cop": 380_000.0,
            "seguro_cuota_manejo_cop": 18_000.0,
        },
    ]

    # Escenario A: Compra de cartera competitiva (12.5% EA a 24 meses)
    compra_buena = simular_compra_cartera(
        lista_deudas=deudas_actuales,
        tasa_ea_compra_cartera=0.1250,
        plazo_meses_nuevo=24,
        seguro_mensual_nuevo_cop=15_000.0,
    )
    assert compra_buena["saldo_unificado_cop"] == 14_300_000.0
    assert compra_buena["es_viable_financieramente"] is True
    assert compra_buena["ahorro_neto_costo_financiero_cop"] > 0

    # Escenario B: Compra de cartera desfavorable (24.0% EA estirada a 60 meses)
    compra_mala = simular_compra_cartera(
        lista_deudas=deudas_actuales,
        tasa_ea_compra_cartera=0.2400,
        plazo_meses_nuevo=60,
        seguro_mensual_nuevo_cop=35_000.0,
    )
    assert compra_mala["es_viable_financieramente"] is False
    assert compra_mala["ahorro_neto_costo_financiero_cop"] < 0
