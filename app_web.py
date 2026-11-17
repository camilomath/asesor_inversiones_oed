"""
Servidor Web Local para el Asesor Financiero e Inversiones OED.
Desarrollado con FastAPI y Uvicorn.
Permite interactuar localmente con los 6 módulos del sistema.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# Importación de los módulos del proyecto
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

app = FastAPI(title="Asesor Financiero OED", description="Plataforma Local de Asesoría Financiera Colombiana")


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


class PresupuestoRequest(BaseModel):
    ingreso_bruto_mensual_cop: float = 6_500_000.0
    gastos_fijos_vitales_cop: float = 2_800_000.0
    gastos_variables_estilo_vida_cop: float = 950_000.0
    gastos_hormiga_mensual_cop: float = 320_000.0
    cuotas_deuda_mensual_cop: float = 600_000.0
    liquidez_actual_fondo_emergencia_cop: float = 9_000_000.0
    modalidad_laboral: str = "EMPLEADO_ORDINARIO"


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
    """Ejecuta la consulta médica financiera completa encadenada."""
    # Paso 0: Consentimiento
    cons = registrar_consentimiento_habeas_data("1032390306", True)

    # Paso 1: Salin (Módulo 6)
    perfil = evaluar_cuestionario_suitability_completo({
        "p1_horizonte": 2, "p2_reaccion_caida": 2, "p3_objetivo_inversion": 2,
        "p4_conocimiento_financiero": 2, "p5_dependencia_ingresos": 2,
        "p6_porcentaje_patrimonio": 1, "p7_fondo_emergencia": 2, "p8_educacion_tributaria": 2
    })
    azar = comparar_azar_vs_inversion_compuesta(200_000.0, 10, 0.11)

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
        "modulo6_salin": {"perfil": perfil, "azar": azar},
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
  <title>Asesor Financiero e Inversiones OED</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body { font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
  </style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen">
  <!-- Header -->
  <header class="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center font-bold text-slate-950 text-xl shadow-lg shadow-emerald-500/20">
          OED
        </div>
        <div>
          <h1 class="text-lg font-bold text-white tracking-tight">Asesor Financiero e Inversiones</h1>
          <p class="text-xs text-slate-400">Equipo OED • Simulación Médica Financiera Local</p>
        </div>
      </div>
      <div class="flex items-center space-x-2">
        <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          ● Modo Local Activo
        </span>
        <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20">
          Rama SALIN
        </span>
      </div>
    </div>
  </header>

  <!-- Navegación de Pestañas -->
  <div class="max-w-7xl mx-auto px-4 pt-6">
    <nav class="flex space-x-2 overflow-x-auto pb-2 border-b border-slate-800" id="tabBar">
      <button onclick="cambiarTab('mod6')" id="tab-mod6" class="px-4 py-2 text-sm font-semibold rounded-lg bg-emerald-600 text-white transition">
        🎲 Módulo 6: Salin (Riesgo y Azar)
      </button>
      <button onclick="cambiarTab('consulta')" id="tab-consulta" class="px-4 py-2 text-sm font-medium rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition">
        🩺 Consulta Médica Completa
      </button>
      <button onclick="cambiarTab('ponzi')" id="tab-ponzi" class="px-4 py-2 text-sm font-medium rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition">
        ⚠️ Detector de Pirámides
      </button>
      <button onclick="cambiarTab('trivias')" id="tab-trivias" class="px-4 py-2 text-sm font-medium rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition">
        🎓 Trivias Colombianas
      </button>
    </nav>
  </div>

  <!-- Contenedor Principal -->
  <main class="max-w-7xl mx-auto px-4 py-8">
    
    <!-- VISTA MÓDULO 6: SALIN -->
    <div id="vista-mod6" class="space-y-8">
      
      <!-- PASO 1: TEST DE IDONEIDAD SFC (Decreto 2555 de 2010) -->
      <div class="bg-slate-800/60 border border-slate-700/80 rounded-2xl p-6 shadow-xl">
        <div class="flex items-center justify-between mb-4 border-b border-slate-700/60 pb-3">
          <div>
            <div class="inline-flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20 mb-1">
              <span>Paso 1 de 2</span>
              <span>•</span>
              <span>Deber de Asesoría SFC</span>
            </div>
            <h2 class="text-base font-bold text-white flex items-center space-x-2">
              <span>📋</span>
              <span>Test de Idoneidad y Perfil de Riesgo (Decreto 2555 de 2010)</span>
            </h2>
            <p class="text-xs text-slate-400 mt-0.5">Determina su perfil regulatorio (Conservador, Moderado o Agresivo) y detecta inconsistencias conductuales.</p>
          </div>
          <button type="button" onclick="evaluarTestSFC()" id="btnDiagnosticarSFC" class="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-4 py-2 rounded-lg text-xs shadow-lg shadow-emerald-600/20 transition">
            📋 Diagnosticar Perfil de Riesgo
          </button>
        </div>

        <div id="cuestionarioContainer" class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Cuestionario inyectado vía JS -->
        </div>

        <!-- Resultado Idoneidad -->
        <div id="resultadoIdoneidad" class="mt-6 hidden bg-slate-950 border border-emerald-500/40 rounded-xl p-5 space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs uppercase tracking-wider text-slate-400">Resultado Oficial de Idoneidad SFC</span>
            <span id="resPerfilBadge" class="px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              Moderado
            </span>
          </div>
          <div class="text-sm text-slate-300" id="resDictamen"></div>
          <div id="resAlertaSuitability" class="hidden text-xs bg-amber-500/10 border border-amber-500/30 text-amber-300 p-3 rounded-lg"></div>
        </div>
      </div>

      <!-- PASO 2: CAPACIDAD FINANCIERA Y PORTAFOLIO REALISTA (RENTA FIJA VS RENTA VARIABLE) -->
      <div class="bg-slate-800/60 border border-slate-700/80 rounded-2xl p-6 shadow-xl space-y-6">
        <div>
          <div class="inline-flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-teal-400 bg-teal-500/10 px-2.5 py-0.5 rounded-full border border-teal-500/20 mb-1">
            <span>Paso 2 de 2</span>
            <span>•</span>
            <span>Estrategia de Asignación de Activos</span>
          </div>
          <h2 class="text-lg font-bold text-white flex items-center space-x-2">
            <span>💼</span>
            <span>Portafolio Realista: Renta Fija (CDTs/FICs/TES) y Renta Variable (ETFs y Acciones Libres)</span>
          </h2>
          <p class="text-xs text-slate-400 mt-1">Nadie apuesta todo: este modelo asigna su capacidad real de ahorro entre instrumentos regulados, dimensiona su ocio y genera recomendaciones de inversión accionables para Colombia.</p>
        </div>

        <!-- Grid de Parámetros y Macro Asignación -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Columna Inputs -->
          <div class="bg-slate-900/80 border border-slate-700/60 rounded-xl p-5 space-y-4">
            <h3 class="text-xs font-bold text-slate-200 uppercase tracking-wider">Parámetros Financieros</h3>

            <div>
              <label class="block text-xs font-semibold text-slate-300">Capacidad de Inversión Mensual (COP)</label>
              <input type="number" id="inpCapacidadMensual" value="1000000" step="50000" min="50000" class="mt-1 w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-teal-500 font-mono">
              <span class="text-[11px] text-slate-500">Aporte constante mensual sugerido</span>
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-300">Capital Inicial Disponible (COP)</label>
              <input type="number" id="inpCapitalInicial" value="2000000" step="100000" min="0" class="mt-1 w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-teal-500 font-mono">
              <span class="text-[11px] text-slate-500">Monto único al iniciar el portafolio</span>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-semibold text-slate-300">Horizonte</label>
                <select id="inpAniosPortafolio" class="mt-1 w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-2 text-xs text-white focus:outline-none focus:border-teal-500">
                  <option value="3">3 años</option>
                  <option value="5">5 años</option>
                  <option value="10" selected>10 años</option>
                  <option value="15">15 años</option>
                  <option value="20">20 años</option>
                </select>
              </div>

              <div>
                <label class="block text-xs font-semibold text-slate-300">Perfil de Riesgo</label>
                <select id="inpPerfilRiesgo" class="mt-1 w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-2 text-xs text-white focus:outline-none focus:border-teal-500 font-semibold">
                  <option value="Conservador">Conservador</option>
                  <option value="Moderado" selected>Moderado</option>
                  <option value="Agresivo">Agresivo</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-300">Gasto Recreativo en Azar/Apuestas (COP/mes)</label>
              <input type="number" id="inpOcioAzar" value="50000" step="10000" min="0" class="mt-1 w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-teal-500 font-mono">
              <span class="text-[11px] text-slate-500">Ocio controlado (máx. 2-5% del presupuesto)</span>
            </div>

            <button type="button" onclick="generarPortafolioRealista()" id="btnGenerarPortafolio" class="w-full bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-500 hover:to-emerald-500 text-white font-bold py-2.5 rounded-lg text-xs shadow-lg shadow-teal-500/20 transition">
              🚀 Generar Escenarios y Recomendaciones
            </button>
            <div id="statusPortafolio" class="hidden text-xs text-center font-medium text-teal-400 mt-2 bg-teal-500/10 border border-teal-500/20 py-1.5 px-3 rounded-lg"></div>
          </div>

          <!-- Columna Resultados Macro y Escenarios -->
          <div class="lg:col-span-2 space-y-4">
            <!-- Macro Tarjetas -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div class="bg-blue-950/40 border border-blue-800/50 rounded-xl p-4">
                <div class="flex items-center justify-between">
                  <span class="text-xs font-bold text-blue-300 uppercase tracking-wider">Renta Fija</span>
                  <span id="lblMacroRentaFijaPct" class="text-xs px-2 py-0.5 rounded font-mono font-bold bg-blue-500/20 text-blue-300">55%</span>
                </div>
                <div id="lblMacroRentaFijaCOP" class="text-lg font-extrabold text-blue-400 mt-1">$550,000 COP/mes</div>
                <p class="text-[11px] text-blue-200/70 mt-1">CDTs Digitales, FICs Liquidez y Bonos TES</p>
              </div>

              <div class="bg-purple-950/40 border border-purple-800/50 rounded-xl p-4">
                <div class="flex items-center justify-between">
                  <span class="text-xs font-bold text-purple-300 uppercase tracking-wider">Renta Variable</span>
                  <span id="lblMacroRentaVariablePct" class="text-xs px-2 py-0.5 rounded font-mono font-bold bg-purple-500/20 text-purple-300">45%</span>
                </div>
                <div id="lblMacroRentaVariableCOP" class="text-lg font-extrabold text-purple-400 mt-1">$450,000 COP/mes</div>
                <p class="text-[11px] text-purple-200/70 mt-1">ETFs S&P 500 (CSPX/VOO), HCOLSEL y Acciones</p>
              </div>

              <div class="bg-emerald-950/40 border border-emerald-800/50 rounded-xl p-4">
                <div class="flex items-center justify-between">
                  <span class="text-xs font-bold text-emerald-300 uppercase tracking-wider">Tasa Ponderada</span>
                  <span id="lblMacroTasaPonderada" class="text-xs px-2 py-0.5 rounded font-mono font-bold bg-emerald-500/20 text-emerald-300">11.45% EA</span>
                </div>
                <div id="lblMacroPatrimonioEsperado" class="text-lg font-extrabold text-emerald-400 mt-1">$221,528,652 COP</div>
                <p class="text-[11px] text-emerald-200/70 mt-1">Patrimonio proyectado a <span id="lblMacroAnios" class="font-bold">10</span> años</p>
              </div>
            </div>

            <!-- Escenarios Proyectados (Pesimista, Esperado, Optimista) -->
            <div class="bg-slate-900/80 border border-slate-700/60 rounded-xl p-4">
              <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">Escenarios Proyectados de Crecimiento Compuesto</h4>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                <div class="bg-slate-950 p-3 rounded-lg border border-slate-800">
                  <span class="text-slate-400 block font-medium">Escenario Pesimista (<span id="lblTasaPesimista">8.0% EA</span>)</span>
                  <span id="lblPatrimonioPesimista" class="text-sm font-bold text-slate-200 font-mono block mt-1">$175,412,000 COP</span>
                  <span class="text-[11px] text-slate-500">Mercados bajistas o inflación elevada</span>
                </div>
                <div class="bg-slate-950 p-3 rounded-lg border border-emerald-500/40">
                  <span class="text-emerald-400 block font-bold">Escenario Esperado (<span id="lblTasaEsperada">11.5% EA</span>)</span>
                  <span id="lblPatrimonioEsperadoTab" class="text-sm font-extrabold text-emerald-400 font-mono block mt-1">$221,528,652 COP</span>
                  <span class="text-[11px] text-emerald-300/70">Rendimiento histórico ponderado</span>
                </div>
                <div class="bg-slate-950 p-3 rounded-lg border border-slate-800">
                  <span class="text-teal-400 block font-medium">Escenario Optimista (<span id="lblTasaOptimista">15.0% EA</span>)</span>
                  <span id="lblPatrimonioOptimista" class="text-sm font-bold text-teal-300 font-mono block mt-1">$284,150,000 COP</span>
                  <span class="text-[11px] text-slate-500">Expansión bursátil y dividendos altos</span>
                </div>
              </div>
            </div>

            <!-- Análisis de Ocio / Azar Realista -->
            <div id="boxAnalisisOcio" class="bg-slate-900/80 border border-slate-700/60 rounded-xl p-4 text-xs space-y-1">
              <div class="flex items-center justify-between">
                <span class="font-bold text-amber-400">⚖️ Dimensión Realista del Ocio / Rifas / Apuestas</span>
                <span id="lblPctAzarFlujo" class="font-mono text-amber-300 font-bold">4.8% del flujo mensual</span>
              </div>
              <p class="text-slate-300" id="lblDetalleOcioAzar">
                Usted destina $50.000 COP/mes a entretenimiento en azar. El <strong>95.2% restante ($1.000.000 COP/mes)</strong> va a su portafolio patrimonial regulado.
                Esto demuestra que no se necesita prohibir el ocio, sino calibrarlo estrictamente como presupuesto recreativo sin poner en riesgo la libertad financiera.
              </p>
            </div>
          </div>
        </div>

        <!-- Tabla Detallada de Instrumentos y Fuentes Oficiales -->
        <div class="bg-slate-900/80 border border-slate-700/60 rounded-xl p-4">
          <div class="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
            <div>
              <h4 class="text-xs font-bold text-white uppercase tracking-wider">Desglose Detallado de Instrumentos y Fuentes Oficiales Aproximadas</h4>
              <p class="text-[11px] text-slate-400">Renta Fija garantizada y Renta Variable con ETFs indexados y acciones libres</p>
            </div>
            <span class="text-[10px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded font-mono">Regulación SFC / BVC</span>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-xs text-left">
              <thead class="text-slate-400 border-b border-slate-800">
                <tr>
                  <th class="py-2 px-2">Instrumento / Vehículo</th>
                  <th class="py-2 px-2">Clase</th>
                  <th class="py-2 px-2">% Asignado</th>
                  <th class="py-2 px-2">Aporte Mensual</th>
                  <th class="py-2 px-2">Tasa Estimada EA</th>
                  <th class="py-2 px-2">Fuente Oficial Aproximada</th>
                </tr>
              </thead>
              <tbody id="tbodyPortafolioDetalle" class="divide-y divide-slate-800 text-slate-300">
                <!-- Inyectado vía JS -->
              </tbody>
            </table>
          </div>
        </div>

        <!-- Recomendaciones de Inversión Finales -->
        <div class="bg-slate-900/80 border border-slate-700/60 rounded-xl p-5 space-y-4">
          <h4 class="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center space-x-1.5">
            <span>💡</span>
            <span>Recomendaciones Finales de Inversión (Normativa y Ejecución Práctica en Colombia)</span>
          </h4>
          <div id="gridRecomendaciones" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            <!-- Inyectado vía JS -->
          </div>
        </div>
      </div>

      <!-- HERRAMIENTA COMPLEMENTARIA: LABORATORIO AZAR VS INVERSIÓN -->
      <div class="bg-slate-800/40 border border-slate-700/60 rounded-2xl p-6 shadow-xl space-y-6">
        <div class="border-b border-slate-700/60 pb-3 flex items-center justify-between">
          <div>
            <h3 class="text-sm font-bold text-slate-200 flex items-center space-x-2">
              <span>🎲</span>
              <span>Laboratorio Complementario: Azar vs. Interés Compuesto (Baloto y Chance)</span>
            </h3>
            <p class="text-xs text-slate-400">Demostración matemática del Valor Esperado E[X] negativo de rifas y apuestas frente a la inversión legal.</p>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div class="bg-slate-900/80 border border-slate-700/80 rounded-xl p-5 space-y-4">
            <form id="formAzar" onsubmit="event.preventDefault(); calcularAzar(); return false;" class="space-y-4">
              <div>
                <label class="block text-xs font-semibold text-slate-300">Gasto Mensual en Azar/Apuestas (COP)</label>
                <input type="number" id="inpMontoAzar" value="200000" step="10000" min="10000" class="mt-1 w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500 font-mono">
                <span class="text-[11px] text-slate-500">Ejemplo: $50.000 COP semanales = $200.000 COP/mes</span>
              </div>

              <div>
                <label class="block text-xs font-semibold text-slate-300">Horizonte de Tiempo</label>
                <select id="inpAniosAzar" class="mt-1 w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500">
                  <option value="3">3 años (36 meses)</option>
                  <option value="5">5 años (60 meses)</option>
                  <option value="10" selected>10 años (120 meses)</option>
                  <option value="15">15 años (180 meses)</option>
                </select>
              </div>

              <div>
                <label class="block text-xs font-semibold text-slate-300">Rentabilidad Estimada Inversión Regulada</label>
                <input type="number" id="inpTasaAzar" value="11.0" step="0.5" class="mt-1 w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500 font-mono">
                <span class="text-[11px] text-slate-500">Tasa Efectiva Anual (EA) de portafolio</span>
              </div>

              <button type="button" onclick="calcularAzar()" id="btnCalcularAzar" class="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold py-2 rounded-lg text-xs shadow-lg shadow-emerald-500/20 transition">
                🎲 Calcular Comparativa
              </button>
              <div id="statusCalculoAzar" class="hidden text-xs text-center font-medium text-emerald-400 mt-2 bg-emerald-500/10 border border-emerald-500/20 py-1 px-2 rounded-lg"></div>
            </form>
          </div>

          <!-- Resultados Azar -->
          <div class="lg:col-span-2 space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div class="bg-rose-950/30 border border-rose-900/50 rounded-xl p-3">
                <span class="text-xs font-semibold text-rose-300 uppercase tracking-wider block">Juegos de Azar (E[X])</span>
                <span id="lblAzar" class="text-base font-bold text-rose-400 mt-1 block">$11,520,000 COP</span>
                <p class="text-[11px] text-rose-300/70 mt-1">Pérdida esperada: <span id="lblPerdidaAzar" class="font-bold">-$12,480,000 COP</span></p>
              </div>

              <div class="bg-blue-950/30 border border-blue-900/50 rounded-xl p-3">
                <span class="text-xs font-semibold text-blue-300 uppercase tracking-wider block">Capital Desembolsado</span>
                <span id="lblCapital" class="text-base font-bold text-blue-400 mt-1 block">$24,000,000 COP</span>
                <p class="text-[11px] text-blue-300/70 mt-1">Total aportado a <span id="lblAnios">10</span> años</p>
              </div>

              <div class="bg-emerald-950/30 border border-emerald-900/50 rounded-xl p-3">
                <span class="text-xs font-semibold text-emerald-300 uppercase tracking-wider block">Inversión Regulada SFC</span>
                <span id="lblInversion" class="text-base font-bold text-emerald-400 mt-1 block">$42,485,950 COP</span>
                <p class="text-[11px] text-emerald-300/70 mt-1">Brecha a favor: <span id="lblBrecha" class="font-bold text-emerald-300">+$30,965,950 COP</span></p>
              </div>
            </div>

            <!-- Tabla de Trayectoria Anual Dinámica -->
            <div class="bg-slate-900/80 rounded-xl p-4 border border-slate-700/50">
              <div class="flex items-center justify-between mb-2">
                <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider">Evolución Anual: Desembolso vs. Inversión Regulada</h4>
                <span id="lblBadgeTrayectoria" class="text-[10px] text-emerald-400 font-mono bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">Dinámico</span>
              </div>
              <div class="overflow-x-auto">
                <table class="w-full text-xs text-left">
                  <thead class="text-slate-400 border-b border-slate-800">
                    <tr>
                      <th class="py-1.5 px-2">Año</th>
                      <th class="py-1.5 px-2">Total Aportado</th>
                      <th class="py-1.5 px-2 text-rose-400">Pérdida Azar E[X]</th>
                      <th class="py-1.5 px-2 text-emerald-400">Inversión SFC</th>
                      <th class="py-1.5 px-2 text-right text-emerald-300 font-bold">Brecha Ganada</th>
                    </tr>
                  </thead>
                  <tbody id="tbodyTrayectoria" class="divide-y divide-slate-800/80 text-slate-300 font-mono">
                    <!-- Inyectado dinámicamente por JS -->
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- VISTA CONSULTA MÉDICA COMPLETA -->
    <div id="vista-consulta" class="hidden space-y-6">
      <div class="bg-slate-800/60 border border-slate-700/80 rounded-2xl p-6 shadow-xl">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-lg font-bold text-white">Consulta Médica Financiera OED (Flujo de Principio a Fin)</h2>
            <p class="text-xs text-slate-400">Ejecuta de forma secuencial los 6 módulos construidos por el equipo.</p>
          </div>
          <button onclick="correrConsultaCompleta()" class="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold px-5 py-2.5 rounded-xl text-sm shadow-lg shadow-emerald-500/20 transition">
            ▶️ Ejecutar Consulta Completa
          </button>
        </div>

        <div id="loadingConsulta" class="hidden py-8 text-center text-slate-400 text-sm">
          ⏳ Ejecutando flujo transversal e integrando módulos...
        </div>

        <div id="contenedorConsulta" class="hidden space-y-4 mt-6">
          <!-- Tarjetas de cada módulo inyectadas por JS -->
        </div>
      </div>
    </div>

    <!-- VISTA DETECTOR DE PIRÁMIDES -->
    <div id="vista-ponzi" class="hidden space-y-6">
      <div class="bg-slate-800/60 border border-slate-700/80 rounded-2xl p-6 shadow-xl max-w-2xl mx-auto">
        <h2 class="text-base font-bold text-rose-400 flex items-center space-x-2">
          <span>⚠️</span>
          <span>Detector de Captación Ilegal y Esquemas Ponzi (Art. 316 C.P.)</span>
        </h2>
        <p class="text-xs text-slate-400 mt-1">Evalúa una promesa de rentabilidad para comprobar si colapsa matemáticamente.</p>

        <form id="formPonzi" onsubmit="event.preventDefault(); evaluarPonzi(); return false;" class="mt-6 space-y-4">
          <div>
            <label class="block text-xs font-semibold text-slate-300">Rentabilidad Mensual Prometida (%)</label>
            <input type="number" id="inpTasaPonzi" value="10.0" step="0.5" min="1" class="mt-1 w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-rose-500">
            <span class="text-[11px] text-slate-500">Ejemplo: 10% mensual "sin riesgo"</span>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-300">Personas que cada miembro debe reclutar</label>
            <input type="number" id="inpPersonasPonzi" value="3" min="2" max="10" class="mt-1 w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-rose-500">
          </div>

          <button type="button" onclick="evaluarPonzi()" id="btnEvaluarPonzi" class="w-full bg-rose-600 hover:bg-rose-500 text-white font-semibold py-2.5 rounded-lg text-sm shadow-lg shadow-rose-600/20 transition">
            ⚠️ Analizar Viabilidad Matemática
          </button>
        </form>

        <div id="resultadoPonzi" class="mt-6 hidden p-4 rounded-xl border">
          <!-- Inyectado por JS -->
        </div>
      </div>
    </div>

    <!-- VISTA TRIVIAS -->
    <div id="vista-trivias" class="hidden space-y-6">
      <div class="bg-slate-800/60 border border-slate-700/80 rounded-2xl p-6 shadow-xl max-w-3xl mx-auto">
        <h2 class="text-base font-bold text-amber-400 flex items-center space-x-2">
          <span>🎓</span>
          <span>Banco de Trivias de Cultura Financiera Colombiana</span>
        </h2>
        <p class="text-xs text-slate-400 mt-1">Aprende sobre la Circular Básica Jurídica SFC, Fogafín, el 4x1000 y la inflación IPC.</p>

        <div id="triviasList" class="mt-6 space-y-4">
          <!-- Inyectado por JS -->
        </div>
      </div>
    </div>

  </main>

  <script>
    let cuestionarioData = [];

    async function init() {
      // Cargar cuestionario de idoneidad
      const resp = await fetch('/api/cuestionario-suitability');
      cuestionarioData = await resp.json();
      renderCuestionario();

      // Cargar trivias
      const rTrivias = await fetch('/api/trivias');
      const trivias = await rTrivias.json();
      renderTrivias(trivias);

      // Generar portafolio realista y comparativa inicial
      await generarPortafolioRealista();
      await calcularAzar();
    }

    function cambiarTab(tab) {
      ['mod6', 'consulta', 'ponzi', 'trivias'].forEach(t => {
        document.getElementById(`vista-${t}`).classList.add('hidden');
        document.getElementById(`tab-${t}`).className = 'px-4 py-2 text-sm font-medium rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition';
      });
      document.getElementById(`vista-${tab}`).classList.remove('hidden');
      document.getElementById(`tab-${tab}`).className = 'px-4 py-2 text-sm font-semibold rounded-lg bg-emerald-600 text-white transition';
    }

    function renderCuestionario() {
      const c = document.getElementById('cuestionarioContainer');
      c.innerHTML = cuestionarioData.map((p, idx) => `
        <div class="bg-slate-900/80 border border-slate-700/60 rounded-xl p-4">
          <label class="block text-xs font-bold text-slate-200 mb-2">
            ${idx + 1}. ${p.pregunta}
          </label>
          <select id="sel_${p.id}" class="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-emerald-500">
            ${p.opciones.map((opt, i) => `<option value="${i}" ${i === 2 ? 'selected' : ''}>${opt.texto}</option>`).join('')}
          </select>
        </div>
      `).join('');
    }

    async function calcularAzar(e) {
      if (e) {
        e.preventDefault();
        e.stopPropagation();
      }
      const btn = document.getElementById('btnCalcularAzar');
      const statusBox = document.getElementById('statusCalculoAzar');
      const monto = parseFloat(document.getElementById('inpMontoAzar').value) || 200000;
      const anios = parseInt(document.getElementById('inpAniosAzar').value) || 10;
      const tasa = (parseFloat(document.getElementById('inpTasaAzar').value) || 11.0) / 100.0;

      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '⏳ Calculando proyección...';
      }

      try {
        const res = await fetch('/api/azar-vs-inversion', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({gasto_mensual_cop: monto, horizonte_anios: anios, tasa_ea: tasa})
        });

        if (!res.ok) throw new Error('Error en el servidor: ' + res.status);
        const data = await res.json();
        const r = data.resumen;
        const tray = data.trayectoria || [];

        document.getElementById('lblAnios').innerText = r.horizonte_anios;
        document.getElementById('lblTotalDesembolsado').innerText = '$' + Math.round(r.total_desembolsado_cop).toLocaleString('es-CO') + ' COP';
        document.getElementById('lblBrecha').innerText = '+$' + Math.round(r.brecha_riqueza_inversion_vs_azar_cop).toLocaleString('es-CO') + ' COP';
        document.getElementById('lblAzar').innerText = '$' + Math.round(r.valor_esperado_azar_cop).toLocaleString('es-CO') + ' COP';
        document.getElementById('lblPerdidaAzar').innerText = '-$' + Math.round(r.perdida_matematica_esperada_azar_cop).toLocaleString('es-CO') + ' COP';
        document.getElementById('lblCapital').innerText = '$' + Math.round(r.total_desembolsado_cop).toLocaleString('es-CO') + ' COP';
        document.getElementById('lblInversion').innerText = '$' + Math.round(r.patrimonio_inversion_compuesta_cop).toLocaleString('es-CO') + ' COP';
        document.getElementById('lblIntereses').innerText = '+$' + Math.round(r.ganancia_intereses_compuestos_cop).toLocaleString('es-CO') + ' COP';
        document.getElementById('lblBaloto').innerText = r.probabilidad_combinatoria_baloto;
        document.getElementById('lblChance').innerText = r.probabilidad_chance_4_cifras;

        // Render trayectoria anualizada
        const tbody = document.getElementById('tbodyTrayectoria');
        if (tbody && tray.length > 0) {
          const hitos = tray.filter(t => t.mes % 12 === 0);
          tbody.innerHTML = hitos.map(h => `
            <tr class="hover:bg-slate-800/50 transition">
              <td class="py-2.5 px-2 font-bold text-white">Año ${h.anio}</td>
              <td class="py-2.5 px-2 text-slate-300">$${Math.round(h.total_aportado_cop).toLocaleString('es-CO')}</td>
              <td class="py-2.5 px-2 text-rose-400">-$${Math.round(h.perdida_esperada_azar_cop).toLocaleString('es-CO')}</td>
              <td class="py-2.5 px-2 text-emerald-400 font-semibold">$${Math.round(h.saldo_inversion_cop).toLocaleString('es-CO')}</td>
              <td class="py-2.5 px-2 text-right text-emerald-300 font-bold">+$${Math.round(h.brecha_patrimonial_cop).toLocaleString('es-CO')}</td>
            </tr>
          `).join('');
        }

        if (statusBox) {
          statusBox.innerText = `✓ Proyección actualizada: $${Math.round(monto).toLocaleString('es-CO')} COP/mes a ${anios} años (${(tasa*100).toFixed(1)}% EA)`;
          statusBox.className = 'text-xs text-center font-medium text-emerald-400 mt-2 bg-emerald-500/10 border border-emerald-500/20 py-1.5 px-3 rounded-lg block';
          setTimeout(() => {
            statusBox.className = 'hidden text-xs text-center font-medium text-emerald-400 mt-2 bg-emerald-500/10 border border-emerald-500/20 py-1.5 px-3 rounded-lg';
          }, 3500);
        }

        if (btn) {
          btn.innerHTML = '✓ ¡Comparativa Actualizada!';
          btn.className = 'w-full bg-emerald-500 hover:bg-emerald-400 text-white font-bold py-2.5 rounded-lg text-sm shadow-lg shadow-emerald-500/30 transition';
          setTimeout(() => {
            btn.innerHTML = '🎲 Calcular Comparativa';
            btn.className = 'w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold py-2.5 rounded-lg text-sm shadow-lg shadow-emerald-500/20 transition';
            btn.disabled = false;
          }, 1500);
        }
      } catch (err) {
        console.error("Error al calcular azar:", err);
        if (statusBox) {
          statusBox.innerText = '❌ Error al calcular: ' + err.message;
          statusBox.className = 'text-xs text-center font-medium text-rose-400 mt-2 bg-rose-500/10 border border-rose-500/20 py-1.5 px-3 rounded-lg block';
        }
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = '🎲 Calcular Comparativa';
        }
      }
    }

    async function evaluarTestSFC() {
      const btn = document.getElementById('btnDiagnosticarSFC');
      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '⏳ Diagnosticando...';
      }

      const respuestas = {};
      cuestionarioData.forEach(p => {
        respuestas[p.id] = parseInt(document.getElementById(`sel_${p.id}`).value);
      });

      try {
        const res = await fetch('/api/evaluar-suitability', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({respuestas})
        });
        const diag = await res.json();

        const box = document.getElementById('resultadoIdoneidad');
        box.classList.remove('hidden');
        document.getElementById('resPerfilBadge').innerText = diag.perfil_riesgo + ' (' + diag.puntaje_idoneidad_100 + '/100)';
        document.getElementById('resDictamen').innerText = diag.recomendacion_normativa;

        const alerta = document.getElementById('resAlertaSuitability');
        if (diag.alerta_conductual_suitability) {
          alerta.innerText = diag.alerta_conductual_suitability;
          alerta.classList.remove('hidden');
        } else {
          alerta.classList.add('hidden');
        }

        // Sincronizar con el selector del portafolio realista y recalcular
        const selPerfil = document.getElementById('inpPerfilRiesgo');
        if (selPerfil) {
          selPerfil.value = diag.perfil_riesgo;
        }
        await generarPortafolioRealista();

        if (btn) {
          btn.innerHTML = '✓ ¡Perfil Asignado!';
          btn.className = 'bg-emerald-500 text-white font-semibold px-4 py-2 rounded-lg text-xs shadow-lg transition';
          setTimeout(() => {
            btn.innerHTML = '📋 Diagnosticar Perfil de Riesgo';
            btn.className = 'bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-4 py-2 rounded-lg text-xs shadow-lg shadow-emerald-600/20 transition';
            btn.disabled = false;
          }, 1500);
        }
      } catch (err) {
        console.error("Error al diagnosticar perfil:", err);
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = '📋 Diagnosticar Perfil de Riesgo';
        }
      }
    }

    async function generarPortafolioRealista() {
      const btn = document.getElementById('btnGenerarPortafolio');
      const statusBox = document.getElementById('statusPortafolio');
      const capacidad = parseFloat(document.getElementById('inpCapacidadMensual').value) || 1000000;
      const capital = parseFloat(document.getElementById('inpCapitalInicial').value) || 0;
      const anios = parseInt(document.getElementById('inpAniosPortafolio').value) || 10;
      const ocio = parseFloat(document.getElementById('inpOcioAzar').value) || 0;
      const perfil = document.getElementById('inpPerfilRiesgo').value || 'Moderado';

      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '⏳ Construyendo Portafolio...';
      }

      try {
        const res = await fetch('/api/portafolio-realista', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            perfil_riesgo: perfil,
            capacidad_inversion_mensual_cop: capacidad,
            capital_inicial_cop: capital,
            horizonte_anios: anios,
            gasto_recreativo_azar_cop: ocio
          })
        });

        if (!res.ok) throw new Error('Error HTTP ' + res.status);
        const data = await res.json();

        // Macro Cards
        document.getElementById('lblMacroRentaFijaPct').innerText = data.asignacion_macro.renta_fija_pct + '%';
        document.getElementById('lblMacroRentaFijaCOP').innerText = '$' + Math.round(data.asignacion_macro.monto_mensual_renta_fija_cop).toLocaleString('es-CO') + ' COP/mes';
        document.getElementById('lblMacroRentaVariablePct').innerText = data.asignacion_macro.renta_variable_pct + '%';
        document.getElementById('lblMacroRentaVariableCOP').innerText = '$' + Math.round(data.asignacion_macro.monto_mensual_renta_variable_cop).toLocaleString('es-CO') + ' COP/mes';
        document.getElementById('lblMacroTasaPonderada').innerText = data.tasa_ponderada_esperada_ea_pct + '% EA';
        document.getElementById('lblMacroPatrimonioEsperado').innerText = '$' + Math.round(data.proyeccion_escenarios.esperado.patrimonio_final_cop).toLocaleString('es-CO') + ' COP';
        document.getElementById('lblMacroAnios').innerText = data.horizonte_anios;

        // Escenarios
        document.getElementById('lblTasaPesimista').innerText = data.proyeccion_escenarios.pesimista.tasa_ea_pct + '% EA';
        document.getElementById('lblPatrimonioPesimista').innerText = '$' + Math.round(data.proyeccion_escenarios.pesimista.patrimonio_final_cop).toLocaleString('es-CO') + ' COP';
        document.getElementById('lblTasaEsperada').innerText = data.proyeccion_escenarios.esperado.tasa_ea_pct + '% EA';
        document.getElementById('lblPatrimonioEsperadoTab').innerText = '$' + Math.round(data.proyeccion_escenarios.esperado.patrimonio_final_cop).toLocaleString('es-CO') + ' COP';
        document.getElementById('lblTasaOptimista').innerText = data.proyeccion_escenarios.optimista.tasa_ea_pct + '% EA';
        document.getElementById('lblPatrimonioOptimista').innerText = '$' + Math.round(data.proyeccion_escenarios.optimista.patrimonio_final_cop).toLocaleString('es-CO') + ' COP';

        // Análisis Ocio / Azar
        const o = data.analisis_recreativo_azar;
        document.getElementById('lblPctAzarFlujo').innerText = o.porcentaje_sobre_flujo_pct + '% del flujo mensual';
        document.getElementById('lblDetalleOcioAzar').innerHTML = `
          Usted destina $${Math.round(o.gasto_mensual_azar_cop).toLocaleString('es-CO')} COP/mes a entretenimiento en azar (${o.porcentaje_sobre_flujo_pct}% del flujo).
          El <strong>${(100 - o.porcentaje_sobre_flujo_pct).toFixed(1)}% restante ($${Math.round(capacidad).toLocaleString('es-CO')} COP/mes)</strong> va a su portafolio regulado.
          En ${anios} años, el azar sumará $${Math.round(o.desembolso_acumulado_azar_cop).toLocaleString('es-CO')} COP (pérdida esperada E[X]: -$${Math.round(o.perdida_matematica_esperada_cop).toLocaleString('es-CO')} COP),
          mientras que su inversión regulada alcanzará <strong>$${Math.round(data.proyeccion_escenarios.esperado.patrimonio_final_cop).toLocaleString('es-CO')} COP</strong>.
        `;

        // Tabla Detallada de Activos
        const fuentesMap = {
          "CDTs": "SFC - Tasas Semanales Captación CDT / FOGAFÍN (hasta $50M)",
          "FICs": "SFC - Boletín Diario Fiduciarias (D+0 / D+1)",
          "TES": "Banco de la República / MinHacienda (Deuda Soberana)",
          "S&P 500": "S&P Dow Jones / BVC Mercado Global Colombiano (CSPX/VOO)",
          "Emergente": "Vanguard / MSCI ACWI (VT / EIMI)",
          "HCOLSEL": "BVC - Índice MSCI Colcap (HCOLSEL - Dividendo ~8%)",
          "Acciones": "BVC / Trii - Dividendos y Valorización Corporativa"
        };

        const tbody = document.getElementById('tbodyPortafolioDetalle');
        tbody.innerHTML = data.distribucion_mensual_detalle.map(item => {
          let fuente = "Superintendencia Financiera de Colombia (SFC) / BVC";
          for (let k in fuentesMap) {
            if (item.activo.includes(k) || item.clase.includes(k)) {
              fuente = fuentesMap[k];
              break;
            }
          }
          return `
            <tr class="hover:bg-slate-800/40 transition">
              <td class="py-2.5 px-2 font-bold text-white">${item.activo}</td>
              <td class="py-2.5 px-2 text-slate-400 text-[11px]">${item.clase}</td>
              <td class="py-2.5 px-2 text-emerald-400 font-mono font-semibold">${item.porcentaje_pct}%</td>
              <td class="py-2.5 px-2 text-slate-200 font-mono">$${Math.round(item.monto_mensual_cop).toLocaleString('es-CO')} COP</td>
              <td class="py-2.5 px-2 text-teal-300 font-mono">${item.tasa_ea_esperada_pct}% EA</td>
              <td class="py-2.5 px-2 text-slate-400 text-[11px] italic">${fuente}</td>
            </tr>
          `;
        }).join('');

        // Grid Recomendaciones
        const gridRec = document.getElementById('gridRecomendaciones');
        gridRec.innerHTML = data.recomendaciones_inversion.map(rec => `
          <div class="bg-slate-950 p-3.5 rounded-xl border border-slate-800 space-y-1.5 hover:border-slate-700 transition">
            <div class="text-xs font-bold text-emerald-400">${rec.titulo}</div>
            <p class="text-[11px] text-slate-300 leading-relaxed whitespace-pre-line">${rec.detalle}</p>
          </div>
        `).join('');

        if (statusBox) {
          statusBox.innerText = `✓ Portafolio ${perfil} proyectado a ${anios} años (${data.tasa_ponderada_esperada_ea_pct}% EA)`;
          statusBox.className = 'text-xs text-center font-medium text-teal-400 mt-2 bg-teal-500/10 border border-teal-500/20 py-1.5 px-3 rounded-lg block';
          setTimeout(() => statusBox.className = 'hidden text-xs text-center font-medium text-teal-400 mt-2 bg-teal-500/10 border border-teal-500/20 py-1.5 px-3 rounded-lg', 3500);
        }

        if (btn) {
          btn.innerHTML = '✓ ¡Portafolio Generado!';
          btn.className = 'w-full bg-teal-500 hover:bg-teal-400 text-white font-bold py-2.5 rounded-lg text-xs shadow-lg shadow-teal-500/30 transition';
          setTimeout(() => {
            btn.innerHTML = '🚀 Generar Escenarios y Recomendaciones';
            btn.className = 'w-full bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-500 hover:to-emerald-500 text-white font-bold py-2.5 rounded-lg text-xs shadow-lg shadow-teal-500/20 transition';
            btn.disabled = false;
          }, 1500);
        }
      } catch (err) {
        console.error("Error al generar portafolio:", err);
        if (statusBox) {
          statusBox.innerText = '❌ Error al generar portafolio: ' + err.message;
          statusBox.className = 'text-xs text-center font-medium text-rose-400 mt-2 bg-rose-500/10 border border-rose-500/20 py-1.5 px-3 rounded-lg block';
        }
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = '🚀 Generar Escenarios y Recomendaciones';
        }
      }
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
        box.className = 'mt-6 p-4 rounded-xl border border-rose-500/40 bg-rose-950/40 text-rose-200 text-xs space-y-2';
        box.innerHTML = `
          <div class="font-bold text-rose-400 text-sm">🚨 ¡ALERTA ROJA DE CAPTACIÓN ILEGAL!</div>
          <p>${data.advertencia_legal_sfc}</p>
          <div class="text-[11px] text-rose-300">En solo <strong>${data.ciclos_para_agotar_poblacion_colombia} niveles</strong> se necesitarían más de 39.5 millones de personas (toda la población adulta de Colombia).</div>
        `;
      } else {
        box.className = 'mt-6 p-4 rounded-xl border border-emerald-500/40 bg-emerald-950/40 text-emerald-200 text-xs';
        box.innerHTML = `<p>${data.advertencia_legal_sfc}</p>`;
      }
    }

    let listaTrivias = [];
    let respuestasTriviaUsuario = {};

    function renderTrivias(trivias) {
      listaTrivias = trivias;
      const list = document.getElementById('triviasList');
      list.innerHTML = trivias.map((t, idx) => `
        <div class="bg-slate-900/80 border border-slate-700/60 rounded-xl p-4 space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-slate-200">${idx + 1}. ${t.pregunta}</span>
            <span id="badgeTrivia_${idx}" class="text-[10px] px-2 py-0.5 rounded font-mono bg-slate-800 text-slate-400">Sin responder</span>
          </div>
          <div class="space-y-1.5" id="opcionesTrivia_${idx}">
            ${t.opciones.map((opt, i) => `
              <button type="button" onclick="responderTrivia(${idx}, ${i})" id="btnTrivia_${idx}_${i}" class="w-full text-left text-xs p-2.5 rounded-lg border border-slate-800 bg-slate-950/60 text-slate-300 hover:border-slate-600 hover:text-white transition">
                <span class="font-bold text-slate-400 mr-1.5">${String.fromCharCode(65 + i)}.</span> ${opt}
              </button>
            `).join('')}
          </div>
          <div id="explicacionTrivia_${idx}" class="hidden text-[11px] p-2.5 rounded-lg border border-slate-800 bg-slate-950 text-slate-300 italic"></div>
        </div>
      `).join('');
    }

    function responderTrivia(triviaIdx, opcionIdx) {
      const t = listaTrivias[triviaIdx];
      const esCorrecto = (opcionIdx === t.respuesta_correcta_idx);
      respuestasTriviaUsuario[triviaIdx] = esCorrecto;

      // Actualizar opciones
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

      // Badge
      const badge = document.getElementById(`badgeTrivia_${triviaIdx}`);
      if (esCorrecto) {
        badge.className = 'text-[10px] px-2 py-0.5 rounded font-mono bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
        badge.innerText = '✓ Correcto';
      } else {
        badge.className = 'text-[10px] px-2 py-0.5 rounded font-mono bg-rose-500/20 text-rose-400 border border-rose-500/30';
        badge.innerText = '✗ Incorrecto';
      }

      // Explicación
      const exp = document.getElementById(`explicacionTrivia_${triviaIdx}`);
      exp.innerHTML = `<span class="font-bold text-amber-400 not-italic">Normativa / Explicación:</span> ${t.explicacion}`;
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
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-slate-900 p-4 rounded-xl border border-slate-700">
            <span class="text-xs font-bold text-emerald-400 block">Paso 0 & 1: Habeas Data & Módulo 6 (Salin)</span>
            <p class="text-xs text-slate-300 mt-1">Perfil: <strong>${data.modulo6_salin.perfil.perfil_riesgo}</strong> (${data.modulo6_salin.perfil.puntaje_idoneidad_100}/100)</p>
            <p class="text-xs text-slate-400">Azar liberado a inversión: $200.000 COP/mes (Brecha 10a: +$${data.modulo6_salin.azar.brecha_riqueza_inversion_vs_azar_cop.toLocaleString('es-CO')} COP)</p>
          </div>

          <div class="bg-slate-900 p-4 rounded-xl border border-slate-700">
            <span class="text-xs font-bold text-blue-400 block">Paso 2: Módulo 1 (Nidia - Presupuesto)</span>
            <p class="text-xs text-slate-300 mt-1">Ingreso Neto: <strong>$${data.modulo1_nidia.ingreso_neto_mensual_cop.toLocaleString('es-CO')} COP</strong></p>
            <p class="text-xs text-slate-400">Excedente Libre: $${data.modulo1_nidia.excedente_mensual_cop.toLocaleString('es-CO')} COP (Fondo Emergencia: ${data.modulo1_nidia.meses_cobertura_fondo_emergencia} meses)</p>
          </div>

          <div class="bg-slate-900 p-4 rounded-xl border border-slate-700">
            <span class="text-xs font-bold text-purple-400 block">Paso 3: Módulo 3 (Catalina - Deudas)</span>
            <p class="text-xs text-slate-300 mt-1">Estrategia Óptima: <strong>${data.modulo3_catalina.estrategia_optima}</strong></p>
            <p class="text-xs text-slate-400">Ahorro en Intereses: $${data.modulo3_catalina.ahorro_intereses_cop.toLocaleString('es-CO')} COP</p>
          </div>

          <div class="bg-slate-900 p-4 rounded-xl border border-slate-700">
            <span class="text-xs font-bold text-teal-400 block">Paso 4: Módulo 2 (Camilo - Inversiones)</span>
            <p class="text-xs text-slate-300 mt-1">Patrimonio Proyectado 5a: <strong>$${data.modulo2_camilo.patrimonio_proyectado_nominal_cop.toLocaleString('es-CO')} COP</strong></p>
            <p class="text-xs text-slate-400">Vehículos: Bolsillos, CDT Digital, FIC y Cuenta AFC</p>
          </div>

          <div class="bg-slate-900 p-4 rounded-xl border border-slate-700">
            <span class="text-xs font-bold text-amber-400 block">Paso 5: Módulo 4 (Jesi - Finca Raíz)</span>
            <p class="text-xs text-slate-300 mt-1">Apartamento $200M VIS: <strong>${data.modulo4_jesi.cumple_ley_546_30pct ? 'Cumple Ley 546 (Tope 30%)' : 'Excede cuota'}</strong></p>
            <p class="text-xs text-slate-400">Cuota crédito: $${data.modulo4_jesi.primera_cuota_credito_cop.toLocaleString('es-CO')} COP (${data.modulo4_jesi.porcentaje_cuota_sobre_ingreso_pct}% del ingreso)</p>
          </div>

          <div class="bg-slate-900 p-4 rounded-xl border border-slate-700">
            <span class="text-xs font-bold text-rose-400 block">Paso 6: Módulo 5 (Nelson - Decisiones de Vida)</span>
            <p class="text-xs text-slate-300 mt-1">Decisión (Hijos 0 a 23 años): <strong>${data.modulo5_nelson.dictamen_viabilidad}</strong></p>
            <p class="text-xs text-slate-400">Éxito Monte Carlo: ${data.modulo5_nelson.probabilidad_exito_montecarlo_pct}% | VPA: $${data.modulo5_nelson.vpa_decision_cop.toLocaleString('es-CO')} COP</p>
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
    print("Abre tu navegador en: http://127.0.0.1:8000")
    print("=" * 60)
    uvicorn.run(app, host="127.0.0.1", port=8000)
