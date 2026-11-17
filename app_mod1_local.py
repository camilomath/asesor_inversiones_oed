"""
Interfaz Gráfica Local (Web App 100% Autónoma) para probar el Módulo 1:
Radiografía del Sueldo, Presupuesto Personal y Gastos Hormiga — Nidia Velásquez (OED).

Características:
- Cero dependencias externas requeridas: utiliza `http.server` de la librería estándar de Python
  y ejecuta directamente las funciones reales de `src/mod1_presupuesto.py` en el backend local.
- Interfaz interactiva en español (100% offline, sin CDNs externos) con:
  • Controles en vivo de modalidad laboral (Empleado, Integral, Independiente OPS + ARL I-V), AFC,
    egresos, fondo de emergencia, calculadora ítem por ítem de gastos hormiga y 4x1000 (GMF).
  • Diagrama de Sankey SVG, Cascada (Waterfall) SVG, Curva de Costo de Oportunidad (120 meses)
    y Termómetro 50/30/20 + Fondo de Emergencia.
  • Comparador simultáneo de las 3 modalidades laborales en Colombia y exportación del
    Contrato JSON de Integración OED.

Uso:
    python app_mod1_local.py
    python app_mod1_local.py --port 8501 --no-browser
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.finance import cargar_configuracion
from src.mod1_presupuesto import (
    comparar_modalidades_laborales,
    diagnosticar_presupuesto_y_flujo_caja,
    ejecutar_modulo_1_perfil_usuario,
)

CONFIG_GLOBAL = cargar_configuracion()

HTML_DASHBOARD = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Módulo 1 OED — Radiografía del Sueldo, Presupuesto y Gastos Hormiga</title>
<style>
  :root {
    --bg: #f1f5f9;
    --card: #ffffff;
    --border: #cbd5e1;
    --text: #0f172a;
    --muted: #475569;
    --primary: #0f4c81;
    --primary-light: #e0f2fe;
    --green: #15803d;
    --green-bg: #dcfce7;
    --amber: #b45309;
    --amber-bg: #fef3c7;
    --red: #b91c1c;
    --red-bg: #fee2e2;
    --purple: #6d28d9;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    font-size: 14px;
    line-height: 1.45;
  }
  header {
    background: linear-gradient(135deg, #0b2545 0%, #134074 60%, #1b6ca8 100%);
    color: #fff;
    padding: 16px 24px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.18);
  }
  header h1 {
    margin: 0;
    font-size: 19px;
    font-weight: 700;
    letter-spacing: -0.2px;
  }
  header p {
    margin: 3px 0 0;
    font-size: 12.5px;
    opacity: 0.9;
  }
  .presets {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  .btn-preset {
    background: rgba(255, 255, 255, 0.14);
    color: #fff;
    border: 1px solid rgba(255, 255, 255, 0.32);
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
    cursor: pointer;
    transition: background 0.15s;
  }
  .btn-preset:hover { background: rgba(255, 255, 255, 0.28); }
  .layout {
    display: grid;
    grid-template-columns: 380px 1fr;
    gap: 18px;
    padding: 18px 22px;
    max-width: 1600px;
    margin: 0 auto;
  }
  @media (max-width: 1080px) {
    .layout { grid-template-columns: 1fr; }
  }
  .panel {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
  }
  .section-title {
    font-size: 13.5px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    color: var(--primary);
    margin: 0 0 12px;
    padding-bottom: 6px;
    border-bottom: 2px solid var(--primary-light);
  }
  .field { margin-bottom: 11px; }
  .field label {
    display: flex;
    justify-content: space-between;
    font-weight: 600;
    font-size: 12.5px;
    margin-bottom: 4px;
    color: #1e293b;
  }
  .field label span.val-hint {
    color: var(--primary);
    font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
  }
  input[type="number"], input[type="text"], select {
    width: 100%;
    padding: 7px 9px;
    border: 1px solid var(--border);
    border-radius: 6px;
    font-size: 13px;
    background: #f8fafc;
    color: var(--text);
  }
  input[type="range"] {
    width: 100%;
    accent-color: var(--primary);
    margin-top: 3px;
  }
  .row-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }
  .hormiga-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 8px;
  }
  .hormiga-item {
    display: grid;
    grid-template-columns: 1.5fr 1fr 0.7fr 26px;
    gap: 5px;
    align-items: center;
  }
  .hormiga-item input { padding: 5px 6px; font-size: 12px; }
  .btn-del {
    background: #fee2e2;
    color: #b91c1c;
    border: 1px solid #fca5a5;
    border-radius: 5px;
    height: 28px;
    cursor: pointer;
    font-weight: bold;
  }
  .btn-add {
    background: var(--primary-light);
    color: var(--primary);
    border: 1px dashed var(--primary);
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    width: 100%;
  }
  .status-banner {
    border-radius: 10px;
    padding: 13px 16px;
    margin-bottom: 14px;
    border-left: 6px solid var(--primary);
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .status-OK { background: var(--green-bg); border-color: var(--green); color: #14532d; }
  .status-WARN { background: var(--amber-bg); border-color: var(--amber); color: #78350f; }
  .status-ERR { background: var(--red-bg); border-color: var(--red); color: #7f1d1d; }
  .kpis {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(195px, 1fr));
    gap: 12px;
    margin-bottom: 16px;
  }
  .kpi {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 13px 14px;
  }
  .kpi .k-label {
    font-size: 11.5px;
    font-weight: 600;
    color: var(--muted);
    text-transform: uppercase;
  }
  .kpi .k-val {
    font-size: 20px;
    font-weight: 800;
    margin: 4px 0;
    font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
  }
  .kpi .k-sub {
    font-size: 11.5px;
    color: var(--muted);
  }
  .tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 12px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
  }
  .tab-btn {
    padding: 7px 14px;
    border-radius: 7px;
    border: 1px solid var(--border);
    background: #f8fafc;
    color: var(--muted);
    font-weight: 600;
    font-size: 12.5px;
    cursor: pointer;
  }
  .tab-btn.active {
    background: var(--primary);
    color: #fff;
    border-color: var(--primary);
  }
  .tab-pane { display: none; }
  .tab-pane.active { display: block; }
  .charts-2col {
    display: grid;
    grid-template-columns: 1.15fr 1fr;
    gap: 14px;
  }
  @media (max-width: 1200px) {
    .charts-2col { grid-template-columns: 1fr; }
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12.5px;
  }
  th, td {
    padding: 8px 10px;
    border-bottom: 1px solid #e2e8f0;
    text-align: right;
  }
  th:first-child, td:first-child { text-align: left; }
  th {
    background: #f1f5f9;
    font-weight: 700;
    color: #1e293b;
  }
  .bar-track {
    width: 100%;
    height: 12px;
    background: #e2e8f0;
    border-radius: 999px;
    overflow: hidden;
    margin: 5px 0;
  }
  .bar-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.25s ease;
  }
  pre.json-box {
    background: #0f172a;
    color: #e2e8f0;
    padding: 14px;
    border-radius: 8px;
    overflow-x: auto;
    font-size: 12px;
    max-height: 420px;
  }
  .badge {
    display: inline-block;
    padding: 2px 7px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
  }
  .badge-ok { background: var(--green-bg); color: var(--green); }
  .badge-warn { background: var(--amber-bg); color: var(--amber); }
  svg { width: 100%; height: auto; display: block; }
</style>
</head>
<body>

<header>
  <div>
    <h1>Módulo 1: Radiografía del Sueldo, Presupuesto y Gastos Hormiga</h1>
    <p>Responsable OED: <strong>Nidia Velásquez</strong> (Ing. Mecánica) · Motor Python Local en Tiempo Real (<code>src/mod1_presupuesto.py</code>)</p>
  </div>
  <div class="presets">
    <button class="btn-preset" onclick="cargarEscenario('semilla')">Caso Semilla OED ($6.5M)</button>
    <button class="btn-preset" onclick="cargarEscenario('joven')">Salario &le; 2 SMMLV ($2.5M)</button>
    <button class="btn-preset" onclick="cargarEscenario('ops')">Contratista OPS ($8.5M)</button>
    <button class="btn-preset" onclick="cargarEscenario('integral')">Integral + AFC ($20M)</button>
    <button class="btn-preset" onclick="cargarEscenario('deficit')">Alerta Déficit (FA-01)</button>
  </div>
</header>

<div class="layout">
  <!-- PANEL IZQUIERDO: PARÁMETROS DE ENTRADA -->
  <aside class="panel">
    <h2 class="section-title">1. Nómina y Modalidad (Colombia)</h2>

    <div class="row-2">
      <div class="field">
        <label>Modalidad Contractual</label>
        <select id="modalidad_laboral" onchange="onModalidadChange()">
          <option value="Empleado">Empleado Ordinario</option>
          <option value="Integral">Salario Integral (&ge;13 SMMLV)</option>
          <option value="Independiente">Independiente / OPS (IBC 40%)</option>
        </select>
      </div>
      <div class="field">
        <label>Clase ARL (OPS)</label>
        <select id="clase_riesgo_arl" onchange="recalcular()">
          <option value="1">Clase I (0.522%)</option>
          <option value="2">Clase II (1.044%)</option>
          <option value="3">Clase III (2.436%)</option>
          <option value="4">Clase IV (4.350%)</option>
          <option value="5">Clase V (6.960%)</option>
        </select>
      </div>
    </div>

    <div class="field">
      <label>Ingreso Bruto Mensual <span class="val-hint" id="lbl_bruto">$6.500.000</span></label>
      <input type="number" id="ingreso_bruto" step="100000" min="0" value="6500000" oninput="syncSlider('ingreso_bruto','rng_bruto'); recalcular();" />
      <input type="range" id="rng_bruto" min="1423500" max="35000000" step="100000" value="6500000" oninput="syncInput('rng_bruto','ingreso_bruto'); recalcular();" />
    </div>

    <div class="row-2">
      <div class="field">
        <label>Otros Ingresos / Mes</label>
        <input type="number" id="otros_ingresos" step="50000" min="0" value="0" oninput="recalcular()" />
      </div>
      <div class="field">
        <label title="Aporte voluntario a Cuenta AFC o Fondo de Pensión Voluntaria para reducir Retefuente">Aporte AFC / FPV</label>
        <input type="number" id="aporte_afc" step="50000" min="0" value="0" oninput="recalcular()" />
      </div>
    </div>

    <h2 class="section-title" style="margin-top:14px;">2. Presupuesto y Liquidez</h2>

    <div class="field">
      <label>Costos Fijos Vitales (Arriendo, Mercado, Servicios) <span class="val-hint" id="lbl_fijos">$2.800.000</span></label>
      <input type="number" id="gastos_fijos" step="50000" min="0" value="2800000" oninput="recalcular()" />
    </div>

    <div class="row-2">
      <div class="field">
        <label>Estilo de Vida / Variables</label>
        <input type="number" id="gastos_variables" step="50000" min="0" value="950000" oninput="recalcular()" />
      </div>
      <div class="field">
        <label>Cuotas Deuda Actuales</label>
        <input type="number" id="cuotas_deuda" step="50000" min="0" value="0" oninput="recalcular()" />
      </div>
    </div>

    <div class="field">
      <label>Liquidez Actual Fondo de Emergencia</label>
      <input type="number" id="liquidez_emergencia" step="200000" min="0" value="6000000" oninput="recalcular()" />
    </div>

    <h2 class="section-title" style="margin-top:14px;">3. Gastos Hormiga y Fugas (4x1000)</h2>
    <div style="font-size:11.5px; color:var(--muted); margin-bottom:6px; display:grid; grid-template-columns:1.5fr 1fr 0.7fr 26px; gap:5px; font-weight:600;">
      <span>Micro-gasto</span><span>$ Unitario</span><span>Veces/mes</span><span></span>
    </div>
    <div id="lista_hormiga" class="hormiga-list"></div>
    <button class="btn-add" onclick="agregarItemHormiga()">+ Agregar Gasto Hormiga</button>

    <div class="row-2" style="margin-top:10px;">
      <div class="field">
        <label>Cuotas de Manejo / Mes</label>
        <input type="number" id="cuotas_manejo" step="5000" min="0" value="0" oninput="recalcular()" />
      </div>
      <div class="field">
        <label>Retiros Sujetos 4x1000</label>
        <input type="number" id="movimientos_gmf" step="100000" min="0" value="0" oninput="recalcular()" />
      </div>
    </div>
    <label style="display:flex; align-items:center; gap:7px; font-size:12px; cursor:pointer;">
      <input type="checkbox" id="cuenta_exenta" checked onchange="recalcular()" />
      Cuenta marcada exenta de 4x1000 (tope legal 350 UVT/mes)
    </label>
  </aside>

  <!-- PANEL PRINCIPAL: RESULTADOS Y GRÁFICOS -->
  <main>
    <div id="banner_estado" class="status-banner status-WARN">Cargando motor financiero colombiano...</div>
    <div id="alerta_normativa_box" style="display:none; margin-bottom:12px;" class="status-banner status-ERR"></div>

    <!-- TARJETAS KPI -->
    <section class="kpis">
      <div class="kpi">
        <div class="k-label">Ingreso Disponible Neto (IDN)</div>
        <div class="k-val" id="kpi_idn">$0</div>
        <div class="k-sub" id="kpi_idn_sub">Descuentos de ley: $0</div>
      </div>
      <div class="kpi">
        <div class="k-label">Excedente Mensual Libre</div>
        <div class="k-val" id="kpi_excedente">$0</div>
        <div class="k-sub" id="kpi_excedente_sub">Eficiencia presupuestal: 0%</div>
      </div>
      <div class="kpi">
        <div class="k-label">Fondo de Emergencia</div>
        <div class="k-val" id="kpi_emergencia">0.0 meses</div>
        <div class="bar-track"><div id="bar_emergencia" class="bar-fill" style="width:0%; background:#15803d;"></div></div>
        <div class="k-sub" id="kpi_emergencia_sub">Meta según contrato: 3 meses</div>
      </div>
      <div class="kpi">
        <div class="k-label">Fugas (Hormiga + 4x1000)</div>
        <div class="k-val" id="kpi_fugas" style="color:#b91c1c;">$0</div>
        <div class="k-sub" id="kpi_fugas_sub">0% del ingreso neto</div>
      </div>
      <div class="kpi">
        <div class="k-label">Costo Oportunidad 10 Años (10% EA)</div>
        <div class="k-val" id="kpi_oportunidad" style="color:#0f4c81;">$0</div>
        <div class="k-sub" id="kpi_oportunidad_sub">A 5 años: $0</div>
      </div>
    </section>

    <!-- PESTAÑAS DE ANÁLISIS -->
    <div class="panel">
      <div class="tabs">
        <button class="tab-btn active" onclick="activarTab('tab_flujos', this)">1. Flujo Sankey &amp; Cascada</button>
        <button class="tab-btn" onclick="activarTab('tab_nomina', this)">2. Radiografía del Sueldo &amp; Comparativa</button>
        <button class="tab-btn" onclick="activarTab('tab_hormiga', this)">3. Costo Oportunidad Hormiga &amp; 50/30/20</button>
        <button class="tab-btn" onclick="activarTab('tab_contrato', this)">4. Contrato JSON OED</button>
      </div>

      <!-- TAB 1: SANKEY & WATERFALL -->
      <div id="tab_flujos" class="tab-pane active">
        <div class="charts-2col">
          <div>
            <h3 class="section-title">Diagrama de Sankey — Balance Termodinámico</h3>
            <div id="svg_sankey_wrap"></div>
          </div>
          <div>
            <h3 class="section-title">Cascada (Waterfall) — Del Bruto al Excedente</h3>
            <div id="svg_waterfall_wrap"></div>
          </div>
        </div>
      </div>

      <!-- TAB 2: NÓMINA Y COMPARADOR -->
      <div id="tab_nomina" class="tab-pane">
        <div class="charts-2col">
          <div>
            <h3 class="section-title">Desglose de Nómina Actual</h3>
            <table id="tabla_nomina_detalle"></table>
          </div>
          <div>
            <h3 class="section-title">Comparativa Mismo Bruto: Empleado vs. Integral vs. OPS</h3>
            <table id="tabla_comparativa_mod"></table>
            <p style="font-size:12px; color:var(--muted); margin-top:8px;">
              <strong>Nota Ingenieril:</strong> En <em>Empleado Ordinario</em> el empleador asume adicionalmente Prima (8.33%), Cesantías (8.33%) e Intereses sobre Cesantías, mientras que en <em>OPS Independiente</em> el contratista asume la totalidad de su seguridad social sobre el 40% del ingreso bruto (piso 1 SMMLV).
            </p>
          </div>
        </div>
      </div>

      <!-- TAB 3: HORMIGA Y 50/30/20 -->
      <div id="tab_hormiga" class="tab-pane">
        <div class="charts-2col">
          <div>
            <h3 class="section-title">Curva de Capitalización de Fugas (1 a 120 Meses al 10% EA)</h3>
            <div id="svg_oportunidad_wrap"></div>
          </div>
          <div>
            <h3 class="section-title">Diagnóstico Regla 50 / 30 / 20 Adaptada a Colombia</h3>
            <div id="panel_50_30_20"></div>
          </div>
        </div>
      </div>

      <!-- TAB 4: CONTRATO JSON -->
      <div id="tab_contrato" class="tab-pane">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
          <h3 class="section-title" style="margin:0; border:none;">Payload Oficial para Módulos 2, 3, 4 y 5</h3>
          <button class="tab-btn active" onclick="descargarContratoJSON()">Descargar perfil_mod1.json</button>
        </div>
        <pre id="json_contrato" class="json-box"></pre>
      </div>
    </div>
  </main>
</div>

<script>
const fmtCOP = (v) => {
  const sign = v < 0 ? "-" : "";
  return sign + "$" + Math.round(Math.abs(v)).toLocaleString("es-CO");
};

let estadoUltimoResultado = null;

let itemsHormiga = [
  { concepto: "Café / snacks calle", monto_unitario_cop: 6500, frecuencia_mensual: 20 },
  { concepto: "Domicilios y propinas", monto_unitario_cop: 12500, frecuencia_mensual: 8 },
  { concepto: "Suscripciones sin uso", monto_unitario_cop: 45000, frecuencia_mensual: 1 },
  { concepto: "Antojos fin de semana", monto_unitario_cop: 22500, frecuencia_mensual: 2 }
];

function renderItemsHormiga() {
  const cont = document.getElementById("lista_hormiga");
  cont.innerHTML = "";
  itemsHormiga.forEach((it, idx) => {
    const row = document.createElement("div");
    row.className = "hormiga-item";
    row.innerHTML = `
      <input type="text" value="${it.concepto}" oninput="itemsHormiga[${idx}].concepto=this.value; recalcular();" />
      <input type="number" step="500" min="0" value="${it.monto_unitario_cop}" oninput="itemsHormiga[${idx}].monto_unitario_cop=Number(this.value||0); recalcular();" />
      <input type="number" step="1" min="0" value="${it.frecuencia_mensual}" oninput="itemsHormiga[${idx}].frecuencia_mensual=Number(this.value||0); recalcular();" />
      <button class="btn-del" title="Eliminar" onclick="eliminarItemHormiga(${idx})">&times;</button>
    `;
    cont.appendChild(row);
  });
}

function agregarItemHormiga() {
  itemsHormiga.push({ concepto: "Nuevo micro-gasto", monto_unitario_cop: 10000, frecuencia_mensual: 4 });
  renderItemsHormiga();
  recalcular();
}

function eliminarItemHormiga(idx) {
  itemsHormiga.splice(idx, 1);
  renderItemsHormiga();
  recalcular();
}

function syncSlider(numId, rngId) {
  document.getElementById(rngId).value = document.getElementById(numId).value;
}
function syncInput(rngId, numId) {
  document.getElementById(numId).value = document.getElementById(rngId).value;
}

function onModalidadChange() {
  const mod = document.getElementById("modalidad_laboral").value;
  document.getElementById("clase_riesgo_arl").disabled = (mod !== "Independiente");
  recalcular();
}

function activarTab(tabId, btn) {
  document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".tabs .tab-btn").forEach(b => b.classList.remove("active"));
  document.getElementById(tabId).classList.add("active");
  btn.classList.add("active");
}

function cargarEscenario(nombre) {
  if (nombre === "semilla") {
    setForm("Empleado", 1, 6500000, 0, 0, 2800000, 950000, 0, 6000000, 0, 0, true);
    itemsHormiga = [
      { concepto: "Café / snacks calle", monto_unitario_cop: 6500, frecuencia_mensual: 20 },
      { concepto: "Domicilios y propinas", monto_unitario_cop: 12500, frecuencia_mensual: 8 },
      { concepto: "Suscripciones sin uso", monto_unitario_cop: 45000, frecuencia_mensual: 1 },
      { concepto: "Antojos fin de semana", monto_unitario_cop: 22500, frecuencia_mensual: 2 }
    ];
  } else if (nombre === "joven") {
    setForm("Empleado", 1, 2500000, 0, 0, 1350000, 450000, 180000, 4200000, 15000, 0, true);
    itemsHormiga = [
      { concepto: "Tinto y empanada", monto_unitario_cop: 4500, frecuencia_mensual: 22 },
      { concepto: "Apps transporte", monto_unitario_cop: 14000, frecuencia_mensual: 6 }
    ];
  } else if (nombre === "ops") {
    setForm("Independiente", 1, 8500000, 0, 400000, 3100000, 1100000, 500000, 19000000, 24000, 4500000, false);
    itemsHormiga = [
      { concepto: "Coworking cafés", monto_unitario_cop: 9000, frecuencia_mensual: 18 },
      { concepto: "Domicilios almuerzo", monto_unitario_cop: 18000, frecuencia_mensual: 10 }
    ];
  } else if (nombre === "integral") {
    setForm("Integral", 1, 20000000, 0, 2000000, 6200000, 2800000, 1200000, 25000000, 35000, 22000000, true);
    itemsHormiga = [
      { concepto: "Restaurantes / cafés", monto_unitario_cop: 25000, frecuencia_mensual: 16 },
      { concepto: "Plataformas / apps", monto_unitario_cop: 65000, frecuencia_mensual: 3 }
    ];
  } else if (nombre === "deficit") {
    setForm("Empleado", 1, 3800000, 0, 0, 2300000, 900000, 650000, 800000, 32000, 3000000, false);
    itemsHormiga = [
      { concepto: "Domicilios nocturnos", monto_unitario_cop: 22000, frecuencia_mensual: 12 },
      { concepto: "Compras impulsivas", monto_unitario_cop: 40000, frecuencia_mensual: 4 }
    ];
  }
  renderItemsHormiga();
  onModalidadChange();
}

function setForm(mod, arl, bruto, otros, afc, fijos, vars, deuda, liq, manejo, gmf, exenta) {
  document.getElementById("modalidad_laboral").value = mod;
  document.getElementById("clase_riesgo_arl").value = String(arl);
  document.getElementById("ingreso_bruto").value = bruto;
  document.getElementById("rng_bruto").value = Math.min(35000000, Math.max(1423500, bruto));
  document.getElementById("otros_ingresos").value = otros;
  document.getElementById("aporte_afc").value = afc;
  document.getElementById("gastos_fijos").value = fijos;
  document.getElementById("gastos_variables").value = vars;
  document.getElementById("cuotas_deuda").value = deuda;
  document.getElementById("liquidez_emergencia").value = liq;
  document.getElementById("cuotas_manejo").value = manejo;
  document.getElementById("movimientos_gmf").value = gmf;
  document.getElementById("cuenta_exenta").checked = exenta;
}

async function recalcular() {
  const payload = {
    modalidad_laboral: document.getElementById("modalidad_laboral").value,
    clase_riesgo_arl: Number(document.getElementById("clase_riesgo_arl").value || 1),
    ingreso_bruto_mensual_cop: Number(document.getElementById("ingreso_bruto").value || 0),
    otros_ingresos_mensuales_cop: Number(document.getElementById("otros_ingresos").value || 0),
    aporte_voluntario_afc_fpv_cop: Number(document.getElementById("aporte_afc").value || 0),
    gastos_fijos_vitales_cop: Number(document.getElementById("gastos_fijos").value || 0),
    gastos_variables_estilo_vida_cop: Number(document.getElementById("gastos_variables").value || 0),
    cuotas_deuda_mensual_cop: Number(document.getElementById("cuotas_deuda").value || 0),
    liquidez_actual_fondo_emergencia_cop: Number(document.getElementById("liquidez_emergencia").value || 0),
    cuotas_manejo_mensual_cop: Number(document.getElementById("cuotas_manejo").value || 0),
    monto_movimientos_gmf_mensual_cop: Number(document.getElementById("movimientos_gmf").value || 0),
    cuenta_exenta_4x1000: document.getElementById("cuenta_exenta").checked,
    gastos_hormiga_mensual_cop: 0,
    detalle_gastos_hormiga: itemsHormiga
  };

  document.getElementById("lbl_bruto").textContent = fmtCOP(payload.ingreso_bruto_mensual_cop);
  document.getElementById("lbl_fijos").textContent = fmtCOP(payload.gastos_fijos_vitales_cop);

  const res = await fetch("/api/diagnostico", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  estadoUltimoResultado = data;
  actualizarUI(data);
}

function actualizarUI(data) {
  const d = data.diagnostico;
  const nom = d.liquidacion_nomina;
  const fugas = d.radiografia_fugas;
  const plan = d.plan_accion_flujo_caja;

  // Banner de estado
  const banner = document.getElementById("banner_estado");
  banner.className = "status-banner " + (
    d.estado_flujo_caja === "LISTO_PARA_INVERTIR" ? "status-OK" :
    d.estado_flujo_caja === "CONSTRUIR_FONDO_EMERGENCIA" ? "status-WARN" : "status-ERR"
  );
  banner.innerHTML = `
    <div style="font-weight:800; font-size:13.5px;">Dictamen CU-01 [${plan.codigo_flujo}] — ${d.estado_flujo_caja.replaceAll("_", " ")}</div>
    <div style="font-size:12.5px;">${plan.recomendacion_ejecutiva}</div>
  `;

  // Alerta normativa (ej. Salario Integral < 13 SMMLV)
  const alertaBox = document.getElementById("alerta_normativa_box");
  if (nom.alerta_normativa) {
    alertaBox.style.display = "block";
    alertaBox.innerHTML = `<strong>Alerta Normativa Laboral:</strong> ${nom.alerta_normativa}`;
  } else {
    alertaBox.style.display = "none";
  }

  // KPIs
  document.getElementById("kpi_idn").textContent = fmtCOP(d.ingreso_neto_mensual_cop);
  document.getElementById("kpi_idn_sub").textContent =
    `Descuentos ley: ${fmtCOP(nom.total_descuentos_ley_cop)} (${nom.tasa_descuento_efectiva_pct}%)` +
    (nom.ahorro_tributario_afc_mensual_cop > 0 ? ` · Ahorro AFC: ${fmtCOP(nom.ahorro_tributario_afc_mensual_cop)}` : "");

  const elExc = document.getElementById("kpi_excedente");
  elExc.textContent = fmtCOP(d.excedente_mensual_cop);
  elExc.style.color = d.excedente_mensual_cop >= 0 ? "#15803d" : "#b91c1c";
  document.getElementById("kpi_excedente_sub").textContent = `Eficiencia presupuestal: ${d.eficiencia_presupuestal_pct}% del IDN`;

  document.getElementById("kpi_emergencia").textContent = `${d.meses_fondo_emergencia.toFixed(2)} meses`;
  const pctEmerg = Math.min(100, (d.meses_fondo_emergencia / d.meta_meses_fondo_emergencia) * 100);
  const barEm = document.getElementById("bar_emergencia");
  barEm.style.width = `${pctEmerg}%`;
  barEm.style.background = d.fondo_emergencia_completo ? "#15803d" : "#d97706";
  document.getElementById("kpi_emergencia_sub").textContent =
    `Meta ${nom.modalidad_laboral}: ${d.meta_meses_fondo_emergencia} meses (${fmtCOP(d.monto_meta_fondo_emergencia_cop)})`;

  document.getElementById("kpi_fugas").textContent = fmtCOP(fugas.fuga_total_mensual_cop) + "/mes";
  document.getElementById("kpi_fugas_sub").textContent =
    `Hormiga: ${fmtCOP(fugas.gastos_hormiga_mensual_cop)} · 4x1000+Bancos: ${fmtCOP(fugas.friccion_bancaria_mensual_cop)} (${fugas.peso_sobre_ingreso_neto_pct}% IDN)`;

  document.getElementById("kpi_oportunidad").textContent = fmtCOP(fugas.costo_oportunidad_fuga_total_10a_nominal_cop);
  document.getElementById("kpi_oportunidad_sub").textContent =
    `A 5 años: ${fmtCOP(fugas.costo_oportunidad_fuga_total_5a_nominal_cop)} · Real 10a (hoy): ${fmtCOP(fugas.costo_oportunidad_fuga_total_10a_real_cop)}`;

  dibujarSankeySVG(d);
  dibujarWaterfallSVG(d);
  renderTablasNomina(nom, data.comparativa_modalidades);
  dibujarCurvaOportunidadSVG(fugas);
  renderRegla503020(d.balance_50_30_20);
  document.getElementById("json_contrato").textContent = JSON.stringify(data.contrato_oed, null, 2);
}

function dibujarSankeySVG(d) {
  const nom = d.liquidacion_nomina;
  const totalIn = nom.ingreso_bruto_mensual_cop + nom.auxilio_transporte_cop + d.otros_ingresos_mensuales_cop;
  if (totalIn <= 0) {
    document.getElementById("svg_sankey_wrap").innerHTML = "<p>Ingrese un salario mayor a $0.</p>";
    return;
  }
  const W = 580, H = 340;
  const segSocial = nom.salud_obligatoria_cop + nom.pension_obligatoria_cop + nom.fondo_solidaridad_pensional_cop + nom.arl_cop;
  const rete = nom.retencion_fuente_cop;
  const idn = d.ingreso_neto_mensual_cop;

  const destinos = [
    { label: "Seg. Social", val: segSocial, color: "#ea580c", col: 1 },
    { label: "Retefuente", val: rete, color: "#9a3412", col: 1 }
  ].filter(x => x.val > 0);

  const salidasIdn = [
    { label: "Costos Fijos", val: d.gastos_fijos_vitales_cop, color: "#2563eb" },
    { label: "Estilo de Vida", val: d.gastos_variables_estilo_vida_cop, color: "#7c3aed" },
    { label: "Hormiga + 4x1000", val: d.fuga_total_mensual_cop, color: "#dc2626" },
    { label: "Cuotas Deuda", val: d.cuotas_deuda_mensual_cop, color: "#d97706" },
    { label: "Excedente Libre", val: Math.max(0, d.excedente_mensual_cop), color: "#16a34a" }
  ].filter(x => x.val > 0);

  const totalBase = Math.max(totalIn, segSocial + rete + salidasIdn.reduce((s, x) => s + x.val, 0));
  const scale = 230 / totalBase;

  let svg = `<svg viewBox="0 0 ${W} ${H}">`;
  const x0 = 20, x1 = 235, x2 = 440, bw = 18;
  const hIn = Math.max(12, totalIn * scale);
  const y0 = 40;

  // Nodo 0: Devengado Total
  svg += `<rect x="${x0}" y="${y0}" width="${bw}" height="${hIn}" fill="#0f4c81" rx="3"/>`;
  svg += `<text x="${x0}" y="${y0 - 8}" font-size="11.5" font-weight="700" fill="#0f172a">Devengado: ${fmtCOP(totalIn)}</text>`;

  // Columna 1: Deducciones de Ley + IDN
  let cy0 = y0;
  let cy1 = 32;
  destinos.forEach(item => {
    const h = Math.max(6, item.val * scale);
    const hSrc = item.val * scale;
    svg += pathCurvo(x0 + bw, cy0, hSrc, x1, cy1, h, item.color, 0.25);
    svg += `<rect x="${x1}" y="${cy1}" width="${bw}" height="${h}" fill="${item.color}" rx="3"/>`;
    svg += `<text x="${x1 + bw + 6}" y="${cy1 + h / 2 + 4}" font-size="11" fill="#1e293b">${item.label}: ${fmtCOP(item.val)}</text>`;
    cy0 += hSrc;
    cy1 += h + 14;
  });

  // Nodo IDN en Columna 1
  const yIdn = cy1 + 4;
  const hIdn = Math.max(14, idn * scale);
  svg += pathCurvo(x0 + bw, cy0, idn * scale, x1, yIdn, hIdn, "#0d9488", 0.28);
  svg += `<rect x="${x1}" y="${yIdn}" width="${bw}" height="${hIdn}" fill="#0d9488" rx="3"/>`;
  svg += `<text x="${x1 - 4}" y="${yIdn + hIdn + 14}" font-size="11.5" font-weight="700" fill="#0f766e">IDN: ${fmtCOP(idn)}</text>`;

  // Columna 2: Distribución del IDN
  let cyIdnSrc = yIdn;
  let cy2 = 24;
  const sumSalidas = salidasIdn.reduce((s, x) => s + x.val, 0) || 1;
  salidasIdn.forEach(item => {
    const h = Math.max(8, item.val * scale);
    const hSrc = (item.val / sumSalidas) * hIdn;
    svg += pathCurvo(x1 + bw, cyIdnSrc, hSrc, x2, cy2, h, item.color, 0.30);
    svg += `<rect x="${x2}" y="${cy2}" width="${bw}" height="${h}" fill="${item.color}" rx="3"/>`;
    svg += `<text x="${x2 - 6}" y="${cy2 + h / 2 + 4}" text-anchor="end" font-size="11" font-weight="600" fill="#1e293b">${item.label}</text>`;
    svg += `<text x="${x2 + bw + 5}" y="${cy2 + h / 2 + 4}" font-size="11" fill="#334155">${fmtCOP(item.val)}</text>`;
    cyIdnSrc += hSrc;
    cy2 += h + 13;
  });

  svg += `</svg>`;
  document.getElementById("svg_sankey_wrap").innerHTML = svg;
}

function pathCurvo(xA, yA, hA, xB, yB, hB, color, alpha) {
  const xm = (xA + xB) / 2;
  return `<path d="M${xA},${yA} C${xm},${yA} ${xm},${yB} ${xB},${yB} L${xB},${yB + hB} C${xm},${yB + hB} ${xm},${yA + hA} ${xA},${yA + hA} Z" fill="${color}" fill-opacity="${alpha}"/>`;
}

function dibujarWaterfallSVG(d) {
  const nom = d.liquidacion_nomina;
  const devengado = nom.ingreso_bruto_mensual_cop + nom.auxilio_transporte_cop + d.otros_ingresos_mensuales_cop;
  const pasos = [
    { label: "Devengado", ini: 0, fin: devengado, color: "#0f4c81" },
    { label: "Ley", ini: devengado, fin: d.ingreso_neto_mensual_cop, color: "#ea580c" },
    { label: "IDN", ini: 0, fin: d.ingreso_neto_mensual_cop, color: "#0d9488" },
    { label: "Fijos", ini: d.ingreso_neto_mensual_cop, fin: d.ingreso_neto_mensual_cop - d.gastos_fijos_vitales_cop, color: "#dc2626" },
    { label: "Variables", ini: d.ingreso_neto_mensual_cop - d.gastos_fijos_vitales_cop, fin: d.ingreso_neto_mensual_cop - d.gastos_fijos_vitales_cop - d.gastos_variables_estilo_vida_cop, color: "#dc2626" },
    { label: "Fugas", ini: d.ingreso_neto_mensual_cop - d.gastos_fijos_vitales_cop - d.gastos_variables_estilo_vida_cop, fin: d.ingreso_neto_mensual_cop - d.gastos_fijos_vitales_cop - d.gastos_variables_estilo_vida_cop - d.fuga_total_mensual_cop, color: "#b91c1c" },
    { label: "Excedente", ini: 0, fin: d.excedente_mensual_cop, color: d.excedente_mensual_cop >= 0 ? "#16a34a" : "#991b1b" }
  ];

  const W = 500, H = 330, padT = 28, padB = 46, padL = 20, padR = 16;
  const maxVal = Math.max(1, devengado, ...pasos.map(p => Math.max(p.ini, p.fin)));
  const minVal = Math.min(0, d.excedente_mensual_cop);
  const span = maxVal - minVal;
  const yMap = (v) => padT + ((maxVal - v) / span) * (H - padT - padB);
  const yZero = yMap(0);

  let svg = `<svg viewBox="0 0 ${W} ${H}">`;
  svg += `<line x1="${padL}" y1="${yZero}" x2="${W - padR}" y2="${yZero}" stroke="#94a3b8" stroke-width="1"/>`;

  const colW = (W - padL - padR) / pasos.length;
  pasos.forEach((p, i) => {
    const x = padL + i * colW + 8;
    const bw = colW - 16;
    const yTop = yMap(Math.max(p.ini, p.fin));
    const yBot = yMap(Math.min(p.ini, p.fin));
    const h = Math.max(3, yBot - yTop);
    const delta = (i === 0 || i === 2 || i === pasos.length - 1) ? p.fin : (p.fin - p.ini);

    svg += `<rect x="${x}" y="${yTop}" width="${bw}" height="${h}" fill="${p.color}" rx="3"/>`;
    svg += `<text x="${x + bw / 2}" y="${yTop - 5}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#1e293b">${(delta / 1e6).toFixed(2)}M</text>`;
    svg += `<text x="${x + bw / 2}" y="${H - 20}" text-anchor="middle" font-size="10.5" font-weight="600" fill="#334155">${p.label}</text>`;
  });
  svg += `</svg>`;
  document.getElementById("svg_waterfall_wrap").innerHTML = svg;
}

function renderTablasNomina(nom, comp) {
  const prov = nom.provisiones_prestacionales_informativas;
  const filas = [
    ["Modalidad Contractual", `<strong>${nom.modalidad_laboral}</strong> (${nom.ingreso_en_smmlv} SMMLV)`],
    ["Ingreso Bruto Mensual", fmtCOP(nom.ingreso_bruto_mensual_cop)],
    ["(+) Auxilio de Transporte (&le; 2 SMMLV)", fmtCOP(nom.auxilio_transporte_cop)],
    ["Ingreso Base de Cotización (IBC)", fmtCOP(nom.ibc_cotizacion_cop)],
    ["(-) Salud Obligatoria", fmtCOP(-nom.salud_obligatoria_cop)],
    ["(-) Pensión Obligatoria", fmtCOP(-nom.pension_obligatoria_cop)],
    [`(-) Fondo Solidaridad Pensional (${nom.porcentaje_fsp_aplicado}%)`, fmtCOP(-nom.fondo_solidaridad_pensional_cop)],
    ["(-) ARL (Riesgos Laborales)", fmtCOP(-nom.arl_cop)],
    ["(-) Retención en la Fuente (Art. 383 E.T.)", fmtCOP(-nom.retencion_fuente_cop)],
    ["Ahorro Tributario por AFC / FPV", `<span style="color:#15803d;font-weight:700;">${fmtCOP(nom.ahorro_tributario_afc_mensual_cop)}</span>`],
    ["<strong>(=) Ingreso Disponible Neto (IDN)</strong>", `<strong>${fmtCOP(nom.ingreso_neto_mensual_cop)}</strong>`],
    ["(+) Prima + Cesantías Mensualizadas (Info)", fmtCOP(prov.prima_servicios_mensualizada_cop + prov.cesantias_mensualizadas_cop + prov.intereses_cesantias_mensualizados_cop)]
  ];
  document.getElementById("tabla_nomina_detalle").innerHTML =
    `<thead><tr><th>Concepto</th><th>Valor</th></tr></thead><tbody>` +
    filas.map(r => `<tr><td>${r[0]}</td><td>${r[1]}</td></tr>`).join("") + `</tbody>`;

  document.getElementById("tabla_comparativa_mod").innerHTML =
    `<thead><tr><th>Modalidad</th><th>IBC</th><th>Seg. Social + ARL</th><th>Retefuente</th><th>Neto en Bolsillo</th></tr></thead><tbody>` +
    comp.map(c => {
      const ss = c.salud_obligatoria_cop + c.pension_obligatoria_cop + c.fondo_solidaridad_pensional_cop + c.arl_cop;
      return `<tr>
        <td><strong>${c.modalidad_laboral}</strong></td>
        <td>${fmtCOP(c.ibc_cotizacion_cop)}</td>
        <td>${fmtCOP(ss)}</td>
        <td>${fmtCOP(c.retencion_fuente_cop)}</td>
        <td><strong>${fmtCOP(c.ingreso_neto_mensual_cop)}</strong></td>
      </tr>`;
    }).join("") + `</tbody>`;
}

function dibujarCurvaOportunidadSVG(fugas) {
  const hist = fugas.historial_capitalizacion_10a || [];
  if (!hist.length || fugas.fuga_total_mensual_cop <= 0) {
    document.getElementById("svg_oportunidad_wrap").innerHTML = "<p>Cero fugas registradas: ¡excelente eficiencia hidráulica!</p>";
    return;
  }
  const W = 540, H = 300, padL = 62, padR = 20, padT = 24, padB = 36;
  const maxY = Math.max(1, hist[hist.length - 1].saldo_final_cop);
  const xMap = (m) => padL + ((m - 1) / 119) * (W - padL - padR);
  const yMap = (v) => padT + (1 - v / maxY) * (H - padT - padB);

  const ptsGastado = hist.map(h => `${xMap(h.mes).toFixed(1)},${yMap(h.capital_acumulado_cop).toFixed(1)}`).join(" ");
  const ptsCompuesto = hist.map(h => `${xMap(h.mes).toFixed(1)},${yMap(h.saldo_final_cop).toFixed(1)}`).join(" ");

  let svg = `<svg viewBox="0 0 ${W} ${H}">`;
  [0, 0.25, 0.5, 0.75, 1].forEach(f => {
    const v = maxY * f;
    const y = yMap(v);
    svg += `<line x1="${padL}" y1="${y}" x2="${W - padR}" y2="${y}" stroke="#e2e8f0"/>`;
    svg += `<text x="${padL - 6}" y="${y + 4}" text-anchor="end" font-size="10" fill="#64748b">$${(v / 1e6).toFixed(1)}M</text>`;
  });

  svg += `<polyline fill="none" stroke="#dc2626" stroke-width="2.2" stroke-dasharray="5,4" points="${ptsGastado}"/>`;
  svg += `<polyline fill="none" stroke="#0f4c81" stroke-width="3" points="${ptsCompuesto}"/>`;

  const h60 = hist[59], h120 = hist[119];
  svg += `<circle cx="${xMap(60)}" cy="${yMap(h60.saldo_final_cop)}" r="4.5" fill="#0f4c81"/>`;
  svg += `<text x="${xMap(60) - 8}" y="${yMap(h60.saldo_final_cop) - 8}" text-anchor="end" font-size="10.5" font-weight="700" fill="#0f4c81">5a: ${fmtCOP(h60.saldo_final_cop)}</text>`;

  svg += `<circle cx="${xMap(120)}" cy="${yMap(h120.saldo_final_cop)}" r="5" fill="#15803d"/>`;
  svg += `<text x="${xMap(120) - 6}" y="${yMap(h120.saldo_final_cop) + 16}" text-anchor="end" font-size="11" font-weight="800" fill="#15803d">10a: ${fmtCOP(h120.saldo_final_cop)}</text>`;

  svg += `<text x="${W / 2}" y="${H - 8}" text-anchor="middle" font-size="11" fill="#475569">Horizonte en Meses (Rojo punteado: Gasto acumulado · Azul: Invertido al 10% EA)</text>`;
  svg += `</svg>`;
  document.getElementById("svg_oportunidad_wrap").innerHTML = svg;
}

function renderRegla503020(b) {
  const bloques = [
    { titulo: "50% Costos Fijos Vitales", d: b.necesidades_50, metaTxt: "&le; 50%", colorOk: "#2563eb", colorWarn: "#dc2626" },
    { titulo: "30% Estilo de Vida + Fugas Hormiga", d: b.estilo_vida_30, metaTxt: "&le; 30%", colorOk: "#7c3aed", colorWarn: "#d97706" },
    { titulo: "20% Excedente Libre (Ahorro / Inversión)", d: b.ahorro_patrimonio_20, metaTxt: "&ge; 20%", colorOk: "#16a34a", colorWarn: "#dc2626" }
  ];
  let html = bloques.map(x => {
    const pct = Math.max(0, Math.min(100, x.d.real_pct));
    const color = x.d.cumple ? x.colorOk : x.colorWarn;
    const badge = x.d.cumple
      ? `<span class="badge badge-ok">Cumple (${x.metaTxt})</span>`
      : `<span class="badge badge-warn">Ajustar (${x.metaTxt})</span>`;
    return `
      <div style="margin-bottom:14px;">
        <div style="display:flex; justify-content:space-between; align-items:center; font-size:12.5px; font-weight:700;">
          <span>${x.titulo}</span>
          <span>${fmtCOP(x.d.real_cop)} (${x.d.real_pct}%) ${badge}</span>
        </div>
        <div class="bar-track"><div class="bar-fill" style="width:${pct}%; background:${color};"></div></div>
        <div style="font-size:11.5px; color:var(--muted);">Referencia ideal sobre IDN: ${fmtCOP(x.d.meta_cop)}</div>
      </div>
    `;
  }).join("");

  if (b.servicio_deuda_cop > 0) {
    html += `<div style="font-size:12px; padding:8px 10px; background:#fef3c7; border-radius:6px; color:#78350f;">
      <strong>Servicio de Deuda Actual:</strong> ${fmtCOP(b.servicio_deuda_cop)} (${b.servicio_deuda_pct}% del IDN). Al liberar estas cuotas en el Módulo 3 (Catalina), pasarán directamente al bloque de Inversión.
    </div>`;
  }
  document.getElementById("panel_50_30_20").innerHTML = html;
}

function descargarContratoJSON() {
  if (!estadoUltimoResultado) return;
  const blob = new Blob([JSON.stringify(estadoUltimoResultado.contrato_oed, null, 2)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "perfil_mod1_oed.json";
  a.click();
}

window.addEventListener("DOMContentLoaded", () => {
  renderItemsHormiga();
  onModalidadChange();
});
</script>
</body>
</html>
"""


class Mod1RequestHandler(BaseHTTPRequestHandler):
    """Servidor HTTP local que conecta la UI con `src/mod1_presupuesto.py`."""

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        return  # Silenciar logs repetitivos en consola

    def _send_json(self, payload: Dict[str, Any], status: int = HTTPStatus.OK) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/", "/index.html"):
            raw = HTML_DASHBOARD.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return

        if self.path == "/api/health":
            self._send_json({"status": "ok", "modulo": "mod1_presupuesto"})
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Ruta no encontrada")

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/diagnostico":
            self.send_error(HTTPStatus.NOT_FOUND, "Endpoint no encontrado")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length).decode("utf-8")) if length > 0 else {}

            diagnostico = diagnosticar_presupuesto_y_flujo_caja(
                ingreso_bruto_mensual_cop=float(body.get("ingreso_bruto_mensual_cop", 0.0)),
                gastos_fijos_vitales_cop=float(body.get("gastos_fijos_vitales_cop", 0.0)),
                gastos_variables_estilo_vida_cop=float(body.get("gastos_variables_estilo_vida_cop", 0.0)),
                gastos_hormiga_mensual_cop=float(body.get("gastos_hormiga_mensual_cop", 0.0)),
                cuotas_deuda_mensual_cop=float(body.get("cuotas_deuda_mensual_cop", 0.0)),
                liquidez_actual_fondo_emergencia_cop=float(body.get("liquidez_actual_fondo_emergencia_cop", 0.0)),
                modalidad_laboral=str(body.get("modalidad_laboral", "Empleado")),
                aporte_voluntario_afc_fpv_cop=float(body.get("aporte_voluntario_afc_fpv_cop", 0.0)),
                clase_riesgo_arl=int(body.get("clase_riesgo_arl", 1)),
                otros_ingresos_mensuales_cop=float(body.get("otros_ingresos_mensuales_cop", 0.0)),
                cuotas_manejo_mensual_cop=float(body.get("cuotas_manejo_mensual_cop", 0.0)),
                monto_movimientos_gmf_mensual_cop=float(body.get("monto_movimientos_gmf_mensual_cop", 0.0)),
                cuenta_exenta_4x1000=bool(body.get("cuenta_exenta_4x1000", True)),
                detalle_gastos_hormiga=body.get("detalle_gastos_hormiga"),
                config=CONFIG_GLOBAL,
            )

            comparativa = comparar_modalidades_laborales(
                ingreso_bruto_mensual_cop=float(body.get("ingreso_bruto_mensual_cop", 0.0)),
                aporte_voluntario_afc_fpv_cop=float(body.get("aporte_voluntario_afc_fpv_cop", 0.0)),
                clase_riesgo_arl=int(body.get("clase_riesgo_arl", 1)),
                config=CONFIG_GLOBAL,
            )

            contrato_completo = ejecutar_modulo_1_perfil_usuario(body, config=CONFIG_GLOBAL)
            contrato_resumen = {
                "usuario_id": contrato_completo.get("usuario_id", "usr_oed_demo_001"),
                "modalidad_laboral": diagnostico["liquidacion_nomina"]["modalidad_laboral"],
                "ingreso_bruto_mensual_cop": diagnostico["liquidacion_nomina"]["ingreso_bruto_mensual_cop"],
                "ingreso_neto_mensual_cop": contrato_completo["ingreso_neto_mensual_cop"],
                "excedente_mensual_cop": contrato_completo["excedente_mensual_cop"],
                "meses_fondo_emergencia": contrato_completo["meses_fondo_emergencia"],
                "costo_oportunidad_hormiga_10a_cop": contrato_completo["costo_oportunidad_hormiga_10a_cop"],
                "estado_flujo_caja": diagnostico["estado_flujo_caja"],
                "aporte_disponible_portafolio_mod2_cop": diagnostico["plan_accion_flujo_caja"][
                    "aporte_disponible_portafolio_mod2_cop"
                ],
            }

            self._send_json(
                {
                    "diagnostico": diagnostico,
                    "comparativa_modalidades": comparativa,
                    "contrato_oed": contrato_resumen,
                }
            )
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)


def iniciar_servidor(host: str = "127.0.0.1", port: int = 8501, abrir_navegador: bool = True) -> None:
    url = f"http://{host}:{port}"
    server = ThreadingHTTPServer((host, port), Mod1RequestHandler)
    print("======================================================================", flush=True)
    print(" Interfaz Gráfica Local — Módulo 1 OED (Nidia Velásquez)", flush=True)
    print(f" URL activa: {url}", flush=True)
    print(" Presiona Ctrl+C para detener el servidor.", flush=True)
    print("======================================================================", flush=True)

    if abrir_navegador:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido correctamente.")
    finally:
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UI Local del Módulo 1 OED (Presupuesto y Gastos Hormiga)")
    parser.add_argument("--host", default="127.0.0.1", help="Host local (por defecto 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8501, help="Puerto local (por defecto 8501)")
    parser.add_argument("--no-browser", action="store_true", help="No abrir automáticamente el navegador")
    args = parser.parse_args()
    iniciar_servidor(host=args.host, port=args.port, abrir_navegador=not args.no_browser)
