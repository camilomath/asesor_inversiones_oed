# 🩺 Manual de Marca, Voz de "Médico Amigo" y Estándar de Interfaz — Equipo OED Colombia

> **Acuerdo de Equipo (Autonomía Total):**  
> Nadie modifica el código ni los archivos de otro compañero. **Cada integrante (Camilo, Nidia, Nelson, Catalina, Jesi y Salin) aplica este manual únicamente en su propia interfaz** usando la plantilla compartida [`src/oed_design_system.py`](src/oed_design_system.py), para que al unir los 6 módulos todo el sistema tenga **exactamente la misma forma visual, el mismo tono cálido y las mismas explicaciones interactivas**.

---

## 1. Nuestra Identidad: El "Médico Financiero Amigo"

Cuando una persona abre cualquiera de nuestros 6 módulos, debe sentir que se sentó a conversar con un **médico amigo de confianza**:

1. **Cercano, cálido y cero regaños:**
   * ❌ *Cómo NO escribir:* `"Relación cuota/ingreso excede el límite normativo; solicitud rechazada."*
   * ✅ *Cómo SÍ escribir:* `"Hagamos una pausa protectora para cuidar tu sueño tranquilo: hoy esta cuota apretaría tu bolsillo mensual. Miremos dos caminos fáciles para lograrlo..."*
2. **Regla "Cero Palabras Huérfanas" (Explicación ahí mismo con `?`):**
   * Si en pantalla aparece **cualquier término que requiera explicación** —financiero (`EA`, `TIR`, `FIC`), de vivienda (`VIS`, `UVR`, `Leasing`), de nómina/impuestos (`IBC`, `UVT`, `SMMLV`, `4x1000`, `Cuenta AFC`), legal (`Ley 546`, `Tasa de Usura`, `Fogafín`, `Habeas Data`) o estadístico (`Valor Esperado`, `Monte Carlo`)—, **la explicación debe salir ahí mismo** al pasar el mouse o tocar la palabra (`?`).
   * La plantilla `src/oed_design_system.py` detecta automáticamente más de **25 términos de las 5 familias** dentro de tus párrafos y les incrusta la burbuja explicativa **`?`** sin trabajo extra.
3. **Siempre cerramos con Receta Práctica:** Todo diagnóstico termina con una sola acción concreta en pesos colombianos (`$ COP`) para aplicar este mismo mes (*"💊 Tu Receta Práctica para este Mes"*).

---

## 2. Estructura Estándar de Interfaz (Los 5 Bloques en el Mismo Orden)

Para que todas las pantallas del proyecto se vean uniformes, cada integrante organiza su interfaz de arriba hacia abajo en estos **5 bloques fijos**:

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ BLOQUE 1: Barra de Progreso (Pasos 0 al 6) + Saludo del Médico Amigo         │
│           -> render_encabezado_modulo_oed(paso_actual=...)                   │
├──────────────────────────────────────────────────────────────────────────────┤
│ BLOQUE 2: Datos de la Persona (Expander limpio de 2 o 3 columnas)            │
│           -> Precargado con `perfil_semilla_taller` + ayudas claras (`help`) │
├──────────────────────────────────────────────────────────────────────────────┤
│ BLOQUE 3: Diagnóstico con Burbujas (?) + 💊 Receta del Mes + 4 Signos Vitales │
│           -> render_semaforo_ciudadano_oed(...) + 4 tarjetas `st.metric`     │
├──────────────────────────────────────────────────────────────────────────────┤
│ BLOQUE 4: Gráficas Interactivas con la Paleta Oficial del Consultorio        │
│           -> aplicar_estilo_plotly_oed(fig, titulo="...")                    │
├──────────────────────────────────────────────────────────────────────────────┤
│ BLOQUE 5: Diccionario Desplegable del Médico Amigo (5 Familias de Términos)  │
│           -> render_glosario_interactivo_oed()                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Paleta Oficial del Consultorio OED

Centralizada en `PALETA_MARCA_OED` y `COLORES_GRAFICAS_OED` dentro de `src/oed_design_system.py`:

| Rol Visual | Nombre Oficial | Código HEX | Uso obligatorio en todas las interfaces |
| :--- | :--- | :---: | :--- |
| **Bata Médica (Confianza)** | **Azul Confianza OED** | `#0F294A` | Encabezados principales, títulos y fondo de burbujas explicativas (`?`). |
| **Cuidado Activo** | **Azul Cuidado Activo** | `#1D4ED8` | Botones principales, subrayado de términos con `?` y línea principal en gráficas. |
| **Receta del Mes** | **Naranja Receta Positiva** | `#EA580C` | Píldora del paso activo y tarjeta de *"💊 Tu Receta Práctica para este Mes"*. |
| **Signos Sanos** | **Verde Bienestar** | `#15803D` | Diagnóstico saludable (`nivel="verde"` — cumple reglas y da tranquilidad). |
| **Prevención** | **Ámbar Preventivo** | `#B45309` | Chequeo preventivo (`nivel="ambar"` — viable hoy, vigilar inflación o riesgos). |
| **Pausa Protectora** | **Rojo Protector** | `#B91C1C` | Cuidado intensivo (`nivel="rojo"` — alerta de sobreendeudamiento o usura sin regañar). |

---

## 4. Las 5 Familias del Diccionario Integrado (Listas para Usar)

El diccionario `GLOSARIO_LENGUAJE_CLARO_OED` ya incluye explicaciones amigables y ejemplos cotidianos en `$ COP` para los módulos de todo el equipo:

* **1. Financiero e Inversión (Camilo / Todos):** `EA`, `EM`, `IPC / Inflación`, `Interés Compuesto`, `CDT`, `FIC`, `VPN y TIR`.
* **2. Vivienda y Finca Raíz (Jesi):** `VIP / VIS / No VIS`, `UVR`, `Ley 546 (Regla del 30%)`, `Encargo Fiduciario`, `Leasing Habitacional`, `Ley 820`, `Cap Rate y Cash-on-Cash`.
* **3. Nómina, Trabajo e Impuestos (Nidia / Camilo / Jesi):** `SMMLV`, `IBC (40% independientes)`, `UVT`, `Cuenta AFC`, `4x1000 (GMF)`.
* **4. Deudas y Leyes Protectoras (Catalina / Nelson):** `Tasa de Usura SFC`, `Avalancha vs. Bola de Nieve`, `Ley 1328 (Abonos a capital)`, `Seguro Fogafín`, `Habeas Data`.
* **5. Probabilidad y Futuro (Salin / Nelson):** `Valor Esperado E[X]`, `Simulación Actuarial de Monte Carlo`.

*(Si necesitas un término adicional propio de tu módulo, agrégalo en `GLOSARIO_LENGUAJE_CLARO_OED` dentro de `src/oed_design_system.py` y se activará automáticamente con `?`).*

---

## 5. Tabla de Pasos por Integrante (`paso_actual`)

Cada compañero usa su número de `paso_actual` al llamar `render_encabezado_modulo_oed(paso_actual=X)`:

| `paso_actual` | Integrante | Título Amigable en Pantalla |
| :-: | :--- | :--- |
| `0` | **Nelson + Camilo** | 🩺 *Bienvenida al Consultorio y Confidencialidad* |
| `1` | **Salin Avellaneda** | 🫀 *Pulso Emocional ante el Riesgo* |
| `2` | **Nidia Velásquez** | 🩻 *Radiografía de tu Sueldo y Pequeñas Fugas* |
| `3` | **Catalina Moreno** | 🩹 *Alivio de Deudas que te Quitan Oxígeno* |
| `4` | **Camilo Matson** | 🌱 *Vitaminas para Multiplicar tu Sueldo* |
| `5` | **Jesi** | 🏡 *Chequeo para Comprar Casa sin Ahogarte* |
| `6` | **Nelson** | 🛡️ *Prueba de Esfuerzo para tus Grandes Planes* |

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
    # BLOQUE 1: Encabezado del Consultorio + Barra de 7 Pasos
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

    # BLOQUE 3: Diagnóstico del Médico Amigo (las siglas sacan burbuja ? solas) + 4 Signos Vitales
    render_semaforo_ciudadano_oed(
        nivel="verde",  # Usa: "verde", "azul", "ambar" o "rojo"
        titulo_claro="Tus signos vitales financieros están en buen camino",
        explicacion_humana=(
            f"Con un ahorro de {formatear_cop_claro(ahorro)} en un FIC o CDT protegido por Fogafín, "
            "tu dinero crece con interés compuesto superando la inflación del IPC."
        ),
        siguiente_paso_accionable="Separa ese monto el mismo día que recibes tu pago mensual.",
    )

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Ingreso Mensual", formatear_cop_claro(ingreso))
    k2.metric("Ahorro Mensual", formatear_cop_claro(ahorro))
    k3.metric("Porcentaje de Ahorro", f"{(ahorro / max(ingreso, 1)) * 100:.1f}%")
    k4.metric("Estado del Chequeo", "Saludable")

    # BLOQUE 4: Tus gráficas Plotly con la paleta oficial del equipo
    # fig = aplicar_estilo_plotly_oed(mi_fig, titulo="Proyección de tu Bienestar Financiero")
    # st.plotly_chart(fig, use_container_width=True)

    # BLOQUE 5: Diccionario desplegable de las 5 familias de términos
    render_glosario_interactivo_oed()
```

---

## 7. Checklist Rápido Antes de Subir tu Interfaz (1 Minuto)

- [ ] ¿Usé `render_encabezado_modulo_oed(paso_actual=...)` con el número de mi módulo?
- [ ] ¿Redacté mis mensajes como **Médico Amigo** (sin regañar y cerrando con una receta práctica en `$ COP`)?
- [ ] ¿Usé `render_semaforo_ciudadano_oed(...)` para que todos los términos técnicos/legales salgan con su explicación `?`?
- [ ] ¿Pasé mis gráficas por `aplicar_estilo_plotly_oed(fig)` para mantener los mismos colores del equipo?
- [ ] ¿Incluí `render_glosario_interactivo_oed()` al cierre de la pantalla?

---

## 8. Ver el Manual Interactivo en el Navegador (100% Local)

Cualquier integrante puede abrir la vista viva del Manual de Marca, probar las burbujas `?` y copiar su bloque de código ejecutando:

```powershell
py src/oed_design_system.py
```
