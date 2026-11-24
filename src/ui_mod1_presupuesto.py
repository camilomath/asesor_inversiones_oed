"""
MÓDULO DE INTERACCIÓN VISUAL (STREAMLIT + PLOTLY) — MÓDULO 1: SUELDO, PRESUPUESTO Y GASTOS HORMIGA.
Responsable OED: Nidia Velásquez (Ingeniera Mecánica - Especialista en Presupuestos).

Cumple el Manual de Marca y Plantilla OED ("Asesor Financiero de Confianza", Paso 2):
- Bloque 1: `render_encabezado_modulo_oed(paso_actual=2)`
- Bloque 2: Entradas de nómina, presupuesto y lista desplegable de microgastos + cierre en ceros ($0)
- Bloque 3: `render_semaforo_ciudadano_oed(...)` + `📌 Plan de Acción para este Mes` + 4 métricas + Consejos/Abstención
- Bloque 4: Gráficas Plotly con `aplicar_estilo_plotly_oed(...)`
- Bloque 5: `render_glosario_interactivo_oed(...)`
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

if __package__ in (None, ""):
    _PROJECT_ROOT = Path(__file__).resolve().parent.parent
    if str(_PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(_PROJECT_ROOT))

from src.mod1_presupuesto import (
    CATALOGO_MICROGASTOS_SUGERIDOS,
    crear_figura_costo_oportunidad_hormiga,
    crear_figura_sankey_presupuesto,
    crear_figura_waterfall_sueldo,
    culminar_asesoria_y_reiniciar,
    diagnosticar_presupuesto_y_flujo_caja,
)
from src.oed_design_system import (
    aplicar_estilo_plotly_oed,
    enriquecer_texto_con_explicaciones,
    formatear_cop_claro,
    render_encabezado_modulo_oed,
    render_glosario_interactivo_oed,
    render_semaforo_ciudadano_oed,
)


def construir_resumen_ciudadano_mod1(diagnostico: Dict[str, Any]) -> Dict[str, str]:
    """Adapta el dictamen del Módulo 1 al formato oficial de `render_semaforo_ciudadano_oed`."""
    plan = diagnostico["plan_accion_flujo_caja"]
    return {
        "nivel": str(plan.get("nivel_semaforo_oed", "azul")),
        "titulo_claro": str(plan.get("titulo_diagnostico_oed", "Análisis de tu flujo de caja mensual")),
        "explicacion_humana": str(plan.get("recomendacion_ejecutiva", "")),
        "siguiente_paso_accionable": str(plan.get("plan_accion_mes_oed", "")),
    }


def render_modulo_1_presupuesto(perfil_estado: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Renderiza el Paso 2 OED en Streamlit siguiendo los 5 bloques del Manual de Marca."""
    import streamlit as st

    if "mod1_ceros" not in st.session_state:
        st.session_state["mod1_ceros"] = False
    if "mod1_micro_items" not in st.session_state:
        st.session_state["mod1_micro_items"] = []

    # BLOQUE 1: Encabezado OED + Barra de Progreso (Paso 2 — Nidia Velásquez)
    render_encabezado_modulo_oed(paso_actual=2)

    base = {} if st.session_state["mod1_ceros"] else (perfil_estado or {})
    bruto_def = 0.0 if st.session_state["mod1_ceros"] else float(base.get("ingreso_bruto_mensual_cop", 6_500_000.0))
    fijos_def = 0.0 if st.session_state["mod1_ceros"] else float(base.get("gastos_fijos_vitales_cop", 2_800_000.0))
    vars_def = 0.0 if st.session_state["mod1_ceros"] else float(base.get("gastos_variables_estilo_vida_cop", 950_000.0))
    liq_def = 0.0 if st.session_state["mod1_ceros"] else float(base.get("liquidez_actual_fondo_emergencia_cop", 6_000_000.0))

    # BLOQUE 2: Datos de la Persona
    with st.expander("⚙️ 1. Cuéntanos tus datos de sueldo, presupuesto y microgastos", expanded=True):
        c1, c2, c3 = st.columns(3)
        modalidad = c1.selectbox(
            "Modalidad contractual",
            options=["Empleado", "Integral", "Independiente"],
            help="Define cómo se liquida tu seguridad social sobre el IBC y tu meta de fondo de emergencia.",
        )
        ingreso_bruto = c2.number_input(
            "Tu ingreso bruto mensual ($ COP)",
            min_value=0.0,
            value=bruto_def,
            step=200_000.0,
            help="Lo que devengas al mes antes de descuentos de Salud, Pensión, FSP y UVT.",
        )
        aporte_afc = c3.number_input(
            "Aporte voluntario Cuenta AFC / FPV ($ COP)",
            min_value=0.0,
            value=0.0,
            step=100_000.0,
            help="Ahorro con beneficio tributario que disminuye tu retención en la fuente.",
        )

        g1, g2, g3 = st.columns(3)
        gastos_fijos = g1.number_input("Costos fijos vitales ($ COP)", min_value=0.0, value=fijos_def, step=100_000.0)
        gastos_variables = g2.number_input("Estilo de vida y variables ($ COP)", min_value=0.0, value=vars_def, step=50_000.0)
        liquidez = g3.number_input("Fondo de emergencia actual ($ COP)", min_value=0.0, value=liq_def, step=250_000.0)

        opciones_micro = ["-- Selecciona un microgasto para agregar --"] + [
            f"[{m['categoria']}] {m['concepto']} ({formatear_cop_claro(m['monto_unitario_cop'])} × {m['frecuencia_mensual']}/mes)"
            for m in CATALOGO_MICROGASTOS_SUGERIDOS
        ]
        sel_micro = st.selectbox("📋 Lista desplegable de microgastos cotidianos", options=opciones_micro)
        b_add, b_fin = st.columns(2)
        if b_add.button("➕ Agregar microgasto seleccionado") and sel_micro != opciones_micro[0]:
            idx = opciones_micro.index(sel_micro) - 1
            elegido = CATALOGO_MICROGASTOS_SUGERIDOS[idx]
            st.session_state["mod1_micro_items"].append(dict(elegido))
        if b_fin.button("✅ Culminar Asesoría (Iniciar en $0)"):
            culminar_asesoria_y_reiniciar(
                datos_cierre={"modalidad_laboral": modalidad, "ingreso_bruto_mensual_cop": ingreso_bruto},
                guardar_cierre_en_historial=True,
            )
            st.session_state["mod1_ceros"] = True
            st.session_state["mod1_micro_items"] = []
            st.rerun()

    diag = diagnosticar_presupuesto_y_flujo_caja(
        ingreso_bruto_mensual_cop=ingreso_bruto,
        gastos_fijos_vitales_cop=gastos_fijos,
        gastos_variables_estilo_vida_cop=gastos_variables,
        gastos_hormiga_mensual_cop=0.0,
        liquidez_actual_fondo_emergencia_cop=liquidez,
        modalidad_laboral=modalidad,
        aporte_voluntario_afc_fpv_cop=aporte_afc,
        detalle_gastos_hormiga=st.session_state["mod1_micro_items"],
    )

    # BLOQUE 3: Diagnóstico Financiero OED (?) + 📌 Plan de Acción + 4 Indicadores Clave
    sem = construir_resumen_ciudadano_mod1(diag)
    render_semaforo_ciudadano_oed(
        nivel=sem["nivel"],
        titulo_claro=sem["titulo_claro"],
        explicacion_humana=sem["explicacion_humana"],
        siguiente_paso_accionable=sem["siguiente_paso_accionable"],
    )

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Ingreso Disponible Neto", formatear_cop_claro(diag["ingreso_neto_mensual_cop"]))
    k2.metric("Excedente Mensual Libre", formatear_cop_claro(diag["excedente_mensual_cop"]))
    k3.metric("Fondo de Emergencia", f"{diag['meses_fondo_emergencia']:.2f} meses")
    k4.metric("Costo Oportunidad 10a", formatear_cop_claro(diag["costo_oportunidad_hormiga_10a_cop"]))

    guia = diag["guia_asesoria"]
    if guia["sesion_activa"]:
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("💡 Consejos Personalizados de Ahorro")
            for c in guia["consejos_ahorro"]:
                st.markdown(f"- **{c['titulo']}:** {enriquecer_texto_con_explicaciones(c['accion'])}", unsafe_allow_html=True)
        with col_b:
            st.subheader("🛑 ¿En Qué Te Recomendamos Abstenerte?")
            for a in guia["en_que_abstenerse"]:
                st.markdown(
                    f"- **[{a['severidad']}] {a['habito_o_rubro']}:** {enriquecer_texto_con_explicaciones(a['accion_inmediata'])}",
                    unsafe_allow_html=True,
                )

    st.download_button(
        "💾 Guardar Expediente de Asesoría (.json)",
        data=json.dumps(diag, ensure_ascii=False, indent=2),
        file_name="asesoria_mod1_oed.json",
        mime="application/json",
    )

    # BLOQUE 4: Gráficas Interactivas con la Paleta Oficial OED
    if diag["ingreso_neto_mensual_cop"] > 0:
        fig_sk = aplicar_estilo_plotly_oed(crear_figura_sankey_presupuesto(diag))
        fig_wf = aplicar_estilo_plotly_oed(crear_figura_waterfall_sueldo(diag))
        st.plotly_chart(fig_sk, use_container_width=True)
        st.plotly_chart(fig_wf, use_container_width=True)
        if diag["fuga_total_mensual_cop"] > 0:
            fig_op = aplicar_estilo_plotly_oed(crear_figura_costo_oportunidad_hormiga(diag))
            st.plotly_chart(fig_op, use_container_width=True)

    # BLOQUE 5: Diccionario Financiero Desplegable (5 Familias de Términos OED)
    render_glosario_interactivo_oed(["SMMLV", "IBC", "UVT", "CUENTA_AFC", "GMF_4X1000", "FOGAFIN", "FIC", "EA", "IPC"])
    return diag


if __name__ == "__main__":
    render_modulo_1_presupuesto()
