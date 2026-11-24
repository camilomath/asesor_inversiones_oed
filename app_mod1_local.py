"""
Interfaz Gráfica Local Interactiva — Módulo 1 OED (Paso 2 — Nidia Velásquez).
Aplica íntegramente el Manual de Marca y Plantilla OED ("Asesor Financiero de Confianza"):
- Paleta Oficial OED (#0F294A, #1D4ED8, #EA580C, #15803D, #B45309, #B91C1C, #F4F7FB)
- Barra de Progreso de los 7 Pasos (Paso 2 activo) + Regla "Cero Palabras Huérfanas" (?)
- Diagnóstico Financiero + 📌 Plan de Acción para este Mes + Diccionario Financiero OED (5 Familias)
- Cierre de Asesoría con Reinicio en Ceros ($0), Impresión/PDF, Guardado (.html/.csv/.json),
  Lista Desplegable de Microgastos, Consejos de Ahorro y Guía de Abstención.
"""

from __future__ import annotations

import argparse
import html
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
    CATALOGO_MICROGASTOS_SUGERIDOS,
    cargar_simulacion_presupuesto,
    comparar_modalidades_laborales,
    culminar_asesoria_y_reiniciar,
    diagnosticar_presupuesto_y_flujo_caja,
    eliminar_simulacion_historial,
    guardar_simulacion_presupuesto,
)
from src.oed_design_system import (
    _CSS_MEDICO_AMIGO_OED,
    GLOSARIO_LENGUAJE_CLARO_OED,
    PALETA_MARCA_OED,
    RUTA_CLINICA_FINANCIERA_OED,
    enriquecer_texto_con_explicaciones,
)

CONFIG_GLOBAL = cargar_configuracion()


def _construir_bloque1_encabezado_oed() -> str:
    """Construye en HTML el Bloque 1 oficial del Manual de Marca OED para `paso_actual=2` (Nidia Velásquez)."""
    paso_actual = 2
    info = next((p for p in RUTA_CLINICA_FINANCIERA_OED if p["paso"] == paso_actual), RUTA_CLINICA_FINANCIERA_OED[2])
    saludo_rico = enriquecer_texto_con_explicaciones(info["saludo_medico"])
    pills = "".join(
        f'<span class="oed-step-pill {"oed-step-active" if p["paso"] == paso_actual else ""}">'
        f'Paso {p["paso"]}: {p["icono"]} {html.escape(p["titulo_ciudadano"])}</span>'
        for p in RUTA_CLINICA_FINANCIERA_OED
    )
    return f"""
    <div class="oed-top-wrap">
      <div class="oed-steps">{pills}</div>
      <div class="oed-header oed-header-flex">
        <div>
          <h1>{info["icono"]} Paso {info["paso"]} — {html.escape(info["titulo_ciudadano"])}</h1>
          <p>💼 <i>"{saludo_rico}"</i><br/>
          <small>Responsable OED en esta etapa: <b>{html.escape(info["responsable"])}</b> · {html.escape(info["modulo_tecnico"])} · Voz de <b>Asesor Financiero de Confianza</b></small></p>
        </div>
        <div class="presets">
          <button class="btn-preset" onclick="cargarEscenario('ceros')">🔄 En Ceros ($0)</button>
          <button class="btn-preset" onclick="cargarEscenario('semilla')">Semilla OED ($6.5M)</button>
          <button class="btn-preset" onclick="cargarEscenario('joven')">&le; 2 SMMLV ($2.5M)</button>
          <button class="btn-preset" onclick="cargarEscenario('ops')">Independiente OPS ($8.5M)</button>
          <button class="btn-preset" onclick="cargarEscenario('integral')">Integral + AFC ($20M)</button>
          <button class="btn-preset" onclick="cargarEscenario('deficit')">Riesgo Alto (FA-01)</button>
        </div>
      </div>
    </div>
    """


ENCABEZADO_BLOQUE1_HTML = _construir_bloque1_encabezado_oed()
GLOSARIO_OED_JSON = json.dumps(GLOSARIO_LENGUAJE_CLARO_OED, ensure_ascii=False)
PALETA_OED_JSON = json.dumps(PALETA_MARCA_OED, ensure_ascii=False)

HTML_DASHBOARD = (
    r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Paso 2 OED — Análisis de tu Sueldo, Gastos y Flujo de Caja (Nidia Velásquez)</title>
"""
    + _CSS_MEDICO_AMIGO_OED
    + r"""
<style>
  :root {
    --bg: #F4F7FB;
    --card: rgba(255, 255, 255, 0.95);
    --border: #CBD5E1;
    --text: #0F294A;
    --muted: #475569;
    --navy-oed: #0F294A;
    --blue-oed: #1D4ED8;
    --blue-light: #EFF6FF;
    --orange-oed: #EA580C;
    --green-oed: #15803D;
    --green-bg: #F0FDF4;
    --amber-oed: #B45309;
    --amber-bg: #FFFBEB;
    --red-oed: #B91C1C;
    --red-bg: #FEF2F2;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: "Segoe UI", system-ui, -apple-system, Roboto, Arial, sans-serif;
    background-color: var(--bg);
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='170' height='170' viewBox='0 0 160 160'%3E%3Cg fill='none' stroke='%230F294A' stroke-opacity='0.09' stroke-width='2.1'%3E%3Ccircle cx='80' cy='32' r='13' fill='%23FEF08A' fill-opacity='0.32' stroke='%23EA580C' stroke-opacity='0.22'/%3E%3Ctext x='80' y='37' text-anchor='middle' font-family='Segoe UI,Arial' font-weight='bold' font-size='14' fill='%23EA580C' fill-opacity='0.35' stroke='none'%3E%24%3C/text%3E%3Cpath d='M68 51h24' stroke-linecap='round'/%3E%3Cellipse cx='80' cy='86' rx='34' ry='25' fill='%23DBEAFE' fill-opacity='0.25'/%3E%3Cpath d='M113 80h8a4 4 0 0 1 4 4v6a4 4 0 0 1-4 4h-8'/%3E%3Cpath d='M56 65l-9-11 15 3'/%3E%3Cpath d='M62 108v12M96 108v12' stroke-linecap='round'/%3E%3Cpath d='M46 86c-6-2-8-8-4-11' stroke-linecap='round'/%3E%3Ccircle cx='98' cy='78' r='2.5' fill='%231D4ED8' fill-opacity='0.25' stroke='none'/%3E%3C/g%3E%3C/svg%3E");
    background-attachment: fixed;
    color: var(--text);
    font-size: 13.5px;
    line-height: 1.48;
    min-height: 100vh;
  }
  .watermark-ahorro {
    position: fixed; right: 24px; bottom: 16px; width: 300px; height: 300px;
    pointer-events: none; z-index: 0; opacity: 0.18;
  }
  .oed-top-wrap, .toolbar-asesoria, .layout, .glosario-footer-wrap {
    position: relative; z-index: 1; max-width: 1640px; margin: 0 auto; padding: 0 20px;
  }
  .oed-top-wrap { padding-top: 14px; }
  .oed-header-flex {
    display: flex; flex-wrap: wrap; justify-content: space-between;
    align-items: center; gap: 14px; margin-bottom: 10px !important;
    box-shadow: 0 4px 14px rgba(15, 41, 74, 0.14);
  }
  .presets { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
  .btn-preset {
    background: rgba(255,255,255,0.16); color: #fff;
    border: 1px solid rgba(255,255,255,0.34); border-radius: 999px;
    padding: 5px 11px; font-size: 11.5px; font-weight: 600; cursor: pointer; transition: all 0.15s;
  }
  .btn-preset:hover { background: #EA580C; border-color: #EA580C; transform: translateY(-1px); }

  .toolbar-inner {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 12px; padding: 10px 15px; display: flex; flex-wrap: wrap;
    justify-content: space-between; align-items: center; gap: 10px;
    box-shadow: 0 2px 8px rgba(15, 41, 74, 0.05);
  }
  .client-box { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
  .client-box input {
    width: 235px; padding: 6px 10px; border: 1px solid var(--border);
    border-radius: 7px; font-size: 12.5px; color: var(--navy-oed);
  }
  .toolbar-actions { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
  .btn-tool {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 7px 13px; border-radius: 8px; font-size: 12px; font-weight: 700;
    cursor: pointer; border: 1px solid var(--border); background: #fff; color: var(--navy-oed);
    transition: all 0.15s;
  }
  .btn-tool:hover { background: var(--blue-light); border-color: var(--blue-oed); color: var(--blue-oed); }
  .btn-tool.print { background: var(--navy-oed); color: #fff; border-color: var(--navy-oed); }
  .btn-tool.print:hover { opacity: 0.92; color: #fff; }
  .btn-tool.save-file { background: var(--blue-oed); color: #fff; border-color: var(--blue-oed); }
  .btn-tool.save-file:hover { opacity: 0.92; color: #fff; }
  .btn-tool.finish {
    background: var(--orange-oed); color: #fff; border-color: var(--orange-oed);
    box-shadow: 0 2px 8px rgba(234, 88, 12, 0.28);
  }
  .btn-tool.finish:hover { opacity: 0.94; transform: translateY(-1px); color: #fff; }

  .dropdown-save { position: relative; display: inline-block; }
  .dropdown-menu {
    display: none; position: absolute; right: 0; top: calc(100% + 4px);
    background: #fff; border: 1px solid var(--border); border-radius: 9px;
    box-shadow: 0 8px 22px rgba(15,41,74,0.18); min-width: 250px; z-index: 999; overflow: hidden;
  }
  .dropdown-menu.open { display: block; }
  .dropdown-menu button {
    width: 100%; text-align: left; padding: 9px 13px; border: none;
    border-bottom: 1px solid #F1F5F9; background: #fff; font-size: 12px;
    font-weight: 600; cursor: pointer; color: var(--navy-oed);
  }
  .dropdown-menu button:hover { background: var(--blue-light); color: var(--blue-oed); }

  .layout {
    display: grid; grid-template-columns: 405px 1fr; gap: 16px;
    padding-top: 12px; padding-bottom: 14px;
  }
  @media (max-width: 1100px) { .layout { grid-template-columns: 1fr; } }
  .panel {
    background: var(--card); backdrop-filter: blur(5px);
    border: 1px solid #DDE4EE; border-radius: 13px; padding: 15px;
    box-shadow: 0 2px 8px rgba(15, 41, 74, 0.05);
  }
  .section-title {
    font-size: 13px; font-weight: 800; text-transform: uppercase;
    letter-spacing: 0.35px; color: var(--navy-oed); margin: 0 0 10px;
    padding-bottom: 5px; border-bottom: 2px solid var(--blue-light);
    display: flex; justify-content: space-between; align-items: center;
  }
  .save-pill {
    font-size: 11px; font-weight: 700; text-transform: none;
    padding: 2px 9px; border-radius: 999px; background: var(--green-bg);
    color: var(--green-oed); border: 1px solid #86EFAC;
  }
  .field { margin-bottom: 9px; }
  .field label {
    display: flex; justify-content: space-between; font-weight: 600;
    font-size: 12px; margin-bottom: 3px; color: var(--navy-oed);
  }
  .val-hint { color: var(--blue-oed); font-family: ui-monospace, Consolas, monospace; font-weight: 700; }
  input[type="number"], input[type="text"], select {
    width: 100%; padding: 6px 8px; border: 1px solid var(--border);
    border-radius: 7px; font-size: 12.5px; background: #fff; color: var(--navy-oed);
  }
  input[type="range"] { width: 100%; accent-color: var(--blue-oed); margin-top: 2px; cursor: pointer; }
  .row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
  .save-box {
    background: var(--blue-light); border: 1px solid #BFDBFE; border-radius: 9px;
    padding: 9px 10px; margin: 8px 0 12px;
  }
  .btn-save {
    width: 100%; background: var(--blue-oed); color: #fff; border: none;
    border-radius: 7px; padding: 7px 10px; font-size: 12px; font-weight: 700;
    cursor: pointer; margin-top: 5px;
  }
  .btn-save:hover { opacity: 0.92; }

  .micro-select-box {
    background: #F8FAFC; border: 1px solid var(--border); border-radius: 9px;
    padding: 8px 9px; margin-bottom: 8px;
  }
  .micro-select-row { display: grid; grid-template-columns: 1fr auto; gap: 6px; margin-top: 4px; }
  .hormiga-list { display: flex; flex-direction: column; gap: 5px; margin-bottom: 7px; }
  .hormiga-item {
    display: grid; grid-template-columns: 1.45fr 0.85fr 0.55fr 0.8fr 24px;
    gap: 4px; align-items: center;
  }
  .hormiga-item input { padding: 4px 6px; font-size: 11.5px; }
  .sub-pill { font-size: 11px; font-family: monospace; text-align: right; color: var(--red-oed); font-weight: 700; }
  .btn-del {
    background: var(--red-bg); color: var(--red-oed); border: 1px solid #FCA5A5;
    border-radius: 5px; height: 25px; cursor: pointer; font-weight: bold;
  }

  .opt-bar {
    background: linear-gradient(90deg, #EFF6FF 0%, #FFF7ED 100%);
    border: 1px solid #BFDBFE; border-radius: 12px; padding: 11px 14px;
    margin-bottom: 13px; display: grid; grid-template-columns: 1.1fr 1.1fr 1.4fr;
    gap: 14px; align-items: center;
  }
  @media (max-width: 1150px) { .opt-bar { grid-template-columns: 1fr; } }
  .btn-action {
    background: var(--blue-oed); color: #fff; border: none; border-radius: 7px;
    padding: 6px 10px; font-size: 11.5px; font-weight: 700; cursor: pointer;
  }

  .kpis {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(185px, 1fr));
    gap: 10px; margin-bottom: 14px;
  }
  .kpi {
    background: var(--card); border: 1px solid #DDE4EE; border-radius: 12px;
    padding: 11px 13px; border-top: 3px solid var(--navy-oed);
  }
  .kpi .k-label { font-size: 11px; font-weight: 700; color: var(--muted); text-transform: uppercase; }
  .kpi .k-val { font-size: 18.5px; font-weight: 800; margin: 3px 0; font-family: ui-monospace, Consolas, monospace; color: var(--navy-oed); }
  .kpi .k-sub { font-size: 11px; color: var(--muted); }

  .coaching-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px;
  }
  @media (max-width: 1100px) { .coaching-grid { grid-template-columns: 1fr; } }
  .coach-card {
    background: var(--card); border: 1px solid #DDE4EE; border-radius: 12px;
    padding: 13px 15px; box-shadow: 0 2px 6px rgba(15,41,74,0.04);
  }
  .coach-card.ahorro { border-top: 4px solid var(--green-oed); }
  .coach-card.abstenerse { border-top: 4px solid var(--red-oed); }
  .tip-item {
    padding: 8px 10px; border-radius: 9px; margin-bottom: 8px;
    background: var(--green-bg); border: 1px solid #BBF7D0; font-size: 12px;
  }
  .abs-item {
    padding: 8px 10px; border-radius: 9px; margin-bottom: 8px;
    background: var(--red-bg); border: 1px solid #FECACA; font-size: 12px;
  }
  .abs-item.MEDIA { background: var(--amber-bg); border-color: #FDE68A; }
  .abs-item.PREVENTIVA { background: #F8FAFC; border-color: var(--border); }

  .tabs { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }
  .tab-btn {
    padding: 7px 13px; border-radius: 999px; border: 1px solid var(--border);
    background: #fff; color: var(--muted); font-weight: 700; font-size: 12px; cursor: pointer;
  }
  .tab-btn.active { background: var(--orange-oed); color: #fff; border-color: var(--orange-oed); }
  .tab-pane { display: none; }
  .tab-pane.active { display: block; }
  .charts-2col { display: grid; grid-template-columns: 1.12fr 1fr; gap: 14px; }
  @media (max-width: 1180px) { .charts-2col { grid-template-columns: 1fr; } }
  table { width: 100%; border-collapse: collapse; font-size: 12px; }
  th, td { padding: 7px 9px; border-bottom: 1px solid #E2E8F0; text-align: right; }
  th:first-child, td:first-child { text-align: left; }
  th { background: #F1F5F9; font-weight: 700; color: var(--navy-oed); }
  .bar-track { width: 100%; height: 11px; background: #E2E8F0; border-radius: 999px; overflow: hidden; margin: 4px 0; }
  .bar-fill { height: 100%; border-radius: 999px; transition: width 0.2s ease; }
  pre.json-box { background: var(--navy-oed); color: #F8FAFC; padding: 13px; border-radius: 9px; overflow-x: auto; font-size: 12px; max-height: 410px; margin: 0; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 10.5px; font-weight: 700; }
  .badge-ok { background: var(--green-bg); color: var(--green-oed); }
  .badge-warn { background: var(--amber-bg); color: var(--amber-oed); }
  .badge-err { background: var(--red-bg); color: var(--red-oed); }
  .btn-mini { padding: 4px 9px; border-radius: 6px; border: 1px solid var(--border); background: #fff; cursor: pointer; font-size: 11px; font-weight: 600; color: var(--navy-oed); }
  .btn-mini:hover { background: var(--blue-light); color: var(--blue-oed); }
  svg { width: 100%; height: auto; display: block; }
  .svg-hover { cursor: pointer; transition: opacity 0.15s; }
  .svg-hover:hover { opacity: 0.82; }
  #floating_tooltip {
    position: fixed; pointer-events: none; z-index: 9999; display: none;
    background: #0F294A; color: #fff; padding: 8px 11px;
    border-radius: 8px; font-size: 11.5px; box-shadow: 0 6px 16px rgba(15,41,74,0.3);
    max-width: 265px; line-height: 1.38;
  }

  /* Bloque 5: Diccionario Financiero OED Desplegable */
  .glosario-footer-wrap { padding-bottom: 28px; }
  details.oed-glosario-details {
    background: var(--card); border: 1px solid #DDE4EE; border-radius: 13px;
    padding: 12px 16px; box-shadow: 0 2px 8px rgba(15,41,74,0.05);
  }
  details.oed-glosario-details summary {
    cursor: pointer; font-weight: 800; font-size: 14px; color: var(--navy-oed);
    list-style: none; display: flex; justify-content: space-between; align-items: center;
  }
  .glosario-pill {
    display: inline-block; padding: 4px 10px; border-radius: 999px; font-size: 11.5px;
    border: 1px solid var(--border); margin: 3px; cursor: pointer; background: #fff; color: var(--navy-oed);
  }
  .glosario-pill.sel { background: var(--blue-oed); color: #fff; border-color: var(--blue-oed); font-weight: 700; }

  .modal-backdrop {
    display: none; position: fixed; inset: 0; background: rgba(15,41,74,0.58);
    z-index: 5000; align-items: center; justify-content: center; padding: 16px;
  }
  .modal-backdrop.open { display: flex; }
  .modal-card {
    background: #fff; border-radius: 13px; max-width: 520px; width: 100%;
    padding: 20px; box-shadow: 0 16px 40px rgba(15,41,74,0.28); border: 1px solid var(--border);
  }

  .print-only-header { display: none; }
  @media print {
    body { background: #fff !important; background-image: none !important; font-size: 11.5px; }
    .oed-top-wrap, .toolbar-asesoria, aside.panel, .opt-bar, .tabs, .watermark-ahorro, #floating_tooltip, .modal-backdrop, .glosario-footer-wrap {
      display: none !important;
    }
    .print-only-header {
      display: block !important; border-bottom: 2px solid #0F294A;
      padding-bottom: 8px; margin-bottom: 12px;
    }
    .layout { display: block !important; padding: 0 !important; max-width: 100% !important; }
    .panel, .coach-card, .kpi, .oed-doc-card, .oed-rx-box { box-shadow: none !important; break-inside: avoid; background: #fff !important; }
    .tab-pane { display: block !important; margin-bottom: 16px; break-inside: avoid; }
    #tab_guardados, #tab_contrato { display: none !important; }
  }
</style>
</head>
<body>

<div id="floating_tooltip"></div>

<div class="watermark-ahorro" aria-hidden="true">
  <svg viewBox="0 0 220 220" xmlns="http://www.w3.org/2000/svg">
    <g fill="none" stroke="#0F294A" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="112" cy="44" r="24" fill="#FEF08A" stroke="#EA580C"/>
      <text x="112" y="53" text-anchor="middle" font-family="Segoe UI,Arial" font-weight="900" font-size="28" fill="#EA580C" stroke="none">$</text>
      <path d="M92 78h40"/>
      <ellipse cx="110" cy="132" rx="62" ry="46" fill="#DBEAFE"/>
      <path d="M170 122h16a8 8 0 0 1 8 8v12a8 8 0 0 1-8 8h-15"/>
      <path d="M72 95l-16-22 28 7"/><path d="M80 172v22M138 172v22"/>
      <path d="M48 132c-12-4-16-16-8-22"/>
      <circle cx="144" cy="116" r="4.5" fill="#1D4ED8" stroke="none"/>
    </g>
  </svg>
</div>

<!-- BLOQUE 1 OFICIAL OED: BARRA DE PROGRESO (PASOS 0 AL 6) + ENCABEZADO DEL ASESOR DE CONFIANZA -->
"""
    + ENCABEZADO_BLOQUE1_HTML
    + r"""

<!-- BARRA DE GESTIÓN DE LA ASESORÍA: IMPRIMIR, GUARDAR ARCHIVO Y CULMINAR EN CEROS -->
<div class="toolbar-asesoria">
  <div class="toolbar-inner">
    <div class="client-box">
      <strong style="color:var(--navy-oed); font-size:12.5px;">👤 Persona Asesorada:</strong>
      <input type="text" id="nombre_asesorado_top" placeholder="Nombre del asesorado o sesión..." />
      <span id="badge_autoguardado" class="save-pill">Sesión lista</span>
    </div>
    <div class="toolbar-actions">
      <button class="btn-tool print" onclick="imprimirAsesoria()">🖨️ Imprimir / Guardar PDF</button>

      <div class="dropdown-save">
        <button class="btn-tool save-file" onclick="toggleMenuGuardar(event)">💾 Guardar Archivo ▾</button>
        <div id="menu_guardar_archivo" class="dropdown-menu">
          <button onclick="guardarInformeHTML()">📄 Guardar Acta Completa (.html)</button>
          <button onclick="exportarCSV()">📊 Guardar Tabla en Excel (.csv)</button>
          <button onclick="descargarContratoJSON()">🗂️ Guardar Expediente JSON (.json)</button>
        </div>
      </div>

      <button class="btn-tool finish" onclick="abrirModalCulminar()">✅ Culminar Asesoría (Reiniciar en $0)</button>
    </div>
  </div>
</div>

<div class="layout">
  <!-- BLOQUE 2 OFICIAL OED: DATOS DE LA PERSONA CON EXPLICACIONES (?) -->
  <aside class="panel">
    <h2 class="section-title"><span>⚙️ 1. Tu Sueldo y Modalidad</span></h2>

    <div class="row-2">
      <div class="field">
        <label><span>Modalidad (<span class="oed-term" tabindex="0" data-tip="💡 IBC (Ingreso Base de Cotización): Base sobre la cual cotizas Salud, Pensión y ARL. En OPS es el 40% de tus honorarios.">IBC<sup class="oed-q">?</sup></span>)</span></label>
        <select id="modalidad_laboral" onchange="onNominaChanged()">
          <option value="Empleado">Empleado Ordinario</option>
          <option value="Integral">Salario Integral (&ge;13 SMMLV)</option>
          <option value="Independiente">Independiente / OPS (IBC 40%)</option>
        </select>
      </div>
      <div class="field">
        <label>Clase ARL (OPS)</label>
        <select id="clase_riesgo_arl" onchange="onNominaChanged()">
          <option value="1">Clase I (0.522%)</option>
          <option value="2">Clase II (1.044%)</option>
          <option value="3">Clase III (2.436%)</option>
          <option value="4">Clase IV (4.350%)</option>
          <option value="5">Clase V (6.960%)</option>
        </select>
      </div>
    </div>

    <div class="field">
      <label><span>Tu Ingreso Bruto Mensual</span> <span class="val-hint" id="lbl_bruto">$0</span></label>
      <input type="number" id="ingreso_bruto" step="100000" min="0" value="0" oninput="syncPair('ingreso_bruto','rng_bruto'); onNominaChanged();" />
      <input type="range" id="rng_bruto" min="0" max="35000000" step="100000" value="0" oninput="syncPair('rng_bruto','ingreso_bruto'); onNominaChanged();" />
    </div>

    <div class="row-2">
      <div class="field">
        <label>Otros Ingresos</label>
        <input type="number" id="otros_ingresos" step="50000" min="0" value="0" oninput="onNominaChanged()" />
      </div>
      <div class="field">
        <label><span><span class="oed-term" tabindex="0" data-tip="💡 Cuenta AFC: Ahorro para vivienda que reduce tu retención en la fuente medida en UVT.">Cuenta AFC<sup class="oed-q">?</sup></span> / FPV</span> <span class="val-hint" id="lbl_afc">$0</span></label>
        <input type="number" id="aporte_afc" step="50000" min="0" value="0" oninput="syncPair('aporte_afc','rng_afc'); onNominaChanged();" />
        <input type="range" id="rng_afc" min="0" max="6000000" step="50000" value="0" oninput="syncPair('rng_afc','aporte_afc'); onNominaChanged();" />
      </div>
    </div>

    <div class="save-box">
      <label style="font-size:11.5px; font-weight:800; color:var(--navy-oed); display:block; margin-bottom:4px;">
        💾 Guardar Cambio de Salario y Modalidad
      </label>
      <input type="text" id="nombre_escenario" placeholder="Etiqueta opcional (ej. Oferta Laboral)" style="font-size:12px; padding:5px 8px;" />
      <button class="btn-save" onclick="guardarEscenarioManual()">💾 Guardar en Historial de Asesorías</button>
      <div id="msg_guardado_detalle" style="font-size:11px; color:var(--blue-oed); margin-top:5px; font-weight:600;">
        Auto-guardado local activo.
      </div>
      <div id="mini_historial_sidebar" style="margin-top:6px; font-size:11px;"></div>
    </div>

    <h2 class="section-title"><span>🏠 2. Tus Gastos y Fondo de Emergencia</span></h2>
    <div class="field">
      <label>Costos Fijos Vitales <span class="val-hint" id="lbl_fijos">$0</span></label>
      <input type="number" id="gastos_fijos" step="50000" min="0" value="0" oninput="syncPair('gastos_fijos','rng_fijos'); onNominaChanged();" />
      <input type="range" id="rng_fijos" min="0" max="15000000" step="50000" value="0" oninput="syncPair('rng_fijos','gastos_fijos'); onNominaChanged();" />
    </div>
    <div class="row-2">
      <div class="field">
        <label>Estilo de Vida</label>
        <input type="number" id="gastos_variables" step="50000" min="0" value="0" oninput="onNominaChanged()" />
      </div>
      <div class="field">
        <label>Cuotas de Deuda</label>
        <input type="number" id="cuotas_deuda" step="50000" min="0" value="0" oninput="onNominaChanged()" />
      </div>
    </div>
    <div class="field">
      <label><span>Liquidez Actual (<span class="oed-term" tabindex="0" data-tip="💡 Seguro Fogafín: Protege tus ahorros bancarios gratuitamente hasta por $50.000.000 COP.">Fogafín<sup class="oed-q">?</sup></span>)</span> <span class="val-hint" id="lbl_liq">$0</span></label>
      <input type="number" id="liquidez_emergencia" step="200000" min="0" value="0" oninput="syncPair('liquidez_emergencia','rng_liq'); onNominaChanged();" />
      <input type="range" id="rng_liq" min="0" max="50000000" step="250000" value="0" oninput="syncPair('rng_liq','liquidez_emergencia'); onNominaChanged();" />
    </div>

    <h2 class="section-title" style="margin-top:12px;">
      <span>🐜 3. Lista Desplegable de Microgastos</span>
      <button class="btn-mini" onclick="vaciarMicrogastos()">Vaciar</button>
    </h2>

    <div class="micro-select-box">
      <label style="font-size:11.5px; font-weight:700; color:var(--navy-oed); display:block;">
        📋 Elige tus gastos hormiga cotidianos:
      </label>
      <div class="micro-select-row">
        <select id="select_microgasto" onchange="agregarDesdeDropdown()">
          <option value="">-- Selecciona un microgasto de la lista --</option>
        </select>
        <button class="btn-mini" style="background:var(--blue-oed); color:#fff; border-color:var(--blue-oed);" onclick="agregarDesdeDropdown(true)">+ Agregar</button>
      </div>
      <div id="hint_sustituto_micro" style="font-size:11px; color:var(--green-oed); margin-top:5px; display:none;"></div>
    </div>

    <div id="encabezado_hormiga" style="display:none; font-size:10.5px; color:var(--muted); font-weight:700; margin-bottom:3px; padding:0 2px;">
      Concepto · Unitario ($) · Veces/mes · Subtotal
    </div>
    <div id="lista_hormiga" class="hormiga-list"></div>

    <div class="row-2" style="margin-top:8px;">
      <div class="field">
        <label>Cuotas Manejo</label>
        <input type="number" id="cuotas_manejo" step="5000" min="0" value="0" oninput="onNominaChanged()" />
      </div>
      <div class="field">
        <label><span>Retiros <span class="oed-term" tabindex="0" data-tip="💡 4x1000 (GMF): Impuesto de $4 por cada $1.000 retirados. Puedes marcar 1 cuenta exenta hasta 350 UVT/mes.">4x1000<sup class="oed-q">?</sup></span></span></label>
        <input type="number" id="movimientos_gmf" step="100000" min="0" value="0" oninput="onNominaChanged()" />
      </div>
    </div>
    <label style="display:flex; align-items:center; gap:6px; font-size:11.5px; cursor:pointer; margin-bottom:10px;">
      <input type="checkbox" id="cuenta_exenta" checked onchange="onNominaChanged()" />
      Cuenta marcada exenta de 4x1000 (350 UVT/mes)
    </label>

    <button class="btn-tool finish" style="width:100%; justify-content:center; padding:9px;" onclick="abrirModalCulminar()">
      ✅ Culminar Asesoría e Iniciar en Ceros ($0)
    </button>
  </aside>

  <main>
    <div class="print-only-header">
      <h2 style="margin:0; color:#0F294A;">💼 Paso 2 OED — Diagnóstico de tu Sueldo, Gastos y Plan de Acción</h2>
      <div id="print_meta_info" style="font-size:12px; color:#334155; margin-top:4px;"></div>
    </div>

    <!-- BLOQUE 3 OFICIAL OED: DIAGNÓSTICO FINANCIERO (?) + 📌 PLAN DE ACCIÓN PARA ESTE MES -->
    <div id="oed_semaforo_box" class="oed-doc-card oed-doc-azul">
      Cargando análisis de tu Asesor Financiero de Confianza...
    </div>
    <div id="oed_plan_mes_box" class="oed-rx-box">
      <b>📌 Plan de Acción para este Mes:</b> Ingresa tus datos para recibir tu acción concreta en pesos colombianos ($ COP).
    </div>
    <div id="alerta_normativa_box" style="display:none;" class="oed-doc-card oed-doc-rojo"></div>

    <!-- OPTIMIZADOR INTERACTIVO EN VIVO -->
    <section class="opt-bar">
      <div>
        <label style="display:flex; justify-content:space-between; font-size:12px; font-weight:700; color:var(--navy-oed);">
          <span>🔧 Simulador Recorte Hormiga:</span>
          <span id="lbl_recorte_pct" style="color:var(--blue-oed);">50%</span>
        </label>
        <input type="range" id="rng_recorte_hormiga" min="0" max="100" step="5" value="50" oninput="recalcular()" />
        <div style="font-size:11px; color:var(--muted);" id="sub_recorte_info">Rescata $0/mes adicionales</div>
      </div>
      <div>
        <label style="display:flex; justify-content:space-between; font-size:12px; font-weight:700; color:var(--navy-oed);">
          <span>📈 Tasa Objetivo (<span class="oed-term" tabindex="0" data-tip="💡 Tasa Efectiva Anual (EA): Velocidad real a la que crece tu ahorro al cumplir 12 meses.">EA<sup class="oed-q">?</sup></span>):</span>
          <span id="lbl_tasa_ea" style="color:var(--green-oed);">10.0% EA</span>
        </label>
        <input type="range" id="rng_tasa_ea" min="5" max="18" step="0.5" value="10" oninput="recalcular()" />
        <div style="font-size:11px; color:var(--muted);" id="sub_tasa_info">Patrimonio rescatado 10a: $0</div>
      </div>
      <div style="display:flex; flex-direction:column; gap:5px;">
        <div id="box_opt_afc" style="font-size:11.5px; color:var(--navy-oed);">Evaluando beneficio tributario...</div>
        <div style="display:flex; gap:6px; flex-wrap:wrap;">
          <button id="btn_aplicar_afc" class="btn-action" style="display:none;" onclick="aplicarAfcOptimo()">⚡ Aplicar AFC Óptimo</button>
          <button id="btn_cero_bancos" class="btn-action" style="background:var(--green-oed); display:none;" onclick="optimizarBancos()">🛡️ Cero Costos Bancarios</button>
        </div>
      </div>
    </section>

    <!-- INDICADORES CLAVE OED -->
    <section class="kpis">
      <div class="kpi" style="border-top-color:var(--navy-oed);">
        <div class="k-label">Ingreso Disponible Neto</div>
        <div class="k-val" id="kpi_idn">$0</div>
        <div class="k-sub" id="kpi_idn_sub">Descuentos ley: $0</div>
      </div>
      <div class="kpi" style="border-top-color:var(--green-oed);">
        <div class="k-label">Excedente Mensual Libre</div>
        <div class="k-val" id="kpi_excedente">$0</div>
        <div class="k-sub" id="kpi_excedente_sub">Optimizado: $0</div>
      </div>
      <div class="kpi" style="border-top-color:var(--orange-oed);">
        <div class="k-label">Fondo de Emergencia</div>
        <div class="k-val" id="kpi_emergencia">0.0 meses</div>
        <div class="bar-track"><div id="bar_emergencia" class="bar-fill" style="width:0%; background:#15803D;"></div></div>
        <div class="k-sub" id="kpi_emergencia_sub">Meta: 3 meses</div>
      </div>
      <div class="kpi" style="border-top-color:var(--red-oed);">
        <div class="k-label">Gastos Hormiga + 4x1000</div>
        <div class="k-val" id="kpi_fugas" style="color:var(--red-oed);">$0</div>
        <div class="k-sub" id="kpi_fugas_sub">0% del ingreso neto</div>
      </div>
      <div class="kpi" style="border-top-color:var(--blue-oed);">
        <div class="k-label">Costo Oportunidad 10 Años</div>
        <div class="k-val" id="kpi_oportunidad" style="color:var(--blue-oed);">$0</div>
        <div class="k-sub" id="kpi_oportunidad_sub">A 5 años: $0</div>
      </div>
    </section>

    <!-- CONSEJOS DE AHORRO Y GUÍA DE ABSTENCIÓN CON BURBUJAS (?) -->
    <section class="coaching-grid">
      <div class="coach-card ahorro">
        <h3 class="section-title" style="color:var(--green-oed); border-bottom-color:#BBF7D0;">
          <span>💡 Consejos de tu Asesor para Ahorrar Más</span>
          <span id="badge_meta_ahorro" class="badge badge-ok">Meta 20%: $0</span>
        </h3>
        <div id="contenedor_consejos_ahorro"></div>
      </div>

      <div class="coach-card abstenerse">
        <h3 class="section-title" style="color:var(--red-oed); border-bottom-color:#FECACA;">
          <span>🛑 ¿En Qué Te Recomendamos Abstenerte Hoy?</span>
          <span id="badge_num_abstenciones" class="badge badge-err">0 alertas</span>
        </h3>
        <div id="contenedor_abstenciones"></div>
      </div>
    </section>

    <!-- BLOQUE 4 OFICIAL OED: GRÁFICAS INTERACTIVAS CON LA PALETA OFICIAL OED -->
    <div class="panel">
      <div class="tabs">
        <button class="tab-btn active" id="btn_tab_flujos" onclick="activarTab('tab_flujos', this)">1. 📊 Flujo Sankey &amp; Cascada OED</button>
        <button class="tab-btn" id="btn_tab_nomina" onclick="activarTab('tab_nomina', this)">2. 💼 Desglose Salarial &amp; Modalidades</button>
        <button class="tab-btn" id="btn_tab_hormiga" onclick="activarTab('tab_hormiga', this)">3. 🌱 Interés Compuesto 10a, Pareto &amp; 50/30/20</button>
        <button class="tab-btn" id="btn_tab_guardados" onclick="activarTab('tab_guardados', this)">4. 🗂️ Historial de Asesorías (<span id="contador_historial">0</span>)</button>
        <button class="tab-btn" id="btn_tab_contrato" onclick="activarTab('tab_contrato', this)">5. 🔗 Contrato JSON OED</button>
      </div>

      <div id="tab_flujos" class="tab-pane active">
        <div class="charts-2col">
          <div>
            <h3 class="section-title"><span>Flujo de tu Sueldo al Ahorro (Paleta Oficial OED)</span></h3>
            <div id="svg_sankey_wrap"></div>
          </div>
          <div>
            <h3 class="section-title"><span>Paso a Paso: Del Sueldo Bruto al Excedente ($ COP)</span></h3>
            <div id="svg_waterfall_wrap"></div>
          </div>
        </div>
      </div>

      <div id="tab_nomina" class="tab-pane">
        <div class="charts-2col">
          <div>
            <h3 class="section-title"><span>Liquidación de tu Ingreso Neto Mensual</span></h3>
            <table id="tabla_nomina_detalle"></table>
          </div>
          <div>
            <h3 class="section-title"><span>Comparativa: Empleado vs. Integral vs. Independiente OPS</span></h3>
            <table id="tabla_comparativa_mod"></table>
          </div>
        </div>
      </div>

      <div id="tab_hormiga" class="tab-pane">
        <div class="charts-2col">
          <div>
            <h3 class="section-title"><span>Proyección con Interés Compuesto Mes a Mes (10 Años)</span></h3>
            <div id="svg_oportunidad_wrap"></div>
            <h3 class="section-title" style="margin-top:12px;"><span>Pareto 80/20 de Microgastos y Costos Bancarios</span></h3>
            <table id="tabla_pareto"></table>
          </div>
          <div>
            <h3 class="section-title"><span>Balance 50 / 30 / 20 y Escenario Optimizado</span></h3>
            <div id="panel_50_30_20"></div>
          </div>
        </div>
      </div>

      <div id="tab_guardados" class="tab-pane">
        <h3 class="section-title"><span>Comparador Visual e Historial de Asesorías Guardadas</span></h3>
        <div id="grafico_comparador_guardados" style="margin-bottom:14px;"></div>
        <div id="contenedor_tabla_historial"></div>
      </div>

      <div id="tab_contrato" class="tab-pane">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:10px;">
          <h3 class="section-title" style="margin:0; border:none;"><span>Integración con los Módulos 2, 3, 4 y 5</span></h3>
          <div style="display:flex; gap:6px;">
            <button class="btn-mini" id="btn_copiar_json" onclick="copiarContratoJSON()">📋 Copiar JSON</button>
            <button class="btn-mini" onclick="guardarInformeHTML()">📄 Guardar Acta (.html)</button>
            <button class="btn-mini" onclick="exportarCSV()">📊 Exportar CSV (Excel)</button>
            <button class="tab-btn active" onclick="descargarContratoJSON()">⬇️ Descargar perfil_mod1.json</button>
          </div>
        </div>
        <div class="charts-2col">
          <pre id="json_contrato" class="json-box"></pre>
          <div id="glosario_contrato" style="font-size:12px;"></div>
        </div>
      </div>
    </div>
  </main>
</div>

<!-- BLOQUE 5 OFICIAL OED: DICCIONARIO FINANCIERO DESPLEGABLE (LAS 5 FAMILIAS COMPLETAS) -->
<div class="glosario-footer-wrap">
  <details class="oed-glosario-details" open>
    <summary>
      <span>📘 ¿Tienes dudas con algún concepto? Consulta aquí el Diccionario Financiero OED (5 Familias de Términos)</span>
      <span class="badge badge-ok">Haz clic para plegar / desplegar</span>
    </summary>
    <div style="margin-top:12px;">
      <div class="row-2" style="margin-bottom:10px;">
        <input type="text" id="buscador_glosario_oed" placeholder="🔍 Busca cualquier término (ej. IBC, UVT, Cuenta AFC, 4x1000, Fogafín, FIC, EA, UVR, Usura)..." oninput="filtrarGlosarioOED()" />
        <select id="filtro_familia_oed" onchange="filtrarGlosarioOED()">
          <option value="TODAS">Todas las 5 familias de términos del equipo OED</option>
          <option value="Nómina e Impuestos">Familia 3: Nómina e Impuestos (SMMLV, IBC, UVT, AFC, 4x1000)</option>
          <option value="Financiero e Inversión">Familia 1: Financiero e Inversión (EA, EM, IPC, CDT, FIC, VPN/TIR)</option>
          <option value="Deudas y Leyes Protectoras">Familia 4: Deudas y Leyes Protectoras (Usura, Fogafín, Ley 1328, Habeas Data)</option>
          <option value="Vivienda y Finca Raíz">Familia 2: Vivienda y Finca Raíz (VIS, UVR, Ley 546, Leasing)</option>
          <option value="Probabilidad y Futuro">Familia 5: Probabilidad y Futuro (Valor Esperado, Monte Carlo)</option>
        </select>
      </div>
      <div id="oed_glosario_pills" style="margin-bottom:10px;"></div>
      <div id="oed_glosario_detalle"></div>
    </div>
  </details>
</div>

<!-- MODAL DE CIERRE DE ASESORÍA Y REINICIO EN CEROS -->
<div id="modal_culminar" class="modal-backdrop">
  <div class="modal-card">
    <h3 style="margin:0 0 8px; color:var(--navy-oed); font-size:16px;">✅ Culminar Asesoría e Iniciar en Ceros ($0)</h3>
    <p style="margin:0 0 12px; font-size:12.5px; color:var(--muted);">
      Antes de dejar el espacio limpio en ceros ($0 COP) para la siguiente persona, puedes imprimir o descargar el acta de esta asesoría:
    </p>
    <div class="field">
      <label>Nombre de la persona asesorada / etiqueta de archivo:</label>
      <input type="text" id="input_cierre_nombre" placeholder="Ej. Asesoría María Gómez" />
    </div>
    <div style="display:flex; gap:8px; flex-wrap:wrap; margin:10px 0 12px;">
      <button class="btn-mini" onclick="imprimirAsesoria()">🖨️ Imprimir / Guardar PDF</button>
      <button class="btn-mini" onclick="guardarInformeHTML()">📄 Descargar Acta (.html)</button>
      <button class="btn-mini" onclick="exportarCSV()">📊 Descargar Excel (.csv)</button>
    </div>
    <label style="display:flex; align-items:center; gap:7px; font-size:12px; margin-bottom:14px; cursor:pointer;">
      <input type="checkbox" id="chk_archivar_historial" checked />
      Guardar respaldo en el Historial de Asesorías antes de reiniciar en ceros
    </label>
    <div style="display:flex; justify-content:flex-end; gap:8px;">
      <button class="btn-tool" onclick="cerrarModalCulminar()">Cancelar</button>
      <button class="btn-tool finish" onclick="confirmarCulminarAsesoria()">✅ Finalizar y Dejar en Ceros ($0)</button>
    </div>
  </div>
</div>

<script>
const GLOSARIO_OED = """
    + GLOSARIO_OED_JSON
    + r""";
const PALETA_OED = """
    + PALETA_OED_JSON
    + r""";
const fmtCOP = (v) => (v < 0 ? "-$" : "$") + Math.round(Math.abs(v)).toLocaleString("es-CO");

let estadoUltimoResultado = null;
let historialGuardado = [];
let catalogoMicrogastos = [];
let timerAutoSave = null;
let abortCalc = null;
let ultimoAfcOptimo = 0;
let itemsHormiga = [];

function showTip(evt, htmlTxt) {
  const t = document.getElementById("floating_tooltip");
  t.innerHTML = htmlTxt;
  t.style.display = "block";
  t.style.left = Math.min(window.innerWidth - 275, evt.clientX + 14) + "px";
  t.style.top = Math.max(10, evt.clientY - 28) + "px";
}
function hideTip() { document.getElementById("floating_tooltip").style.display = "none"; }

function toggleMenuGuardar(evt) {
  evt.stopPropagation();
  document.getElementById("menu_guardar_archivo").classList.toggle("open");
}
window.addEventListener("click", () => {
  const m = document.getElementById("menu_guardar_archivo");
  if (m) m.classList.remove("open");
});

function syncPair(srcId, dstId) {
  document.getElementById(dstId).value = document.getElementById(srcId).value;
}

/* BLOQUE 5: DICCIONARIO FINANCIERO INTERACTIVO OED */
function verTerminoOED(clave) {
  document.querySelectorAll("#oed_glosario_pills .glosario-pill").forEach(el => {
    el.classList.toggle("sel", el.dataset.k === clave);
  });
  const f = GLOSARIO_OED[clave];
  if (!f) return;
  document.getElementById("oed_glosario_detalle").innerHTML = `
    <div class="oed-doc-card oed-doc-verde" style="margin:6px 0;">
      <div style="font-size:11px; font-weight:800; color:#1D4ED8; text-transform:uppercase;">${f.categoria} · ${f.termino_tecnico}</div>
      <div style="margin-top:4px;"><b>💡 En palabras sencillas:</b> ${f.lenguaje_claro}</div>
    </div>
    <div class="oed-rx-box" style="margin:6px 0 0;">
      <b>🇨🇴 Ejemplo en pesos colombianos:</b> ${f.ejemplo_cotidiano}
    </div>
  `;
}

function filtrarGlosarioOED() {
  const q = (document.getElementById("buscador_glosario_oed").value || "").trim().toLowerCase();
  const fam = document.getElementById("filtro_familia_oed").value;
  const claves = Object.keys(GLOSARIO_OED).filter(k => {
    const f = GLOSARIO_OED[k];
    const okFam = (fam === "TODAS") || (f.categoria === fam);
    const okQ = !q || f.termino_tecnico.toLowerCase().includes(q) || f.lenguaje_claro.toLowerCase().includes(q) || (f.alias || []).some(a => a.toLowerCase().includes(q));
    return okFam && okQ;
  });
  document.getElementById("oed_glosario_pills").innerHTML = claves.map(k =>
    `<span class="glosario-pill" data-k="${k}" onclick="verTerminoOED('${k}')">${GLOSARIO_OED[k].termino_tecnico}</span>`
  ).join("");
  if (claves.length) verTerminoOED(claves.includes("IBC") ? "IBC" : claves[0]);
}

function poblarDropdownMicrogastos(catalogo) {
  catalogoMicrogastos = Array.isArray(catalogo) ? catalogo : [];
  const sel = document.getElementById("select_microgasto");
  sel.innerHTML = `<option value="">-- Selecciona un microgasto de la lista --</option>`;
  const grupos = {};
  catalogoMicrogastos.forEach((it, idx) => {
    const cat = it.categoria || "Otros";
    if (!grupos[cat]) grupos[cat] = [];
    grupos[cat].push({ ...it, idx });
  });
  Object.entries(grupos).forEach(([cat, lista]) => {
    const og = document.createElement("optgroup");
    og.label = cat;
    lista.forEach(it => {
      const opt = document.createElement("option");
      opt.value = String(it.idx);
      opt.textContent = `${it.concepto} (${fmtCOP(it.monto_unitario_cop)} × ${it.frecuencia_mensual}/mes)`;
      og.appendChild(opt);
    });
    sel.appendChild(og);
  });
}

function agregarDesdeDropdown(forzarManual = false) {
  const sel = document.getElementById("select_microgasto");
  const hint = document.getElementById("hint_sustituto_micro");
  if (sel.value === "") {
    if (forzarManual) {
      itemsHormiga.push({ concepto: "Microgasto personalizado", monto_unitario_cop: 10000, frecuencia_mensual: 1 });
      renderItemsHormiga();
      onNominaChanged();
    }
    return;
  }
  const itemCat = catalogoMicrogastos[Number(sel.value)];
  if (!itemCat) return;
  itemsHormiga.push({
    concepto: itemCat.concepto,
    monto_unitario_cop: Number(itemCat.monto_unitario_cop || 0),
    frecuencia_mensual: Number(itemCat.frecuencia_mensual || 1)
  });
  if (itemCat.sustituto_ahorro) {
    hint.style.display = "block";
    hint.innerHTML = `💡 <strong>Alternativa práctica:</strong> ${itemCat.sustituto_ahorro}`;
  }
  sel.value = "";
  renderItemsHormiga();
  onNominaChanged();
}

function vaciarMicrogastos() {
  itemsHormiga = [];
  document.getElementById("hint_sustituto_micro").style.display = "none";
  renderItemsHormiga();
  onNominaChanged();
}

function obtenerPayloadFormulario() {
  return {
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
    tasa_oportunidad_ea: Number(document.getElementById("rng_tasa_ea").value || 10) / 100.0,
    recorte_hormiga_simulacion_pct: Number(document.getElementById("rng_recorte_hormiga").value || 50),
    gastos_hormiga_mensual_cop: 0,
    detalle_gastos_hormiga: itemsHormiga
  };
}

function renderItemsHormiga() {
  const cont = document.getElementById("lista_hormiga");
  const enc = document.getElementById("encabezado_hormiga");
  cont.innerHTML = "";
  if (!itemsHormiga.length) {
    enc.style.display = "none";
    cont.innerHTML = `<div style="font-size:11.5px; color:var(--muted); padding:6px 8px; background:#F8FAFC; border-radius:7px; border:1px dashed #CBD5E1;">Sin microgastos registrados ($0 COP). Usa la lista desplegable para elegir los tuyos.</div>`;
    return;
  }
  enc.style.display = "block";
  itemsHormiga.forEach((it, idx) => {
    const sub = (Number(it.monto_unitario_cop) || 0) * (Number(it.frecuencia_mensual) || 0);
    const row = document.createElement("div");
    row.className = "hormiga-item";
    row.innerHTML = `
      <input type="text" value="${it.concepto}" oninput="itemsHormiga[${idx}].concepto=this.value; onNominaChanged();" />
      <input type="number" step="500" min="0" value="${it.monto_unitario_cop}" oninput="itemsHormiga[${idx}].monto_unitario_cop=Number(this.value||0); renderItemsHormiga(); onNominaChanged();" />
      <input type="number" step="1" min="0" value="${it.frecuencia_mensual}" oninput="itemsHormiga[${idx}].frecuencia_mensual=Number(this.value||0); renderItemsHormiga(); onNominaChanged();" />
      <span class="sub-pill">${fmtCOP(sub)}</span>
      <button class="btn-del" onclick="itemsHormiga.splice(${idx},1); renderItemsHormiga(); onNominaChanged();">&times;</button>
    `;
    cont.appendChild(row);
  });
}

function actualizarEstadoARL() {
  document.getElementById("clase_riesgo_arl").disabled = (document.getElementById("modalidad_laboral").value !== "Independiente");
}

function onNominaChanged() {
  actualizarEstadoARL();
  recalcular();
  document.getElementById("badge_autoguardado").textContent = "Guardando...";
  if (timerAutoSave) clearTimeout(timerAutoSave);
  timerAutoSave = setTimeout(() => persistirEnServidor(false), 300);
}

function aplicarAfcOptimo() {
  if (ultimoAfcOptimo > 0) {
    document.getElementById("aporte_afc").value = ultimoAfcOptimo;
    document.getElementById("rng_afc").value = Math.min(6000000, ultimoAfcOptimo);
    onNominaChanged();
  }
}

function optimizarBancos() {
  document.getElementById("cuotas_manejo").value = 0;
  document.getElementById("cuenta_exenta").checked = true;
  onNominaChanged();
}

async function persistirEnServidor(guardarEnHistorial) {
  const payload = obtenerPayloadFormulario();
  const etiqueta = document.getElementById("nombre_escenario").value || document.getElementById("nombre_asesorado_top").value || "";
  const res = await fetch("/api/guardar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ parametros: payload, nombre_escenario: etiqueta, guardar_en_historial: guardarEnHistorial })
  });
  const data = await res.json();
  if (data.guardado_exitoso) {
    const hora = new Date().toLocaleTimeString("es-CO", { hour12: false });
    document.getElementById("badge_autoguardado").textContent = `✓ Guardado ${hora}`;
    historialGuardado = data.historial || [];
    renderTablaHistorial();
    if (guardarEnHistorial) {
      document.getElementById("msg_guardado_detalle").innerHTML = `✓ Archivado: <strong>${data.perfil_activo.nombre_escenario}</strong>`;
      document.getElementById("nombre_escenario").value = "";
    } else {
      document.getElementById("msg_guardado_detalle").textContent = `✓ Datos sincronizados (${hora}).`;
    }
  }
}

async function guardarEscenarioManual() {
  await persistirEnServidor(true);
  activarTab("tab_guardados", document.getElementById("btn_tab_guardados"));
}

function abrirModalCulminar() {
  document.getElementById("input_cierre_nombre").value = document.getElementById("nombre_asesorado_top").value || "";
  document.getElementById("modal_culminar").classList.add("open");
}
function cerrarModalCulminar() {
  document.getElementById("modal_culminar").classList.remove("open");
}

async function confirmarCulminarAsesoria() {
  if (timerAutoSave) clearTimeout(timerAutoSave);
  const payloadActual = obtenerPayloadFormulario();
  const nombreCierre = document.getElementById("input_cierre_nombre").value || "";
  const archivar = document.getElementById("chk_archivar_historial").checked;

  const res = await fetch("/api/culminar_asesoria", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      datos_cierre: payloadActual,
      nombre_asesorado: nombreCierre,
      guardar_cierre_en_historial: archivar
    })
  });
  const data = await res.json();
  cerrarModalCulminar();
  if (data.reiniciado_en_ceros) {
    document.getElementById("nombre_asesorado_top").value = "";
    document.getElementById("nombre_escenario").value = "";
    document.getElementById("hint_sustituto_micro").style.display = "none";
    aplicarParametrosAlFormulario(data.parametros_ceros);
    historialGuardado = data.historial || [];
    renderTablaHistorial();
    document.getElementById("badge_autoguardado").textContent = "✓ Reiniciado en $0";
    document.getElementById("msg_guardado_detalle").textContent = "Asesoría culminada. Formulario limpio en $0 COP.";
    await recalcular();
  }
}

function activarTab(tabId, btn) {
  document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".tabs .tab-btn").forEach(b => b.classList.remove("active"));
  document.getElementById(tabId).classList.add("active");
  btn.classList.add("active");
}

function setForm(mod, arl, bruto, otros, afc, fijos, vars, deuda, liq, manejo, gmf, exenta) {
  document.getElementById("modalidad_laboral").value = mod;
  document.getElementById("clase_riesgo_arl").value = String(arl);
  document.getElementById("ingreso_bruto").value = bruto;
  document.getElementById("rng_bruto").value = Math.min(35000000, Math.max(0, bruto));
  document.getElementById("otros_ingresos").value = otros;
  document.getElementById("aporte_afc").value = afc;
  document.getElementById("rng_afc").value = Math.min(6000000, Math.max(0, afc));
  document.getElementById("gastos_fijos").value = fijos;
  document.getElementById("rng_fijos").value = Math.min(15000000, Math.max(0, fijos));
  document.getElementById("gastos_variables").value = vars;
  document.getElementById("cuotas_deuda").value = deuda;
  document.getElementById("liquidez_emergencia").value = liq;
  document.getElementById("rng_liq").value = Math.min(50000000, Math.max(0, liq));
  document.getElementById("cuotas_manejo").value = manejo;
  document.getElementById("movimientos_gmf").value = gmf;
  document.getElementById("cuenta_exenta").checked = exenta;
}

function aplicarParametrosAlFormulario(p) {
  setForm(
    p.modalidad_laboral || "Empleado", p.clase_riesgo_arl || 1,
    p.ingreso_bruto_mensual_cop ?? 0, p.otros_ingresos_mensuales_cop ?? 0,
    p.aporte_voluntario_afc_fpv_cop ?? 0, p.gastos_fijos_vitales_cop ?? 0,
    p.gastos_variables_estilo_vida_cop ?? 0, p.cuotas_deuda_mensual_cop ?? 0,
    p.liquidez_actual_fondo_emergencia_cop ?? 0, p.cuotas_manejo_mensual_cop ?? 0,
    p.monto_movimientos_gmf_mensual_cop ?? 0, p.cuenta_exenta_4x1000 !== false
  );
  if (Array.isArray(p.detalle_gastos_hormiga)) {
    itemsHormiga = p.detalle_gastos_hormiga.map(x => ({
      concepto: x.concepto || "Micro-gasto",
      monto_unitario_cop: Number(x.monto_unitario_cop ?? x.gasto_mensual_cop ?? 0),
      frecuencia_mensual: Number(x.frecuencia_mensual ?? 1)
    }));
  } else {
    itemsHormiga = [];
  }
  renderItemsHormiga();
  actualizarEstadoARL();
}

function cargarEscenario(nombre) {
  if (nombre === "ceros") {
    setForm("Empleado", 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, true);
    itemsHormiga = [];
  } else if (nombre === "semilla") {
    setForm("Empleado", 1, 6500000, 0, 0, 2800000, 950000, 0, 6000000, 0, 0, true);
    itemsHormiga = [
      { concepto: "Café / tinto / capuchino en calle", monto_unitario_cop: 6500, frecuencia_mensual: 20 },
      { concepto: "Domicilios por apps (recargos + propinas)", monto_unitario_cop: 12500, frecuencia_mensual: 8 },
      { concepto: "Plataforma de streaming sin uso frecuente", monto_unitario_cop: 45000, frecuencia_mensual: 1 },
      { concepto: "Comidas rápidas / salidas de fin de semana", monto_unitario_cop: 22500, frecuencia_mensual: 2 }
    ];
  } else if (nombre === "joven") {
    setForm("Empleado", 1, 2500000, 0, 0, 1350000, 450000, 180000, 4200000, 15000, 0, true);
    itemsHormiga = [{ concepto: "Empanada / panadería / mecato media mañana", monto_unitario_cop: 4500, frecuencia_mensual: 22 }, { concepto: "Taxi / app de transporte por salir tarde", monto_unitario_cop: 14000, frecuencia_mensual: 6 }];
  } else if (nombre === "ops") {
    setForm("Independiente", 1, 8500000, 0, 0, 3100000, 1100000, 500000, 19000000, 24000, 4500000, false);
    itemsHormiga = [{ concepto: "Café / tinto / capuchino en calle", monto_unitario_cop: 9000, frecuencia_mensual: 18 }, { concepto: "Domicilios por apps (recargos + propinas)", monto_unitario_cop: 18000, frecuencia_mensual: 10 }];
  } else if (nombre === "integral") {
    setForm("Integral", 1, 20000000, 0, 2000000, 6200000, 2800000, 1200000, 25000000, 35000, 22000000, true);
    itemsHormiga = [{ concepto: "Almuerzos fuera en lugar de llevar de casa", monto_unitario_cop: 25000, frecuencia_mensual: 16 }, { concepto: "Plataforma de streaming sin uso frecuente", monto_unitario_cop: 65000, frecuencia_mensual: 3 }];
  } else if (nombre === "deficit") {
    setForm("Empleado", 1, 3800000, 0, 0, 2300000, 900000, 650000, 800000, 32000, 3000000, false);
    itemsHormiga = [{ concepto: "Domicilios por apps (recargos + propinas)", monto_unitario_cop: 22000, frecuencia_mensual: 12 }, { concepto: "Apuestas deportivas / casino online / chance", monto_unitario_cop: 20000, frecuencia_mensual: 6 }];
  }
  renderItemsHormiga();
  onNominaChanged();
}

async function recalcular() {
  const payload = obtenerPayloadFormulario();
  document.getElementById("lbl_bruto").textContent = fmtCOP(payload.ingreso_bruto_mensual_cop);
  document.getElementById("lbl_afc").textContent = fmtCOP(payload.aporte_voluntario_afc_fpv_cop);
  document.getElementById("lbl_fijos").textContent = fmtCOP(payload.gastos_fijos_vitales_cop);
  document.getElementById("lbl_liq").textContent = fmtCOP(payload.liquidez_actual_fondo_emergencia_cop);
  document.getElementById("lbl_recorte_pct").textContent = `${payload.recorte_hormiga_simulacion_pct}%`;
  document.getElementById("lbl_tasa_ea").textContent = `${(payload.tasa_oportunidad_ea * 100).toFixed(1)}% EA`;

  if (abortCalc) abortCalc.abort();
  abortCalc = new AbortController();
  try {
    const res = await fetch("/api/diagnostico", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: abortCalc.signal
    });
    const data = await res.json();
    estadoUltimoResultado = data;
    requestAnimationFrame(() => actualizarUI(data));
  } catch (err) {
    if (err.name !== "AbortError") console.error(err);
  }
}

function actualizarUI(data) {
  const d = data.diagnostico;
  const nom = d.liquidacion_nomina;
  const fugas = d.radiografia_fugas;
  const opt = d.optimizacion_ingenieril;
  const sim = opt.simulacion_que_pasa_si;
  const afcOpt = opt.tributaria_afc;
  const oed = data.oed_ui;
  const guia = d.guia_asesoria || { consejos_ahorro: [], en_que_abstenerse: [], meta_ahorro_mensual_sugerida_cop: 0 };

  // BLOQUE 3: Semáforo Oficial OED con burbujas (?) + 📌 Plan de Acción para este Mes
  const semBox = document.getElementById("oed_semaforo_box");
  semBox.className = `oed-doc-card ${oed.clase_css}`;
  semBox.innerHTML = `
    <div><b>${oed.icono} ${oed.prefijo} ${oed.titulo_rico_html}</b></div>
    <div style="margin-top:4px;">${oed.explicacion_rica_html}</div>
    <div style="margin-top:6px; font-size:0.78rem; opacity:0.86;">
      💡 <i>Tip OED: Pasa el cursor sobre cualquier palabra subrayada con <b>?</b> para ver su explicación en sencillo.</i>
    </div>
  `;
  document.getElementById("oed_plan_mes_box").innerHTML =
    `<b>📌 Plan de Acción para este Mes:</b> ${oed.plan_mes_rico_html}`;

  const alertaBox = document.getElementById("alerta_normativa_box");
  alertaBox.style.display = nom.alerta_normativa ? "block" : "none";
  if (nom.alerta_normativa) alertaBox.innerHTML = `<b>⚠️ Nota legal laboral:</b> ${oed.alerta_normativa_html || nom.alerta_normativa}`;

  document.getElementById("sub_recorte_info").innerHTML =
    `Libera <strong>${fmtCOP(sim.flujo_mensual_rescatado_total_cop)}/mes</strong>` +
    (sim.meses_aceleracion_fondo_emergencia > 0 ? ` · Meta emergencia <strong>${sim.meses_aceleracion_fondo_emergencia} meses antes</strong>` : "");
  document.getElementById("sub_tasa_info").innerHTML =
    `Construye <strong>${fmtCOP(sim.patrimonio_rescatado_10a_cop)}</strong> en 10 años (${fmtCOP(sim.patrimonio_rescatado_5a_cop)} en 5a)`;

  ultimoAfcOptimo = afcOpt.aporte_afc_optimo_mensual_cop;
  const btnAfc = document.getElementById("btn_aplicar_afc");
  const boxAfc = document.getElementById("box_opt_afc");
  if (afcOpt.aplica_optimizacion_afc && Number(document.getElementById("aporte_afc").value) < ultimoAfcOptimo) {
    boxAfc.innerHTML = `💡 <strong>Beneficio Tributario AFC:</strong> Ahorrar ${fmtCOP(ultimoAfcOptimo)} en Cuenta AFC reduce tu retención en <strong>${fmtCOP(afcOpt.ahorro_tributario_mensual_cop)}/mes</strong>.`;
    btnAfc.style.display = "inline-block";
  } else if (nom.ahorro_tributario_afc_mensual_cop > 0) {
    boxAfc.innerHTML = `✅ <strong>Cuenta AFC Activa:</strong> Ahorras <strong>${fmtCOP(nom.ahorro_tributario_afc_mensual_cop)}/mes</strong> en retención.`;
    btnAfc.style.display = "none";
  } else {
    boxAfc.innerHTML = `✅ <strong>Retención $0 COP:</strong> Tu base tributaria está exenta (&le; 95 UVT).`;
    btnAfc.style.display = "none";
  }
  document.getElementById("btn_cero_bancos").style.display = (sim.ahorro_eliminar_friccion_bancaria_cop > 0) ? "inline-block" : "none";

  document.getElementById("kpi_idn").textContent = fmtCOP(d.ingreso_neto_mensual_cop);
  document.getElementById("kpi_idn_sub").textContent = `Descuentos ley: ${fmtCOP(nom.total_descuentos_ley_cop)} (${nom.tasa_descuento_efectiva_pct}%)`;

  const elExc = document.getElementById("kpi_excedente");
  elExc.textContent = fmtCOP(d.excedente_mensual_cop);
  elExc.style.color = d.excedente_mensual_cop >= 0 ? "#15803D" : "#B91C1C";
  document.getElementById("kpi_excedente_sub").innerHTML = `Con plan optimizado: <strong>${fmtCOP(sim.excedente_optimizado_cop)}</strong> (${sim.eficiencia_optimizada_pct}%)`;

  document.getElementById("kpi_emergencia").textContent = `${d.meses_fondo_emergencia.toFixed(2)} meses`;
  const pctEm = Math.min(100, (d.meses_fondo_emergencia / d.meta_meses_fondo_emergencia) * 100);
  const barEm = document.getElementById("bar_emergencia");
  barEm.style.width = `${pctEm}%`;
  barEm.style.background = d.fondo_emergencia_completo ? "#15803D" : "#EA580C";
  document.getElementById("kpi_emergencia_sub").textContent = `Meta ${nom.modalidad_laboral}: ${d.meta_meses_fondo_emergencia}m (${fmtCOP(d.monto_meta_fondo_emergencia_cop)})`;

  document.getElementById("kpi_fugas").textContent = fmtCOP(fugas.fuga_total_mensual_cop) + "/mes";
  document.getElementById("kpi_fugas_sub").textContent = `Hormiga: ${fmtCOP(fugas.gastos_hormiga_mensual_cop)} · Bancos: ${fmtCOP(fugas.friccion_bancaria_mensual_cop)} (${fugas.peso_sobre_ingreso_neto_pct}%)`;

  document.getElementById("kpi_oportunidad").textContent = fmtCOP(fugas.costo_oportunidad_fuga_total_10a_nominal_cop);
  document.getElementById("kpi_oportunidad_sub").textContent = `5a: ${fmtCOP(fugas.costo_oportunidad_fuga_total_5a_nominal_cop)} · Real 10a: ${fmtCOP(fugas.costo_oportunidad_fuga_total_10a_real_cop)}`;

  renderConsejosYAbstenciones(guia, oed);
  dibujarSankeySVG(d);
  dibujarWaterfallSVG(d);
  renderTablasNomina(nom, data.comparativa_modalidades);
  dibujarCurvaOportunidadSVG(fugas);
  renderParetoY503020(opt.ranking_pareto_fugas, d.balance_50_30_20, sim);
  renderContratoYGlosario(data.contrato_oed);
}

function renderConsejosYAbstenciones(guia, oed) {
  document.getElementById("badge_meta_ahorro").textContent = `Meta 20%: ${fmtCOP(guia.meta_ahorro_mensual_sugerida_cop || 0)}/mes`;
  const absList = oed.abstenciones_ricas || [];
  document.getElementById("badge_num_abstenciones").textContent = `${absList.length} recomendaciones`;

  const cAhorro = document.getElementById("contenedor_consejos_ahorro");
  const cAbs = document.getElementById("contenedor_abstenciones");

  if (!guia.sesion_activa) {
    cAhorro.innerHTML = `<div style="color:var(--muted); font-size:12px; padding:6px 0;">${guia.resumen_orientacion}</div>`;
    cAbs.innerHTML = `<div style="color:var(--muted); font-size:12px; padding:6px 0;">Registra tus ingresos, gastos o elige microgastos en la lista desplegable para recibir orientación preventiva personalizada.</div>`;
    return;
  }

  cAhorro.innerHTML = (oed.consejos_ricos || []).map(c => `
    <div class="tip-item">
      <div style="display:flex; justify-content:space-between; gap:8px; font-weight:700; color:#14532D; margin-bottom:2px;">
        <span>✅ ${c.titulo}</span>
        ${c.impacto_mensual_cop > 0 ? `<span class="badge badge-ok">+${fmtCOP(c.impacto_mensual_cop)}/mes</span>` : ""}
      </div>
      <div style="color:#0F294A;">${c.accion_html}</div>
      ${c.impacto_10a_cop > 0 ? `<div style="font-size:11px; color:#15803D; margin-top:3px; font-weight:600;">📈 Potencial en 10 años: ${fmtCOP(c.impacto_10a_cop)}</div>` : ""}
    </div>
  `).join("");

  cAbs.innerHTML = absList.map(a => {
    const badgeCls = a.severidad === "CRITICA" || a.severidad === "ALTA" ? "badge-err" : (a.severidad === "MEDIA" ? "badge-warn" : "badge-ok");
    return `
      <div class="abs-item ${a.severidad}">
        <div style="display:flex; justify-content:space-between; gap:8px; font-weight:700; color:#7F1D1D; margin-bottom:2px;">
          <span>🛑 Te recomendamos abstenerte de: ${a.habito_o_rubro}</span>
          <span class="badge ${badgeCls}">${a.severidad}</span>
        </div>
        <div style="font-size:11.5px; color:#475569; margin-bottom:2px;"><em>Por qué:</em> ${a.motivo_html}</div>
        <div style="color:#0F294A; font-weight:600;">👉 ${a.accion_html}</div>
        ${a.ahorro_estimado_mensual_cop > 0 ? `<div style="font-size:11px; color:#B91C1C; margin-top:2px; font-weight:700;">💰 Flujo mensual que recuperas: ${fmtCOP(a.ahorro_estimado_mensual_cop)}/mes</div>` : ""}
      </div>
    `;
  }).join("");
}

/* BLOQUE 4: GRÁFICAS SVG CON LA PALETA OFICIAL OED */
function dibujarSankeySVG(d) {
  const nom = d.liquidacion_nomina;
  const totalIn = nom.ingreso_bruto_mensual_cop + nom.auxilio_transporte_cop + d.otros_ingresos_mensuales_cop;
  if (totalIn <= 0) {
    document.getElementById("svg_sankey_wrap").innerHTML = `<div style="padding:28px; text-align:center; color:var(--muted); background:#F8FAFC; border-radius:9px; border:1px dashed #CBD5E1;">Sesión en ceros ($0 COP). Ingresa tu sueldo en el panel izquierdo para ver tu flujo de caja con la Paleta OED.</div>`;
    return;
  }
  const W = 580, H = 335, x0 = 18, x1 = 230, x2 = 435, bw = 18;
  const segSocial = nom.salud_obligatoria_cop + nom.pension_obligatoria_cop + nom.fondo_solidaridad_pensional_cop + nom.arl_cop;
  const rete = nom.retencion_fuente_cop, idn = d.ingreso_neto_mensual_cop;

  const col1 = [{ label: "Seg. Social", val: segSocial, color: "#EA580C" }, { label: "Retefuente", val: rete, color: "#B45309" }].filter(x => x.val > 0);
  const col2 = [
    { label: "Costos Fijos", val: d.gastos_fijos_vitales_cop, color: "#1D4ED8" },
    { label: "Estilo de Vida", val: d.gastos_variables_estilo_vida_cop, color: "#7C3AED" },
    { label: "Hormiga + 4x1000", val: d.fuga_total_mensual_cop, color: "#DC2626" },
    { label: "Cuotas Deuda", val: d.cuotas_deuda_mensual_cop, color: "#EA580C" },
    { label: "Excedente Libre", val: Math.max(0, d.excedente_mensual_cop), color: "#15803D" }
  ].filter(x => x.val > 0);

  const scale = 225 / Math.max(totalIn, segSocial + rete + col2.reduce((s, x) => s + x.val, 0));
  const hIn = Math.max(12, totalIn * scale), y0 = 38;
  let svg = `<svg viewBox="0 0 ${W} ${H}" onmouseleave="hideTip()">`;
  svg += `<rect class="svg-hover" x="${x0}" y="${y0}" width="${bw}" height="${hIn}" fill="#0F294A" rx="3" onmousemove="showTip(event,'<strong>Total Devengado</strong><br/>${fmtCOP(totalIn)} (100%)')"/>`;
  svg += `<text x="${x0}" y="${y0 - 8}" font-size="11.5" font-weight="700" fill="#0F294A">Devengado: ${fmtCOP(totalIn)}</text>`;

  let cy0 = y0, cy1 = 30;
  col1.forEach(it => {
    const h = Math.max(6, it.val * scale), hSrc = it.val * scale;
    const pct = ((it.val / totalIn) * 100).toFixed(1);
    svg += pathCurvo(x0 + bw, cy0, hSrc, x1, cy1, h, it.color, 0.28, `${it.label}: ${fmtCOP(it.val)} (${pct}% del bruto)`);
    svg += `<rect class="svg-hover" x="${x1}" y="${cy1}" width="${bw}" height="${h}" fill="${it.color}" rx="3" onmousemove="showTip(event,'<strong>${it.label}</strong><br/>${fmtCOP(it.val)} (${pct}%)')"/>`;
    svg += `<text x="${x1 + bw + 6}" y="${cy1 + h/2 + 4}" font-size="11" fill="#0F294A">${it.label}: ${fmtCOP(it.val)}</text>`;
    cy0 += hSrc; cy1 += h + 14;
  });

  const yIdn = cy1 + 4, hIdn = Math.max(14, idn * scale);
  svg += pathCurvo(x0 + bw, cy0, idn * scale, x1, yIdn, hIdn, "#1D4ED8", 0.26, `Ingreso Neto IDN: ${fmtCOP(idn)} (${((idn/totalIn)*100).toFixed(1)}%)`);
  svg += `<rect class="svg-hover" x="${x1}" y="${yIdn}" width="${bw}" height="${hIdn}" fill="#1D4ED8" rx="3" onmousemove="showTip(event,'<strong>Ingreso Disponible Neto</strong><br/>${fmtCOP(idn)}')"/>`;
  svg += `<text x="${x1 - 4}" y="${yIdn + hIdn + 14}" font-size="11.5" font-weight="700" fill="#1D4ED8">Neto: ${fmtCOP(idn)}</text>`;

  let cyIdnSrc = yIdn, cy2 = 22;
  const sumSal = col2.reduce((s, x) => s + x.val, 0) || 1;
  col2.forEach(it => {
    const h = Math.max(8, it.val * scale), hSrc = (it.val / sumSal) * hIdn;
    const pctIdn = idn > 0 ? ((it.val / idn) * 100).toFixed(1) : "0.0";
    svg += pathCurvo(x1 + bw, cyIdnSrc, hSrc, x2, cy2, h, it.color, 0.30, `${it.label}: ${fmtCOP(it.val)} (${pctIdn}% del IDN)`);
    svg += `<rect class="svg-hover" x="${x2}" y="${cy2}" width="${bw}" height="${h}" fill="${it.color}" rx="3" onmousemove="showTip(event,'<strong>${it.label}</strong><br/>${fmtCOP(it.val)}<br/>${pctIdn}% del Ingreso Neto')"/>`;
    svg += `<text x="${x2 - 6}" y="${cy2 + h/2 + 4}" text-anchor="end" font-size="11" font-weight="600" fill="#0F294A">${it.label}</text>`;
    svg += `<text x="${x2 + bw + 5}" y="${cy2 + h/2 + 4}" font-size="11" fill="#475569">${fmtCOP(it.val)}</text>`;
    cyIdnSrc += hSrc; cy2 += h + 13;
  });
  svg += `</svg>`;
  document.getElementById("svg_sankey_wrap").innerHTML = svg;
}

function pathCurvo(xA, yA, hA, xB, yB, hB, color, alpha, tip) {
  const xm = (xA + xB) / 2;
  const safeTip = tip.replaceAll("'", "");
  return `<path class="svg-hover" onmousemove="showTip(event,'${safeTip}')" d="M${xA},${yA} C${xm},${yA} ${xm},${yB} ${xB},${yB} L${xB},${yB + hB} C${xm},${yB + hB} ${xm},${yA + hA} ${xA},${yA + hA} Z" fill="${color}" fill-opacity="${alpha}"/>`;
}

function dibujarWaterfallSVG(d) {
  const nom = d.liquidacion_nomina;
  const dev = nom.ingreso_bruto_mensual_cop + nom.auxilio_transporte_cop + d.otros_ingresos_mensuales_cop;
  if (dev <= 0 && d.egresos_totales_mensuales_cop <= 0) {
    document.getElementById("svg_waterfall_wrap").innerHTML = `<div style="padding:28px; text-align:center; color:var(--muted); background:#F8FAFC; border-radius:9px; border:1px dashed #CBD5E1;">Cascada salarial lista en ceros ($0 COP).</div>`;
    return;
  }
  const pasos = [
    { label: "Devengado", ini: 0, fin: dev, color: "#0F294A" },
    { label: "Ley", ini: dev, fin: d.ingreso_neto_mensual_cop, color: "#EA580C" },
    { label: "Neto IDN", ini: 0, fin: d.ingreso_neto_mensual_cop, color: "#1D4ED8" },
    { label: "Fijos", ini: d.ingreso_neto_mensual_cop, fin: d.ingreso_neto_mensual_cop - d.gastos_fijos_vitales_cop, color: "#475569" },
    { label: "Variables", ini: d.ingreso_neto_mensual_cop - d.gastos_fijos_vitales_cop, fin: d.ingreso_neto_mensual_cop - d.gastos_fijos_vitales_cop - d.gastos_variables_estilo_vida_cop, color: "#7C3AED" },
    { label: "Hormiga", ini: d.ingreso_neto_mensual_cop - d.gastos_fijos_vitales_cop - d.gastos_variables_estilo_vida_cop, fin: d.ingreso_neto_mensual_cop - d.gastos_fijos_vitales_cop - d.gastos_variables_estilo_vida_cop - d.fuga_total_mensual_cop, color: "#DC2626" },
    { label: "Excedente", ini: 0, fin: d.excedente_mensual_cop, color: d.excedente_mensual_cop >= 0 ? "#15803D" : "#B91C1C" }
  ];
  const W = 500, H = 330, padT = 28, padB = 44, padL = 18, padR = 14;
  const maxV = Math.max(1, dev, ...pasos.map(p => Math.max(p.ini, p.fin))), minV = Math.min(0, d.excedente_mensual_cop);
  const yMap = (v) => padT + ((maxV - v) / (maxV - minV)) * (H - padT - padB);
  let svg = `<svg viewBox="0 0 ${W} ${H}" onmouseleave="hideTip()">`;
  svg += `<line x1="${padL}" y1="${yMap(0)}" x2="${W - padR}" y2="${yMap(0)}" stroke="#94A3B8"/>`;
  const colW = (W - padL - padR) / pasos.length;
  pasos.forEach((p, i) => {
    const x = padL + i * colW + 7, bw = colW - 14;
    const yTop = yMap(Math.max(p.ini, p.fin)), h = Math.max(4, yMap(Math.min(p.ini, p.fin)) - yTop);
    const val = (i === 0 || i === 2 || i === pasos.length - 1) ? p.fin : (p.fin - p.ini);
    svg += `<rect class="svg-hover" x="${x}" y="${yTop}" width="${bw}" height="${h}" fill="${p.color}" rx="3" onmousemove="showTip(event,'<strong>${p.label}</strong><br/>${fmtCOP(val)}')"/>`;
    svg += `<text x="${x + bw/2}" y="${yTop - 5}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#0F294A">${(val/1e6).toFixed(2)}M</text>`;
    svg += `<text x="${x + bw/2}" y="${H - 18}" text-anchor="middle" font-size="10.5" font-weight="600" fill="#475569">${p.label}</text>`;
  });
  svg += `</svg>`;
  document.getElementById("svg_waterfall_wrap").innerHTML = svg;
}

function dibujarCurvaOportunidadSVG(fugas) {
  const hist = fugas.historial_capitalizacion_10a || [];
  if (!hist.length || fugas.fuga_total_mensual_cop <= 0) {
    document.getElementById("svg_oportunidad_wrap").innerHTML = `<div style="padding:18px; color:var(--muted); background:#F8FAFC; border-radius:9px; border:1px dashed #CBD5E1;">Sin gastos hormiga ni fugas registradas ($0 COP).</div>`;
    return;
  }
  window._histCurva = hist;
  const W = 540, H = 285, padL = 62, padR = 20, padT = 22, padB = 34;
  const maxY = Math.max(1, hist[hist.length - 1].saldo_final_cop);
  const xMap = (m) => padL + ((m - 1) / 119) * (W - padL - padR);
  const yMap = (v) => padT + (1 - v / maxY) * (H - padT - padB);
  const ptsG = hist.map(h => `${xMap(h.mes).toFixed(1)},${yMap(h.capital_acumulado_cop).toFixed(1)}`).join(" ");
  const ptsC = hist.map(h => `${xMap(h.mes).toFixed(1)},${yMap(h.saldo_final_cop).toFixed(1)}`).join(" ");

  let svg = `<svg id="svg_curva_10a" viewBox="0 0 ${W} ${H}" onmousemove="hoverCurva10a(event, ${W}, ${padL}, ${padR})" onmouseleave="hideTip()">`;
  [0, 0.25, 0.5, 0.75, 1].forEach(f => {
    const v = maxY * f, y = yMap(v);
    svg += `<line x1="${padL}" y1="${y}" x2="${W - padR}" y2="${y}" stroke="#E2E8F0"/>`;
    svg += `<text x="${padL - 6}" y="${y + 4}" text-anchor="end" font-size="10" fill="#475569">$${(v/1e6).toFixed(1)}M</text>`;
  });
  svg += `<polyline fill="none" stroke="#DC2626" stroke-width="2.2" stroke-dasharray="5,4" points="${ptsG}"/>`;
  svg += `<polyline fill="none" stroke="#1D4ED8" stroke-width="3" points="${ptsC}"/>`;
  svg += `<circle cx="${xMap(60)}" cy="${yMap(hist[59].saldo_final_cop)}" r="4.5" fill="#EA580C"/>`;
  svg += `<circle cx="${xMap(120)}" cy="${yMap(hist[119].saldo_final_cop)}" r="5" fill="#15803D"/>`;
  svg += `<line id="cursor_curva" x1="-10" y1="${padT}" x2="-10" y2="${H-padB}" stroke="#0F294A" stroke-dasharray="3,3"/>`;
  svg += `<text x="${W/2}" y="${H - 8}" text-anchor="middle" font-size="10.5" fill="#475569">Rojo: Gastado · Azul Acción OED: Invertido con Interés Compuesto al ${(fugas.tasa_oportunidad_ea*100).toFixed(1)}% EA</text>`;
  svg += `</svg>`;
  document.getElementById("svg_oportunidad_wrap").innerHTML = svg;
}

function hoverCurva10a(evt, W, padL, padR) {
  const svgEl = document.getElementById("svg_curva_10a");
  if (!svgEl || !window._histCurva) return;
  const rect = svgEl.getBoundingClientRect();
  const relX = ((evt.clientX - rect.left) / rect.width) * W;
  const idx = Math.min(119, Math.max(0, Math.round(((relX - padL) / (W - padL - padR)) * 119)));
  const h = window._histCurva[idx];
  const cx = padL + (idx / 119) * (W - padL - padR);
  const line = document.getElementById("cursor_curva");
  if (line) { line.setAttribute("x1", cx); line.setAttribute("x2", cx); }
  const interesAcum = h.saldo_final_cop - h.capital_acumulado_cop;
  showTip(evt, `<strong>Mes ${h.mes} (${(h.mes/12).toFixed(1)} años)</strong><br/>• Gastado: ${fmtCOP(h.capital_acumulado_cop)}<br/>• En FIC/CDT: <strong>${fmtCOP(h.saldo_final_cop)}</strong><br/>• Rendimiento compuesto: <span style="color:#86EFAC;">+${fmtCOP(interesAcum)}</span>`);
}

function renderTablasNomina(nom, comp) {
  const prov = nom.provisiones_prestacionales_informativas;
  const filas = [
    ["Modalidad Contractual", `<strong>${nom.modalidad_laboral}</strong> (${nom.ingreso_en_smmlv} SMMLV)`],
    ["Ingreso Bruto Mensual", fmtCOP(nom.ingreso_bruto_mensual_cop)],
    ["(+) Auxilio de Transporte", fmtCOP(nom.auxilio_transporte_cop)],
    ["IBC (Ingreso Base de Cotización)", fmtCOP(nom.ibc_cotizacion_cop)],
    ["(-) Salud Obligatoria", fmtCOP(-nom.salud_obligatoria_cop)],
    ["(-) Pensión Obligatoria", fmtCOP(-nom.pension_obligatoria_cop)],
    [`(-) Fondo Solidaridad Pensional (${nom.porcentaje_fsp_aplicado}%)`, fmtCOP(-nom.fondo_solidaridad_pensional_cop)],
    ["(-) ARL", fmtCOP(-nom.arl_cop)],
    ["(-) Retención en la Fuente (UVT)", fmtCOP(-nom.retencion_fuente_cop)],
    ["Beneficio Tributario Cuenta AFC", `<span style="color:#15803D;font-weight:700;">${fmtCOP(nom.ahorro_tributario_afc_mensual_cop)}</span>`],
    ["<strong>(=) Ingreso Disponible Neto</strong>", `<strong>${fmtCOP(nom.ingreso_neto_mensual_cop)}</strong>`],
    ["(+) Prima + Cesantías Mensualizadas (Info)", fmtCOP(prov.prima_servicios_mensualizada_cop + prov.cesantias_mensualizadas_cop + prov.intereses_cesantias_mensualizados_cop)]
  ];
  document.getElementById("tabla_nomina_detalle").innerHTML = `<thead><tr><th>Concepto</th><th>Valor ($ COP)</th></tr></thead><tbody>` + filas.map(r => `<tr><td>${r[0]}</td><td>${r[1]}</td></tr>`).join("") + `</tbody>`;
  document.getElementById("tabla_comparativa_mod").innerHTML = `<thead><tr><th>Modalidad</th><th>IBC</th><th>Seg. Social+ARL</th><th>Retefuente</th><th>Neto Mensual</th></tr></thead><tbody>` +
    comp.map(c => `<tr style="${c.modalidad_laboral===nom.modalidad_laboral?'background:#EFF6FF;':''}"><td><strong>${c.modalidad_laboral}</strong></td><td>${fmtCOP(c.ibc_cotizacion_cop)}</td><td>${fmtCOP(c.salud_obligatoria_cop+c.pension_obligatoria_cop+c.fondo_solidaridad_pensional_cop+c.arl_cop)}</td><td>${fmtCOP(c.retencion_fuente_cop)}</td><td><strong>${fmtCOP(c.ingreso_neto_mensual_cop)}</strong></td></tr>`).join("") + `</tbody>`;
}

function renderParetoY503020(pareto, b, sim) {
  document.getElementById("tabla_pareto").innerHTML = pareto.length
    ? `<thead><tr><th>Fuente de Fuga</th><th>Mensual</th><th>% Fuga</th><th>Prioridad</th></tr></thead><tbody>` +
      pareto.map(p => `<tr><td>${p.origen}</td><td>${fmtCOP(p.monto_mensual_cop)}</td><td>${p.participacion_pct}%</td><td>${p.impacto_pareto_80 ? '<span class="badge badge-warn">80% Principal</span>' : '<span class="badge badge-ok">20% Menor</span>'}</td></tr>`).join("") + `</tbody>`
    : `<p style="color:var(--muted);">Sin fugas activas ($0 COP).</p>`;

  const bloques = [
    { titulo: "50% Costos Fijos Vitales", d: b.necesidades_50, m: "&le; 50%", ok: "#1D4ED8", w: "#DC2626" },
    { titulo: "30% Estilo de Vida + Microgastos", d: b.estilo_vida_30, m: "&le; 30%", ok: "#7C3AED", w: "#EA580C" },
    { titulo: "20% Ahorro y Patrimonio Libre", d: b.ahorro_patrimonio_20, m: "&ge; 20%", ok: "#15803D", w: "#B91C1C" }
  ];
  document.getElementById("panel_50_30_20").innerHTML = bloques.map(x => `
    <div style="margin-bottom:13px;">
      <div style="display:flex; justify-content:space-between; font-size:12px; font-weight:700;">
        <span>${x.titulo}</span>
        <span>${fmtCOP(x.d.real_cop)} (${x.d.real_pct}%) <span class="badge ${x.d.cumple?'badge-ok':'badge-warn'}">${x.d.cumple?'En meta':'Revisar'} (${x.m})</span></span>
      </div>
      <div class="bar-track"><div class="bar-fill" style="width:${Math.min(100,Math.max(0,x.d.real_pct))}%; background:${x.d.cumple?x.ok:x.w};"></div></div>
      <div style="font-size:11px; color:var(--muted);">Referencia saludable: ${fmtCOP(x.d.meta_cop)}</div>
    </div>`).join("") +
    `<div class="oed-rx-box" style="margin-top:8px;">
      <b>📌 Impacto de tu Simulación Activa:</b><br/>
      • Ahorro mensual recuperado: <b>+${fmtCOP(sim.flujo_mensual_rescatado_total_cop)}/mes</b><br/>
      • Nuevo Excedente Mensual: <b>${fmtCOP(sim.excedente_optimizado_cop)}</b> (${sim.eficiencia_optimizada_pct}% de tu ingreso neto)<br/>
      • Patrimonio adicional en 10 años: <b>${fmtCOP(sim.patrimonio_rescatado_10a_cop)}</b>
    </div>`;
}

function renderTablaHistorial() {
  document.getElementById("contador_historial").textContent = String(historialGuardado.length);
  const cont = document.getElementById("contenedor_tabla_historial");
  const mini = document.getElementById("mini_historial_sidebar");
  const graf = document.getElementById("grafico_comparador_guardados");
  if (!historialGuardado.length) {
    cont.innerHTML = `<p style="color:var(--muted);">No hay asesorías archivadas aún.</p>`;
    if (mini) mini.innerHTML = "";
    if (graf) graf.innerHTML = "";
    return;
  }
  if (mini) {
    mini.innerHTML = `<div style="border-top:1px solid #BFDBFE; padding-top:4px; color:var(--navy-oed);"><strong>Archivadas (${historialGuardado.length}):</strong></div>` +
      historialGuardado.slice(0, 3).map((it, idx) => `<div style="display:flex; justify-content:space-between; align-items:center; margin-top:3px;"><span style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width:210px;">• ${it.nombre_escenario}</span><button class="btn-mini" style="padding:1px 6px;" onclick="restaurarDesdeHistorial(${idx})">Cargar</button></div>`).join("");
  }
  const maxBruto = Math.max(1, ...historialGuardado.map(x => x.resumen_resultados?.ingreso_bruto_mensual_cop || 0));
  graf.innerHTML = historialGuardado.slice(0, 6).map(it => {
    const r = it.resumen_resultados || {};
    const wIdn = Math.max(2, ((r.ingreso_neto_mensual_cop || 0) / maxBruto) * 100);
    const wExc = Math.max(2, (Math.max(0, r.excedente_mensual_cop || 0) / maxBruto) * 100);
    return `<div style="margin-bottom:8px; font-size:11.5px;">
      <div style="display:flex; justify-content:space-between;"><strong>${it.nombre_escenario} (${r.modalidad_laboral})</strong><span>Neto: ${fmtCOP(r.ingreso_neto_mensual_cop||0)} · Excedente: <strong>${fmtCOP(r.excedente_mensual_cop||0)}</strong></span></div>
      <div class="bar-track" style="height:9px;"><div class="bar-fill" style="width:${wIdn}%; background:#1D4ED8;"></div></div>
      <div class="bar-track" style="height:7px; margin-top:2px;"><div class="bar-fill" style="width:${wExc}%; background:#15803D;"></div></div>
    </div>`;
  }).join("");

  cont.innerHTML = `<table><thead><tr><th>Asesoría / Fecha</th><th>Modalidad</th><th>Bruto</th><th>Neto (IDN)</th><th>Excedente</th><th>Acciones</th></tr></thead><tbody>` +
    historialGuardado.map((it, idx) => {
      const r = it.resumen_resultados || {};
      return `<tr><td><strong>${it.nombre_escenario}</strong><br/><span style="font-size:10.5px;color:var(--muted);">${it.fecha_guardado_iso}</span></td><td>${r.modalidad_laboral}</td><td>${fmtCOP(r.ingreso_bruto_mensual_cop||0)}</td><td>${fmtCOP(r.ingreso_neto_mensual_cop||0)}</td><td style="font-weight:700;color:${(r.excedente_mensual_cop||0)>=0?'#15803D':'#B91C1C'};">${fmtCOP(r.excedente_mensual_cop||0)}</td><td><button class="btn-mini" onclick="restaurarDesdeHistorial(${idx})">Cargar</button> <button class="btn-mini" style="color:#B91C1C;" onclick="eliminarDelHistorial('${it.id_registro}')">Eliminar</button></td></tr>`;
    }).join("") + `</tbody></table>`;
}

function restaurarDesdeHistorial(idx) {
  const item = historialGuardado[idx];
  if (item && item.parametros_entrada) {
    document.getElementById("nombre_asesorado_top").value = item.nombre_escenario || "";
    aplicarParametrosAlFormulario(item.parametros_entrada);
    onNominaChanged();
  }
}

async function eliminarDelHistorial(idRegistro) {
  const res = await fetch("/api/eliminar_guardado", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id_registro: idRegistro }) });
  const data = await res.json();
  historialGuardado = data.historial || [];
  renderTablaHistorial();
}

function renderContratoYGlosario(c) {
  document.getElementById("json_contrato").textContent = JSON.stringify(c, null, 2);
  const desc = [
    ["usuario_id", "Identificador protegido bajo Habeas Data Ley 1581 (Paso 0 - Nelson)."],
    ["modalidad_laboral", "Define cotización sobre IBC y meta de emergencia (3 o 6 meses)."],
    ["ingreso_neto_mensual_cop", "Lo que recibes libre al mes; conecta con Deudas (Paso 3) y Vivienda (Paso 5)."],
    ["excedente_mensual_cop", "Capacidad mensual real de ahorro e inversión (Pasos 3, 4 y 6)."],
    ["meses_fondo_emergencia", "Meses de gastos vitales respaldados hoy por tu ahorro líquido."],
    ["costo_oportunidad_hormiga_10a_cop", "Patrimonio a 10 años si conviertes tus gastos hormiga en inversión."],
    ["estado_flujo_caja", "Diagnóstico Financiero OED del flujo mensual."],
    ["aporte_disponible_portafolio_mod2_cop", "Monto mensual listo para invertir en el Paso 4 (Camilo)."]
  ];
  document.getElementById("glosario_contrato").innerHTML = desc.map(d => `<div style="padding:5px 0; border-bottom:1px solid #E2E8F0;"><code>${d[0]}</code>: <span style="color:var(--muted);">${d[1]}</span></div>`).join("");
}

function imprimirAsesoria() {
  const cliente = document.getElementById("nombre_asesorado_top").value || "Persona Asesorada";
  const fecha = new Date().toLocaleString("es-CO");
  document.getElementById("print_meta_info").innerHTML =
    `<strong>Persona asesorada:</strong> ${cliente} &nbsp;|&nbsp; <strong>Asesor Financiero OED (Paso 2):</strong> Nidia Velásquez &nbsp;|&nbsp; <strong>Fecha:</strong> ${fecha}`;
  window.print();
}

function guardarInformeHTML() {
  if (!estadoUltimoResultado) return;
  const d = estadoUltimoResultado.diagnostico;
  const nom = d.liquidacion_nomina;
  const plan = d.plan_accion_flujo_caja;
  const guia = d.guia_asesoria || { consejos_ahorro: [], en_que_abstenerse: [] };
  const cliente = document.getElementById("nombre_asesorado_top").value || "Asesorado";
  const fecha = new Date().toLocaleString("es-CO");

  const tipsHtml = (guia.consejos_ahorro || []).map(c =>
    `<li><strong>${c.titulo}:</strong> ${c.accion} ${c.impacto_mensual_cop > 0 ? `(Impacto: ${fmtCOP(c.impacto_mensual_cop)}/mes)` : ""}</li>`
  ).join("") || "<li>Sin registros activos.</li>";

  const absHtml = (guia.en_que_abstenerse || []).map(a =>
    `<li><strong>[${a.severidad}] Abstenerse de ${a.habito_o_rubro}:</strong> ${a.motivo} <em>Recomendación:</em> ${a.accion_inmediata}</li>`
  ).join("") || "<li>Sin alertas activas.</li>";

  const microHtml = (d.radiografia_fugas.detalle_items || []).map(m =>
    `<tr><td>${m.concepto}</td><td>${fmtCOP(m.monto_unitario_cop)}</td><td>${m.frecuencia_mensual}</td><td>${fmtCOP(m.gasto_mensual_cop)}</td></tr>`
  ).join("") || `<tr><td colspan="4">Sin microgastos registrados ($0 COP)</td></tr>`;

  const doc = `<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Acta OED Paso 2 - ${cliente}</title>
  <style>body{font-family:'Segoe UI',Arial,sans-serif;max-width:900px;margin:24px auto;color:#0F294A;line-height:1.5;}
  .hdr{background:linear-gradient(135deg,#0F294A,#1D4ED8);color:#fff;padding:16px 20px;border-radius:12px;}
  h2{color:#0F294A;border-bottom:2px solid #E2E8F0;padding-bottom:4px;}
  table{width:100%;border-collapse:collapse;margin:10px 0;}th,td{border:1px solid #CBD5E1;padding:7px 9px;text-align:left;}
  th{background:#F1F5F9;}.rx{padding:12px;border-radius:10px;background:#FFF7ED;border-left:6px solid #EA580C;margin:12px 0;}</style></head><body>
  <div class="hdr"><h1 style="margin:0;font-size:20px;">📊 Paso 2 OED — Análisis de tu Sueldo, Gastos y Flujo de Caja</h1>
  <p style="margin:4px 0 0;font-size:13px;">Persona asesorada: <b>${cliente}</b> · Responsable OED: <b>Nidia Velásquez</b> · Fecha: ${fecha}</p></div>
  <div class="rx"><b>Diagnóstico Financiero:</b> ${plan.recomendacion_ejecutiva}<br/><b>📌 Plan de Acción para este Mes:</b> ${plan.plan_accion_mes_oed || ""}</div>
  <h2>1. Resumen de tu Sueldo y Presupuesto (${nom.modalidad_laboral})</h2>
  <table>
    <tr><th>Ingreso Bruto</th><td>${fmtCOP(nom.ingreso_bruto_mensual_cop)}</td><th>Descuentos de Ley + Retención</th><td>${fmtCOP(nom.total_descuentos_ley_cop)}</td></tr>
    <tr><th>Ingreso Disponible Neto</th><td><strong>${fmtCOP(d.ingreso_neto_mensual_cop)}</strong></td><th>Costos Fijos Vitales</th><td>${fmtCOP(d.gastos_fijos_vitales_cop)}</td></tr>
    <tr><th>Estilo de Vida + Deudas</th><td>${fmtCOP(d.gastos_variables_estilo_vida_cop + d.cuotas_deuda_mensual_cop)}</td><th>Gastos Hormiga + 4x1000</th><td>${fmtCOP(d.fuga_total_mensual_cop)}</td></tr>
    <tr><th>Excedente Mensual Libre</th><td><strong>${fmtCOP(d.excedente_mensual_cop)}</strong></td><th>Potencial a 10 Años</th><td>${fmtCOP(d.radiografia_fugas.costo_oportunidad_fuga_total_10a_nominal_cop)}</td></tr>
  </table>
  <h2>2. Microgastos Identificados</h2>
  <table><thead><tr><th>Concepto</th><th>Unitario</th><th>Veces/Mes</th><th>Subtotal Mensual</th></tr></thead><tbody>${microHtml}</tbody></table>
  <h2>3. Consejos de tu Asesor Financiero para Ahorrar</h2><ul>${tipsHtml}</ul>
  <h2>4. ¿En Qué Te Recomendamos Abstenerte?</h2><ul>${absHtml}</ul>
  </body></html>`;

  const blob = new Blob([doc], { type: "text/html;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `acta_oed_paso2_${cliente.replaceAll(" ", "_").toLowerCase()}.html`;
  a.click();
}

function copiarContratoJSON() {
  if (!estadoUltimoResultado) return;
  navigator.clipboard.writeText(JSON.stringify(estadoUltimoResultado.contrato_oed, null, 2));
  const b = document.getElementById("btn_copiar_json");
  b.textContent = "✅ ¡Copiado!";
  setTimeout(() => { b.textContent = "📋 Copiar JSON"; }, 1800);
}

function descargarContratoJSON() {
  if (!estadoUltimoResultado) return;
  const completo = {
    asesorado: document.getElementById("nombre_asesorado_top").value || "Asesorado",
    fecha_exportacion: new Date().toISOString(),
    parametros_formulario: obtenerPayloadFormulario(),
    contrato_oed: estadoUltimoResultado.contrato_oed,
    guia_asesoria: estadoUltimoResultado.diagnostico.guia_asesoria
  };
  const blob = new Blob([JSON.stringify(completo, null, 2)], { type: "application/json" });
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "expediente_asesoria_mod1.json"; a.click();
}

function exportarCSV() {
  if (!estadoUltimoResultado) return;
  const d = estadoUltimoResultado.diagnostico;
  const c = estadoUltimoResultado.contrato_oed;
  const guia = d.guia_asesoria || { consejos_ahorro: [], en_que_abstenerse: [] };
  const esc = (s) => `"${String(s).replaceAll('"', '""')}"`;

  let filas = ["Seccion,Concepto,Valor_o_Detalle"];
  Object.entries(c).forEach(([k, v]) => filas.push(`Contrato_OED,${esc(k)},${esc(v)}`));
  (d.radiografia_fugas.detalle_items || []).forEach(m => {
    filas.push(`Microgasto,${esc(m.concepto)},${esc(m.gasto_mensual_cop)}`);
  });
  (guia.consejos_ahorro || []).forEach(t => {
    filas.push(`Consejo_Ahorro,${esc(t.titulo)},${esc(t.accion)}`);
  });
  (guia.en_que_abstenerse || []).forEach(ab => {
    filas.push(`Abstenerse_${ab.severidad},${esc(ab.habito_o_rubro)},${esc(ab.accion_inmediata)}`);
  });

  const blob = new Blob(["\uFEFF" + filas.join("\n")], { type: "text/csv;charset=utf-8;" });
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "reporte_asesoria_mod1.csv"; a.click();
}

async function inicializarAplicacion() {
  filtrarGlosarioOED();
  try {
    const res = await fetch("/api/estado_guardado");
    const guardado = await res.json();
    poblarDropdownMicrogastos(guardado.catalogo_microgastos || []);
    historialGuardado = guardado.historial || [];
    renderTablaHistorial();
    if (guardado.existe_perfil_guardado && guardado.perfil_activo?.parametros_entrada) {
      aplicarParametrosAlFormulario(guardado.perfil_activo.parametros_entrada);
      const esCeros = (guardado.perfil_activo.parametros_entrada.ingreso_bruto_mensual_cop || 0) === 0;
      document.getElementById("badge_autoguardado").textContent = esCeros ? "✓ En Ceros ($0)" : "✓ Restaurado";
    } else {
      renderItemsHormiga();
      actualizarEstadoARL();
    }
  } catch (e) {
    renderItemsHormiga();
    actualizarEstadoARL();
  }
  await recalcular();
}
window.addEventListener("DOMContentLoaded", inicializarAplicacion);
</script>
</body>
</html>
"""
)


def _construir_oed_ui_enriquecido(diagnostico: Dict[str, Any]) -> Dict[str, Any]:
    """Aplica `enriquecer_texto_con_explicaciones` de `src.oed_design_system` a todos los textos visibles."""
    plan = diagnostico["plan_accion_flujo_caja"]
    nivel = str(plan.get("nivel_semaforo_oed", "azul")).lower()
    if nivel == "verde":
        clase_css, icono, prefijo = "oed-doc-verde", "✅", "Diagnóstico Financiero favorable:"
    elif nivel == "ambar":
        clase_css, icono, prefijo = "oed-doc-ambar", "⚠️", "Revisión preventiva:"
    elif nivel == "rojo":
        clase_css, icono, prefijo = "oed-doc-rojo", "🛑", "Riesgo alto — Te recomendamos esperar:"
    else:
        clase_css, icono, prefijo = "oed-doc-azul", "ℹ️", "Análisis de tu Asesor Financiero:"

    guia = diagnostico.get("guia_asesoria", {})
    consejos_ricos = [
        {**c, "accion_html": enriquecer_texto_con_explicaciones(str(c.get("accion", "")))}
        for c in guia.get("consejos_ahorro", [])
    ]
    abstenciones_ricas = [
        {
            **a,
            "motivo_html": enriquecer_texto_con_explicaciones(str(a.get("motivo", ""))),
            "accion_html": enriquecer_texto_con_explicaciones(str(a.get("accion_inmediata", ""))),
        }
        for a in guia.get("en_que_abstenerse", [])
    ]
    alerta_norm = diagnostico["liquidacion_nomina"].get("alerta_normativa")
    return {
        "nivel": nivel,
        "clase_css": clase_css,
        "icono": icono,
        "prefijo": prefijo,
        "titulo_rico_html": enriquecer_texto_con_explicaciones(str(plan.get("titulo_diagnostico_oed", ""))),
        "explicacion_rica_html": enriquecer_texto_con_explicaciones(str(plan.get("recomendacion_ejecutiva", ""))),
        "plan_mes_rico_html": enriquecer_texto_con_explicaciones(str(plan.get("plan_accion_mes_oed", ""))),
        "alerta_normativa_html": enriquecer_texto_con_explicaciones(alerta_norm) if alerta_norm else None,
        "consejos_ricos": consejos_ricos,
        "abstenciones_ricas": abstenciones_ricas,
    }


class Mod1RequestHandler(BaseHTTPRequestHandler):
    """Servidor HTTP local conectado a `src/mod1_presupuesto.py` y `src/oed_design_system.py`."""

    ruta_activo: Path | None = None
    ruta_historial: Path | None = None

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        return

    def _send_json(self, payload: Dict[str, Any], status: int = HTTPStatus.OK) -> None:
        raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/" or self.path.startswith("/?") or self.path.startswith("/index.html"):
            raw = HTML_DASHBOARD.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return

        if self.path == "/api/health":
            self._send_json({"status": "ok", "modulo": "mod1_presupuesto", "paso_oed": 2})
            return

        if self.path == "/api/catalogo_microgastos":
            self._send_json({"catalogo_microgastos": CATALOGO_MICROGASTOS_SUGERIDOS})
            return

        if self.path == "/api/estado_guardado":
            self._send_json(
                cargar_simulacion_presupuesto(ruta_activo=self.ruta_activo, ruta_historial=self.ruta_historial)
            )
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Ruta no encontrada")

    def do_POST(self) -> None:  # noqa: N802
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length).decode("utf-8")) if length > 0 else {}

            if self.path == "/api/guardar":
                self._send_json(
                    guardar_simulacion_presupuesto(
                        datos_entrada=body.get("parametros", body),
                        nombre_escenario=body.get("nombre_escenario"),
                        guardar_en_historial=bool(body.get("guardar_en_historial", False)),
                        ruta_activo=self.ruta_activo,
                        ruta_historial=self.ruta_historial,
                        config=CONFIG_GLOBAL,
                    )
                )
                return

            if self.path == "/api/culminar_asesoria":
                self._send_json(
                    culminar_asesoria_y_reiniciar(
                        datos_cierre=body.get("datos_cierre"),
                        nombre_asesorado=body.get("nombre_asesorado"),
                        guardar_cierre_en_historial=bool(body.get("guardar_cierre_en_historial", True)),
                        ruta_activo=self.ruta_activo,
                        ruta_historial=self.ruta_historial,
                        config=CONFIG_GLOBAL,
                    )
                )
                return

            if self.path == "/api/eliminar_guardado":
                self._send_json(
                    {
                        "eliminado": True,
                        "historial": eliminar_simulacion_historial(
                            id_registro=str(body.get("id_registro", "")),
                            ruta_historial=self.ruta_historial,
                        ),
                    }
                )
                return

            if self.path == "/api/diagnostico":
                diagnostico = diagnosticar_presupuesto_y_flujo_caja(
                    ingreso_bruto_mensual_cop=float(body.get("ingreso_bruto_mensual_cop", 0.0)),
                    gastos_fijos_vitales_cop=float(body.get("gastos_fijos_vitales_cop", 0.0)),
                    gastos_variables_estilo_vida_cop=float(body.get("gastos_variables_estilo_vida_cop", 0.0)),
                    gastos_hormiga_mensual_cop=float(body.get("gastos_hormiga_mensual_cop", 0.0)),
                    cuotas_deuda_mensual_cop=float(body.get("cuotas_deuda_mensual_cop", 0.0)),
                    liquidez_actual_fondo_emergencia_cop=float(
                        body.get("liquidez_actual_fondo_emergencia_cop", 0.0)
                    ),
                    modalidad_laboral=str(body.get("modalidad_laboral", "Empleado")),
                    aporte_voluntario_afc_fpv_cop=float(body.get("aporte_voluntario_afc_fpv_cop", 0.0)),
                    clase_riesgo_arl=int(body.get("clase_riesgo_arl", 1)),
                    otros_ingresos_mensuales_cop=float(body.get("otros_ingresos_mensuales_cop", 0.0)),
                    cuotas_manejo_mensual_cop=float(body.get("cuotas_manejo_mensual_cop", 0.0)),
                    monto_movimientos_gmf_mensual_cop=float(body.get("monto_movimientos_gmf_mensual_cop", 0.0)),
                    cuenta_exenta_4x1000=bool(body.get("cuenta_exenta_4x1000", True)),
                    detalle_gastos_hormiga=body.get("detalle_gastos_hormiga"),
                    tasa_oportunidad_ea=float(body.get("tasa_oportunidad_ea", 0.10)),
                    recorte_hormiga_simulacion_pct=float(body.get("recorte_hormiga_simulacion_pct", 50.0)),
                    config=CONFIG_GLOBAL,
                )

                comparativa = comparar_modalidades_laborales(
                    ingreso_bruto_mensual_cop=float(body.get("ingreso_bruto_mensual_cop", 0.0)),
                    aporte_voluntario_afc_fpv_cop=float(body.get("aporte_voluntario_afc_fpv_cop", 0.0)),
                    clase_riesgo_arl=int(body.get("clase_riesgo_arl", 1)),
                    config=CONFIG_GLOBAL,
                )

                contrato_resumen = {
                    "usuario_id": str(body.get("usuario_id", "usr_oed_demo_001")),
                    "modalidad_laboral": diagnostico["liquidacion_nomina"]["modalidad_laboral"],
                    "ingreso_bruto_mensual_cop": diagnostico["liquidacion_nomina"]["ingreso_bruto_mensual_cop"],
                    "ingreso_neto_mensual_cop": diagnostico["ingreso_neto_mensual_cop"],
                    "excedente_mensual_cop": diagnostico["excedente_mensual_cop"],
                    "meses_fondo_emergencia": diagnostico["meses_fondo_emergencia"],
                    "costo_oportunidad_hormiga_10a_cop": diagnostico["costo_oportunidad_hormiga_10a_cop"],
                    "estado_flujo_caja": diagnostico["estado_flujo_caja"],
                    "aporte_disponible_portafolio_mod2_cop": diagnostico["plan_accion_flujo_caja"][
                        "aporte_disponible_portafolio_mod2_cop"
                    ],
                }

                self._send_json(
                    {
                        "diagnostico": diagnostico,
                        "oed_ui": _construir_oed_ui_enriquecido(diagnostico),
                        "comparativa_modalidades": comparativa,
                        "contrato_oed": contrato_resumen,
                    }
                )
                return

            self.send_error(HTTPStatus.NOT_FOUND, "Endpoint no encontrado")
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)


class ExclusiveThreadingHTTPServer(ThreadingHTTPServer):
    """Evita colisiones silenciosas de puerto en Windows (`SO_REUSEADDR`)."""

    allow_reuse_address = sys.platform != "win32"


def iniciar_servidor(host: str = "127.0.0.1", port: int = 8501, abrir_navegador: bool = True) -> None:
    server: ThreadingHTTPServer | None = None
    puerto_final = port
    for intento in range(15):
        candidato = port + intento
        try:
            server = ExclusiveThreadingHTTPServer((host, candidato), Mod1RequestHandler)
            puerto_final = candidato
            break
        except OSError:
            continue

    if server is None:
        raise RuntimeError(f"No fue posible abrir un puerto libre entre {port} y {port + 14}.")

    url = f"http://{host}:{puerto_final}"
    print("======================================================================", flush=True)
    print(" Paso 2 OED — Asesor Financiero de Confianza (Nidia Velásquez)", flush=True)
    print(f" URL activa: {url}", flush=True)
    print(" Presiona Ctrl+C para detener el servidor.", flush=True)
    print("======================================================================", flush=True)

    if abrir_navegador:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido correctamente.", flush=True)
    finally:
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UI Local Paso 2 OED — Manual de Marca Aplicado")
    parser.add_argument("--host", default="127.0.0.1", help="Host local")
    parser.add_argument("--port", type=int, default=8501, help="Puerto inicial preferido")
    parser.add_argument("--no-browser", action="store_true", help="No abrir navegador automáticamente")
    args = parser.parse_args()
    iniciar_servidor(host=args.host, port=args.port, abrir_navegador=not args.no_browser)
