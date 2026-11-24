r"""
Interfaz Gráfica Local (Dashboard Web 100% Local) — Asesor Financiero e Inversiones OED.
Enfoque Principal:
- Fase 0 Transversal: Gobierno de Datos, Cifrado Local y Habeas Data (Ley 1581/2012 y Ley 1266/2008) — Nelson Angel.
- Módulo 5: Viabilidad Actuarial de Decisiones de Vida (Casarse, Hijos 0-23a con Tarifas Reales Colegio Agustiniano Suba,
  Crédito TCO) y Monte Carlo — Nelson Angel.
- Integración con los Módulos 1 (Nidia), 2 (Camilo), 3 (Catalina), 4 (Jesi) y 6 (Salin).

Cómo ejecutar:
1. Dale clic al botón ▶ (Run Python File) arriba a la derecha en VS Code, o
2. Ejecuta en la terminal: .\.venv\Scripts\python.exe app.py
Se abrirá automáticamente en tu navegador local en http://127.0.0.1:8501
"""

from __future__ import annotations

import json
import random
import socket
import sys
import threading
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Tuple

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.data_governance import (
    TEXTO_AUTORIZACION_LEY_1581,
    calcular_permanencia_centrales_riesgo_ley_1266,
    descifrar_payload_local,
    ejercer_derecho_olvido_supresion,
    guardar_perfil_local_seguro,
    registrar_consentimiento_habeas_data,
)
from src.finance import cargar_configuracion, cuota_fija_francesa, ea_a_em
from src.mod1_presupuesto import diagnosticar_presupuesto_y_flujo_caja
from src.mod2_inversiones_salario import estructurar_portafolio_salario
from src.mod3_gestion_deudas import optimizar_portafolio_deudas
from src.mod4_finca_raiz import evaluar_inversion_finca_raiz
from src.mod5_decisiones_vida import evaluar_viabilidad_decision_vida
from src.mod6_educacion_financiera import (
    comparar_azar_vs_inversion_compuesta,
    detectar_esquema_piramidal_ponzi,
    perfilar_inversionista_decreto_2555,
)
from src.oed_design_system import (
    COLORES_GRAFICAS_OED,
    GLOSARIO_LENGUAJE_CLARO_OED,
    PALETA_MARCA_OED,
    RUTA_CLINICA_FINANCIERA_OED,
    enriquecer_texto_con_explicaciones,
    formatear_cop_claro,
)

def _to_float(val: Any, default: float) -> float:
    if val is None or val == "":
        return default
    if isinstance(val, (int, float)):
        return float(val)
    try:
        return float(str(val).replace(",", ".").strip())
    except Exception:
        return default


def _calcular_payload_completo(params: Dict[str, Any]) -> Dict[str, Any]:
    """Ejecuta todos los cálculos actuariales, de Habeas Data e integrados en tiempo real (100% paramétrico, base en cero)."""
    cfg = cargar_configuracion()
    ipc = _to_float(params.get("ipc_anual_pct"), 0.0) / 100.0
    inf_edu = _to_float(params.get("inflacion_educativa_pct"), 0.0) / 100.0
    tasa_descuento = _to_float(params.get("tasa_descuento_pct"), 0.0) / 100.0

    # Copia local de config con tasas parametrizadas por el usuario
    cfg_custom = json.loads(json.dumps(cfg))
    cfg_custom["parametros_macro_colombia"]["ipc_anual_dane"] = ipc
    cfg_custom["parametros_macro_colombia"]["inflacion_educativa_anual"] = inf_edu

    # 1. Parámetros de Flujo de Caja del Hogar (en cero por defecto)
    ingreso_neto_hogar = _to_float(params.get("ingreso_neto_hogar"), 0.0)
    excedente_mensual = _to_float(params.get("excedente_mensual"), 0.0)
    liquidez_emergencia = _to_float(params.get("liquidez_emergencia"), 0.0)

    # Respuestas a las 3 preguntas iniciales (Hijos, Boda, Crédito)
    raw_desea_boda = params.get("desea_boda")
    raw_desea_credito = params.get("desea_credito")

    # 2. Parámetros Boda / Unión Marital (en cero por defecto)
    costo_boda = _to_float(params.get("costo_boda"), 0.0)
    ingreso_pareja = _to_float(params.get("ingreso_pareja"), 0.0)
    plazo_boda_meses = max(0, int(_to_float(params.get("plazo_boda_meses"), 0)))
    ahorro_sinergia_pct = _to_float(params.get("ahorro_sinergia_pct"), 0.0)
    if raw_desea_boda is not None:
        desea_boda = str(raw_desea_boda).lower() in ("true", "1", "si", "sí", "yes")
    else:
        desea_boda = (costo_boda > 0) or (ingreso_pareja > 0)
    if not desea_boda:
        costo_boda = 0.0
        ingreso_pareja = 0.0
        plazo_boda_meses = 0
        ahorro_sinergia_pct = 0.0

    # 3. Parámetros Crédito Estructural + TCO (en cero por defecto)
    monto_credito = _to_float(params.get("monto_credito"), 0.0)
    tasa_ea_credito = _to_float(params.get("tasa_ea_credito"), 0.0) / 100.0
    plazo_credito = max(0, int(_to_float(params.get("plazo_credito"), 0)))
    tasa_tco_mensual_pct = _to_float(params.get("tasa_tco_mensual_pct"), 0.0)
    if raw_desea_credito is not None:
        desea_credito = str(raw_desea_credito).lower() in ("true", "1", "si", "sí", "yes")
    else:
        desea_credito = monto_credito > 0
    if not desea_credito:
        monto_credito = 0.0
        tasa_ea_credito = 0.0
        plazo_credito = 0
        tasa_tco_mensual_pct = 0.0

    # 4. Parámetros Educativos Dinámicos para N Hijos (0, 1, 2, 3, 4 o más)
    nivel_hijo = str(params.get("nivel_costo_hijo", "Agustiniano_Suba"))
    numero_hijos_input = max(0, min(10, int(_to_float(params.get("numero_hijos"), 0))))
    modo_horizonte = str(params.get("modo_horizonte", "ciclo_completo"))
    grado_h1 = str(params.get("grado_agustiniano_h1", "personalizado"))
    mapa_etiquetas_grado = {
        "personalizado": "Paramétrico",
        "personalizado_cero": "Paramétrico",
        "jardin": "Jardín / Preescolar",
        "primaria": "Primaria",
        "bachillerato": "Bachillerato",
        "universidad": "Universidad",
        "jardin_2026": "Jardín",
        "transicion_1_2026": "Transición / 1°",
        "primaria_2_3_2026": "Primaria 2°-3°",
        "cuarto_sexto_2026": "Grados 4°-6°",
        "septimo_noveno_2026": "Bachillerato 7°-9°",
        "decimo_2026": "Bachillerato 10°",
        "once_2026": "Bachillerato 11°",
        "historico_base": "Tarifa Base",
    }

    if nivel_hijo == "Bajo":
        escala_perfil_edu = 0.65
    elif nivel_hijo == "Medio":
        escala_perfil_edu = 0.80
    elif nivel_hijo == "Alto":
        escala_perfil_edu = 1.35
    else:
        escala_perfil_edu = 1.0

    # Compatibilidad con parámetros planos Hijo 1 e Hijo 2 y soporte de lista N hijos (`hijos_lista`)
    edad_hijo1 = max(0, min(30, int(_to_float(params.get("edad_hijo1"), 0))))
    etapa_hijo1 = str(params.get("etapa_hijo1", "bachillerato"))
    anios_colegio_h1_input = max(0, int(_to_float(params.get("anios_colegio_h1"), 0)))
    pension_colegio_mes = _to_float(params.get("pension_colegio_mes"), 0.0) * escala_perfil_edu
    matricula_anual = _to_float(params.get("matricula_anual"), 0.0) * escala_perfil_edu
    transporte_mes = _to_float(params.get("transporte_mes"), 0.0)
    manutencion_hijo_mes = _to_float(params.get("manutencion_hijo_mes"), 0.0)
    otros_gastos_mes = _to_float(params.get("otros_gastos_mes"), 0.0)
    semestre_univ_hoy = _to_float(params.get("semestre_univ_hoy"), 0.0) * escala_perfil_edu
    semestres_univ_h1_input = max(0, int(_to_float(params.get("semestres_univ_h1"), 0)))
    semestre_actual_h1 = max(0, min(14, int(_to_float(params.get("semestre_actual_h1"), 0))))

    edad_hijo2 = max(0, min(30, int(_to_float(params.get("edad_hijo2"), 0))))
    etapa_hijo2 = str(params.get("etapa_hijo2", "universidad"))
    anios_colegio_h2_input = max(0, int(_to_float(params.get("anios_colegio_h2"), 0)))
    semestre_actual_h2 = max(0, min(14, int(_to_float(params.get("semestre_actual_h2"), 0))))
    semestres_cursar_h2_input = max(0, int(_to_float(params.get("semestres_cursar_h2"), 0)))
    semestre_univ_h2 = _to_float(params.get("semestre_univ_h2"), 0.0) * escala_perfil_edu
    pension_hijo2_mes = _to_float(params.get("pension_hijo2_mes"), 0.0) * escala_perfil_edu
    matricula_hijo2_anual = _to_float(params.get("matricula_hijo2_anual"), 0.0) * escala_perfil_edu
    ruta_hijo2_mes = _to_float(params.get("ruta_hijo2_mes"), 0.0)
    manutencion_hijo2_mes = _to_float(params.get("manutencion_hijo2_mes"), 0.0)
    otros_gastos_hijo2_mes = _to_float(params.get("otros_gastos_hijo2_mes"), 0.0)

    hijos_lista_raw = params.get("hijos_lista")
    if isinstance(hijos_lista_raw, list):
        hijos_config_list = hijos_lista_raw[:numero_hijos_input] if "numero_hijos" in params else hijos_lista_raw
    else:
        # Construir desde parámetros planos (Hijo 1, Hijo 2, Hijo 3, Hijo 4...)
        tiene_flat_h1 = any(
            v > 0
            for v in (
                pension_colegio_mes,
                matricula_anual,
                transporte_mes,
                manutencion_hijo_mes,
                otros_gastos_mes,
                semestre_univ_hoy,
            )
        )
        tiene_flat_h2 = any(
            v > 0
            for v in (
                semestre_univ_h2,
                pension_hijo2_mes,
                matricula_hijo2_anual,
                ruta_hijo2_mes,
                manutencion_hijo2_mes,
                otros_gastos_hijo2_mes,
            )
        )
        n_efectivo = numero_hijos_input if numero_hijos_input > 0 else ((1 if tiene_flat_h1 else 0) + (1 if tiene_flat_h2 else 0))
        hijos_config_list = []
        if n_efectivo >= 1:
            hijos_config_list.append(
                {
                    "edad": edad_hijo1,
                    "etapa": etapa_hijo1 if "etapa_hijo1" in params else ("universidad" if str(grado_h1).startswith("univ") else "bachillerato"),
                    "plantilla": grado_h1,
                    "anios_colegio": anios_colegio_h1_input,
                    "pension_mes": _to_float(params.get("pension_colegio_mes"), 0.0),
                    "matricula_anual": _to_float(params.get("matricula_anual"), 0.0),
                    "ruta_mes": transporte_mes,
                    "manutencion_mes": manutencion_hijo_mes,
                    "otros_gastos_mes": otros_gastos_mes,
                    "semestre_univ": _to_float(params.get("semestre_univ_hoy"), 0.0),
                    "semestres_univ": semestres_univ_h1_input,
                    "semestre_actual": semestre_actual_h1,
                    "semestres_cursar": semestres_univ_h1_input,
                }
            )
        if n_efectivo >= 2:
            hijos_config_list.append(
                {
                    "edad": edad_hijo2,
                    "etapa": etapa_hijo2,
                    "plantilla": etapa_hijo2,
                    "anios_colegio": anios_colegio_h2_input,
                    "pension_mes": _to_float(params.get("pension_hijo2_mes"), 0.0),
                    "matricula_anual": _to_float(params.get("matricula_hijo2_anual"), 0.0),
                    "ruta_mes": ruta_hijo2_mes,
                    "manutencion_mes": manutencion_hijo2_mes,
                    "otros_gastos_mes": otros_gastos_hijo2_mes,
                    "semestre_univ": _to_float(params.get("semestre_univ_h2"), 0.0),
                    "semestres_univ": semestres_cursar_h2_input,
                    "semestre_actual": semestre_actual_h2,
                    "semestres_cursar": semestres_cursar_h2_input,
                }
            )
        for idx_extra in range(3, n_efectivo + 1):
            hijos_config_list.append(
                {
                    "edad": max(0, min(30, int(_to_float(params.get(f"edad_hijo{idx_extra}"), 0)))),
                    "etapa": str(params.get(f"etapa_hijo{idx_extra}", "bachillerato")),
                    "plantilla": str(params.get(f"plantilla_hijo{idx_extra}", "personalizado")),
                    "anios_colegio": max(0, int(_to_float(params.get(f"anios_colegio_h{idx_extra}"), 0))),
                    "pension_mes": _to_float(params.get(f"pension_hijo{idx_extra}_mes"), 0.0),
                    "matricula_anual": _to_float(params.get(f"matricula_hijo{idx_extra}_anual"), 0.0),
                    "ruta_mes": _to_float(params.get(f"ruta_hijo{idx_extra}_mes"), 0.0),
                    "manutencion_mes": _to_float(params.get(f"manutencion_hijo{idx_extra}_mes"), 0.0),
                    "otros_gastos_mes": _to_float(params.get(f"otros_gastos_hijo{idx_extra}_mes"), 0.0),
                    "semestre_univ": _to_float(params.get(f"semestre_univ_h{idx_extra}"), 0.0),
                    "semestres_univ": max(0, int(_to_float(params.get(f"semestres_cursar_h{idx_extra}"), 0))),
                    "semestre_actual": max(0, int(_to_float(params.get(f"semestre_actual_h{idx_extra}"), 0))),
                    "semestres_cursar": max(0, int(_to_float(params.get(f"semestres_cursar_h{idx_extra}"), 0))),
                }
            )

    numero_hijos = len(hijos_config_list)
    if numero_hijos > 0:
        edad_actual_hijo = max(0, min(22, int(round(sum(min(22, _to_float(h.get("edad"), 0)) for h in hijos_config_list) / numero_hijos))))
        edad_inicio_curva = 0 if modo_horizonte == "ciclo_completo" else min(int(_to_float(h.get("edad"), 0)) for h in hijos_config_list)
    else:
        edad_actual_hijo = 0
        edad_inicio_curva = 0

    # 1. Gobierno de Datos y Habeas Data (Nelson)
    usuario_id = str(params.get("usuario_id", "CC_1020304050_NELSON"))
    acepta_habeas = bool(params.get("acepta_habeas", True))
    meses_mora = max(0, int(_to_float(params.get("meses_mora"), 0)))
    obligacion_pagada = bool(params.get("obligacion_pagada", True))
    accion_disco = str(params.get("accion_disco", "ninguna"))

    consentimiento = registrar_consentimiento_habeas_data(
        usuario_id=usuario_id,
        acepta_tratamiento=acepta_habeas,
    )
    permanencia = calcular_permanencia_centrales_riesgo_ley_1266(
        meses_en_mora=meses_mora,
        obligacion_pagada=obligacion_pagada,
    )

    curva_habeas = []
    for m in range(0, 37, 2):
        r = calcular_permanencia_centrales_riesgo_ley_1266(meses_en_mora=m, obligacion_pagada=obligacion_pagada)
        curva_habeas.append({"mora": m, "permanencia": r["meses_permanencia_post_pago"]})

    ruta_archivo_cifrado = ROOT_DIR / "data" / "processed" / "perfil_gui_nelson.oed"
    estado_disco_msg = "Listo para operar en disco local."
    token_muestra = ""

    if accion_disco == "guardar":
        try:
            res_g = guardar_perfil_local_seguro(
                perfil_datos={
                    "usuario_id": usuario_id,
                    "ingreso_neto_hogar_mensual_cop": ingreso_neto_hogar,
                    "excedente_mensual_actual_cop": excedente_mensual,
                },
                consentimiento=consentimiento,
                ruta_destino=ruta_archivo_cifrado,
            )
            token_raw = ruta_archivo_cifrado.read_text(encoding="utf-8")
            token_muestra = token_raw[:100] + "..."
            rec = descifrar_payload_local(token_raw)
            estado_disco_msg = (
                f"Guardado y cifrado exitoso en {res_g['ruta_archivo']}. "
                f"ID seudonimizado verificado: {rec['perfil']['usuario_id']}"
            )
        except Exception as exc:
            estado_disco_msg = str(exc)
    elif accion_disco == "olvido":
        res_o = ejercer_derecho_olvido_supresion(ruta_archivo=ruta_archivo_cifrado)
        estado_disco_msg = res_o["mensaje"]

    def _calcular_curva_ciclo_hijo(
        costos_etapa: Dict[str, float],
        edad_fin_ciclo: int = 22,
        factor_edad_actual: float = 1.0,
        edad_ref_hijo: int = 0,
    ) -> Dict[str, Any]:
        """Calcula el Valor Presente Actuarial (VPA) del ciclo educativo completo de un hijo (0 hasta edad_fin_ciclo)."""
        prob_sup = 1.0
        vpa_acum = 0.0
        vpa_colegio = 0.0
        vpa_univ = 0.0
        vf_univ_a_18 = 0.0
        edades = []
        flujo_nominal = []
        vp_anual = []
        vpa_acum_lista = []
        for edad in range(0, edad_fin_ciclo + 1):
            prob_sup *= 0.9985
            if edad <= 4:
                c_mes = costos_etapa["infancia"]
                inf_ap = ipc
            elif edad <= 17:
                c_mes = costos_etapa["colegio"]
                inf_ap = inf_edu
            else:
                c_mes = costos_etapa["univ"] * factor_edad_actual
                inf_ap = inf_edu
            f_hoy = c_mes * 12.0
            f_fut = f_hoy * ((1.0 + inf_ap) ** edad)
            vp = (f_fut / ((1.0 + tasa_descuento) ** edad)) * prob_sup
            vpa_acum += vp
            if edad <= 17:
                vpa_colegio += vp
            else:
                vpa_univ += vp
                vf_univ_a_18 += f_fut / ((1.0 + tasa_descuento) ** max(0, edad - 18))
            edades.append(edad)
            flujo_nominal.append(round(f_fut / 1e6, 2))
            vp_anual.append(round(vp / 1e6, 2))
            vpa_acum_lista.append(round(vpa_acum / 1e6, 2))

        meses_univ = max(12, (18 - min(17, edad_ref_hijo)) * 12)
        tasa_em_f = ea_a_em(tasa_descuento)
        if abs(tasa_em_f) < 1e-9:
            ahorro_mes_u = vf_univ_a_18 / max(1, meses_univ)
        else:
            ahorro_mes_u = (vf_univ_a_18 * tasa_em_f) / (((1.0 + tasa_em_f) ** meses_univ) - 1.0)
        if len(edades) < 24:
            edades = list(range(0, 24))
            flujo_nominal.append(0.0)
            vpa_acum_lista.append(vpa_acum_lista[-1] if vpa_acum_lista else 0.0)
        return {
            "edades": edades,
            "flujo_nominal_m": flujo_nominal,
            "vp_anual_m": vp_anual,
            "vpa_acum_m": vpa_acum_lista,
            "vpa_total_cop": round(vpa_acum, 2),
            "vpa_colegio_cop": round(vpa_colegio, 2),
            "vpa_univ_cop": round(vpa_univ, 2),
            "ahorro_mensual_univ_cop": round(ahorro_mes_u, 2),
        }

    horizonte_max_anios = 6
    for h_cfg in hijos_config_list:
        et_raw = str(h_cfg.get("etapa", "bachillerato")).lower()
        es_u = et_raw.startswith("univ") or et_raw == "universidad"
        ed_h = max(0, min(30, int(_to_float(h_cfg.get("edad"), 0))))
        if es_u:
            s_cur = max(0, int(_to_float(h_cfg.get("semestres_cursar"), h_cfg.get("semestres_univ", 0))))
            s_act = max(0, int(_to_float(h_cfg.get("semestre_actual"), 0)))
            s_rest = s_cur if s_cur > 0 else (max(1, 10 - s_act + 1) if s_act > 0 else 10)
            horizonte_max_anios = max(horizonte_max_anios, int((s_rest + 1) // 2) + 2)
        else:
            a_col = max(0, int(_to_float(h_cfg.get("anios_colegio"), 0)))
            if a_col == 0:
                a_col = max(1, 17 - min(16, ed_h)) if ed_h <= 17 else 0
            s_u = max(0, int(_to_float(h_cfg.get("semestres_univ"), h_cfg.get("semestres_cursar", 0))))
            a_u = max(1, int((s_u + 1) // 2)) if s_u > 0 else 5
            horizonte_max_anios = max(horizonte_max_anios, a_col + a_u)

    def _crear_hijo_vacio(idx_num: int) -> Dict[str, Any]:
        return {
            "indice": idx_num,
            "edad": 0,
            "etapa_educativa": "bachillerato",
            "etiqueta_grado": "Sin Datos ($0)",
            "en_universidad": False,
            "anios_colegio_rest": 0,
            "anios_univ_rest": 0,
            "semestre_actual": 0,
            "semestres_restantes": 0,
            "valor_semestre_univ_cop": 0.0,
            "matricula_univ_mensualizada_cop": 0.0,
            "matricula_univ_anual_cop": 0.0,
            "pension_mes_cop": 0.0,
            "matricula_anual_cop": 0.0,
            "matricula_prorrateada_mes_cop": 0.0,
            "ruta_mes_cop": 0.0,
            "manutencion_y_otros_mes_cop": 0.0,
            "gasto_mes_directo_cop": 0.0,
            "impacto_mes_anualizado_cop": 0.0,
            "flujo_anual_hoy_cop": 0.0,
            "vpa_ciclo_completo_cop": 0.0,
            "vpa_restante_edad_actual_cop": 0.0,
            "vpa_saldo_neto_cop": 0.0,
            "vpa_etapa_univ_cop": 0.0,
            "vpa_colegio_restante_cop": 0.0,
            "vpa_univ_proyectada_cop": 0.0,
            "ahorro_mensual_univ_cop": 0.0,
        }

    def _evaluar_hijo_individual(idx_num: int, h_cfg: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, float]]:
        ed_h = max(0, min(30, int(_to_float(h_cfg.get("edad"), 0))))
        etapa_raw = str(h_cfg.get("etapa", "bachillerato")).lower()
        plantilla_raw = str(h_cfg.get("plantilla", etapa_raw))
        en_univ = etapa_raw.startswith("univ") or etapa_raw == "universidad"

        if en_univ:
            etapa_norm = "universidad"
        elif "jardin" in etapa_raw or "preescolar" in etapa_raw or "transicion" in etapa_raw:
            etapa_norm = "jardin"
        elif "primaria" in etapa_raw or "cuarto" in etapa_raw:
            etapa_norm = "primaria"
        else:
            etapa_norm = "bachillerato"

        etiqueta_etapa = mapa_etiquetas_grado.get(
            plantilla_raw,
            {
                "jardin": "Jardín / Preescolar",
                "primaria": "Primaria",
                "bachillerato": "Bachillerato",
                "universidad": "Universidad",
            }.get(etapa_norm, "Paramétrico"),
        )

        pens_mes = _to_float(h_cfg.get("pension_mes", h_cfg.get("pension_colegio")), 0.0) * escala_perfil_edu
        matr_anual = _to_float(h_cfg.get("matricula_anual", h_cfg.get("matricula_colegio_anual")), 0.0) * escala_perfil_edu
        ruta_m = _to_float(h_cfg.get("ruta_mes", h_cfg.get("ruta_escolar")), 0.0)
        manut_m = _to_float(h_cfg.get("manutencion_mes", h_cfg.get("manutencion_hijo_mes")), manutencion_hijo_mes)
        otros_m = _to_float(h_cfg.get("otros_gastos_mes"), 0.0)
        sem_univ_val = _to_float(h_cfg.get("semestre_univ", h_cfg.get("semestre_universidad")), 0.0) * escala_perfil_edu
        anios_col_in = max(0, int(_to_float(h_cfg.get("anios_colegio"), 0)))
        sem_act_in = max(0, min(14, int(_to_float(h_cfg.get("semestre_actual"), 0))))
        sem_cur_in = max(0, int(_to_float(h_cfg.get("semestres_cursar", h_cfg.get("semestres_univ", h_cfg.get("semestres_totales"))), 0)))

        tiene_datos = any(v > 0 for v in (pens_mes, matr_anual, ruta_m, manut_m, otros_m, sem_univ_val))
        eje_anios = [f"Año {i + 1} ({ed_h + i}a)" for i in range(horizonte_max_anios)]

        if not tiene_datos:
            h_vacio = _crear_hijo_vacio(idx_num)
            h_vacio["edad"] = ed_h
            h_vacio["etapa_educativa"] = etapa_norm
            h_vacio["etiqueta_grado"] = etiqueta_etapa
            h_vacio["en_universidad"] = en_univ
            curva_cero_c = {
                "edades": list(range(0, 24)),
                "flujo_nominal_m": [0.0] * 24,
                "vpa_acum_m": [0.0] * 24,
                "vpa_total_cop": 0.0,
                "vpa_colegio_cop": 0.0,
                "vpa_univ_cop": 0.0,
                "ahorro_mensual_univ_cop": 0.0,
            }
            curva_cero_r = {
                "edades": eje_anios,
                "flujo_nominal_m": [0.0] * horizonte_max_anios,
                "vpa_acum_m": [0.0] * horizonte_max_anios,
                "vpa_total_cop": 0.0,
                "vpa_saldo_neto_cop": 0.0,
                "vpa_etapa_univ_cop": 0.0,
                "vpa_colegio_cop": 0.0,
                "vpa_univ_cop": 0.0,
                "ahorro_mensual_univ_cop": 0.0,
            }
            return h_vacio, curva_cero_c, curva_cero_r, {"infancia": 0.0, "colegio": 0.0, "univ": 0.0}

        if en_univ:
            sem_rest = sem_cur_in if sem_cur_in > 0 else (max(1, 10 - sem_act_in + 1) if sem_act_in > 0 else (10 if sem_univ_val > 0 else 0))
            matr_u_anual = sem_univ_val * 2.0
            matr_u_mes = matr_u_anual / 12.0
            flujo_anual = matr_u_anual + ((ruta_m + manut_m + otros_m) * 12.0)
            gasto_mes_dir = matr_u_mes + ruta_m + manut_m + otros_m
            costo_mes_eq = flujo_anual / 12.0
            flujo_col_ref = (
                (pens_mes + ruta_m) * 10.0 + matr_anual + ((manut_m + otros_m) * 12.0)
                if (pens_mes > 0 or matr_anual > 0)
                else ((manut_m + otros_m + ruta_m) * 12.0)
            )
            costos_et = {
                "infancia": manut_m + otros_m,
                "colegio": flujo_col_ref / 12.0,
                "univ": costo_mes_eq,
            }
            factor_sem = 1.0 + (max(0, sem_act_in - 1) * 0.015) + max(0, ed_h - 18) * 0.02
            curva_comp = _calcular_curva_ciclo_hijo(costos_et, edad_fin_ciclo=23, factor_edad_actual=factor_sem, edad_ref_hijo=ed_h)

            flujo_sem_hoy = sem_univ_val + ((ruta_m + manut_m + otros_m) * 6.0)
            inf_sem = ((1.0 + inf_edu) ** 0.5) - 1.0
            desc_sem = ((1.0 + tasa_descuento) ** 0.5) - 1.0
            sem_cursados = max(0, sem_act_in - 1)
            vpa_sem_cursados = sem_cursados * flujo_sem_hoy
            sem_posgrado = max(4, (23 - min(21, ed_h)) * 2) if sem_act_in > 0 else 0
            tot_sem_proy = sem_rest + sem_posgrado
            prob_s = 1.0
            vpa_preg_falt = 0.0
            vpa_posg = 0.0
            vpa_acum_u = vpa_sem_cursados
            flujo_nom_r = []
            vpa_acum_r = []
            cap_col_prev = curva_comp["vpa_colegio_cop"]
            for anio_idx in range(horizonte_max_anios):
                f_anio = 0.0
                for sem_off in (0, 1):
                    s_idx = anio_idx * 2 + sem_off
                    if s_idx < sem_rest:
                        prob_s *= 0.99925
                        f_sf = flujo_sem_hoy * ((1.0 + inf_sem) ** s_idx)
                        vp_s = (f_sf / ((1.0 + desc_sem) ** s_idx)) * prob_s
                        f_anio += f_sf
                        vpa_preg_falt += vp_s
                        vpa_acum_u += vp_s
                    elif s_idx < tot_sem_proy:
                        prob_s *= 0.99925
                        f_sf = (flujo_sem_hoy * 1.08) * ((1.0 + inf_sem) ** s_idx)
                        vp_s = (f_sf / ((1.0 + desc_sem) ** s_idx)) * prob_s
                        f_anio += f_sf
                        vpa_posg += vp_s
                        vpa_acum_u += vp_s
                flujo_nom_r.append(round(f_anio / 1e6, 2))
                vpa_acum_r.append(round((cap_col_prev + vpa_acum_u) / 1e6, 2))

            vpa_rest_total = round(cap_col_prev + vpa_acum_u, 2)
            vpa_saldo_neto = round(vpa_preg_falt + vpa_posg, 2)
            curva_rest = {
                "edades": eje_anios,
                "flujo_nominal_m": flujo_nom_r,
                "vpa_acum_m": vpa_acum_r,
                "vpa_total_cop": vpa_rest_total,
                "vpa_saldo_neto_cop": vpa_saldo_neto,
                "vpa_etapa_univ_cop": round(vpa_acum_u, 2),
                "vpa_colegio_cop": round(vpa_sem_cursados, 2),
                "vpa_univ_cop": vpa_saldo_neto,
                "ahorro_mensual_univ_cop": round(costo_mes_eq, 2),
            }
            h_res = {
                "indice": idx_num,
                "edad": ed_h,
                "etapa_educativa": etapa_norm,
                "etiqueta_grado": f"{sem_act_in}° Sem. Universidad" if sem_act_in > 0 else "Universidad",
                "en_universidad": True,
                "anios_colegio_rest": 0,
                "anios_univ_rest": int((sem_rest + 1) // 2),
                "semestre_actual": sem_act_in,
                "semestres_restantes": sem_rest,
                "valor_semestre_univ_cop": round(sem_univ_val, 2),
                "matricula_univ_mensualizada_cop": round(matr_u_mes, 2),
                "matricula_univ_anual_cop": round(matr_u_anual, 2),
                "pension_mes_cop": round(pens_mes, 2),
                "matricula_anual_cop": round(matr_anual, 2),
                "matricula_prorrateada_mes_cop": round(matr_anual / 12.0, 2),
                "ruta_mes_cop": round(ruta_m, 2),
                "manutencion_y_otros_mes_cop": round(manut_m + otros_m, 2),
                "gasto_mes_directo_cop": round(gasto_mes_dir, 2),
                "impacto_mes_anualizado_cop": round(costo_mes_eq, 2),
                "flujo_anual_hoy_cop": round(flujo_anual, 2),
                "vpa_ciclo_completo_cop": curva_comp["vpa_total_cop"],
                "vpa_restante_edad_actual_cop": vpa_rest_total,
                "vpa_saldo_neto_cop": vpa_saldo_neto,
                "vpa_etapa_univ_cop": round(vpa_acum_u, 2),
                "vpa_colegio_restante_cop": round(vpa_sem_cursados, 2),
                "vpa_univ_proyectada_cop": vpa_saldo_neto,
                "ahorro_mensual_univ_cop": round(costo_mes_eq, 2),
            }
            return h_res, curva_comp, curva_rest, costos_et
        else:
            # Etapa Jardín, Primaria o Bachillerato
            if anios_col_in > 0:
                anios_col_rest = anios_col_in
            elif pens_mes > 0 or matr_anual > 0:
                anios_col_rest = max(1, 17 - min(16, ed_h)) if ed_h <= 17 else 0
            else:
                anios_col_rest = 0

            if sem_cur_in > 0:
                anios_u_rest = max(1, int((sem_cur_in + 1) // 2))
            elif sem_univ_val > 0:
                anios_u_rest = 5
            else:
                anios_u_rest = 0

            flujo_anual = (pens_mes + ruta_m) * 10.0 + matr_anual + ((manut_m + otros_m) * 12.0)
            gasto_mes_dir = pens_mes + ruta_m + (matr_anual / 12.0) + manut_m + otros_m
            costo_mes_eq = flujo_anual / 12.0
            costos_et = {
                "infancia": manut_m + otros_m,
                "colegio": costo_mes_eq,
                "univ": ((sem_univ_val * 2.0) / 12.0) + manut_m + otros_m,
            }
            factor_ed = 1.0 + max(0, 16 - ed_h) * 0.012
            curva_comp = _calcular_curva_ciclo_hijo(costos_et, edad_fin_ciclo=22, factor_edad_actual=factor_ed, edad_ref_hijo=ed_h)

            cap_col_cursado = curva_comp["vpa_colegio_cop"] * (min(16, ed_h) / 17.0)
            prob_s = 1.0
            vpa_acum_r_val = 0.0
            vpa_col_r_val = 0.0
            vpa_univ_r_val = 0.0
            vf_u_val = 0.0
            flujo_nom_r = []
            vpa_acum_r = []
            for anio_idx in range(horizonte_max_anios):
                if anio_idx < anios_col_rest:
                    prob_s *= 0.9985
                    f_hoy = costos_et["colegio"] * 12.0
                    f_fut = f_hoy * ((1.0 + inf_edu) ** anio_idx)
                    vp_i = (f_fut / ((1.0 + tasa_descuento) ** anio_idx)) * prob_s
                    vpa_col_r_val += vp_i
                    vpa_acum_r_val += vp_i
                elif anio_idx < (anios_col_rest + anios_u_rest):
                    prob_s *= 0.9985
                    f_hoy = costos_et["univ"] * 12.0
                    f_fut = f_hoy * ((1.0 + inf_edu) ** anio_idx)
                    vp_i = (f_fut / ((1.0 + tasa_descuento) ** anio_idx)) * prob_s
                    vpa_univ_r_val += vp_i
                    vpa_acum_r_val += vp_i
                    vf_u_val += f_fut / ((1.0 + tasa_descuento) ** max(0, anio_idx - anios_col_rest))
                else:
                    f_fut = 0.0
                flujo_nom_r.append(round(f_fut / 1e6, 2))
                vpa_acum_r.append(round((cap_col_cursado + vpa_acum_r_val) / 1e6, 2))

            meses_para_u = max(12, anios_col_rest * 12)
            tasa_em_f = ea_a_em(tasa_descuento)
            if abs(tasa_em_f) < 1e-9:
                ahorro_u_mes = vf_u_val / max(1, meses_para_u)
            else:
                ahorro_u_mes = (vf_u_val * tasa_em_f) / (((1.0 + tasa_em_f) ** meses_para_u) - 1.0)

            vpa_saldo_neto = round(vpa_acum_r_val, 2)
            vpa_cap_total = round(cap_col_cursado + vpa_acum_r_val, 2)
            curva_rest = {
                "edades": eje_anios,
                "flujo_nominal_m": flujo_nom_r,
                "vpa_acum_m": vpa_acum_r,
                "vpa_total_cop": vpa_cap_total,
                "vpa_saldo_neto_cop": vpa_saldo_neto,
                "vpa_etapa_univ_cop": vpa_saldo_neto,
                "vpa_colegio_cop": round(vpa_col_r_val, 2),
                "vpa_univ_cop": round(vpa_univ_r_val, 2),
                "ahorro_mensual_univ_cop": round(ahorro_u_mes, 2),
            }
            h_res = {
                "indice": idx_num,
                "edad": ed_h,
                "etapa_educativa": etapa_norm,
                "etiqueta_grado": etiqueta_etapa,
                "en_universidad": False,
                "anios_colegio_rest": anios_col_rest,
                "anios_univ_rest": anios_u_rest,
                "semestre_actual": 0,
                "semestres_restantes": anios_u_rest * 2,
                "valor_semestre_univ_cop": round(sem_univ_val, 2),
                "matricula_univ_mensualizada_cop": round((sem_univ_val * 2.0) / 12.0, 2),
                "matricula_univ_anual_cop": round(sem_univ_val * 2.0, 2),
                "pension_mes_cop": round(pens_mes, 2),
                "matricula_anual_cop": round(matr_anual, 2),
                "matricula_prorrateada_mes_cop": round(matr_anual / 12.0, 2),
                "ruta_mes_cop": round(ruta_m, 2),
                "manutencion_y_otros_mes_cop": round(manut_m + otros_m, 2),
                "gasto_mes_directo_cop": round(gasto_mes_dir, 2),
                "impacto_mes_anualizado_cop": round(costo_mes_eq, 2),
                "flujo_anual_hoy_cop": round(flujo_anual, 2),
                "vpa_ciclo_completo_cop": curva_comp["vpa_total_cop"],
                "vpa_restante_edad_actual_cop": vpa_cap_total,
                "vpa_saldo_neto_cop": vpa_saldo_neto,
                "vpa_etapa_univ_cop": vpa_saldo_neto,
                "vpa_colegio_restante_cop": round(vpa_col_r_val, 2),
                "vpa_univ_proyectada_cop": round(vpa_univ_r_val, 2),
                "ahorro_mensual_univ_cop": round(ahorro_u_mes, 2),
            }
            return h_res, curva_comp, curva_rest, costos_et

    hijos_detalle: list[Dict[str, Any]] = []
    curvas_completo_por_hijo: list[Dict[str, Any]] = []
    curvas_restante_por_hijo: list[Dict[str, Any]] = []
    costos_etapa_totales = {"infancia": 0.0, "colegio": 0.0, "univ": 0.0}

    for i_h, cfg_h in enumerate(hijos_config_list, start=1):
        h_det, c_comp, c_rest, c_et = _evaluar_hijo_individual(i_h, cfg_h)
        hijos_detalle.append(h_det)
        curvas_completo_por_hijo.append(c_comp)
        curvas_restante_por_hijo.append(c_rest)
        costos_etapa_totales["infancia"] += c_et["infancia"]
        costos_etapa_totales["colegio"] += c_et["colegio"]
        costos_etapa_totales["univ"] += c_et["univ"]

    hijo1_dict = hijos_detalle[0] if len(hijos_detalle) >= 1 else _crear_hijo_vacio(1)
    hijo2_dict = hijos_detalle[1] if len(hijos_detalle) >= 2 else _crear_hijo_vacio(2)
    curva_h1_completo, curva_h1_restante = (
        (curvas_completo_por_hijo[0], curvas_restante_por_hijo[0])
        if len(hijos_detalle) >= 1
        else (_evaluar_hijo_individual(1, {})[1], _evaluar_hijo_individual(1, {})[2])
    )
    curva_h2_completo, curva_h2_restante = (
        (curvas_completo_por_hijo[1], curvas_restante_por_hijo[1])
        if len(hijos_detalle) >= 2
        else (_evaluar_hijo_individual(2, {})[1], _evaluar_hijo_individual(2, {})[2])
    )

    tiene_algun_dato_hijos = any(h["gasto_mes_directo_cop"] > 0 or h["vpa_ciclo_completo_cop"] > 0 for h in hijos_detalle)
    n_ref = numero_hijos if tiene_algun_dato_hijos else 0

    flujo_anual_agustiniano_total = sum(h["flujo_anual_hoy_cop"] for h in hijos_detalle)
    pago_mes_directo_total = sum(h["gasto_mes_directo_cop"] for h in hijos_detalle)
    costo_mes_equiv_agustiniano_total = sum(h["impacto_mes_anualizado_cop"] for h in hijos_detalle)
    vpa_ciclo_completo_consolidado = round(sum(h["vpa_ciclo_completo_cop"] for h in hijos_detalle), 2)
    vpa_restante_consolidado = round(sum(h["vpa_restante_edad_actual_cop"] for h in hijos_detalle), 2)
    ahorro_univ_restante_consolidado = round(sum(h["ahorro_mensual_univ_cop"] for h in hijos_detalle), 2)

    eje_anios_rest = [f"Año {i + 1}" for i in range(horizonte_max_anios)]
    edades_0_23 = list(range(0, 24))
    flujo_nom_cons_rest = [
        round(sum(c["flujo_nominal_m"][i] for c in curvas_restante_por_hijo), 2) for i in range(horizonte_max_anios)
    ]
    vpa_acum_cons_rest = [
        round(sum(c["vpa_acum_m"][i] for c in curvas_restante_por_hijo), 2) for i in range(horizonte_max_anios)
    ]
    flujo_nom_cons_comp = [
        round(sum(c["flujo_nominal_m"][i] for c in curvas_completo_por_hijo), 2) for i in range(24)
    ]
    vpa_acum_cons_comp = [
        round(sum(c["vpa_acum_m"][i] for c in curvas_completo_por_hijo), 2) for i in range(24)
    ]

    curvas_hijo: Dict[str, Any] = {}
    if modo_horizonte == "restante":
        curvas_hijo["Hijo_1"] = curva_h1_restante
        curvas_hijo["Hijo_2"] = curva_h2_restante
        for idx_c, c_r in enumerate(curvas_restante_por_hijo, start=1):
            curvas_hijo[f"Hijo_{idx_c}"] = c_r
        curvas_hijo["Agustiniano_Suba"] = {
            "edades": eje_anios_rest,
            "flujo_nominal_m": flujo_nom_cons_rest,
            "vpa_acum_m": vpa_acum_cons_rest,
            "vpa_total_cop": vpa_restante_consolidado,
            "vpa_colegio_cop": round(sum(h["vpa_colegio_restante_cop"] for h in hijos_detalle), 2),
            "vpa_univ_cop": round(sum(h["vpa_univ_proyectada_cop"] for h in hijos_detalle), 2),
        }
        for niv_ref in ("Bajo", "Medio", "Alto"):
            mult_ref = 0.65 if niv_ref == "Bajo" else (1.0 if niv_ref == "Medio" else 1.85)
            vpa_ref_acum = 0.0
            lista_ref_acum = []
            flujo_ref_lista = []
            for i in range(horizonte_max_anios):
                f_ref = (1_950_000.0 * mult_ref * n_ref * 12.0) * ((1.0 + inf_edu) ** i)
                vp_r = f_ref / ((1.0 + tasa_descuento) ** i)
                vpa_ref_acum += vp_r
                flujo_ref_lista.append(round(f_ref / 1e6, 2))
                lista_ref_acum.append(round(vpa_ref_acum / 1e6, 2))
            curvas_hijo[niv_ref] = {
                "edades": eje_anios_rest,
                "flujo_nominal_m": flujo_ref_lista,
                "vpa_acum_m": lista_ref_acum,
                "vpa_total_cop": round(vpa_ref_acum, 2),
                "vpa_colegio_cop": round(vpa_ref_acum * 0.3, 2),
                "vpa_univ_cop": round(vpa_ref_acum * 0.7, 2),
            }
    else:
        perfiles_curva = {
            "Bajo": {
                "infancia": 1_150_000.0 * 0.65 * n_ref,
                "colegio": 1_650_000.0 * 0.65 * n_ref,
                "univ": 2_450_000.0 * 0.65 * n_ref,
            },
            "Medio": {
                "infancia": 1_150_000.0 * 1.0 * n_ref,
                "colegio": 1_650_000.0 * 1.0 * n_ref,
                "univ": 2_450_000.0 * 1.0 * n_ref,
            },
            "Alto": {
                "infancia": 1_150_000.0 * 1.85 * n_ref,
                "colegio": 1_650_000.0 * 1.85 * n_ref,
                "univ": 2_450_000.0 * 1.85 * n_ref,
            },
        }
        for niv, costos_etapa in perfiles_curva.items():
            curvas_hijo[niv] = _calcular_curva_ciclo_hijo(costos_etapa, edad_fin_ciclo=23, factor_edad_actual=1.0)
        curvas_hijo["Hijo_1"] = curva_h1_completo
        curvas_hijo["Hijo_2"] = curva_h2_completo
        for idx_c, c_c in enumerate(curvas_completo_por_hijo, start=1):
            curvas_hijo[f"Hijo_{idx_c}"] = c_c
        curvas_hijo["Agustiniano_Suba"] = {
            "edades": edades_0_23,
            "flujo_nominal_m": flujo_nom_cons_comp,
            "vpa_acum_m": vpa_acum_cons_comp,
            "vpa_total_cop": vpa_ciclo_completo_consolidado,
            "vpa_colegio_cop": round(sum(c["vpa_colegio_cop"] for c in curvas_completo_por_hijo), 2),
            "vpa_univ_cop": round(sum(c["vpa_univ_cop"] for c in curvas_completo_por_hijo), 2),
        }

    # Variables de compatibilidad para evaluación Monte Carlo y sensibilidad
    tiene_datos_h1 = hijo1_dict["gasto_mes_directo_cop"] > 0 or hijo1_dict["vpa_ciclo_completo_cop"] > 0
    tiene_datos_h2 = hijo2_dict["gasto_mes_directo_cop"] > 0 or hijo2_dict["vpa_ciclo_completo_cop"] > 0
    hijo2_en_univ = hijo2_dict["en_universidad"]
    pago_mes_directo_h1 = hijo1_dict["gasto_mes_directo_cop"]
    pago_mes_directo_h2 = hijo2_dict["gasto_mes_directo_cop"]
    costo_mes_equiv_h1 = hijo1_dict["impacto_mes_anualizado_cop"]
    costo_mes_equiv_h2 = hijo2_dict["impacto_mes_anualizado_cop"]
    flujo_anual_h1 = hijo1_dict["flujo_anual_hoy_cop"]
    flujo_anual_h2 = hijo2_dict["flujo_anual_hoy_cop"]

    # 3. Evaluación Actuarial y Monte Carlo de las 3 Decisiones Vitales (100% Paramétrico)
    decisiones_eval = {}
    trayectorias_mc = {}

    plazo_boda_ef = plazo_boda_meses if plazo_boda_meses > 0 else (24 if costo_boda > 0 else 0)
    cuota_boda_mes = (costo_boda / plazo_boda_ef) if plazo_boda_ef > 0 else 0.0
    sinergia_frac = (
        (ahorro_sinergia_pct / 100.0)
        if "ahorro_sinergia_pct" in params
        else (0.08 if (costo_boda > 0 or ingreso_pareja > 0) else 0.0)
    )
    ahorro_sinergia_pareja = (ingreso_neto_hogar + ingreso_pareja) * sinergia_frac
    balance_neto_casarse = max(0.0, cuota_boda_mes - ahorro_sinergia_pareja)

    usar_custom_colegio = nivel_hijo == "Agustiniano_Suba"

    for dec in ("CASARSE", "HIJOS", "CREDITO"):
        res_d = evaluar_viabilidad_decision_vida(
            tipo_decision=dec,
            ingreso_neto_hogar_mensual_cop=ingreso_neto_hogar,
            excedente_mensual_actual_cop=excedente_mensual,
            liquidez_emergencia_cop=liquidez_emergencia,
            nivel_costo_hijo=nivel_hijo,
            ingreso_pareja_mensual_cop=ingreso_pareja,
            costo_boda_cop=costo_boda,
            monto_credito_estructural_cop=monto_credito,
            tasa_ea_credito=tasa_ea_credito,
            plazo_credito_meses=max(1, plazo_credito) if monto_credito > 0 else 0,
            iteraciones_montecarlo=1000,
            config=cfg_custom,
            numero_hijos=max(1, numero_hijos),
            edad_actual_hijo=edad_inicio_curva,
            pension_colegio_mensual_cop=pension_colegio_mes if usar_custom_colegio else None,
            matricula_anual_cop=matricula_anual if usar_custom_colegio else None,
            transporte_escolar_mensual_cop=transporte_mes if usar_custom_colegio else 0.0,
            otros_gastos_hijo_mensual_cop=otros_gastos_mes if usar_custom_colegio else 0.0,
            manutencion_mensual_hijo_cop=manutencion_hijo_mes,
            semestre_universidad_hoy_cop=semestre_univ_hoy,
            pension_hijo2_mensual_cop=pension_hijo2_mes if usar_custom_colegio else None,
            matricula_hijo2_anual_cop=matricula_hijo2_anual if usar_custom_colegio else None,
            hijo2_en_universidad=hijo2_en_univ,
            semestre_universidad_hijo2_cop=semestre_univ_h2,
        )
        if dec == "CASARSE":
            res_d["vpa_decision_cop"] = round(costo_boda, 2)
            res_d["impacto_flujo_mensual_inmediato_cop"] = round(balance_neto_casarse, 2)
            res_d["ahorro_mensual_requerido_cop"] = round(cuota_boda_mes, 2)
            res_d["ahorro_sinergia_mensual_cop"] = round(ahorro_sinergia_pareja, 2)
            res_d["flujo_neto_sinergia_cop"] = round(ahorro_sinergia_pareja - cuota_boda_mes, 2)
            res_d["plazo_boda_meses"] = plazo_boda_ef
        elif dec == "CREDITO":
            if monto_credito <= 0 or plazo_credito <= 0:
                res_d["vpa_decision_cop"] = 0.0
                res_d["impacto_flujo_mensual_inmediato_cop"] = 0.0
                res_d["ahorro_mensual_requerido_cop"] = 0.0
                res_d["cuota_pura_credito_cop"] = 0.0
                res_d["costo_tco_mensual_cop"] = 0.0
            else:
                tasa_em_cred = ea_a_em(tasa_ea_credito)
                cuota_cred = cuota_fija_francesa(monto_credito, tasa_em_cred, plazo_credito)
                tco_frac = (tasa_tco_mensual_pct / 100.0) if "tasa_tco_mensual_pct" in params else 0.008
                tco_mes = monto_credito * tco_frac
                imp_cred = cuota_cred + tco_mes
                res_d["cuota_pura_credito_cop"] = round(cuota_cred, 2)
                res_d["costo_tco_mensual_cop"] = round(tco_mes, 2)
                res_d["impacto_flujo_mensual_inmediato_cop"] = round(imp_cred, 2)
                res_d["ahorro_mensual_requerido_cop"] = round(imp_cred, 2)
                res_d["vpa_decision_cop"] = round(imp_cred * plazo_credito, 2)
        elif dec == "HIJOS":
            if modo_horizonte == "restante":
                res_d["vpa_decision_cop"] = round(vpa_restante_consolidado, 2)
            else:
                res_d["vpa_decision_cop"] = round(vpa_ciclo_completo_consolidado, 2)
            res_d["impacto_flujo_mensual_inmediato_cop"] = round(costo_mes_equiv_agustiniano_total, 2)
            res_d["ahorro_mensual_requerido_cop"] = round(ahorro_univ_restante_consolidado, 2)
            if numero_hijos == 0:
                res_d["recomendacion_actuarial_y_legal"] = (
                    "Sin hijos seleccionados (0 hijos). Si proyecta tener o financiar hijos, seleccione la cantidad en el Paso Inicial."
                )
            else:
                resumen_hijos_txt = " + ".join(
                    f"Hijo {h['indice']} ({h['edad']}a, {h['etiqueta_grado']})" for h in hijos_detalle
                )
                res_d["recomendacion_actuarial_y_legal"] = (
                    f"{resumen_hijos_txt}. Con Excedente=${excedente_mensual:,.0f} y Ahorro=${liquidez_emergencia:,.0f}, "
                    f"flujo consolidado=${pago_mes_directo_total:,.0f} COP/mes."
                )
            vpa_1_hijo_completo = round(vpa_ciclo_completo_consolidado / max(1, numero_hijos), 2)
            res_d["desglose_colegio"] = {
                "numero_hijos": numero_hijos,
                "edad_actual": edad_actual_hijo,
                "edad_hijo1": hijo1_dict["edad"],
                "edad_hijo2": hijo2_dict["edad"],
                "edad_inicio_curva": edad_inicio_curva,
                "modo_horizonte": modo_horizonte,
                "hijos_detalle": hijos_detalle,
                "hijo1": hijo1_dict,
                "hijo2": hijo2_dict,
                "consolidado": {
                    "numero_hijos": numero_hijos,
                    "hijo2_en_universidad": hijo2_en_univ,
                    "semestre_actual_h2": hijo2_dict["semestre_actual"],
                    "educacion_h1_colegio_mes_cop": round(
                        (
                            hijo1_dict["matricula_univ_mensualizada_cop"] + hijo1_dict["ruta_mes_cop"]
                            if hijo1_dict["en_universidad"]
                            else hijo1_dict["pension_mes_cop"] + hijo1_dict["ruta_mes_cop"] + hijo1_dict["matricula_prorrateada_mes_cop"]
                        ),
                        2,
                    ),
                    "educacion_h2_univ_mes_cop": round(
                        (
                            hijo2_dict["matricula_univ_mensualizada_cop"] + hijo2_dict["ruta_mes_cop"]
                            if hijo2_dict["en_universidad"]
                            else hijo2_dict["pension_mes_cop"] + hijo2_dict["ruta_mes_cop"] + hijo2_dict["matricula_prorrateada_mes_cop"]
                        ),
                        2,
                    ),
                    "educacion_todos_hijos_mes_cop": round(
                        sum(
                            (
                                h["matricula_univ_mensualizada_cop"] + h["ruta_mes_cop"]
                                if h["en_universidad"]
                                else h["pension_mes_cop"] + h["ruta_mes_cop"] + h["matricula_prorrateada_mes_cop"]
                            )
                            for h in hijos_detalle
                        ),
                        2,
                    ),
                    "pensiones_sumadas_mes_cop": round(
                        sum((h["matricula_univ_mensualizada_cop"] if h["en_universidad"] else h["pension_mes_cop"]) for h in hijos_detalle),
                        2,
                    ),
                    "matriculas_sumadas_anual_cop": round(
                        sum((h["matricula_univ_anual_cop"] if h["en_universidad"] else h["matricula_anual_cop"]) for h in hijos_detalle),
                        2,
                    ),
                    "rutas_sumadas_mes_cop": round(sum(h["ruta_mes_cop"] for h in hijos_detalle), 2),
                    "manutencion_y_otros_sumados_mes_cop": round(
                        sum(h["manutencion_y_otros_mes_cop"] for h in hijos_detalle),
                        2,
                    ),
                    "gasto_mes_directo_total_cop": round(pago_mes_directo_total, 2),
                    "impacto_mes_anualizado_total_cop": round(costo_mes_equiv_agustiniano_total, 2),
                    "flujo_anual_total_hoy_cop": round(flujo_anual_agustiniano_total, 2),
                    "vpa_ciclo_completo_total_cop": vpa_ciclo_completo_consolidado,
                    "vpa_restante_total_cop": round(vpa_restante_consolidado, 2),
                    "ahorro_mensual_univ_total_cop": round(ahorro_univ_restante_consolidado, 2),
                    "excedente_mensual_cop": round(excedente_mensual, 2),
                    "liquidez_emergencia_cop": round(liquidez_emergencia, 2),
                    "balance_flujo_mensual_cop": round(excedente_mensual - pago_mes_directo_total, 2),
                },
                "vpa_1_hijo_ciclo_completo_cop": vpa_1_hijo_completo,
                "vpa_total_hijos_ciclo_completo_cop": vpa_ciclo_completo_consolidado,
                "vpa_restante_desde_edad_actual_cop": round(vpa_restante_consolidado, 2),
                "pago_mes_directo_h1_cop": round(pago_mes_directo_h1, 2),
                "pago_mes_directo_h2_cop": round(pago_mes_directo_h2, 2),
                "pago_mes_escolar_1_hijo_cop": round(costo_mes_equiv_h1, 2),
                "pago_mes_escolar_total_hijos_cop": round(pago_mes_directo_total, 2),
                "impacto_anualizado_total_hijos_cop": round(costo_mes_equiv_agustiniano_total, 2),
                "flujo_anual_colegio_total_hijos_cop": round(flujo_anual_agustiniano_total, 2),
                "vpa_colegio_restante_cop": curvas_hijo[nivel_hijo]["vpa_colegio_cop"],
                "vpa_universidad_proyectada_cop": curvas_hijo[nivel_hijo]["vpa_univ_cop"],
            }

        # Recalcular Monte Carlo con el impacto mensual exacto parametrizado
        rng = random.Random(20261110)
        impacto_mc = res_d["impacto_flujo_mensual_inmediato_cop"]
        flujos_sim = []
        solventes_mc = 0
        for _ in range(1000):
            c_ing = rng.gauss(1.0, 0.08)
            c_gas = rng.gauss(1.0, 0.07)
            f_neto = excedente_mensual * c_ing - impacto_mc * c_gas + (liquidez_emergencia / 24.0)
            if f_neto >= 0:
                solventes_mc += 1
            flujos_sim.append(round(f_neto / 1e6, 3))
        prob_mc = round((solventes_mc / 1000.0) * 100.0, 2)
        res_d["probabilidad_exito_montecarlo_pct"] = prob_mc
        res_d["dictamen_viabilidad"] = (
            "VIABLE_SOLVENTE"
            if prob_mc >= 80.0
            else ("VIABLE_CON_AJUSTES_PREVIOS" if prob_mc >= 55.0 else "RIESGO_CRITICO_APLAZAR_Y_CAPITALIZAR")
        )
        decisiones_eval[dec] = res_d
        trayectorias_mc[dec] = flujos_sim

    # 4. Curva de sensibilidad (Excedente vs Probabilidad de Solvencia)
    eje_excedentes_m = []
    sens_casarse = []
    sens_hijos = []
    sens_credito = []
    for exc in range(500_000, 8_500_000, 500_000):
        eje_excedentes_m.append(round(exc / 1e6, 2))
        for dec, lista_dest in (("CASARSE", sens_casarse), ("HIJOS", sens_hijos), ("CREDITO", sens_credito)):
            r_s = evaluar_viabilidad_decision_vida(
                tipo_decision=dec,
                ingreso_neto_hogar_mensual_cop=ingreso_neto_hogar,
                excedente_mensual_actual_cop=float(exc),
                liquidez_emergencia_cop=liquidez_emergencia,
                nivel_costo_hijo=nivel_hijo,
                ingreso_pareja_mensual_cop=ingreso_pareja,
                costo_boda_cop=costo_boda,
                monto_credito_estructural_cop=monto_credito,
                tasa_ea_credito=tasa_ea_credito,
                plazo_credito_meses=max(1, plazo_credito) if monto_credito > 0 else 0,
                iteraciones_montecarlo=350,
                config=cfg_custom,
                numero_hijos=max(1, numero_hijos) if (tiene_datos_h1 or tiene_datos_h2) else 0,
                edad_actual_hijo=edad_inicio_curva,
                pension_colegio_mensual_cop=pension_colegio_mes if usar_custom_colegio else None,
                matricula_anual_cop=matricula_anual if usar_custom_colegio else None,
                transporte_escolar_mensual_cop=transporte_mes if usar_custom_colegio else 0.0,
                otros_gastos_hijo_mensual_cop=otros_gastos_mes if usar_custom_colegio else 0.0,
                manutencion_mensual_hijo_cop=manutencion_hijo_mes,
                semestre_universidad_hoy_cop=semestre_univ_hoy,
                pension_hijo2_mensual_cop=pension_hijo2_mes if usar_custom_colegio else None,
                matricula_hijo2_anual_cop=matricula_hijo2_anual if usar_custom_colegio else None,
                hijo2_en_universidad=hijo2_en_univ,
                semestre_universidad_hijo2_cop=semestre_univ_h2,
            )
            lista_dest.append(r_s["probabilidad_exito_montecarlo_pct"])

    # 5. Flujo Integrado Caso Maestro OED (6 Módulos)
    mod6_perfil = perfilar_inversionista_decreto_2555(5, 12.0, 4, 3)
    mod6_azar = comparar_azar_vs_inversion_compuesta(200_000.0, 10)
    mod6_piramide = detectar_esquema_piramidal_ponzi(10.0, 3)
    mod1_pres = diagnosticar_presupuesto_y_flujo_caja(
        ingreso_bruto_mensual_cop=ingreso_neto_hogar if ingreso_neto_hogar > 0 else 6_500_000.0,
        gastos_fijos_vitales_cop=2_800_000.0,
        gastos_variables_estilo_vida_cop=950_000.0,
        gastos_hormiga_mensual_cop=320_000.0,
        cuotas_deuda_mensual_cop=600_000.0,
        liquidez_actual_fondo_emergencia_cop=liquidez_emergencia,
    )
    mod3_deudas = optimizar_portafolio_deudas(
        ingreso_neto_mensual_cop=mod1_pres["ingreso_neto_mensual_cop"],
        abono_extra_mensual_cop=300_000.0,
        lista_deudas=[
            {"nombre": "Tarjeta Crédito", "saldo_cop": 4_500_000.0, "tasa_ea": 0.255, "cuota_mensual_cop": 350_000.0},
            {"nombre": "Libre Inversión", "saldo_cop": 8_000_000.0, "tasa_ea": 0.165, "cuota_mensual_cop": 250_000.0},
        ],
    )
    mod2_inv = estructurar_portafolio_salario(
        excedente_mensual_cop=excedente_mensual,
        perfil_riesgo=mod6_perfil["perfil_riesgo"],
        horizonte_meses=60,
    )
    mod4_finca = evaluar_inversion_finca_raiz(
        valor_inmueble_cop=200_000_000.0,
        ingreso_familiar_neto_cop=ingreso_neto_hogar if ingreso_neto_hogar > 0 else 6_500_000.0,
    )

    # 6. Diagnóstico cálido del "Médico Financiero Amigo" + Receta del Mes (Manual de Marca OED)
    decs_activas = []
    if desea_boda:
        decs_activas.append(("Boda", decisiones_eval["CASARSE"]))
    if numero_hijos > 0:
        decs_activas.append((f"Hijos ({numero_hijos})", decisiones_eval["HIJOS"]))
    if desea_credito:
        decs_activas.append(("Crédito", decisiones_eval["CREDITO"]))

    if not decs_activas:
        nivel_med = "azul"
        titulo_med = "Bienvenida tranquila a tu Consultorio Financiero Amigo OED"
        explicacion_med = (
            "Tus signos vitales están listos en $0 COP esperando que elijas tus metas en el Paso 1. "
            "Aquí evaluamos tus planes con simulación actuarial de Monte Carlo, descuento en EA y ajuste por IPC, "
            "cuidando tu privacidad bajo Habeas Data y Ley 1581."
        )
        receta_med = (
            "Selecciona arriba a la izquierda cuántos hijos deseas proyectar (0 a 6), si deseas un crédito o una boda, "
            "y separa desde hoy un primer ahorro mensual en un FIC o CDT protegido por Fogafín."
        )
    else:
        prob_min = min(d["probabilidad_exito_montecarlo_pct"] for _, d in decs_activas)
        impacto_tot_mes = sum(d["impacto_flujo_mensual_inmediato_cop"] for _, d in decs_activas)
        vpa_tot_planes = sum(d["vpa_decision_cop"] for _, d in decs_activas)
        if prob_min >= 80.0:
            nivel_med = "verde"
            titulo_med = "Tus signos vitales financieros están firmes y saludables"
            explicacion_med = (
                f"¡Excelente noticia! Con tu excedente mensual de {formatear_cop_claro(excedente_mensual)} y tu reserva "
                f"de {formatear_cop_claro(liquidez_emergencia)}, superas el {prob_min:.1f}% de los 1.000 escenarios de "
                f"Monte Carlo frente a un compromiso mensual estimado de {formatear_cop_claro(impacto_tot_mes)} "
                f"(valor presente total de {formatear_cop_claro(vpa_tot_planes)} descontado en EA frente al IPC)."
            )
            receta_med = (
                f"Programa un débito automático mensual de {formatear_cop_claro(max(200_000.0, impacto_tot_mes * 0.25))} "
                "el mismo día que recibes tu pago hacia un FIC o CDT vigilado con seguro Fogafín para blindar tu tranquilidad."
            )
        elif prob_min >= 55.0:
            nivel_med = "ambar"
            titulo_med = "Chequeo preventivo a tiempo: tu meta es viable cuidando el flujo mensual"
            explicacion_med = (
                f"Tu plan alcanza una solvencia de {prob_min:.1f}% en la prueba de esfuerzo de Monte Carlo. "
                f"El flujo requerido hoy es de {formatear_cop_claro(impacto_tot_mes)}/mes frente a tu excedente de "
                f"{formatear_cop_claro(excedente_mensual)}/mes, por lo que conviene vigilar la inflación del IPC y "
                "evitar créditos cercanos a la Tasa de Usura."
            )
            brecha_preventiva = max(150_000.0, impacto_tot_mes - excedente_mensual) if impacto_tot_mes > excedente_mensual else max(200_000.0, impacto_tot_mes * 0.15)
            receta_med = (
                f"Fortalece tu colchón separando {formatear_cop_claro(brecha_preventiva)} adicionales este mes en un FIC "
                "con interés compuesto antes de asumir nuevos compromisos fijos."
            )
        else:
            nivel_med = "rojo"
            titulo_med = "Hagamos una pausa protectora para cuidar tu sueño tranquilo"
            brecha_mes = max(0.0, impacto_tot_mes - excedente_mensual)
            explicacion_med = (
                f"Cero regaños, estamos aquí para cuidarte: hoy tus planes requieren {formatear_cop_claro(impacto_tot_mes)}/mes "
                f"y tu excedente libre es de {formatear_cop_claro(excedente_mensual)}/mes (brecha de {formatear_cop_claro(brecha_mes)}/mes). "
                f"En la prueba de Monte Carlo tu solvencia actual es {prob_min:.1f}%, así que primero demos oxígeno a tu caja."
            )
            dosis_inicial = max(100_000.0, round((brecha_mes if brecha_mes > 0 else 300_000.0) * 0.20, -3))
            receta_med = (
                f"Empieza este mes separando una dosis suave de {formatear_cop_claro(dosis_inicial)} en un CDT o FIC protegido por Fogafín "
                "y aplaza 6 a 12 meses los gastos no urgentes para evitar sobreendeudamiento."
            )

    return {
        "mensaje_ejecucion": "PRUEBA EXITOSA",
        "timestamp_calculo": datetime.now().strftime("%H:%M:%S"),
        "manual_marca_oed": {
            "paleta": PALETA_MARCA_OED,
            "colores_graficas": COLORES_GRAFICAS_OED,
            "ruta_clinica": RUTA_CLINICA_FINANCIERA_OED,
            "glosario": GLOSARIO_LENGUAJE_CLARO_OED,
            "diagnostico_medico_amigo": {
                "nivel": nivel_med,
                "titulo_html": enriquecer_texto_con_explicaciones(titulo_med),
                "explicacion_html": enriquecer_texto_con_explicaciones(explicacion_med),
                "receta_html": enriquecer_texto_con_explicaciones(receta_med),
            },
        },
        "parametros_activos": {
            "ingreso_neto_hogar": ingreso_neto_hogar,
            "excedente_mensual": excedente_mensual,
            "excedente_m": round(excedente_mensual / 1e6, 2),
            "liquidez_emergencia": liquidez_emergencia,
            "numero_hijos": numero_hijos,
            "tiene_hijos": numero_hijos > 0,
            "desea_boda": desea_boda,
            "desea_credito": desea_credito,
            "edad_actual_hijo": edad_actual_hijo,
            "inflacion_educativa_pct": round(inf_edu * 100.0, 2),
            "tasa_descuento_pct": round(tasa_descuento * 100.0, 2),
            "ipc_anual_pct": round(ipc * 100.0, 2),
        },
        "habeas_data": {
            "consentimiento": consentimiento,
            "permanencia": permanencia,
            "curva_habeas": curva_habeas,
            "estado_disco_msg": estado_disco_msg,
            "token_muestra": token_muestra,
            "archivo_existe": ruta_archivo_cifrado.exists(),
            "texto_ley_1581": TEXTO_AUTORIZACION_LEY_1581,
        },
        "actuaria_mod5": {
            "nivel_seleccionado": nivel_hijo,
            "curvas_hijo": curvas_hijo,
            "decisiones": decisiones_eval,
            "trayectorias_mc": trayectorias_mc,
            "sensibilidad": {
                "excedentes_m": eje_excedentes_m,
                "CASARSE": sens_casarse,
                "HIJOS": sens_hijos,
                "CREDITO": sens_credito,
            },
        },
        "caso_integrado_6_modulos": {
            "mod6_salin": {
                "perfil_riesgo": mod6_perfil["perfil_riesgo"],
                "puntaje": mod6_perfil["puntaje_idoneidad_100"],
                "patrimonio_10a_inversion_cop": mod6_azar["patrimonio_inversion_compuesta_cop"],
                "valor_esperado_azar_cop": mod6_azar["valor_esperado_azar_cop"],
                "ciclos_colapso_piramide": mod6_piramide["ciclos_para_agotar_poblacion_colombia"],
            },
            "mod1_nidia": {
                "ingreso_neto_cop": mod1_pres["ingreso_neto_mensual_cop"],
                "excedente_mensual_cop": mod1_pres["excedente_mensual_cop"],
                "costo_hormiga_10a_cop": mod1_pres["costo_oportunidad_hormiga_10a_cop"],
                "meses_emergencia": mod1_pres["meses_fondo_emergencia"],
            },
            "mod3_catalina": {
                "indice_endeudamiento_pct": mod3_deudas["indice_endeudamiento_pct"],
                "estrategia_optima": mod3_deudas["estrategia_optima"],
                "ahorro_intereses_cop": mod3_deudas["ahorro_intereses_cop"],
                "flujo_liberado_cop": mod3_deudas["flujo_caja_liberado_cop"],
            },
            "mod2_camilo": {
                "patrimonio_5a_nominal_cop": mod2_inv.get("patrimonio_proyectado_nominal_cop", 0.0),
                "patrimonio_5a_real_cop": mod2_inv.get("patrimonio_proyectado_real_cop", 0.0),
                "tasa_real_neta_pct": mod2_inv.get("tasa_real_neta_portafolio_pct", 0.0),
            },
            "mod4_jesi": {
                "segmento": mod4_finca["segmento_vivienda"],
                "primera_cuota_pesos_cop": mod4_finca["primera_cuota_credito_cop"],
                "cumple_ley_546": mod4_finca["cumple_ley_546_30pct"],
                "cap_rate_neto_pct": mod4_finca["cap_rate_neto_pct"],
            },
        },
    }


HTML_DASHBOARD = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Consultorio Financiero Amigo OED — Positiva (Nelson Angel)</title>
<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
<style>
  :root {
    /* PALETA OFICIAL DEL CONSULTORIO FINANCIERO AMIGO OED + TONOS SUAVES */
    --bg: #F4F7FB;
    --card: #FFFFFF;
    --primary: #0F294A;       /* Azul Bata Médica (Confianza OED) */
    --accent: #1D4ED8;        /* Azul Cuidado Activo */
    --positiva: #EA580C;      /* Naranja Receta Positiva */
    --positiva-soft: #FFF7ED; /* Fondo suave Crema Positiva */
    --success: #15803D;       /* Verde Signos Vitales Sanos */
    --warn: #B45309;          /* Ámbar Chequeo Preventivo */
    --danger: #B91C1C;        /* Rojo Cuidado Intensivo (Sin Regaños) */
    --text: #0F294A;
    --muted: #475569;
    --border: #DDE4EE;
  }
  * { box-sizing: border-box; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }
  body { margin: 0; background: var(--bg); color: var(--text); }
  header {
    background: linear-gradient(135deg, #0F294A 0%, #163A66 58%, #1D4ED8 100%);
    color: #fff; padding: 14px 28px; display: flex; justify-content: space-between; align-items: center;
    box-shadow: 0 4px 16px rgba(15, 41, 74, 0.12); border-bottom: 3px solid #EA580C;
  }
  .header-brand {
    display: flex; align-items: center; gap: 14px;
  }
  .positiva-logo-wrap {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    background: linear-gradient(180deg, #FFFFFF 0%, #FFF7ED 100%);
    border: 2px solid #FDBA74; border-radius: 12px; padding: 5px 8px;
    box-shadow: 0 3px 10px rgba(234, 88, 12, 0.22); flex-shrink: 0;
  }
  .positiva-logo-wrap span {
    font-size: 0.6rem; font-weight: 800; letter-spacing: 0.9px; color: #EA580C; margin-top: 1px;
    text-transform: uppercase;
  }
  header h1 { margin: 0; font-size: 1.26rem; font-weight: 700; color: #FFFFFF; letter-spacing: -0.2px; }
  header p { margin: 3px 0 0; font-size: 0.85rem; color: #E2E8F0; }
  .badge-top {
    background: rgba(255, 247, 237, 0.14); border: 1px solid rgba(253, 186, 116, 0.55);
    padding: 7px 14px; border-radius: 999px; font-size: 0.8rem; font-weight: 600; color: #FFF7ED;
    display: flex; align-items: center; gap: 7px;
  }
  .oed-steps-bar {
    background: #FFFFFF; border-bottom: 1px solid var(--border); padding: 9px 28px;
    display: flex; flex-wrap: wrap; gap: 6px; align-items: center;
  }
  .oed-step-pill {
    font-size: 0.75rem; padding: 4px 11px; border-radius: 999px;
    border: 1px solid #CBD5E1; background: #F8FAFC; color: #475569; font-weight: 500;
    transition: all 0.18s ease;
  }
  .oed-step-active {
    background: #EA580C; color: #FFFFFF; border-color: #EA580C; font-weight: 700;
    box-shadow: 0 2px 6px rgba(234, 88, 12, 0.25);
  }
  .oed-medico-banner {
    background: linear-gradient(135deg, #EFF6FF 0%, #FFF7ED 100%);
    border: 1px solid #BFDBFE; border-left: 5px solid #0F294A;
    border-radius: 12px; padding: 11px 16px; margin-bottom: 14px;
    display: flex; align-items: center; justify-content: space-between; gap: 12px;
  }
  .oed-medico-banner p { margin: 0; font-size: 0.86rem; color: #0F294A; line-height: 1.45; }
  .oed-doc-card {
    border-radius: 12px; padding: 12px 15px; margin: 0 0 10px 0; border-left: 6px solid;
    font-size: 0.88rem; line-height: 1.5; box-shadow: 0 2px 6px rgba(15, 41, 74, 0.04);
  }
  .oed-doc-verde { background: #F0FDF4; border-color: #15803D; color: #14532D; }
  .oed-doc-azul  { background: #EFF6FF; border-color: #1D4ED8; color: #1E3A8A; }
  .oed-doc-ambar { background: #FFFBEB; border-color: #B45309; color: #78350F; }
  .oed-doc-rojo  { background: #FEF2F2; border-color: #B91C1C; color: #7F1D1D; }
  .oed-rx-box {
    background: #FFF7ED; border: 1px solid #FED7AA; border-left: 6px solid #EA580C;
    padding: 11px 15px; border-radius: 12px; margin: 0 0 14px 0; color: #431407;
    font-size: 0.87rem; line-height: 1.48;
  }
  .oed-term {
    position: relative; border-bottom: 2px dotted #1D4ED8; cursor: help;
    font-weight: 600; padding: 0 2px; border-radius: 3px; background: rgba(29, 78, 216, 0.07);
  }
  .oed-q {
    font-size: 0.68em; color: #FFFFFF; background: #1D4ED8; border-radius: 999px;
    padding: 0 4px; margin-left: 2px; font-weight: 700;
  }
  .oed-term:hover::after, .oed-term:focus::after {
    content: attr(data-tip); position: absolute; left: 0; bottom: 125%;
    min-width: 250px; max-width: 330px; background: #0F294A; color: #FFFFFF;
    padding: 9px 11px; border-radius: 9px; font-size: 0.78rem; font-weight: 400;
    line-height: 1.4; z-index: 9999; box-shadow: 0 8px 20px rgba(15, 41, 74, 0.28);
    white-space: normal;
  }
  .tabs {
    display: flex; gap: 8px; padding: 10px 28px 0; background: #EEF3F9; border-bottom: 1px solid var(--border);
  }
  .tab-btn {
    border: none; background: transparent; padding: 10px 18px; font-size: 0.9rem; font-weight: 600;
    color: var(--muted); cursor: pointer; border-bottom: 3px solid transparent; border-radius: 10px 10px 0 0;
    transition: all 0.15s ease;
  }
  .tab-btn.active { background: var(--card); color: var(--primary); border-bottom-color: var(--positiva); font-weight: 700; }
  .container { max-width: 1480px; margin: 0 auto; padding: 16px 24px 40px; }
  .tab-content { display: none; }
  .tab-content.active { display: block; }
  .grid-sidebar { display: grid; grid-template-columns: 375px 1fr; gap: 20px; align-items: start; }
  .card {
    background: var(--card); border: 1px solid var(--border); border-radius: 13px; padding: 16px;
    box-shadow: 0 2px 8px rgba(15, 41, 74, 0.04); margin-bottom: 16px;
  }
  .card h3 { margin: 0 0 10px; font-size: 0.98rem; color: var(--primary); }
  .sub-panel {
    background: #F8FAFC; border: 1px solid #DBEAFE; border-radius: 10px; padding: 11px 12px; margin-bottom: 12px;
  }
  .sub-panel h4 { margin: 0 0 8px; font-size: 0.85rem; color: #0F294A; }
  .child-input-box {
    border-radius: 9px; padding: 9px 10px; margin-bottom: 9px; border: 1px solid #DDE4EE;
  }
  .child-input-h1 { background: #EFF6FF; border-left: 4px solid #1D4ED8; }
  .child-input-h2 { background: #FFF7ED; border-left: 4px solid #EA580C; }
  .child-input-h3 { background: #F0FDF4; border-left: 4px solid #15803D; }
  .child-input-h4 { background: #F5F3FF; border-left: 4px solid #7C3AED; }
  .child-input-h5 { background: #FEF2F2; border-left: 4px solid #DC2626; }
  .child-input-h6 { background: #F8FAFC; border-left: 4px solid #475569; }
  .child-input-box h5 { margin: 0 0 6px; font-size: 0.82rem; font-weight: 700; color: #0F294A; }
  .children-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(275px, 1fr)); gap: 14px; margin-bottom: 16px;
  }
  .child-card {
    background: #FFFFFF; border: 1px solid var(--border); border-radius: 13px; padding: 14px 16px;
    box-shadow: 0 3px 10px rgba(15, 41, 74, 0.05); position: relative; overflow: hidden;
  }
  .child-card.h1 { border-top: 5px solid #1D4ED8; }
  .child-card.h2 { border-top: 5px solid #EA580C; }
  .child-card.h3 { border-top: 5px solid #15803D; }
  .child-card.h4 { border-top: 5px solid #7C3AED; }
  .child-card.h5 { border-top: 5px solid #DC2626; }
  .child-card.h6 { border-top: 5px solid #475569; }
  .child-card.consolidado {
    background: linear-gradient(180deg, #EFF6FF 0%, #FFFFFF 100%);
    border: 2px solid #0F294A; border-top: 5px solid #EA580C;
    box-shadow: 0 4px 14px rgba(15, 41, 74, 0.10);
  }
  .child-badge {
    display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 0.73rem; font-weight: 700;
    margin-bottom: 6px;
  }
  .badge-h1 { background: #DBEAFE; color: #1E3A8A; }
  .badge-h2 { background: #FFEDD5; color: #9A3412; }
  .badge-h3 { background: #DCFCE7; color: #14532D; }
  .badge-h4 { background: #EDE9FE; color: #5B21B6; }
  .badge-h5 { background: #FEE2E2; color: #991B1B; }
  .badge-h6 { background: #F1F5F9; color: #334155; }
  .badge-cons { background: #0F294A; color: #FFFFFF; }
  .wizard-box {
    background: linear-gradient(135deg, #EFF6FF 0%, #FFF7ED 100%);
    border: 1.5px solid #93C5FD; border-left: 5px solid #EA580C;
    border-radius: 11px; padding: 12px 13px; margin-bottom: 14px;
  }
  .wizard-box h3 { margin: 0 0 8px; font-size: 0.93rem; color: #0F294A; }
  .child-vpa-main { font-size: 1.26rem; font-weight: 800; color: #0F294A; margin: 2px 0 4px; }
  .child-vpa-sub { font-size: 0.77rem; color: var(--muted); margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px dashed #CBD5E1; }
  .metric-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
  .metric-table td { padding: 4px 0; border-bottom: 1px solid #F1F5F9; }
  .metric-table td:last-child { text-align: right; font-weight: 700; color: #0F294A; }
  .metric-table tr.total-row td {
    border-top: 2px solid #CBD5E1; border-bottom: none; padding-top: 7px; font-size: 0.85rem; font-weight: 800; color: #1D4ED8;
  }
  .metric-table tr.highlight-row td {
    background: #FFF7ED; padding: 5px 6px; border-radius: 4px; color: #EA580C; font-weight: 800;
  }
  .section-label {
    font-size: 0.88rem; font-weight: 800; color: var(--primary); margin: 0 0 10px;
    display: flex; align-items: center; justify-content: space-between;
  }
  .form-row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
  .form-group { margin-bottom: 9px; position: relative; }
  .form-group label {
    display: flex; align-items: center; justify-content: space-between;
    font-size: 0.78rem; font-weight: 600; color: var(--muted); margin-bottom: 3px; cursor: help;
  }
  .tip-badge {
    display: inline-flex; align-items: center; justify-content: center;
    width: 15px; height: 15px; border-radius: 50%; background: #DBEAFE; color: #1D4ED8;
    font-size: 0.68rem; font-weight: 800; margin-left: 4px; flex-shrink: 0;
  }
  .form-group input, .form-group select {
    width: 100%; padding: 7px 9px; border: 1px solid #CBD5E1; border-radius: 7px; font-size: 0.87rem;
    background: #FFFFFF; color: #0F294A; transition: border-color 0.15s, box-shadow 0.15s;
  }
  .form-group input:hover, .form-group select:hover,
  .form-group input:focus, .form-group select:focus {
    border-color: #1D4ED8; box-shadow: 0 0 0 3px rgba(29, 78, 216, 0.14); outline: none;
  }
  .oed-tooltip-floating {
    position: fixed; z-index: 99999; pointer-events: none;
    background: #0F294A; color: #FFFFFF; padding: 9px 12px; border-radius: 9px;
    font-size: 0.8rem; line-height: 1.4; font-weight: 400;
    max-width: 295px; box-shadow: 0 8px 22px rgba(15, 41, 74, 0.30);
    border-left: 4px solid #EA580C;
    opacity: 0; transform: translateY(4px); transition: opacity 0.12s ease, transform 0.12s ease;
  }
  .oed-tooltip-floating.visible {
    opacity: 1; transform: translateY(0);
  }
  .oed-tooltip-floating strong {
    display: block; color: #FDBA74; font-size: 0.74rem; text-transform: uppercase;
    letter-spacing: 0.3px; margin-bottom: 2px;
  }
  .btn {
    display: inline-block; width: 100%; padding: 10px 14px; border: none; border-radius: 9px;
    font-weight: 700; font-size: 0.89rem; cursor: pointer; text-align: center; transition: 0.18s;
    margin-top: 6px;
  }
  .btn-primary { background: #1D4ED8; color: #fff; }
  .btn-primary:hover { background: #0F294A; transform: translateY(-1px); }
  .btn-success { background: #15803D; color: #fff; }
  .btn-danger { background: #B91C1C; color: #fff; }
  .status-banner {
    margin-top: 9px; padding: 7px 10px; border-radius: 8px; font-size: 0.8rem; font-weight: 600;
    background: #F0FDF4; color: #14532D; text-align: center; border: 1px solid #BBF7D0;
  }
  .kpi-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(275px, 1fr)); gap: 14px; margin-bottom: 16px; }
  .kpi-card {
    background: var(--card); border: 1px solid var(--border); border-left: 5px solid var(--accent);
    border-radius: 12px; padding: 14px 16px; transition: box-shadow 0.25s;
  }
  .kpi-card.flash { box-shadow: 0 0 0 3px rgba(29, 78, 216, 0.28); }
  .kpi-title { font-size: 0.77rem; font-weight: 700; color: var(--muted); text-transform: uppercase; }
  .kpi-val { font-size: 1.28rem; font-weight: 800; color: var(--primary); margin: 5px 0; }
  .kpi-sub { font-size: 0.79rem; color: var(--muted); line-height: 1.45; }
  .pill { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 0.74rem; font-weight: 700; }
  .pill-ok { background: #F0FDF4; color: #15803D; border: 1px solid #BBF7D0; }
  .pill-warn { background: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }
  .pill-bad { background: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }
  .legal-box {
    background: #EFF6FF; border-left: 4px solid var(--primary); padding: 12px 14px;
    border-radius: 8px; font-size: 0.84rem; line-height: 1.45; margin-bottom: 12px;
  }
  .code-box {
    background: #0F294A; color: #A7F3D0; font-family: Consolas, monospace; font-size: 0.8rem;
    padding: 10px 12px; border-radius: 8px; overflow-x: auto; margin-top: 8px;
  }
  .glossary-pill {
    display: inline-block; padding: 4px 11px; border-radius: 999px; font-size: 0.76rem;
    border: 1px solid #CBD5E1; margin: 3px; cursor: pointer; background: #FFFFFF; color: #334155;
    transition: all 0.15s;
  }
  .glossary-pill.active {
    background: #1D4ED8; color: #FFFFFF; border-color: #1D4ED8; font-weight: 700;
  }
  .charts-2col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  @media (max-width: 1100px) {
    .grid-sidebar, .children-grid, .kpi-row, .charts-2col { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>

<header>
  <div class="header-brand">
    <!-- LOGO SIMÉTRICO Y SUAVE DE POSITIVA COMPAÑÍA DE SEGUROS / OED -->
    <div class="positiva-logo-wrap" title="Positiva Compañía de Seguros — Consultorio Financiero Amigo OED">
      <svg id="logo-positiva-svg" width="38" height="38" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="Logo Positiva">
        <rect x="4" y="4" width="56" height="56" rx="16" fill="#0F294A" stroke="#EA580C" stroke-width="3"/>
        <circle cx="32" cy="32" r="20" fill="#FFF7ED" stroke="#FDBA74" stroke-width="2"/>
        <!-- Cruz simétrica cálida Positiva -->
        <rect x="28" y="16" width="8" height="32" rx="4" fill="#EA580C"/>
        <rect x="16" y="28" width="32" height="8" rx="4" fill="#EA580C"/>
        <!-- Punto central de equilibrio y bienestar -->
        <circle cx="32" cy="32" r="5" fill="#0F294A"/>
        <circle cx="32" cy="32" r="2.2" fill="#FFFFFF"/>
      </svg>
      <span>POSITIVA</span>
    </div>
    <div>
      <h1>🩺 Consultorio Financiero Amigo OED — Tu Médico Financiero de Cabecera</h1>
      <p>Especialista Paso 6 y Paso 0: <strong>Nelson Angel</strong> (Rama <code>nean</code>) &bull; Manual de Marca Oficial OED &bull; Cero Palabras Huérfanas (<code>?</code>)</p>
    </div>
  </div>
  <div class="badge-top" id="badge-hora">🛡️ Positiva OED &bull; Ley 1581 &bull; Monte Carlo</div>
</header>

<!-- BLOQUE 1 DEL MANUAL DE MARCA: BARRA DE PROGRESO DE LOS 7 PASOS (PASOS 0 AL 6) -->
<div class="oed-steps-bar" id="barra-7-pasos-oed">
  <span class="oed-step-pill" id="pill-paso-0">Paso 0: 🩺 Bienvenida y Confidencialidad (Nelson + Camilo)</span>
  <span class="oed-step-pill">Paso 1: 🫀 Pulso ante el Riesgo (Salin)</span>
  <span class="oed-step-pill">Paso 2: 🩻 Radiografía de tu Sueldo (Nidia)</span>
  <span class="oed-step-pill">Paso 3: 🩹 Alivio de Deudas (Catalina)</span>
  <span class="oed-step-pill">Paso 4: 🌱 Vitaminas de Inversión (Camilo)</span>
  <span class="oed-step-pill">Paso 5: 🏡 Comprar Casa sin Ahogarte (Jesi)</span>
  <span class="oed-step-pill oed-step-active" id="pill-paso-6">Paso 6: 🛡️ Prueba de Esfuerzo Grandes Planes (Nelson)</span>
</div>

<div class="tabs">
  <button class="tab-btn active" onclick="abrirTab('tab-mod5', this)">🛡️ Paso 6: Prueba de Esfuerzo Actuarial (Módulo 5 — Nelson)</button>
  <button class="tab-btn" onclick="abrirTab('tab-habeas', this)">🩺 Paso 0: Confidencialidad y Habeas Data (Nelson)</button>
  <button class="tab-btn" onclick="abrirTab('tab-integrado', this)">🚀 Consulta Completa OED: Los 6 Módulos + Glosario</button>
</div>

<div class="container">

  <!-- SALUDO CÁLIDO DEL MÉDICO FINANCIERO AMIGO (BLOQUE 1 MANUAL DE MARCA) -->
  <div class="oed-medico-banner">
    <p id="saludo-medico-top">
      🩺 <strong>Saludo de tu Médico Financiero Amigo (Nelson Angel):</strong>
      <i>"Hagamos una prueba de esfuerzo con 1.000 escenarios futuros para que casarte, tener hijos o tomar un crédito te tome bien preparado y durmiendo tranquilo."</i>
    </p>
    <span class="pill" style="background:#FFF7ED;color:#EA580C;border:1px solid #FED7AA;flex-shrink:0;">🧡 Voz Médico Amigo</span>
  </div>

  <!-- ==================== PESTAÑA 1: MÓDULO 5 ACTUARIAL PARAMÉTRICO (NELSON) ==================== -->
  <div id="tab-mod5" class="tab-content active">
    <div class="grid-sidebar">
      <div class="card">

        <!-- PASO 0: PREGUNTAS INICIALES DE CONFIGURACIÓN (HIJOS, CRÉDITO, BODA) -->
        <div class="wizard-box">
          <h3>🧭 Paso 1: Preguntas Iniciales — ¿Qué desea evaluar hoy?</h3>
          <div class="form-group">
            <label>1️⃣ ¿Tiene hijos o cuántos hijos desea evaluar?</label>
            <div style="display:grid;grid-template-columns:1.6fr 1fr;gap:6px;">
              <select id="sel_numero_hijos" title="Elija cuántos hijos tiene o desea proyectar (0 oculta los cuadros de hijos; 1 a 6 despliega un cuadro por cada hijo)." data-tooltip="Elija cuántos hijos tiene o desea proyectar (0 oculta los cuadros de hijos; 1 a 6 despliega un cuadro por cada hijo)." onchange="seleccionarCantidadHijos(this.value)">
                <option value="0" selected>🚫 No tiene hijos (0 — Ocultar cuadros)</option>
                <option value="1">👦 Sí — 1 Hijo</option>
                <option value="2">👦👧 Sí — 2 Hijos</option>
                <option value="3">👨‍👧‍👦 Sí — 3 Hijos</option>
                <option value="4">👨‍👩‍👧‍👦 Sí — 4 Hijos</option>
                <option value="5">👨‍👩‍👧‍👦 Sí — 5 Hijos</option>
                <option value="6">👨‍👩‍👧‍👦 Sí — 6 Hijos</option>
              </select>
              <input type="number" id="numero_hijos" value="0" min="0" max="6" step="1" title="Escriba el número exacto de hijos a evaluar (de 0 a 6)." data-tooltip="Escriba el número exacto de hijos a evaluar (de 0 a 6)." oninput="sincronizarInputNumeroHijos()">
            </div>
          </div>
          <div class="form-row-2">
            <div class="form-group" style="margin-bottom:2px;">
              <label>2️⃣ ¿Desea un Crédito?</label>
              <select id="desea_credito" title="Elija 'Sí' para activar y simular un crédito bancario o 'No' para dejarlo en $0." data-tooltip="Elija 'Sí' para activar y simular un crédito bancario o 'No' para dejarlo en $0." onchange="ajustarSeccionesPorPreguntas(true)">
                <option value="no" selected>🚫 No ($0)</option>
                <option value="si">🚗 Sí deseo Crédito</option>
              </select>
            </div>
            <div class="form-group" style="margin-bottom:2px;">
              <label>3️⃣ ¿Desea una Boda?</label>
              <select id="desea_boda" title="Elija 'Sí' para simular el costo de casarse y el aporte de su pareja, o 'No' para omitirlo." data-tooltip="Elija 'Sí' para simular el costo de casarse y el aporte de su pareja, o 'No' para omitirlo." onchange="ajustarSeccionesPorPreguntas(true)">
                <option value="no" selected>🚫 No ($0)</option>
                <option value="si">💍 Sí deseo Boda</option>
              </select>
            </div>
          </div>
        </div>

        <!-- PASO 2: FLUJO DE CAJA DEL HOGAR Y TASAS MACRO -->
        <h3>⚙️ Paso 2: Flujo de Caja del Hogar y Tasas Macro</h3>
        <div class="form-row-2">
          <div class="form-group">
            <label>Ingreso Neto Hogar ($)</label>
            <input type="number" id="ingreso_neto_hogar" value="0" step="100000" title="Escriba el ingreso mensual total del hogar libre de descuentos en pesos COP (ej. 9000000)." data-tooltip="Escriba el ingreso mensual total del hogar libre de descuentos en pesos COP (ej. 9000000)." oninput="actualizarDashboard()">
          </div>
          <div class="form-group">
            <label>Excedente Libre Mes ($)</label>
            <input type="number" id="excedente_mensual" value="0" step="50000" title="Dinero libre que le queda cada mes después de pagar gastos básicos (ej. 1500000)." data-tooltip="Dinero libre que le queda cada mes después de pagar gastos básicos (ej. 1500000)." oninput="actualizarDashboard()">
          </div>
        </div>
        <div class="form-row-2">
          <div class="form-group">
            <label>Liquidez Emergencia / Ahorro ($)</label>
            <input type="number" id="liquidez_emergencia" value="0" step="500000" title="Total de ahorros disponibles hoy en cuentas, CDT o fondo de emergencia en pesos COP." data-tooltip="Total de ahorros disponibles hoy en cuentas, CDT o fondo de emergencia en pesos COP." oninput="actualizarDashboard()">
          </div>
          <div class="form-group">
            <label>IPC General Anual (% EA)</label>
            <input type="number" id="ipc_anual_pct" value="0" step="0.5" title="Inflación anual general estimada en porcentaje (ej. 5.5 para 5.5% EA)." data-tooltip="Inflación anual general estimada en porcentaje (ej. 5.5 para 5.5% EA)." oninput="actualizarDashboard()">
          </div>
        </div>
        <div class="form-row-2">
          <div class="form-group">
            <label>Inflación Educativa (% EA)</label>
            <input type="number" id="inflacion_educativa_pct" value="0" step="0.5" title="Aumento anual esperado en pensiones de colegio y matrículas universitarias (% EA, ej. 8.5)." data-tooltip="Aumento anual esperado en pensiones de colegio y matrículas universitarias (% EA, ej. 8.5)." oninput="actualizarDashboard()">
          </div>
          <div class="form-group">
            <label>Tasa Descuento / Rend. (% EA)</label>
            <input type="number" id="tasa_descuento_pct" value="0" step="0.5" title="Rentabilidad anual esperada de sus ahorros/inversiones para descontar flujos futuros (% EA, ej. 9.5)." data-tooltip="Rentabilidad anual esperada de sus ahorros/inversiones para descontar flujos futuros (% EA, ej. 9.5)." oninput="actualizarDashboard()">
          </div>
        </div>

        <!-- SUB-PANEL DINÁMICO: HIJOS (SE OCULTA SI NUMERO_HIJOS == 0, O MUESTRA 1..N CUADROS) -->
        <div class="sub-panel" id="panel-parametros-hijos" style="display:none;">
          <h4 id="titulo-panel-hijos">🎓 Parámetros Educativos por Hijo (Jardín, Primaria, Bachillerato o Universidad)</h4>
          <div class="form-row-2">
            <div class="form-group">
              <label>Perfil Educativo Base</label>
              <select id="nivel_costo_hijo" title="Modo 'Paramétrico Directo' usa exactamente los valores en pesos que escriba; Bajo/Medio/Alto aplica un factor." data-tooltip="Modo 'Paramétrico Directo' usa exactamente los valores en pesos que escriba; Bajo/Medio/Alto aplica un factor." onchange="actualizarDashboard()">
                <option value="Agustiniano_Suba" selected>🎓 Paramétrico Directo ($)</option>
                <option value="Bajo">Colombia Bajo (0.65x)</option>
                <option value="Medio">Colombia Medio (1.0x)</option>
                <option value="Alto">Colombia Alto (1.85x)</option>
              </select>
            </div>
            <div class="form-group">
              <label>Horizonte Cálculo VPA</label>
              <select id="modo_horizonte" title="'Etapa Por Pagar' calcula lo que falta desde hoy; 'Ciclo Completo' proyecta de 0 a 23 años." data-tooltip="'Etapa Por Pagar' calcula lo que falta desde hoy; 'Ciclo Completo' proyecta de 0 a 23 años." onchange="actualizarDashboard()">
                <option value="restante" selected>Etapa Por Pagar (Paramétrico)</option>
                <option value="ciclo_completo">Ciclo Completo (0 a 23a)</option>
              </select>
            </div>
          </div>

          <!-- CUADRO CONFIGURACIÓN HIJO 1 (CUALQUIER ETAPA: JARDÍN, PRIMARIA, BACHILLERATO O UNIVERSIDAD) -->
          <div class="child-input-box child-input-h1" id="box-param-hijo-1">
            <h5>👦 Cuadro Hijo 1 — Seleccionar Etapa (Jardín, Bachillerato o Universidad)</h5>
            <div class="form-row-2">
              <div class="form-group">
                <label>Etapa Educativa Hijo 1</label>
                <select id="etapa_hijo1" title="Seleccione la etapa actual del Hijo 1: Jardín, Primaria, Bachillerato o Universidad." data-tooltip="Seleccione la etapa actual del Hijo 1: Jardín, Primaria, Bachillerato o Universidad." onchange="cambiarEtapaHijo(1)">
                  <option value="jardin">🧒 Jardín / Preescolar</option>
                  <option value="primaria">🏫 Primaria (1° a 5°)</option>
                  <option value="bachillerato" selected>🎒 Bachillerato (6° a 11°)</option>
                  <option value="universidad">🎓 Universidad (Pregrado)</option>
                </select>
              </div>
              <div class="form-group">
                <label>Plantilla Opcional H1</label>
                <select id="grado_agustiniano_h1" title="Elija 'Paramétrico Manual ($0)' para digitar sus propios valores, o cargue una tarifa guía." data-tooltip="Elija 'Paramétrico Manual ($0)' para digitar sus propios valores, o cargue una tarifa guía." onchange="aplicarGradoAgustiniano(1)">
                  <option value="personalizado" selected>✏️ Paramétrico Manual ($0)</option>
                  <option value="jardin_2026">🧒 Jardín ($1.478k | 4a)</option>
                  <option value="transicion_1_2026">🧒 Transición / 1° ($1.464k | 6a)</option>
                  <option value="primaria_2_3_2026">🏫 Primaria 2°-3° ($1.454k | 8a)</option>
                  <option value="cuarto_sexto_2026">🏫 Grados 4°-6° ($1.438k | 10a)</option>
                  <option value="septimo_noveno_2026">🎒 Bachillerato 7°-9° ($1.431k | 12a)</option>
                  <option value="decimo_2026">🎒 Grado 10° ($1.421k | 15a)</option>
                  <option value="once_2026">🎒 Grado 11° ($1.421k | 16a)</option>
                  <option value="univ_sem1">🎓 Univ. 1° Semestre ($13M)</option>
                  <option value="univ_sem6">🎓 Univ. 6° Semestre ($13M)</option>
                  <option value="univ_sem7">🎓 Univ. 7° Semestre ($13M)</option>
                </select>
              </div>
            </div>
            <div class="form-row-2">
              <div class="form-group">
                <label>Edad Actual Hijo 1 (Años)</label>
                <input type="number" id="edad_hijo1" value="0" min="0" max="30" title="Edad actual en años cumplidos del Hijo 1 (ej. 4 jardín, 15 colegio, 20 universidad)." data-tooltip="Edad actual en años cumplidos del Hijo 1 (ej. 4 jardín, 15 colegio, 20 universidad)." oninput="actualizarDashboard()">
              </div>
              <div class="form-group" id="grp-anios-col-h1">
                <label>Años Colegio Restantes H1</label>
                <input type="number" id="anios_colegio_h1" value="0" min="0" max="18" title="Cuántos años de colegio le faltan por cursar al Hijo 1 hasta graduarse de grado 11°." data-tooltip="Cuántos años de colegio le faltan por cursar al Hijo 1 hasta graduarse de grado 11°." oninput="actualizarDashboard()">
              </div>
              <div class="form-group" id="grp-sem-act-h1" style="display:none;">
                <label>Semestre Univ. Actual H1</label>
                <input type="number" id="semestre_actual_h1" value="0" min="0" max="14" title="Número de semestre universitario en el que va actualmente el Hijo 1 (ej. 1 a 10)." data-tooltip="Número de semestre universitario en el que va actualmente el Hijo 1 (ej. 1 a 10)." oninput="actualizarDashboard()">
              </div>
            </div>
            <div class="form-row-2" id="row-col-pension-h1">
              <div class="form-group">
                <label>Pensión Mes H1 ($)</label>
                <input type="number" id="pension_colegio_mes" value="0" step="50000" title="Valor mensual de la pensión del jardín o colegio del Hijo 1 en pesos COP." data-tooltip="Valor mensual de la pensión del jardín o colegio del Hijo 1 en pesos COP." oninput="actualizarDashboard()">
              </div>
              <div class="form-group">
                <label>Matrícula Anual H1 ($)</label>
                <input type="number" id="matricula_anual" value="0" step="50000" title="Valor anual de matrícula y cobros periódicos del colegio del Hijo 1 en pesos COP." data-tooltip="Valor anual de matrícula y cobros periódicos del colegio del Hijo 1 en pesos COP." oninput="actualizarDashboard()">
              </div>
            </div>
            <div class="form-row-2">
              <div class="form-group">
                <label id="lbl-sem-univ-h1">Valor Semestre Univ. H1 ($)</label>
                <input type="number" id="semestre_univ_hoy" value="0" step="500000" title="Costo de un semestre de universidad para el Hijo 1 en pesos COP de hoy (ej. 13000000)." data-tooltip="Costo de un semestre de universidad para el Hijo 1 en pesos COP de hoy (ej. 13000000)." oninput="actualizarDashboard()">
              </div>
              <div class="form-group">
                <label id="lbl-num-sem-h1">N° Semestres Univ. H1</label>
                <input type="number" id="semestres_univ_h1" value="0" min="0" max="16" title="Cantidad de semestres de universidad que cursará o le faltan por pagar al Hijo 1 (ej. 10)." data-tooltip="Cantidad de semestres de universidad que cursará o le faltan por pagar al Hijo 1 (ej. 10)." oninput="actualizarDashboard()">
              </div>
            </div>
            <div class="form-row-2">
              <div class="form-group">
                <label>Ruta / Transp. Mes H1 ($)</label>
                <input type="number" id="transporte_mes" value="0" step="20000" title="Gasto mensual en ruta escolar o transporte del Hijo 1 en pesos COP (0 si no usa ruta)." data-tooltip="Gasto mensual en ruta escolar o transporte del Hijo 1 en pesos COP (0 si no usa ruta)." oninput="actualizarDashboard()">
              </div>
              <div class="form-group">
                <label>Manutención Mes H1 ($)</label>
                <input type="number" id="manutencion_hijo_mes" value="0" step="50000" title="Gasto mensual en alimentación, lonchera, salud y vestuario del Hijo 1 en pesos COP." data-tooltip="Gasto mensual en alimentación, lonchera, salud y vestuario del Hijo 1 en pesos COP." oninput="actualizarDashboard()">
              </div>
            </div>
            <div class="form-group" style="margin-bottom:2px;">
              <label>Otros / Materiales Mes H1 ($)</label>
              <input type="number" id="otros_gastos_mes" value="0" step="25000" title="Gasto mensual en útiles, materiales, cursos o extracurriculares del Hijo 1 en pesos COP." data-tooltip="Gasto mensual en útiles, materiales, cursos o extracurriculares del Hijo 1 en pesos COP." oninput="actualizarDashboard()">
            </div>
          </div>

          <!-- CUADRO CONFIGURACIÓN HIJO 2 (CUALQUIER ETAPA: JARDÍN, PRIMARIA, BACHILLERATO O UNIVERSIDAD) -->
          <div class="child-input-box child-input-h2" id="box-param-hijo-2">
            <h5 style="color:#6a1b9a;">👧 Cuadro Hijo 2 — Seleccionar Etapa (Jardín, Bachillerato o Universidad)</h5>
            <div class="form-row-2">
              <div class="form-group">
                <label>Etapa Educativa Hijo 2</label>
                <select id="etapa_hijo2" title="Seleccione la etapa actual del Hijo 2: Jardín, Primaria, Bachillerato o Universidad." data-tooltip="Seleccione la etapa actual del Hijo 2: Jardín, Primaria, Bachillerato o Universidad." onchange="cambiarEtapaHijo(2)">
                  <option value="jardin">🧒 Jardín / Preescolar</option>
                  <option value="primaria">🏫 Primaria (1° a 5°)</option>
                  <option value="bachillerato">🎒 Bachillerato (6° a 11°)</option>
                  <option value="universidad" selected>🎓 Universidad (Pregrado)</option>
                  <option value="univ_custom">🎓 Universidad (Paramétrico)</option>
                  <option value="colegio_custom">🏫 Colegio (Paramétrico)</option>
                </select>
              </div>
              <div class="form-group">
                <label>Plantilla Opcional H2</label>
                <select id="plantilla_hijo2" title="Elija 'Paramétrico Manual ($0)' para digitar sus propios valores, o cargue una tarifa guía." data-tooltip="Elija 'Paramétrico Manual ($0)' para digitar sus propios valores, o cargue una tarifa guía." onchange="aplicarGradoAgustiniano(2)">
                  <option value="personalizado" selected>✏️ Paramétrico Manual ($0)</option>
                  <option value="jardin_2026">🧒 Jardín ($1.478k | 4a)</option>
                  <option value="transicion_1_2026">🧒 Transición / 1° ($1.464k | 6a)</option>
                  <option value="primaria_2_3_2026">🏫 Primaria 2°-3° ($1.454k | 8a)</option>
                  <option value="cuarto_sexto_2026">🏫 Grados 4°-6° ($1.438k | 10a)</option>
                  <option value="septimo_noveno_2026">🎒 Bachillerato 7°-9° ($1.431k | 12a)</option>
                  <option value="decimo_2026">🎒 Grado 10° ($1.421k | 15a)</option>
                  <option value="once_2026">🎒 Grado 11° ($1.421k | 16a)</option>
                  <option value="univ_sem6">🎓 Univ. 6° Semestre ($13M)</option>
                  <option value="univ_sem7">🎓 Univ. 7° Semestre ($13M)</option>
                </select>
              </div>
            </div>
            <div class="form-row-2">
              <div class="form-group">
                <label>Edad Actual Hijo 2 (Años)</label>
                <input type="number" id="edad_hijo2" value="0" min="0" max="30" title="Edad actual en años cumplidos del Hijo 2 (ej. 4 jardín, 15 colegio, 20 universidad)." data-tooltip="Edad actual en años cumplidos del Hijo 2 (ej. 4 jardín, 15 colegio, 20 universidad)." oninput="actualizarDashboard()">
              </div>
              <div class="form-group" id="grp-anios-col-h2" style="display:none;">
                <label>Años Colegio Restantes H2</label>
                <input type="number" id="anios_colegio_h2" value="0" min="0" max="18" title="Cuántos años de colegio le faltan por cursar al Hijo 2 hasta graduarse de grado 11°." data-tooltip="Cuántos años de colegio le faltan por cursar al Hijo 2 hasta graduarse de grado 11°." oninput="actualizarDashboard()">
              </div>
              <div class="form-group" id="grp-sem-act-h2">
                <label>Semestre Univ. Actual H2</label>
                <input type="number" id="semestre_actual_h2" value="0" min="0" max="14" title="Número de semestre universitario en el que va actualmente el Hijo 2 (ej. 6 o 7)." data-tooltip="Número de semestre universitario en el que va actualmente el Hijo 2 (ej. 6 o 7)." oninput="sincronizarSemestreHijo2()">
              </div>
            </div>
            <div class="form-row-2" id="row-col-pension-h2" style="display:none;">
              <div class="form-group">
                <label>Pensión Colegio Mes H2 ($)</label>
                <input type="number" id="pension_hijo2_mes" value="0" step="50000" title="Valor mensual de la pensión del jardín o colegio del Hijo 2 en pesos COP." data-tooltip="Valor mensual de la pensión del jardín o colegio del Hijo 2 en pesos COP." oninput="actualizarDashboard()">
              </div>
              <div class="form-group">
                <label>Matrícula Colegio Anual H2 ($)</label>
                <input type="number" id="matricula_hijo2_anual" value="0" step="50000" title="Valor anual de matrícula y cobros periódicos del colegio del Hijo 2 en pesos COP." data-tooltip="Valor anual de matrícula y cobros periódicos del colegio del Hijo 2 en pesos COP." oninput="actualizarDashboard()">
              </div>
            </div>
            <div class="form-row-2">
              <div class="form-group">
                <label id="lbl-sem-univ-h2">Valor Semestre Univ. H2 ($)</label>
                <input type="number" id="semestre_univ_h2" value="0" step="500000" title="Costo de un semestre de universidad para el Hijo 2 en pesos COP de hoy (ej. 13000000)." data-tooltip="Costo de un semestre de universidad para el Hijo 2 en pesos COP de hoy (ej. 13000000)." oninput="actualizarDashboard()">
              </div>
              <div class="form-group">
                <label id="lbl-num-sem-h2">Semestres Univ. por Cursar H2</label>
                <input type="number" id="semestres_cursar_h2" value="0" min="0" max="16" title="Cantidad de semestres universitarios que le faltan por cursar y pagar al Hijo 2 (ej. 4 o 5)." data-tooltip="Cantidad de semestres universitarios que le faltan por cursar y pagar al Hijo 2 (ej. 4 o 5)." oninput="actualizarDashboard()">
              </div>
            </div>
            <div class="form-row-2">
              <div class="form-group">
                <label>Ruta / Transp. Mes H2 ($)</label>
                <input type="number" id="ruta_hijo2_mes" value="0" step="20000" title="Gasto mensual en ruta escolar o transporte universitario del Hijo 2 en pesos COP." data-tooltip="Gasto mensual en ruta escolar o transporte universitario del Hijo 2 en pesos COP." oninput="actualizarDashboard()">
              </div>
              <div class="form-group">
                <label>Manutención Mes H2 ($)</label>
                <input type="number" id="manutencion_hijo2_mes" value="0" step="50000" title="Gasto mensual en alimentación, salud y sostenimiento del Hijo 2 en pesos COP." data-tooltip="Gasto mensual en alimentación, salud y sostenimiento del Hijo 2 en pesos COP." oninput="actualizarDashboard()">
              </div>
            </div>
            <div class="form-group" style="margin-bottom:2px;">
              <label>Otros / Materiales Mes H2 ($)</label>
              <input type="number" id="otros_gastos_hijo2_mes" value="0" step="25000" title="Gasto mensual en libros, fotocopias, equipos o actividades del Hijo 2 en pesos COP." data-tooltip="Gasto mensual en libros, fotocopias, equipos o actividades del Hijo 2 en pesos COP." oninput="actualizarDashboard()">
            </div>
          </div>

          <!-- CONTENEDOR DINÁMICO PARA HIJOS 3, 4, 5, 6 -->
          <div id="contenedor-hijos-extra"></div>
        </div>

        <!-- SUB-PANEL DINÁMICO: BODA / UNIÓN MARITAL (SE OCULTA SI DESEA_BODA == NO) -->
        <div class="sub-panel" id="panel-parametros-boda" style="display:none;">
          <h4>💍 Parámetros Boda / Unión Marital</h4>
          <div class="form-row-2">
            <div class="form-group">
              <label>Costo Boda / Evento ($ COP)</label>
              <input type="number" id="costo_boda" value="0" step="500000" title="Presupuesto total estimado para la fiesta, ceremonia y gastos de boda en pesos COP." data-tooltip="Presupuesto total estimado para la fiesta, ceremonia y gastos de boda en pesos COP." oninput="actualizarDashboard()">
            </div>
            <div class="form-group">
              <label>Ingreso Mensual Pareja ($)</label>
              <input type="number" id="ingreso_pareja" value="0" step="250000" title="Ingreso mensual neto que aporta su pareja al hogar en pesos COP." data-tooltip="Ingreso mensual neto que aporta su pareja al hogar en pesos COP." oninput="actualizarDashboard()">
            </div>
          </div>
          <div class="form-row-2">
            <div class="form-group" style="margin-bottom:2px;">
              <label>Plazo Meta Ahorro Boda (m)</label>
              <input type="number" id="plazo_boda_meses" value="0" min="0" max="120" title="Número de meses en los que planea reunir el ahorro para pagar la boda (ej. 12 o 24)." data-tooltip="Número de meses en los que planea reunir el ahorro para pagar la boda (ej. 12 o 24)." oninput="actualizarDashboard()">
            </div>
            <div class="form-group" style="margin-bottom:2px;">
              <label>Sinergia Gastos Pareja (%)</label>
              <input type="number" id="ahorro_sinergia_pct" value="0" step="1" title="Porcentaje de ahorro al compartir vivienda y servicios en pareja (ej. 8 para 8%)." data-tooltip="Porcentaje de ahorro al compartir vivienda y servicios en pareja (ej. 8 para 8%)." oninput="actualizarDashboard()">
            </div>
          </div>
        </div>

        <!-- SUB-PANEL DINÁMICO: CRÉDITO ESTRUCTURAL (+TCO) (SE OCULTA SI DESEA_CREDITO == NO) -->
        <div class="sub-panel" id="panel-parametros-credito" style="display:none;">
          <h4>🚗 Parámetros Crédito Estructural (+TCO)</h4>
          <div class="form-row-2">
            <div class="form-group">
              <label>Monto Crédito ($ COP)</label>
              <input type="number" id="monto_credito" value="0" step="1000000" title="Capital o monto total del préstamo solicitado al banco en pesos COP (ej. 50000000)." data-tooltip="Capital o monto total del préstamo solicitado al banco en pesos COP (ej. 50000000)." oninput="actualizarDashboard()">
            </div>
            <div class="form-group">
              <label>Tasa Interés Crédito (% EA)</label>
              <input type="number" id="tasa_ea_credito" value="0" step="0.5" title="Tasa de interés Efectiva Anual del crédito bancario en porcentaje (% EA, ej. 15.5)." data-tooltip="Tasa de interés Efectiva Anual del crédito bancario en porcentaje (% EA, ej. 15.5)." oninput="actualizarDashboard()">
            </div>
          </div>
          <div class="form-row-2">
            <div class="form-group" style="margin-bottom:2px;">
              <label>Plazo Crédito (Meses)</label>
              <input type="number" id="plazo_credito" value="0" min="0" max="360" step="6" title="Número total de cuotas mensuales para pagar el crédito (ej. 60 meses = 5 años)." data-tooltip="Número total de cuotas mensuales para pagar el crédito (ej. 60 meses = 5 años)." oninput="actualizarDashboard()">
            </div>
            <div class="form-group" style="margin-bottom:2px;">
              <label>Tasa TCO / Seguros (% Mes)</label>
              <input type="number" id="tasa_tco_mensual_pct" value="0" step="0.1" title="Porcentaje mensual adicional por seguros, impuestos y mantenimiento del bien (ej. 0.4)." data-tooltip="Porcentaje mensual adicional por seguros, impuestos y mantenimiento del bien (ej. 0.4)." oninput="actualizarDashboard()">
            </div>
          </div>
        </div>

        <button type="button" id="btn-recalcular" class="btn btn-primary" title="Haga clic para ejecutar todas las fórmulas actuariales y actualizar los cuadros con sus datos." data-tooltip="Haga clic para ejecutar todas las fórmulas actuariales y actualizar los cuadros con sus datos." onclick="actualizarDashboard('ninguna', true)">
          🔄 Ejecutar y Recalcular Modelo Paramétrico
        </button>
        <button type="button" id="btn-limpiar-ceros" class="btn" style="background:#eceff1;color:#37474f;margin-top:6px;" title="Reinicia todas las cajas numéricas a $0 COP y vuelve las preguntas iniciales a su estado base." data-tooltip="Reinicia todas las cajas numéricas a $0 COP y vuelve las preguntas iniciales a su estado base." onclick="ponerTodoEnCero()">
          🧹 Poner Todos los Parámetros en Cero ($0)
        </button>
        <div id="status-calculo" class="status-banner">✅ PRUEBA EXITOSA — Todos los parámetros listos en $0 COP</div>
      </div>

      <div>
        <!-- BLOQUE 3 MANUAL DE MARCA: DIAGNÓSTICO DEL MÉDICO AMIGO + BURBUJAS (?) + RECETA DEL MES -->
        <div id="box-diagnostico-medico-oed"></div>

        <!-- SECCIÓN SUPERIOR DINÁMICA: CUADROS POR HIJO + CONSOLIDADO (SE OCULTA SI NUMERO_HIJOS == 0) -->
        <div id="seccion-cuadros-hijos" style="display:none;">
          <div class="section-label">
            <span id="lbl-titulo-desglose-hijos">🎓 Desglose Separado por Hijo y Cifra Consolidada Familiar — Calculadora Paramétrica OED</span>
            <span id="lbl-sub-desglose-hijos" style="font-size:0.78rem;color:var(--muted);font-weight:600;">Hijos Individuales | Consolidado Total</span>
          </div>
          <div class="children-grid" id="grid-hijos-detalle"></div>
        </div>

        <!-- SECCIÓN COMPARATIVA DE LAS DECISIONES VITALES ACTIVAS -->
        <div class="section-label" style="margin-top:4px;">
          <span>⚖️ Comparativa de Viabilidad de las Decisiones de Vida (Módulo 5 — Simulación Monte Carlo)</span>
        </div>
        <div class="kpi-row" id="kpis-decisiones"></div>

        <!-- BLOQUE 4 MANUAL DE MARCA: GRÁFICAS INTERACTIVAS CON PALETA OFICIAL DEL CONSULTORIO -->
        <div class="card" id="card-chart-hijo" style="display:none;">
          <h3 id="titulo-curva-hijo">📈 1. Curva Actuarial de Costos Educativos por Hijo y Consolidado</h3>
          <div id="chart-hijo" style="height:410px;"></div>
        </div>

        <div class="charts-2col">
          <div class="card">
            <h3>🎲 2. Simulación Monte Carlo (1.000 Escenarios de Flujo Neto)</h3>
            <div id="chart-mc" style="height:380px;"></div>
          </div>
          <div class="card">
            <h3>📉 3. Curva de Fragilidad Actuarial (Excedente vs. Solvencia)</h3>
            <div id="chart-sens" style="height:380px;"></div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ==================== PESTAÑA 2: HABEAS DATA (NELSON) ==================== -->
  <div id="tab-habeas" class="tab-content">
    <div class="grid-sidebar">
      <div class="card">
        <h3>🔐 Control Local Ley 1581 de 2012</h3>
        <div class="legal-box" id="texto-ley1581"></div>
        <div class="form-group">
          <label>Documento / Identificador del Titular (PII)</label>
          <input type="text" id="usuario_id" value="CC_1020304050_NELSON_DEMO" title="Escriba su documento o alias para generar la huella criptográfica local (nunca sale de su PC)." data-tooltip="Escriba su documento o alias para generar la huella criptográfica local (nunca sale de su PC)." oninput="actualizarDashboard()">
        </div>
        <div class="form-group">
          <label>
            <input type="checkbox" id="acepta_habeas" checked title="Marque para autorizar el tratamiento 100% local de sus datos (Ley 1581/2012)." data-tooltip="Marque para autorizar el tratamiento 100% local de sus datos (Ley 1581/2012)." onchange="actualizarDashboard()" style="width:auto;margin-right:6px;">
            Autorizo tratamiento 100% local (Ley 1581/2012)
          </label>
        </div>
        <button type="button" class="btn btn-success" title="Cifra con AES-Fernet y guarda su perfil localmente en un archivo .oed." data-tooltip="Cifra con AES-Fernet y guarda su perfil localmente en un archivo .oed." onclick="actualizarDashboard('guardar', true)">💾 Cifrar y Guardar Perfil en Disco (.oed)</button>
        <button type="button" class="btn btn-danger" title="Elimina de forma segura e irreversible el archivo .oed del disco local." data-tooltip="Elimina de forma segura e irreversible el archivo .oed del disco local." onclick="actualizarDashboard('olvido', true)">🗑️ Ejercer Derecho al Olvido (Art. 8 Ley 1581)</button>

        <hr style="border:0;border-top:1px solid var(--border);margin:16px 0;">
        <h3>⚖️ Calculadora Datacrédito (Ley 1266/2008 & Ley 2157/2021)</h3>
        <div class="form-group">
          <label>Meses en Mora antes del Pago: <span id="lbl-mora" style="color:var(--primary);font-weight:800;">0</span> meses</label>
          <input type="range" id="meses_mora" min="0" max="36" value="0" title="Deslice para elegir cuántos meses estuvo en mora la deuda antes de pagarla." data-tooltip="Deslice para elegir cuántos meses estuvo en mora la deuda antes de pagarla." oninput="document.getElementById('lbl-mora').innerText=this.value; actualizarDashboard()">
        </div>
        <div class="form-group">
          <label>
            <input type="checkbox" id="obligacion_pagada" checked title="Marque si ya pagó la obligación para calcular los meses de permanencia del reporte." data-tooltip="Marque si ya pagó la obligación para calcular los meses de permanencia del reporte." onchange="actualizarDashboard()" style="width:auto;margin-right:6px;">
            ¿Obligación ya pagada / Paz y Salvo? (Ley 2157/2021)
          </label>
        </div>
      </div>

      <div>
        <div class="card">
          <h3>📋 Auditoría Criptográfica y Estado en Disco Local</h3>
          <div id="auditoria-habeas"></div>
          <div class="code-box" id="estado-disco-box"></div>
        </div>
        <div class="card">
          <h3>📊 Curva Legal de Permanencia del Reporte Negativo Post-Pago (Ley 1266/2008 y Ley 2157/2021)</h3>
          <div id="chart-habeas" style="height:400px;"></div>
        </div>
      </div>
    </div>
  </div>

  <!-- ==================== PESTAÑA 3: CASO MAESTRO 6 MÓDULOS ==================== -->
  <div id="tab-integrado" class="tab-content">
    <div class="card">
      <h3>🔗 El Caso de Vida OED: Pipeline Integrado de los 6 Módulos en Paralelo</h3>
      <p style="color:var(--muted);margin-top:0;">
        Así se conectan las salidas de tus compañeros con tu <strong>Módulo 5 (Nelson Angel)</strong> y tu capa transversal de <strong>Gobierno de Datos</strong>:
      </p>
      <div class="kpi-row" id="kpis-6-modulos"></div>
    </div>
  </div>

  <!-- ==================== BLOQUE 5 MANUAL DE MARCA: DICCIONARIO DEL MÉDICO AMIGO ==================== -->
  <div class="card" id="bloque-glosario-oed" style="margin-top:18px;border-top:4px solid #0F294A;">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:10px;">
      <h3 style="margin:0;">🩺 ¿Alguna palabra te sonó a chino? Diccionario del Médico Financiero Amigo (5 Familias OED)</h3>
      <input type="text" id="buscador-glosario-oed" placeholder="🔍 Buscar sigla o concepto (ej. EA, IPC, Monte Carlo, Habeas Data, UVR, Fogafín)..."
             title="Escriba cualquier sigla o término para ver su explicación sencilla y ejemplo en pesos."
             data-tooltip="Escriba cualquier sigla o término para ver su explicación sencilla y ejemplo en pesos."
             style="width:360px;max-width:100%;padding:7px 11px;border:1px solid #CBD5E1;border-radius:8px;font-size:0.84rem;"
             oninput="filtrarGlosarioOED()">
    </div>
    <div id="pills-glosario-oed" style="margin-bottom:10px;"></div>
    <div id="detalle-glosario-oed"></div>
  </div>

</div>

<script>
const TARIFAS_AGUSTINIANO = {
  jardin_2026:         { matricula: 1890000, pension: 1478000, edad: 4,  anios_col: 13, etapa: 'jardin' },
  transicion_1_2026:   { matricula: 1860000, pension: 1464000, edad: 6,  anios_col: 11, etapa: 'jardin' },
  primaria_2_3_2026:   { matricula: 1845000, pension: 1454000, edad: 8,  anios_col: 9,  etapa: 'primaria' },
  cuarto_sexto_2026:   { matricula: 1825000, pension: 1438000, edad: 10, anios_col: 7,  etapa: 'primaria' },
  septimo_noveno_2026: { matricula: 1815000, pension: 1431000, edad: 12, anios_col: 5,  etapa: 'bachillerato' },
  decimo_2026:         { matricula: 1800000, pension: 1421000, edad: 15, anios_col: 2,  etapa: 'bachillerato' },
  once_2026:           { matricula: 1800000, pension: 1421000, edad: 16, anios_col: 1,  etapa: 'bachillerato' },
  historico_base:      { matricula: 1051500, pension: 946300,  edad: 12, anios_col: 5,  etapa: 'bachillerato' },
  univ_sem1:           { semestre_actual: 1, semestres_cursar: 10, semestre_univ: 13000000, edad: 18, etapa: 'universidad' },
  univ_sem6:           { semestre_actual: 6, semestres_cursar: 5,  semestre_univ: 13000000, edad: 20, etapa: 'universidad' },
  univ_sem7:           { semestre_actual: 7, semestres_cursar: 4,  semestre_univ: 13000000, edad: 20, etapa: 'universidad' }
};

/* PALETA OFICIAL DE GRÁFICAS DEL CONSULTORIO OED (src/oed_design_system.py) */
const COLORES_HIJOS = ['#1D4ED8', '#EA580C', '#15803D', '#7C3AED', '#DC2626', '#475569'];
const ICONOS_HIJOS = ['👦', '👧', '🧒', '👶', '🧑', '🎓'];

function crearHtmlHijoExtra(i) {
  const colorH = COLORES_HIJOS[(i - 1) % COLORES_HIJOS.length];
  const iconoH = ICONOS_HIJOS[(i - 1) % ICONOS_HIJOS.length];
  return `
    <div class="child-input-box child-input-h${i}" id="box-param-hijo-${i}" style="display:none;">
      <h5 style="color:${colorH};">${iconoH} Cuadro Hijo ${i} — Seleccionar Etapa (Jardín, Bachillerato o Universidad)</h5>
      <div class="form-row-2">
        <div class="form-group">
          <label>Etapa Educativa Hijo ${i}</label>
          <select id="etapa_hijo${i}" title="Seleccione la etapa actual del Hijo ${i}: Jardín, Primaria, Bachillerato o Universidad." data-tooltip="Seleccione la etapa actual del Hijo ${i}: Jardín, Primaria, Bachillerato o Universidad." onchange="cambiarEtapaHijo(${i})">
            <option value="jardin">🧒 Jardín / Preescolar</option>
            <option value="primaria">🏫 Primaria (1° a 5°)</option>
            <option value="bachillerato" selected>🎒 Bachillerato (6° a 11°)</option>
            <option value="universidad">🎓 Universidad (Pregrado)</option>
          </select>
        </div>
        <div class="form-group">
          <label>Plantilla Opcional H${i}</label>
          <select id="plantilla_hijo${i}" title="Elija 'Paramétrico Manual ($0)' para digitar sus propios valores del Hijo ${i}, o cargue una tarifa guía." data-tooltip="Elija 'Paramétrico Manual ($0)' para digitar sus propios valores del Hijo ${i}, o cargue una tarifa guía." onchange="aplicarGradoAgustiniano(${i})">
            <option value="personalizado" selected>✏️ Paramétrico Manual ($0)</option>
            <option value="jardin_2026">🧒 Jardín ($1.478k | 4a)</option>
            <option value="transicion_1_2026">🧒 Transición / 1° ($1.464k | 6a)</option>
            <option value="primaria_2_3_2026">🏫 Primaria 2°-3° ($1.454k | 8a)</option>
            <option value="cuarto_sexto_2026">🏫 Grados 4°-6° ($1.438k | 10a)</option>
            <option value="septimo_noveno_2026">🎒 Bachillerato 7°-9° ($1.431k | 12a)</option>
            <option value="decimo_2026">🎒 Grado 10° ($1.421k | 15a)</option>
            <option value="once_2026">🎒 Grado 11° ($1.421k | 16a)</option>
            <option value="univ_sem1">🎓 Univ. 1° Semestre ($13M)</option>
            <option value="univ_sem6">🎓 Univ. 6° Semestre ($13M)</option>
            <option value="univ_sem7">🎓 Univ. 7° Semestre ($13M)</option>
          </select>
        </div>
      </div>
      <div class="form-row-2">
        <div class="form-group">
          <label>Edad Actual Hijo ${i} (Años)</label>
          <input type="number" id="edad_hijo${i}" value="0" min="0" max="30" title="Edad actual en años cumplidos del Hijo ${i} (ej. 4 jardín, 15 colegio, 20 universidad)." data-tooltip="Edad actual en años cumplidos del Hijo ${i} (ej. 4 jardín, 15 colegio, 20 universidad)." oninput="actualizarDashboard()">
        </div>
        <div class="form-group" id="grp-anios-col-h${i}">
          <label>Años Colegio Restantes H${i}</label>
          <input type="number" id="anios_colegio_h${i}" value="0" min="0" max="18" title="Cuántos años de colegio le faltan por cursar al Hijo ${i} hasta grado 11°." data-tooltip="Cuántos años de colegio le faltan por cursar al Hijo ${i} hasta grado 11°." oninput="actualizarDashboard()">
        </div>
        <div class="form-group" id="grp-sem-act-h${i}" style="display:none;">
          <label>Semestre Univ. Actual H${i}</label>
          <input type="number" id="semestre_actual_h${i}" value="0" min="0" max="14" title="Número de semestre universitario en el que va actualmente el Hijo ${i} (ej. 1 a 10)." data-tooltip="Número de semestre universitario en el que va actualmente el Hijo ${i} (ej. 1 a 10)." oninput="actualizarDashboard()">
        </div>
      </div>
      <div class="form-row-2" id="row-col-pension-h${i}">
        <div class="form-group">
          <label>Pensión Colegio Mes H${i} ($)</label>
          <input type="number" id="pension_hijo${i}_mes" value="0" step="50000" title="Valor mensual de la pensión del jardín o colegio del Hijo ${i} en pesos COP." data-tooltip="Valor mensual de la pensión del jardín o colegio del Hijo ${i} en pesos COP." oninput="actualizarDashboard()">
        </div>
        <div class="form-group">
          <label>Matrícula Colegio Anual H${i} ($)</label>
          <input type="number" id="matricula_hijo${i}_anual" value="0" step="50000" title="Valor anual de matrícula y cobros periódicos del colegio del Hijo ${i} en pesos COP." data-tooltip="Valor anual de matrícula y cobros periódicos del colegio del Hijo ${i} en pesos COP." oninput="actualizarDashboard()">
        </div>
      </div>
      <div class="form-row-2">
        <div class="form-group">
          <label id="lbl-sem-univ-h${i}">Valor Semestre Univ. H${i} ($)</label>
          <input type="number" id="semestre_univ_h${i}" value="0" step="500000" title="Costo de un semestre de universidad para el Hijo ${i} en pesos COP de hoy (ej. 13000000)." data-tooltip="Costo de un semestre de universidad para el Hijo ${i} en pesos COP de hoy (ej. 13000000)." oninput="actualizarDashboard()">
        </div>
        <div class="form-group">
          <label id="lbl-num-sem-h${i}">N° Semestres Univ. H${i}</label>
          <input type="number" id="semestres_cursar_h${i}" value="0" min="0" max="16" title="Cantidad de semestres de universidad que cursará o le faltan por pagar al Hijo ${i} (ej. 10)." data-tooltip="Cantidad de semestres de universidad que cursará o le faltan por pagar al Hijo ${i} (ej. 10)." oninput="actualizarDashboard()">
        </div>
      </div>
      <div class="form-row-2">
        <div class="form-group">
          <label>Ruta / Transp. Mes H${i} ($)</label>
          <input type="number" id="ruta_hijo${i}_mes" value="0" step="20000" title="Gasto mensual en ruta escolar o transporte del Hijo ${i} en pesos COP (0 si no usa ruta)." data-tooltip="Gasto mensual en ruta escolar o transporte del Hijo ${i} en pesos COP (0 si no usa ruta)." oninput="actualizarDashboard()">
        </div>
        <div class="form-group">
          <label>Manutención Mes H${i} ($)</label>
          <input type="number" id="manutencion_hijo${i}_mes" value="0" step="50000" title="Gasto mensual en alimentación, lonchera, salud y vestuario del Hijo ${i} en pesos COP." data-tooltip="Gasto mensual en alimentación, lonchera, salud y vestuario del Hijo ${i} en pesos COP." oninput="actualizarDashboard()">
        </div>
      </div>
      <div class="form-group" style="margin-bottom:2px;">
        <label>Otros / Materiales Mes H${i} ($)</label>
        <input type="number" id="otros_gastos_hijo${i}_mes" value="0" step="25000" title="Gasto mensual en útiles, materiales o actividades extracurriculares del Hijo ${i} en pesos COP." data-tooltip="Gasto mensual en útiles, materiales o actividades extracurriculares del Hijo ${i} en pesos COP." oninput="actualizarDashboard()">
      </div>
    </div>
  `;
}

function inicializarCajasHijosExtra() {
  const cont = document.getElementById('contenedor-hijos-extra');
  if (cont && cont.innerHTML.trim() === '') {
    let htmlExtra = '';
    for (let i = 3; i <= 6; i++) {
      htmlExtra += crearHtmlHijoExtra(i);
    }
    cont.innerHTML = htmlExtra;
  }
}

function seleccionarCantidadHijos(val) {
  const n = Math.max(0, Math.min(6, parseInt(val || '0', 10) || 0));
  document.getElementById('numero_hijos').value = n;
  ajustarSeccionesPorPreguntas(true);
}

function sincronizarInputNumeroHijos() {
  const n = Math.max(0, Math.min(6, Math.round(numVal('numero_hijos', 0))));
  const sel = document.getElementById('sel_numero_hijos');
  if (sel) sel.value = String(n);
  ajustarSeccionesPorPreguntas(true);
}

function cambiarEtapaHijo(numHijo) {
  const elEtapa = document.getElementById('etapa_hijo' + numHijo);
  if (!elEtapa) return;
  const val = elEtapa.value;
  const esUniv = val.startsWith('univ') || val === 'universidad';

  const grpCol = document.getElementById('grp-anios-col-h' + numHijo);
  const grpSemAct = document.getElementById('grp-sem-act-h' + numHijo);
  const rowPension = document.getElementById('row-col-pension-h' + numHijo);
  const lblSemUniv = document.getElementById('lbl-sem-univ-h' + numHijo);
  const lblNumSem = document.getElementById('lbl-num-sem-h' + numHijo);

  if (grpCol) grpCol.style.display = esUniv ? 'none' : 'block';
  if (grpSemAct) grpSemAct.style.display = esUniv ? 'block' : 'none';
  if (rowPension) rowPension.style.display = esUniv ? 'none' : 'grid';

  if (esUniv) {
    if (numHijo === 1) {
      document.getElementById('pension_colegio_mes').value = '0';
      document.getElementById('matricula_anual').value = '0';
    } else {
      const pEl = document.getElementById(`pension_hijo${numHijo}_mes`);
      const mEl = document.getElementById(`matricula_hijo${numHijo}_anual`);
      if (pEl) pEl.value = '0';
      if (mEl) mEl.value = '0';
    }
    if (lblSemUniv) lblSemUniv.innerText = `Valor Semestre Univ. H${numHijo} ($)`;
    if (lblNumSem) lblNumSem.innerText = `Semestres Univ. por Cursar H${numHijo}`;
  } else {
    if (lblSemUniv) lblSemUniv.innerText = `Semestre Univ. Proy. H${numHijo} ($)`;
    if (lblNumSem) lblNumSem.innerText = `N° Semestres Univ. Proy. H${numHijo}`;
  }
  actualizarDashboard();
}

function ajustarSeccionesPorPreguntas(dispararCalculo = true) {
  inicializarCajasHijosExtra();
  const nHijos = Math.max(0, Math.min(6, Math.round(numVal('numero_hijos', 0))));
  const selNHijos = document.getElementById('sel_numero_hijos');
  if (selNHijos && selNHijos.value !== String(nHijos)) {
    selNHijos.value = String(nHijos);
  }

  const panelHijos = document.getElementById('panel-parametros-hijos');
  if (panelHijos) {
    panelHijos.style.display = nHijos > 0 ? 'block' : 'none';
  }
  const tituloPanelHijos = document.getElementById('titulo-panel-hijos');
  if (tituloPanelHijos && nHijos > 0) {
    tituloPanelHijos.innerText = `🎓 Parámetros Educativos (${nHijos} ${nHijos === 1 ? 'Hijo Activo' : 'Hijos Activos'}: Jardín, Bachillerato o Universidad)`;
  }

  for (let i = 1; i <= 6; i++) {
    const box = document.getElementById('box-param-hijo-' + i);
    if (box) {
      box.style.display = i <= nHijos ? 'block' : 'none';
    }
  }

  const deseaBoda = (document.getElementById('desea_boda')?.value || 'no') === 'si';
  const panelBoda = document.getElementById('panel-parametros-boda');
  if (panelBoda) {
    panelBoda.style.display = deseaBoda ? 'block' : 'none';
  }
  if (!deseaBoda) {
    ['costo_boda', 'ingreso_pareja', 'plazo_boda_meses', 'ahorro_sinergia_pct'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.value = '0';
    });
  }

  const deseaCredito = (document.getElementById('desea_credito')?.value || 'no') === 'si';
  const panelCredito = document.getElementById('panel-parametros-credito');
  if (panelCredito) {
    panelCredito.style.display = deseaCredito ? 'block' : 'none';
  }
  if (!deseaCredito) {
    ['monto_credito', 'tasa_ea_credito', 'plazo_credito', 'tasa_tco_mensual_pct'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.value = '0';
    });
  }

  if (dispararCalculo) {
    actualizarDashboard();
  }
}

function ponerTodoEnCero() {
  inicializarCajasHijosExtra();
  document.getElementById('sel_numero_hijos').value = '0';
  document.getElementById('numero_hijos').value = '0';
  document.getElementById('desea_boda').value = 'no';
  document.getElementById('desea_credito').value = 'no';

  const idsCero = [
    'ingreso_neto_hogar', 'excedente_mensual', 'liquidez_emergencia', 'numero_hijos',
    'inflacion_educativa_pct', 'tasa_descuento_pct', 'ipc_anual_pct',
    'edad_hijo1', 'anios_colegio_h1', 'semestre_actual_h1', 'pension_colegio_mes', 'matricula_anual',
    'transporte_mes', 'manutencion_hijo_mes', 'otros_gastos_mes',
    'semestre_univ_hoy', 'semestres_univ_h1',
    'edad_hijo2', 'anios_colegio_h2', 'semestre_actual_h2', 'semestres_cursar_h2', 'semestre_univ_h2',
    'pension_hijo2_mes', 'matricula_hijo2_anual', 'ruta_hijo2_mes',
    'manutencion_hijo2_mes', 'otros_gastos_hijo2_mes',
    'costo_boda', 'ingreso_pareja', 'plazo_boda_meses', 'ahorro_sinergia_pct',
    'monto_credito', 'tasa_ea_credito', 'plazo_credito', 'tasa_tco_mensual_pct',
    'meses_mora'
  ];
  for (let i = 3; i <= 6; i++) {
    idsCero.push(
      `edad_hijo${i}`, `anios_colegio_h${i}`, `semestre_actual_h${i}`,
      `pension_hijo${i}_mes`, `matricula_hijo${i}_anual`, `semestre_univ_h${i}`,
      `semestres_cursar_h${i}`, `ruta_hijo${i}_mes`, `manutencion_hijo${i}_mes`, `otros_gastos_hijo${i}_mes`
    );
  }
  idsCero.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '0';
  });
  const lblMora = document.getElementById('lbl-mora');
  if (lblMora) lblMora.innerText = '0';
  document.getElementById('grado_agustiniano_h1').value = 'personalizado';
  if (document.getElementById('plantilla_hijo2')) document.getElementById('plantilla_hijo2').value = 'personalizado';
  ajustarSeccionesPorPreguntas(false);
  actualizarDashboard('ninguna', true);
}

function aplicarGradoAgustiniano(numHijo = 1) {
  const idSelect = numHijo === 1 ? 'grado_agustiniano_h1' : `plantilla_hijo${numHijo}`;
  const selEl = document.getElementById(idSelect) || document.getElementById('etapa_hijo2');
  if (!selEl) return;
  const clave = selEl.value;
  if (clave === 'personalizado' || clave === 'univ_custom' || clave === 'colegio_custom') {
    cambiarEtapaHijo(numHijo);
    return;
  }
  const info = TARIFAS_AGUSTINIANO[clave];
  if (!info) {
    cambiarEtapaHijo(numHijo);
    return;
  }
  if (numVal('numero_hijos', 0) < numHijo) {
    document.getElementById('numero_hijos').value = numHijo;
    ajustarSeccionesPorPreguntas(false);
  }
  const elEtapa = document.getElementById('etapa_hijo' + numHijo);
  if (elEtapa) elEtapa.value = info.etapa;
  cambiarEtapaHijo(numHijo);

  if (info.etapa === 'universidad') {
    document.getElementById(`edad_hijo${numHijo}`).value = info.edad;
    document.getElementById(`semestre_actual_h${numHijo}`).value = info.semestre_actual;
    if (numHijo === 1) {
      document.getElementById('semestre_univ_hoy').value = info.semestre_univ;
      document.getElementById('semestres_univ_h1').value = info.semestres_cursar;
    } else {
      document.getElementById(`semestre_univ_h${numHijo}`).value = info.semestre_univ;
      document.getElementById(`semestres_cursar_h${numHijo}`).value = info.semestres_cursar;
    }
  } else {
    document.getElementById(`edad_hijo${numHijo}`).value = info.edad;
    document.getElementById(`anios_colegio_h${numHijo}`).value = info.anios_col;
    if (numHijo === 1) {
      document.getElementById('pension_colegio_mes').value = info.pension;
      document.getElementById('matricula_anual').value = info.matricula;
    } else {
      document.getElementById(`pension_hijo${numHijo}_mes`).value = info.pension;
      document.getElementById(`matricula_hijo${numHijo}_anual`).value = info.matricula;
    }
  }
  document.getElementById('nivel_costo_hijo').value = 'Agustiniano_Suba';
  actualizarDashboard('ninguna', true);
}

function sincronizarSemestreHijo2() {
  const s = Math.round(numVal('semestre_actual_h2', 0));
  if (s >= 1 && s <= 10 && numVal('semestres_cursar_h2', 0) === 0) {
    document.getElementById('semestres_cursar_h2').value = Math.max(0, 10 - s + 1);
  }
  actualizarDashboard();
}

function fmtCOP(v) {
  return '$' + Math.round(v || 0).toLocaleString('es-CO') + ' COP';
}

function numVal(id, defVal = 0) {
  const el = document.getElementById(id);
  if (!el || el.value === '') return defVal;
  const parsed = parseFloat(String(el.value).replace(',', '.'));
  return isNaN(parsed) ? defVal : parsed;
}

function abrirTab(tabId, btn) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
  document.getElementById(tabId).classList.add('active');
  btn.classList.add('active');

  const pill0 = document.getElementById('pill-paso-0');
  const pill6 = document.getElementById('pill-paso-6');
  const saludoEl = document.getElementById('saludo-medico-top');
  if (tabId === 'tab-habeas') {
    if (pill0) pill0.classList.add('oed-step-active');
    if (pill6) pill6.classList.remove('oed-step-active');
    if (saludoEl) {
      saludoEl.innerHTML = '🩺 <strong>Paso 0 — Bienvenida al Consultorio y Confidencialidad (Nelson + Camilo):</strong> <i>"Igual que en una historia clínica médica, tus datos son privados, se quedan cifrados en tu equipo y nadie más los ve."</i>';
    }
  } else {
    if (pill0) pill0.classList.remove('oed-step-active');
    if (pill6) pill6.classList.add('oed-step-active');
    if (saludoEl) {
      saludoEl.innerHTML = '🛡️ <strong>Paso 6 — Prueba de Esfuerzo para tus Grandes Planes (Nelson Angel):</strong> <i>"Hagamos una prueba de esfuerzo con 1.000 escenarios futuros para que casarte, tener hijos o estudiar te tome bien preparado."</i>';
    }
  }

  setTimeout(() => {
    window.dispatchEvent(new Event('resize'));
    ['chart-hijo', 'chart-mc', 'chart-sens', 'chart-habeas'].forEach(id => {
      const el = document.getElementById(id);
      if (el && el.offsetParent !== null && window.Plotly) {
        Plotly.Plots.resize(el);
      }
    });
  }, 50);
}

function construirListaHijosPayload(nHijos) {
  const lista = [];
  for (let i = 1; i <= nHijos; i++) {
    if (i === 1) {
      lista.push({
        edad: Math.round(numVal('edad_hijo1', 0)),
        etapa: document.getElementById('etapa_hijo1')?.value || 'bachillerato',
        plantilla: document.getElementById('grado_agustiniano_h1')?.value || 'personalizado',
        anios_colegio: Math.round(numVal('anios_colegio_h1', 0)),
        semestre_actual: Math.round(numVal('semestre_actual_h1', 0)),
        pension_mes: numVal('pension_colegio_mes', 0),
        matricula_anual: numVal('matricula_anual', 0),
        ruta_mes: numVal('transporte_mes', 0),
        manutencion_mes: numVal('manutencion_hijo_mes', 0),
        otros_gastos_mes: numVal('otros_gastos_mes', 0),
        semestre_univ: numVal('semestre_univ_hoy', 0),
        semestres_univ: Math.round(numVal('semestres_univ_h1', 0)),
        semestres_cursar: Math.round(numVal('semestres_univ_h1', 0))
      });
    } else if (i === 2) {
      lista.push({
        edad: Math.round(numVal('edad_hijo2', 0)),
        etapa: document.getElementById('etapa_hijo2')?.value || 'universidad',
        plantilla: document.getElementById('plantilla_hijo2')?.value || 'personalizado',
        anios_colegio: Math.round(numVal('anios_colegio_h2', 0)),
        semestre_actual: Math.round(numVal('semestre_actual_h2', 0)),
        pension_mes: numVal('pension_hijo2_mes', 0),
        matricula_anual: numVal('matricula_hijo2_anual', 0),
        ruta_mes: numVal('ruta_hijo2_mes', 0),
        manutencion_mes: numVal('manutencion_hijo2_mes', 0),
        otros_gastos_mes: numVal('otros_gastos_hijo2_mes', 0),
        semestre_univ: numVal('semestre_univ_h2', 0),
        semestres_univ: Math.round(numVal('semestres_cursar_h2', 0)),
        semestres_cursar: Math.round(numVal('semestres_cursar_h2', 0))
      });
    } else {
      lista.push({
        edad: Math.round(numVal(`edad_hijo${i}`, 0)),
        etapa: document.getElementById(`etapa_hijo${i}`)?.value || 'bachillerato',
        plantilla: document.getElementById(`plantilla_hijo${i}`)?.value || 'personalizado',
        anios_colegio: Math.round(numVal(`anios_colegio_h${i}`, 0)),
        semestre_actual: Math.round(numVal(`semestre_actual_h${i}`, 0)),
        pension_mes: numVal(`pension_hijo${i}_mes`, 0),
        matricula_anual: numVal(`matricula_hijo${i}_anual`, 0),
        ruta_mes: numVal(`ruta_hijo${i}_mes`, 0),
        manutencion_mes: numVal(`manutencion_hijo${i}_mes`, 0),
        otros_gastos_mes: numVal(`otros_gastos_hijo${i}_mes`, 0),
        semestre_univ: numVal(`semestre_univ_h${i}`, 0),
        semestres_univ: Math.round(numVal(`semestres_cursar_h${i}`, 0)),
        semestres_cursar: Math.round(numVal(`semestres_cursar_h${i}`, 0))
      });
    }
  }
  return lista;
}

async function actualizarDashboard(accionDisco = 'ninguna', esClickBoton = false) {
  inicializarCajasHijosExtra();
  const btn = document.getElementById('btn-recalcular');
  const statusEl = document.getElementById('status-calculo');
  if (esClickBoton && btn) {
    btn.innerText = '⏳ Ejecutando cálculos paramétricos...';
    btn.style.background = '#0f4c81';
  }

  const nHijos = Math.max(0, Math.min(6, Math.round(numVal('numero_hijos', 0))));
  const deseaBoda = (document.getElementById('desea_boda')?.value || 'no') === 'si';
  const deseaCredito = (document.getElementById('desea_credito')?.value || 'no') === 'si';
  const obPagadaEl = document.getElementById('obligacion_pagada');

  const payload = {
    usuario_id: document.getElementById('usuario_id').value,
    acepta_habeas: document.getElementById('acepta_habeas').checked,
    meses_mora: Math.round(numVal('meses_mora', 0)),
    obligacion_pagada: obPagadaEl ? obPagadaEl.checked : true,
    accion_disco: accionDisco,
    ingreso_neto_hogar: numVal('ingreso_neto_hogar', 0),
    excedente_mensual: numVal('excedente_mensual', 0),
    liquidez_emergencia: numVal('liquidez_emergencia', 0),
    numero_hijos: nHijos,
    desea_boda: deseaBoda,
    desea_credito: deseaCredito,
    hijos_lista: construirListaHijosPayload(nHijos),
    inflacion_educativa_pct: numVal('inflacion_educativa_pct', 0),
    tasa_descuento_pct: numVal('tasa_descuento_pct', 0),
    ipc_anual_pct: numVal('ipc_anual_pct', 0),
    nivel_costo_hijo: document.getElementById('nivel_costo_hijo').value,
    modo_horizonte: document.getElementById('modo_horizonte').value,
    grado_agustiniano_h1: document.getElementById('grado_agustiniano_h1').value,
    etapa_hijo1: document.getElementById('etapa_hijo1')?.value || 'bachillerato',
    edad_hijo1: Math.round(numVal('edad_hijo1', 0)),
    anios_colegio_h1: Math.round(numVal('anios_colegio_h1', 0)),
    pension_colegio_mes: numVal('pension_colegio_mes', 0),
    matricula_anual: numVal('matricula_anual', 0),
    transporte_mes: numVal('transporte_mes', 0),
    manutencion_hijo_mes: numVal('manutencion_hijo_mes', 0),
    otros_gastos_mes: numVal('otros_gastos_mes', 0),
    semestre_univ_hoy: numVal('semestre_univ_hoy', 0),
    semestres_univ_h1: Math.round(numVal('semestres_univ_h1', 0)),
    etapa_hijo2: document.getElementById('etapa_hijo2').value,
    edad_hijo2: Math.round(numVal('edad_hijo2', 0)),
    semestre_actual_h2: Math.round(numVal('semestre_actual_h2', 0)),
    semestres_cursar_h2: Math.round(numVal('semestres_cursar_h2', 0)),
    semestre_univ_h2: numVal('semestre_univ_h2', 0),
    pension_hijo2_mes: numVal('pension_hijo2_mes', 0),
    matricula_hijo2_anual: numVal('matricula_hijo2_anual', 0),
    ruta_hijo2_mes: numVal('ruta_hijo2_mes', 0),
    manutencion_hijo2_mes: numVal('manutencion_hijo2_mes', 0),
    otros_gastos_hijo2_mes: numVal('otros_gastos_hijo2_mes', 0),
    costo_boda: deseaBoda ? numVal('costo_boda', 0) : 0,
    ingreso_pareja: deseaBoda ? numVal('ingreso_pareja', 0) : 0,
    plazo_boda_meses: deseaBoda ? Math.round(numVal('plazo_boda_meses', 0)) : 0,
    ahorro_sinergia_pct: deseaBoda ? numVal('ahorro_sinergia_pct', 0) : 0,
    monto_credito: deseaCredito ? numVal('monto_credito', 0) : 0,
    tasa_ea_credito: deseaCredito ? numVal('tasa_ea_credito', 0) : 0,
    plazo_credito: deseaCredito ? Math.round(numVal('plazo_credito', 0)) : 0,
    tasa_tco_mensual_pct: deseaCredito ? numVal('tasa_tco_mensual_pct', 0) : 0,
  };

  try {
    const res = await fetch('/api/calcular?t=' + Date.now(), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-cache' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    renderizarTodo(data, esClickBoton);
    if (statusEl) {
      statusEl.innerText = `✅ ${data.mensaje_ejecucion || 'PRUEBA EXITOSA'} (${data.timestamp_calculo}) — Hijos: ${nHijos} | Crédito: ${deseaCredito ? 'SÍ' : 'NO'} | Boda: ${deseaBoda ? 'SÍ' : 'NO'}`;
      statusEl.style.background = '#e8f5e9';
      statusEl.style.color = '#1b5e20';
    }
    document.getElementById('badge-hora').innerText = '🔒 Actualizado: ' + data.timestamp_calculo + ' | Modo Paramétrico Adaptativo';
  } catch (err) {
    if (statusEl) {
      statusEl.innerText = '⚠️ Error conectando con servidor Python local: ' + err;
      statusEl.style.background = '#ffebee';
      statusEl.style.color = '#c62828';
    }
  } finally {
    if (esClickBoton && btn) {
      setTimeout(() => {
        btn.innerText = '🔄 Ejecutar y Recalcular Modelo Paramétrico';
        btn.style.background = '';
      }, 350);
    }
  }
}

function renderizarTodo(data, animar = false) {
  const decs = data.actuaria_mod5.decisiones;
  const pAct = data.parametros_activos || {};
  const infoHijos = decs.HIJOS.desglose_colegio || {};
  const listaHijos = infoHijos.hijos_detalle || [];
  const nHijos = infoHijos.numero_hijos ?? listaHijos.length;
  const cons = infoHijos.consolidado || {};
  const esCompleto = infoHijos.modo_horizonte === 'ciclo_completo';

  // 0. BLOQUE 3 MANUAL DE MARCA: DIAGNÓSTICO DEL MÉDICO FINANCIERO AMIGO + RECETA DEL MES
  const manualOED = data.manual_marca_oed || {};
  if (manualOED.glosario) {
    window.__GLOSARIO_OED = manualOED.glosario;
    if (!window.__glosarioInicializado) {
      window.__glosarioInicializado = true;
      filtrarGlosarioOED();
    }
  }
  const diagMed = manualOED.diagnostico_medico_amigo;
  const boxDiagEl = document.getElementById('box-diagnostico-medico-oed');
  if (boxDiagEl && diagMed) {
    const mapaNivel = {
      verde: { clase: 'oed-doc-verde', icono: '🩺💚', prefijo: 'Signos vitales saludables:' },
      azul:  { clase: 'oed-doc-azul',  icono: '🩺💙', prefijo: 'Lectura tranquila de tu médico financiero:' },
      ambar: { clase: 'oed-doc-ambar', icono: '🩺🧡', prefijo: 'Chequeo preventivo a tiempo:' },
      rojo:  { clase: 'oed-doc-rojo',  icono: '🩺❤️‍🩹', prefijo: 'Pausa protectora para cuidar tu tranquilidad:' }
    };
    const cfgNiv = mapaNivel[diagMed.nivel] || mapaNivel.azul;
    boxDiagEl.innerHTML = `
      <div class="oed-doc-card ${cfgNiv.clase}">
        <div><strong>${cfgNiv.icono} ${cfgNiv.prefijo} ${diagMed.titulo_html}</strong></div>
        <div style="margin-top:4px;">${diagMed.explicacion_html}</div>
        <div style="margin-top:5px;font-size:0.76rem;opacity:0.86;">
          💡 <i>Tip Manual de Marca OED: Pasa el cursor sobre cualquier término subrayado con <b>?</b> para ver su explicación sencilla.</i>
        </div>
      </div>
      <div class="oed-rx-box">
        <strong>💊 Tu Receta Práctica para este Mes:</strong> ${diagMed.receta_html}
      </div>
    `;
  }

  const seccionHijosEl = document.getElementById('seccion-cuadros-hijos');
  const cardChartHijoEl = document.getElementById('card-chart-hijo');

  // 1. SI LOS HIJOS SON CERO (0), NO DESPLEGAR LOS CUADROS DE HIJOS NI SU GRÁFICA
  if (nHijos <= 0) {
    if (seccionHijosEl) seccionHijosEl.style.display = 'none';
    if (cardChartHijoEl) cardChartHijoEl.style.display = 'none';
    document.getElementById('grid-hijos-detalle').innerHTML = '';
  } else {
    if (seccionHijosEl) seccionHijosEl.style.display = 'block';
    if (cardChartHijoEl) cardChartHijoEl.style.display = 'block';

    document.getElementById('lbl-titulo-desglose-hijos').innerText =
      `🎓 Desglose Separado por Hijo (${nHijos} ${nHijos === 1 ? 'Hijo' : 'Hijos'}) y Cifra Consolidada Familiar`;
    document.getElementById('lbl-sub-desglose-hijos').innerText =
      listaHijos.map(h => `Hijo ${h.indice} (${h.etiqueta_grado})`).join(' | ') + ' | Consolidado Total';

    let htmlCardsHijos = '';
    const resumenLineasConsolidado = [];

    listaHijos.forEach((h, idx) => {
      const i = h.indice || (idx + 1);
      const colorH = COLORES_HIJOS[(i - 1) % COLORES_HIJOS.length];
      const iconoH = ICONOS_HIJOS[(i - 1) % ICONOS_HIJOS.length];
      const vpaMostrar = esCompleto ? h.vpa_ciclo_completo_cop : h.vpa_restante_edad_actual_cop;
      resumenLineasConsolidado.push(
        `${iconoH} VPA Hijo ${i} (${h.edad ?? 0}a - ${h.etiqueta_grado}): <strong style="color:${colorH};">${fmtCOP(vpaMostrar)}</strong>`
      );

      const filasTabla = h.en_universidad ? `
        <tr><td>🎓 Semestre Universidad (${h.semestre_actual ?? 0}° | Faltan ${h.semestres_restantes ?? 0})</td><td>${fmtCOP(h.valor_semestre_univ_cop)}/sem</td></tr>
        <tr><td>📅 Matrícula Univ. Mensualizada (2 sem/12)</td><td>${fmtCOP(h.matricula_univ_mensualizada_cop)}/mes</td></tr>
        <tr><td>🚌 Ruta / Transp. Hijo ${i} (Mes)</td><td>${fmtCOP(h.ruta_mes_cop)}/mes</td></tr>
        <tr><td>🍎 Manutención + Materiales Univ.</td><td>${fmtCOP(h.manutencion_y_otros_mes_cop)}/mes</td></tr>
        <tr class="total-row"><td style="color:${colorH};">💳 Gasto Mensual Total Hijo ${i}</td><td style="color:${colorH};">${fmtCOP(h.gasto_mes_directo_cop)}/mes</td></tr>
        <tr><td>📊 Flujo Anual Univ. + Manut. Hijo ${i}</td><td>${fmtCOP(h.flujo_anual_hoy_cop)}/año</td></tr>
        <tr><td>🎯 VPA Por Ejecutar (${h.semestres_restantes ?? 0} sem. restantes)</td><td style="color:${colorH};font-weight:800;">${fmtCOP(h.vpa_univ_proyectada_cop)}</td></tr>
      ` : `
        <tr><td>🏫 Pensión (${h.etiqueta_grado}) Mes</td><td>${fmtCOP(h.pension_mes_cop)}/mes</td></tr>
        <tr><td>🚌 Ruta Escolar Hijo ${i} (Mes)</td><td>${fmtCOP(h.ruta_mes_cop)}/mes</td></tr>
        <tr><td>📋 Matrícula + Cobros (Anual / 12)</td><td>${fmtCOP(h.matricula_prorrateada_mes_cop)}/mes</td></tr>
        <tr><td>🍎 Manutención + Otros Hijo ${i}</td><td>${fmtCOP(h.manutencion_y_otros_mes_cop)}/mes</td></tr>
        <tr class="total-row"><td style="color:${colorH};">💳 Gasto Mensual Directo Hijo ${i}</td><td style="color:${colorH};">${fmtCOP(h.gasto_mes_directo_cop)}/mes</td></tr>
        <tr><td>📊 Impacto Anualizado Hijo ${i}</td><td>${fmtCOP(h.impacto_mes_anualizado_cop)}/mes</td></tr>
        <tr><td>🗓️ Flujo Anual Hoy Hijo ${i}</td><td style="color:${colorH};font-weight:800;">${fmtCOP(h.flujo_anual_hoy_cop)}/año</td></tr>
      `;

      htmlCardsHijos += `
        <div class="child-card h${i} ${animar ? 'flash' : ''}">
          <span class="child-badge badge-h${i}">${iconoH} CUADRO ${i}: HIJO ${i} (${h.edad ?? 0} AÑOS | ${(h.etiqueta_grado || 'PARAMÉTRICO').toUpperCase()})</span>
          <div class="kpi-title">VPA Individual Hijo ${i} (${esCompleto ? 'Ciclo Completo' : (h.en_universidad ? (h.semestres_restantes ?? 0) + ' Sem. Univ.' : (h.anios_colegio_rest ?? 0) + 'a Col. + ' + (h.anios_univ_rest ?? 0) + 'a Univ.')})</div>
          <div class="child-vpa-main" style="color:${colorH};">${fmtCOP(vpaMostrar)}</div>
          <div class="child-vpa-sub">
            🏫 VPA Ciclo Completo: <strong>${fmtCOP(h.vpa_ciclo_completo_cop)}</strong><br>
            🎯 Por Ejecutar Hoy: <strong>${fmtCOP(h.vpa_saldo_neto_cop ?? h.vpa_restante_edad_actual_cop)}</strong>
          </div>
          <table class="metric-table">
            ${filasTabla}
          </table>
        </div>
      `;
    });

    const vpaConsMostrar = esCompleto ? cons.vpa_ciclo_completo_total_cop : cons.vpa_restante_total_cop;
    const balanceFlujoColor = cons.balance_flujo_mensual_cop >= 0 ? '#15803D' : '#B91C1C';
    const balanceFlujoLbl = cons.balance_flujo_mensual_cop >= 0 ? 'Superávit' : 'Déficit';

    htmlCardsHijos += `
      <div class="child-card consolidado ${animar ? 'flash' : ''}">
        <span class="child-badge badge-cons">👨‍👩‍👧‍👦 CUADRO ${nHijos + 1}: CONSOLIDADO TOTAL (${nHijos} ${nHijos === 1 ? 'HIJO' : 'HIJOS'})</span>
        <div class="kpi-title">VPA Consolidado Familiar (Suma Exacta Hijos 1 a ${nHijos})</div>
        <div class="child-vpa-main" style="color:#0F294A;font-size:1.38rem;">${fmtCOP(vpaConsMostrar)}</div>
        <div class="child-vpa-sub">
          ${resumenLineasConsolidado.join('<br>')}
        </div>
        <table class="metric-table">
          <tr><td>🏫 Educación Mensualizada (${nHijos} ${nHijos === 1 ? 'Hijo' : 'Hijos'})</td><td>${fmtCOP(cons.educacion_todos_hijos_mes_cop ?? (cons.educacion_h1_colegio_mes_cop + cons.educacion_h2_univ_mes_cop))}/mes</td></tr>
          <tr><td>🍎 Manutención + Otros (${nHijos} ${nHijos === 1 ? 'Hijo' : 'Hijos'})</td><td>${fmtCOP(cons.manutencion_y_otros_sumados_mes_cop)}/mes</td></tr>
          <tr class="highlight-row"><td>🔥 GASTO MENSUAL CONSOLIDADO</td><td>${fmtCOP(cons.gasto_mes_directo_total_cop)}/mes</td></tr>
          <tr class="total-row"><td>📊 Impacto Anualizado Consolidado</td><td>${fmtCOP(cons.impacto_mes_anualizado_total_cop)}/mes</td></tr>
          <tr><td>🗓️ Desembolso Anual Total (${nHijos} ${nHijos === 1 ? 'Hijo' : 'Hijos'})</td><td style="color:#0F294A;font-weight:800;">${fmtCOP(cons.flujo_anual_total_hoy_cop)}/año</td></tr>
          <tr><td>⚠️ Excedente: ${fmtCOP(cons.excedente_mensual_cop)} | Ahorro: ${fmtCOP(cons.liquidez_emergencia_cop)}</td><td style="color:${balanceFlujoColor};font-weight:800;">${balanceFlujoLbl}: ${fmtCOP(cons.balance_flujo_mensual_cop)}/mes</td></tr>
        </table>
      </div>
    `;
    document.getElementById('grid-hijos-detalle').innerHTML = htmlCardsHijos;

    // Gráfico Curva Actuarial Hijos (Paleta Oficial Manual de Marca OED)
    const nivSel = data.actuaria_mod5.nivel_seleccionado;
    const cHijo = data.actuaria_mod5.curvas_hijo;
    document.getElementById('titulo-curva-hijo').innerText =
      `📈 1. Curva Actuarial Educativa: ${listaHijos.map(h => `Hijo ${h.indice} (${h.edad}a - ${h.etiqueta_grado})`).join(' vs. ')} vs. Consolidado`;

    const trazasHijos = [
      {
        x: cHijo[nivSel].edades,
        y: cHijo[nivSel].flujo_nominal_m,
        type: 'bar',
        name: `Flujo Anual Consolidado (${nHijos} ${nHijos === 1 ? 'Hijo' : 'Hijos'})`,
        marker: { color: '#BFDBFE' }
      }
    ];
    listaHijos.forEach((h, idx) => {
      const i = h.indice || (idx + 1);
      const cInd = cHijo[`Hijo_${i}`];
      if (cInd) {
        trazasHijos.push({
          x: cInd.edades,
          y: cInd.vpa_acum_m,
          mode: 'lines+markers',
          name: `${ICONOS_HIJOS[(i - 1) % ICONOS_HIJOS.length]} VPA Hijo ${i} (${h.edad}a, ${h.etiqueta_grado})`,
          line: { color: COLORES_HIJOS[(i - 1) % COLORES_HIJOS.length], width: 3, dash: 'dot' }
        });
      }
    });
    trazasHijos.push({
      x: cHijo['Agustiniano_Suba'].edades,
      y: cHijo['Agustiniano_Suba'].vpa_acum_m,
      mode: 'lines+markers',
      name: `👨‍👩‍👧‍👦 VPA Consolidado Familiar (${nHijos} ${nHijos === 1 ? 'Hijo' : 'Hijos'})`,
      line: { color: '#0F294A', width: 4 }
    });

    Plotly.react('chart-hijo', trazasHijos, {
      template: 'plotly_white',
      font: { family: 'Segoe UI, system-ui, sans-serif', color: '#0F294A', size: 12 },
      margin: { t: 20, r: 20, b: 45, l: 55 },
      xaxis: { title: esCompleto ? 'Edad de los Hijos (Años 0 a 23)' : 'Horizonte de Pago desde Hoy (Años Restantes)' },
      yaxis: { title: 'Millones de Pesos ($ COP)' },
      legend: { orientation: 'h', y: 1.14 }
    }, { responsive: true });
  }

  // 2. RENDERIZAR LOS MARCOS DE LAS DECISIONES VITALES SELECCIONADAS
  const titulos = {
    CASARSE: '💍 Decisión: Casarse / Unión Marital',
    HIJOS: `🎓 Decisión: Hijos Consolidado (${nHijos} ${nHijos === 1 ? 'Hijo Activo' : 'Hijos Activos'})`,
    CREDITO: '🚗 Decisión: Crédito Estructural (+TCO)'
  };

  const decisionesMostrar = [];
  if (pAct.desea_boda) decisionesMostrar.push('CASARSE');
  if (nHijos > 0) decisionesMostrar.push('HIJOS');
  if (pAct.desea_credito) decisionesMostrar.push('CREDITO');

  let htmlKpis = '';
  if (decisionesMostrar.length === 0) {
    htmlKpis = `
      <div class="kpi-card" style="grid-column: 1 / -1; border-left-color: #0F294A; background: #F8FAFC;">
        <div class="kpi-title">🩺 MODO CONSULTORIO EN CERO ($0 COP) — ELIJA SUS METAS EN EL PASO 1</div>
        <div class="kpi-val">$0 COP</div>
        <div class="kpi-sub">
          En el <strong>Paso 1 (Preguntas Iniciales)</strong> arriba a la izquierda, seleccione:<br>
          &bull; <strong>¿Tiene hijos o cuántos desea evaluar?</strong> (1 a 6 hijos, pudiendo elegir en cada uno si está en <em>Jardín, Primaria, Bachillerato o Universidad</em>).<br>
          &bull; <strong>¿Desea un Crédito?</strong> (Sí / No) &nbsp;|&nbsp; <strong>¿Desea una Boda?</strong> (Sí / No).
        </div>
      </div>
    `;
  } else {
    for (const k of decisionesMostrar) {
      const d = decs[k];
      const pillClass = d.probabilidad_exito_montecarlo_pct >= 80 ? 'pill-ok' : (d.probabilidad_exito_montecarlo_pct >= 55 ? 'pill-warn' : 'pill-bad');
      let extraInfo = '';
      if (k === 'CASARSE' && d.ahorro_sinergia_mensual_cop !== undefined) {
        extraInfo = `<br><strong>Ahorro Sinergia Pareja:</strong> <span style="color:#15803D;font-weight:700;">+${fmtCOP(d.ahorro_sinergia_mensual_cop)}/mes</span>`;
      } else if (k === 'HIJOS' && listaHijos.length > 0) {
        extraInfo = '<br>' + listaHijos.map(h => `<strong>Hijo ${h.indice} (${h.etiqueta_grado}):</strong> ${fmtCOP(h.gasto_mes_directo_cop)}/mes`).join(' + ') +
          `<br><strong>👨‍👩‍👧‍👦 Gasto Mensual Consolidado:</strong> <span style="color:#EA580C;font-weight:800;">${fmtCOP(cons.gasto_mes_directo_total_cop)}/mes</span>`;
      } else if (k === 'CREDITO' && d.cuota_pura_credito_cop !== undefined) {
        extraInfo = `<br><strong>Cuota Pura:</strong> ${fmtCOP(d.cuota_pura_credito_cop)}/mes + <strong>TCO:</strong> ${fmtCOP(d.costo_tco_mensual_cop)}/mes`;
      }
      htmlKpis += `
        <div class="kpi-card ${animar ? 'flash' : ''}">
          <div class="kpi-title">${titulos[k]}</div>
          <div class="kpi-val">${fmtCOP(d.vpa_decision_cop)}</div>
          <div style="margin-bottom:6px;">
            <span class="pill ${pillClass}">${d.dictamen_viabilidad} (${d.probabilidad_exito_montecarlo_pct.toFixed(1)}% Éxito MC)</span>
          </div>
          <div class="kpi-sub">
            <strong>Impacto Mensual Anualizado:</strong> <span style="font-weight:700;">${fmtCOP(d.impacto_flujo_mensual_inmediato_cop)}/mes</span><br>
            <strong>Ahorro Mensual Requerido:</strong> ${fmtCOP(d.ahorro_mensual_requerido_cop)}${extraInfo}<br>
            <span style="display:block;margin-top:5px;color:#0F294A;">${d.recomendacion_actuarial_y_legal}</span>
          </div>
        </div>`;
    }
  }
  document.getElementById('kpis-decisiones').innerHTML = htmlKpis;

  // 3. Gráfico Monte Carlo (Paleta Oficial Manual de Marca OED: #15803D, #1D4ED8, #EA580C)
  const mc = data.actuaria_mod5.trayectorias_mc;
  const trazasMc = [];
  if (pAct.desea_boda || decisionesMostrar.length === 0) {
    trazasMc.push({ x: mc.CASARSE, type: 'histogram', name: 'Casarse (Con Sinergia)', opacity: 0.68, marker: { color: '#15803D' } });
  }
  if (nHijos > 0 || decisionesMostrar.length === 0) {
    trazasMc.push({ x: mc.HIJOS, type: 'histogram', name: `Hijos (${nHijos})`, opacity: 0.68, marker: { color: '#1D4ED8' } });
  }
  if (pAct.desea_credito || decisionesMostrar.length === 0) {
    trazasMc.push({ x: mc.CREDITO, type: 'histogram', name: 'Crédito (+TCO)', opacity: 0.68, marker: { color: '#EA580C' } });
  }
  Plotly.react('chart-mc', trazasMc, {
    template: 'plotly_white',
    font: { family: 'Segoe UI, system-ui, sans-serif', color: '#0F294A', size: 12 },
    barmode: 'overlay',
    margin: { t: 20, r: 20, b: 45, l: 50 },
    xaxis: { title: 'Flujo de Caja Mensual Post-Decisión (Millones COP)' },
    yaxis: { title: 'Escenarios (de 1.000)' },
    shapes: [{
      type: 'line', x0: 0, x1: 0, y0: 0, y1: 1, yref: 'paper',
      line: { color: '#B91C1C', width: 2.5, dash: 'dash' }
    }],
    legend: { orientation: 'h', y: 1.12 }
  }, { responsive: true });

  // 4. Gráfico Sensibilidad con Paleta Oficial Manual de Marca OED
  const sens = data.actuaria_mod5.sensibilidad;
  const excActualM = data.parametros_activos.excedente_m;
  const trazasSens = [];
  if (pAct.desea_boda || decisionesMostrar.length === 0) {
    trazasSens.push({ x: sens.excedentes_m, y: sens.CASARSE, mode: 'lines+markers', name: 'Casarse', line: { color: '#15803D', width: 3 } });
  }
  if (nHijos > 0 || decisionesMostrar.length === 0) {
    trazasSens.push({ x: sens.excedentes_m, y: sens.HIJOS, mode: 'lines+markers', name: `Hijos (${nHijos})`, line: { color: '#1D4ED8', width: 3 } });
  }
  if (pAct.desea_credito || decisionesMostrar.length === 0) {
    trazasSens.push({ x: sens.excedentes_m, y: sens.CREDITO, mode: 'lines+markers', name: 'Crédito (+TCO)', line: { color: '#EA580C', width: 3 } });
  }
  Plotly.react('chart-sens', trazasSens, {
    template: 'plotly_white',
    font: { family: 'Segoe UI, system-ui, sans-serif', color: '#0F294A', size: 12 },
    margin: { t: 20, r: 20, b: 45, l: 50 },
    xaxis: { title: 'Excedente Mensual Disponible (Millones COP)' },
    yaxis: { title: 'Probabilidad de Solvencia (%)', range: [0, 105] },
    shapes: [{
      type: 'line', x0: excActualM, x1: excActualM, y0: 0, y1: 1, yref: 'paper',
      line: { color: '#0F294A', width: 2, dash: 'dot' }
    }],
    legend: { orientation: 'h', y: 1.12 }
  }, { responsive: true });

  // 5. Renderizar Pestaña Habeas Data
  const hb = data.habeas_data;
  document.getElementById('texto-ley1581').innerText = hb.texto_ley_1581;
  document.getElementById('auditoria-habeas').innerHTML = `
    <p style="margin:6px 0;"><strong>Consentimiento Ley 1581 Válido:</strong> ${hb.consentimiento.consentimiento_valido ? '✅ SÍ (Autorizado)' : '❌ NO (Bloqueado)'}</p>
    <p style="margin:6px 0;"><strong>ID Seudonimizado (HMAC-SHA256):</strong> <code>${hb.consentimiento.usuario_seudonimizado}</code></p>
    <p style="margin:6px 0;"><strong>Hash SHA-256 de Integridad:</strong> <code>${hb.consentimiento.hash_evidencia_sha256}</code></p>
    <p style="margin:6px 0;"><strong>Dictamen Ley 1266/2008 y Ley 2157/2021:</strong> ${hb.permanencia.norma_aplicada}</p>
  `;
  document.getElementById('estado-disco-box').innerText =
    `Estado en Disco: ${hb.estado_disco_msg}` +
    (hb.token_muestra ? `\nToken Cifrado (.oed): ${hb.token_muestra}` : '');

  Plotly.react('chart-habeas', [
    {
      x: hb.curva_habeas.map(r => r.mora),
      y: hb.curva_habeas.map(r => r.permanencia),
      mode: 'lines+markers',
      name: 'Permanencia Legal Post-Pago (Meses)',
      line: { color: '#1D4ED8', width: 3 }
    },
    {
      x: [hb.permanencia.meses_en_mora_registrados || 0],
      y: [hb.permanencia.meses_permanencia_post_pago],
      mode: 'markers',
      name: 'Caso Evaluado Actual',
      marker: { color: '#EA580C', size: 13 }
    }
  ], {
    template: 'plotly_white',
    font: { family: 'Segoe UI, system-ui, sans-serif', color: '#0F294A', size: 12 },
    margin: { t: 20, r: 20, b: 45, l: 55 },
    xaxis: { title: 'Tiempo en Mora antes del Pago (Meses)' },
    yaxis: { title: 'Permanencia Máxima del Reporte Negativo (Meses)', range: [0, Math.max(54, (hb.permanencia.meses_permanencia_post_pago || 48) + 10)] },
    legend: { orientation: 'h', y: 1.12 }
  }, { responsive: true });

  // 6. Renderizar Pestaña 6 Módulos
  const m6 = data.caso_integrado_6_modulos;
  document.getElementById('kpis-6-modulos').innerHTML = `
    <div class="kpi-card">
      <div class="kpi-title">🫀 Paso 1 — Módulo 6 (Salin Avellaneda)</div>
      <div class="kpi-val">Perfil: ${m6.mod6_salin.perfil_riesgo}</div>
      <div class="kpi-sub">
        Puntaje Suitability SFC: ${m6.mod6_salin.puntaje}/100<br>
        Inversión Compuesta 10a ($200k/m): <strong>${fmtCOP(m6.mod6_salin.patrimonio_10a_inversion_cop)}</strong> vs. Azar: ${fmtCOP(m6.mod6_salin.valor_esperado_azar_cop)}<br>
        Colapso Pirámide (r=3): Nivel ${m6.mod6_salin.ciclos_colapso_piramide}
      </div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">🩻 Paso 2 — Módulo 1 (Nidia Velásquez)</div>
      <div class="kpi-val">${fmtCOP(m6.mod1_nidia.ingreso_neto_cop)}</div>
      <div class="kpi-sub">
        Ingreso Disponible Neto (de $6.5M brutos)<br>
        Excedente Mensual: <strong>${fmtCOP(m6.mod1_nidia.excedente_mensual_cop)}</strong><br>
        Costo Oportunidad Gastos Hormiga (10a): ${fmtCOP(m6.mod1_nidia.costo_hormiga_10a_cop)}
      </div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">🩹 Paso 3 — Módulo 3 (Catalina Moreno)</div>
      <div class="kpi-val">Estrategia ${m6.mod3_catalina.estrategia_optima}</div>
      <div class="kpi-sub">
        Índice Endeudamiento: ${m6.mod3_catalina.indice_endeudamiento_pct}%<br>
        Ahorro en Intereses: <strong>${fmtCOP(m6.mod3_catalina.ahorro_intereses_cop)}</strong><br>
        Flujo de Caja Liberado: ${fmtCOP(m6.mod3_catalina.flujo_liberado_cop)}/mes
      </div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">🌱 Paso 4 — Módulo 2 (Camilo Matson)</div>
      <div class="kpi-val">${fmtCOP(m6.mod2_camilo.patrimonio_5a_nominal_cop)}</div>
      <div class="kpi-sub">
        Patrimonio Proyectado a 5 Años (Nominal)<br>
        En Pesos Reales de Hoy: <strong>${fmtCOP(m6.mod2_camilo.patrimonio_5a_real_cop)}</strong><br>
        Rentabilidad Real Neta: ${m6.mod2_camilo.tasa_real_neta_pct}% EA
      </div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">🏡 Paso 5 — Módulo 4 (Jesi)</div>
      <div class="kpi-val">${fmtCOP(m6.mod4_jesi.primera_cuota_pesos_cop)}/mes</div>
      <div class="kpi-sub">
        Segmento: ${m6.mod4_jesi.segmento}<br>
        ¿Cumple Ley 546/1999 (<=30%)?: <strong>${m6.mod4_jesi.cumple_ley_546 ? '✅ SÍ CUMPLE' : '❌ NO CUMPLE'}</strong><br>
        Cap Rate Neto Inmobiliario: ${m6.mod4_jesi.cap_rate_neto_pct}% EA
      </div>
    </div>
    <div class="kpi-card" style="border-left-color:#EA580C;">
      <div class="kpi-title">🛡️ Paso 6 + Paso 0 — Módulo 5 y Habeas Data (Nelson Angel)</div>
      <div class="kpi-val">${fmtCOP(decs.HIJOS.vpa_decision_cop)}</div>
      <div class="kpi-sub">
        VPA Hijos Consolidado | Simulación Monte Carlo<br>
        Éxito Monte Carlo Hijos: <strong>${decs.HIJOS.probabilidad_exito_montecarlo_pct}% (${decs.HIJOS.dictamen_viabilidad})</strong><br>
        Protección Ley 1581 y Ley 1266 Activa
      </div>
    </div>
  `;
}

function verTerminoGlosarioOED(clave) {
  const glosario = window.__GLOSARIO_OED || {};
  const f = glosario[clave];
  if (!f) return;
  document.querySelectorAll('#pills-glosario-oed .glossary-pill').forEach(el => {
    el.classList.toggle('active', el.dataset.k === clave);
  });
  const cont = document.getElementById('detalle-glosario-oed');
  if (cont) {
    cont.innerHTML = `
      <div style="font-size:0.74rem;color:#1D4ED8;font-weight:700;text-transform:uppercase;margin-bottom:4px;">
        Familia: ${f.categoria} &bull; ${f.termino_tecnico}
      </div>
      <div class="oed-doc-card oed-doc-verde" style="margin:4px 0 8px 0;">
        <strong>🩺 Explicación sencilla de tu Médico Financiero Amigo:</strong> ${f.lenguaje_claro}
      </div>
      <div class="oed-rx-box" style="margin:0;">
        <strong>🇨🇴 Ejemplo cotidiano en pesos ($ COP):</strong> ${f.ejemplo_cotidiano}
      </div>
    `;
  }
}

function filtrarGlosarioOED() {
  const glosario = window.__GLOSARIO_OED || {};
  const q = (document.getElementById('buscador-glosario-oed')?.value || '').trim().toLowerCase();
  const claves = Object.keys(glosario).filter(k => {
    const f = glosario[k];
    return !q ||
      f.termino_tecnico.toLowerCase().includes(q) ||
      f.lenguaje_claro.toLowerCase().includes(q) ||
      f.categoria.toLowerCase().includes(q);
  });
  const pillsEl = document.getElementById('pills-glosario-oed');
  if (!pillsEl) return;
  pillsEl.innerHTML = claves.map(k =>
    `<span class="glossary-pill" data-k="${k}" onclick="verTerminoGlosarioOED('${k}')">${glosario[k].termino_tecnico}</span>`
  ).join('');
  if (claves.length > 0) {
    const preferido = claves.includes('MONTE_CARLO') ? 'MONTE_CARLO' : claves[0];
    verTerminoGlosarioOED(preferido);
  }
}

function inicializarTooltipsInteractivos() {
  let tipBox = document.getElementById('oed-floating-tooltip');
  if (!tipBox) {
    tipBox = document.createElement('div');
    tipBox.id = 'oed-floating-tooltip';
    tipBox.className = 'oed-tooltip-floating';
    document.body.appendChild(tipBox);
  }

  // Propagar tooltip desde cada input/select a su .form-group y <label>, agregando insignia '?'
  document.querySelectorAll('.form-group').forEach(grp => {
    const ctrl = grp.querySelector('input[data-tooltip], select[data-tooltip], input[title], select[title]');
    if (!ctrl) return;
    const textoTip = ctrl.getAttribute('data-tooltip') || ctrl.getAttribute('title') || '';
    if (!textoTip) return;
    ctrl.setAttribute('data-tooltip', textoTip);
    ctrl.setAttribute('title', textoTip);
    grp.setAttribute('data-tooltip', textoTip);
    const lbl = grp.querySelector('label');
    if (lbl) {
      lbl.setAttribute('data-tooltip', textoTip);
      lbl.setAttribute('title', textoTip);
      if (!lbl.querySelector('.tip-badge')) {
        const badge = document.createElement('span');
        badge.className = 'tip-badge';
        badge.innerText = '?';
        lbl.appendChild(badge);
      }
    }
  });

  function posicionarTooltip(ev, targetEl) {
    const rect = targetEl.getBoundingClientRect();
    const tipRect = tipBox.getBoundingClientRect();
    let top = rect.top - tipRect.height - 8;
    if (top < 8) {
      top = rect.bottom + 8;
    }
    let left = (ev && ev.clientX) ? (ev.clientX - 24) : rect.left;
    if (left + tipRect.width > window.innerWidth - 12) {
      left = window.innerWidth - tipRect.width - 12;
    }
    if (left < 10) left = 10;
    tipBox.style.top = `${top}px`;
    tipBox.style.left = `${left}px`;
  }

  function mostrarTooltip(ev) {
    const el = ev.target.closest('[data-tooltip]');
    if (!el) {
      tipBox.classList.remove('visible');
      return;
    }
    const txt = el.getAttribute('data-tooltip');
    if (!txt) return;
    tipBox.innerHTML = `<strong>💡 Qué colocar aquí:</strong>${txt}`;
    tipBox.classList.add('visible');
    posicionarTooltip(ev, el);
  }

  function ocultarTooltip() {
    tipBox.classList.remove('visible');
  }

  if (!window.__oedTooltipsBound) {
    window.__oedTooltipsBound = true;
    document.addEventListener('mouseover', mostrarTooltip);
    document.addEventListener('mousemove', ev => {
      if (tipBox.classList.contains('visible')) {
        const el = ev.target.closest('[data-tooltip]');
        if (el) posicionarTooltip(ev, el);
      }
    });
    document.addEventListener('mouseout', ev => {
      const rel = ev.relatedTarget;
      if (!rel || !rel.closest || !rel.closest('[data-tooltip]')) {
        ocultarTooltip();
      }
    });
    document.addEventListener('focusin', mostrarTooltip);
    document.addEventListener('focusout', ocultarTooltip);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  ajustarSeccionesPorPreguntas(false);
  inicializarTooltipsInteractivos();
  actualizarDashboard(false);
});
</script>
</body>
</html>
"""


class DashboardOEDHandler(BaseHTTPRequestHandler):
    """Servidor HTTP multihilo local que entrega la interfaz gráfica y procesa las simulaciones en Python."""

    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        body = HTML_DASHBOARD.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path.startswith("/api/calcular"):
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            params = json.loads(raw)
            respuesta = _calcular_payload_completo(params)
            body = json.dumps(respuesta, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()


def _encontrar_puerto_libre(puerto_inicial: int = 8501) -> int:
    for p in range(puerto_inicial, puerto_inicial + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    return 8501


def iniciar_interfaz_grafica_local() -> None:
    puerto = _encontrar_puerto_libre(8501)
    url = f"http://127.0.0.1:{puerto}"
    servidor = ThreadingHTTPServer(("127.0.0.1", puerto), DashboardOEDHandler)
    print("=" * 80)
    print("🚀 INTERFAZ GRÁFICA LOCAL OED ACTIVA (NELSON ANGEL — COLEGIO AGUSTINIANO SUBA)")
    print(f"🌐 Abre en tu navegador: {url}")
    print("   (Presiona Ctrl + C en la terminal para detener el servidor)")
    print("=" * 80)
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️ Servidor local detenido.")
        servidor.server_close()


def main() -> None:
    """Punto de entrada principal del orquestador e interfaz gráfica local OED."""
    iniciar_interfaz_grafica_local()


if __name__ == "__main__":
    main()
