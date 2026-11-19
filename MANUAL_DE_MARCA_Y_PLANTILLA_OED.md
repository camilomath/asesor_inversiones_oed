# 💼 Manual de Marca, Voz de "Asesor Financiero de Confianza" y Estándar de Interfaz — Equipo OED Colombia

> **Acuerdo de Equipo (Autonomía Total):**  
> Nadie modifica el código ni los archivos de otro compañero. **Cada integrante (Camilo, Nidia, Nelson, Catalina, Jesi y Salin) aplica este manual únicamente en su propia interfaz** usando la plantilla compartida [`src/oed_design_system.py`](src/oed_design_system.py), para que al unir los 6 módulos todo el sistema tenga **exactamente la misma estructura visual, el mismo criterio financiero cercano y las mismas explicaciones interactivas**.

---

## 1. Nuestra Identidad: El "Asesor Financiero de Confianza"

Cuando una persona abre cualquiera de nuestros 6 módulos, debe sentir que conversa con un **Asesor Financiero de Confianza**:

1. **Cercano, claro y cero regaños:**
   * ❌ *Cómo NO escribir:* `"Relación cuota/ingreso excede el límite normativo; solicitud rechazada."`
   * ✅ *Cómo SÍ escribir:* `"Te recomendamos esperar antes de tomar este crédito: hoy esta cuota compromete demasiado tu flujo de caja mensual. Revisemos dos alternativas concretas en pesos para lograr tu meta sin sobreendeudarte..."`
2. **Regla "Cero Palabras Huérfanas" (Explicación ahí mismo con `?`):**
   * Si en pantalla aparece **cualquier término que requiera explicación** —financiero (`EA`, `TIR`, `FIC`), de vivienda (`VIS`, `UVR`, `Leasing`), de nómina/impuestos (`IBC`, `UVT`, `SMMLV`, `4x1000`, `Cuenta AFC`), legal (`Ley 546`, `Tasa de Usura`, `Fogafín`, `Habeas Data`) o estadístico (`Valor Esperado`, `Monte Carlo`)—, **la explicación debe salir ahí mismo** al pasar el cursor o tocar la palabra (`?`).
   * La plantilla `src/oed_design_system.py` detecta automáticamente más de **25 términos de las 5 familias** dentro de tus párrafos y les incrusta la burbuja explicativa **`?`** sin trabajo extra.
3. **Siempre cerramos con un Plan de Acción:** Todo Diagnóstico Financiero termina con una sola acción concreta en pesos colombianos (`$ COP`) para ejecutar este mismo mes (*"📌 Plan de Acción para este Mes"*).

---

## 2. Estructura Estándar de Interfaz (Los 5 Bloques en el Mismo Orden)

Para que todas las pantallas del proyecto se vean uniformes, cada integrante organiza su interfaz de arriba hacia abajo en estos **5 bloques fijos**:

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ BLOQUE 1: Barra de Progreso (Pasos 0 al 6) + Encabezado del Asesor OED       │
│           -> render_encabezado_modulo_oed(paso_actual=...)                   │
├──────────────────────────────────────────────────────────────────────────────┤
│ BLOQUE 2: Datos de la Persona (Expander limpio de 2 o 3 columnas)            │
│           -> Precargado con `perfil_semilla_taller` + ayudas claras (`help`) │
├──────────────────────────────────────────────────────────────────────────────┤
│ BLOQUE 3: Diagnóstico Financiero (?) + 📌 Plan de Acción + 4 Indicadores Clave│
│           -> render_semaforo_ciudadano_oed(...) + 4 tarjetas `st.metric`     │
├──────────────────────────────────────────────────────────────────────────────┤
│ BLOQUE 4: Gráficas Interactivas con la Paleta Oficial OED                    │
│           -> aplicar_estilo_plotly_oed(fig, titulo="...")                    │
├──────────────────────────────────────────────────────────────────────────────┤
│ BLOQUE 5: Diccionario Financiero Desplegable (5 Familias de Términos)        │
│           -> render_glosario_interactivo_oed()                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Paleta Oficial OED

Centralizada en `PALETA_MARCA_OED` y `COLORES_GRAFICAS_OED` dentro de `src/oed_design_system.py`:

| Rol Visual | Nombre Oficial | Código HEX | Uso obligatorio en todas las interfaces |
| :--- | :--- | :---: | :--- |
| **Identidad Institucional** | **Azul Solidez OED** | `#0F294A` | Encabezados principales, títulos y fondo de burbujas explicativas (`?`). |
| **Acción Principal** | **Azul Acción Financiera** | `#1D4ED8` | Botones principales, subrayado de términos con `?` y serie principal en gráficas. |
| **Plan del Mes** | **Naranja Plan de Acción** | `#EA580C` | Indicador del paso activo y tarjeta de *"📌 Plan de Acción para este Mes"*. |
| **Meta Viable** | **Verde Viabilidad** | `#15803D` | Diagnóstico Financiero favorable (`nivel="verde"` — cumple reglas legales y capacidad de pago). |
| **Revisión Preventiva** | **Ámbar Revisión Preventiva** | `#B45309` | Revisión preventiva (`nivel="ambar"` — viable hoy, requiere vigilar inflación, tasas o liquidez). |
| **Riesgo Alto** | **Rojo Riesgo Alto** | `#B91C1C` | Riesgo alto / Te recomendamos esperar (`nivel="rojo"` — alerta de sobreendeudamiento o usura sin regañar). |

---

## 4. Las 5 Familias del Diccionario Financiero Integrado (Listas para Usar)

El diccionario `GLOSARIO_LENGUAJE_CLARO_OED` ya incluye explicaciones claras y ejemplos cotidianos en `$ COP` para los módulos de todo el equipo:

* **1. Financiero e Inversión (Camilo / Todos):** `EA`, `EM`, `IPC / Inflación`, `Interés Compuesto`, `CDT`, `FIC`, `VPN y TIR`.
* **2. Vivienda y Finca Raíz (Jesi):** `VIP / VIS / No VIS`, `UVR`, `Ley 546 (Regla del 30%)`, `Encargo Fiduciario`, `Leasing Habitacional`, `Ley 820`, `Cap Rate y Cash-on-Cash`.
* **3. Nómina, Trabajo e Impuestos (Nidia / Camilo / Jesi):** `SMMLV`, `IBC (40% independientes)`, `UVT`, `Cuenta AFC`, `4x1000 (GMF)`.
* **4. Deudas y Leyes Protectoras (Catalina / Nelson):** `Tasa de Usura SFC`, `Avalancha vs. Bola de Nieve`, `Ley 1328 (Abonos a capital)`, `Seguro Fogafín`, `Habeas Data`.
* **5. Probabilidad y Futuro (Salin / Nelson):** `Valor Esperado E[X]`, `Simulación Actuarial de Monte Carlo`.

*(Si necesitas un término adicional propio de tu módulo, agrégalo en `GLOSARIO_LENGUAJE_CLARO_OED` dentro de `src/oed_design_system.py` y se activará automáticamente con `?`).*

---

## 5. Tabla de Pasos por Integrante (`paso_actual`)

Cada compañero usa su número de `paso_actual` al llamar `render_encabezado_modulo_oed(paso_actual=X)`:

| `paso_actual` | Integrante | Título en Pantalla |
| :-: | :--- | :--- |
| `0` | **Nelson + Camilo** | 🤝 *Bienvenida a OED y Protección de tus Datos* |
| `1` | **Salin Avellaneda** | 🎯 *Tu Perfil de Riesgo y Criterio de Inversión* |
| `2` | **Nidia Velásquez** | 📊 *Análisis de tu Sueldo, Gastos y Flujo de Caja* |
| `3` | **Catalina Moreno** | 🔓 *Estrategia para Salir de Deudas y Pagar Menos Intereses* |
| `4` | **Camilo Matson** | 🌱 *Plan de Inversión Mensual desde tu Sueldo* |
| `5` | **Jesi** | 🏡 *Viabilidad para Comprar Vivienda o Invertir en Finca Raíz* |
| `6` | **Nelson** | 🛡️ *Prueba de Estrés Financiero para tus Grandes Metas* |

---

## 6. Plantilla Base para Copiar y Pegar en tu Propio Módulo

Copia este esqueleto en el archivo de interfaz de tu módulo (reemplazando `paso_actual` por el tuyo):

```python
import streamlit as st
from src.oed_design_system import (
    aplicar_estilo_plotly_oed,
    formatear_cop_claro,
    render_encabezado_modulo_oed,
    render_glosario_interactivo_oed,
    render_semaforo_ciudadano_oed,
)


def render_interfaz_mi_modulo():
    # BLOQUE 1: Encabezado OED + Barra de 7 Pasos
    render_encabezado_modulo_oed(paso_actual=2)  # <- Cambia al número de tu paso (0 a 6)

    # BLOQUE 2: Entradas de usuario claras y con valores semilla por defecto
    with st.expander("⚙️ 1. Cuéntanos tus datos principales", expanded=True):
        col1, col2 = st.columns(2)
        ingreso = col1.number_input(
            "Tu ingreso mensual en pesos ($ COP)",
            min_value=0.0,
            value=6_500_000.0,
            step=250_000.0,
            help="Lo que recibes cada mes antes o después de descuentos sobre tu IBC.",
        )
        ahorro = col2.number_input(
            "Cuánto puedes separar al mes ($ COP)",
            min_value=0.0,
            value=650_000.0,
            step=50_000.0,
        )

    # BLOQUE 3: Diagnóstico Financiero (las siglas sacan burbuja ? solas) + 4 Indicadores Clave
    render_semaforo_ciudadano_oed(
        nivel="verde",  # Usa: "verde", "azul", "ambar" o "rojo"
        titulo_claro="Tus indicadores clave muestran capacidad sólida de ahorro",
        explicacion_humana=(
            f"Con un aporte mensual de {formatear_cop_claro(ahorro)} en un FIC o CDT protegido por Fogafín, "
            "tu capital crece con interés compuesto superando la inflación del IPC."
        ),
        siguiente_paso_accionable="Programa una transferencia automática por ese monto el mismo día que recibes tu pago mensual.",
    )

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Ingreso Mensual", formatear_cop_claro(ingreso))
    k2.metric("Ahorro Mensual", formatear_cop_claro(ahorro))
    k3.metric("Tasa de Ahorro", f"{(ahorro / max(ingreso, 1)) * 100:.1f}%")
    k4.metric("Nivel de Viabilidad", "Favorable")

    # BLOQUE 4: Tus gráficas Plotly con la paleta oficial OED
    # fig = aplicar_estilo_plotly_oed(mi_fig, titulo="Proyección de tu Patrimonio en Pesos ($ COP)")
    # st.plotly_chart(fig, use_container_width=True)

    # BLOQUE 5: Diccionario Financiero desplegable de las 5 familias de términos
    render_glosario_interactivo_oed()
```

---

## 7. Checklist Rápido Antes de Subir tu Interfaz (1 Minuto)

- [ ] ¿Usé `render_encabezado_modulo_oed(paso_actual=...)` con el número de mi módulo?
- [ ] ¿Redacté mis textos con voz de **Asesor Financiero de Confianza** (claro, sin regañar y cerrando con un `📌 Plan de Acción para este Mes` en `$ COP`)?
- [ ] ¿Usé `render_semaforo_ciudadano_oed(...)` para que todos los términos técnicos y legales salgan con su explicación `?`?
- [ ] ¿Pasé mis gráficas por `aplicar_estilo_plotly_oed(fig)` para mantener los mismos colores de OED?
- [ ] ¿Incluí `render_glosario_interactivo_oed()` al cierre de la pantalla?

---

## 8. Ver el Manual Interactivo en el Navegador (100% Local)

Cualquier integrante puede abrir la vista interactiva del Manual de Marca OED, probar las burbujas `?` y copiar su bloque de código ejecutando:

```powershell
py src/oed_design_system.py
```

---

## Textos a actualizar en `src/oed_design_system.py`

Guía de reemplazo directo de textos visibles para quien mantiene la plantilla compartida (sin cambiar nombres de funciones, llaves ni variables):

| Antes (médico) | Ahora (financiero) |
| :--- | :--- |
| `VOZ DE "MÉDICO FINANCIERO AMIGO" — EQUIPO OED COLOMBIA` | `VOZ DE "ASESOR FINANCIERO DE CONFIANZA" — EQUIPO OED COLOMBIA` |
| `Azul Bata Médica (Confianza OED)` | `Azul Solidez OED` |
| `Azul Cuidado Activo` | `Azul Acción Financiera` |
| `Naranja Receta Positiva` / `Tu Receta Práctica del Mes` | `Naranja Plan de Acción` / `📌 Plan de Acción para este Mes` |
| `Verde Signos Vitales Sanos` | `Verde Viabilidad` |
| `Ámbar Chequeo Preventivo` | `Ámbar Revisión Preventiva` |
| `Rojo Cuidado Intensivo (Sin Regaños)` | `Rojo Riesgo Alto` |
| `Blanco Consultorio Cálido` | `Gris Claro Fondo OED` |
| `🩺 Bienvenida al Consultorio y Confidencialidad` | `🤝 Bienvenida a OED y Protección de tus Datos` |
| `Igual que en una historia clínica médica, tus datos son privados...` | `Tus datos financieros son 100% privados, se procesan cifrados en tu equipo y nadie más tiene acceso a ellos.` |
| `🫀 Pulso Emocional ante el Riesgo` | `🎯 Tu Perfil de Riesgo y Criterio de Inversión` |
| `Antes de recetarte cualquier inversión, miremos qué tanta variación aguanta tu corazón durmiendo tranquilo.` | `Antes de elegir en qué invertir, identifiquemos tu tolerancia real a las variaciones del mercado y tu horizonte de tiempo.` |
| `🩻 Radiografía de tu Sueldo y Pequeñas Fugas` | `📊 Análisis de tu Sueldo, Gastos y Flujo de Caja` |
| `Revisemos con lupa cuánto te llega libre después de descuentos de ley y por dónde se están escapando pesitos sin darte cuenta.` | `Calculemos cuánto recibes neto después de descuentos de ley e identifiquemos gastos hormiga para liberar ahorro mensual.` |
| `🩹 Alivio de Deudas que te Quitan Oxígeno` | `🔓 Estrategia para Salir de Deudas y Pagar Menos Intereses` |
| `Si tienes créditos caros, primero bajemos esa fiebre pagando menos intereses y liberando flujo mensual para ti.` | `Si tienes créditos con tasas altas, prioricemos su pago para ahorrar intereses y liberar flujo de caja cada mes.` |
| `🌱 Vitaminas para Multiplicar tu Sueldo` | `🌱 Plan de Inversión Mensual desde tu Sueldo` |
| `🏡 Chequeo para Comprar Casa sin Ahogarte` | `🏡 Viabilidad para Comprar Vivienda o Invertir en Finca Raíz` |
| `Revisemos con calma si la cuota de esa vivienda cuida la tranquilidad de tu hogar y si te conviene más Pesos o UVR.` | `Evaluemos si la cuota cumple el tope del 30% de la Ley 546 y comparemos con números claros entre Pesos, UVR o invertir en un FIC.` |
| `🛡️ Prueba de Esfuerzo para tus Grandes Planes` | `🛡️ Prueba de Estrés Financiero para tus Grandes Metas` |
| `Hagamos una prueba de esfuerzo con 1.000 escenarios futuros...` | `Ejecutemos una Prueba de Estrés Financiero con 1.000 escenarios de Monte Carlo para evaluar tus metas de matrimonio, hijos o estudio.` |
| `Son los dos exámenes médicos de cualquier negocio...` (`VPN_TIR`) | `Son los dos indicadores decisivos de cualquier inversión: la TIR mide el rendimiento porcentual anual y el VPN cuántos pesos netos genera frente a tu mejor alternativa segura.` |
| `Dos recetas médicas para salir de deudas... te da alivio emocional rápido` (`AVALANCHA_NIEVE`) | `Dos estrategias probadas para salir de deudas: 'Avalancha' prioriza la tasa más alta (ahorra más intereses) y 'Bola de Nieve' liquida primero el saldo menor (libera cuotas rápido).` |
| `Una 'prueba de esfuerzo' igual a la que te hace el cardiólogo... tu corazón financiero está listo` (`MONTE_CARLO`) | `Una Prueba de Estrés Financiero que evalúa tu presupuesto en 1.000 escenarios económicos posibles (inflación alta o caída temporal de ingresos): superar más de 850 de 1.000 indica alta solidez.` |
| Tooltip `🩺 {termino_tecnico}: ...` | Tooltip `💡 {termino_tecnico}: ...` |
| `Tu Médico Financiero en esta etapa:` | `Responsable OED en esta etapa:` |
| `🩺💚 Signos vitales saludables:` | `✅ Diagnóstico Financiero favorable:` |
| `🩺💙 Lectura tranquila de tu médico financiero:` | `ℹ️ Análisis de tu Asesor Financiero:` |
| `🩺🧡 Chequeo preventivo a tiempo:` | `⚠️ Revisión preventiva:` |
| `🩺❤️‍🩹 Pausa protectora para cuidar tu tranquilidad:` | `🛑 Riesgo alto — Te recomendamos esperar:` |
| `💊 Tu Receta Práctica para este Mes:` | `📌 Plan de Acción para este Mes:` |
| `🩺 ¿Alguna palabra te sonó a chino? Pregúntale aquí al Diccionario del Médico Amigo` | `📘 ¿Tienes dudas con algún concepto? Consulta aquí el Diccionario Financiero OED` |
| `🩺 Explicación de tu Médico Amigo:` | `💡 En palabras sencillas:` |
| `Manual de Marca: "Tu Médico Financiero Amigo" — Equipo OED` | `Manual de Marca: "Asesor Financiero de Confianza" — Equipo OED` |
