"""
Servidor Web Local para el Asesor Financiero e Inversiones OED.
Desarrollado con FastAPI y Uvicorn.
Aplica el Manual de Marca Oficial OED:
- Voz de "Asesor Financiero de Confianza" (cercano, empático, sin regaños).
- Los 5 Bloques Estándar de Interfaz (Paso 1: Salin Avellaneda).
- Regla "Cero Palabras Huérfanas" con burbujas interactivas (?) del Diccionario OED.
- Paleta Oficial OED (Azul Solidez #0F294A, Azul Acción #1D4ED8, Naranja Plan de Acción #EA580C, Verde Viabilidad #15803D).
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# Importación de módulos del proyecto
from src.data_governance import (
    registrar_consentimiento_habeas_data,
    cifrar_payload_local,
    descifrar_payload_local,
    calcular_permanencia_centrales_riesgo_ley_1266,
)
from src.finance import (
    ea_a_em,
    em_a_ea,
    validar_usura_sfc,
    valor_futuro_aportes_periodicos,
    cuota_fija_francesa,
)
from src.mod1_presupuesto import diagnosticar_presupuesto_y_flujo_caja
from src.mod2_inversiones_salario import estructurar_portafolio_salario
from src.mod3_gestion_deudas import optimizar_portafolio_deudas
from src.mod4_finca_raiz import evaluar_inversion_finca_raiz
from src.mod5_decisiones_vida import evaluar_viabilidad_decision_vida
from src.mod6_educacion_financiera import (
    obtener_cuestionario_suitability,
    evaluar_cuestionario_suitability_completo,
    comparar_azar_vs_inversion_compuesta,
    simular_trayectoria_mensual_azar_vs_inversion,
    detectar_esquema_piramidal_ponzi,
    obtener_trivias_cultura_financiera,
    simular_portafolio_realista_segun_perfil,
    CATALOGO_ACTIVOS_COLOMBIA,
)
from src.oed_design_system import (
    COLORES_GRAFICAS_OED,
    GLOSARIO_LENGUAJE_CLARO_OED,
    PALETA_MARCA_OED,
    RUTA_CLINICA_FINANCIERA_OED,
    formatear_cop_claro,
)

app = FastAPI(
    title="Asesor Financiero e Inversiones OED",
    description="Plataforma Local de Asesoría Financiera Colombiana — Manual de Marca OED",
)


class SuitabilityRequest(BaseModel):
    respuestas: Dict[str, int]


class PortafolioRequest(BaseModel):
    perfil_riesgo: str = "Moderado"
    capacidad_inversion_mensual_cop: float = 1_000_000.0
    capital_inicial_cop: float = 2_000_000.0
    horizonte_anios: int = 10
    gasto_recreativo_azar_cop: float = 50_000.0


class AzarRequest(BaseModel):
    gasto_mensual_cop: float
    horizonte_anios: int = 10
    tasa_ea: float = 0.11


class PonziRequest(BaseModel):
    rentabilidad_mensual_pct: float
    personas_por_ciclo: int = 3


# Endpoints API
@app.get("/api/cuestionario-suitability")
def api_cuestionario():
    return obtener_cuestionario_suitability()


@app.post("/api/evaluar-suitability")
def api_evaluar_suitability(req: SuitabilityRequest):
    return evaluar_cuestionario_suitability_completo(req.respuestas)


@app.post("/api/portafolio-realista")
def api_portafolio_realista(req: PortafolioRequest):
    return simular_portafolio_realista_segun_perfil(
        perfil_riesgo=req.perfil_riesgo,
        capacidad_inversion_mensual_cop=req.capacidad_inversion_mensual_cop,
        capital_inicial_cop=req.capital_inicial_cop,
        horizonte_anios=req.horizonte_anios,
        gasto_recreativo_azar_cop=req.gasto_recreativo_azar_cop,
    )


@app.get("/api/catalogo-activos")
def api_catalogo_activos():
    return CATALOGO_ACTIVOS_COLOMBIA


@app.get("/api/glosario-oed")
def api_glosario():
    return GLOSARIO_LENGUAJE_CLARO_OED


@app.post("/api/azar-vs-inversion")
def api_azar(req: AzarRequest):
    res = comparar_azar_vs_inversion_compuesta(
        gasto_mensual_juegos_azar_cop=req.gasto_mensual_cop,
        horizonte_anios=req.horizonte_anios,
        tasa_ea_inversion_regulada=req.tasa_ea,
    )
    trayectoria = simular_trayectoria_mensual_azar_vs_inversion(
        monto_mensual_cop=req.gasto_mensual_cop,
        anios=req.horizonte_anios,
        tasa_ea_inversion=req.tasa_ea,
    )
    return {"resumen": res, "trayectoria": trayectoria}


@app.post("/api/detector-ponzi")
def api_ponzi(req: PonziRequest):
    return detectar_esquema_piramidal_ponzi(
        rentabilidad_mensual_prometida_pct=req.rentabilidad_mensual_pct,
        personas_reclutadas_por_ciclo=req.personas_por_ciclo,
    )


@app.get("/api/trivias")
def api_trivias():
    return obtener_trivias_cultura_financiera()


@app.post("/api/caso-completo-oed")
def api_caso_completo():
    """Ejecuta la consulta integral con los 6 módulos del Asesor Financiero OED."""
    # Paso 0: Consentimiento
    cons = registrar_consentimiento_habeas_data("1032390306", True)

    # Paso 1: Salin (Módulo 6)
    perfil = evaluar_cuestionario_suitability_completo({
        "p1_horizonte": 2, "p2_reaccion_caida": 2, "p3_objetivo_inversion": 2,
        "p4_conocimiento_financiero": 2, "p5_dependencia_ingresos": 2,
        "p6_porcentaje_patrimonio": 1, "p7_fondo_emergencia": 2, "p8_educacion_tributaria": 2
    })
    portafolio = simular_portafolio_realista_segun_perfil(
        perfil_riesgo=perfil["perfil_riesgo"],
        capacidad_inversion_mensual_cop=1_000_000.0,
        capital_inicial_cop=2_000_000.0,
        horizonte_anios=10,
        gasto_recreativo_azar_cop=50_000.0,
    )
    azar = comparar_azar_vs_inversion_compuesta(50_000.0, 10, 0.11)

    # Paso 2: Nidia (Módulo 1)
    pres = diagnosticar_presupuesto_y_flujo_caja(
        ingreso_bruto_mensual_cop=6_500_000.0,
        gastos_fijos_vitales_cop=2_800_000.0,
        gastos_variables_estilo_vida_cop=950_000.0,
        gastos_hormiga_mensual_cop=320_000.0,
        cuotas_deuda_mensual_cop=600_000.0,
        liquidez_actual_fondo_emergencia_cop=9_000_000.0,
    )

    # Paso 3: Catalina (Módulo 3)
    deudas = optimizar_portafolio_deudas(
        ingreso_neto_mensual_cop=pres["ingreso_neto_mensual_cop"],
        abono_extra_mensual_cop=300_000.0,
        lista_deudas=[
            {"nombre": "Tarjeta Crédito", "saldo_cop": 4_500_000.0, "tasa_ea": 0.255, "cuota_mensual_cop": 350_000.0},
            {"nombre": "Libre Inversión", "saldo_cop": 8_000_000.0, "tasa_ea": 0.165, "cuota_mensual_cop": 250_000.0},
        ],
    )

    # Paso 4: Camilo (Módulo 2)
    inv = estructurar_portafolio_salario(
        excedente_mensual_cop=pres["excedente_mensual_cop"],
        perfil_riesgo=perfil["perfil_riesgo"],
        horizonte_meses=60,
    )

    # Paso 5: Jesi (Módulo 4)
    finca = evaluar_inversion_finca_raiz(
        valor_inmueble_cop=200_000_000.0,
        ingreso_familiar_neto_cop=pres["ingreso_neto_mensual_cop"] + 3_500_000.0,
    )

    # Paso 6: Nelson (Módulo 5)
    vida = evaluar_viabilidad_decision_vida(
        tipo_decision="HIJOS",
        ingreso_neto_hogar_mensual_cop=pres["ingreso_neto_mensual_cop"] + 3_500_000.0,
        excedente_mensual_actual_cop=pres["excedente_mensual_cop"] + 1_200_000.0,
    )

    return {
        "habeas_data": cons,
        "modulo6_salin": {"perfil": perfil, "portafolio": portafolio, "azar": azar},
        "modulo1_nidia": pres,
        "modulo3_catalina": deudas,
        "modulo2_camilo": inv,
        "modulo4_jesi": finca,
        "modulo5_nelson": vida,
    }


HTML_CONTENT = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Asesor Financiero e Inversiones OED — Manual de Marca</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    :root {
      --azul-solidez: #0F294A;
      --azul-accion: #1D4ED8;
      --naranja-plan: #EA580C;
      --verde-viabilidad: #15803D;
      --ambar-preventivo: #B45309;
      --rojo-riesgo: #B91C1C;
      --gris-fondo: #0b1325;
    }
    body {
      font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background-color: var(--gris-fondo);
      color: #E2E8F0;
    }
    /* Estilos Oficiales del Sistema de Diseño OED */
    .oed-header {
      background: linear-gradient(135deg, #0F294A 0%, #1D4ED8 100%);
      border-bottom: 2px solid rgba(234, 88, 12, 0.4);
    }
    .oed-step-pill {
      font-size: 0.76rem;
      padding: 5px 12px;
      border-radius: 9999px;
      border: 1px solid #334155;
      background: #1e293b;
      color: #94a3b8;
      transition: all 0.2s;
      white-space: nowrap;
    }
    .oed-step-pill:hover {
      border-color: #64748b;
      color: #f1f5f9;
    }
    .oed-step-active {
      background: #EA580C !important;
      color: #FFFFFF !important;
      border-color: #EA580C !important;
      font-weight: 700;
      box-shadow: 0 4px 14px rgba(234, 88, 12, 0.35);
    }
    /* Tarjetas del Semáforo Financiero OED */
    .oed-doc-card {
      border-radius: 12px;
      padding: 1.15rem 1.35rem;
      border-left: 6px solid;
      font-size: 0.93rem;
      line-height: 1.55;
    }
    .oed-doc-verde {
      background: rgba(21, 128, 61, 0.12);
      border-color: #15803D;
      color: #86efac;
    }
    .oed-doc-ambar {
      background: rgba(180, 83, 9, 0.14);
      border-color: #B45309;
      color: #fcd34d;
    }
    .oed-doc-rojo {
      background: rgba(185, 28, 28, 0.15);
      border-color: #B91C1C;
      color: #fca5a5;
    }
    .oed-doc-azul {
      background: rgba(29, 78, 216, 0.12);
      border-color: #1D4ED8;
      color: #93c5fd;
    }
    .oed-rx-box {
      background: linear-gradient(135deg, rgba(234, 88, 12, 0.12) 0%, rgba(234, 88, 12, 0.05) 100%);
      border: 1px solid rgba(234, 88, 12, 0.4);
      border-left: 6px solid #EA580C;
      padding: 1rem 1.25rem;
      border-radius: 12px;
      color: #fed7aa;
      font-size: 0.92rem;
      line-height: 1.5;
    }
    /* Burbujas Explicativas Interactivas (?) — Regla Cero Palabras Huérfanas */
    .oed-term {
      position: relative;
      border-bottom: 2px dotted #1D4ED8;
      cursor: help;
      font-weight: 600;
      padding: 0 3px;
      border-radius: 3px;
      background: rgba(29, 78, 216, 0.15);
      color: #93c5fd;
      display: inline-block;
    }
    .oed-term:hover::after, .oed-term:focus::after {
      content: attr(data-tip);
      position: absolute;
      bottom: 125%;
      left: 50%;
      transform: translateX(-50%);
      background: #0F294A;
      color: #FFFFFF;
      padding: 9px 13px;
      border-radius: 8px;
      font-size: 0.77rem;
      line-height: 1.4;
      white-space: normal;
      width: 290px;
      z-index: 1000;
      box-shadow: 0 12px 30px rgba(0, 0, 0, 0.6);
      pointer-events: none;
      border: 1px solid #1D4ED8;
      text-align: left;
      font-weight: 400;
    }
    .oed-q {
      font-size: 0.72em;
      color: #EA580C;
      margin-left: 2px;
      font-weight: bold;
    }
    /* Métricas estilo Streamlit st.metric */
    .kpi-metric-box {
      background: #111e33;
      border: 1px solid #1e293b;
      border-radius: 12px;
      padding: 1rem 1.15rem;
      transition: all 0.2s;
    }
    .kpi-metric-box:hover {
      border-color: #1D4ED8;
      box-shadow: 0 6px 20px rgba(15, 41, 74, 0.35);
    }
  </style>
</head>
<body class="min-h-screen flex flex-col">

  <!-- ============================================================================== -->
  <!-- ENCABEZADO INSTITUCIONAL OED (AZUL SOLIDEZ #0F294A + AZUL ACCIÓN #1D4ED8) -->
  <!-- ============================================================================== -->
  <header class="oed-header text-white sticky top-0 z-50 shadow-xl backdrop-blur">
    <div class="max-w-7xl mx-auto px-4 py-3.5 flex flex-wrap items-center justify-between gap-3">
      <div class="flex items-center space-x-3.5">
        <div class="w-11 h-11 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center font-black text-white text-xl tracking-tight shadow-inner">
          OED
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <h1 class="text-base sm:text-lg font-bold tracking-tight">Asesor Financiero y de Inversiones OED</h1>
            <span class="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              Modo Local 100%
            </span>
          </div>
          <p class="text-xs text-slate-300">Voz de "Asesor Financiero de Confianza" • Cero Palabras Huérfanas (<sup class="oed-q">?</sup>) • Rama <code>SALIN</code></p>
        </div>
      </div>
      <div class="flex items-center space-x-2">
        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-orange-500/20 text-orange-300 border border-orange-500/30">
          🎯 Paso 1: Salin Avellaneda
        </span>
      </div>
    </div>
  </header>

  <!-- ============================================================================== -->
  <!-- BLOQUE 1 DEL MANUAL DE MARCA: BARRA DE PROGRESO DE LOS 7 PASOS (PASOS 0 AL 6) -->
  <!-- ============================================================================== -->
  <div class="bg-slate-950/90 border-b border-slate-800 py-2.5 px-4 sticky top-[68px] z-40 backdrop-blur">
    <div class="max-w-7xl mx-auto flex items-center space-x-2 overflow-x-auto text-xs pb-1">
      <span class="oed-step-pill" title="Habeas Data Local">Paso 0: 🤝 Bienvenida y Datos (Nelson + Camilo)</span>
      <span class="oed-step-pill oed-step-active" title="Módulo 6: Perfil de Riesgo y Portafolio">Paso 1: 🎯 Tu Perfil de Riesgo y Criterio de Inversión (Salin)</span>
      <span class="oed-step-pill" title="Módulo 1: Flujo de Caja">Paso 2: 📊 Análisis de tu Sueldo y Gastos (Nidia)</span>
      <span class="oed-step-pill" title="Módulo 3: Optimización de Deudas">Paso 3: 🔓 Estrategia Salir de Deudas (Catalina)</span>
      <span class="oed-step-pill" title="Módulo 2: Inversión Salarial">Paso 4: 🌱 Plan de Inversión Mensual (Camilo)</span>
      <span class="oed-step-pill" title="Módulo 4: Finca Raíz">Paso 5: 🏡 Viabilidad Finca Raíz (Jesi)</span>
      <span class="oed-step-pill" title="Módulo 5: Estrés Monte Carlo">Paso 6: 🛡️ Prueba de Estrés Financiero (Nelson)</span>
    </div>
  </div>

  <!-- Pestañas de Navegación de Vistas -->
  <div class="max-w-7xl mx-auto px-4 pt-5 w-full">
    <nav class="flex space-x-2 overflow-x-auto border-b border-slate-800 pb-2" id="tabBar">
      <button onclick="cambiarTab('mod6')" id="tab-mod6" class="px-4 py-2 text-xs sm:text-sm font-semibold rounded-lg bg-blue-700 text-white transition shadow-lg shadow-blue-700/20">
        🎯 Paso 1: Módulo 6 (Salin — Riesgo y Portafolio Realista)
      </button>
      <button onclick="cambiarTab('diccionario')" id="tab-diccionario" class="px-4 py-2 text-xs sm:text-sm font-medium rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition">
        📘 Diccionario Financiero OED (5 Familias)
      </button>
      <button onclick="cambiarTab('consulta')" id="tab-consulta" class="px-4 py-2 text-xs sm:text-sm font-medium rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition">
        🚀 Consulta Integral OED (6 Módulos)
      </button>
      <button onclick="cambiarTab('ponzi')" id="tab-ponzi" class="px-4 py-2 text-xs sm:text-sm font-medium rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition">
        ⚠️ Detector de Pirámides (Art. 316 C.P.)
      </button>
      <button onclick="cambiarTab('trivias')" id="tab-trivias" class="px-4 py-2 text-xs sm:text-sm font-medium rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition">
        🎓 Trivias de Cultura Financiera
      </button>
    </nav>
  </div>

  <!-- Contenedor de Vistas -->
  <main class="max-w-7xl mx-auto px-4 py-6 flex-1 w-full space-y-8">

    <!-- ============================================================================== -->
    <!-- VISTA PRINCIPAL: PASO 1 (SALIN AVELLANEDA) ORGANIZADO EN LOS 5 BLOQUES OED -->
    <!-- ============================================================================== -->
    <div id="vista-mod6" class="space-y-7">

      <!-- BLOQUE 1: ENCABEZADO DE ETAPA DEL ASESOR OED -->
      <div class="bg-gradient-to-r from-slate-900 to-[#111e38] border border-blue-900/60 rounded-2xl p-5 sm:p-6 shadow-xl">
        <div class="flex items-center space-x-3 mb-2">
          <span class="text-2xl">🎯</span>
          <div>
            <h2 class="text-lg sm:text-xl font-bold text-white">Tu Perfil de Riesgo y Criterio de Inversión</h2>
            <p class="text-xs text-blue-300">Paso 1 de la Ruta OED • Responsable: <strong>Salin Avellaneda</strong> (Matemático, Líder de Rifas, Juegos y Espectáculos)</p>
          </div>
        </div>
        <div class="mt-3 bg-blue-950/40 border border-blue-800/40 rounded-xl p-3.5 text-xs text-slate-300 leading-relaxed">
          <span class="font-semibold text-blue-200">💬 Mensaje de tu Asesor de Confianza:</span> "Antes de elegir en qué invertir, identifiquemos tu tolerancia real a las variaciones del mercado, el <span class="oed-term" data-tip="💡 Valor Esperado: El resultado promedio real de repetir miles de veces una inversión o apuesta. En juegos de azar es negativo.">Valor Esperado<sup class="oed-q">?</sup></span> y tu horizonte de tiempo. Nadie apuesta todo su dinero: asignemos tu ahorro con números reales entre Renta Fija y Renta Variable con ETFs y acciones en Colombia."
        </div>
      </div>

      <!-- BLOQUE 2: DATOS DE LA PERSONA (EXPANDER LIMPIO DE ENTRADAS) -->
      <div class="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
        <div class="border-b border-slate-800 pb-3 flex items-center justify-between flex-wrap gap-2">
          <div>
            <span class="text-xs font-bold uppercase tracking-wider text-orange-400">Bloque 2 • Entradas del Usuario</span>
            <h3 class="text-base font-bold text-white">1. Test de Idoneidad SFC (<span class="oed-term" data-tip="💡 Decreto 2555 de 2010: Norma de la SFC que obliga a perfilar el riesgo de cada persona antes de recomendar productos de inversión.">Decreto 2555 de 2010<sup class="oed-q">?</sup></span>) & Parámetros Financieros</h3>
          </div>
          <button type="button" onclick="evaluarTestSFC()" id="btnDiagnosticarSFC" class="bg-blue-600 hover:bg-blue-500 text-white font-semibold px-4 py-2 rounded-lg text-xs shadow-lg shadow-blue-600/30 transition flex items-center space-x-1.5">
            <span>📋</span>
            <span>Diagnosticar Perfil de Riesgo</span>
          </button>
        </div>

        <!-- Cuestionario de Idoneidad SFC -->
        <div id="cuestionarioContainer" class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Cuestionario inyectado dinámicamente vía JS -->
        </div>

        <!-- Parámetros de Capacidad de Inversión y Ocio Realista -->
        <div class="pt-4 border-t border-slate-800">
          <span class="text-xs font-bold uppercase tracking-wider text-blue-400 block mb-3">2. Capacidad Real de Ahorro, Capital Inicial y Presupuesto de Ocio</span>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div class="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
              <label class="block text-xs font-semibold text-slate-300">Capacidad Mensual ($ COP)</label>
              <input type="number" id="inpCapacidadMensual" value="1000000" step="50000" min="50000" class="mt-1.5 w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500 font-mono">
              <span class="text-[10px] text-slate-500 mt-0.5 block">Aporte constante sugerido</span>
            </div>

            <div class="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
              <label class="block text-xs font-semibold text-slate-300">Capital Inicial ($ COP)</label>
              <input type="number" id="inpCapitalInicial" value="2000000" step="100000" min="0" class="mt-1.5 w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500 font-mono">
              <span class="text-[10px] text-slate-500 mt-0.5 block">Aporte de partida disponible</span>
            </div>

            <div class="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
              <label class="block text-xs font-semibold text-slate-300">Gasto Ocio / Azar ($ COP/mes)</label>
              <input type="number" id="inpGastoAzar" value="50000" step="10000" min="0" class="mt-1.5 w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500 font-mono">
              <span class="text-[10px] text-slate-500 mt-0.5 block">Presupuesto controlado de recreación</span>
            </div>

            <div class="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
              <label class="block text-xs font-semibold text-slate-300">Horizonte de Tiempo</label>
              <select id="inpAniosPortafolio" class="mt-1.5 w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500">
                <option value="3">3 años (Corto Plazo)</option>
                <option value="5">5 años (Mediano Plazo)</option>
                <option value="10" selected>10 años (Largo Plazo)</option>
                <option value="15">15 años (Construcción Patrimonial)</option>
                <option value="20">20 años (Libertad Financiera)</option>
              </select>
              <span class="text-[10px] text-slate-500 mt-0.5 block">Años de capitalización</span>
            </div>
          </div>

          <div class="mt-4 flex items-center justify-between flex-wrap gap-3">
            <div class="flex items-center space-x-2">
              <span class="text-xs text-slate-400">Perfil calibrado:</span>
              <select id="inpPerfilRiesgo" class="bg-slate-950 border border-blue-600 rounded-lg px-3 py-1.5 text-xs text-white font-bold focus:outline-none">
                <option value="Conservador">Conservador (80% Renta Fija / 20% Variable)</option>
                <option value="Moderado" selected>Moderado (55% Renta Fija / 45% Variable)</option>
                <option value="Agresivo">Agresivo (25% Renta Fija / 75% Variable)</option>
              </select>
            </div>
            <button type="button" onclick="generarPortafolioRealista()" id="btnGenerarPortafolio" class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-5 py-2.5 rounded-lg text-xs shadow-lg shadow-blue-600/30 transition flex items-center space-x-2">
              <span>💼</span>
              <span>Generar Portafolio Realista y Recomendaciones</span>
            </button>
          </div>
        </div>
      </div>

      <!-- BLOQUE 3: DIAGNÓSTICO FINANCIERO + 📌 PLAN DE ACCIÓN + 4 INDICADORES CLAVE -->
      <div id="bloque3Diagnostico" class="space-y-4">
        <!-- Tarjeta del Semáforo Financiero Ciudadano -->
        <div id="tarjetaSemaforo" class="oed-doc-card oed-doc-verde">
          <div class="flex items-center justify-between mb-1.5">
            <span class="font-bold text-sm uppercase tracking-wide flex items-center space-x-1.5">
              <span>✅</span>
              <span id="semTitulo">Diagnóstico Financiero Favorable</span>
            </span>
            <span id="semPerfilBadge" class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-white/20 text-white">
              Perfil Moderado
            </span>
          </div>
          <p id="semExplicacion" class="text-xs sm:text-sm text-slate-200">
            Con una capacidad de ahorro de $1.000.000 COP al mes y $2.000.000 COP de capital inicial, tu portafolio equilibra solidez en <span class="oed-term" data-tip="💡 CDT: Certificado de Depósito a Término respaldado por Fogafín hasta $50M COP.">CDTs<sup class="oed-q">?</sup></span> y <span class="oed-term" data-tip="💡 FIC: Fondo de Inversión Colectiva de liquidez a la vista vigilado por la SFC.">FICs<sup class="oed-q">?</sup></span> con crecimiento global a través de <span class="oed-term" data-tip="💡 ETF: Canasta diversificada de acciones o bonos que se compra en bolsa a bajo costo.">ETFs indexados<sup class="oed-q">?</sup></span>.
          </p>
        </div>

        <!-- Tarjeta de Alerta Conductual Preventiva (si aplica) -->
        <div id="alertaConductualBox" class="hidden oed-doc-card oed-doc-ambar text-xs">
          <span class="font-bold block mb-1">⚠️ Revisión Preventiva de Idoneidad (Decreto 2555 de 2010):</span>
          <span id="alertaConductualTexto"></span>
        </div>

        <!-- Tarjeta Naranja Oficial: 📌 Plan de Acción para este Mes -->
        <div class="oed-rx-box shadow-lg">
          <div class="font-bold text-xs uppercase tracking-wider text-orange-300 flex items-center space-x-1.5 mb-1.5">
            <span>📌</span>
            <span>Plan de Acción para este Mes (En Pesos Colombianos)</span>
          </div>
          <p id="planAccionMesTexto" class="text-xs sm:text-sm text-orange-100 leading-relaxed font-medium">
            Destina este mismo mes $550.000 COP a Renta Fija protegida por Fogafín (CDT digital o FIC a la vista) y $450.000 COP a ETFs indexados globales (S&P 500 vía MGC) programando una transferencia automática el día que recibes tu salario. Mantén tu presupuesto de recreación en máximo $50.000 COP/mes sin tocar tus ahorros.
          </p>
        </div>

        <!-- 4 Indicadores Clave (Estilo st.metric) -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3.5">
          <div class="kpi-metric-box">
            <span class="text-[11px] uppercase tracking-wider text-slate-400 block font-semibold">Capacidad Mensual</span>
            <span class="text-base sm:text-lg font-bold text-white block mt-0.5" id="kpiCapacidadMensual">$1.000.000 COP</span>
            <span class="text-[10px] text-slate-400">Aporte constante</span>
          </div>
          <div class="kpi-metric-box">
            <span class="text-[11px] uppercase tracking-wider text-slate-400 block font-semibold">Asignación Macro</span>
            <span class="text-base sm:text-lg font-bold text-blue-400 block mt-0.5" id="kpiAsignacionMacro">55% RF / 45% RV</span>
            <span class="text-[10px] text-slate-400">Renta Fija / Renta Var.</span>
          </div>
          <div class="kpi-metric-box">
            <span class="text-[11px] uppercase tracking-wider text-slate-400 block font-semibold">Tasa Ponderada <span class="oed-term" data-tip="💡 EA: Tasa Efectiva Anual, rendimiento compuesto anualizado real.">EA<sup class="oed-q">?</sup></span></span>
            <span class="text-base sm:text-lg font-bold text-emerald-400 block mt-0.5" id="kpiTasaEA">11.8% EA</span>
            <span class="text-[10px] text-slate-400">Retorno estimado portafolio</span>
          </div>
          <div class="kpi-metric-box">
            <span class="text-[11px] uppercase tracking-wider text-slate-400 block font-semibold">Patrimonio Proyectado</span>
            <span class="text-base sm:text-lg font-bold text-orange-400 block mt-0.5" id="kpiPatrimonioFinal">$248.500.000 COP</span>
            <span class="text-[10px] text-slate-400" id="kpiHorizonteSub">A 10 años (Esc. Esperado)</span>
          </div>
        </div>
      </div>

      <!-- BLOQUE 4: ASIGNACIÓN DE ACTIVOS REALISTA, FUENTES OFICIALES Y PROYECCIONES -->
      <div id="bloque4Portafolio" class="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
        <div>
          <span class="text-xs font-bold uppercase tracking-wider text-blue-400">Bloque 4 • Desglose de Inversión y Proyecciones Tri-Escenario</span>
          <h3 class="text-base font-bold text-white mt-0.5">Asignación Estratégica: Renta Fija (CDTs/FICs/TES) y Renta Variable (ETFs y Acciones Libres)</h3>
          <p class="text-xs text-slate-400 mt-1">Con fuentes de referencia del mercado colombiano y seguro <span class="oed-term" data-tip="💡 Seguro Fogafín: Cobertura pública automática hasta $50M COP por persona en cada entidad inscrita.">Fogafín<sup class="oed-q">?</sup></span>.</p>
        </div>

        <!-- Tabla Detallada de Activos -->
        <div class="overflow-x-auto rounded-xl border border-slate-800">
          <table class="w-full text-xs text-left">
            <thead class="bg-slate-950 text-slate-300 uppercase tracking-wider font-semibold border-b border-slate-800 text-[11px]">
              <tr>
                <th class="px-4 py-3">Activo Financiero</th>
                <th class="px-4 py-3">Clase de Activo</th>
                <th class="px-3 py-3 text-center">Ponderación</th>
                <th class="px-4 py-3 text-right">Aporte Mensual ($ COP)</th>
                <th class="px-3 py-3 text-center">Retorno Ref.</th>
                <th class="px-4 py-3">Fuente Oficial de Referencia</th>
              </tr>
            </thead>
            <tbody id="tablaActivosBody" class="divide-y divide-slate-800 bg-slate-900/50">
              <!-- Inyectado vía JS -->
            </tbody>
          </table>
        </div>

        <!-- 3 Escenarios de Proyección a Futuro -->
        <div>
          <h4 class="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3 flex items-center space-x-1.5">
            <span>📈</span>
            <span>Proyección de Patrimonio en 3 Escenarios (Interés Compuesto)</span>
          </h4>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4" id="cardsEscenarios">
            <!-- Cards de Escenarios inyectados vía JS -->
          </div>
        </div>

        <!-- Análisis de Ocio y Azar (Valor Esperado E[X] vs Inversión) -->
        <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-4 space-y-2">
          <div class="flex items-center justify-between flex-wrap gap-2">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-1.5">
              <span>🎲</span>
              <span>Laboratorio de Ocio y Azar: <span class="oed-term" data-tip="💡 Valor Esperado E[X]: Pérdida matemática de ~52% por peso apostado en juegos de suerte y azar.">Valor Esperado E[X]<sup class="oed-q">?</sup></span> vs Inversión</span>
            </span>
            <span id="badgeOcioSaludable" class="text-[11px] px-2.5 py-0.5 rounded-full font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              Ocio Saludable (&lt;5% del ahorro)
            </span>
          </div>
          <p class="text-xs text-slate-300 leading-relaxed" id="textoOcioAnalisis">
            Destinas $50.000 COP/mes a entretenimiento/azar (4.8% de tu flujo de ahorro). En 10 años, ese desembolso sumará $6.000.000 COP con una pérdida matemática estimada de $3.120.000 COP frente a los $11.500.000 COP que ese mismo dinero construiría si se invirtiera al 11% EA.
          </p>
        </div>

        <!-- Recomendaciones de Inversión Estructuradas para Colombia -->
        <div>
          <h4 class="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3 flex items-center space-x-1.5">
            <span>💡</span>
            <span>Recomendaciones del Asesor Financiero de Confianza para Colombia</span>
          </h4>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5" id="cardsRecomendaciones">
            <!-- Recomendaciones inyectadas vía JS -->
          </div>
        </div>
      </div>

      <!-- BLOQUE 5: DICCIONARIO FINANCIERO DESPLEGABLE (LAS 5 FAMILIAS DE TÉRMINOS) -->
      <div class="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div class="flex items-center justify-between flex-wrap gap-2">
          <div>
            <span class="text-xs font-bold uppercase tracking-wider text-blue-400">Bloque 5 • Diccionario Financiero Integrado OED</span>
            <h3 class="text-base font-bold text-white">¿Tienes dudas con algún concepto? Consulta el Diccionario en Lenguaje Claro</h3>
            <p class="text-xs text-slate-400">Explicaciones cotidianas con ejemplos en pesos colombianos ($ COP) para las 5 familias de conceptos.</p>
          </div>
          <button type="button" onclick="toggleGlosario()" id="btnToggleGlosario" class="bg-slate-800 hover:bg-slate-700 text-slate-200 px-3.5 py-1.5 rounded-lg text-xs font-semibold border border-slate-700 transition">
            📖 Ver Diccionario Completo
          </button>
        </div>

        <div id="contenedorGlosario" class="space-y-4 pt-3 border-t border-slate-800 hidden">
          <div class="flex flex-wrap items-center gap-2">
            <input type="text" id="busquedaGlosario" oninput="filtrarGlosario()" placeholder="Buscar término (ej. CDT, VIS, UVT, ETF, Usura)..." class="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500">
            <select id="filtroFamiliaGlosario" onchange="filtrarGlosario()" class="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-300 focus:outline-none">
              <option value="TODAS">Todas las Familias (5)</option>
              <option value="Financiero e Inversión">1. Financiero e Inversión</option>
              <option value="Vivienda y Finca Raíz">2. Vivienda y Finca Raíz</option>
              <option value="Nómina e Impuestos">3. Nómina, Trabajo e Impuestos</option>
              <option value="Deudas y Leyes Protectoras">4. Deudas y Leyes Protectoras</option>
              <option value="Probabilidad y Futuro">5. Probabilidad y Futuro</option>
            </select>
          </div>
          <div id="gridGlosario" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5 max-h-[460px] overflow-y-auto pr-1">
            <!-- Tarjetas de Glosario inyectadas vía JS -->
          </div>
        </div>
      </div>

    </div>

    <!-- VISTA DICCIONARIO DIRECTO -->
    <div id="vista-diccionario" class="hidden space-y-6">
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <h2 class="text-xl font-bold text-white flex items-center space-x-2">
          <span>📘</span>
          <span>Diccionario Financiero OED — Las 5 Familias de Términos</span>
        </h2>
        <p class="text-xs text-slate-400 mt-1">Regla "Cero Palabras Huérfanas": cada término técnico cuenta con su explicación cercana y su ejemplo práctico en pesos colombianos.</p>
        <div class="mt-6" id="glosarioVistaDirecta">
          <!-- Se duplica el grid de glosario para consulta directa -->
        </div>
      </div>
    </div>

    <!-- VISTA CONSULTA INTEGRAL OED (6 MÓDULOS) -->
    <div id="vista-consulta" class="hidden space-y-6">
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div class="flex items-center justify-between flex-wrap gap-2">
          <div>
            <h2 class="text-xl font-bold text-white flex items-center space-x-2">
              <span>🚀</span>
              <span>Consulta Integral OED — Los 6 Módulos del Equipo</span>
            </h2>
            <p class="text-xs text-slate-400 mt-0.5">Ejecuta el pipeline completo de asesoría financiera local (Salin, Nidia, Catalina, Camilo, Jesi y Nelson).</p>
          </div>
          <button type="button" onclick="correrConsultaCompleta()" class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-4 py-2 rounded-lg text-xs shadow-lg shadow-blue-600/30 transition">
            ⚡ Ejecutar Consulta Integral
          </button>
        </div>
        <div id="loadingConsulta" class="hidden text-xs text-blue-400 py-6 text-center animate-pulse">
          Calculando diagnósticos de los 6 módulos bajo la normativa colombiana...
        </div>
        <div id="contenedorConsulta" class="hidden space-y-4 pt-3 border-t border-slate-800">
          <!-- Casos integrados inyectados vía JS -->
        </div>
      </div>
    </div>

    <!-- VISTA DETECTOR DE PIRÁMIDES (ART. 316 C.P.) -->
    <div id="vista-ponzi" class="hidden space-y-6">
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl max-w-2xl mx-auto space-y-5">
        <div>
          <span class="text-xs font-bold uppercase tracking-wider text-rose-400">Protección al Consumidor Financiero</span>
          <h2 class="text-xl font-bold text-white mt-0.5">Detector Matemático de Pirámides y Captación Ilegal</h2>
          <p class="text-xs text-slate-400 mt-1">Evalúa matemáticamente el colapso geométrico bajo el Artículo 316 del Código Penal Colombiano.</p>
        </div>
        <form onsubmit="evaluarPonzi(event)" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-slate-300">Rentabilidad mensual prometida (%)</label>
            <input type="number" id="inpTasaPonzi" value="15.0" step="0.5" min="1" class="mt-1 w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-rose-500 font-mono">
            <span class="text-[10px] text-slate-500 mt-0.5 block">Cualquier oferta por encima de la tasa de usura es altamente sospechosa.</span>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-300">Personas que exigen reclutar por ciclo</label>
            <input type="number" id="inpPersonasPonzi" value="3" min="2" max="10" class="mt-1 w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-rose-500 font-mono">
          </div>
          <button type="submit" class="w-full bg-rose-600 hover:bg-rose-500 text-white font-bold py-2.5 rounded-lg text-xs transition shadow-lg shadow-rose-600/30">
            🚨 Evaluar Esquema
          </button>
        </form>
        <div id="resultadoPonzi" class="hidden"></div>
      </div>
    </div>

    <!-- VISTA TRIVIAS COLOMBIANAS -->
    <div id="vista-trivias" class="hidden space-y-6">
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
        <div>
          <span class="text-xs font-bold uppercase tracking-wider text-emerald-400">Educación Financiera Lúdica</span>
          <h2 class="text-xl font-bold text-white mt-0.5">Trivias de Cultura Financiera y Normativa Colombiana</h2>
          <p class="text-xs text-slate-400 mt-1">Aprende sobre capitalización compuesta, seguro Fogafín, exención de 4x1000 y rentabilidad real frente a la inflación.</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4" id="triviasList">
          <!-- Trivias inyectadas vía JS -->
        </div>
      </div>
    </div>

  </main>

  <footer class="border-t border-slate-800 bg-slate-950/80 py-4 text-center text-xs text-slate-400">
    Asesor Financiero e Inversiones OED • Construido con Python, FastAPI y el Manual de Marca Oficial OED • 100% Local y Seguro
  </footer>

  <!-- ============================================================================== -->
  <!-- JAVASCRIPT DEL CLIENTE: CONSUMO DE ENDPOINTS Y REACTIVIDAD -->
  <!-- ============================================================================== -->
  <script>
    let glosarioOED = {};
    let catalogoActivos = {};

    function fmtCOP(val) {
      if (val === null || val === undefined) return "$0 COP";
      const num = Math.round(val);
      return "$" + num.toLocaleString("es-CO") + " COP";
    }

    function cambiarTab(tabId) {
      const tabs = ['mod6', 'diccionario', 'consulta', 'ponzi', 'trivias'];
      tabs.forEach(t => {
        const v = document.getElementById('vista-' + t);
        const b = document.getElementById('tab-' + t);
        if (v) v.classList.add('hidden');
        if (b) {
          b.className = 'px-4 py-2 text-xs sm:text-sm font-medium rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition';
        }
      });
      const targetVista = document.getElementById('vista-' + tabId);
      const targetBtn = document.getElementById('tab-' + tabId);
      if (targetVista) targetVista.classList.remove('hidden');
      if (targetBtn) {
        targetBtn.className = 'px-4 py-2 text-xs sm:text-sm font-semibold rounded-lg bg-blue-700 text-white transition shadow-lg shadow-blue-700/20';
      }
      if (tabId === 'diccionario') {
        renderGlosarioEnContenedor('glosarioVistaDirecta');
      }
    }

    async function init() {
      // 1. Cargar Cuestionario de Idoneidad SFC
      const resCuest = await fetch('/api/cuestionario-suitability');
      const preguntas = await resCuest.json();
      renderCuestionario(preguntas);

      // 2. Cargar Catálogo de Activos
      const resCat = await fetch('/api/catalogo-activos');
      catalogoActivos = await resCat.json();

      // 3. Cargar Glosario OED
      const resGlos = await fetch('/api/glosario-oed');
      glosarioOED = await resGlos.json();
      renderGlosarioEnContenedor('gridGlosario');

      // 4. Cargar Trivias
      const resTriv = await fetch('/api/trivias');
      const trivias = await resTriv.json();
      renderTrivias(trivias);

      // 5. Ejecutar Simulación Inicial
      await generarPortafolioRealista();
    }

    function renderCuestionario(preguntas) {
      const cont = document.getElementById('cuestionarioContainer');
      cont.innerHTML = preguntas.map((p, idx) => `
        <div class="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2.5 hover:border-slate-700 transition">
          <label class="block text-xs font-semibold text-slate-100 leading-snug">
            <span class="inline-flex items-center justify-center w-5 h-5 rounded-full bg-blue-900/60 text-blue-400 text-[11px] font-bold mr-1.5">${idx + 1}</span>
            <span>${p.pregunta || p.texto || 'Pregunta de Idoneidad'}</span>
          </label>
          <select id="p_${p.id}" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-blue-500 font-normal">
            ${p.opciones.map((opt, i) => `
              <option value="${i}" ${i === 2 ? 'selected' : ''}>${opt.texto} (${opt.puntaje !== undefined ? opt.puntaje : (opt.puntos !== undefined ? opt.puntos : '')} pts)</option>
            `).join('')}
          </select>
        </div>
      `).join('');
    }

    async function evaluarTestSFC() {
      const btn = document.getElementById('btnDiagnosticarSFC');
      const textoOrig = btn.innerHTML;
      btn.innerHTML = '<span>⏳</span><span>Evaluando...</span>';

      const inputs = document.querySelectorAll('[id^="p_"]');
      const respuestas = {};
      inputs.forEach(inp => {
        const id = inp.id.replace('p_', '');
        respuestas[id] = parseInt(inp.value);
      });

      const res = await fetch('/api/evaluar-suitability', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({respuestas})
      });
      const data = await res.json();

      document.getElementById('inpPerfilRiesgo').value = data.perfil_riesgo;

      const semaforo = document.getElementById('tarjetaSemaforo');
      const semPerfilBadge = document.getElementById('semPerfilBadge');
      const semTitulo = document.getElementById('semTitulo');
      const semExplicacion = document.getElementById('semExplicacion');

      semPerfilBadge.innerText = `Perfil: ${data.perfil_riesgo} (${data.puntaje_idoneidad_100}/100 pts)`;
      semTitulo.innerText = `Diagnóstico de Idoneidad SFC: Perfil ${data.perfil_riesgo}`;
      semExplicacion.innerHTML = data.dictamen_perfil;

      if (data.perfil_riesgo === 'Conservador') {
        semaforo.className = 'oed-doc-card oed-doc-azul';
      } else if (data.perfil_riesgo === 'Moderado') {
        semaforo.className = 'oed-doc-card oed-doc-verde';
      } else {
        semaforo.className = 'oed-doc-card oed-doc-ambar';
      }

      const alertaBox = document.getElementById('alertaConductualBox');
      const alertaTexto = document.getElementById('alertaConductualTexto');
      if (data.alerta_conductual_suitability) {
        alertaTexto.innerText = data.alerta_conductual_suitability;
        alertaBox.classList.remove('hidden');
      } else {
        alertaBox.classList.add('hidden');
      }

      await generarPortafolioRealista();
      btn.innerHTML = textoOrig;
    }

    async function generarPortafolioRealista() {
      const capacidad = parseFloat(document.getElementById('inpCapacidadMensual').value) || 1000000;
      const capital = parseFloat(document.getElementById('inpCapitalInicial').value) || 2000000;
      const azar = parseFloat(document.getElementById('inpGastoAzar').value) || 50000;
      const anios = parseInt(document.getElementById('inpAniosPortafolio').value) || 10;
      const perfil = document.getElementById('inpPerfilRiesgo').value || 'Moderado';

      const res = await fetch('/api/portafolio-realista', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          perfil_riesgo: perfil,
          capacidad_inversion_mensual_cop: capacidad,
          capital_inicial_cop: capital,
          horizonte_anios: anios,
          gasto_recreativo_azar_cop: azar
        })
      });
      const data = await res.json();

      // Actualizar 4 Métricas Clave
      document.getElementById('kpiCapacidadMensual').innerText = fmtCOP(data.capacidad_inversion_mensual_cop);
      document.getElementById('kpiAsignacionMacro').innerText = `${data.asignacion_macro.renta_fija_pct}% RF / ${data.asignacion_macro.renta_variable_pct}% RV`;
      document.getElementById('kpiTasaEA').innerText = `${data.tasa_ponderada_esperada_ea_pct}% EA`;
      document.getElementById('kpiPatrimonioFinal').innerText = fmtCOP(data.proyeccion_escenarios.esperado.patrimonio_final_cop);
      document.getElementById('kpiHorizonteSub').innerText = `A ${data.horizonte_anios} años (Esc. Esperado)`;

      // Actualizar Plan de Acción para este Mes
      document.getElementById('planAccionMesTexto').innerText = data.plan_de_accion_mes;

      // Actualizar Semáforo Diagnóstico
      if (data.diagnostico_asesor_confianza) {
        document.getElementById('semTitulo').innerText = data.diagnostico_asesor_confianza.titulo_claro;
        document.getElementById('semExplicacion').innerText = data.diagnostico_asesor_confianza.explicacion_humana;
      }

      // Tabla de Activos Detallada
      const tbody = document.getElementById('tablaActivosBody');
      tbody.innerHTML = data.distribucion_mensual_detalle.map(act => `
        <tr class="hover:bg-slate-800/40 transition">
          <td class="px-4 py-3 font-semibold text-white">${act.activo}</td>
          <td class="px-4 py-3 text-slate-300">${act.clase}</td>
          <td class="px-3 py-3 text-center font-bold text-blue-400">${act.porcentaje_pct}%</td>
          <td class="px-4 py-3 text-right font-mono font-semibold text-white">${fmtCOP(act.monto_mensual_cop)}</td>
          <td class="px-3 py-3 text-center font-semibold text-emerald-400">${act.tasa_ea_esperada_pct}% EA</td>
          <td class="px-4 py-3 text-[11px] text-slate-400">${obtenerFuenteActivo(act.activo)}</td>
        </tr>
      `).join('');

      // Cards de Proyección Tri-Escenario
      const escBox = document.getElementById('cardsEscenarios');
      const esc = data.proyeccion_escenarios;
      escBox.innerHTML = `
        <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-slate-400 uppercase">Escenario Pesimista</span>
            <span class="text-xs px-2 py-0.5 rounded font-mono bg-slate-800 text-slate-300">${esc.pesimista.tasa_ea_pct}% EA</span>
          </div>
          <div class="text-lg font-bold text-slate-200 mt-2">${fmtCOP(esc.pesimista.patrimonio_final_cop)}</div>
          <p class="text-[11px] text-slate-500 mt-1">Intereses: ${fmtCOP(esc.pesimista.intereses_ganados_cop)} (Aporte: ${fmtCOP(esc.pesimista.total_aportado_cop)})</p>
        </div>

        <div class="bg-slate-950 p-4 rounded-xl border-2 border-blue-600 shadow-lg shadow-blue-600/10">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-blue-400 uppercase">Escenario Esperado</span>
            <span class="text-xs px-2 py-0.5 rounded font-mono bg-blue-900/40 text-blue-300 font-bold">${esc.esperado.tasa_ea_pct}% EA</span>
          </div>
          <div class="text-xl font-black text-white mt-2">${fmtCOP(esc.esperado.patrimonio_final_cop)}</div>
          <p class="text-[11px] text-emerald-400 mt-1">Intereses Ganados: <strong>+${fmtCOP(esc.esperado.intereses_ganados_cop)}</strong></p>
        </div>

        <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-emerald-400 uppercase">Escenario Optimista</span>
            <span class="text-xs px-2 py-0.5 rounded font-mono bg-emerald-950 text-emerald-300">${esc.optimista.tasa_ea_pct}% EA</span>
          </div>
          <div class="text-lg font-bold text-white mt-2">${fmtCOP(esc.optimista.patrimonio_final_cop)}</div>
          <p class="text-[11px] text-slate-400 mt-1">Intereses: ${fmtCOP(esc.optimista.intereses_ganados_cop)} (Expansión bursátil)</p>
        </div>
      `;

      // Análisis de Ocio/Azar
      const ocio = data.analisis_recreativo_azar;
      const ocioTexto = document.getElementById('textoOcioAnalisis');
      const badgeOcio = document.getElementById('badgeOcioSaludable');
      ocioTexto.innerHTML = `
        Usted destina <strong>${fmtCOP(ocio.gasto_mensual_azar_cop)}/mes</strong> a apuestas/azar (${ocio.porcentaje_sobre_flujo_pct}% de su capacidad mensual).
        En ${data.horizonte_anios} años, ese desembolso sumará <strong>${fmtCOP(ocio.desembolso_acumulado_azar_cop)}</strong> con una pérdida matemática esperada de <strong>${fmtCOP(ocio.perdida_matematica_esperada_cop)}</strong>.
        Como su Asesor de Confianza, recomendamos tratarlo estrictamente como ocio controlado (tope máximo 5%), salvaguardando el 95%+ restante para su libertad financiera.
      `;
      if (ocio.porcentaje_sobre_flujo_pct <= 5.0) {
        badgeOcio.className = 'text-[11px] px-2.5 py-0.5 rounded-full font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30';
        badgeOcio.innerText = `Ocio Saludable (${ocio.porcentaje_sobre_flujo_pct}%)`;
      } else {
        badgeOcio.className = 'text-[11px] px-2.5 py-0.5 rounded-full font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30';
        badgeOcio.innerText = `Revisión Ocio (${ocio.porcentaje_sobre_flujo_pct}%)`;
      }

      // Recomendaciones Oficiales
      const recBox = document.getElementById('cardsRecomendaciones');
      recBox.innerHTML = data.recomendaciones_inversion.map(r => `
        <div class="bg-slate-950 p-3.5 rounded-xl border border-slate-800 space-y-1.5">
          <span class="text-xs font-bold text-blue-300 block">${r.titulo}</span>
          <p class="text-[11px] text-slate-400 leading-relaxed">${r.detalle}</p>
        </div>
      `).join('');
    }

    function obtenerFuenteActivo(nombreActivo) {
      if (nombreActivo.includes('CDT')) return 'SFC / Fogafín (Cobertura hasta $50M COP)';
      if (nombreActivo.includes('FIC')) return 'SFC / Boletín Fiduciarias D+0';
      if (nombreActivo.includes('TES')) return 'MinHacienda / Banco de la República';
      if (nombreActivo.includes('S&P 500')) return 'S&P Dow Jones / BVC Mercado Global';
      if (nombreActivo.includes('VT') || nombreActivo.includes('Global')) return 'Vanguard / BlackRock / BVC';
      if (nombreActivo.includes('HCOLSEL')) return 'BVC / MSCI Colcap';
      return 'BVC / FactSet / SFC';
    }

    function toggleGlosario() {
      const box = document.getElementById('contenedorGlosario');
      const btn = document.getElementById('btnToggleGlosario');
      if (box.classList.contains('hidden')) {
        box.classList.remove('hidden');
        btn.innerText = '✕ Ocultar Diccionario';
      } else {
        box.classList.add('hidden');
        btn.innerText = '📖 Ver Diccionario Completo';
      }
    }

    function renderGlosarioEnContenedor(contenedorId) {
      const cont = document.getElementById(contenedorId);
      if (!cont) return;
      const terms = Object.values(glosarioOED);
      cont.innerHTML = terms.map(t => `
        <div class="bg-slate-950 p-3.5 rounded-xl border border-slate-800 space-y-1.5">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-blue-300">${t.termino_tecnico}</span>
            <span class="text-[10px] px-2 py-0.5 rounded bg-slate-900 text-slate-400">${t.categoria}</span>
          </div>
          <p class="text-xs text-slate-300 leading-relaxed">${t.lenguaje_claro}</p>
          <div class="text-[11px] text-orange-300 bg-orange-950/20 p-2 rounded border border-orange-900/30">
            <strong>Ejemplo:</strong> ${t.ejemplo_cotidiano}
          </div>
        </div>
      `).join('');
    }

    function filtrarGlosario() {
      const query = (document.getElementById('busquedaGlosario').value || '').toLowerCase();
      const familia = document.getElementById('filtroFamiliaGlosario').value;
      const cont = document.getElementById('gridGlosario');

      const filtrados = Object.values(glosarioOED).filter(t => {
        const matchFamilia = (familia === 'TODAS' || t.categoria === familia);
        const matchQuery = !query ||
          t.termino_tecnico.toLowerCase().includes(query) ||
          t.lenguaje_claro.toLowerCase().includes(query) ||
          (t.alias && t.alias.some(a => a.toLowerCase().includes(query)));
        return matchFamilia && matchQuery;
      });

      cont.innerHTML = filtrados.map(t => `
        <div class="bg-slate-950 p-3.5 rounded-xl border border-slate-800 space-y-1.5">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-blue-300">${t.termino_tecnico}</span>
            <span class="text-[10px] px-2 py-0.5 rounded bg-slate-900 text-slate-400">${t.categoria}</span>
          </div>
          <p class="text-xs text-slate-300 leading-relaxed">${t.lenguaje_claro}</p>
          <div class="text-[11px] text-orange-300 bg-orange-950/20 p-2 rounded border border-orange-900/30">
            <strong>Ejemplo:</strong> ${t.ejemplo_cotidiano}
          </div>
        </div>
      `).join('');
    }

    async function evaluarPonzi(e) {
      if (e) e.preventDefault();
      const tasa = parseFloat(document.getElementById('inpTasaPonzi').value);
      const reclutados = parseInt(document.getElementById('inpPersonasPonzi').value);

      const res = await fetch('/api/detector-ponzi', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({rentabilidad_mensual_pct: tasa, personas_por_ciclo: reclutados})
      });
      const data = await res.json();

      const box = document.getElementById('resultadoPonzi');
      box.classList.remove('hidden');
      if (data.alerta_piramide) {
        box.className = 'mt-5 p-4 rounded-xl border border-rose-500/40 bg-rose-950/40 text-rose-200 text-xs space-y-2';
        box.innerHTML = `
          <div class="font-bold text-rose-400 text-sm">🚨 ¡ALERTA ROJA DE CAPTACIÓN ILEGAL!</div>
          <p>${data.advertencia_legal_sfc}</p>
          <div class="text-[11px] text-rose-300">En solo <strong>${data.ciclos_para_agotar_poblacion_colombia} niveles</strong> se necesitarían más de 39.5 millones de personas (toda la población adulta de Colombia).</div>
        `;
      } else {
        box.className = 'mt-5 p-4 rounded-xl border border-emerald-500/40 bg-emerald-950/40 text-emerald-200 text-xs';
        box.innerHTML = `<p>${data.advertencia_legal_sfc}</p>`;
      }
    }

    let listaTrivias = [];

    function renderTrivias(trivias) {
      listaTrivias = trivias;
      const list = document.getElementById('triviasList');
      list.innerHTML = trivias.map((t, idx) => `
        <div class="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-slate-200">${idx + 1}. ${t.pregunta}</span>
            <span id="badgeTrivia_${idx}" class="text-[10px] px-2 py-0.5 rounded font-mono bg-slate-900 text-slate-400">Sin responder</span>
          </div>
          <div class="space-y-1.5" id="opcionesTrivia_${idx}">
            ${t.opciones.map((opt, i) => `
              <button type="button" onclick="responderTrivia(${idx}, ${i})" id="btnTrivia_${idx}_${i}" class="w-full text-left text-xs p-2.5 rounded-lg border border-slate-800 bg-slate-900/60 text-slate-300 hover:border-blue-500 hover:text-white transition">
                <span class="font-bold text-slate-400 mr-1.5">${String.fromCharCode(65 + i)}.</span> ${opt}
              </button>
            `).join('')}
          </div>
          <div id="explicacionTrivia_${idx}" class="hidden text-[11px] p-2.5 rounded-lg border border-slate-800 bg-slate-900 text-slate-300 italic"></div>
        </div>
      `).join('');
    }

    function responderTrivia(triviaIdx, opcionIdx) {
      const t = listaTrivias[triviaIdx];
      const esCorrecto = (opcionIdx === t.respuesta_correcta_idx);

      t.opciones.forEach((_, i) => {
        const btn = document.getElementById(`btnTrivia_${triviaIdx}_${i}`);
        btn.disabled = true;
        if (i === t.respuesta_correcta_idx) {
          btn.className = 'w-full text-left text-xs p-2.5 rounded-lg border border-emerald-500/50 bg-emerald-950/40 text-emerald-300 font-medium';
        } else if (i === opcionIdx && !esCorrecto) {
          btn.className = 'w-full text-left text-xs p-2.5 rounded-lg border border-rose-500/50 bg-rose-950/40 text-rose-300 font-medium';
        } else {
          btn.className = 'w-full text-left text-xs p-2.5 rounded-lg border border-slate-800 bg-slate-950/30 text-slate-500 opacity-60';
        }
      });

      const badge = document.getElementById(`badgeTrivia_${triviaIdx}`);
      if (esCorrecto) {
        badge.className = 'text-[10px] px-2 py-0.5 rounded font-mono bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
        badge.innerText = '✓ Correcto';
      } else {
        badge.className = 'text-[10px] px-2 py-0.5 rounded font-mono bg-rose-500/20 text-rose-400 border border-rose-500/30';
        badge.innerText = '✗ Incorrecto';
      }

      const exp = document.getElementById(`explicacionTrivia_${triviaIdx}`);
      exp.innerHTML = `<span class="font-bold text-orange-400 not-italic">Normativa / Explicación:</span> ${t.explicacion}`;
      exp.classList.remove('hidden');
    }

    async function correrConsultaCompleta() {
      document.getElementById('loadingConsulta').classList.remove('hidden');
      document.getElementById('contenedorConsulta').classList.add('hidden');

      const res = await fetch('/api/caso-completo-oed', {method: 'POST'});
      const data = await res.json();

      document.getElementById('loadingConsulta').classList.add('hidden');
      const cont = document.getElementById('contenedorConsulta');
      cont.classList.remove('hidden');

      cont.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div class="bg-slate-950 p-4 rounded-xl border border-blue-900/60">
            <span class="text-xs font-bold text-blue-400 block uppercase">Paso 0 & 1: Salin Avellaneda (Módulo 6)</span>
            <p class="text-xs text-white font-semibold mt-1">Perfil: ${data.modulo6_salin.perfil.perfil_riesgo} (${data.modulo6_salin.perfil.puntaje_idoneidad_100}/100 pts)</p>
            <p class="text-[11px] text-slate-300 mt-1">Asignación: ${data.modulo6_salin.portafolio.asignacion_macro.renta_fija_pct}% Renta Fija / ${data.modulo6_salin.portafolio.asignacion_macro.renta_variable_pct}% Renta Variable</p>
            <p class="text-[11px] text-orange-300 mt-1">Patrimonio Proyectado 10a: ${fmtCOP(data.modulo6_salin.portafolio.proyeccion_escenarios.esperado.patrimonio_final_cop)}</p>
          </div>

          <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <span class="text-xs font-bold text-emerald-400 block uppercase">Paso 2: Nidia Velásquez (Módulo 1)</span>
            <p class="text-xs text-white font-semibold mt-1">Ingreso Neto: ${fmtCOP(data.modulo1_nidia.ingreso_neto_mensual_cop)}</p>
            <p class="text-[11px] text-slate-300 mt-1">Excedente Libre: ${fmtCOP(data.modulo1_nidia.excedente_mensual_cop)}</p>
            <p class="text-[11px] text-slate-400 mt-1">Fondo Emergencia: ${data.modulo1_nidia.meses_cobertura_fondo_emergencia} meses cubiertos</p>
          </div>

          <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <span class="text-xs font-bold text-purple-400 block uppercase">Paso 3: Catalina Moreno (Módulo 3)</span>
            <p class="text-xs text-white font-semibold mt-1">Estrategia: ${data.modulo3_catalina.estrategia_optima}</p>
            <p class="text-[11px] text-slate-300 mt-1">Ahorro Intereses: ${fmtCOP(data.modulo3_catalina.ahorro_intereses_cop)}</p>
            <p class="text-[11px] text-slate-400 mt-1">Índice Endeudamiento: ${data.modulo3_catalina.indice_endeudamiento_pct}%</p>
          </div>

          <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <span class="text-xs font-bold text-teal-400 block uppercase">Paso 4: Camilo Matson (Módulo 2)</span>
            <p class="text-xs text-white font-semibold mt-1">Patrimonio 5a: ${fmtCOP(data.modulo2_camilo.patrimonio_proyectado_nominal_cop)}</p>
            <p class="text-[11px] text-slate-300 mt-1">Vehículos: Bolsillos, CDT Digital, FIC y AFC</p>
          </div>

          <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <span class="text-xs font-bold text-amber-400 block uppercase">Paso 5: Jesi (Módulo 4)</span>
            <p class="text-xs text-white font-semibold mt-1">Inmueble $200M VIS: ${data.modulo4_jesi.cumple_ley_546_30pct ? 'Cumple Ley 546 (Tope 30%)' : 'Excede cuota'}</p>
            <p class="text-[11px] text-slate-300 mt-1">Primera cuota: ${fmtCOP(data.modulo4_jesi.primera_cuota_credito_cop)} (${data.modulo4_jesi.porcentaje_cuota_sobre_ingreso_pct}%)</p>
          </div>

          <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <span class="text-xs font-bold text-rose-400 block uppercase">Paso 6: Nelson Angel (Módulo 5)</span>
            <p class="text-xs text-white font-semibold mt-1">Decisión Hijos: ${data.modulo5_nelson.dictamen_viabilidad}</p>
            <p class="text-[11px] text-slate-300 mt-1">Éxito Monte Carlo: ${data.modulo5_nelson.probabilidad_exito_montecarlo_pct}% | VPA: ${fmtCOP(data.modulo5_nelson.vpa_decision_cop)}</p>
          </div>
        </div>
      `;
    }

    window.onload = init;
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(content=HTML_CONTENT)


if __name__ == "__main__":
    print("=" * 60)
    print("Iniciando Servidor Web Local - Asesor Financiero OED...")
    print("Manual de Marca: Voz de Asesor Financiero de Confianza")
    print("Abre tu navegador en: http://127.0.0.1:8000")
    print("=" * 60)
    uvicorn.run(app, host="127.0.0.1", port=8000)
