"""
Orquestador principal del Asesor de Inversiones OED.
Ejecuta los módulos en el orden establecido como una "Consulta Médica Financiera".
"""

def main():
    print("Iniciando Asesor Financiero OED...")
    print("==========================================")

    # PASO 0: Firma de Consentimiento y Reglas de Juego
    print("\n[PASO 0] Data Governance & Finance (Nelson + Camilo)")
    print("- Solicitando autorización de datos (Ley 1581 de 2012)...")
    print("- Cargando tasas macroeconómicas (EA/EM, UVT, IPC)...")
    # import src.data_governance as dg
    # import src.finance as fin

    # PASO 1: Módulo 6 - Personalidad de Riesgo
    print("\n[PASO 1] Módulo 6: Examen de Personalidad de Riesgo (Salin Avellaneda)")
    print("- Evaluando perfil de riesgo (Conservador, Moderado, Agresivo)...")
    # import src.mod6_educacion_financiera as mod6

    # PASO 2: Módulo 1 - Presupuesto y Gastos
    print("\n[PASO 2] Módulo 1: Radiografía del Sueldo y Presupuesto (Nidia Velásquez)")
    print("- Calculando descuentos de ley, gastos fijos y excedente mensual...")
    # import src.mod1_presupuesto as mod1

    # PASO 3: Módulo 3 - Gestión de Deudas
    print("\n[PASO 3] Módulo 3: Cirugía de Deudas (Catalina Moreno)")
    print("- Aplicando estrategia Avalancha/Bola de Nieve sobre el excedente...")
    # import src.mod3_gestion_deudas as mod3

    # PASO 4: Módulo 2 - Inversiones de Bajo Monto
    print("\n[PASO 4] Módulo 2: Multiplicar el Sueldo (Camilo Matson)")
    print("- Invirtiendo el excedente en Neobancos, CDTs, FICs, AFC y BVC...")
    # import src.mod2_inversiones_salario as mod2

    # PASO 5: Módulo 4 - Finca Raíz
    print("\n[PASO 5] Módulo 4: Compra Inteligente de Vivienda (Jesi)")
    print("- Evaluando compra VIS/No VIS, Pesos vs UVR y Regla del 30%...")
    # import src.mod4_finca_raiz as mod4

    # PASO 6: Módulo 5 - Decisiones de Vida
    print("\n[PASO 6] Módulo 5: Simulador del Futuro (Nelson)")
    print("- Ejecutando simulaciones actuariales Monte Carlo para hitos de vida...")
    # import src.mod5_decisiones_vida as mod5

    print("\n==========================================")
    print("Consulta Financiera OED Finalizada con Éxito.")

if __name__ == "__main__":
    main()

