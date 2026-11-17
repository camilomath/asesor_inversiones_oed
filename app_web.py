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
)

app = FastAPI(title="Asesor Financiero OED", description="Plataforma Local de Asesoría Financiera Colombiana")


class SuitabilityRequest(BaseModel):
    respuestas: Dict[str, int]


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
      <!-- Sección Azar vs Inversión -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="bg-slate-800/60 border border-slate-700/80 rounded-2xl p-6 shadow-xl">
          <h2 class="text-base font-bold text-emerald-400 flex items-center space-x-2">
            <span>🎲</span>
            <span>Simulador Azar vs. Interés Compuesto</span>
          </h2>
          <p class="text-xs text-slate-400 mt-1">Modela el costo de oportunidad de loterías, Baloto y apuestas frente a inversión legal SFC.</p>
          
          <form id="formAzar" onsubmit="event.preventDefault(); calcularAzar(); return false;" class="mt-5 space-y-4">
            <div>
              <label class="block text-xs font-semibold text-slate-300">Gasto Mensual en Azar/Apuestas (COP)</label>
              <input type="number" id="inpMontoAzar" value="200000" step="10000" min="10000" class="mt-1 w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500">
              <span class="text-[11px] text-slate-500">Ejemplo: $50.000 COP semanales = $200.000 COP/mes</span>
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-300">Horizonte de Tiempo</label>
              <select id="inpAniosAzar" class="mt-1 w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500">
                <option value="3">3 años (36 meses)</option>
                <option value="5">5 años (60 meses)</option>
                <option value="10" selected>10 años (120 meses)</option>
                <option value="15">15 años (180 meses)</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-300">Rentabilidad Estimada Inversión Regulada</label>
              <input type="number" id="inpTasaAzar" value="11.0" step="0.5" class="mt-1 w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500">
              <span class="text-[11px] text-slate-500">Tasa Efectiva Anual (EA) de portafolio balanceado</span>
            </div>

            <button type="button" onclick="calcularAzar()" id="btnCalcularAzar" class="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold py-2.5 rounded-lg text-sm shadow-lg shadow-emerald-500/20 transition">
              🎲 Calcular Comparativa
            </button>
            <div id="statusCalculoAzar" class="hidden text-xs text-center font-medium text-emerald-400 mt-2 bg-emerald-500/10 border border-emerald-500/20 py-1.5 px-3 rounded-lg"></div>
          </form>
        </div>

        <!-- Resultados Azar -->
        <div class="lg:col-span-2 bg-slate-800/60 border border-slate-700/80 rounded-2xl p-6 shadow-xl space-y-6">
          <div class="flex items-center justify-between border-b border-slate-700/60 pb-4">
            <div>
              <h3 class="font-bold text-white text-base">Impacto Patrimonial a <span id="lblAnios" class="text-emerald-400">10</span> Años</h3>
              <p class="text-xs text-slate-400">Desembolsando <span id="lblTotalDesembolsado" class="font-bold text-slate-200">$24,000,000 COP</span></p>
            </div>
            <div class="text-right">
              <span class="text-xs text-slate-400 block">Brecha Neta a Favor del Ahorro</span>
              <span id="lblBrecha" class="text-xl font-extrabold text-emerald-400">+$30,965,950 COP</span>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="bg-rose-950/30 border border-rose-900/50 rounded-xl p-4">
              <span class="text-xs font-semibold text-rose-300 uppercase tracking-wider block">Juegos de Azar (E[X])</span>
              <span id="lblAzar" class="text-lg font-bold text-rose-400 mt-1 block">$11,520,000 COP</span>
              <p class="text-[11px] text-rose-300/70 mt-1">Pérdida matemática: <span id="lblPerdidaAzar" class="font-bold">-$12,480,000 COP</span></p>
            </div>

            <div class="bg-blue-950/30 border border-blue-900/50 rounded-xl p-4">
              <span class="text-xs font-semibold text-blue-300 uppercase tracking-wider block">Capital Aportado Puro</span>
              <span id="lblCapital" class="text-lg font-bold text-blue-400 mt-1 block">$24,000,000 COP</span>
              <p class="text-[11px] text-blue-300/70 mt-1">Ahorro en alcancía (sin rentabilidad)</p>
            </div>

            <div class="bg-emerald-950/30 border border-emerald-900/50 rounded-xl p-4">
              <span class="text-xs font-semibold text-emerald-300 uppercase tracking-wider block">Inversión Regulada SFC</span>
              <span id="lblInversion" class="text-lg font-bold text-emerald-400 mt-1 block">$42,485,950 COP</span>
              <p class="text-[11px] text-emerald-300/70 mt-1">Interés compuesto: <span id="lblIntereses" class="font-bold">+$18,485,950 COP</span></p>
            </div>
          </div>

          <div class="bg-slate-900/80 rounded-xl p-4 border border-slate-700/50">
            <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Probabilidades Exactas en Colombia</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              <div class="bg-slate-800/80 rounded-lg p-3">
                <span class="text-slate-400 block">Baloto (5 cifras + súper balota):</span>
                <span id="lblBaloto" class="font-mono text-amber-400 font-semibold">1 en 15,401,568 (0.00000649%)</span>
              </div>
              <div class="bg-slate-800/80 rounded-lg p-3">
                <span class="text-slate-400 block">Chance de 4 cifras:</span>
                <span id="lblChance" class="font-mono text-amber-400 font-semibold">1 en 10,000 (0.0100%)</span>
              </div>
            </div>
          </div>

          <!-- Trayectoria Anualizada Dinámica -->
          <div class="bg-slate-900/80 rounded-xl p-4 border border-slate-700/50">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider">Evolución Anual: Desembolso vs. Inversión Regulada</h4>
              <span id="lblBadgeTrayectoria" class="text-[11px] text-emerald-400 font-mono bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">Dinámico</span>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-xs text-left">
                <thead class="text-slate-400 border-b border-slate-800">
                  <tr>
                    <th class="py-2 px-2">Año</th>
                    <th class="py-2 px-2">Total Aportado</th>
                    <th class="py-2 px-2 text-rose-400">Pérdida Azar E[X]</th>
                    <th class="py-2 px-2 text-emerald-400">Inversión SFC</th>
                    <th class="py-2 px-2 text-right text-emerald-300 font-bold">Brecha Ganada</th>
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

      <!-- Test de Idoneidad SFC (8 Preguntas) -->
      <div class="bg-slate-800/60 border border-slate-700/80 rounded-2xl p-6 shadow-xl">
        <div class="flex items-center justify-between mb-4 border-b border-slate-700/60 pb-3">
          <div>
            <h3 class="text-base font-bold text-white flex items-center space-x-2">
              <span>📋</span>
              <span>Test de Idoneidad y Perfil de Riesgo (Decreto 2555 de 2010 SFC)</span>
            </h3>
            <p class="text-xs text-slate-400 mt-0.5">Evalúa el horizonte, capacidad patrimonial y psicología ante fluctuaciones de mercado.</p>
          </div>
          <button onclick="evaluarTestSFC()" class="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-4 py-2 rounded-lg text-xs transition">
            Diagnosticar Mi Perfil
          </button>
        </div>

        <div id="cuestionarioContainer" class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Cuestionario inyectado vía JS -->
        </div>

        <!-- Resultado Idoneidad -->
        <div id="resultadoIdoneidad" class="mt-6 hidden bg-slate-950 border border-emerald-500/40 rounded-xl p-5 space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs uppercase tracking-wider text-slate-400">Resultado de Idoneidad SFC</span>
            <span id="resPerfilBadge" class="px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              Moderado
            </span>
          </div>
          <div class="text-sm text-slate-300" id="resDictamen"></div>
          <div id="resAlertaSuitability" class="hidden text-xs bg-amber-500/10 border border-amber-500/30 text-amber-300 p-3 rounded-lg"></div>
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

        <form onsubmit="evaluarPonzi(event)" class="mt-6 space-y-4">
          <div>
            <label class="block text-xs font-semibold text-slate-300">Rentabilidad Mensual Prometida (%)</label>
            <input type="number" id="inpTasaPonzi" value="10.0" step="0.5" min="1" class="mt-1 w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-rose-500">
            <span class="text-[11px] text-slate-500">Ejemplo: 10% mensual "sin riesgo"</span>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-300">Personas que cada miembro debe reclutar</label>
            <input type="number" id="inpPersonasPonzi" value="3" min="2" max="10" class="mt-1 w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-rose-500">
          </div>

          <button type="submit" class="w-full bg-rose-600 hover:bg-rose-500 text-white font-semibold py-2.5 rounded-lg text-sm shadow-lg shadow-rose-600/20 transition">
            Analizar Viabilidad Matemática
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

      // Calcular comparativa inicial para poblar datos dinámicos y tabla
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
      const respuestas = {};
      cuestionarioData.forEach(p => {
        respuestas[p.id] = parseInt(document.getElementById(`sel_${p.id}`).value);
      });

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

    function renderTrivias(trivias) {
      const list = document.getElementById('triviasList');
      list.innerHTML = trivias.map((t, idx) => `
        <div class="bg-slate-900/80 border border-slate-700/60 rounded-xl p-4 space-y-2">
          <div class="text-xs font-bold text-slate-200">${idx + 1}. ${t.pregunta}</div>
          <div class="space-y-1.5 pl-2">
            ${t.opciones.map((opt, i) => `
              <div class="text-xs ${i === t.respuesta_correcta_idx ? 'text-emerald-400 font-semibold' : 'text-slate-400'}">
                ${i === t.respuesta_correcta_idx ? '✓' : '•'} ${opt}
              </div>
            `).join('')}
          </div>
          <p class="text-[11px] text-slate-400 border-t border-slate-800 pt-2 italic">Explicación: ${t.explicacion}</p>
        </div>
      `).join('');
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
