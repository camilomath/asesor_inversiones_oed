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
from typing import Any, Dict

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
from src.finance import cargar_configuracion, ea_a_em
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
    """Ejecuta todos los cálculos actuariales, de Habeas Data e integrados en tiempo real."""
    cfg = cargar_configuracion()
    macro = cfg["parametros_macro_colombia"]
    ipc = float(macro["ipc_anual_dane"])
    inf_edu = _to_float(params.get("inflacion_educativa_pct"), float(macro["inflacion_educativa_anual"]) * 100.0) / 100.0
    tasa_descuento = 0.095

    # Copia local de config con la inflación educativa parametrizada (Resolución MEN)
    cfg_custom = json.loads(json.dumps(cfg))
    cfg_custom["parametros_macro_colombia"]["inflacion_educativa_anual"] = inf_edu

    ingreso_neto_hogar = _to_float(params.get("ingreso_neto_hogar"), 9_115_000.0)
    excedente_mensual = _to_float(params.get("excedente_mensual"), 0.0)
    liquidez_emergencia = _to_float(params.get("liquidez_emergencia"), 0.0)
    ingreso_pareja = _to_float(params.get("ingreso_pareja"), 4_500_000.0)
    costo_boda = _to_float(params.get("costo_boda"), 18_000_000.0)
    monto_credito = _to_float(params.get("monto_credito"), 45_000_000.0)
    tasa_ea_credito = _to_float(params.get("tasa_ea_credito"), 16.5) / 100.0
    plazo_credito = max(6, int(_to_float(params.get("plazo_credito"), 48)))

    # Parámetros reales de los hijos de Nelson:
    # - Hijo 1: 16 años, Grado 11 en el Colegio Agustiniano Suba, Sin Ruta ($0)
    # - Hijo 2: 20 años, Semestre 7 de Universidad (valor semestre $13.000.000 COP)
    # - Sin excedente mensual ($0) y sin ahorro / fondo de emergencia ($0)
    nivel_hijo = str(params.get("nivel_costo_hijo", "Agustiniano_Suba"))
    numero_hijos = max(1, int(_to_float(params.get("numero_hijos"), 2)))
    modo_horizonte = str(params.get("modo_horizonte", "ciclo_completo"))
    grado_h1 = str(params.get("grado_agustiniano_h1", "once_2026"))
    mapa_etiquetas_grado = {
        "jardin_2026": "Jardín",
        "transicion_1_2026": "Transición / 1°",
        "primaria_2_3_2026": "Primaria 2°-3°",
        "cuarto_sexto_2026": "Grados 4°-6°",
        "septimo_noveno_2026": "Grados 7°-9°",
        "decimo_2026": "Grado 10°",
        "once_2026": "Grado 11°",
        "historico_base": "Tarifa Base",
    }
    etiqueta_grado_h1 = mapa_etiquetas_grado.get(grado_h1, "Grado 11°")
    edad_hijo1 = max(0, min(22, int(_to_float(params.get("edad_hijo1"), 16))))
    edad_hijo2 = max(0, min(25, int(_to_float(params.get("edad_hijo2"), 20))))
    etapa_hijo2 = str(params.get("etapa_hijo2", "univ_sem7"))
    hijo2_en_univ = etapa_hijo2.startswith("univ")
    semestre_actual_h2 = max(1, min(10, int(_to_float(params.get("semestre_actual_h2"), 7))))
    semestres_restantes_h2 = max(1, 10 - semestre_actual_h2 + 1)

    # Años de colegio que le faltan al Hijo 1 según su edad actual y grado:
    # A los 16 años en Grado 11 = 1 año restante de colegio (17 - 16 = 1) + 5 años (10 semestres) de universidad.
    if edad_hijo1 <= 16:
        anios_colegio_rest_h1 = max(1, 17 - edad_hijo1)
        anios_univ_rest_h1 = 5
    elif edad_hijo1 == 17:
        anios_colegio_rest_h1 = 1 if grado_h1 == "once_2026" else 0
        anios_univ_rest_h1 = 5
    else:
        anios_colegio_rest_h1 = 0
        anios_univ_rest_h1 = max(0, 23 - edad_hijo1)

    edad_actual_hijo = max(0, min(22, int(round((edad_hijo1 + min(22, edad_hijo2)) / 2.0))))
    edad_inicio_curva = 0 if modo_horizonte == "ciclo_completo" else min(edad_hijo1, min(22, edad_hijo2))

    # Multiplicador si el usuario cambia Perfil Educativo a Bajo (0.65x), Medio (1.0x) o Alto (1.85x)
    if nivel_hijo == "Bajo":
        escala_perfil_edu = 0.65
    elif nivel_hijo == "Medio":
        escala_perfil_edu = 0.80
    elif nivel_hijo == "Alto":
        escala_perfil_edu = 1.35
    else:
        escala_perfil_edu = 1.0

    pension_colegio_mes = _to_float(params.get("pension_colegio_mes"), 1_421_000.0) * escala_perfil_edu
    matricula_anual = _to_float(params.get("matricula_anual"), 1_800_000.0) * escala_perfil_edu
    pension_hijo2_mes = _to_float(params.get("pension_hijo2_mes"), 1_421_000.0) * escala_perfil_edu
    matricula_hijo2_anual = _to_float(params.get("matricula_hijo2_anual"), 1_800_000.0) * escala_perfil_edu
    transporte_mes = _to_float(params.get("transporte_mes"), 0.0)
    manutencion_hijo_mes = _to_float(params.get("manutencion_hijo_mes"), 1_150_000.0)
    otros_gastos_mes = _to_float(params.get("otros_gastos_mes"), 300_000.0)
    semestre_univ_hoy = _to_float(params.get("semestre_univ_hoy"), 13_000_000.0) * escala_perfil_edu
    semestre_univ_h2 = _to_float(params.get("semestre_univ_h2"), 13_000_000.0) * escala_perfil_edu

    # 1. Gobierno de Datos y Habeas Data (Nelson)
    usuario_id = str(params.get("usuario_id", "CC_1020304050_NELSON"))
    acepta_habeas = bool(params.get("acepta_habeas", True))
    meses_mora = int(_to_float(params.get("meses_mora"), 14))
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

    # 2. Curva Actuarial para Hijo 1 (16a Grado 11 Agustiniano Suba, Sin Ruta) e Hijo 2 (20a, 7° Sem. Universidad @ $13M)
    flujo_anual_h1 = (pension_colegio_mes + transporte_mes) * 10.0 + matricula_anual + ((manutencion_hijo_mes + otros_gastos_mes) * 12.0)
    pago_mes_directo_h1 = pension_colegio_mes + transporte_mes + manutencion_hijo_mes + otros_gastos_mes
    costo_mes_equiv_h1 = flujo_anual_h1 / 12.0

    # Para Hijo 2 (20 años, 7° Semestre de Universidad @ $13M/semestre):
    # En su etapa escolar previa cursó con ruta escolar completa ($380k/mes) y en universidad tiene
    # gastos adicionales de práctica, materiales especializados, derechos de grado y posgrado/sostenimiento hasta los 23 años.
    ruta_hist_colegio_h2 = 380_000.0 * escala_perfil_edu
    flujo_anual_colegio_ref_h2 = (pension_hijo2_mes + ruta_hist_colegio_h2) * 10.0 + matricula_hijo2_anual + ((manutencion_hijo_mes + otros_gastos_mes) * 12.0)
    if hijo2_en_univ:
        matricula_univ_anual_h2 = semestre_univ_h2 * 2.0
        matricula_univ_mes_h2 = matricula_univ_anual_h2 / 12.0
        flujo_anual_h2 = matricula_univ_anual_h2 + ((manutencion_hijo_mes + otros_gastos_mes) * 12.0)
        pago_mes_directo_h2 = matricula_univ_mes_h2 + manutencion_hijo_mes + otros_gastos_mes
        costo_mes_equiv_h2 = flujo_anual_h2 / 12.0
    else:
        matricula_univ_anual_h2 = matricula_hijo2_anual
        matricula_univ_mes_h2 = matricula_hijo2_anual / 12.0
        flujo_anual_h2 = flujo_anual_colegio_ref_h2
        pago_mes_directo_h2 = pension_hijo2_mes + transporte_mes + manutencion_hijo_mes + otros_gastos_mes
        costo_mes_equiv_h2 = flujo_anual_h2 / 12.0

    if numero_hijos == 1:
        flujo_anual_agustiniano_total = flujo_anual_h1
        pago_mes_directo_total = pago_mes_directo_h1
    elif numero_hijos == 2:
        flujo_anual_agustiniano_total = flujo_anual_h1 + flujo_anual_h2
        pago_mes_directo_total = pago_mes_directo_h1 + pago_mes_directo_h2
    else:
        flujo_prom = (flujo_anual_h1 + flujo_anual_h2) / 2.0
        flujo_anual_agustiniano_total = flujo_anual_h1 + flujo_anual_h2 + flujo_prom * (numero_hijos - 2)
        pago_prom = (pago_mes_directo_h1 + pago_mes_directo_h2) / 2.0
        pago_mes_directo_total = pago_mes_directo_h1 + pago_mes_directo_h2 + pago_prom * (numero_hijos - 2)

    costo_mes_equiv_agustiniano_total = flujo_anual_agustiniano_total / 12.0

    costos_etapa_h1 = {
        "infancia": manutencion_hijo_mes + otros_gastos_mes + 450_000.0,
        "colegio": costo_mes_equiv_h1,
        "univ": ((semestre_univ_hoy * 2.0) / 12.0) + manutencion_hijo_mes + otros_gastos_mes,
    }
    costos_etapa_h2 = {
        "infancia": manutencion_hijo_mes + otros_gastos_mes + 450_000.0,
        "colegio": flujo_anual_colegio_ref_h2 / 12.0,
        "univ": ((semestre_univ_h2 * 2.0) / 12.0) + manutencion_hijo_mes + otros_gastos_mes + 250_000.0,
    }

    perfiles_curva = {
        "Agustiniano_Suba": {
            "infancia": costos_etapa_h1["infancia"] + (costos_etapa_h2["infancia"] if numero_hijos >= 2 else 0.0),
            "colegio": costos_etapa_h1["colegio"] + (costos_etapa_h2["colegio"] if numero_hijos >= 2 else 0.0),
            "univ": costos_etapa_h1["univ"] + (costos_etapa_h2["univ"] if numero_hijos >= 2 else 0.0),
        },
        "Bajo": {
            "infancia": 1_150_000.0 * 0.65 * numero_hijos,
            "colegio": 1_650_000.0 * 0.65 * numero_hijos,
            "univ": 2_450_000.0 * 0.65 * numero_hijos,
        },
        "Medio": {
            "infancia": 1_150_000.0 * 1.0 * numero_hijos,
            "colegio": 1_650_000.0 * 1.0 * numero_hijos,
            "univ": 2_450_000.0 * 1.0 * numero_hijos,
        },
        "Alto": {
            "infancia": 1_150_000.0 * 1.85 * numero_hijos,
            "colegio": 1_650_000.0 * 1.85 * numero_hijos,
            "univ": 2_450_000.0 * 1.85 * numero_hijos,
        },
    }

    def _calcular_curva_ciclo_hijo(
        costos_etapa: Dict[str, float],
        edad_fin_ciclo: int = 22,
        factor_edad_actual: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Calcula el Valor Presente Actuarial (VPA) del ciclo educativo completo del hijo (0 hasta edad_fin_ciclo).
        """
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

        meses_univ = max(12, (18 - min(17, edad_actual_hijo)) * 12)
        tasa_em_f = ea_a_em(tasa_descuento)
        ahorro_mes_u = (vf_univ_a_18 * tasa_em_f) / (((1.0 + tasa_em_f) ** meses_univ) - 1.0)
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

    # Curvas de Ciclo Completo (0 a 23 años):
    # - Hijo 1 (16 años, Grado 11 Sin Ruta, ciclo 0 a 22 años): ~$599.7M COP
    # - Hijo 2 (20 años, 7° Semestre Univ. @ $13M/sem, ciclo 0 a 23 años con ruta histórica y etapa posgrado/grado): ~$702.8M COP
    factor_sem_h2 = 1.0 + ((semestre_actual_h2 - 1) * 0.015) + max(0, edad_hijo2 - 18) * 0.02
    curva_h1_completo = _calcular_curva_ciclo_hijo(costos_etapa_h1, edad_fin_ciclo=22, factor_edad_actual=1.0 + (16 - edad_hijo1) * 0.012)
    curva_h2_completo = _calcular_curva_ciclo_hijo(
        costos_etapa_h2,
        edad_fin_ciclo=23 if hijo2_en_univ else 22,
        factor_edad_actual=factor_sem_h2 if hijo2_en_univ else 1.0,
    )

    edades_0_23 = list(range(0, 24))
    if len(curva_h1_completo["edades"]) < 24:
        curva_h1_completo["edades"] = edades_0_23
        curva_h1_completo["flujo_nominal_m"].append(0.0)
        curva_h1_completo["vpa_acum_m"].append(curva_h1_completo["vpa_acum_m"][-1])
    if len(curva_h2_completo["edades"]) < 24:
        curva_h2_completo["edades"] = edades_0_23
        curva_h2_completo["flujo_nominal_m"].append(0.0)
        curva_h2_completo["vpa_acum_m"].append(curva_h2_completo["vpa_acum_m"][-1])

    # 2A. Valoración Capitalizada a Edad Actual + Etapa Restante Hijo 1 (16a, Grado 11)
    horizonte_anios_h1 = max(1, anios_colegio_rest_h1 + anios_univ_rest_h1)
    horizonte_anios_h2 = max(1, int((semestres_restantes_h2 + 1) // 2) + 2) if hijo2_en_univ else max(1, 22 - min(21, edad_hijo2))
    horizonte_max_anios = max(horizonte_anios_h1, horizonte_anios_h2, 6)

    capital_escolar_cursado_h1 = curva_h1_completo["vpa_colegio_cop"] * (min(16, edad_hijo1) / 17.0)
    prob_sup_h1 = 1.0
    vpa_acum_h1_rest = 0.0
    vpa_col_h1_rest = 0.0
    vpa_univ_h1_rest = 0.0
    vf_univ_h1 = 0.0
    eje_anios_rest = []
    flujo_nom_h1_rest = []
    vpa_acum_lista_h1_rest = []

    for anio_idx in range(horizonte_max_anios):
        etiqueta_anio = f"Año {anio_idx + 1} ({edad_hijo1 + anio_idx}a H1 / {edad_hijo2 + anio_idx}a H2)"
        eje_anios_rest.append(etiqueta_anio)
        if anio_idx < anios_colegio_rest_h1:
            prob_sup_h1 *= 0.9985
            f_hoy_h1 = costos_etapa_h1["colegio"] * 12.0
            f_fut_h1 = f_hoy_h1 * ((1.0 + inf_edu) ** anio_idx)
            vp_h1 = (f_fut_h1 / ((1.0 + tasa_descuento) ** anio_idx)) * prob_sup_h1
            vpa_col_h1_rest += vp_h1
            vpa_acum_h1_rest += vp_h1
        elif anio_idx < (anios_colegio_rest_h1 + anios_univ_rest_h1):
            prob_sup_h1 *= 0.9985
            f_hoy_h1 = costos_etapa_h1["univ"] * 12.0
            f_fut_h1 = f_hoy_h1 * ((1.0 + inf_edu) ** anio_idx)
            vp_h1 = (f_fut_h1 / ((1.0 + tasa_descuento) ** anio_idx)) * prob_sup_h1
            vpa_univ_h1_rest += vp_h1
            vpa_acum_h1_rest += vp_h1
            vf_univ_h1 += f_fut_h1 / ((1.0 + tasa_descuento) ** max(0, anio_idx - anios_colegio_rest_h1))
        else:
            f_fut_h1 = 0.0
        flujo_nom_h1_rest.append(round(f_fut_h1 / 1e6, 2))
        vpa_acum_lista_h1_rest.append(round((capital_escolar_cursado_h1 + vpa_acum_h1_rest) / 1e6, 2))

    meses_para_univ_h1 = max(12, anios_colegio_rest_h1 * 12)
    tasa_em_f = ea_a_em(tasa_descuento)
    ahorro_mes_univ_h1_cop = (vf_univ_h1 * tasa_em_f) / (((1.0 + tasa_em_f) ** meses_para_univ_h1) - 1.0)
    vpa_saldo_neto_h1_cop = round(vpa_acum_h1_rest, 2)
    vpa_capitalizado_h1_cop = round(capital_escolar_cursado_h1 + vpa_acum_h1_rest, 2)

    curva_h1_restante = {
        "edades": eje_anios_rest,
        "flujo_nominal_m": flujo_nom_h1_rest,
        "vpa_acum_m": vpa_acum_lista_h1_rest,
        "vpa_total_cop": vpa_capitalizado_h1_cop,
        "vpa_saldo_neto_cop": vpa_saldo_neto_h1_cop,
        "vpa_colegio_cop": round(vpa_col_h1_rest, 2),
        "vpa_univ_cop": round(vpa_univ_h1_rest, 2),
        "ahorro_mensual_univ_cop": round(ahorro_mes_univ_h1_cop, 2),
    }

    # 2B. Valoración Capitalizada a Edad Actual + Etapa Universitaria Superior Hijo 2 (20 años, Semestre 7 de 10 @ $13M/sem)
    flujo_nom_h2_rest = []
    vpa_acum_lista_h2_rest = []
    capital_escolar_cursado_h2 = curva_h2_completo["vpa_colegio_cop"]
    if hijo2_en_univ:
        flujo_semestral_hoy_h2 = semestre_univ_h2 + ((manutencion_hijo_mes + otros_gastos_mes) * 6.0)
        inf_sem = ((1.0 + inf_edu) ** 0.5) - 1.0
        desc_sem = ((1.0 + tasa_descuento) ** 0.5) - 1.0
        semestres_cursados_h2 = max(0, semestre_actual_h2 - 1)
        vpa_semestres_cursados_h2 = semestres_cursados_h2 * flujo_semestral_hoy_h2
        semestres_posgrado_sostenimiento_h2 = max(4, (23 - min(21, edad_hijo2)) * 2)
        total_semestres_proy_h2 = semestres_restantes_h2 + semestres_posgrado_sostenimiento_h2
        prob_sup_sem = 1.0
        vpa_pregrado_faltante_h2 = 0.0
        vpa_posgrado_sost_h2 = 0.0
        vpa_acum_h2_etapa_univ = vpa_semestres_cursados_h2

        for anio_idx in range(horizonte_max_anios):
            f_anio_h2 = 0.0
            for sem_offset in (0, 1):
                s_idx = anio_idx * 2 + sem_offset
                if s_idx < semestres_restantes_h2:
                    prob_sup_sem *= 0.99925
                    f_sem_fut = flujo_semestral_hoy_h2 * ((1.0 + inf_sem) ** s_idx)
                    vp_sem = (f_sem_fut / ((1.0 + desc_sem) ** s_idx)) * prob_sup_sem
                    f_anio_h2 += f_sem_fut
                    vpa_pregrado_faltante_h2 += vp_sem
                    vpa_acum_h2_etapa_univ += vp_sem
                elif s_idx < total_semestres_proy_h2:
                    prob_sup_sem *= 0.99925
                    f_sem_fut = (flujo_semestral_hoy_h2 * 1.08) * ((1.0 + inf_sem) ** s_idx)
                    vp_sem = (f_sem_fut / ((1.0 + desc_sem) ** s_idx)) * prob_sup_sem
                    f_anio_h2 += f_sem_fut
                    vpa_posgrado_sost_h2 += vp_sem
                    vpa_acum_h2_etapa_univ += vp_sem
            flujo_nom_h2_rest.append(round(f_anio_h2 / 1e6, 2))
            vpa_acum_lista_h2_rest.append(round((capital_escolar_cursado_h2 + vpa_acum_h2_etapa_univ) / 1e6, 2))

        vpa_etapa_univ_completa_h2_cop = round(vpa_acum_h2_etapa_univ, 2)
        vpa_restante_h2_cop = round(capital_escolar_cursado_h2 + vpa_acum_h2_etapa_univ, 2)
        vpa_colegio_rest_h2_cop = round(vpa_semestres_cursados_h2, 2)  # Semestres 1° al 6° ya invertidos en Univ.
        vpa_univ_rest_h2_cop = round(vpa_pregrado_faltante_h2 + vpa_posgrado_sost_h2, 2)  # Semestres 7° a 10° + Grado/Posgrado a 23a
        ahorro_mes_univ_h2_cop = round(costo_mes_equiv_h2, 2)
    else:
        anios_col_h2 = max(1, 17 - min(16, edad_hijo2))
        anios_univ_h2 = 5
        capital_prev_col_h2 = curva_h2_completo["vpa_colegio_cop"] * (min(16, edad_hijo2) / 17.0)
        prob_sup_h2 = 1.0
        vpa_acum_h2_rest = 0.0
        vpa_col_h2_tmp = 0.0
        vpa_univ_h2_tmp = 0.0
        for anio_idx in range(horizonte_max_anios):
            if anio_idx < anios_col_h2:
                prob_sup_h2 *= 0.9985
                f_fut_h2 = (costos_etapa_h2["colegio"] * 12.0) * ((1.0 + inf_edu) ** anio_idx)
                vp_h2 = (f_fut_h2 / ((1.0 + tasa_descuento) ** anio_idx)) * prob_sup_h2
                vpa_col_h2_tmp += vp_h2
                vpa_acum_h2_rest += vp_h2
            elif anio_idx < (anios_col_h2 + anios_univ_h2):
                prob_sup_h2 *= 0.9985
                f_fut_h2 = (costos_etapa_h2["univ"] * 12.0) * ((1.0 + inf_edu) ** anio_idx)
                vp_h2 = (f_fut_h2 / ((1.0 + tasa_descuento) ** anio_idx)) * prob_sup_h2
                vpa_univ_h2_tmp += vp_h2
                vpa_acum_h2_rest += vp_h2
            else:
                f_fut_h2 = 0.0
            flujo_nom_h2_rest.append(round(f_fut_h2 / 1e6, 2))
            vpa_acum_lista_h2_rest.append(round((capital_prev_col_h2 + vpa_acum_h2_rest) / 1e6, 2))
        vpa_etapa_univ_completa_h2_cop = round(vpa_acum_h2_rest, 2)
        vpa_restante_h2_cop = round(capital_prev_col_h2 + vpa_acum_h2_rest, 2)
        vpa_colegio_rest_h2_cop = round(vpa_col_h2_tmp, 2)
        vpa_univ_rest_h2_cop = round(vpa_univ_h2_tmp, 2)
        ahorro_mes_univ_h2_cop = round(costo_mes_equiv_h2, 2)

    curva_h2_restante = {
        "edades": eje_anios_rest,
        "flujo_nominal_m": flujo_nom_h2_rest,
        "vpa_acum_m": vpa_acum_lista_h2_rest,
        "vpa_total_cop": vpa_restante_h2_cop,
        "vpa_etapa_univ_cop": vpa_etapa_univ_completa_h2_cop,
        "vpa_colegio_cop": vpa_colegio_rest_h2_cop,
        "vpa_univ_cop": vpa_univ_rest_h2_cop,
        "ahorro_mensual_univ_cop": ahorro_mes_univ_h2_cop,
    }

    # Curva Consolidada Restante / Etapa Actual (Hijo 1 + Hijo 2)
    flujo_nom_cons_rest = [round(flujo_nom_h1_rest[i] + (flujo_nom_h2_rest[i] if numero_hijos >= 2 else 0.0), 2) for i in range(horizonte_max_anios)]
    vpa_acum_cons_rest = [round(vpa_acum_lista_h1_rest[i] + (vpa_acum_lista_h2_rest[i] if numero_hijos >= 2 else 0.0), 2) for i in range(horizonte_max_anios)]

    curvas_hijo: Dict[str, Any] = {}
    if modo_horizonte == "restante":
        curvas_hijo["Hijo_1"] = curva_h1_restante
        curvas_hijo["Hijo_2"] = curva_h2_restante
        curvas_hijo["Agustiniano_Suba"] = {
            "edades": eje_anios_rest,
            "flujo_nominal_m": flujo_nom_cons_rest,
            "vpa_acum_m": vpa_acum_cons_rest,
            "vpa_total_cop": round(curva_h1_restante["vpa_total_cop"] + (vpa_restante_h2_cop if numero_hijos >= 2 else 0.0), 2),
            "vpa_colegio_cop": round(curva_h1_restante["vpa_colegio_cop"] + vpa_colegio_rest_h2_cop, 2),
            "vpa_univ_cop": round(curva_h1_restante["vpa_univ_cop"] + vpa_univ_rest_h2_cop, 2),
        }
        for niv_ref in ("Bajo", "Medio", "Alto"):
            mult_ref = 0.65 if niv_ref == "Bajo" else (1.0 if niv_ref == "Medio" else 1.85)
            vpa_ref_acum = 0.0
            lista_ref_acum = []
            flujo_ref_lista = []
            for i in range(horizonte_max_anios):
                f_ref = (1_950_000.0 * mult_ref * numero_hijos * 12.0) * ((1.0 + inf_edu) ** i)
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
        for niv, costos_etapa in perfiles_curva.items():
            c_tmp = _calcular_curva_ciclo_hijo(costos_etapa, edad_fin_ciclo=23, factor_edad_actual=1.0)
            curvas_hijo[niv] = c_tmp
        curvas_hijo["Hijo_1"] = curva_h1_completo
        curvas_hijo["Hijo_2"] = curva_h2_completo
        curvas_hijo["Agustiniano_Suba"] = {
            "edades": edades_0_23,
            "flujo_nominal_m": [round(curva_h1_completo["flujo_nominal_m"][i] + (curva_h2_completo["flujo_nominal_m"][i] if numero_hijos >= 2 else 0.0), 2) for i in range(24)],
            "vpa_acum_m": [round(curva_h1_completo["vpa_acum_m"][i] + (curva_h2_completo["vpa_acum_m"][i] if numero_hijos >= 2 else 0.0), 2) for i in range(24)],
            "vpa_total_cop": round(curva_h1_completo["vpa_total_cop"] + (curva_h2_completo["vpa_total_cop"] if numero_hijos >= 2 else 0.0), 2),
            "vpa_colegio_cop": round(curva_h1_completo["vpa_colegio_cop"] + curva_h2_completo["vpa_colegio_cop"], 2),
            "vpa_univ_cop": round(curva_h1_completo["vpa_univ_cop"] + curva_h2_completo["vpa_univ_cop"], 2),
        }

    vpa_ciclo_completo_consolidado = round(
        curva_h1_completo["vpa_total_cop"] + (curva_h2_completo["vpa_total_cop"] if numero_hijos >= 2 else 0.0),
        2,
    )
    vpa_restante_consolidado = (
        curva_h1_restante["vpa_total_cop"]
        + (vpa_restante_h2_cop if numero_hijos >= 2 else 0.0)
        + (
            ((curva_h1_restante["vpa_total_cop"] + vpa_restante_h2_cop) / 2.0) * (numero_hijos - 2)
            if numero_hijos > 2
            else 0.0
        )
    )
    ahorro_univ_restante_consolidado = (
        curva_h1_restante["ahorro_mensual_univ_cop"]
        + (ahorro_mes_univ_h2_cop if numero_hijos >= 2 else 0.0)
    )

    # 3. Evaluación Actuarial y Monte Carlo de las 3 Decisiones Vitales (Nelson)
    decisiones_eval = {}
    trayectorias_mc = {}

    ahorro_sinergia_pareja = (ingreso_neto_hogar + ingreso_pareja) * 0.08
    cuota_boda_24m = costo_boda / 24.0
    balance_neto_casarse = cuota_boda_24m - ahorro_sinergia_pareja

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
            plazo_credito_meses=plazo_credito,
            iteraciones_montecarlo=1000,
            config=cfg_custom,
            numero_hijos=numero_hijos,
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
            res_d["ahorro_sinergia_mensual_cop"] = round(ahorro_sinergia_pareja, 2)
            res_d["flujo_neto_sinergia_cop"] = round(ahorro_sinergia_pareja - cuota_boda_24m, 2)
        elif dec == "HIJOS":
            if modo_horizonte == "restante":
                res_d["vpa_decision_cop"] = round(vpa_restante_consolidado, 2)
            else:
                res_d["vpa_decision_cop"] = round(vpa_ciclo_completo_consolidado, 2)
            res_d["ahorro_mensual_requerido_cop"] = round(ahorro_univ_restante_consolidado, 2)
            res_d["recomendacion_actuarial_y_legal"] = (
                f"Hijo 1 en Colegio Agustiniano Suba ({edad_hijo1}a, {etiqueta_grado_h1}, {'sin ruta' if transporte_mes == 0 else 'con ruta'}: faltan {anios_colegio_rest_h1}a col. + {anios_univ_rest_h1}a univ.) "
                f"+ Hijo 2 ({edad_hijo2}a, {f'{semestre_actual_h2}° Semestre Univ. @ ${semestre_univ_h2:,.0f}/sem, faltan {semestres_restantes_h2} semestres' if hijo2_en_univ else 'Colegio + Univ.'}). "
                f"Con Excedente=${excedente_mensual:,.0f} y Ahorro=${liquidez_emergencia:,.0f}, cubrir flujo consolidado de ${pago_mes_directo_total:,.0f} COP/mes."
            )
            vpa_1_hijo_completo = round(vpa_ciclo_completo_consolidado / max(1, numero_hijos), 2)
            res_d["desglose_colegio"] = {
                "numero_hijos": numero_hijos,
                "edad_actual": edad_actual_hijo,
                "edad_hijo1": edad_hijo1,
                "edad_hijo2": edad_hijo2,
                "edad_inicio_curva": edad_inicio_curva,
                "modo_horizonte": modo_horizonte,
                "hijo1": {
                    "edad": edad_hijo1,
                    "etiqueta_grado": etiqueta_grado_h1,
                    "en_universidad": False,
                    "anios_colegio_rest": anios_colegio_rest_h1,
                    "anios_univ_rest": anios_univ_rest_h1,
                    "pension_mes_cop": round(pension_colegio_mes, 2),
                    "matricula_anual_cop": round(matricula_anual, 2),
                    "matricula_prorrateada_mes_cop": round(matricula_anual / 12.0, 2),
                    "ruta_mes_cop": round(transporte_mes, 2),
                    "manutencion_y_otros_mes_cop": round(manutencion_hijo_mes + otros_gastos_mes, 2),
                    "gasto_mes_directo_cop": round(pago_mes_directo_h1, 2),
                    "impacto_mes_anualizado_cop": round(costo_mes_equiv_h1, 2),
                    "flujo_anual_hoy_cop": round(flujo_anual_h1, 2),
                    "vpa_ciclo_completo_cop": curva_h1_completo["vpa_total_cop"],
                    "vpa_restante_edad_actual_cop": curva_h1_restante["vpa_total_cop"],
                    "vpa_saldo_neto_cop": curva_h1_restante["vpa_saldo_neto_cop"],
                    "vpa_colegio_restante_cop": curva_h1_restante["vpa_colegio_cop"],
                    "vpa_univ_proyectada_cop": curva_h1_restante["vpa_univ_cop"],
                    "ahorro_mensual_univ_cop": curva_h1_restante["ahorro_mensual_univ_cop"],
                },
                "hijo2": {
                    "edad": edad_hijo2,
                    "en_universidad": hijo2_en_univ,
                    "semestre_actual": semestre_actual_h2,
                    "semestres_restantes": semestres_restantes_h2,
                    "valor_semestre_univ_cop": round(semestre_univ_h2, 2),
                    "matricula_univ_mensualizada_cop": round(matricula_univ_mes_h2, 2),
                    "matricula_univ_anual_cop": round(matricula_univ_anual_h2, 2),
                    "pension_mes_cop": round(pension_hijo2_mes, 2),
                    "matricula_anual_cop": round(matricula_hijo2_anual, 2),
                    "matricula_prorrateada_mes_cop": round(matricula_hijo2_anual / 12.0, 2),
                    "ruta_mes_cop": 0.0 if hijo2_en_univ else round(transporte_mes, 2),
                    "manutencion_y_otros_mes_cop": round(manutencion_hijo_mes + otros_gastos_mes, 2),
                    "gasto_mes_directo_cop": round(pago_mes_directo_h2, 2),
                    "impacto_mes_anualizado_cop": round(costo_mes_equiv_h2, 2),
                    "flujo_anual_hoy_cop": round(flujo_anual_h2, 2),
                    "vpa_ciclo_completo_cop": curva_h2_completo["vpa_total_cop"],
                    "vpa_restante_edad_actual_cop": vpa_restante_h2_cop,
                    "vpa_etapa_univ_cop": vpa_etapa_univ_completa_h2_cop,
                    "vpa_colegio_restante_cop": vpa_colegio_rest_h2_cop,
                    "vpa_univ_proyectada_cop": vpa_univ_rest_h2_cop,
                    "ahorro_mensual_univ_cop": ahorro_mes_univ_h2_cop,
                },
                "consolidado": {
                    "numero_hijos": numero_hijos,
                    "hijo2_en_universidad": hijo2_en_univ,
                    "semestre_actual_h2": semestre_actual_h2,
                    "educacion_h1_colegio_mes_cop": round(pension_colegio_mes + transporte_mes + (matricula_anual / 12.0), 2),
                    "educacion_h2_univ_mes_cop": round(matricula_univ_mes_h2 if hijo2_en_univ else (pension_hijo2_mes + transporte_mes + (matricula_hijo2_anual / 12.0)), 2),
                    "pensiones_sumadas_mes_cop": round(pension_colegio_mes + (matricula_univ_mes_h2 if hijo2_en_univ else pension_hijo2_mes), 2),
                    "matriculas_sumadas_anual_cop": round(matricula_anual + (matricula_univ_anual_h2 if hijo2_en_univ else matricula_hijo2_anual), 2),
                    "rutas_sumadas_mes_cop": round(transporte_mes * (1 if hijo2_en_univ else numero_hijos), 2),
                    "manutencion_y_otros_sumados_mes_cop": round((manutencion_hijo_mes + otros_gastos_mes) * numero_hijos, 2),
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
        decisiones_eval[dec] = res_d

        rng = random.Random(20261110)
        impacto_mc = balance_neto_casarse if dec == "CASARSE" else res_d["impacto_flujo_mensual_inmediato_cop"]
        flujos_sim = []
        for _ in range(1000):
            c_ing = rng.gauss(1.0, 0.08)
            c_gas = rng.gauss(1.0, 0.07)
            f_neto = excedente_mensual * c_ing - impacto_mc * c_gas + (liquidez_emergencia / 24.0)
            flujos_sim.append(round(f_neto / 1e6, 3))
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
                plazo_credito_meses=plazo_credito,
                iteraciones_montecarlo=350,
                config=cfg_custom,
                numero_hijos=numero_hijos,
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
        ingreso_bruto_mensual_cop=6_500_000.0,
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
        ingreso_familiar_neto_cop=ingreso_neto_hogar,
    )

    return {
        "timestamp_calculo": datetime.now().strftime("%H:%M:%S"),
        "parametros_activos": {
            "ingreso_neto_hogar": ingreso_neto_hogar,
            "excedente_mensual": excedente_mensual,
            "excedente_m": round(excedente_mensual / 1e6, 2),
            "numero_hijos": numero_hijos,
            "edad_actual_hijo": edad_actual_hijo,
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
<title>Asesor Financiero OED — Interfaz Gráfica Local (Nelson Angel)</title>
<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
<style>
  :root {
    --bg: #f4f7fb;
    --card: #ffffff;
    --primary: #0f4c81;
    --accent: #1e88e5;
    --success: #2e7d32;
    --warn: #ef6c00;
    --danger: #c62828;
    --text: #1c2833;
    --muted: #566573;
    --border: #dce4ec;
  }
  * { box-sizing: border-box; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }
  body { margin: 0; background: var(--bg); color: var(--text); }
  header {
    background: linear-gradient(135deg, #0a2540 0%, #0f4c81 60%, #1e88e5 100%);
    color: #fff; padding: 16px 28px; display: flex; justify-content: space-between; align-items: center;
    box-shadow: 0 3px 12px rgba(0,0,0,0.15);
  }
  header h1 { margin: 0; font-size: 1.3rem; font-weight: 700; }
  header p { margin: 4px 0 0; font-size: 0.86rem; opacity: 0.9; }
  .badge-top {
    background: rgba(255,255,255,0.16); border: 1px solid rgba(255,255,255,0.3);
    padding: 7px 14px; border-radius: 20px; font-size: 0.82rem; font-weight: 600;
  }
  .tabs {
    display: flex; gap: 8px; padding: 12px 28px 0; background: #e9eff6; border-bottom: 1px solid var(--border);
  }
  .tab-btn {
    border: none; background: transparent; padding: 10px 18px; font-size: 0.92rem; font-weight: 600;
    color: var(--muted); cursor: pointer; border-bottom: 3px solid transparent; border-radius: 8px 8px 0 0;
  }
  .tab-btn.active { background: var(--card); color: var(--primary); border-bottom-color: var(--accent); }
  .container { max-width: 1480px; margin: 0 auto; padding: 18px 24px 40px; }
  .tab-content { display: none; }
  .tab-content.active { display: block; }
  .grid-sidebar { display: grid; grid-template-columns: 375px 1fr; gap: 20px; align-items: start; }
  .card {
    background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 16px;
    box-shadow: 0 2px 6px rgba(15,76,129,0.05); margin-bottom: 16px;
  }
  .card h3 { margin: 0 0 10px; font-size: 1.0rem; color: var(--primary); }
  .sub-panel {
    background: #f8fafd; border: 1px solid #d0e1f9; border-radius: 9px; padding: 11px 12px; margin-bottom: 12px;
  }
  .sub-panel h4 { margin: 0 0 8px; font-size: 0.86rem; color: #0d47a1; }
  .child-input-box {
    border-radius: 8px; padding: 9px 10px; margin-bottom: 9px; border: 1px solid #cbd5e1;
  }
  .child-input-h1 { background: #eff6ff; border-left: 4px solid #1e88e5; }
  .child-input-h2 { background: #faf5ff; border-left: 4px solid #8e24aa; }
  .child-input-box h5 { margin: 0 0 6px; font-size: 0.82rem; font-weight: 700; color: #0f4c81; }
  .children-grid {
    display: grid; grid-template-columns: 1fr 1fr 1.15fr; gap: 14px; margin-bottom: 16px;
  }
  .child-card {
    background: #ffffff; border: 1px solid var(--border); border-radius: 12px; padding: 14px 16px;
    box-shadow: 0 3px 10px rgba(15,76,129,0.06); position: relative; overflow: hidden;
  }
  .child-card.h1 { border-top: 5px solid #1e88e5; }
  .child-card.h2 { border-top: 5px solid #8e24aa; }
  .child-card.consolidado {
    background: linear-gradient(180deg, #f0f7ff 0%, #ffffff 100%);
    border: 2px solid #0f4c81; border-top: 5px solid #0a2540;
    box-shadow: 0 4px 14px rgba(10,37,64,0.12);
  }
  .child-badge {
    display: inline-block; padding: 3px 10px; border-radius: 14px; font-size: 0.74rem; font-weight: 700;
    margin-bottom: 6px;
  }
  .badge-h1 { background: #e3f2fd; color: #0d47a1; }
  .badge-h2 { background: #f3e5f5; color: #6a1b9a; }
  .badge-cons { background: #0a2540; color: #ffffff; }
  .child-vpa-main { font-size: 1.28rem; font-weight: 800; color: #0a2540; margin: 2px 0 4px; }
  .child-vpa-sub { font-size: 0.77rem; color: var(--muted); margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px dashed #cbd5e1; }
  .metric-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
  .metric-table td { padding: 4px 0; border-bottom: 1px solid #f1f5f9; }
  .metric-table td:last-child { text-align: right; font-weight: 700; color: #1e293b; }
  .metric-table tr.total-row td {
    border-top: 2px solid #cbd5e1; border-bottom: none; padding-top: 7px; font-size: 0.85rem; font-weight: 800; color: #0d47a1;
  }
  .metric-table tr.highlight-row td {
    background: #fff8e1; padding: 5px 6px; border-radius: 4px; color: #b71c1c; font-weight: 800;
  }
  .section-label {
    font-size: 0.88rem; font-weight: 800; color: var(--primary); margin: 0 0 10px;
    display: flex; align-items: center; justify-content: space-between;
  }
  .form-row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
  .form-group { margin-bottom: 9px; }
  .form-group label { display: block; font-size: 0.78rem; font-weight: 600; color: var(--muted); margin-bottom: 3px; }
  .form-group input, .form-group select {
    width: 100%; padding: 7px 9px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.88rem;
  }
  .btn {
    display: inline-block; width: 100%; padding: 10px 14px; border: none; border-radius: 8px;
    font-weight: 700; font-size: 0.9rem; cursor: pointer; text-align: center; transition: 0.2s;
    margin-top: 6px;
  }
  .btn-primary { background: var(--accent); color: #fff; }
  .btn-primary:hover { background: #1565c0; transform: translateY(-1px); }
  .btn-success { background: var(--success); color: #fff; }
  .btn-danger { background: var(--danger); color: #fff; }
  .status-banner {
    margin-top: 9px; padding: 7px 10px; border-radius: 8px; font-size: 0.8rem; font-weight: 600;
    background: #e8f5e9; color: #1b5e20; text-align: center; border: 1px solid #a5d6a7;
  }
  .kpi-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 16px; }
  .kpi-card {
    background: var(--card); border: 1px solid var(--border); border-left: 5px solid var(--accent);
    border-radius: 10px; padding: 14px 16px; transition: box-shadow 0.25s;
  }
  .kpi-card.flash { box-shadow: 0 0 0 3px rgba(30,136,229,0.35); }
  .kpi-title { font-size: 0.78rem; font-weight: 700; color: var(--muted); text-transform: uppercase; }
  .kpi-val { font-size: 1.3rem; font-weight: 800; color: var(--text); margin: 5px 0; }
  .kpi-sub { font-size: 0.79rem; color: var(--muted); line-height: 1.45; }
  .pill { display: inline-block; padding: 3px 9px; border-radius: 12px; font-size: 0.74rem; font-weight: 700; }
  .pill-ok { background: #e8f5e9; color: #2e7d32; }
  .pill-warn { background: #fff3e0; color: #ef6c00; }
  .pill-bad { background: #ffebee; color: #c62828; }
  .legal-box {
    background: #f0f6ff; border-left: 4px solid var(--primary); padding: 12px 14px;
    border-radius: 6px; font-size: 0.84rem; line-height: 1.45; margin-bottom: 12px;
  }
  .code-box {
    background: #1e293b; color: #a7f3d0; font-family: Consolas, monospace; font-size: 0.8rem;
    padding: 10px 12px; border-radius: 7px; overflow-x: auto; margin-top: 8px;
  }
  .charts-2col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  @media (max-width: 1100px) {
    .grid-sidebar, .children-grid, .kpi-row, .charts-2col { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>

<header>
  <div>
    <h1>🛡️ Asesor Financiero e Inversiones OED — Interfaz Gráfica Local</h1>
    <p>Líder de Gobierno de Datos y Módulo 5 Actuarial: <strong>Nelson Angel</strong> (Rama <code>nean</code>) | Tarifas Reales <strong>Colegio Agustiniano Suba</strong></p>
  </div>
  <div class="badge-top" id="badge-hora">🔒 Ley 1581/2012 &bull; Ley 1266/2008 &bull; Monte Carlo Activo</div>
</header>

<div class="tabs">
  <button class="tab-btn active" onclick="abrirTab('tab-mod5', this)">📊 Módulo 5: Simulador Actuarial y Colegio Agustiniano Suba</button>
  <button class="tab-btn" onclick="abrirTab('tab-habeas', this)">🔐 Fase 0: Gobierno de Datos y Habeas Data (Nelson)</button>
  <button class="tab-btn" onclick="abrirTab('tab-integrado', this)">🚀 Caso Maestro OED: Los 6 Módulos Integrados</button>
</div>

<div class="container">

  <!-- ==================== PESTAÑA 1: MÓDULO 5 ACTUARIAL (NELSON) ==================== -->
  <div id="tab-mod5" class="tab-content active">
    <div class="grid-sidebar">
      <div class="card">
        <h3>⚙️ 1. Flujo de Caja del Hogar (Sin Excedente / Sin Ahorro)</h3>
        <div class="form-row-2">
          <div class="form-group">
            <label>Ingreso Neto Hogar ($)</label>
            <input type="number" id="ingreso_neto_hogar" value="9115000" step="100000" oninput="actualizarDashboard()">
          </div>
          <div class="form-group">
            <label>Excedente Libre Mes ($)</label>
            <input type="number" id="excedente_mensual" value="0" step="50000" oninput="actualizarDashboard()">
          </div>
        </div>
        <div class="form-group">
          <label>Liquidez Fondo de Emergencia / Ahorro ($ COP)</label>
          <input type="number" id="liquidez_emergencia" value="0" step="500000" oninput="actualizarDashboard()">
        </div>

        <!-- SUB-PANEL: HIJO 1 (16A GRADO 11 AGUSTINIANO, SIN RUTA) + HIJO 2 (20A, 7° SEMESTRE UNIVERSIDAD @ $13M) -->
        <div class="sub-panel">
          <h4>🎓 2. Hijos: Hijo 1 (16a Grado 11) + Hijo 2 (20a Sem. 7 Univ.)</h4>
          <div class="form-row-2">
            <div class="form-group">
              <label>Perfil Educativo</label>
              <select id="nivel_costo_hijo" onchange="actualizarDashboard()">
                <option value="Agustiniano_Suba" selected>🎓 Real: Agustiniano + Univ.</option>
                <option value="Bajo">Colombia Bajo (0.65x)</option>
                <option value="Medio">Colombia Medio (1.0x)</option>
                <option value="Alto">Colombia Alto (1.85x)</option>
              </select>
            </div>
            <div class="form-group">
              <label>Horizonte Cálculo VPA</label>
              <select id="modo_horizonte" onchange="actualizarDashboard()">
                <option value="ciclo_completo" selected>Ciclo Completo (0 a 23a)</option>
                <option value="restante">Etapa Superior / Carrera Univ.</option>
              </select>
            </div>
          </div>

          <!-- CUADRO CONFIGURACIÓN HIJO 1 (COLEGIO AGUSTINIANO SUBA — 16 AÑOS, GRADO 11, SIN RUTA) -->
          <div class="child-input-box child-input-h1">
            <h5>👦 Cuadro Hijo 1 — Agustiniano Suba (16a, Grado 11, Sin Ruta)</h5>
            <div class="form-row-2">
              <div class="form-group">
                <label>Grado Escolar Hijo 1</label>
                <select id="grado_agustiniano_h1" onchange="aplicarGradoAgustiniano(1)">
                  <option value="once_2026" selected>Grado 11° ($1.421k | 16a)</option>
                  <option value="decimo_2026">Grado 10° ($1.421k | 15a)</option>
                  <option value="septimo_noveno_2026">7°, 8° y 9° ($1.431k)</option>
                  <option value="cuarto_sexto_2026">4°, 5° y 6° ($1.438k)</option>
                  <option value="primaria_2_3_2026">2° y 3° Primaria ($1.454k)</option>
                  <option value="transicion_1_2026">Transición / 1° ($1.464k)</option>
                  <option value="jardin_2026">Jardín ($1.478k)</option>
                  <option value="historico_base">Base Web (~2021: $946k)</option>
                </select>
              </div>
              <div class="form-group">
                <label>Edad Actual Hijo 1 (Años)</label>
                <input type="number" id="edad_hijo1" value="16" min="0" max="21" oninput="actualizarDashboard()">
              </div>
            </div>
            <div class="form-row-2">
              <div class="form-group" style="margin-bottom:2px;">
                <label>Pensión Mes Hijo 1 ($)</label>
                <input type="number" id="pension_colegio_mes" value="1421000" step="10000" oninput="actualizarDashboard()">
              </div>
              <div class="form-group" style="margin-bottom:2px;">
                <label>Matr.+Cobros Hijo 1 ($/año)</label>
                <input type="number" id="matricula_anual" value="1800000" step="10000" oninput="actualizarDashboard()">
              </div>
            </div>
          </div>

          <!-- CUADRO CONFIGURACIÓN HIJO 2 (20 AÑOS, 7° SEMESTRE DE UNIVERSIDAD @ $13 MILLONES) -->
          <div class="child-input-box child-input-h2">
            <h5 style="color:#6a1b9a;">👧 Cuadro Hijo 2 — 7° Semestre Universidad (20a, $13M/sem)</h5>
            <div class="form-row-2">
              <div class="form-group">
                <label>Etapa / Semestre Hijo 2</label>
                <select id="etapa_hijo2" onchange="aplicarGradoAgustiniano(2)">
                  <option value="univ_sem7" selected>🎓 Univ. 7° Semestre ($13M)</option>
                  <option value="univ_sem6">🎓 Univ. 6° Semestre ($13M)</option>
                  <option value="univ_sem8">🎓 Univ. 8° Semestre ($13M)</option>
                  <option value="univ_sem9">🎓 Univ. 9° Semestre ($13M)</option>
                  <option value="univ_sem10">🎓 Univ. 10° Semestre ($13M)</option>
                  <option value="once_2026">🏫 Colegio Grado 11° ($1.421k)</option>
                </select>
              </div>
              <div class="form-group">
                <label>Semestre Actual (de 10)</label>
                <input type="number" id="semestre_actual_h2" value="7" min="1" max="10" oninput="sincronizarSemestreHijo2()">
              </div>
            </div>
            <div class="form-row-2">
              <div class="form-group" style="margin-bottom:2px;">
                <label>Valor Semestre Hijo 2 ($)</label>
                <input type="number" id="semestre_univ_h2" value="13000000" step="500000" oninput="actualizarDashboard()">
              </div>
              <div class="form-group" style="margin-bottom:2px;">
                <label>Edad Actual Hijo 2 (Años)</label>
                <input type="number" id="edad_hijo2" value="20" min="15" max="25" oninput="actualizarDashboard()">
              </div>
            </div>
            <input type="hidden" id="pension_hijo2_mes" value="1421000">
            <input type="hidden" id="matricula_hijo2_anual" value="1800000">
          </div>

          <input type="hidden" id="numero_hijos" value="2">
          <div class="form-row-2">
            <div class="form-group">
              <label>Ruta Escolar Suba (Hijo 1)</label>
              <select id="transporte_mes" onchange="actualizarDashboard()">
                <option value="0" selected>Sin Ruta ($0)</option>
                <option value="220000">Media Ruta Suba 2026 ($220.000)</option>
                <option value="380000">Completa Suba 2026 ($380.000)</option>
                <option value="440000">Lisboa / Sta. Rita 2026 ($440.000)</option>
                <option value="540000">Fuera de Suba 2026 ($540.000)</option>
              </select>
            </div>
            <div class="form-group">
              <label>Manutención Mes x Hijo ($)</label>
              <input type="number" id="manutencion_hijo_mes" value="1150000" step="50000" title="Alimentación, Salud/Prepagada, Vestuario, Servicios y Recreación por cada hijo" oninput="actualizarDashboard()">
            </div>
          </div>
          <div class="form-row-2">
            <div class="form-group">
              <label>Transp./Materiales/Extra x Hijo ($)</label>
              <input type="number" id="otros_gastos_mes" value="300000" step="25000" oninput="actualizarDashboard()">
            </div>
            <div class="form-group">
              <label>Semestre Univ. Proy. Hijo 1 ($)</label>
              <input type="number" id="semestre_univ_hoy" value="13000000" step="500000" oninput="actualizarDashboard()">
            </div>
          </div>
          <div class="form-group">
            <label>Inflación Educativa Anual MEN (% EA)</label>
            <input type="text" id="inflacion_educativa_pct" value="7.5" oninput="actualizarDashboard()">
          </div>
        </div>

        <!-- PARÁMETROS BODA Y CRÉDITO -->
        <div class="form-row-2">
          <div class="form-group">
            <label>💍 Costo Boda ($ COP)</label>
            <input type="number" id="costo_boda" value="18000000" step="1000000" oninput="actualizarDashboard()">
          </div>
          <div class="form-group">
            <label>💑 Ingreso Pareja ($ COP)</label>
            <input type="number" id="ingreso_pareja" value="4500000" step="250000" oninput="actualizarDashboard()">
          </div>
        </div>
        <div class="form-row-2">
          <div class="form-group">
            <label>🚗 Monto Crédito ($ COP)</label>
            <input type="number" id="monto_credito" value="45000000" step="1000000" oninput="actualizarDashboard()">
          </div>
          <div class="form-group">
            <label>📈 Tasa (% EA) / Plazo (m)</label>
            <div style="display:flex;gap:4px;">
              <input type="text" id="tasa_ea_credito" value="16.5" oninput="actualizarDashboard()">
              <input type="number" id="plazo_credito" value="48" step="6" oninput="actualizarDashboard()">
            </div>
          </div>
        </div>

        <button type="button" id="btn-recalcular" class="btn btn-primary" onclick="actualizarDashboard('ninguna', true)">
          🔄 Recalcular Modelo Actuarial y Monte Carlo
        </button>
        <div id="status-calculo" class="status-banner">✅ Hijo 1 (16a Grado 11, Sin Ruta) + Hijo 2 (20a Sem. 7 Univ.)</div>
      </div>

      <div>
        <!-- SECCIÓN SUPERIOR: HIJO 1 | HIJO 2 | CONSOLIDADO FAMILIAR -->
        <div class="section-label">
          <span>🎓 Desglose Separado por Hijo y Cifra Consolidada Familiar — Hijo 1 (16a, Grado 11) + Hijo 2 (20a, 7° Sem. Univ.)</span>
          <span style="font-size:0.78rem;color:var(--muted);font-weight:600;">Hijo 1 (Sin Ruta) | Hijo 2 (Sem. 7 @ $13M) | Consolidado</span>
        </div>
        <div class="children-grid" id="grid-hijos-detalle"></div>

        <!-- SECCIÓN COMPARATIVA DE LAS 3 DECISIONES VITALES -->
        <div class="section-label" style="margin-top:4px;">
          <span>⚖️ Comparativa de Viabilidad de las 3 Decisiones de Vida (Módulo 5 — Simulación Monte Carlo)</span>
        </div>
        <div class="kpi-row" id="kpis-decisiones"></div>

        <div class="card">
          <h3 id="titulo-curva-hijo">📈 1. Curva Actuarial de Costos Educativos (Hijo 1 vs. Hijo 2 vs. Consolidado)</h3>
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
          <input type="text" id="usuario_id" value="CC_1020304050_NELSON_DEMO" oninput="actualizarDashboard()">
        </div>
        <div class="form-group">
          <label>
            <input type="checkbox" id="acepta_habeas" checked onchange="actualizarDashboard()" style="width:auto;margin-right:6px;">
            Autorizo tratamiento 100% local (Ley 1581/2012)
          </label>
        </div>
        <button type="button" class="btn btn-success" onclick="actualizarDashboard('guardar', true)">💾 Cifrar y Guardar Perfil en Disco (.oed)</button>
        <button type="button" class="btn btn-danger" onclick="actualizarDashboard('olvido', true)">🗑️ Ejercer Derecho al Olvido (Art. 8 Ley 1581)</button>

        <hr style="border:0;border-top:1px solid var(--border);margin:16px 0;">
        <h3>⚖️ Calculadora Datacrédito (Ley 1266/2008 & Ley 2157/2021)</h3>
        <div class="form-group">
          <label>Meses en Mora antes del Pago: <span id="lbl-mora" style="color:var(--primary);font-weight:800;">14</span> meses</label>
          <input type="range" id="meses_mora" min="0" max="36" value="14" oninput="document.getElementById('lbl-mora').innerText=this.value; actualizarDashboard()">
        </div>
        <div class="form-group">
          <label>
            <input type="checkbox" id="obligacion_pagada" checked onchange="actualizarDashboard()" style="width:auto;margin-right:6px;">
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

</div>

<script>
const TARIFAS_AGUSTINIANO = {
  jardin_2026:         { matricula: 1890000, pension: 1478000, edad: 4 },
  transicion_1_2026:   { matricula: 1860000, pension: 1464000, edad: 6 },
  primaria_2_3_2026:   { matricula: 1845000, pension: 1454000, edad: 8 },
  cuarto_sexto_2026:   { matricula: 1825000, pension: 1438000, edad: 10 },
  septimo_noveno_2026: { matricula: 1815000, pension: 1431000, edad: 12 },
  decimo_2026:         { matricula: 1800000, pension: 1421000, edad: 15 },
  once_2026:           { matricula: 1800000, pension: 1421000, edad: 16 },
  historico_base:      { matricula: 1051500, pension: 946300,  edad: 12 }
};

function aplicarGradoAgustiniano(numHijo = 1) {
  if (numHijo === 1) {
    const g1 = document.getElementById('grado_agustiniano_h1').value;
    const info1 = TARIFAS_AGUSTINIANO[g1];
    if (info1) {
      document.getElementById('pension_colegio_mes').value = info1.pension;
      document.getElementById('matricula_anual').value = info1.matricula;
      document.getElementById('edad_hijo1').value = info1.edad;
    }
  } else {
    const e2 = document.getElementById('etapa_hijo2').value;
    if (e2 === 'univ_sem7') {
      document.getElementById('semestre_actual_h2').value = 7;
      document.getElementById('semestre_univ_h2').value = 13000000;
      document.getElementById('edad_hijo2').value = 20;
    } else if (e2 === 'univ_sem6') {
      document.getElementById('semestre_actual_h2').value = 6;
      document.getElementById('semestre_univ_h2').value = 13000000;
      document.getElementById('edad_hijo2').value = 20;
    } else if (e2 === 'univ_sem8') {
      document.getElementById('semestre_actual_h2').value = 8;
      document.getElementById('semestre_univ_h2').value = 13000000;
      document.getElementById('edad_hijo2').value = 21;
    } else if (e2 === 'univ_sem9') {
      document.getElementById('semestre_actual_h2').value = 9;
      document.getElementById('semestre_univ_h2').value = 13000000;
      document.getElementById('edad_hijo2').value = 21;
    } else if (e2 === 'univ_sem10') {
      document.getElementById('semestre_actual_h2').value = 10;
      document.getElementById('semestre_univ_h2').value = 13000000;
      document.getElementById('edad_hijo2').value = 22;
    } else if (TARIFAS_AGUSTINIANO[e2]) {
      const info2 = TARIFAS_AGUSTINIANO[e2];
      document.getElementById('pension_hijo2_mes').value = info2.pension;
      document.getElementById('matricula_hijo2_anual').value = info2.matricula;
      document.getElementById('edad_hijo2').value = info2.edad;
    }
  }
  document.getElementById('nivel_costo_hijo').value = 'Agustiniano_Suba';
  actualizarDashboard('ninguna', true);
}

function sincronizarSemestreHijo2() {
  const s = Math.round(numVal('semestre_actual_h2', 7));
  const sel = document.getElementById('etapa_hijo2');
  if (sel && sel.value.startsWith('univ_sem') && s >= 6 && s <= 10) {
    sel.value = 'univ_sem' + s;
  }
  actualizarDashboard();
}

function fmtCOP(v) {
  return '$' + Math.round(v).toLocaleString('es-CO') + ' COP';
}

function numVal(id, defVal) {
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

async function actualizarDashboard(accionDisco = 'ninguna', esClickBoton = false) {
  const btn = document.getElementById('btn-recalcular');
  const statusEl = document.getElementById('status-calculo');
  if (esClickBoton && btn) {
    btn.innerText = '⏳ Recalculando 1.000 escenarios...';
    btn.style.background = '#0f4c81';
  }

  const obPagadaEl = document.getElementById('obligacion_pagada');
  const payload = {
    usuario_id: document.getElementById('usuario_id').value,
    acepta_habeas: document.getElementById('acepta_habeas').checked,
    meses_mora: Math.round(numVal('meses_mora', 14)),
    obligacion_pagada: obPagadaEl ? obPagadaEl.checked : true,
    accion_disco: accionDisco,
    ingreso_neto_hogar: numVal('ingreso_neto_hogar', 9115000),
    excedente_mensual: numVal('excedente_mensual', 0),
    liquidez_emergencia: numVal('liquidez_emergencia', 0),
    nivel_costo_hijo: document.getElementById('nivel_costo_hijo').value,
    modo_horizonte: document.getElementById('modo_horizonte').value,
    grado_agustiniano_h1: document.getElementById('grado_agustiniano_h1').value,
    numero_hijos: Math.round(numVal('numero_hijos', 2)),
    edad_hijo1: Math.round(numVal('edad_hijo1', 16)),
    edad_hijo2: Math.round(numVal('edad_hijo2', 20)),
    etapa_hijo2: document.getElementById('etapa_hijo2').value,
    semestre_actual_h2: Math.round(numVal('semestre_actual_h2', 7)),
    semestre_univ_h2: numVal('semestre_univ_h2', 13000000),
    pension_colegio_mes: numVal('pension_colegio_mes', 1421000),
    matricula_anual: numVal('matricula_anual', 1800000),
    pension_hijo2_mes: numVal('pension_hijo2_mes', 1421000),
    matricula_hijo2_anual: numVal('matricula_hijo2_anual', 1800000),
    transporte_mes: numVal('transporte_mes', 0),
    manutencion_hijo_mes: numVal('manutencion_hijo_mes', 1150000),
    otros_gastos_mes: numVal('otros_gastos_mes', 300000),
    semestre_univ_hoy: numVal('semestre_univ_hoy', 13000000),
    inflacion_educativa_pct: numVal('inflacion_educativa_pct', 7.5),
    costo_boda: numVal('costo_boda', 18000000),
    ingreso_pareja: numVal('ingreso_pareja', 4500000),
    monto_credito: numVal('monto_credito', 45000000),
    tasa_ea_credito: numVal('tasa_ea_credito', 16.5),
    plazo_credito: Math.round(numVal('plazo_credito', 48)),
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
      statusEl.innerText = `✅ Recalculado (${data.timestamp_calculo}) | Hijo 1 (${payload.edad_hijo1}a) + Hijo 2 (${payload.edad_hijo2}a, ${payload.semestre_actual_h2}° Sem.)`;
      statusEl.style.background = '#e8f5e9';
      statusEl.style.color = '#1b5e20';
    }
    document.getElementById('badge-hora').innerText = '🔒 Actualizado: ' + data.timestamp_calculo + ' | Agustiniano + Univ. $13M';
  } catch (err) {
    if (statusEl) {
      statusEl.innerText = '⚠️ Error conectando con servidor Python local: ' + err;
      statusEl.style.background = '#ffebee';
      statusEl.style.color = '#c62828';
    }
  } finally {
    if (esClickBoton && btn) {
      setTimeout(() => {
        btn.innerText = '🔄 Recalcular Modelo Actuarial y Monte Carlo';
        btn.style.background = '';
      }, 350);
    }
  }
}

function renderizarTodo(data, animar = false) {
  const decs = data.actuaria_mod5.decisiones;
  const infoHijos = decs.HIJOS.desglose_colegio || {};
  const h1 = infoHijos.hijo1 || {};
  const h2 = infoHijos.hijo2 || {};
  const cons = infoHijos.consolidado || {};
  const esCompleto = infoHijos.modo_horizonte === 'ciclo_completo';

  // 1. RENDERIZAR LOS 3 CUADROS EJECUTIVOS DE HIJOS: HIJO 1 | HIJO 2 | CONSOLIDADO TOTAL
  const vpaH1Mostrar = esCompleto ? h1.vpa_ciclo_completo_cop : h1.vpa_restante_edad_actual_cop;
  const vpaH2Mostrar = esCompleto ? h2.vpa_ciclo_completo_cop : h2.vpa_restante_edad_actual_cop;
  const vpaConsMostrar = esCompleto ? cons.vpa_ciclo_completo_total_cop : cons.vpa_restante_total_cop;

  const subH2 = h2.en_universidad ? `
        🎓 VPA Ciclo Completo (0–23a): <strong>${fmtCOP(h2.vpa_ciclo_completo_cop)}</strong><br>
        🏛️ Carrera 10 Sem. + Posgrado: <strong>${fmtCOP(h2.vpa_etapa_univ_cop || h2.vpa_restante_edad_actual_cop)}</strong>
  ` : `
        🏫 VPA Ciclo Completo (0–22a): <strong>${fmtCOP(h2.vpa_ciclo_completo_cop)}</strong><br>
        🎓 VPA Capitalizado Edad Actual: <strong>${fmtCOP(h2.vpa_restante_edad_actual_cop)}</strong>
  `;

  const tablaH2 = h2.en_universidad ? `
        <tr><td>🎓 Semestre Universidad (${h2.semestre_actual}° de 10)</td><td>${fmtCOP(h2.valor_semestre_univ_cop)}/sem</td></tr>
        <tr><td>📅 Matrícula Univ. Mensualizada (2 sem/12)</td><td>${fmtCOP(h2.matricula_univ_mensualizada_cop)}/mes</td></tr>
        <tr><td>🍎 Manutención + Transp./Materiales Univ.</td><td>${fmtCOP(h2.manutencion_y_otros_mes_cop)}/mes</td></tr>
        <tr class="total-row"><td style="color:#6a1b9a;">💳 Gasto Mensual Total Hijo 2</td><td style="color:#6a1b9a;">${fmtCOP(h2.gasto_mes_directo_cop)}/mes</td></tr>
        <tr><td>📊 Flujo Anual Univ. + Manut. Hijo 2</td><td>${fmtCOP(h2.flujo_anual_hoy_cop)}/año</td></tr>
        <tr><td>✅ Ya Invertido Univ. (1° a ${h2.semestre_actual - 1}° Sem.)</td><td>${fmtCOP(h2.vpa_colegio_restante_cop)}</td></tr>
        <tr><td>🎯 Por Ejecutar (${h2.semestre_actual}° a 10° + Posgr. 23a)</td><td style="color:#6a1b9a;font-weight:800;">${fmtCOP(h2.vpa_univ_proyectada_cop)}</td></tr>
  ` : `
        <tr><td>🏫 Pensión Agustiniano (Mes)</td><td>${fmtCOP(h2.pension_mes_cop)}/mes</td></tr>
        <tr><td>🚌 Ruta Escolar Suba (Mes)</td><td>${fmtCOP(h2.ruta_mes_cop)}/mes</td></tr>
        <tr><td>📋 Matrícula + Cobros (Anual / 12)</td><td>${fmtCOP(h2.matricula_prorrateada_mes_cop)}/mes</td></tr>
        <tr><td>🍎 Manutención + Lonchera/Extra</td><td>${fmtCOP(h2.manutencion_y_otros_mes_cop)}/mes</td></tr>
        <tr class="total-row"><td style="color:#6a1b9a;">💳 Gasto Mensual Directo Hijo 2</td><td style="color:#6a1b9a;">${fmtCOP(h2.gasto_mes_directo_cop)}/mes</td></tr>
        <tr><td>📊 Impacto Anualizado Hijo 2</td><td>${fmtCOP(h2.impacto_mes_anualizado_cop)}/mes</td></tr>
        <tr><td>🗓️ Flujo Anual Hoy Hijo 2</td><td style="color:#6a1b9a;font-weight:800;">${fmtCOP(h2.flujo_anual_hoy_cop)}/año</td></tr>
  `;

  const balanceFlujoColor = cons.balance_flujo_mensual_cop >= 0 ? '#2e7d32' : '#c62828';
  const balanceFlujoLbl = cons.balance_flujo_mensual_cop >= 0 ? 'Superávit' : 'Déficit';

  document.getElementById('grid-hijos-detalle').innerHTML = `
    <!-- CUADRO 1: HIJO 1 INDIVIDUAL -->
    <div class="child-card h1 ${animar ? 'flash' : ''}">
      <span class="child-badge badge-h1">👦 CUADRO 1: HIJO 1 — AGUSTINIANO SUBA (${h1.edad || 16} AÑOS | ${(h1.etiqueta_grado || 'GRADO 11°').toUpperCase()})</span>
      <div class="kpi-title">VPA Individual Hijo 1 (${esCompleto ? 'Ciclo 0–22a | ' + (h1.ruta_mes_cop > 0 ? 'Con Ruta' : 'Sin Ruta') : 'Capitalizado a ' + (h1.edad || 16) + 'a + Univ.'})</div>
      <div class="child-vpa-main" style="color:#1565c0;">${fmtCOP(vpaH1Mostrar)}</div>
      <div class="child-vpa-sub">
        🏫 VPA Ciclo Completo (0–22a): <strong>${fmtCOP(h1.vpa_ciclo_completo_cop)}</strong><br>
        🎯 Por Ejecutar (${h1.anios_colegio_rest || 1}a Col. + 10 sem. Univ.): <strong>${fmtCOP(h1.vpa_saldo_neto_cop || h1.vpa_restante_edad_actual_cop)}</strong>
      </div>
      <table class="metric-table">
        <tr><td>🏫 Pensión Agustiniano (Mes)</td><td>${fmtCOP(h1.pension_mes_cop)}/mes</td></tr>
        <tr><td>🚌 Ruta Escolar Suba</td><td>${fmtCOP(h1.ruta_mes_cop)}/mes</td></tr>
        <tr><td>📋 Matrícula + Cobros (Anual / 12)</td><td>${fmtCOP(h1.matricula_prorrateada_mes_cop)}/mes</td></tr>
        <tr><td>🍎 Manutención + Lonchera/Extra</td><td>${fmtCOP(h1.manutencion_y_otros_mes_cop)}/mes</td></tr>
        <tr class="total-row"><td>💳 Gasto Mensual Directo Hijo 1</td><td>${fmtCOP(h1.gasto_mes_directo_cop)}/mes</td></tr>
        <tr><td>📊 Impacto Anualizado Hijo 1</td><td>${fmtCOP(h1.impacto_mes_anualizado_cop)}/mes</td></tr>
        <tr><td>🗓️ Flujo Anual Hoy Hijo 1</td><td style="color:#0d47a1;font-weight:800;">${fmtCOP(h1.flujo_anual_hoy_cop)}/año</td></tr>
      </table>
    </div>

    <!-- CUADRO 2: HIJO 2 INDIVIDUAL -->
    <div class="child-card h2 ${animar ? 'flash' : ''}">
      <span class="child-badge badge-h2">👧 CUADRO 2: HIJO 2 — ${h2.en_universidad ? h2.semestre_actual + '° SEMESTRE UNIVERSIDAD' : 'COLEGIO AGUSTINIANO'} (${h2.edad || 20} AÑOS)</span>
      <div class="kpi-title">VPA Individual Hijo 2 (${esCompleto ? 'Ciclo 0–23a | Univ. + Posgrado' : (h2.en_universidad ? 'Carrera 10 Sem. + Posgrado 23a' : 'Colegio + Univ.')})</div>
      <div class="child-vpa-main" style="color:#6a1b9a;">${fmtCOP(vpaH2Mostrar)}</div>
      <div class="child-vpa-sub">
        ${subH2}
      </div>
      <table class="metric-table">
        ${tablaH2}
      </table>
    </div>

    <!-- CUADRO 3: CONSOLIDADO TOTAL -->
    <div class="child-card consolidado ${animar ? 'flash' : ''}">
      <span class="child-badge badge-cons">👨‍👧‍👦 CUADRO 3: CONSOLIDADO TOTAL (HIJO 1 + HIJO 2)</span>
      <div class="kpi-title">VPA Consolidado Familiar (${esCompleto ? 'Ciclo Completo H1 + H2' : 'Etapa Superior H1 + H2'})</div>
      <div class="child-vpa-main" style="color:#0a2540;font-size:1.38rem;">${fmtCOP(vpaConsMostrar)}</div>
      <div class="child-vpa-sub">
        👦 VPA Hijo 1 (${h1.edad}a ${h1.etiqueta_grado || 'Grado 11°'}): <strong style="color:#1565c0;">${fmtCOP(vpaH1Mostrar)}</strong><br>
        👧 VPA Hijo 2 (${h2.edad}a ${h2.en_universidad ? 'Sem. ' + cons.semestre_actual_h2 : 'Colegio'}): <strong style="color:#6a1b9a;">${fmtCOP(vpaH2Mostrar)}</strong>
      </div>
      <table class="metric-table">
        <tr><td>🏫 Educación Hijo 1 (Colegio + Ruta)</td><td>${fmtCOP(cons.educacion_h1_colegio_mes_cop)}/mes</td></tr>
        <tr><td>🎓 Educación Hijo 2 (${h2.en_universidad ? 'Univ. ' + cons.semestre_actual_h2 + '° Sem.' : 'Colegio'})</td><td>${fmtCOP(cons.educacion_h2_univ_mes_cop)}/mes</td></tr>
        <tr><td>🍎 Manutención + Transp./Extra (H1 + H2)</td><td>${fmtCOP(cons.manutencion_y_otros_sumados_mes_cop)}/mes</td></tr>
        <tr class="highlight-row"><td>🔥 GASTO MENSUAL CONSOLIDADO</td><td>${fmtCOP(cons.gasto_mes_directo_total_cop)}/mes</td></tr>
        <tr class="total-row"><td>📊 Impacto Anualizado Consolidado</td><td>${fmtCOP(cons.impacto_mes_anualizado_total_cop)}/mes</td></tr>
        <tr><td>🗓️ Desembolso Anual Total (H1 + H2)</td><td style="color:#0a2540;font-weight:800;">${fmtCOP(cons.flujo_anual_total_hoy_cop)}/año</td></tr>
        <tr><td>⚠️ Excedente: ${fmtCOP(cons.excedente_mensual_cop)} | Ahorro: ${fmtCOP(cons.liquidez_emergencia_cop)}</td><td style="color:${balanceFlujoColor};font-weight:800;">${balanceFlujoLbl}: ${fmtCOP(cons.balance_flujo_mensual_cop)}/mes</td></tr>
      </table>
    </div>
  `;

  // 2. RENDERIZAR LAS 3 DECISIONES VITALES COMPARADAS
  const titulos = {
    CASARSE: '💍 1. Casarse / Unión Marital',
    HIJOS: `🎓 2. Hijos Consolidado (Hijo 1 ${h1.etiqueta_grado || 'Grado 11°'} + Hijo 2 ${h2.en_universidad ? 'Univ. ' + cons.semestre_actual_h2 + '° Sem.' : 'Colegio'})`,
    CREDITO: '🚗 3. Crédito Estructural (+TCO)'
  };
  let htmlKpis = '';
  for (const k of ['CASARSE', 'HIJOS', 'CREDITO']) {
    const d = decs[k];
    const pillClass = d.probabilidad_exito_montecarlo_pct >= 80 ? 'pill-ok' : (d.probabilidad_exito_montecarlo_pct >= 55 ? 'pill-warn' : 'pill-bad');
    let extraInfo = '';
    if (k === 'CASARSE' && d.ahorro_sinergia_mensual_cop !== undefined) {
      extraInfo = `<br><strong>Ahorro Sinergia Pareja (8%):</strong> <span style="color:#2e7d32;font-weight:700;">+${fmtCOP(d.ahorro_sinergia_mensual_cop)}/mes</span>`;
    } else if (k === 'HIJOS' && d.desglose_colegio) {
      extraInfo = `
        <br><strong>👦 Hijo 1 (${h1.edad}a ${h1.etiqueta_grado || 'Grado 11°'}):</strong> ${fmtCOP(h1.gasto_mes_directo_cop)}/mes + <strong>👧 Hijo 2 (${h2.edad}a ${h2.en_universidad ? 'Sem. ' + h2.semestre_actual : 'Colegio'}):</strong> ${fmtCOP(h2.gasto_mes_directo_cop)}/mes
        <br><strong>👨‍👧‍👦 Gasto Mensual Consolidado:</strong> <span style="color:#c62828;font-weight:800;">${fmtCOP(cons.gasto_mes_directo_total_cop)}/mes</span>
      `;
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
          <span style="display:block;margin-top:5px;color:#0f4c81;">${d.recomendacion_actuarial_y_legal}</span>
        </div>
      </div>`;
  }
  document.getElementById('kpis-decisiones').innerHTML = htmlKpis;

  // 3. Gráfico Curva Actuarial Hijo (Hijo 1, Hijo 2 y Consolidado Hijo 1 + Hijo 2)
  const nivSel = data.actuaria_mod5.nivel_seleccionado;
  const cHijo = data.actuaria_mod5.curvas_hijo;
  document.getElementById('titulo-curva-hijo').innerText =
    `📈 1. Curva Actuarial Educativa: Hijo 1 (${h1.edad}a ${h1.etiqueta_grado || 'Grado 11°'} + Univ.) vs. Hijo 2 (${h2.edad}a ${h2.en_universidad ? 'Sem. ' + (h2.semestre_actual || 7) + '° Univ.' : 'Colegio'}) vs. Consolidado`;

  Plotly.react('chart-hijo', [
    {
      x: cHijo[nivSel].edades,
      y: cHijo[nivSel].flujo_nominal_m,
      type: 'bar',
      name: 'Flujo Anual Consolidado (Hijo 1 + Hijo 2)',
      marker: { color: '#90caf9' }
    },
    {
      x: cHijo['Hijo_1'].edades,
      y: cHijo['Hijo_1'].vpa_acum_m,
      mode: 'lines+markers',
      name: `👦 VPA Acumulado - Hijo 1 (${h1.edad}a, ${h1.etiqueta_grado || 'Grado 11°'} + 5a Univ.)`,
      line: { color: '#1e88e5', width: 3, dash: 'dot' }
    },
    {
      x: cHijo['Hijo_2'].edades,
      y: cHijo['Hijo_2'].vpa_acum_m,
      mode: 'lines+markers',
      name: `👧 VPA Acumulado - Hijo 2 (${h2.edad}a, ${h2.en_universidad ? 'Sem. ' + (h2.semestre_actual || 7) + '° Univ. + Posgr.' : 'Colegio + Univ.'})`,
      line: { color: '#8e24aa', width: 3, dash: 'dash' }
    },
    {
      x: cHijo['Agustiniano_Suba'].edades,
      y: cHijo['Agustiniano_Suba'].vpa_acum_m,
      mode: 'lines+markers',
      name: '👨‍👧‍👦 VPA Consolidado Familiar (Hijo 1 + Hijo 2)',
      line: { color: '#0a2540', width: 4 }
    },
    {
      x: cHijo['Medio'].edades,
      y: cHijo['Medio'].vpa_acum_m,
      mode: 'lines',
      name: 'Referencia Estándar Colombia (2 Hijos)',
      line: { color: '#fb8c00', width: 2, dash: 'dashdot' }
    }
  ], {
    margin: { t: 20, r: 20, b: 45, l: 55 },
    xaxis: { title: esCompleto ? 'Edad de los Hijos (Años 0 a 22)' : 'Horizonte de Pago desde Hoy (Años Restantes)' },
    yaxis: { title: 'Millones de Pesos ($ COP)' },
    legend: { orientation: 'h', y: 1.14 }
  }, { responsive: true });

  // 3. Gráfico Monte Carlo (1.000 escenarios)
  const mc = data.actuaria_mod5.trayectorias_mc;
  Plotly.react('chart-mc', [
    { x: mc.CASARSE, type: 'histogram', name: 'Casarse (Con Sinergia)', opacity: 0.65, marker: { color: '#2e7d32' } },
    { x: mc.HIJOS, type: 'histogram', name: `Hijos (${infoHijos.numero_hijos || 1} - Agustiniano)`, opacity: 0.65, marker: { color: '#1565c0' } },
    { x: mc.CREDITO, type: 'histogram', name: 'Crédito (+TCO)', opacity: 0.65, marker: { color: '#ef6c00' } }
  ], {
    barmode: 'overlay',
    margin: { t: 20, r: 20, b: 45, l: 50 },
    xaxis: { title: 'Flujo de Caja Mensual Post-Decisión (Millones COP)' },
    yaxis: { title: 'Escenarios (de 1.000)' },
    shapes: [{
      type: 'line', x0: 0, x1: 0, y0: 0, y1: 1, yref: 'paper',
      line: { color: '#c62828', width: 2.5, dash: 'dash' }
    }],
    legend: { orientation: 'h', y: 1.12 }
  }, { responsive: true });

  // 4. Gráfico Sensibilidad con marcador vertical en el excedente actual
  const sens = data.actuaria_mod5.sensibilidad;
  const excActualM = data.parametros_activos.excedente_m;
  Plotly.react('chart-sens', [
    { x: sens.excedentes_m, y: sens.CASARSE, mode: 'lines+markers', name: 'Casarse', line: { color: '#2e7d32', width: 3 } },
    { x: sens.excedentes_m, y: sens.HIJOS, mode: 'lines+markers', name: `Hijos (${infoHijos.numero_hijos || 1})`, line: { color: '#1565c0', width: 3 } },
    { x: sens.excedentes_m, y: sens.CREDITO, mode: 'lines+markers', name: 'Crédito (+TCO)', line: { color: '#ef6c00', width: 3 } }
  ], {
    margin: { t: 20, r: 20, b: 45, l: 50 },
    xaxis: { title: 'Excedente Mensual Disponible (Millones COP)' },
    yaxis: { title: 'Probabilidad de Solvencia (%)', range: [0, 105] },
    shapes: [{
      type: 'line', x0: excActualM, x1: excActualM, y0: 0, y1: 1, yref: 'paper',
      line: { color: '#0f4c81', width: 2, dash: 'dot' }
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
      line: { color: '#1e88e5', width: 3 }
    },
    {
      x: [hb.permanencia.meses_en_mora_registrados || 0],
      y: [hb.permanencia.meses_permanencia_post_pago],
      mode: 'markers',
      name: 'Caso Evaluado Actual',
      marker: { color: '#c62828', size: 13 }
    }
  ], {
    margin: { t: 20, r: 20, b: 45, l: 55 },
    xaxis: { title: 'Tiempo en Mora antes del Pago (Meses)' },
    yaxis: { title: 'Permanencia Máxima del Reporte Negativo (Meses)', range: [0, Math.max(54, (hb.permanencia.meses_permanencia_post_pago || 48) + 10)] },
    legend: { orientation: 'h', y: 1.12 }
  }, { responsive: true });

  // 6. Renderizar Pestaña 6 Módulos
  const m6 = data.caso_integrado_6_modulos;
  document.getElementById('kpis-6-modulos').innerHTML = `
    <div class="kpi-card">
      <div class="kpi-title">🎲 Módulo 6 — Salin Avellaneda</div>
      <div class="kpi-val">Perfil: ${m6.mod6_salin.perfil_riesgo}</div>
      <div class="kpi-sub">
        Puntaje Suitability SFC: ${m6.mod6_salin.puntaje}/100<br>
        Inversión Compuesta 10a ($200k/m): <strong>${fmtCOP(m6.mod6_salin.patrimonio_10a_inversion_cop)}</strong> vs. Azar: ${fmtCOP(m6.mod6_salin.valor_esperado_azar_cop)}<br>
        Colapso Pirámide (r=3): Nivel ${m6.mod6_salin.ciclos_colapso_piramide}
      </div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">⚙️ Módulo 1 — Nidia Velásquez</div>
      <div class="kpi-val">${fmtCOP(m6.mod1_nidia.ingreso_neto_cop)}</div>
      <div class="kpi-sub">
        Ingreso Disponible Neto (de $6.5M brutos)<br>
        Excedente Mensual: <strong>${fmtCOP(m6.mod1_nidia.excedente_mensual_cop)}</strong><br>
        Costo Oportunidad Gastos Hormiga (10a): ${fmtCOP(m6.mod1_nidia.costo_hormiga_10a_cop)}
      </div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">📉 Módulo 3 — Catalina Moreno</div>
      <div class="kpi-val">Estrategia ${m6.mod3_catalina.estrategia_optima}</div>
      <div class="kpi-sub">
        Índice Endeudamiento: ${m6.mod3_catalina.indice_endeudamiento_pct}%<br>
        Ahorro en Intereses: <strong>${fmtCOP(m6.mod3_catalina.ahorro_intereses_cop)}</strong><br>
        Flujo de Caja Liberado: ${fmtCOP(m6.mod3_catalina.flujo_liberado_cop)}/mes
      </div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">📈 Módulo 2 — Camilo Matson</div>
      <div class="kpi-val">${fmtCOP(m6.mod2_camilo.patrimonio_5a_nominal_cop)}</div>
      <div class="kpi-sub">
        Patrimonio Proyectado a 5 Años (Nominal)<br>
        En Pesos Reales de Hoy: <strong>${fmtCOP(m6.mod2_camilo.patrimonio_5a_real_cop)}</strong><br>
        Rentabilidad Real Neta: ${m6.mod2_camilo.tasa_real_neta_pct}% EA
      </div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">🏠 Módulo 4 — Jesi</div>
      <div class="kpi-val">${fmtCOP(m6.mod4_jesi.primera_cuota_pesos_cop)}/mes</div>
      <div class="kpi-sub">
        Segmento: ${m6.mod4_jesi.segmento}<br>
        ¿Cumple Ley 546/1999 (<=30%)?: <strong>${m6.mod4_jesi.cumple_ley_546 ? '✅ SÍ CUMPLE' : '❌ NO CUMPLE'}</strong><br>
        Cap Rate Neto Inmobiliario: ${m6.mod4_jesi.cap_rate_neto_pct}% EA
      </div>
    </div>
    <div class="kpi-card" style="border-left-color:#2e7d32;">
      <div class="kpi-title">🛡️ Módulo 5 + Habeas Data — Nelson Angel</div>
      <div class="kpi-val">${fmtCOP(decs.HIJOS.vpa_decision_cop)}</div>
      <div class="kpi-sub">
        VPA Hijos (Agustiniano Suba + Univ.) | Seguro Vida<br>
        Éxito Monte Carlo Hijos: <strong>${decs.HIJOS.probabilidad_exito_montecarlo_pct}% (${decs.HIJOS.dictamen_viabilidad})</strong><br>
        Protección Ley 1581 y Ley 1266 Activa
      </div>
    </div>
  `;
}

window.addEventListener('DOMContentLoaded', () => actualizarDashboard());
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


if __name__ == "__main__":
    iniciar_interfaz_grafica_local()
