# MANUAL PASO A PASO 'PARA DUMMIES' - TALLER ANTIGRAVITY & GIT | EQUIPO OED COLOMBIA

## GUÍA PASO A PASO 'PARA DUMMIES': TALLER ANTIGRAVITY EQUIPO OED

**Cómo usar Antigravity desde cero, en qué orden se ejecuta el proyecto y qué hace cada integrante**

Esta guía está escrita sin tecnicismos confusos ('Para Dummies') para que Camilo, Nidia, Nelson, Catalina, Jesi y Salin sepan exactamente dónde hacer clic, qué comando pegar en la terminal, en qué orden funciona el proyecto y cómo actualizar Git en cada etapa sin miedo a dañar nada.

### 1. Conceptos Básicos 'Para Dummies' Antes de Empezar

**¿QUÉ ES... La Terminal (Consola) vs. El Chat de Antigravity**
1) **LA TERMINAL** es la ventana inferior (se abre con `Ctrl + Ñ` o menú `Terminal -> New Terminal`) donde se escriben comandos de Git y Python. 
2) **EL CHAT DE ANTIGRAVITY** es el panel donde hablas en español con la IA para pedirle que cree o edite código.

**¿CÓMO... Trabajar los 6 al mismo tiempo sin tener que esperar a nadie**
En el archivo `config/config.yaml` ya dejamos cargado un 'Usuario Semilla de Prueba' (con salario de $6.500.000 COP, gastos y deudas). Gracias a eso, los 6 pueden programar al mismo tiempo desde el minuto 1.

---

### 2. Orden de Ejecución del Proyecto (La Analogía de la Consulta Médica Financiera)

Imagina que el software es una clínica financiera en Colombia. Cuando entra un usuario, el programa ejecuta los módulos en este orden exacto (del Paso 0 al Paso 6) a través del archivo `app.py`:

#### PASO 0: Firma de Consentimiento y Reglas de Juego (Nelson + Camilo)
*   **Archivos:** `src/data_governance.py` y `src/finance.py`. 
*   Primero el usuario autoriza el uso local de sus datos (Ley 1581 de 2012, liderado por Nelson) y se cargan las fórmulas de tasas EA/EM, UVT e IPC (Camilo).

#### PASO 1: Módulo 6 - Examen de Personalidad de Riesgo y Educación (Salin Avellaneda)
*   **Archivo:** `src/mod6_educacion_financiera.py`. 
*   Por ley colombiana (Decreto 2555 de 2010), antes de invertir Salin mide si el usuario es Conservador, Moderado o Agresivo, y le enseña por qué loterías/pirámides no son inversión.

#### PASO 2: Módulo 1 - Radiografía del Sueldo, Presupuesto y Gastos Hormiga (Nidia Velásquez)
*   **Archivo:** `src/mod1_presupuesto.py`. 
*   Nidia toma el sueldo bruto, descuenta Salud (4%), Pensión (4%), FSP y Retefuente, resta gastos fijos y gastos hormiga, y descubre cuánto dinero libre queda al mes (`excedente_mensual_cop`).

#### PASO 3: Módulo 3 - Cirugía de Deudas con Avalancha vs. Bola de Nieve (Catalina Moreno)
*   **Archivo:** `src/mod3_gestion_deudas.py`. 
*   Catalina toma el dinero libre que calculó Nidia y primero ataca las deudas caras (validando que no superen la Tasa de Usura SFC) y simula abonos a capital (Ley 1328 de 2009).

#### PASO 4: Módulo 2 - Multiplicar el Sueldo en Inversiones de Bajo Monto (Camilo Matson)
*   **Archivo:** `src/mod2_inversiones_salario.py`. 
*   Con las deudas bajo control y el perfil de riesgo que entregó Salin, Camilo invierte el excedente mensual en Neobancos, CDTs, FICs, Cuentas AFC y Bolsa de Valores de Colombia (BVC).

#### PASO 5: Módulo 4 - Compra Inteligente de Vivienda o Finca Raíz (Jesi)
*   **Archivo:** `src/mod4_finca_raiz.py`. 
*   Jesi usa el ahorro acumulado (AFC + cesantías) y el ingreso familiar para evaluar comprar apartamento VIS o No VIS en Pesos vs. UVR, cuidando que la cuota no pase del 30% del ingreso (Ley 546).

#### PASO 6: Módulo 5 - Simulador del Futuro: Casarse, Tener Hijos o Tomar Créditos (Nelson)
*   **Archivo:** `src/mod5_decisiones_vida.py`. 
*   Con toda la foto financiera lista, Nelson corre 1.000 simulaciones actuariales (Monte Carlo) para responder si el hogar aguanta financieramente casarse o criar un hijo de 0 a 23 años.


### 3. El "Ritual" de Git: Cómo guardar y subir tu trabajo sin dañar nada

Como los 6 están trabajando al mismo tiempo, cada vez que termines una parte de tu módulo, debes hacer este "ritual" en la **Terminal** para enviar tus cambios a GitHub y que los demás puedan verlos.

**Paso 1: Ver qué archivos cambiaste hoy**
Copia y pega este comando y presiona Enter:
```bash
git status
```
*(Te mostrará en letras rojas los archivos que modificaste o creaste).*

**Paso 2: Empacar tus cambios**
```bash
git add .
```
*(El espacio y el punto al final son súper importantes, significan "empacar TODO lo que cambié").*

**Paso 3: Ponerle un mensaje/etiqueta a tu paquete**
```bash
git commit -m "Escribe aquí qué hiciste"
```
*(Ejemplo: `git commit -m "Nidia: Terminé de calcular el excedente mensual en el Módulo 1"`).*

**Paso 4: Enviar tus cambios a la nube (GitHub)**
```bash
git push
```
*(¡Listo! Tus compañeros ya pueden ver tu trabajo).*

---

### 4. ¿Qué hacer todos los días al empezar a trabajar?

Antes de escribir una sola línea de código nueva o pedirle algo a la IA, abre tu **Terminal** y descarga lo que tus compañeros hicieron el día anterior:

```bash
git pull
```
*(Esto traerá todos los cambios nuevos a tu computador. Si dice "Already up to date", significa que ya tienes la última versión).*