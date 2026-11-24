"""
Script Interactivo para Probar el Módulo 6 de Salin Avellaneda.
Asesor Financiero e Inversiones OED.
"""

from __future__ import annotations

import sys
from src.mod6_educacion_financiera import (
    obtener_cuestionario_suitability,
    evaluar_cuestionario_suitability_completo,
    comparar_azar_vs_inversion_compuesta,
    simular_trayectoria_mensual_azar_vs_inversion,
    detectar_esquema_piramidal_ponzi,
    obtener_trivias_cultura_financiera,
    POBLACION_ADULTA_COLOMBIA,
)


def ejecutar_demo_caso_oed():
    print("\n" + "=" * 65)
    print("DEMOSTRACIÓN AUTOMÁTICA DEL CASO DE USO CU-06 (SALIN AVELLANEDA)")
    print("=" * 65)

    # 1. Test de Idoneidad
    print("\n--- 1. Perfilamiento SFC (Decreto 2555 de 2010) ---")
    respuestas = {
        "p1_horizonte": 2,            # 3 a 5 años
        "p2_reaccion_caida": 2,       # Calma ante volatilidad
        "p3_objetivo_inversion": 2,   # Crecimiento balanceado
        "p4_conocimiento_financiero": 2, # Conoce CDTs y FICs
        "p5_dependencia_ingresos": 2,
        "p6_porcentaje_patrimonio": 1,
        "p7_fondo_emergencia": 2,
        "p8_educacion_tributaria": 2,
    }
    diagnostico = evaluar_cuestionario_suitability_completo(respuestas)
    print(f"-> Perfil Resultante: {diagnostico['perfil_riesgo']}")
    print(f"-> Puntaje de Idoneidad: {diagnostico['puntaje_idoneidad_100']}/100")
    print(f"-> Asignación sugerida: {diagnostico['distribucion_activos_sugerida']}")
    print(f"-> Dictamen: {diagnostico['recomendacion_normativa']}")

    # 2. Prueba de Inconsistencia Conductual
    print("\n--- 2. Detector de Inconsistencia Conductual (Suitability) ---")
    respuestas_inconsistentes = {
        "p1_horizonte": 3,
        "p2_reaccion_caida": 0,  # Pánico ante caída del 5%
        "p3_objetivo_inversion": 3,  # Desea máxima rentabilidad bursátil agresiva
    }
    inconsistencia = evaluar_cuestionario_suitability_completo(respuestas_inconsistentes)
    print(f"-> Perfil reajustado preventivamente: {inconsistencia['perfil_riesgo']}")
    print(f"-> Alerta: {inconsistencia['alerta_conductual_suitability']}")

    # 3. Laboratorio Azar vs Inversión
    print("\n--- 3. Azar vs. Interés Compuesto ($200.000 COP/mes a 10 años) ---")
    azar = comparar_azar_vs_inversion_compuesta(200_000.0, horizonte_anios=10, tasa_ea_inversion_regulada=0.11)
    print(f"-> Probabilidad Baloto: {azar['probabilidad_combinatoria_baloto']}")
    print(f"-> Probabilidad Chance 4 cifras: {azar['probabilidad_chance_4_cifras']}")
    print(f"-> Total dinero destinado: ${azar['total_desembolsado_cop']:,.0f} COP")
    print(f"-> Valor Esperado en Juegos de Azar: ${azar['valor_esperado_azar_cop']:,.0f} COP")
    print(f"-> Pérdida Matemática en Azar: ${azar['perdida_matematica_esperada_azar_cop']:,.0f} COP")
    print(f"-> Patrimonio acumulado en Inversión (11% EA): ${azar['patrimonio_inversion_compuesta_cop']:,.0f} COP")
    print(f"-> BRECHA PATRIMONIAL A FAVOR DEL AHORRO: +${azar['brecha_riqueza_inversion_vs_azar_cop']:,.0f} COP")

    # 4. Detector de Pirámides
    print("\n--- 4. Detector de Captación Ilegal (Art. 316 Código Penal) ---")
    piramide = detectar_esquema_piramidal_ponzi(10.0, personas_reclutadas_por_ciclo=3)
    print(f"-> Promesa evaluada: 10% mensual (Equivale a {piramide['tasa_ea_equivalente_pct']:,.1f}% EA)")
    print(f"-> ¿Alerta de Esquema Piramidal?: {piramide['alerta_piramide']}")
    print(f"-> Niveles para superar a Colombia ({POBLACION_ADULTA_COLOMBIA:,} adultos): {piramide['ciclos_para_agotar_poblacion_colombia']} niveles")
    print(f"-> Dictamen SFC: {piramide['advertencia_legal_sfc']}")
    print("\n" + "=" * 65)


def responder_test_interactivo():
    print("\n" + "=" * 65)
    print("TEST INTERACTIVO DE IDONEIDAD SFC (DECRETO 2555 DE 2010)")
    print("=" * 65)
    cuestionario = obtener_cuestionario_suitability()
    respuestas = {}

    for i, preg in enumerate(cuestionario, 1):
        print(f"\n[{i}/{len(cuestionario)}] {preg['pregunta']}")
        for j, opc in enumerate(preg["opciones"]):
            print(f"  {j}) {opc['texto']}")
        
        while True:
            try:
                sel = input("Selecciona una opción (0-3): ").strip()
                sel_int = int(sel)
                if 0 <= sel_int < len(preg["opciones"]):
                    respuestas[preg["id"]] = sel_int
                    break
                else:
                    print("Por favor ingresa un número válido entre 0 y 3.")
            except ValueError:
                print("Entrada inválida. Ingresa un número.")

    diag = evaluar_cuestionario_suitability_completo(respuestas)
    print("\n" + "-" * 40)
    print("RESULTADO DE TU PERFIL DE INVERSIONISTA")
    print("-" * 40)
    print(f"Perfil Asignado: {diag['perfil_riesgo']}")
    print(f"Puntaje: {diag['puntaje_idoneidad_100']}/100")
    if diag.get("alerta_conductual_suitability"):
        print(f"Alerta Suitability: {diag['alerta_conductual_suitability']}")
    print(f"Distribución Sugerida de Activos:")
    for k, v in diag["distribucion_activos_sugerida"].items():
        print(f"  - {k.replace('_', ' ').capitalize()}: {v}%")


def simular_azar_personalizado():
    print("\n" + "=" * 65)
    print("SIMULADOR DE AZAR VS. INVERSIÓN COMPUESTA")
    print("=" * 65)
    try:
        monto = float(input("¿Cuánto dinero gastas (o piensas gastar) al mes en azar/rifas/loterías? [COP] (ej. 200000): "))
        anios = int(input("¿A cuántos años deseas proyectarlo? (ej. 5 o 10): "))
    except ValueError:
        print("Valores inválidos. Usando $200.000 COP a 10 años por defecto.")
        monto = 200_000.0
        anios = 10

    res = comparar_azar_vs_inversion_compuesta(monto, anios, tasa_ea_inversion_regulada=0.11)
    print("\nResultados:")
    print(f"- Total destinado en {anios} años: ${res['total_desembolsado_cop']:,.0f} COP")
    print(f"- Valor esperado que recuperarías en azar: ${res['valor_esperado_azar_cop']:,.0f} COP")
    print(f"- Pérdida esperada matemática: ${res['perdida_matematica_esperada_azar_cop']:,.0f} COP")
    print(f"- Patrimonio acumulado en inversión vigilada SFC (11% EA): ${res['patrimonio_inversion_compuesta_cop']:,.0f} COP")
    print(f"- Brecha patrimonial a favor del ahorro: +${res['brecha_riqueza_inversion_vs_azar_cop']:,.0f} COP")


def evaluar_promesa_piramidal():
    print("\n" + "=" * 65)
    print("DETECTOR DE ESQUEMAS PIRAMIDALES / PONZI (ART. 316 C.P.)")
    print("=" * 65)
    try:
        tasa = float(input("¿Qué rentabilidad mensual prometen? (%) (ej. 10 para 10% mensual): "))
        reclutados = int(input("¿A cuántas personas te piden reclutar? (ej. 3): "))
    except ValueError:
        print("Valores inválidos. Usando 10% y 3 personas por defecto.")
        tasa = 10.0
        reclutados = 3

    alerta = detectar_esquema_piramidal_ponzi(tasa, reclutados)
    print(f"\n- Tasa Efectiva Anual: {alerta['tasa_ea_equivalente_pct']:,.1f}% EA")
    print(f"- ¿Alerta de captación ilegal / Ponzi?: {alerta['alerta_piramide']}")
    print(f"- Niveles hasta agotar la población de Colombia: {alerta['ciclos_para_agotar_poblacion_colombia']} niveles")
    print(f"- Advertencia: {alerta['advertencia_legal_sfc']}")


def main():
    while True:
        print("\n" + "=" * 55)
        print("    MENÚ DE PRUEBAS - MÓDULO 6 (SALIN AVELLANEDA)")
        print("=" * 55)
        print("1. Ejecutar Demostración Rápida Completa (Recomendado)")
        print("2. Responder el Test de Perfil de Riesgo (8 Preguntas)")
        print("3. Simular Azar vs. Inversión Compuesta Personalizado")
        print("4. Evaluar una Oferta Sospechosa (Detector de Pirámides)")
        print("5. Salir")
        opc = input("\nElige una opción (1-5): ").strip()

        if opc == "1":
            ejecutar_demo_caso_oed()
        elif opc == "2":
            responder_test_interactivo()
        elif opc == "3":
            simular_azar_personalizado()
        elif opc == "4":
            evaluar_promesa_piramidal()
        elif opc == "5":
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        ejecutar_demo_caso_oed()
    else:
        main()
