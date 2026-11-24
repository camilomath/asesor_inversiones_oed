"""
MÓDULO DE INTERACCIÓN VISUAL (STREAMLIT + PLOTLY) — MÓDULO 4: FINCA RAÍZ COLOMBIANA.
Responsable OED: Jesi (Administradora de Empresas - Magíster en Analítica).

Diseñado con arquitectura dual:
1. Ejecución autónoma en la rama `Jesi`:
      py -m streamlit run src/ui_mod4_finca_raiz.py
2. Integración directa en 1 línea dentro de `app.py` (Etapa 5 del Taller OED):
      from src.ui_mod4_finca_raiz import render_modulo_4_finca_raiz
      resultado_mod4 = render_modulo_4_finca_raiz(perfil_estado=estado_usuario)
"""

from __future__ import annotations

import csv
import html
import io
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Permite ejecutar `streamlit run src/ui_mod4_finca_raiz.py` desde la raíz sin errores de importación
if __package__ in (None, ""):
    _PROJECT_ROOT = Path(__file__).resolve().parent.parent
    if str(_PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(_PROJECT_ROOT))

from src.finance import cargar_configuracion
from src.mod4_finca_raiz import (
    estimar_costo_oportunidad_por_perfil_oed,
    evaluar_inversion_finca_raiz,
)
from src.oed_design_system import (
    _CSS_MEDICO_AMIGO_OED,
    GLOSARIO_LENGUAJE_CLARO_OED,
    RUTA_CLINICA_FINANCIERA_OED,
    aplicar_estilo_plotly_oed,
    enriquecer_texto_con_explicaciones,
    formatear_cop_claro,
    render_encabezado_modulo_oed,
    render_glosario_interactivo_oed,
    render_semaforo_ciudadano_oed,
)


# ==============================================================================
# 1. ADAPTADORES PUROS DE ESTADO Y LENGUAJE CIUDADANO (TESTEABLES SIN UI)
# ==============================================================================


def extraer_valores_iniciales_desde_estado(
    perfil_estado: Dict[str, Any] | None = None,
    config: Dict[str, Any] | None = None,
    cargar_archivo_mod1_local: bool = False,
) -> Dict[str, Any]:
    """
    Obtiene los valores por defecto para los controles interactivos del Módulo 4:
    - Conecta salidas previas de Nidia (Módulo 1: modalidad laboral, prestaciones reales, fondo de emergencia),
      Camilo (Módulo 2: portafolio salarial / AFC), Catalina (Módulo 3: cuotas de otras deudas actuales)
      y Salin (Módulo 6: perfil de riesgo y tasa esperada de portafolio).
    - Opcionalmente lee `data/processed/perfil_mod1_activo.json` si se ejecuta en modo UI local.
    - De lo contrario, usa el `perfil_semilla_taller` de `config/config.yaml` para trabajar sin bloqueos.
    """
    cfg = config or cargar_configuracion()
    semilla = cfg.get("perfil_semilla_taller", {})
    estado_raw: Dict[str, Any] = dict(perfil_estado) if perfil_estado else {}

    if not estado_raw and cargar_archivo_mod1_local:
        ruta_mod1 = Path(__file__).resolve().parent.parent / "data" / "processed" / "perfil_mod1_activo.json"
        if ruta_mod1.exists():
            try:
                cargado = json.loads(ruta_mod1.read_text(encoding="utf-8"))
                if isinstance(cargado, dict):
                    estado_raw = cargado
            except Exception:
                estado_raw = {}

    # Soporta tanto diccionario plano como estructuras anidadas de integración entre módulos
    estado: Dict[str, Any] = {}
    for sub_key in (
        "entradas",
        "diagnostico",
        "resultado_mod1",
        "modulo1_nidia",
        "modulo2_camilo",
        "modulo3_catalina",
        "modulo6_salin",
    ):
        if isinstance(estado_raw.get(sub_key), dict):
            estado.update(estado_raw[sub_key])
    estado.update(estado_raw)

    ingreso_bruto_semilla = float(semilla.get("ingreso_bruto_mensual_cop", 6_500_000.0))
    # Si Nidia (Módulo 1) ya calculó `ingreso_neto_mensual_cop`, lo tomamos; si no, estimamos ~91% neto
    ingreso_titular_neto = float(
        estado.get("ingreso_neto_mensual_cop", round(ingreso_bruto_semilla * 0.91, -3))
    )
    ingreso_pareja_neto = float(estado.get("ingreso_pareja_neto_cop", 3_500_000.0))

    # Modalidad laboral y prestaciones reales (Conexión Módulo 1 — Nidia: Empleado vs. Independiente/OPS vs. Integral)
    nomina = estado.get("liquidacion_nomina", {}) if isinstance(estado.get("liquidacion_nomina"), dict) else {}
    mod_lab_raw = str(
        estado.get("modalidad_laboral", nomina.get("modalidad_laboral", "Empleado"))
    ).strip().lower()
    if mod_lab_raw in ("independiente", "contratista", "ops"):
        modalidad_laboral_norm = "Independiente"
    elif mod_lab_raw in ("integral", "salario integral"):
        modalidad_laboral_norm = "Integral"
    else:
        modalidad_laboral_norm = "Empleado"

    provisiones = estado.get(
        "provisiones_prestacionales_informativas",
        nomina.get("provisiones_prestacionales_informativas"),
    )
    if "cesantias_y_primas_anuales_cop" in estado:
        cesantias_y_primas_anuales = float(estado["cesantias_y_primas_anuales_cop"])
    elif isinstance(provisiones, dict):
        mensual_prestaciones = (
            float(provisiones.get("prima_servicios_mensualizada_cop", 0.0))
            + float(provisiones.get("cesantias_mensualizadas_cop", 0.0))
            + float(provisiones.get("intereses_cesantias_mensualizados_cop", 0.0))
        )
        cesantias_y_primas_anuales = round(mensual_prestaciones * 12.0, 2)
    elif modalidad_laboral_norm in ("Independiente", "Integral"):
        cesantias_y_primas_anuales = 0.0
    else:
        cesantias_y_primas_anuales = 5_500_000.0

    fondo_emergencia_completo = bool(estado.get("fondo_emergencia_completo", True))

    # Si Camilo (Módulo 2) ya proyectó capital o cuenta AFC previa, lo tomamos; si no, semilla $8M
    ahorro_previo_afc = float(
        estado.get(
            "ahorro_previo_afc_cop",
            estado.get("liquidez_actual_fondo_emergencia_cop", 8_000_000.0),
        )
    )

    # Cuotas mensuales de otras deudas vigentes (Conexión Módulo 3 — Catalina y Módulo 1 — Nidia)
    cuotas_otras_deudas = float(
        estado.get(
            "cuotas_otras_deudas_mensuales_cop",
            estado.get(
                "cuota_mensual_total_actual_cop",
                estado.get("cuotas_deuda_mensual_cop", 0.0),
            ),
        )
    )

    # Costo de oportunidad personalizado según Perfil de Riesgo (Conexión Módulo 6 — Salin y Módulo 2 — Camilo)
    cok_info = estimar_costo_oportunidad_por_perfil_oed(estado, cfg)

    conectado = any(
        llave in estado
        for llave in (
            "ingreso_neto_mensual_cop",
            "modalidad_laboral",
            "liquidacion_nomina",
            "cuota_mensual_total_actual_cop",
            "tasa_ponderada_esperada_ea_pct",
            "perfil_riesgo",
        )
    )

    return {
        "valor_inmueble_cop": float(estado.get("valor_inmueble_cop", 200_000_000.0)),
        "ingreso_titular_neto_cop": ingreso_titular_neto,
        "ingreso_pareja_neto_cop": ingreso_pareja_neto,
        "ingreso_familiar_neto_cop": ingreso_titular_neto + ingreso_pareja_neto,
        "modalidad_laboral_titular": modalidad_laboral_norm,
        "fondo_emergencia_completo": fondo_emergencia_completo,
        "cuotas_otras_deudas_mensuales_cop": cuotas_otras_deudas,
        "porcentaje_cuota_inicial_pct": int(round(float(estado.get("porcentaje_cuota_inicial", 0.30)) * 100)),
        "plazo_entrega_planos_meses": int(estado.get("plazo_entrega_planos_meses", 24)),
        "plazo_credito_anios": int(estado.get("plazo_credito_anios", 15)),
        "tasa_ea_pesos_pct": round(float(estado.get("tasa_ea_pesos", 0.115)) * 100.0, 2),
        "tasa_ea_uvr_spread_pct": round(float(estado.get("tasa_ea_uvr_mas_spread", 0.065)) * 100.0, 2),
        "costo_oportunidad_ea_pct": round(float(cok_info["costo_oportunidad_ea"]) * 100.0, 2),
        "fuente_costo_oportunidad": str(cok_info["fuente"]),
        "ahorro_previo_afc_cop": ahorro_previo_afc,
        "cesantias_y_primas_anuales_cop": cesantias_y_primas_anuales,
        "canon_arriendo_estimado_cop": float(estado.get("canon_arriendo_mensual_estimado_cop", 1_400_000.0)),
        "modalidad_financiacion": str(estado.get("modalidad_financiacion", "HIPOTECARIO")).upper(),
        "conectado_con_modulos_previos": conectado,
    }


def generar_resumen_ejecutivo_ciudadano(resultado: Dict[str, Any]) -> Dict[str, str]:
    """
    Traduce el dictamen técnico del Módulo 4 a la voz cercana del 'Asesor Financiero de Confianza'
    definida en el Manual de Marca OED, incluyendo Diagnóstico Financiero claro y Plan de Acción mensual.
    """
    dictamen = resultado["dictamen_viabilidad_inmobiliaria"]
    cuota_pesos = resultado["primera_cuota_credito_cop"]
    tope_30 = resultado["tope_cuota_ley_546_30pct_cop"]

    if dictamen == "PENDIENTE_DATOS_INMUEBLE_E_INGRESOS":
        plan = (
            "Escribe el precio comercial de la vivienda que estás evaluando y tu ingreso neto mensual; "
            "si es sobre planos, simularemos también tu ahorro en Cuenta AFC."
        )
        return {
            "nivel": "info",
            "titulo": "Simulador listo: ingresa el valor del inmueble y tus ingresos para tu Diagnóstico Financiero",
            "mensaje": (
                "Aún tienes el valor del apartamento o el ingreso mensual del hogar en $0 COP. "
                "Anótalos arriba para evaluar el límite legal del 30% de la Ley 546 "
                "y comparar con números claros entre Pesos, UVR o invertir en un FIC."
            ),
            "plan_accion": plan,
            "receta": plan,
        }
    if dictamen == "CUMPLE_LEY_546_PERO_EXCEDE_ENDEUDAMIENTO_BANCARIO_TOTAL":
        otras_deudas = resultado.get("cuotas_otras_deudas_mensuales_cop", 0.0)
        carga_pct = resultado.get("relacion_carga_financiera_total_pct", 0.0)
        liberar = resultado.get("cupo_mensual_a_liberar_deudas_cop", 0.0)
        plan = (
            f"Antes de radicar el crédito hipotecario, aplica el método Avalancha del Módulo 3 para liberar al menos "
            f"{formatear_cop_claro(liberar)}/mes de cuotas actuales mientras ahorras tu inicial en Cuenta AFC."
        )
        return {
            "nivel": "warning",
            "titulo": "Cumples el 30% de Ley 546 en vivienda, pero tus otras deudas superan el cupo bancario total (40%)",
            "mensaje": (
                f"La cuota sola del apartamento ({formatear_cop_claro(cuota_pesos)}) sí respeta el tope de la Ley 546 "
                f"({formatear_cop_claro(tope_30)}), pero al sumar tus otras deudas actuales "
                f"({formatear_cop_claro(otras_deudas)}/mes) comprometes el {carga_pct:.1f}% de tus ingresos "
                "(las entidades suelen aprobar hasta el 40% sumando todas las obligaciones)."
            ),
            "plan_accion": plan,
            "receta": plan,
        }

    if dictamen == "VIABLE_COMPRA_EN_PESOS_OPTIMA":
        plan = (
            "Programa desde este mes tu ahorro del encargo fiduciario a través de una Cuenta AFC para optimizar "
            "retención en la fuente medida en UVT y solicita cotización en Pesos Cuota Fija."
        )
        return {
            "nivel": "success",
            "titulo": "Indicadores clave favorables para comprar en Pesos (cumples la Ley 546)",
            "mensaje": (
                f"Con números claros, la primera cuota fija en Pesos ({formatear_cop_claro(cuota_pesos)}) "
                f"respeta con holgura el tope legal del 30% de tu hogar ({formatear_cop_claro(tope_30)}) y el "
                f"inmueble proyecta una TIR del {resultado['tir_inmobiliaria_ea_pct']}% EA, superando tu costo de oportunidad."
            ),
            "plan_accion": plan,
            "receta": plan,
        }
    if dictamen == "VIABLE_VIVIENDA_PROPIA_PERO_FIC_SUPERA_RENTA":
        plan = (
            "Si tu meta es vivienda propia, usa tu Cuenta AFC para aprovechar el beneficio tributario; si solo buscas "
            "rentabilidad financiera sin administrar arrendatarios, compara invertir ese capital en un FIC."
        )
        return {
            "nivel": "info",
            "titulo": "Viable para vivienda propia (cumples Ley 546), aunque para renta pura un FIC rinde más",
            "mensaje": (
                f"Tu flujo de caja responde bien: la cuota en Pesos ({formatear_cop_claro(cuota_pesos)}) cabe "
                f"dentro del tope legal ({formatear_cop_claro(tope_30)}). Si es para habitarla en familia, es viable; si la "
                "evalúas únicamente como inversión para arrendar, hoy su Cap Rate neto rinde menos que un FIC o un CDT."
            ),
            "plan_accion": plan,
            "receta": plan,
        }
    if dictamen == "SOLO_CUMPLE_EN_UVR_CON_RIESGO_INFLACIONARIO":
        plan = (
            "Amplía unos meses el ahorro sobre planos en encargo fiduciario o incrementa tus aportes en Cuenta AFC "
            "para disminuir el monto del préstamo y pasar con seguridad a Pesos Cuota Fija."
        )
        return {
            "nivel": "warning",
            "titulo": "Revisión preventiva: hoy solo cumples en UVR y conviene vigilar la inflación",
            "mensaje": (
                f"En Pesos Fijos la cuota ({formatear_cop_claro(cuota_pesos)}) supera el tope del 30% de la "
                f"Ley 546 ({formatear_cop_claro(tope_30)}), y solo cumple en UVR "
                f"({formatear_cop_claro(resultado['primera_cuota_uvr_cop'])}). Como en UVR el saldo sube con el IPC, "
                "tomarlo así puede presionar tu flujo mensual en los próximos años."
            ),
            "plan_accion": plan,
            "receta": plan,
        }
    plan = (
        f"Tienes dos alternativas concretas en pesos: sumar ingresos familiares con co-deudor por "
        f"{formatear_cop_claro(resultado['deficit_ingreso_familiar_cop'])}/mes, o reunir "
        f"{formatear_cop_claro(resultado['cuota_inicial_extra_requerida_ley_546_cop'])} adicionales de cuota inicial en Cuenta AFC."
    )
    return {
        "nivel": "error",
        "titulo": "Riesgo alto — Te recomendamos esperar: hoy la cuota supera el límite del 30% (Ley 546)",
        "mensaje": (
            f"Evaluarlo antes de firmar protege tu patrimonio: la primera cuota ({formatear_cop_claro(cuota_pesos)}) supera "
            f"el tope legal del 30% de los ingresos del hogar ({formatear_cop_claro(tope_30)}). Ajustando la cuota inicial "
            "o el ingreso familiar puedes alcanzar la meta sin sobreendeudarte."
        ),
        "plan_accion": plan,
        "receta": plan,
    }


def _filas_a_csv_bytes(filas: List[Dict[str, Any]]) -> bytes:
    """Convierte una lista de diccionarios en bytes CSV UTF-8 con BOM (compatible con Excel en Colombia)."""
    if not filas:
        return b""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(filas[0].keys()))
    writer.writeheader()
    writer.writerows(filas)
    return ("\ufeff" + buffer.getvalue()).encode("utf-8")


# ==============================================================================
# 2. CONSTRUCTORES DE GRÁFICAS INTERACTIVAS EN PLOTLY
# ==============================================================================


def construir_figuras_plotly_mod4(resultado: Dict[str, Any]) -> Dict[str, Any]:
    """Construye las 3 figuras interactivas de Plotly del Módulo 4 a partir del resultado detallado."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    plan = resultado["plan_cuota_inicial_detalle"]
    amort = resultado["amortizacion_detalle"]

    # --- Figura 1: Encargo Fiduciario Sobre Planos (Paleta Oficial OED) ---
    cronograma = plan["cronograma_fiduciario_mensual"]
    meses_fid = [r["mes"] for r in cronograma]
    fig_planos = make_subplots(specs=[[{"secondary_y": True}]])
    if cronograma:
        fig_planos.add_trace(
            go.Bar(
                x=meses_fid,
                y=[r["cuota_mensual_afc_cop"] for r in cronograma],
                name="Cuota Mensual (Cuenta AFC)",
                marker_color="#1D4ED8",
            ),
            secondary_y=False,
        )
        fig_planos.add_trace(
            go.Bar(
                x=meses_fid,
                y=[r["abono_extra_cesantias_primas_subsidio_cop"] for r in cronograma],
                name="Cesantías, Primas y Subsidio",
                marker_color="#15803D",
            ),
            secondary_y=False,
        )
        fig_planos.add_trace(
            go.Scatter(
                x=meses_fid,
                y=[r["saldo_acumulado_encargo_cop"] for r in cronograma],
                name="Saldo Acumulado en Fiducia",
                mode="lines+markers",
                line=dict(color="#EA580C", width=3),
            ),
            secondary_y=True,
        )
    fig_planos.update_layout(
        barmode="stack",
        xaxis_title="Mes de Entrega sobre Planos",
    )
    fig_planos.update_yaxes(title_text="Aporte del Mes (COP)", secondary_y=False)
    fig_planos.update_yaxes(title_text="Saldo Acumulado (COP)", secondary_y=True)

    # --- Figura 2: Comparativa Ley 546 (Cuotas y Saldos Pesos vs. UVR) ---
    t_fija = amort["tabla_pesos_cuota_fija"]
    t_const = amort["tabla_pesos_abono_constante"]
    t_uvr = amort["tabla_uvr_ciclica"]
    tope_ley_546 = resultado["tope_cuota_ley_546_30pct_cop"]

    fig_amort = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            "Cuota Mensual (COP) vs. Cinturón 30% Ley 546",
            "Saldo de la Deuda en Pesos (Efecto Inflación UVR)",
        ),
    )
    fig_amort.add_trace(
        go.Scatter(
            x=[r["anio"] for r in t_fija],
            y=[r["cuota_total_cop"] for r in t_fija],
            name="Pesos Cuota Fija",
            line=dict(color="#1D4ED8", width=3),
        ),
        row=1,
        col=1,
    )
    fig_amort.add_trace(
        go.Scatter(
            x=[r["anio"] for r in t_const],
            y=[r["cuota_total_cop"] for r in t_const],
            name="Abono Constante Capital",
            line=dict(color="#15803D", width=2, dash="dot"),
        ),
        row=1,
        col=1,
    )
    fig_amort.add_trace(
        go.Scatter(
            x=[r["anio"] for r in t_uvr],
            y=[r["cuota_total_cop"] for r in t_uvr],
            name="UVR Indexada al IPC",
            line=dict(color="#DC2626", width=3),
        ),
        row=1,
        col=1,
    )
    fig_amort.add_hline(
        y=tope_ley_546,
        line_dash="dash",
        line_color="#475569",
        annotation_text=f"Tope 30% ({formatear_cop_claro(tope_ley_546)})",
        row=1,
        col=1,
    )

    fig_amort.add_trace(
        go.Scatter(
            x=[r["anio"] for r in t_fija],
            y=[r["saldo_capital_cop"] for r in t_fija],
            name="Saldo Pesos Fija",
            line=dict(color="#1D4ED8", width=3),
            showlegend=False,
        ),
        row=1,
        col=2,
    )
    fig_amort.add_trace(
        go.Scatter(
            x=[r["anio"] for r in t_const],
            y=[r["saldo_capital_cop"] for r in t_const],
            name="Saldo Abono Constante",
            line=dict(color="#15803D", width=2, dash="dot"),
            showlegend=False,
        ),
        row=1,
        col=2,
    )
    fig_amort.add_trace(
        go.Scatter(
            x=[r["anio"] for r in t_uvr],
            y=[r["saldo_capital_cop"] for r in t_uvr],
            name="Saldo UVR en COP",
            line=dict(color="#DC2626", width=3),
            showlegend=False,
        ),
        row=1,
        col=2,
    )
    fig_amort.update_xaxes(title_text="Año del Crédito")
    fig_amort.update_yaxes(title_text="Pesos Colombianos (COP)")

    # --- Figura 3: Flujos del Inversionista y Comparativa Patrimonial a 10 años ---
    comp = resultado["comparativa_estrategias_10a"]
    flujos = resultado["flujos_anuales_inversionista_cop"]
    estrategias = ["Comprar en Pesos", "Comprar en UVR", "Arrendar + FIC Inmobiliario"]
    patrimonios = [
        comp["comprar_pesos_patrimonio_10a_cop"],
        comp["comprar_uvr_patrimonio_10a_cop"],
        comp["arrendar_e_invertir_fic_patrimonio_10a_cop"],
    ]

    fig_renta = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            "Flujo de Caja Anual del Inversionista (Años 0 a 10)",
            "Patrimonio Neto Consolidado al Año 10",
        ),
    )
    fig_renta.add_trace(
        go.Bar(
            x=list(range(len(flujos))),
            y=flujos,
            marker_color=["#DC2626" if f < 0 else "#15803D" for f in flujos],
            name="Flujo Neto (COP)",
        ),
        row=1,
        col=1,
    )
    fig_renta.add_trace(
        go.Bar(
            x=estrategias,
            y=patrimonios,
            marker_color=["#1D4ED8", "#EA580C", "#7C3AED"],
            text=[f"${p / 1e6:,.1f}M" for p in patrimonios],
            textposition="auto",
            name="Patrimonio Año 10",
        ),
        row=1,
        col=2,
    )
    fig_renta.update_layout(showlegend=False)
    fig_renta.update_xaxes(title_text="Año", row=1, col=1)
    fig_renta.update_yaxes(title_text="COP", row=1, col=1)
    fig_renta.update_yaxes(title_text="Patrimonio Neto (COP)", row=1, col=2)

    return {
        "fig_planos": aplicar_estilo_plotly_oed(
            fig_planos,
            titulo="Acumulación de tu Cuota Inicial en Encargo Fiduciario + Cuenta AFC",
            altura=400,
        ),
        "fig_amortizacion": aplicar_estilo_plotly_oed(fig_amort, altura=430),
        "fig_rentabilidad": aplicar_estilo_plotly_oed(fig_renta, altura=420),
    }


# ==============================================================================
# 3. COMPONENTE VISUAL DE STREAMLIT (AUTÓNOMO Y CONECTABLE A APP.PY)
# ==============================================================================


def render_modulo_4_finca_raiz(
    perfil_estado: Dict[str, Any] | None = None,
    config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Renderiza la interfaz interactiva completa del Módulo 4 (Jesi) en Streamlit
    y retorna el diccionario de resultados compatible con el Contrato de Integración OED.
    """
    import streamlit as st

    cfg = config or cargar_configuracion()
    macro = cfg["parametros_macro_colombia"]
    estado_previo = perfil_estado if perfil_estado is not None else dict(st.session_state.get("perfil_usuario", {}))
    defaults = extraer_valores_iniciales_desde_estado(
        estado_previo,
        cfg,
        cargar_archivo_mod1_local=True,
    )

    # BLOQUE 1: Encabezado del Consultorio + Barra de Progreso (Pasos 0 al 6)
    render_encabezado_modulo_oed(paso_actual=5)

    if defaults["conectado_con_modulos_previos"]:
        st.info(
            "🔗 Datos conectados automáticamente con los módulos previos del equipo OED "
            f"(Modalidad: {defaults['modalidad_laboral_titular']} | COK: {defaults['costo_oportunidad_ea_pct']}% EA)."
        )
    else:
        st.info(
            f"🌱 Modo Autónomo Activo: Usando valores iniciales del Usuario Semilla OED "
            f"(SMMLV {macro['anio_vigencia']}: ${macro['smmlv_cop']:,.0f} COP | IPC DANE: {macro['ipc_anual_dane'] * 100:.1f}%)."
        )

    # --- Panel Interactivo de Entradas del Usuario ---
    with st.expander("⚙️ 1. Ingresa los Datos de tu Hogar, del Apartamento y del Crédito", expanded=True):
        col_hogar, col_inmueble, col_credito = st.columns(3)

        with col_hogar:
            st.subheader("👨‍👩‍👧 Ingresos, Empleo y Deudas")
            opciones_laborales = ["Empleado", "Independiente", "Integral"]
            idx_laboral = (
                opciones_laborales.index(defaults["modalidad_laboral_titular"])
                if defaults["modalidad_laboral_titular"] in opciones_laborales
                else 0
            )
            modalidad_laboral = st.selectbox(
                "Modalidad laboral titular (Módulo 1)",
                options=opciones_laborales,
                index=idx_laboral,
                help="En Independiente/OPS o Salario Integral no recibes primas ni cesantías adicionales del empleador.",
            )
            ingreso_titular = st.number_input(
                "Tu ingreso neto mensual (COP)",
                min_value=0.0,
                value=defaults["ingreso_titular_neto_cop"],
                step=250_000.0,
                format="%.0f",
                help="Sueldo libre después de Salud, Pensión y Retefuente (entregado por el Módulo 1 de Nidia).",
            )
            ingreso_pareja = st.number_input(
                "Ingreso neto mensual pareja / co-deudor (COP)",
                min_value=0.0,
                value=defaults["ingreso_pareja_neto_cop"],
                step=250_000.0,
                format="%.0f",
                help="Pon 0 si compras de forma individual, o suma ingresos familiares para cumplir la Ley 546.",
            )
            cuotas_otras_deudas = st.number_input(
                "Cuotas mensuales de otras deudas actuales (COP)",
                min_value=0.0,
                value=defaults["cuotas_otras_deudas_mensuales_cop"],
                step=100_000.0,
                format="%.0f",
                help="Tarjetas, libre inversión o vehículo (Módulo 3 de Catalina). Los bancos vigilan que todo junto no supere el 40%.",
            )
            ahorro_previo_afc = st.number_input(
                "Ahorro previo disponible / Cuenta AFC (COP)",
                min_value=0.0,
                value=defaults["ahorro_previo_afc_cop"],
                step=1_000_000.0,
                format="%.0f",
            )
            cesantias_primas = st.number_input(
                "Cesantías + Primas anuales para vivienda (COP)",
                min_value=0.0,
                value=0.0 if modalidad_laboral in ("Independiente", "Integral") and not defaults["conectado_con_modulos_previos"] else defaults["cesantias_y_primas_anuales_cop"],
                step=500_000.0,
                format="%.0f",
            )
            fondo_emergencia_ok = st.checkbox(
                "Mi fondo de emergencia ya está completo y separado de esta cuota inicial",
                value=defaults["fondo_emergencia_completo"],
            )
            aplicar_subsidio_ccf = st.checkbox(
                "Aplicar Subsidio Caja de Compensación (si ingreso <= 4 SMMLV y es VIS/VIP)",
                value=True,
            )

        with col_inmueble:
            st.subheader("🏢 El Inmueble")
            valor_inmueble = st.number_input(
                "Valor comercial del inmueble (COP)",
                min_value=0.0,
                value=defaults["valor_inmueble_cop"],
                step=5_000_000.0,
                format="%.0f",
            )
            modalidad = st.selectbox(
                "Modalidad de financiación",
                options=["HIPOTECARIO", "LEASING"],
                index=0 if defaults["modalidad_financiacion"] != "LEASING" else 1,
                help="En Leasing Habitacional puedes financiar hasta 80%-85% y no desembolsas escrituración al inicio.",
            )
            pct_cuota_inicial = st.slider(
                "Porcentaje de Cuota Inicial (%)",
                min_value=0,
                max_value=80,
                value=defaults["porcentaje_cuota_inicial_pct"],
                step=1,
            )
            plazo_planos_meses = st.slider(
                "Plazo entrega sobre planos (meses en fiducia)",
                min_value=0,
                max_value=48,
                value=defaults["plazo_entrega_planos_meses"],
                step=1,
            )

        with col_credito:
            st.subheader("🏦 Crédito y Renta")
            plazo_anios = st.slider(
                "Plazo del crédito (años)",
                min_value=5,
                max_value=30,
                value=defaults["plazo_credito_anios"],
                step=1,
            )
            tasa_ea_pesos_pct = st.number_input(
                "Tasa crédito en Pesos (% EA)",
                min_value=0.0,
                max_value=26.0,
                value=defaults["tasa_ea_pesos_pct"],
                step=0.25,
            )
            tasa_uvr_spread_pct = st.number_input(
                "Tasa real en UVR + Spread (% EA sin IPC)",
                min_value=0.0,
                max_value=18.0,
                value=defaults["tasa_ea_uvr_spread_pct"],
                step=0.25,
            )
            canon_estimado = st.number_input(
                "Canon mensual de arriendo estimado (COP)",
                min_value=0.0,
                value=defaults["canon_arriendo_estimado_cop"],
                step=100_000.0,
                format="%.0f",
                help="La Ley 820 de 2003 limita el canon mensual máximo al 1% del valor comercial.",
            )
            cok_ea_pct = st.number_input(
                "Rentabilidad alternativa FIC / Portafolio (% EA)",
                min_value=0.0,
                max_value=25.0,
                value=defaults["costo_oportunidad_ea_pct"],
                step=0.25,
                help="Se calibra automáticamente si vienes con perfil de riesgo del Módulo 6 (Salin) o portafolio del Módulo 2 (Camilo).",
            )

    ingreso_familiar_total = ingreso_titular + ingreso_pareja

    # --- Ejecución en Vivo del Motor Matemático de Jesi ---
    resultado = evaluar_inversion_finca_raiz(
        valor_inmueble_cop=valor_inmueble,
        ingreso_familiar_neto_cop=ingreso_familiar_total,
        porcentaje_cuota_inicial=pct_cuota_inicial / 100.0,
        plazo_entrega_planos_meses=plazo_planos_meses,
        cesantias_y_primas_anuales_cop=cesantias_primas,
        plazo_credito_anios=plazo_anios,
        tasa_ea_pesos=tasa_ea_pesos_pct / 100.0,
        tasa_ea_uvr_mas_spread=tasa_uvr_spread_pct / 100.0,
        canon_arriendo_mensual_estimado_cop=canon_estimado,
        costo_oportunidad_ea=cok_ea_pct / 100.0,
        ahorro_previo_afc_cop=ahorro_previo_afc,
        aplicar_subsidio_ccf=aplicar_subsidio_ccf,
        modalidad_financiacion=modalidad,
        incluir_tablas_detalle=True,
        config=cfg,
        cuotas_otras_deudas_mensuales_cop=cuotas_otras_deudas,
        fondo_emergencia_completo=fondo_emergencia_ok,
        modalidad_laboral_titular=modalidad_laboral,
    )

    # BLOQUE 3: Diagnóstico Financiero con burbujas (?) + Plan de Acción + 4 Indicadores Clave
    semaforo = generar_resumen_ejecutivo_ciudadano(resultado)
    render_semaforo_ciudadano_oed(
        nivel=semaforo["nivel"],
        titulo_claro=semaforo["titulo"],
        explicacion_humana=semaforo["mensaje"],
        siguiente_paso_accionable=semaforo["plan_accion"],
    )

    for alerta in resultado["alertas_regulatorias"]:
        alerta_rica = enriquecer_texto_con_explicaciones(alerta)
        st.markdown(
            f'<div class="oed-doc-card oed-doc-ambar">⚖️ {alerta_rica}</div>',
            unsafe_allow_html=True,
        )

    k1, k2, k3, k4 = st.columns(4)
    k1.metric(
        "Clasificación Inmueble",
        resultado["codigo_segmento"],
        f"{resultado['valor_inmueble_smmlv']} SMMLV",
    )
    k2.metric(
        f"Cuota Inicial Mensual ({plazo_planos_meses}m)",
        f"${resultado['cuota_inicial_mensual_cop']:,.0f}",
        f"Total inicial: ${resultado['cuota_inicial_total_cop']:,.0f}",
    )
    diferencia_ley_546 = resultado["tope_cuota_ley_546_30pct_cop"] - resultado["primera_cuota_credito_cop"]
    k3.metric(
        "1ra Cuota Crédito en Pesos",
        f"${resultado['primera_cuota_credito_cop']:,.0f}",
        f"Margen Ley 546: ${diferencia_ley_546:,.0f}",
    )
    k4.metric(
        "TIR Inmobiliaria (10 años)",
        f"{resultado['tir_inmobiliaria_ea_pct']}% EA",
        f"Cap Rate Neto: {resultado['cap_rate_neto_pct']}%",
    )

    figuras = construir_figuras_plotly_mod4(resultado)

    # --- Pestañas Analíticas ---
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "🏗️ 1. Cuota Inicial & AFC",
            "⚖️ 2. Ley 546: Pesos vs. UVR",
            "📈 3. Renta (Ley 820) vs. FIC",
            "📋 4. Tablas & Integración OED",
        ]
    )

    with tab1:
        plan_det = resultado["plan_cuota_inicial_detalle"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Subsidio CCF Aplicado", f"${plan_det['subsidio_ccf_aplicado_cop']:,.0f} COP")
        c2.metric("Ahorro Tributario AFC Estimado", f"${plan_det['ahorro_tributario_afc_total_cop']:,.0f} COP")
        c3.metric("Rendimientos Fiducia", f"${plan_det['rendimientos_encargo_fiduciario_cop']:,.0f} COP")
        st.plotly_chart(figuras["fig_planos"], use_container_width=True)

    with tab2:
        amort_det = resultado["amortizacion_detalle"]
        st.plotly_chart(figuras["fig_amortizacion"], use_container_width=True)
        sens = amort_det["sensibilidad_cuota_uvr_anio_5"]
        s1, s2, s3 = st.columns(3)
        s1.metric("Cuota UVR Año 5 (IPC Bajo 3.5%)", f"${sens['ipc_bajo_3_5pct_cop']:,.0f} COP")
        s2.metric("Cuota UVR Año 5 (IPC Base DANE)", f"${sens['ipc_base_dane_cop']:,.0f} COP")
        s3.metric("Cuota UVR Año 5 (Choque IPC 8.5%)", f"${sens['ipc_alto_choque_8_5pct_cop']:,.0f} COP")

    with tab3:
        r1, r2, r3 = st.columns(3)
        r1.metric("Canon Aplicado (Ley 820 <= 1%)", f"${resultado['canon_mensual_aplicado_cop']:,.0f} COP/mes")
        r2.metric("Cash-on-Cash Año 1", f"{resultado['cash_on_cash_anual_pct']}%")
        r3.metric("VPN Inmobiliario (10 años)", f"${resultado['vpn_inmobiliario_cop']:,.0f} COP")
        st.plotly_chart(figuras["fig_rentabilidad"], use_container_width=True)

    with tab4:
        amort_det = resultado["amortizacion_detalle"]
        sistema_elegido = st.selectbox(
            "Selecciona la tabla mensual a consultar o descargar en Excel/CSV:",
            options=[
                "Crédito en Pesos — Cuota Fija (Francés)",
                "Crédito en Pesos — Abono Constante a Capital",
                "Crédito en UVR — Cuota Cíclica Indexada a IPC",
                "Plan de Encargo Fiduciario — Cuota Inicial Sobre Planos",
            ],
        )
        mapa_tablas = {
            "Crédito en Pesos — Cuota Fija (Francés)": amort_det["tabla_pesos_cuota_fija"],
            "Crédito en Pesos — Abono Constante a Capital": amort_det["tabla_pesos_abono_constante"],
            "Crédito en UVR — Cuota Cíclica Indexada a IPC": amort_det["tabla_uvr_ciclica"],
            "Plan de Encargo Fiduciario — Cuota Inicial Sobre Planos": resultado["plan_cuota_inicial_detalle"][
                "cronograma_fiduciario_mensual"
            ],
        }
        filas_mostrar = mapa_tablas[sistema_elegido]
        st.dataframe(filas_mostrar[:36], use_container_width=True)
        st.download_button(
            label="📥 Descargar tabla completa en CSV (compatible con Excel)",
            data=_filas_a_csv_bytes(filas_mostrar),
            file_name="tabla_modulo4_finca_raiz_jesi.csv",
            mime="text/csv",
        )
        with st.expander("🔌 Ver Contrato de Datos entregado al Módulo 5 (Nelson)"):
            resumen_contrato = {
                k: v
                for k, v in resultado.items()
                if k not in ("plan_cuota_inicial_detalle", "amortizacion_detalle")
            }
            st.json(resumen_contrato)

    # BLOQUE 5: Diccionario Financiero desplegable (con foco en vivienda + acceso a las 5 familias)
    render_glosario_interactivo_oed(
        [
            "LEY_546",
            "VIS_VIP",
            "UVR",
            "ENCARGO_FIDUCIARIO",
            "LEASING",
            "CUENTA_AFC",
            "LEY_820",
            "CAP_RATE",
            "VPN_TIR",
            "SMMLV",
            "UVT",
            "FIC",
        ]
    )

    # Guardar en sesión de Streamlit para que el Módulo 5 de Nelson pueda leerlo en Etapa 5
    st.session_state["resultado_mod4_finca_raiz"] = resultado
    return resultado


def _corriendo_dentro_de_streamlit() -> bool:
    """Detecta si el archivo fue invocado mediante `streamlit run`."""
    if "streamlit" not in sys.modules:
        return False
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx  # type: ignore

        return get_script_run_ctx() is not None
    except Exception:
        return False


def _a_float(valor: Any, defecto: float) -> float:
    """Convierte entradas web (incluyendo cadenas vacías) a float seguro sin lanzar excepción."""
    if valor in (None, ""):
        return 0.0 if valor == "" else defecto
    try:
        return float(valor)
    except (TypeError, ValueError):
        return defecto


def _a_int(valor: Any, defecto: int) -> int:
    """Convierte entradas web (incluyendo cadenas vacías) a entero seguro."""
    if valor in (None, ""):
        return 0 if valor == "" else defecto
    try:
        return int(float(valor))
    except (TypeError, ValueError):
        return defecto


def procesar_simulacion_api_local(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Ejecuta el motor de Jesi desde el servidor web local sin requerir librerías externas."""
    cfg = cargar_configuracion()
    ingreso_titular = _a_float(payload.get("ingreso_titular_cop"), 5_915_000.0)
    ingreso_pareja = _a_float(payload.get("ingreso_pareja_cop"), 3_500_000.0)
    resultado = evaluar_inversion_finca_raiz(
        valor_inmueble_cop=_a_float(payload.get("valor_inmueble_cop"), 200_000_000.0),
        ingreso_familiar_neto_cop=ingreso_titular + ingreso_pareja,
        porcentaje_cuota_inicial=_a_float(payload.get("porcentaje_cuota_inicial_pct"), 30.0) / 100.0,
        plazo_entrega_planos_meses=_a_int(payload.get("plazo_planos_meses"), 24),
        cesantias_y_primas_anuales_cop=_a_float(payload.get("cesantias_primas_cop"), 5_500_000.0),
        plazo_credito_anios=_a_int(payload.get("plazo_credito_anios"), 15),
        tasa_ea_pesos=_a_float(payload.get("tasa_ea_pesos_pct"), 11.5) / 100.0,
        tasa_ea_uvr_mas_spread=_a_float(payload.get("tasa_uvr_spread_pct"), 6.5) / 100.0,
        canon_arriendo_mensual_estimado_cop=_a_float(payload.get("canon_estimado_cop"), 1_400_000.0),
        costo_oportunidad_ea=_a_float(payload.get("cok_ea_pct"), 10.5) / 100.0,
        ahorro_previo_afc_cop=_a_float(payload.get("ahorro_previo_afc_cop"), 8_000_000.0),
        aplicar_subsidio_ccf=bool(payload.get("aplicar_subsidio_ccf", True)),
        modalidad_financiacion=str(payload.get("modalidad_financiacion", "HIPOTECARIO")),
        incluir_tablas_detalle=True,
        config=cfg,
        cuotas_otras_deudas_mensuales_cop=_a_float(payload.get("cuotas_otras_deudas_cop"), 0.0),
        fondo_emergencia_completo=bool(payload.get("fondo_emergencia_completo", True)),
        modalidad_laboral_titular=str(payload.get("modalidad_laboral_titular", "Empleado")),
    )
    semaforo = generar_resumen_ejecutivo_ciudadano(resultado)
    semaforo["titulo_html"] = enriquecer_texto_con_explicaciones(semaforo["titulo"])
    semaforo["mensaje_html"] = enriquecer_texto_con_explicaciones(semaforo["mensaje"])
    semaforo["plan_accion_html"] = enriquecer_texto_con_explicaciones(semaforo["plan_accion"])
    semaforo["receta_html"] = semaforo["plan_accion_html"]
    return {
        "resultado": resultado,
        "semaforo": semaforo,
        "alertas_html": [enriquecer_texto_con_explicaciones(a) for a in resultado["alertas_regulatorias"]],
    }


def _construir_html_dashboard_local() -> str:
    """Genera el visualizador web local de Jesi aplicando los 5 bloques del Manual de Marca OED."""
    info_paso = next((p for p in RUTA_CLINICA_FINANCIERA_OED if p["paso"] == 5), RUTA_CLINICA_FINANCIERA_OED[-1])
    pills_html = "".join(
        f'<span class="oed-step-pill {"oed-step-active" if p["paso"] == 5 else ""}">'
        f'Paso {p["paso"]}: {p["icono"]} {html.escape(p["titulo_ciudadano"])}</span>'
        for p in RUTA_CLINICA_FINANCIERA_OED
    )
    saludo_rico = enriquecer_texto_con_explicaciones(info_paso["saludo_medico"])
    glosario_json = json.dumps(GLOSARIO_LENGUAJE_CLARO_OED, ensure_ascii=False)

    return (
        """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Paso 5: Viabilidad para Comprar Vivienda o Invertir en Finca Raíz — Jesi (OED)</title>
"""
        + _CSS_MEDICO_AMIGO_OED
        + """
<style>
  :root { --bg:#F4F7FB; --card:#FFFFFF; --ink:#0F294A; --muted:#475569; --blue:#1D4ED8; --green:#15803D; --amber:#B45309; --red:#B91C1C; --border:#DDE4EE; }
  * { box-sizing:border-box; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }
  body { margin:0; background:var(--bg); color:var(--ink); padding:20px; }
  .wrap { max-width:1260px; margin:0 auto; }
  .grid3 { display:grid; grid-template-columns:repeat(auto-fit,minmax(290px,1fr)); gap:14px; margin-bottom:16px; }
  .grid4 { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; margin-bottom:16px; }
  .grid2 { display:grid; grid-template-columns:repeat(auto-fit,minmax(420px,1fr)); gap:14px; margin-bottom:16px; }
  .card { background:var(--card); border:1px solid var(--border); border-radius:12px; padding:16px; box-shadow:0 2px 6px rgba(15,41,74,0.04); }
  .card h3 { margin:0 0 12px 0; font-size:15px; color:#0F294A; border-bottom:1px solid var(--border); padding-bottom:6px; }
  label { display:block; font-size:12.5px; color:var(--muted); margin:8px 0 3px; font-weight:600; }
  input, select { width:100%; padding:7px 9px; border:1px solid #CBD5E1; border-radius:7px; font-size:13.5px; }
  .chk { display:flex; align-items:center; gap:8px; margin-top:12px; font-size:12.5px; }
  .chk input { width:auto; }
  .btn { background:var(--blue); color:#fff; border:none; padding:10px 16px; border-radius:8px; font-weight:600; cursor:pointer; font-size:13.5px; }
  .btn-sec { background:#15803D; }
  .kpi-title { font-size:12px; color:var(--muted); font-weight:600; }
  .kpi-val { font-size:21px; font-weight:700; margin:4px 0; color:#0F294A; }
  .kpi-sub { font-size:12px; color:var(--blue); }
  table { width:100%; border-collapse:collapse; font-size:12.5px; }
  th, td { padding:7px 8px; border-bottom:1px solid var(--border); text-align:right; }
  th:first-child, td:first-child { text-align:left; }
  th { background:#F8FAFC; color:#334155; }
  svg { width:100%; height:250px; background:#fff; border-radius:8px; }
  details summary { cursor:pointer; font-weight:700; color:#0F294A; font-size:14.5px; }
</style>
</head>
<body>
<div class="wrap">
  <!-- BLOQUE 1: Barra de Pasos (0 al 6) + Encabezado del Asesor Financiero de Confianza -->
  <div class="oed-steps">"""
        + pills_html
        + """</div>
  <div class="oed-header">
    <h1>🏡 Paso 5 — Viabilidad para Comprar Vivienda o Invertir en Finca Raíz</h1>
    <p>💼 <i>\""""
        + saludo_rico
        + """\"</i><br>
    <small>Responsable OED en esta etapa: <b>Jesi</b> · Módulo 4: Inversión Patrimonial en Finca Raíz</small></p>
  </div>

  <!-- BLOQUE 2: Datos de tu Hogar, del Inmueble y del Crédito -->
  <div class="grid3">
    <div class="card">
      <h3>👨‍👩‍👧 1. Hogar, Empleo y Deudas</h3>
      <label>Modalidad laboral titular (Módulo 1)</label>
      <select id="modalidad_laboral_titular" onchange="ajustarModalidadLaboral()">
        <option value="Empleado">Empleado (con primas y cesantías)</option>
        <option value="Independiente">Independiente / Contratista OPS</option>
        <option value="Integral">Salario Integral</option>
      </select>
      <label>Tu ingreso neto mensual (COP)</label>
      <input type="number" id="ingreso_titular_cop" value="5915000" min="0" step="250000">
      <label>Ingreso neto pareja / co-deudor (COP)</label>
      <input type="number" id="ingreso_pareja_cop" value="3500000" min="0" step="250000">
      <label>Cuotas mensuales de otras deudas actuales (COP)</label>
      <input type="number" id="cuotas_otras_deudas_cop" value="0" min="0" step="100000">
      <label>Ahorro previo / Cuenta AFC (COP)</label>
      <input type="number" id="ahorro_previo_afc_cop" value="8000000" min="0" step="1000000">
      <label>Cesantías + Primas anuales (COP)</label>
      <input type="number" id="cesantias_primas_cop" value="5500000" min="0" step="500000">
      <label class="chk"><input type="checkbox" id="fondo_emergencia_completo" checked> Mi fondo de emergencia ya está completo y protegido aparte</label>
      <label class="chk"><input type="checkbox" id="aplicar_subsidio_ccf" checked> Aplicar Subsidio Caja Compensación (si &lt;= 4 SMMLV y VIS)</label>
    </div>

    <div class="card">
      <h3>🏢 2. El Inmueble y Cuota Inicial</h3>
      <label>Valor comercial del inmueble (COP)</label>
      <input type="number" id="valor_inmueble_cop" value="200000000" min="0" step="5000000">
      <label>Modalidad de financiación</label>
      <select id="modalidad_financiacion">
        <option value="HIPOTECARIO">Crédito Hipotecario Tradicional</option>
        <option value="LEASING">Leasing Habitacional</option>
      </select>
      <label>Porcentaje de Cuota Inicial (%): <span id="lbl_ci">30%</span></label>
      <input type="range" id="porcentaje_cuota_inicial_pct" min="0" max="80" value="30" oninput="document.getElementById('lbl_ci').innerText=this.value+'%'; simular();">
      <label>Plazo sobre planos en fiducia (meses): <span id="lbl_pl">24</span></label>
      <input type="range" id="plazo_planos_meses" min="0" max="48" value="24" oninput="document.getElementById('lbl_pl').innerText=this.value; simular();">
    </div>

    <div class="card">
      <h3>🏦 3. Crédito y Renta (Ley 820)</h3>
      <label>Plazo del crédito (años): <span id="lbl_an">15</span></label>
      <input type="range" id="plazo_credito_anios" min="5" max="30" value="15" oninput="document.getElementById('lbl_an').innerText=this.value; simular();">
      <label>Tasa Crédito en Pesos (% EA)</label>
      <input type="number" id="tasa_ea_pesos_pct" value="11.5" min="0" step="0.25">
      <label>Tasa Real UVR + Spread (% EA sin IPC)</label>
      <input type="number" id="tasa_uvr_spread_pct" value="6.5" min="0" step="0.25">
      <label>Canon mensual arriendo estimado (COP)</label>
      <input type="number" id="canon_estimado_cop" value="1400000" min="0" step="100000">
      <label>Rentabilidad alternativa FIC / Portafolio (% EA)</label>
      <input type="number" id="cok_ea_pct" value="10.5" min="0" step="0.25">
    </div>
  </div>

  <div style="margin-bottom:14px; display:flex; gap:10px;">
    <button class="btn" onclick="simular()">🔄 Actualizar Diagnóstico Financiero</button>
    <button class="btn btn-sec" onclick="descargarCSV()">📥 Descargar Tabla Amortización Pesos (CSV Excel)</button>
  </div>

  <!-- BLOQUE 3: Diagnóstico Financiero + Burbujas (?) + Plan de Acción + 4 Indicadores Clave -->
  <div id="semaforo_box"></div>
  <div id="alertas_box"></div>

  <div class="grid4">
    <div class="card"><div class="kpi-title">Clasificación Regulatoria</div><div class="kpi-val" id="k_seg">-</div><div class="kpi-sub" id="k_smmlv">-</div></div>
    <div class="card"><div class="kpi-title">Cuota Inicial Mensual (Planos)</div><div class="kpi-val" id="k_cim">-</div><div class="kpi-sub" id="k_cit">-</div></div>
    <div class="card"><div class="kpi-title">1ra Cuota en Pesos vs. Ley 546</div><div class="kpi-val" id="k_cuota">-</div><div class="kpi-sub" id="k_tope">-</div></div>
    <div class="card"><div class="kpi-title">TIR Inmobiliaria (10 años)</div><div class="kpi-val" id="k_tir">-</div><div class="kpi-sub" id="k_cap">-</div></div>
  </div>

  <!-- BLOQUE 4: Gráficas Interactivas con la Paleta Oficial OED -->
  <div class="grid2">
    <div class="card">
      <h3>⚖️ Evolución de Cuota Mensual: Pesos Fija vs. Abono Capital vs. UVR</h3>
      <svg id="svg_cuotas" viewBox="0 0 540 240"></svg>
      <div style="font-size:12px; color:#475569; margin-top:6px;">
        🔵 Pesos Cuota Fija &nbsp;|&nbsp; 🟢 Abono Constante Capital &nbsp;|&nbsp; 🔴 UVR Indexada IPC &nbsp;|&nbsp; ⚫ Línea Punteada: Tope 30% Ley 546
      </div>
    </div>
    <div class="card">
      <h3>📈 Patrimonio Neto al Año 10: Comprar vs. Arrendar + Invertir en FIC</h3>
      <svg id="svg_patrimonio" viewBox="0 0 540 240"></svg>
      <div id="resumen_renta" style="font-size:12px; color:#475569; margin-top:6px;"></div>
    </div>
  </div>

  <div class="card" style="margin-bottom:16px;">
    <h3>📋 Comparativa de los 3 Sistemas de Amortización Vigilados por la SFC</h3>
    <table id="tabla_sistemas"></table>
  </div>

  <!-- BLOQUE 5: Diccionario Financiero Desplegable (5 Familias de Términos) -->
  <div class="card">
    <details open>
      <summary>📘 ¿Tienes dudas con algún concepto? Consulta aquí el Diccionario Financiero OED (5 Familias)</summary>
      <div style="margin-top:12px;">
        <label>Selecciona el término que quieres consultar sin tecnicismos:</label>
        <select id="glosario_select" onchange="mostrarTerminoGlosario()"></select>
        <div id="glosario_detalle" style="margin-top:10px;"></div>
      </div>
    </details>
  </div>
</div>

<script>
const GLOSARIO_OED = """
        + glosario_json
        + """;
let ultimoResultado = null;
const cop = n => '$' + Math.round(n).toLocaleString('es-CO');

function inicializarGlosario() {
  const sel = document.getElementById('glosario_select');
  const ordenModulo4 = ['LEY_546','VIS_VIP','UVR','ENCARGO_FIDUCIARIO','LEASING','CUENTA_AFC','LEY_820','CAP_RATE','VPN_TIR'];
  const resto = Object.keys(GLOSARIO_OED).filter(k => !ordenModulo4.includes(k));
  const todos = [...ordenModulo4, ...resto].filter(k => GLOSARIO_OED[k]);
  sel.innerHTML = todos.map(k => `<option value="${k}">[${GLOSARIO_OED[k].categoria}] ${GLOSARIO_OED[k].termino_tecnico}</option>`).join('');
  mostrarTerminoGlosario();
}

function mostrarTerminoGlosario() {
  const k = document.getElementById('glosario_select').value;
  const f = GLOSARIO_OED[k];
  if (!f) return;
  document.getElementById('glosario_detalle').innerHTML = `
    <div class="oed-doc-card oed-doc-azul" style="margin-bottom:8px;">
      <b>💡 En palabras sencillas (${f.termino_tecnico}):</b><br>${f.lenguaje_claro}
    </div>
    <div class="oed-rx-box" style="margin:0;">
      <b>🇨🇴 Ejemplo cotidiano en pesos:</b> ${f.ejemplo_cotidiano}
    </div>
  `;
}

function dibujarLineas(svgId, series, topeY) {
  const svg = document.getElementById(svgId);
  const W = 540, H = 240, padL = 72, padR = 18, padT = 18, padB = 30;
  let maxY = topeY || 1;
  series.forEach(s => s.datos.forEach(v => { if (v > maxY) maxY = v; }));
  maxY *= 1.1;
  const n = series[0].datos.length;
  const x = i => padL + (i / Math.max(1, n - 1)) * (W - padL - padR);
  const y = v => padT + (1 - v / maxY) * (H - padT - padB);
  let html = `<line x1="${padL}" y1="${H-padB}" x2="${W-padR}" y2="${H-padB}" stroke="#cbd5e1"/>`;
  for (let g = 0; g <= 4; g++) {
    const val = (maxY * g) / 4;
    const yy = y(val);
    html += `<line x1="${padL}" y1="${yy}" x2="${W-padR}" y2="${yy}" stroke="#f1f5f9"/>`;
    html += `<text x="${padL-6}" y="${yy+4}" font-size="10" fill="#64748b" text-anchor="end">$${(val/1e6).toFixed(1)}M</text>`;
  }
  if (topeY) {
    const yt = y(topeY);
    html += `<line x1="${padL}" y1="${yt}" x2="${W-padR}" y2="${yt}" stroke="#475569" stroke-dasharray="5,4" stroke-width="1.5"/>`;
  }
  series.forEach(s => {
    const pts = s.datos.map((v, i) => `${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(' ');
    html += `<polyline fill="none" stroke="${s.color}" stroke-width="2.5" points="${pts}"/>`;
  });
  svg.innerHTML = html;
}

function dibujarBarras(svgId, etiquetas, valores, colores) {
  const svg = document.getElementById(svgId);
  const W = 540, H = 240, padL = 70, padR = 20, padT = 26, padB = 38;
  const maxY = Math.max(...valores, 1) * 1.15;
  const bw = 95, gap = (W - padL - padR - bw * valores.length) / (valores.length + 1);
  let html = `<line x1="${padL}" y1="${H-padB}" x2="${W-padR}" y2="${H-padB}" stroke="#cbd5e1"/>`;
  valores.forEach((v, i) => {
    const bx = padL + gap * (i + 1) + bw * i;
    const bh = ((v / maxY) * (H - padT - padB));
    const by = H - padB - bh;
    html += `<rect x="${bx}" y="${by}" width="${bw}" height="${bh}" rx="6" fill="${colores[i]}"/>`;
    html += `<text x="${bx + bw/2}" y="${by - 6}" font-size="11" font-weight="700" fill="#0F294A" text-anchor="middle">$${(v/1e6).toFixed(1)}M</text>`;
    html += `<text x="${bx + bw/2}" y="${H - 14}" font-size="11" fill="#334155" text-anchor="middle">${etiquetas[i]}</text>`;
  });
  svg.innerHTML = html;
}

function ajustarModalidadLaboral() {
  const mod = document.getElementById('modalidad_laboral_titular').value;
  const ces = document.getElementById('cesantias_primas_cop');
  if (mod === 'Independiente' || mod === 'Integral') {
    ces.value = '0';
  } else if (ces.value === '0') {
    ces.value = '5500000';
  }
  simular();
}

async function simular() {
  const ids = ['modalidad_laboral_titular','ingreso_titular_cop','ingreso_pareja_cop','cuotas_otras_deudas_cop',
    'ahorro_previo_afc_cop','cesantias_primas_cop','valor_inmueble_cop','modalidad_financiacion',
    'porcentaje_cuota_inicial_pct','plazo_planos_meses','plazo_credito_anios','tasa_ea_pesos_pct',
    'tasa_uvr_spread_pct','canon_estimado_cop','cok_ea_pct'];
  const payload = {};
  ids.forEach(id => payload[id] = document.getElementById(id).value);
  payload.aplicar_subsidio_ccf = document.getElementById('aplicar_subsidio_ccf').checked;
  payload.fondo_emergencia_completo = document.getElementById('fondo_emergencia_completo').checked;

  const resp = await fetch('/api/evaluar', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)});
  const data = await resp.json();
  const r = data.resultado, sem = data.semaforo;
  ultimoResultado = r;

  const mapaEstilos = {
    success: {cls:'oed-doc-verde', ico:'✅ Diagnóstico Financiero favorable:'},
    info:    {cls:'oed-doc-azul',  ico:'ℹ️ Análisis de tu Asesor Financiero:'},
    warning: {cls:'oed-doc-ambar', ico:'⚠️ Revisión preventiva:'},
    error:   {cls:'oed-doc-rojo',  ico:'🛑 Riesgo alto — Te recomendamos esperar:'}
  };
  const est = mapaEstilos[sem.nivel] || mapaEstilos.error;
  document.getElementById('semaforo_box').innerHTML = `
    <div class="oed-doc-card ${est.cls}">
      <b>${est.ico} ${sem.titulo_html || sem.titulo}</b>
      <div style="margin-top:4px;">${sem.mensaje_html || sem.mensaje}</div>
      <div style="margin-top:6px; font-size:12px; opacity:0.85;">💡 <i>Tip: Pasa el cursor sobre cualquier palabra subrayada con <b>?</b> para ver su explicación sencilla.</i></div>
    </div>
    <div class="oed-rx-box"><b>📌 Plan de Acción para este Mes:</b> ${sem.plan_accion_html || sem.receta_html || sem.plan_accion || sem.receta}</div>
  `;
  const alertasHtml = data.alertas_html || r.alertas_regulatorias;
  document.getElementById('alertas_box').innerHTML = alertasHtml.map(a => `<div class="oed-doc-card oed-doc-ambar">⚖️ ${a}</div>`).join('');

  document.getElementById('k_seg').innerText = r.codigo_segmento;
  document.getElementById('k_smmlv').innerText = `${r.valor_inmueble_smmlv} SMMLV`;
  document.getElementById('k_cim').innerText = cop(r.cuota_inicial_mensual_cop);
  document.getElementById('k_cit').innerText = `Inicial total: ${cop(r.cuota_inicial_total_cop)}`;
  document.getElementById('k_cuota').innerText = cop(r.primera_cuota_credito_cop);
  document.getElementById('k_tope').innerText = `Tope 30% Ley 546: ${cop(r.tope_cuota_ley_546_30pct_cop)}`;
  document.getElementById('k_tir').innerText = `${r.tir_inmobiliaria_ea_pct}% EA`;
  document.getElementById('k_cap').innerText = `Cap Rate Neto: ${r.cap_rate_neto_pct}% | VPN: ${cop(r.vpn_inmobiliario_cop)}`;

  const am = r.amortizacion_detalle;
  dibujarLineas('svg_cuotas', [
    {color:'#1D4ED8', datos: am.tabla_pesos_cuota_fija.map(x => x.cuota_total_cop)},
    {color:'#15803D', datos: am.tabla_pesos_abono_constante.map(x => x.cuota_total_cop)},
    {color:'#DC2626', datos: am.tabla_uvr_ciclica.map(x => x.cuota_total_cop)}
  ], r.tope_cuota_ley_546_30pct_cop);

  const c = r.comparativa_estrategias_10a;
  dibujarBarras('svg_patrimonio',
    ['Comprar Pesos', 'Comprar UVR', 'Arrendar + FIC'],
    [c.comprar_pesos_patrimonio_10a_cop, c.comprar_uvr_patrimonio_10a_cop, c.arrendar_e_invertir_fic_patrimonio_10a_cop],
    ['#1D4ED8', '#EA580C', '#7C3AED']
  );
  document.getElementById('resumen_renta').innerText =
    `Canon aplicado (Ley 820 <= 1%): ${cop(r.canon_mensual_aplicado_cop)}/mes | Beneficio AFC est.: ${cop(r.ahorro_tributario_afc_total_cop)}`;

  document.getElementById('tabla_sistemas').innerHTML = `
    <tr><th>Sistema SFC (Ley 546/1999)</th><th>1ra Cuota</th><th>¿Cumple 30%?</th><th>Total Intereses</th><th>Total Pagado</th></tr>
    <tr><td>1. Pesos — Cuota Fija</td><td>${cop(am.primera_cuota_pesos_fija_cop)}</td><td>${r.cumple_ley_546_30pct?'✅ Sí':'❌ No'}</td><td>${cop(am.total_intereses_pesos_fija_cop)}</td><td>${cop(am.total_pagado_pesos_fija_cop)}</td></tr>
    <tr><td>2. Pesos — Abono Constante Capital</td><td>${cop(am.primera_cuota_abono_constante_cop)}</td><td>${am.primera_cuota_abono_constante_cop<=r.tope_cuota_ley_546_30pct_cop?'✅ Sí':'❌ No'}</td><td>${cop(am.total_intereses_abono_constante_cop)}</td><td>${cop(am.total_pagado_abono_constante_cop)}</td></tr>
    <tr><td>3. UVR — Indexado a Inflación IPC</td><td>${cop(am.primera_cuota_uvr_cop)}</td><td>${r.cumple_ley_546_en_uvr?'✅ Sí':'❌ No'}</td><td>${cop(am.total_intereses_uvr_cop)}</td><td>${cop(am.total_pagado_uvr_cop)}</td></tr>
  `;
}

function descargarCSV() {
  if (!ultimoResultado) return;
  const filas = ultimoResultado.amortizacion_detalle.tabla_pesos_cuota_fija;
  const cols = Object.keys(filas[0]);
  const csv = '\\uFEFF' + [cols.join(','), ...filas.map(f => cols.map(k => f[k]).join(','))].join('\\n');
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([csv], {type:'text/csv;charset=utf-8;'}));
  a.download = 'amortizacion_modulo4_jesi.csv';
  a.click();
}

inicializarGlosario();
document.querySelectorAll('input, select:not(#glosario_select)').forEach(el => el.addEventListener('change', simular));
simular();
</script>
</body>
</html>
"""
    )


def iniciar_servidor_web_local_autonomo(puerto: int = 8504, abrir_navegador: bool = True) -> None:
    """
    Levanta una calculadora web interactiva en `http://127.0.0.1:8504` usando únicamente la
    librería estándar de Python, ideal cuando la red corporativa demora la instalación de Streamlit.
    """
    import webbrowser
    from http.server import BaseHTTPRequestHandler, HTTPServer

    cuerpo_html = _construir_html_dashboard_local().encode("utf-8")

    class Mod4Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
            return

        def do_GET(self) -> None:  # noqa: N802
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(cuerpo_html)))
            self.end_headers()
            self.wfile.write(cuerpo_html)

        def do_POST(self) -> None:  # noqa: N802
            longitud = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(longitud).decode("utf-8") if longitud > 0 else "{}"
            respuesta = json.dumps(procesar_simulacion_api_local(json.loads(raw))).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(respuesta)))
            self.end_headers()
            self.wfile.write(respuesta)

    url = f"http://127.0.0.1:{puerto}"
    servidor = HTTPServer(("127.0.0.1", puerto), Mod4Handler)
    print("=" * 72)
    print(f"DASHBOARD WEB MÓDULO 4 (JESI) ACTIVO EN: {url}")
    print("Presiona Ctrl + C en esta terminal cuando quieras detenerlo.")
    print("=" * 72)
    if abrir_navegador:
        webbrowser.open(url)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido correctamente.")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    if _corriendo_dentro_de_streamlit():
        import streamlit as st

        st.set_page_config(
            page_title="Módulo 4: Finca Raíz OED — Jesi",
            page_icon="🏗️",
            layout="wide",
        )
        render_modulo_4_finca_raiz()
    else:
        iniciar_servidor_web_local_autonomo()


