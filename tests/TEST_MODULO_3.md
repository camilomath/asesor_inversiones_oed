# Documentación Oficial de Pruebas: "Test Modulo 3"

* **Módulo Evaluado:** Módulo 3 — Gestión, Administración y Optimización Analítica de Deudas ([src/mod3_gestion_deudas.py](file:///c:/github/asesor_inversiones_oed/src/mod3_gestion_deudas.py))
* **Responsable OED:** **Catalina Moreno** (Ingeniera Industrial — Líder de Proyectos y Analítica)
* **Archivo de Pruebas Ejecutable:** [tests/test_modulo_3.py](file:///c:/github/asesor_inversiones_oed/tests/test_modulo_3.py)
* **Marco Regulatorio Verificado:** Circular Básica Jurídica SFC (Tasas $EA \leftrightarrow EM$), Art. 884 Código de Comercio / Art. 305 Código Penal (Límite de Usura SFC), Ley 1328 de 2009 (Prepago a capital sin penalidad).

---

## 1. Matriz Resumen de Casos de Prueba ("Test Modulo 3")

| ID Prueba | Nombre de la Función en `tests/test_modulo_3.py` | Componente Evaluado | Criterio de Éxito (Aceptación) | Criterio de Rechazo (Fallo) |
| :---: | :--- | :--- | :--- | :--- |
| **TC-M3-01** | `test_01_semaforo_indice_endeudamiento_y_alertas` | `optimizar_portafolio_deudas` | Clasifica exactamente $IE \le 30\%$ como `VERDE_SALUDABLE`, $30\% < IE \le 40\%$ como `AMARILLO_ALERTA` y $IE > 40\%$ como `ROJO_SOBREENDEUDAMIENTO_CRITICO`. | Error en el cálculo porcentual de $IE$ o asignación errónea de la categoría del semáforo. |
| **TC-M3-02** | `test_02_validador_usura_sfc_en_portafolio` | `optimizar_portafolio_deudas` + `validar_usura_sfc` | Detecta tasas $> 26.50\%\text{ EA}$ marcando `excede_usura = True`, calcula los puntos básicos de exceso y emite `ALERTA LEGAL SFC`. | Omitir una tasa que supere la usura o marcar falso positivo en una tasa legal ($\le 26.50\%\text{ EA}$). |
| **TC-M3-03** | `test_03_optimalidad_avalancha_vs_bola_de_nieve_y_pago_minimo` | `_simular_estrategia_desendeudamiento` | **Avalancha** logra el menor pago de intereses totales; **Bola de Nieve** logra extinguir primero la deuda de menor saldo; ambas convergen a saldo $\$0\text{ COP}$ con *roll-over*. | Que Avalancha genere más intereses que Bola de Nieve/Pago Mínimo o que el saldo final no llegue a $\$0\text{ COP}$. |
| **TC-M3-04** | `test_04_simulador_abono_extraordinario_ley_1328` | `simular_abono_extraordinario_ley_1328` | **Reducción de Plazo** genera mayor ahorro en intereses que **Reducción de Cuota**; **Reducción de Cuota** disminuye la cuota mensual inmediata; si el abono $\ge$ saldo, cancela el 100% de la deuda. | Que la reducción de cuota ahorre más intereses que la reducción de plazo o error en el nuevo número de meses. |
| **TC-M3-05** | `test_05_evaluacion_compra_cartera_viable_vs_no_viable` | `simular_compra_cartera` | Aprueba (`es_viable_financieramente = True`) cuando el nuevo costo total $<$ costo actual y rechaza (`False`) cuando alargar el plazo o subir la tasa encarece la deuda. | Recomendar una compra de cartera donde el usuario termine pagando más intereses y seguros totales. |

---

## 2. Especificación Detallada de Cada Caso de Prueba (Entradas, Salidas y Parámetros)

---

### TC-M3-01: Clasificación del Semáforo de Índice de Endeudamiento ($IE$)
* **Función probada:** `optimizar_portafolio_deudas()`
* **Fórmula verificada:**
  $$IE = \frac{\sum (\text{Cuota Mensual}_i + \text{Seguro y Cuota de Manejo}_i)}{\text{Ingreso Neto Mensual}} \times 100\%$$
* **Entradas (Inputs):**
  1. **Escenario 1 (Saludable):** `ingreso_neto_mensual_cop = 6_000_000.0`, Cuota $= \$1.450.000 + \$50.000\text{ seguro} = \$1.500.000\text{ COP}$.
  2. **Escenario 2 (Alerta):** `ingreso_neto_mensual_cop = 6_000_000.0`, Cuota $= \$2.050.000 + \$50.000\text{ seguro} = \$2.100.000\text{ COP}$.
  3. **Escenario 3 (Crítico):** `ingreso_neto_mensual_cop = 6_000_000.0`, Cuota $= \$2.600.000 + \$100.000\text{ seguro} = \$2.700.000\text{ COP}$.
* **Salidas Esperadas (Outputs):**
  * Escenario 1: `indice_endeudamiento_pct = 25.0`, `semaforo_endeudamiento = "VERDE_SALUDABLE"`
  * Escenario 2: `indice_endeudamiento_pct = 35.0`, `semaforo_endeudamiento = "AMARILLO_ALERTA"`
  * Escenario 3: `indice_endeudamiento_pct = 45.0`, `semaforo_endeudamiento = "ROJO_SOBREENDEUDAMIENTO_CRITICO"`
* **Parámetros de Éxito / Rechazo:**
  * **Éxito:** Coincidencia exacta de los porcentajes ($25.0\%$, $35.0\%$, $45.0\%$) y del estado del semáforo.
  * **Rechazo:** No incluir los seguros/cuotas de manejo en el numerador del endeudamiento o clasificar erróneamente los cortes del $30\%$ y $40\%$.

---

### TC-M3-02: Validador Legal de Tasa de Usura SFC en el Portafolio
* **Función probada:** `optimizar_portafolio_deudas()`
* **Norma verificada:** Art. 884 del Código de Comercio y Art. 305 del Código Penal Colombiano (Tope de Usura vigente en configuración: $26.50\%\text{ EA}$).
* **Entradas (Inputs):**
  * Obligación 1 (`"Tarjeta Vigilada SFC"`): `saldo_cop = 3_000_000.0`, `tasa_ea = 0.2550` ($25.50\%\text{ EA}$).
  * Obligación 2 (`"Crédito Extrabancario Usura"`): `saldo_cop = 2_000_000.0`, `tasa_ea = 0.4200` ($42.00\%\text{ EA}$).
* **Salidas Esperadas (Outputs):**
  * Para Obligación 1: `excede_usura = False`, `exceso_puntos_basicos = 0.0`.
  * Para Obligación 2: `excede_usura = True`, `exceso_puntos_basicos = 1550.0` ($15.50\%$ por encima de usura), `mensaje_legal` contiene `"ALERTA LEGAL SFC"`.
* **Parámetros de Éxito / Rechazo:**
  * **Éxito:** Detección booleana exacta y cálculo de exceso en puntos básicos con tolerancia $\pm 0.1\text{ pb}$.
  * **Rechazo:** Permitir una tasa $> 26.50\%\text{ EA}$ sin activar `excede_usura = True`.

---

### TC-M3-03: Investigación de Operaciones — Avalancha vs. Bola de Nieve con *Roll-Over*
* **Función probada:** `optimizar_portafolio_deudas()` y `_simular_estrategia_desendeudamiento()`
* **Entradas (Inputs):**
  * `ingreso_neto_mensual_cop = 5_500_000.0`
  * `abono_extra_mensual_cop = 350_000.0`
  * `Deuda Pequeña Tasa Baja`: Saldo $\$1.500.000\text{ COP}$, Tasa $12.0\%\text{ EA}$, Cuota $\$100.000\text{ COP}$, Seguro $\$5.000\text{ COP}$.
  * `Deuda Grande Tasa Alta`: Saldo $\$6.000.000\text{ COP}$, Tasa $26.0\%\text{ EA}$, Cuota $\$250.000\text{ COP}$, Seguro $\$20.000\text{ COP}$.
* **Salidas Esperadas (Outputs):**
  * `sim_avalancha["total_intereses_pagados_cop"] < sim_bola_nieve["total_intereses_pagados_cop"] < sim_base["total_intereses_pagados_cop"]`
  * Mes de extinción de `Deuda Pequeña Tasa Baja` en Bola de Nieve $<$ Mes de extinción en Avalancha.
  * Último registro de `historial_mensual` con `saldo_total_cop == 0.0`.
* **Parámetros de Éxito / Rechazo:**
  * **Éxito:** Se comprueba simultáneamente la optimalidad matemática de **Avalancha** (menor costo de intereses) y la propiedad conductual de **Bola de Nieve** (elimina la primera deuda más rápido).
  * **Rechazo:** Que no se aplique el efecto *roll-over* de las cuotas liberadas o que Avalancha resulte más costosa que Bola de Nieve.

---

### TC-M3-04: Simulador de Abonos Extraordinarios a Capital (Ley 1328 de 2009)
* **Función probada:** `simular_abono_extraordinario_ley_1328()`
* **Norma verificada:** Ley 1328 de 2009 (Derecho del consumidor financiero a prepagar total o parcialmente obligaciones sin penalidad).
* **Entradas (Inputs):**
  * **Subcaso 4A (Abono Parcial con Prima):** `saldo_actual_cop = 9_500_000.0`, `tasa_ea = 0.1680`, `plazo_restante_meses = 36`, `abono_extra_capital_cop = 2_500_000.0`.
  * **Subcaso 4B (Pago Total Anticipado):** Mismos parámetros con `abono_extra_capital_cop = 10_000_000.0`.
* **Salidas Esperadas (Outputs):**
  * **Subcaso 4A:**
    * `opcion_reduccion_plazo["nuevo_plazo_meses"] < 36` y `meses_ahorrados >= 10`.
    * `opcion_reduccion_cuota["flujo_mensual_liberado_cop"] > 80_000.0`.
    * `opcion_reduccion_plazo["ahorro_intereses_cop"] > opcion_reduccion_cuota["ahorro_intereses_cop"]`.
  * **Subcaso 4B:**
    * `deuda_cancelada_totalmente = True`, `meses_ahorrados = 36`.
* **Parámetros de Éxito / Rechazo:**
  * **Éxito:** Reducir plazo ahorra significativamente más intereses que reducir cuota, y el pago total extingue los 36 meses restantes.
  * **Rechazo:** Error en la fórmula logarítmica de despeje de períodos ($n$) en anualidades francesas o ahorros negativos.

---

### TC-M3-05: Evaluación Financiera de Compra de Cartera Consolidada
* **Función probada:** `simular_compra_cartera()`
* **Entradas (Inputs):**
  * Portafolio actual: Tarjeta Gold ($\$4.800.000$ al $25.8\%\text{ EA}$) + Libre Inversión ($\$9.500.000$ al $16.8\%\text{ EA}$). Saldo total unificado $= \$14.300.000\text{ COP}$.
  * **Escenario A (Oferta Competitiva):** `tasa_ea_compra_cartera = 0.1250` ($12.5\%\text{ EA}$), `plazo_meses_nuevo = 24`, `seguro_mensual_nuevo_cop = 15_000.0`.
  * **Escenario B (Oferta Engañosa / Plazo Excesivo):** `tasa_ea_compra_cartera = 0.2400` ($24.0\%\text{ EA}$), `plazo_meses_nuevo = 60`, `seguro_mensual_nuevo_cop = 35_000.0`.
* **Salidas Esperadas (Outputs):**
  * Escenario A: `es_viable_financieramente = True`, `ahorro_neto_costo_financiero_cop > 0`.
  * Escenario B: `es_viable_financieramente = False`, `ahorro_neto_costo_financiero_cop < 0`.
* **Parámetros de Éxito / Rechazo:**
  * **Éxito:** El modelo recomienda la compra de cartera en el Escenario A y advierte/rechaza la compra de cartera en el Escenario B aunque la cuota mensual parezca menor por haberse estirado a 60 meses.
  * **Rechazo:** Evaluar la compra de cartera únicamente por el valor de la cuota mensual sin comparar el costo financiero total de intereses + seguros.

---

## 3. Cómo Ejecutar el "Test Modulo 3" en la Terminal

Para correr exclusivamente las pruebas del Módulo 3 de Catalina con detalle de cada caso:

```powershell
pytest tests/test_modulo_3.py -v
```

---

## 4. Test de Usabilidad de la Interfaz Gráfica (3 Iteraciones en Tonos Lilas)

* **Archivo de Interfaz Evaluado:** [outputs/ui_modulo_3_catalina.html](file:///c:/github/asesor_inversiones_oed/outputs/ui_modulo_3_catalina.html)
* **Metodología:** Evaluación Heurística de Nielsen + Prueba de Recorrido Cognitivo (*Cognitive Walkthrough*) ejecutada en **3 iteraciones sucesivas**.

### Matriz de Evolución por Iteración de Usabilidad

| Iteración | Foco de la Prueba | Hallazgo / Fricción Detectada (Antes) | Mejora de Diseño e Ingeniería Implementada (Después) | Resultado / Criterio de Éxito UX |
| :---: | :--- | :--- | :--- | :--- |
| **Iteración 1** | **Libertad de Entrada vs. Caso Semilla** (*Heurística 3: Control y libertad del usuario*) | El usuario iniciaba atado a las 4 deudas del Caso Semilla y debía borrar fila por fila si quería ingresar sus propias obligaciones desde cero. | 1. Se creó el botón destacado **`✍️ Diligenciar Mis Propios Datos (En Blanco)`** que limpia el portafolio para empezar desde cero.<br>2. Se dejó al lado el botón **`🌱 Cargar Caso Semilla OED`** para poblar instantáneamente el caso base.<br>3. Se añadió un **Formulario Guiado de Creación Rápida** con placeholders claros. | El usuario alterna en **1 clic** (`< 1 segundo`) entre diligenciar sus propios datos o restaurar el Caso Semilla OED, con indicador visual del modo activo. |
| **Iteración 2** | **Prevención de Errores Financieros y Legibilidad Monetaria** (*Heurísticas 5 y 6: Prevención de errores y reconocimiento*) | 1. Al digitar cifras en millones (ej. `9500000`) sin puntos era fácil equivocarse en un cero.<br>2. Si el usuario ingresaba una cuota menor al interés mensual del crédito, no entendía por qué la deuda no se extinguía. | 1. Formateo en vivo en Pesos Colombianos (`$5.915.000`) junto a los campos numéricos y debajo de cada celda de saldo/cuota.<br>2. Botón **`✨ Auto-calcular cuota sugerida (36 meses)`** con fórmula francesa.<br>3. Alerta preventiva (`⚠️ Interés: $X`) cuando la cuota ingresada es menor al interés mensual. | Reducción del $100\%$ en errores de digitación de ceros y prevención automática de cuotas insuficientes para amortizar capital. |
| **Iteración 3** | **Identidad Visual en Tonos Lilas y Flujo Integrado 1-Clic** (*Heurísticas 4 y 8: Estética minimalista y eficiencia de uso*) | 1. El tema oscuro genérico carecía de identidad visual propia.<br>2. Para probar el Simulador Ley 1328 con una deuda de la tabla superior, el usuario tenía que copiar y pegar manualmente saldo y tasa. | 1. Rediseño integral en **paleta de tonos lilas, violetas y lavanda** (`#2e1065`, `#581c87`, `#a855f7`, `#c084fc`, `#f3e8ff`) con contraste accesible WCAG AA.<br>2. Se agregó el botón **`📥 Ley 1328`** en cada fila de la tabla para transferir saldo, tasa y plazo estimado al simulador de abonos a capital en un clic. | Cero re-digitación entre secciones y consistencia visual en tonos lilas en tarjetas, bordes, curvas del gráfico Canvas y barras Gantt. |

