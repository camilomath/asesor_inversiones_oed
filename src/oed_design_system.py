"""
SISTEMA DE DISEÑO, MANUAL DE MARCA Y VOZ DE "ASESOR FINANCIERO DE CONFIANZA" — EQUIPO OED COLOMBIA.

Filosofía central ("Cero Palabras Huérfanas"):
1. Tono de Asesor Financiero de Confianza: cercano, claro, empático y sin regaños.
   - Indicadores Clave -> Diagnóstico Financiero -> 📌 Plan de Acción para este Mes.
2. Ningún término financiero, legal, tributario, laboral o estadístico queda sin explicación:
   - `enriquecer_texto_con_explicaciones(texto)` detecta automáticamente siglas y tecnicismos dentro
     de cualquier párrafo y les incrusta una burbuja explicativa interactiva al pasar el cursor o tocar.
   - `GLOSARIO_LENGUAJE_CLARO_OED` cubre las 5 familias de conceptos de los 6 módulos OED.

Modos de uso:
- En cualquier módulo del equipo (`Streamlit` + `Plotly`):
    from src.oed_design_system import (
        render_encabezado_modulo_oed,
        render_semaforo_ciudadano_oed,
        render_glosario_interactivo_oed,
        enriquecer_texto_con_explicaciones,
        aplicar_estilo_plotly_oed,
    )
- Vista interactiva completa del Manual de Marca en navegador (100% offline):
    py src/oed_design_system.py
"""

from __future__ import annotations

import html
import json
import re
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List

if __package__ in (None, ""):
    _PROJECT_ROOT = Path(__file__).resolve().parent.parent
    if str(_PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(_PROJECT_ROOT))


# ==============================================================================
# 1. PALETA OFICIAL OED (ASESOR FINANCIERO DE CONFIANZA)
# ==============================================================================

PALETA_MARCA_OED: Dict[str, Dict[str, str]] = {
    "azul_confianza": {
        "nombre": "Azul Solidez OED",
        "hex": "#0F294A",
        "uso": "Encabezados principales, títulos institucionales y fondo de burbujas explicativas (?).",
    },
    "azul_impulso": {
        "nombre": "Azul Acción Financiera",
        "hex": "#1D4ED8",
        "uso": "Botones principales, subrayado de términos con (?) y serie base en gráficas.",
    },
    "naranja_calidez": {
        "nombre": "Naranja Plan de Acción",
        "hex": "#EA580C",
        "uso": "Indicador del paso activo y tarjeta de '📌 Plan de Acción para este Mes'.",
    },
    "verde_meta": {
        "nombre": "Verde Viabilidad",
        "hex": "#15803D",
        "uso": "Diagnóstico Financiero favorable: cumple reglas legales y capacidad de pago.",
    },
    "ambar_ajuste": {
        "nombre": "Ámbar Revisión Preventiva",
        "hex": "#B45309",
        "uso": "Revisión preventiva: viable hoy, pero requiere vigilar inflación, tasas o liquidez.",
    },
    "rojo_protector": {
        "nombre": "Rojo Riesgo Alto",
        "hex": "#B91C1C",
        "uso": "Riesgo alto / Te recomendamos esperar para evitar sobreendeudamiento o usura.",
    },
    "fondo_claro": {
        "nombre": "Gris Claro Fondo OED",
        "hex": "#F4F7FB",
        "uso": "Fondo limpio y descansado para analizar cifras con claridad.",
    },
}

COLORES_GRAFICAS_OED: List[str] = [
    "#1D4ED8",  # Azul Acción Financiera
    "#EA580C",  # Naranja Plan de Acción
    "#15803D",  # Verde Viabilidad
    "#7C3AED",  # Violeta Comparativo (FIC / Escenario alterno)
    "#DC2626",  # Rojo Alerta Financiera (Gastos hormiga / Inflación UVR / Usura)
    "#475569",  # Gris Referencia Legal (Topes normativos)
]


# ==============================================================================
# 2. LOS 7 PASOS DE LA RUTA FINANCIERA OED (PASOS 0 A 6)
# ==============================================================================

RUTA_CLINICA_FINANCIERA_OED: List[Dict[str, Any]] = [
    {
        "paso": 0,
        "icono": "🤝",
        "titulo_ciudadano": "Bienvenida a OED y Protección de tus Datos",
        "modulo_tecnico": "Habeas Data Local y Reglas Base",
        "responsable": "Nelson + Camilo",
        "archivo": "src/data_governance.py · src/finance.py",
        "saludo_medico": "Tus datos financieros son 100% privados, se procesan cifrados bajo Habeas Data en tu equipo y nadie más tiene acceso a ellos.",
    },
    {
        "paso": 1,
        "icono": "🎯",
        "titulo_ciudadano": "Tu Perfil de Riesgo y Criterio de Inversión",
        "modulo_tecnico": "Módulo 6: Educación Financiera y Probabilidad",
        "responsable": "Salin Avellaneda",
        "archivo": "src/mod6_educacion_financiera.py",
        "saludo_medico": "Antes de elegir en qué invertir, identifiquemos tu tolerancia real a las variaciones del mercado, el Valor Esperado y tu horizonte de tiempo.",
    },
    {
        "paso": 2,
        "icono": "📊",
        "titulo_ciudadano": "Análisis de tu Sueldo, Gastos y Flujo de Caja",
        "modulo_tecnico": "Módulo 1: Presupuesto y Flujo de Caja",
        "responsable": "Nidia Velásquez",
        "archivo": "src/mod1_presupuesto.py",
        "saludo_medico": "Calculemos cuánto recibes neto sobre tu IBC después de descuentos de ley e identifiquemos gastos hormiga para liberar ahorro mensual.",
    },
    {
        "paso": 3,
        "icono": "🔓",
        "titulo_ciudadano": "Estrategia para Salir de Deudas y Pagar Menos Intereses",
        "modulo_tecnico": "Módulo 3: Optimización de Deudas",
        "responsable": "Catalina Moreno",
        "archivo": "src/mod3_gestion_deudas.py",
        "saludo_medico": "Si tienes créditos con tasas altas cercanas a la Tasa de Usura, prioricemos su pago con Avalancha o Bola de Nieve para liberar flujo mensual.",
    },
    {
        "paso": 4,
        "icono": "🌱",
        "titulo_ciudadano": "Plan de Inversión Mensual desde tu Sueldo",
        "modulo_tecnico": "Módulo 2: Micro-Inversiones Salariales",
        "responsable": "Camilo Matson",
        "archivo": "src/mod2_inversiones_salario.py",
        "saludo_medico": "Con tu flujo de caja ordenado, pongamos tus ahorros mensuales en CDT o FIC a crecer con interés compuesto por encima del IPC.",
    },
    {
        "paso": 5,
        "icono": "🏡",
        "titulo_ciudadano": "Viabilidad para Comprar Vivienda o Invertir en Finca Raíz",
        "modulo_tecnico": "Módulo 4: Inversión Patrimonial en Finca Raíz",
        "responsable": "Jesi",
        "archivo": "src/mod4_finca_raiz.py",
        "saludo_medico": "Evaluemos si la cuota cumple el tope del 30% de la Ley 546 y comparemos con números claros entre Pesos, UVR o invertir en un FIC.",
    },
    {
        "paso": 6,
        "icono": "🛡️",
        "titulo_ciudadano": "Prueba de Estrés Financiero para tus Grandes Metas",
        "modulo_tecnico": "Módulo 5: Viabilidad Actuarial de Decisiones de Vida",
        "responsable": "Nelson",
        "archivo": "src/mod5_decisiones_vida.py",
        "saludo_medico": "Ejecutemos una Prueba de Estrés Financiero con 1.000 escenarios de Monte Carlo para evaluar tus metas de matrimonio, hijos o estudio.",
    },
]


# ==============================================================================
# 3. DICCIONARIO FINANCIERO OED: TODOS LOS TÉRMINOS EXPLICADOS EN CLARO
#    (Financieros · Leyes Colombianas · Nómina e Impuestos · Vivienda · Estadística)
# ==============================================================================

GLOSARIO_LENGUAJE_CLARO_OED: Dict[str, Dict[str, Any]] = {
    # --- FAMILIA 1: CONCEPTOS FINANCIEROS E INVERSIÓN ---
    "EA": {
        "categoria": "Financiero e Inversión",
        "termino_tecnico": "Tasa Efectiva Anual (EA)",
        "como_no_decir": "Tasa compuesta anualizada bajo convención de capitalización SFC.",
        "lenguaje_claro": "Es la velocidad real a la que crece un ahorro (o una deuda) al cumplir 12 meses completos. En Colombia jamás se divide simplemente entre 12.",
        "ejemplo_cotidiano": "$1.000.000 guardados al 10% EA se convierten en $1.100.000 al cabo de un año antes de impuestos.",
        "alias": ["EA", "Efectivo Anual", "Efectiva Anual"],
    },
    "EM": {
        "categoria": "Financiero e Inversión",
        "termino_tecnico": "Tasa Efectiva Mensual (EM)",
        "como_no_decir": "Raíz duodécima del factor de capitalización efectivo anual menos uno.",
        "lenguaje_claro": "Es la fracción exacta de interés que te cobran o te pagan en un solo mes, calculada con interés sobre interés.",
        "ejemplo_cotidiano": "Un 12% EA equivale aproximadamente a 0,95% EM cada mes (no a 1%).",
        "alias": ["EM", "Efectiva Mensual", "Efectivo Mensual"],
    },
    "IPC": {
        "categoria": "Financiero e Inversión",
        "termino_tecnico": "Inflación / IPC DANE",
        "como_no_decir": "Variación porcentual interanual del Índice de Precios al Consumidor.",
        "lenguaje_claro": "Qué tanto subió el costo del mercado, el arriendo y los bienes básicos en Colombia durante el año según el DANE.",
        "ejemplo_cotidiano": "Si el IPC es 5,2% y tu dinero guardado en efectivo rinde 0%, perdiste 5,2% de poder adquisitivo.",
        "alias": ["IPC", "IPC DANE", "inflación"],
    },
    "INTERES_COMPUESTO": {
        "categoria": "Financiero e Inversión",
        "termino_tecnico": "Interés Compuesto",
        "como_no_decir": "Capitalización exponencial por reinversión periódica de rendimientos.",
        "lenguaje_claro": "El efecto multiplicador del ahorro: los rendimientos que ganas este mes se reinvierten y empiezan a generar sus propios rendimientos el mes siguiente.",
        "ejemplo_cotidiano": "Invertir de forma constante durante 10 años termina sumando más por rendimientos acumulados que por los aportes de tu bolsillo.",
        "alias": ["interés compuesto", "interes compuesto"],
    },
    "CDT": {
        "categoria": "Financiero e Inversión",
        "termino_tecnico": "CDT (Certificado de Depósito a Término)",
        "como_no_decir": "Título valor de renta fija a plazo emitido por establecimiento de crédito.",
        "lenguaje_claro": "Un acuerdo con un banco vigilado: dejas tu dinero a un plazo fijo (ej. 90, 180 o 360 días) a cambio de una tasa pactada y conocida desde el primer día.",
        "ejemplo_cotidiano": "Ideal para metas con fecha definida cuando sabes que no necesitarás retirar ese dinero antes del vencimiento.",
        "alias": ["CDT", "CDTs"],
    },
    "FIC": {
        "categoria": "Financiero e Inversión",
        "termino_tecnico": "FIC (Fondo de Inversión Colectiva)",
        "como_no_decir": "Vehículo fiduciario colectivo administrado por sociedad vigilada SFC.",
        "lenguaje_claro": "Un fondo vigilado por la Superintendencia Financiera donde profesionales invierten el dinero de miles de personas juntas desde montos bajos ($20.000 COP).",
        "ejemplo_cotidiano": "Te permite acceder a portafolios diversificados aunque empieces separando una fracción pequeña de tu sueldo.",
        "alias": ["FIC", "FICs", "Fondo de Inversión Colectiva"],
    },
    "VPN_TIR": {
        "categoria": "Financiero e Inversión",
        "termino_tecnico": "VPN y TIR",
        "como_no_decir": "Valor Presente Neto descontado al COK y Tasa Interna de Retorno.",
        "lenguaje_claro": "Son los dos indicadores decisivos de cualquier inversión: la TIR mide el rendimiento porcentual anual y el VPN cuántos pesos netos genera hoy frente a tu mejor alternativa segura.",
        "ejemplo_cotidiano": "Si el VPN es mayor a $0, el proyecto crea valor; si es menor a $0, obtienes mejor resultado invirtiendo ese capital en un CDT o FIC.",
        "alias": ["VPN", "TIR", "COK", "costo de oportunidad"],
    },
    # --- FAMILIA 2: VIVIENDA Y FINCA RAÍZ ---
    "VIS_VIP": {
        "categoria": "Vivienda y Finca Raíz",
        "termino_tecnico": "Vivienda VIP, VIS y No VIS",
        "como_no_decir": "Segmentación regulatoria habitacional según topes en salarios mínimos CONPES.",
        "lenguaje_claro": "Son los segmentos de precio de vivienda en Colombia medidos en salarios mínimos: VIP (hasta 90 SMMLV), VIS (hasta 135 o 150 SMMLV, con acceso a subsidios) y No VIS (más de 150 SMMLV).",
        "ejemplo_cotidiano": "Si el apartamento es VIS y tus ingresos son de hasta 4 SMMLV, puedes postularte al subsidio de tu Caja de Compensación para la cuota inicial.",
        "alias": ["VIS", "VIP", "No VIS"],
    },
    "UVR": {
        "categoria": "Vivienda y Finca Raíz",
        "termino_tecnico": "UVR (Unidad de Valor Real)",
        "como_no_decir": "Unidad de cuenta hipotecaria indexada al IPC certificada por el Banco de la República.",
        "lenguaje_claro": "Modalidad de crédito hipotecario donde el saldo de la deuda y las cuotas se ajustan con la inflación. Inicia con una cuota más baja que en pesos, pero sube cuando sube el IPC.",
        "ejemplo_cotidiano": "Si la inflación sube fuerte, durante los primeros años el saldo expresado en pesos puede crecer aunque pagues puntualmente cada mes.",
        "alias": ["UVR"],
    },
    "LEY_546": {
        "categoria": "Vivienda y Finca Raíz",
        "termino_tecnico": "Ley 546 de 1999 (Regla del 30%)",
        "como_no_decir": "Límite legal de relación primera cuota hipotecaria sobre ingreso familiar comprobado.",
        "lenguaje_claro": "Regla de protección hipotecaria en Colombia: la primera cuota del crédito de vivienda (incluyendo seguros) no puede superar el 30% de los ingresos mensuales del hogar.",
        "ejemplo_cotidiano": "Si el ingreso familiar neto es $8.000.000, la primera cuota máxima permitida por ley es $2.400.000.",
        "alias": ["Ley 546", "Regla del 30%"],
    },
    "ENCARGO_FIDUCIARIO": {
        "categoria": "Vivienda y Finca Raíz",
        "termino_tecnico": "Encargo Fiduciario (Compra sobre Planos)",
        "como_no_decir": "Patrimonio autónomo de preventa inmobiliaria administrado por fiduciaria.",
        "lenguaje_claro": "Cuenta administrada por una fiduciaria vigilada donde abonas mes a mes la cuota inicial mientras avanza el proyecto: la constructora solo recibe los recursos al cumplir el punto de equilibrio.",
        "ejemplo_cotidiano": "Te permite reunir el 30% de cuota inicial entre 18 y 36 meses combinando ahorro mensual, primas y cesantías.",
        "alias": ["encargo fiduciario", "fiducia", "sobre planos"],
    },
    "LEASING": {
        "categoria": "Vivienda y Finca Raíz",
        "termino_tecnico": "Leasing Habitacional",
        "como_no_decir": "Contrato de arrendamiento financiero inmobiliario con opción de adquisición.",
        "lenguaje_claro": "Modalidad de financiación donde la entidad financiera conserva la titularidad mientras pagas un canon mensual y, al finalizar el plazo, ejerces la opción de compra a tu nombre.",
        "ejemplo_cotidiano": "Permite financiar hasta el 80%–85% del inmueble y difiere los gastos de escrituración para el final del contrato.",
        "alias": ["Leasing Habitacional", "Leasing"],
    },
    "LEY_820": {
        "categoria": "Vivienda y Finca Raíz",
        "termino_tecnico": "Ley 820 de 2003 (Arrendamiento en Colombia)",
        "como_no_decir": "Tope normativo del canon mensual equivalente al 1% del valor comercial.",
        "lenguaje_claro": "Ley de arrendamiento de vivienda urbana en Colombia: establece que el canon mensual no puede exceder el 1% del valor comercial del inmueble y su reajuste anual máximo es el IPC.",
        "ejemplo_cotidiano": "Para un apartamento de $200.000.000 COP, el canon máximo legal es $2.000.000 COP al mes (en mercado suele ubicarse entre 0,55% y 0,75%).",
        "alias": ["Ley 820"],
    },
    "CAP_RATE": {
        "categoria": "Vivienda y Finca Raíz",
        "termino_tecnico": "Cap Rate Neto y Cash-on-Cash",
        "como_no_decir": "Ingreso Operativo Neto (NOI) sobre valor del activo y retorno efectivo sobre equity.",
        "lenguaje_claro": "El Cap Rate Neto mide qué rentabilidad anual libre deja el arriendo después de descontar predial, administración, vacancia y mantenimiento. El Cash-on-Cash mide el flujo anual frente al capital inicial aportado.",
        "ejemplo_cotidiano": "Evita sobreestimar la rentabilidad mirando solo el arriendo bruto sin descontar los costos reales del inmueble.",
        "alias": ["Cap Rate", "NOI", "Cash-on-Cash"],
    },
    # --- FAMILIA 3: NÓMINA, TRABAJO E IMPUESTOS ---
    "SMMLV": {
        "categoria": "Nómina e Impuestos",
        "termino_tecnico": "SMMLV (Salario Mínimo Mensual Legal Vigente)",
        "como_no_decir": "Remuneración mínima vital indexada por decreto anual en Colombia.",
        "lenguaje_claro": "El salario mínimo oficial del año en Colombia. Además de remuneraciones, define los topes legales de vivienda VIS/VIP y de subsidios familiares.",
        "ejemplo_cotidiano": "Cuando un proyecto VIS cuesta 140 SMMLV, su precio se calcula multiplicando 140 por el salario mínimo del año de escrituración.",
        "alias": ["SMMLV", "salarios mínimos"],
    },
    "IBC": {
        "categoria": "Nómina e Impuestos",
        "termino_tecnico": "IBC (Ingreso Base de Cotización)",
        "como_no_decir": "Base salarial o proporción del 40% de honorarios para liquidación PILA.",
        "lenguaje_claro": "La base sobre la cual se liquidan tus aportes a Salud, Pensión y ARL. Para trabajadores independientes por prestación de servicios corresponde al 40% de sus honorarios brutos.",
        "ejemplo_cotidiano": "Si facturas $5.000.000 COP por honorarios, tu seguridad social se calcula sobre un IBC de $2.000.000 COP.",
        "alias": ["IBC"],
    },
    "UVT": {
        "categoria": "Nómina e Impuestos",
        "termino_tecnico": "UVT (Unidad de Valor Tributario)",
        "como_no_decir": "Unidad de medida tributaria reajustada anualmente por la DIAN.",
        "lenguaje_claro": "La unidad con la que la DIAN expresa los topes de impuestos, retención en la fuente, beneficios tributarios y exención del 4x1000 en Colombia.",
        "ejemplo_cotidiano": "Tu cuenta bancaria marcada como exenta no paga 4x1000 en retiros de hasta 350 UVT mensuales.",
        "alias": ["UVT"],
    },
    "CUENTA_AFC": {
        "categoria": "Nómina e Impuestos",
        "termino_tecnico": "Cuenta AFC (Art. 126-4 Estatuto Tributario)",
        "como_no_decir": "Beneficio de renta exenta por ahorro con destinación específica habitacional.",
        "lenguaje_claro": "Cuenta de Ahorro para el Fomento de la Construcción: los aportes destinados a cuota inicial o cuotas hipotecarias reducen tu base de retención en la fuente hasta los topes legales en UVT.",
        "ejemplo_cotidiano": "Convierte parte de lo que pagarías en retención salarial en capital directo para comprar tu vivienda.",
        "alias": ["Cuenta AFC", "Cuentas AFC", "AFC"],
    },
    "GMF_4X1000": {
        "categoria": "Nómina e Impuestos",
        "termino_tecnico": "4x1000 (GMF — Gravamen a los Movimientos Financieros)",
        "como_no_decir": "Tributo indirecto de cuatro por mil sobre retiros y débitos bancarios.",
        "lenguaje_claro": "Impuesto financiero en el que por cada $1.000 COP retirados o transferidos desde una cuenta no exenta se descuentan $4 COP.",
        "ejemplo_cotidiano": "En Colombia tienes derecho a marcar una cuenta exenta de 4x1000 hasta por 350 UVT al mes.",
        "alias": ["4x1000", "GMF"],
    },
    # --- FAMILIA 4: DEUDAS Y PROTECCIÓN AL CONSUMIDOR ---
    "USURA": {
        "categoria": "Deudas y Leyes Protectoras",
        "termino_tecnico": "Tasa de Usura SFC",
        "como_no_decir": "Tope legal equivalente a 1.5 veces el Interés Bancario Corriente certificado.",
        "lenguaje_claro": "El interés máximo legal que puede cobrar un crédito o tarjeta en Colombia según certificación de la Superintendencia Financiera. Cobrar por encima es ilegal.",
        "ejemplo_cotidiano": "Un préstamo informal al 10% mensual supera varias veces la Tasa de Usura y destruye tu flujo de caja.",
        "alias": ["Tasa de Usura", "Usura"],
    },
    "AVALANCHA_NIEVE": {
        "categoria": "Deudas y Leyes Protectoras",
        "termino_tecnico": "Método Avalancha vs. Bola de Nieve",
        "como_no_decir": "Heurísticas de amortización acelerada con reasignación de flujo liberado (roll-over).",
        "lenguaje_claro": "Dos estrategias probadas para salir de deudas: 'Avalancha' prioriza la deuda con tasa más alta (ahorra más dinero en intereses) y 'Bola de Nieve' liquida primero el saldo más pequeño (libera cuotas rápido).",
        "ejemplo_cotidiano": "En ambas estrategias, al terminar de pagar una obligación sumas esa cuota liberada para acelerar la siguiente.",
        "alias": ["Avalancha", "Bola de Nieve"],
    },
    "LEY_1328": {
        "categoria": "Deudas y Leyes Protectoras",
        "termino_tecnico": "Abono Extra a Capital (Ley 1328 de 2009)",
        "como_no_decir": "Derecho del consumidor financiero al prepago parcial o total sin sanción.",
        "lenguaje_claro": "Derecho legal en Colombia a realizar pagos anticipados a capital en tus créditos en cualquier momento, sin penalidad, eligiendo entre reducir plazo o reducir cuota.",
        "ejemplo_cotidiano": "Abonar extra reduciendo plazo disminuye de forma directa millones de pesos en intereses futuros.",
        "alias": ["Ley 1328", "abono a capital", "abonos a capital"],
    },
    "FOGAFIN": {
        "categoria": "Deudas y Leyes Protectoras",
        "termino_tecnico": "Seguro de Depósitos Fogafín",
        "como_no_decir": "Garantía pública de depósitos en establecimientos adscritos.",
        "lenguaje_claro": "Seguro estatal gratuito y automático que protege tus cuentas de ahorro y CDTs hasta por $50.000.000 COP por persona en cada entidad inscrita.",
        "ejemplo_cotidiano": "Verifica siempre que el banco o entidad donde guardas tu fondo de emergencia cuente con respaldo Fogafín o vigilancia SFC.",
        "alias": ["Fogafín", "Fogafin"],
    },
    "HABEAS_DATA": {
        "categoria": "Deudas y Leyes Protectoras",
        "termino_tecnico": "Habeas Data (Ley 1581 de 2012 y Ley 1266 de 2008)",
        "como_no_decir": "Régimen estatutario de protección de datos personales y reporte crediticio.",
        "lenguaje_claro": "Derecho constitucional a conocer, actualizar y proteger tus datos personales y tu historial crediticio en centrales de riesgo (Datacrédito / TransUnion).",
        "ejemplo_cotidiano": "Tras pagar una obligación en mora, la permanencia máxima del reporte negativo es el doble del tiempo de mora (con tope de 4 años).",
        "alias": ["Habeas Data", "Ley 1581", "Ley 1266"],
    },
    # --- FAMILIA 5: ESTADÍSTICA, PROBABILIDAD Y ACTUARÍA ---
    "VALOR_ESPERADO": {
        "categoria": "Probabilidad y Futuro",
        "termino_tecnico": "Valor Esperado Matemático E[X]",
        "como_no_decir": "Esperanza matemática ponderada por distribución discreta de probabilidades.",
        "lenguaje_claro": "El resultado promedio real que obtendrías al repetir una apuesta o inversión miles de veces. En juegos de azar y loterías siempre es negativo para el jugador.",
        "ejemplo_cotidiano": "Destinar dinero de forma constante a inversión regulada construye patrimonio; los juegos de azar tienen pérdida matemática esperada.",
        "alias": ["Valor Esperado", "esperanza matemática"],
    },
    "MONTE_CARLO": {
        "categoria": "Probabilidad y Futuro",
        "termino_tecnico": "Simulación Actuarial de Monte Carlo",
        "como_no_decir": "Modelación estocástica multiescenario de solvencia de ciclo de vida.",
        "lenguaje_claro": "Una Prueba de Estrés Financiero que evalúa tu presupuesto familiar en 1.000 escenarios económicos posibles (incluyendo inflación alta o caída temporal de ingresos) para medir la solidez de tu plan.",
        "ejemplo_cotidiano": "Si tu flujo de caja resiste más de 850 escenarios de 1.000, cuentas con margen financiero sólido para asumir esa meta.",
        "alias": ["Monte Carlo", "actuarial", "actuariales"],
    },
    "SUITABILITY": {
        "categoria": "Probabilidad y Futuro",
        "termino_tecnico": "Test de Idoneidad SFC (Decreto 2555 de 2010)",
        "como_no_decir": "Evaluación estandarizada de perfil de cliente bajo el marco del Decreto 2555.",
        "lenguaje_claro": "Evaluación obligatoria que protege al inversionista identificando su horizonte de tiempo, tolerancia al riesgo y capacidad financiera antes de sugerir cualquier producto.",
        "ejemplo_cotidiano": "Permite clasificar objetivamente si tu perfil es Conservador, Moderado o Agresivo para que nunca asumas un riesgo que no toleres.",
        "alias": ["Suitability", "Test de Idoneidad", "Decreto 2555", "perfil de riesgo"],
    },
    "ETF": {
        "categoria": "Financiero e Inversión",
        "termino_tecnico": "ETF (Exchange Traded Fund o Fondo Bursátil)",
        "como_no_decir": "Vehículo indexado de inversión colectiva cotizado en rueda continua bursátil.",
        "lenguaje_claro": "Una canasta diversificada de cientos de acciones o bonos que se compra y vende en bolsa como si fuera una sola acción, con comisiones ultra bajas.",
        "ejemplo_cotidiano": "Comprar una fracción del ETF CSPX o VOO te hace dueño instantáneo de una pequeña parte de las 500 empresas más grandes de EE.UU. (S&P 500).",
        "alias": ["ETF", "ETFs"],
    },
    "MGC": {
        "categoria": "Financiero e Inversión",
        "termino_tecnico": "Mercado Global Colombiano (MGC de la BVC)",
        "como_no_decir": "Segmento de cotización de valores extranjeros listados en la Bolsa de Valores de Colombia.",
        "lenguaje_claro": "Plataforma de la Bolsa de Valores de Colombia que te permite comprar ETFs y acciones internacionales en pesos colombianos ($ COP) a través de comisionistas vigiladas.",
        "ejemplo_cotidiano": "Puedes invertir en el S&P 500 o en acciones globales desde comisionistas como Trii o tradicionales sin necesidad de transferir dólares al exterior.",
        "alias": ["Mercado Global Colombiano", "MGC"],
    },
    "DCA": {
        "categoria": "Financiero e Inversión",
        "termino_tecnico": "Estrategia DCA (Dollar Cost Averaging)",
        "como_no_decir": "Estrategia de periodicidad fija de acumulación de activos independientes del ciclo de mercado.",
        "lenguaje_claro": "Invertir un monto fijo todos los meses sin importar si el mercado sube o baja. Cuando los precios bajan compras más títulos y cuando suben ganas más valor.",
        "ejemplo_cotidiano": "Aportar $500.000 COP cada mes el día del pago te quita el estrés de intentar adivinar el mejor momento para comprar.",
        "alias": ["DCA", "Dollar Cost Averaging"],
    },
    "TES": {
        "categoria": "Financiero e Inversión",
        "termino_tecnico": "Bonos de Deuda Pública TES",
        "como_no_decir": "Títulos de deuda pública soberana emitidos por la Dirección del Tesoro Nacional.",
        "lenguaje_claro": "Préstamos directos que los inversionistas hacen a la Nación colombiana a cambio de una tasa fija o indexada a UVR, respaldados por el Estado.",
        "ejemplo_cotidiano": "Es el activo de menor riesgo crediticio en Colombia: mientras el Estado colombiano exista, los pagos de intereses y capital están asegurados.",
        "alias": ["TES", "Bonos TES"],
    },
    "PONZI": {
        "categoria": "Probabilidad y Futuro",
        "termino_tecnico": "Esquema Piramidal o Ponzi (Art. 316 C.P.)",
        "como_no_decir": "Estructura de financiamiento fraudulento por colapso geométrico de base poblacional.",
        "lenguaje_claro": "Fraude financiero donde no existe inversión real: las supuestas ganancias de los primeros se pagan con el dinero de las nuevas personas que ingresan hasta que colapsa matemáticamente.",
        "ejemplo_cotidiano": "Cualquier oferta que prometa '20% mensual garantizado' o te pida 'traer 3 referidos' es un delito de captación ilegal que matemáticamente se queda sin personas en pocos meses.",
        "alias": ["Ponzi", "pirámide", "esquema piramidal", "piramidales"],
    },
}


def explicar_termino_en_lenguaje_claro(clave_termino: str) -> Dict[str, Any]:
    """Busca un concepto por clave o por alias y devuelve su explicación financiera clara."""
    busqueda = clave_termino.strip().upper()
    if busqueda in GLOSARIO_LENGUAJE_CLARO_OED:
        return GLOSARIO_LENGUAJE_CLARO_OED[busqueda]
    for ficha in GLOSARIO_LENGUAJE_CLARO_OED.values():
        for alias in ficha.get("alias", []):
            if alias.strip().upper() == busqueda:
                return ficha
    return {
        "categoria": "Concepto General",
        "termino_tecnico": clave_termino,
        "como_no_decir": "Explicación en jerga técnica sin contexto práctico.",
        "lenguaje_claro": "En OED explicamos cada concepto mostrando su impacto directo en tu flujo de caja y en tu patrimonio.",
        "ejemplo_cotidiano": "Acompaña siempre el indicador con un ejemplo concreto en pesos colombianos ($ COP).",
        "alias": [clave_termino],
    }


def detectar_terminos_en_texto(texto: str) -> List[str]:
    """
    Escanea cualquier párrafo y devuelve la lista ordenada de claves del diccionario OED
    que aparecen mencionadas, para que ningún término quede sin explicación contextual.
    """
    encontrados: List[str] = []
    for clave, ficha in GLOSARIO_LENGUAJE_CLARO_OED.items():
        for alias in ficha.get("alias", []):
            patron = r"(?<![A-Za-zÁÉÍÓÚáéíóúñÑ0-9])" + re.escape(alias) + r"(?![A-Za-zÁÉÍÓÚáéíóúñÑ0-9])"
            if re.search(patron, texto, flags=re.IGNORECASE):
                encontrados.append(clave)
                break
    return encontrados


def enriquecer_texto_con_explicaciones(texto: str) -> str:
    """
    Convierte un texto plano en HTML seguro donde la primera aparición de cada término
    financiero, legal, tributario o estadístico queda subrayada con una burbuja interactiva
    del Diccionario Financiero OED al pasar el cursor o tocar en pantalla.
    """
    pares_alias: List[tuple[str, str]] = []
    for clave, ficha in GLOSARIO_LENGUAJE_CLARO_OED.items():
        for alias in ficha.get("alias", []):
            pares_alias.append((alias, clave))
    pares_alias.sort(key=lambda par: len(par[0]), reverse=True)

    marcadores: Dict[str, str] = {}
    claves_ya_marcadas: set[str] = set()
    texto_trabajo = texto

    for idx, (alias, clave) in enumerate(pares_alias):
        if clave in claves_ya_marcadas:
            continue
        patron = r"(?<![A-Za-zÁÉÍÓÚáéíóúñÑ0-9_])(" + re.escape(alias) + r")(?![A-Za-zÁÉÍÓÚáéíóúñÑ0-9_])"
        coincidencia = re.search(patron, texto_trabajo, flags=re.IGNORECASE)
        if coincidencia:
            claves_ya_marcadas.add(clave)
            token = f"__OEDTERM{idx}__"
            palabra_original = coincidencia.group(1)
            ficha = GLOSARIO_LENGUAJE_CLARO_OED[clave]
            tooltip = html.escape(f"💡 {ficha['termino_tecnico']}: {ficha['lenguaje_claro']}")
            marcadores[token] = (
                f'<span class="oed-term" tabindex="0" data-tip="{tooltip}">'
                f"{html.escape(palabra_original)}<sup class=\"oed-q\">?</sup></span>"
            )
            texto_trabajo = texto_trabajo[: coincidencia.start()] + token + texto_trabajo[coincidencia.end() :]

    texto_seguro = html.escape(texto_trabajo)
    for token, html_span in marcadores.items():
        texto_seguro = texto_seguro.replace(token, html_span)
    return texto_seguro


def formatear_cop_claro(monto_cop: float) -> str:
    """Formatea pesos colombianos con separador de miles legible (ej. '$6.500.000 COP')."""
    signo = "-" if monto_cop < 0 else ""
    texto = f"{abs(round(monto_cop)):,}".replace(",", ".")
    return f"{signo}${texto} COP"


# ==============================================================================
# 4. COMPONENTES REUTILIZABLES EN STREAMLIT (ASESOR FINANCIERO + BURBUJAS ?)
# ==============================================================================

_CSS_MEDICO_AMIGO_OED = """
<style>
.oed-header {
    background: linear-gradient(135deg, #0F294A 0%, #1D4ED8 100%);
    color: #FFFFFF; padding: 1.25rem 1.5rem; border-radius: 14px; margin-bottom: 1rem;
}
.oed-header h1 { color: #FFFFFF !important; font-size: 1.5rem !important; margin: 0 0 0.35rem 0 !important; }
.oed-header p { color: #E2E8F0 !important; font-size: 0.95rem !important; margin: 0 !important; line-height: 1.45; }
.oed-steps { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 0.85rem; }
.oed-step-pill {
    font-size: 0.77rem; padding: 4px 10px; border-radius: 999px;
    border: 1px solid #CBD5E1; background: #FFFFFF; color: #475569;
}
.oed-step-active { background: #EA580C; color: #FFFFFF; border-color: #EA580C; font-weight: 700; }
.oed-doc-card {
    border-radius: 12px; padding: 1rem 1.2rem; margin: 0.6rem 0; border-left: 6px solid;
    font-size: 0.95rem; line-height: 1.55;
}
.oed-doc-verde { background: #F0FDF4; border-color: #15803D; color: #14532D; }
.oed-doc-azul  { background: #EFF6FF; border-color: #1D4ED8; color: #1E3A8A; }
.oed-doc-ambar { background: #FFFBEB; border-color: #B45309; color: #78350F; }
.oed-doc-rojo  { background: #FEF2F2; border-color: #B91C1C; color: #7F1D1D; }
.oed-rx-box {
    background: #FFF7ED; border: 1px solid #FED7AA; border-left: 6px solid #EA580C;
    padding: 0.95rem 1.2rem; border-radius: 12px; margin: 0.65rem 0 1rem 0; color: #431407;
    font-size: 0.93rem; line-height: 1.5;
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
    min-width: 260px; max-width: 340px; background: #0F294A; color: #FFFFFF;
    padding: 9px 11px; border-radius: 9px; font-size: 0.8rem; font-weight: 400;
    line-height: 1.4; z-index: 9999; box-shadow: 0 8px 20px rgba(15, 41, 74, 0.28);
    white-space: normal;
}
</style>
"""


def aplicar_tema_visual_oed() -> None:
    """Inyecta en Streamlit el diseño institucional OED y las burbujas explicativas interactivas."""
    import streamlit as st

    st.markdown(_CSS_MEDICO_AMIGO_OED, unsafe_allow_html=True)


def render_encabezado_modulo_oed(paso_actual: int, subtitulo_personalizado: str | None = None) -> None:
    """Dibuja la barra de los 7 pasos de OED y la introducción del Asesor Financiero de Confianza."""
    import streamlit as st

    aplicar_tema_visual_oed()
    info = next((p for p in RUTA_CLINICA_FINANCIERA_OED if p["paso"] == paso_actual), RUTA_CLINICA_FINANCIERA_OED[0])
    saludo = subtitulo_personalizado or info["saludo_medico"]
    saludo_con_ayudas = enriquecer_texto_con_explicaciones(saludo)

    pills_html = "".join(
        f'<span class="oed-step-pill {"oed-step-active" if p["paso"] == paso_actual else ""}">'
        f'Paso {p["paso"]}: {p["icono"]} {p["titulo_ciudadano"]}</span>'
        for p in RUTA_CLINICA_FINANCIERA_OED
    )

    st.markdown(
        f"""
        <div class="oed-steps">{pills_html}</div>
        <div class="oed-header">
            <h1>{info['icono']} Paso {info['paso']} — {html.escape(info['titulo_ciudadano'])}</h1>
            <p>💼 <i>"{saludo_con_ayudas}"</i><br>
            <small>Responsable OED en esta etapa: <b>{html.escape(info['responsable'])}</b> · {html.escape(info['modulo_tecnico'])}</small></p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_semaforo_ciudadano_oed(
    nivel: str,
    titulo_claro: str,
    explicacion_humana: str,
    siguiente_paso_accionable: str | None = None,
) -> None:
    """
    Presenta el Diagnóstico Financiero con voz de Asesor Financiero de Confianza,
    auto-explicando términos financieros, legales o estadísticos mediante burbujas (`?`),
    seguido de '📌 Plan de Acción para este Mes'.
    """
    import streamlit as st

    aplicar_tema_visual_oed()
    norm = nivel.strip().lower()
    if norm in ("verde", "success"):
        clase, icono, prefijo = "oed-doc-verde", "✅", "Diagnóstico Financiero favorable:"
    elif norm in ("azul", "info"):
        clase, icono, prefijo = "oed-doc-azul", "ℹ️", "Análisis de tu Asesor Financiero:"
    elif norm in ("ambar", "amarillo", "warning"):
        clase, icono, prefijo = "oed-doc-ambar", "⚠️", "Revisión preventiva:"
    else:
        clase, icono, prefijo = "oed-doc-rojo", "🛑", "Riesgo alto — Te recomendamos esperar:"

    titulo_rico = enriquecer_texto_con_explicaciones(titulo_claro)
    explicacion_rica = enriquecer_texto_con_explicaciones(explicacion_humana)

    st.markdown(
        f"""
        <div class="oed-doc-card {clase}">
            <div><b>{icono} {prefijo} {titulo_rico}</b></div>
            <div style="margin-top:4px;">{explicacion_rica}</div>
            <div style="margin-top:6px; font-size:0.78rem; opacity:0.85;">
                💡 <i>Tip: Pasa el cursor sobre cualquier palabra subrayada con <b>?</b> para ver su explicación en sencillo.</i>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if siguiente_paso_accionable:
        accion_rica = enriquecer_texto_con_explicaciones(siguiente_paso_accionable)
        st.markdown(
            f"""
            <div class="oed-rx-box">
                <b>📌 Plan de Acción para este Mes:</b> {accion_rica}
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_glosario_interactivo_oed(claves_terminos: List[str] | None = None) -> None:
    """
    Renderiza el Diccionario Financiero OED (filtrable por categoría o enfocado en los términos del módulo)
    para que ningún concepto financiero, legal, laboral o estadístico quede sin explicación.
    """
    import streamlit as st

    with st.expander("📘 ¿Tienes dudas con algún concepto? Consulta aquí el Diccionario Financiero OED"):
        todas = list(GLOSARIO_LENGUAJE_CLARO_OED.keys())
        ver_todos = st.checkbox(
            "Ver las 5 familias completas de términos del proyecto (Finanzas, Vivienda, Nómina, Deudas y Probabilidad)",
            value=claves_terminos is None,
        )
        opciones = todas if (ver_todos or not claves_terminos) else [k for k in claves_terminos if k in GLOSARIO_LENGUAJE_CLARO_OED]
        if not opciones:
            opciones = todas

        seleccion = st.selectbox(
            "Selecciona el término que quieres consultar sin tecnicismos:",
            options=opciones,
            format_func=lambda k: f"[{GLOSARIO_LENGUAJE_CLARO_OED[k]['categoria']}] {GLOSARIO_LENGUAJE_CLARO_OED[k]['termino_tecnico']}",
        )
        ficha = explicar_termino_en_lenguaje_claro(seleccion)
        st.markdown(f"**💡 En palabras sencillas:** {ficha['lenguaje_claro']}")
        st.info(f"🇨🇴 **Ejemplo en pesos colombianos:** {ficha['ejemplo_cotidiano']}")


def aplicar_estilo_plotly_oed(fig: Any, titulo: str | None = None, altura: int = 420) -> Any:
    """Aplica la paleta y tipografía limpia del Manual de Marca OED a cualquier gráfica de Plotly."""
    ajustes: Dict[str, Any] = {
        "template": "plotly_white",
        "height": altura,
        "colorway": COLORES_GRAFICAS_OED,
        "font": {"family": "Segoe UI, system-ui, sans-serif", "color": "#0F294A", "size": 13},
        "legend": {"orientation": "h", "yanchor": "bottom", "y": 1.03, "xanchor": "left", "x": 0},
        "margin": {"l": 50, "r": 30, "t": 65, "b": 45},
    }
    if titulo:
        ajustes["title"] = {"text": titulo, "font": {"size": 16, "color": "#0F294A"}}
    fig.update_layout(**ajustes)
    return fig


# ==============================================================================
# 5. SHOWROOM INTERACTIVO EN NAVEGADOR (`py src/oed_design_system.py`)
# ==============================================================================


def _generar_html_manual_marca_interactivo() -> str:
    frase_demo = (
        "Revisando tus indicadores clave con claridad: tu crédito cumple la Ley 546 porque no supera el 30% "
        "de tus ingresos en SMMLV. Ahorrar tu cuota inicial en un encargo fiduciario usando tu Cuenta AFC "
        "reduce retención medida en UVT, evita el riesgo de inflación del IPC en UVR y mejora tu VPN y TIR "
        "con ahorros protegidos por Fogafín."
    )
    frase_enriquecida = enriquecer_texto_con_explicaciones(frase_demo)
    datos_js = json.dumps(
        {
            "paleta": PALETA_MARCA_OED,
            "ruta": RUTA_CLINICA_FINANCIERA_OED,
            "glosario": GLOSARIO_LENGUAJE_CLARO_OED,
        },
        ensure_ascii=False,
    )
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Manual de Marca: Asesor Financiero de Confianza — Equipo OED</title>
{_CSS_MEDICO_AMIGO_OED}
<style>
  * {{ box-sizing:border-box; font-family:'Segoe UI',system-ui,-apple-system,sans-serif; }}
  body {{ margin:0; background:#F4F7FB; color:#0F294A; padding:22px; }}
  .wrap {{ max-width:1180px; margin:0 auto; }}
  .tabs {{ display:flex; gap:8px; flex-wrap:wrap; margin-bottom:16px; }}
  .tab {{ border:1px solid #CBD5E1; background:#fff; color:#334155; padding:9px 16px; border-radius:999px; cursor:pointer; font-weight:600; font-size:13.5px; }}
  .tab.active {{ background:#EA580C; color:#fff; border-color:#EA580C; }}
  .panel {{ display:none; }}
  .panel.active {{ display:block; }}
  .grid3 {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:14px; }}
  .card {{ background:#fff; border:1px solid #DDE4EE; border-radius:13px; padding:16px; box-shadow:0 2px 6px rgba(15,41,74,0.04); }}
  .swatch {{ height:60px; border-radius:9px; margin-bottom:10px; display:flex; align-items:flex-end; padding:8px 10px; color:#fff; font-weight:700; font-size:12px; cursor:pointer; }}
  .pill {{ display:inline-block; padding:5px 11px; border-radius:999px; font-size:12px; border:1px solid #CBD5E1; margin:3px; cursor:pointer; background:#fff; }}
  .pill.sel {{ background:#1D4ED8; color:#fff; border-color:#1D4ED8; font-weight:700; }}
  pre {{ background:#0F294A; color:#F8FAFC; padding:14px; border-radius:10px; overflow-x:auto; font-size:12.5px; line-height:1.45; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="oed-header">
    <h1>💼 Manual de Marca: "Asesor Financiero de Confianza" — Equipo OED</h1>
    <p>Identidad unificada para <b>Camilo, Nidia, Nelson, Catalina, Jesi y Salin</b> con la regla de oro: <b>ninguna palabra financiera, legal o estadística se queda sin su explicación inmediata (?)</b>.</p>
  </div>

  <div class="tabs">
    <button class="tab active" onclick="verTab(0)">1. 💼 Voz de Asesor Financiero + Burbujas (?)</button>
    <button class="tab" onclick="verTab(1)">2. 📘 Diccionario Financiero (25+ Términos)</button>
    <button class="tab" onclick="verTab(2)">3. 🎨 Paleta Oficial OED</button>
    <button class="tab" onclick="verTab(3)">4. 👩‍💻 Plantilla por Integrante</button>
  </div>

  <div class="panel active" id="p0">
    <div class="card">
      <h3 style="margin-top:0;">Prueba en vivo las burbujas automáticas ("Cero Palabras Huérfanas")</h3>
      <p style="font-size:13.5px; color:#475569;">Pasa el cursor por encima de cualquier término con <b>?</b> — el sistema lo detecta automáticamente dentro del párrafo de cualquier integrante:</p>
      <div class="oed-doc-card oed-doc-verde">
        <b>✅ Diagnóstico Financiero favorable:</b><br>
        {frase_enriquecida}
      </div>
      <div class="oed-rx-box">
        <b>📌 Plan de Acción para este Mes:</b> Programa una transferencia automática el mismo día que recibes tu ingreso mensual para consolidar tu ahorro sin afectar tu flujo de caja.
      </div>
    </div>
  </div>

  <div class="panel" id="p1">
    <div class="card">
      <input id="buscador" type="text" placeholder="🔍 Escribe cualquier sigla o palabra (ej. UVR, IBC, Usura, Leasing, Monte Carlo, Fogafín)..."
             style="width:100%; padding:10px 12px; border:1px solid #CBD5E1; border-radius:9px; font-size:14px; margin-bottom:12px;" oninput="filtrarTerminos()">
      <div id="term_pills"></div>
      <div id="term_detail" style="margin-top:14px;"></div>
    </div>
  </div>

  <div class="panel" id="p2">
    <div class="grid3" id="swatches"></div>
  </div>

  <div class="panel" id="p3">
    <div class="card">
      <h3 style="margin-top:0;">Haz clic en cualquier integrante para ver su encabezado OED y copiar su código:</h3>
      <div id="code_pills" style="margin-bottom:12px;"></div>
      <div id="step_banner" style="margin-bottom:12px;"></div>
      <pre id="code_box"></pre>
    </div>
  </div>
</div>

<script>
const DATA = {datos_js};
function verTab(idx) {{
  document.querySelectorAll('.tab').forEach((t,i)=>t.classList.toggle('active', i===idx));
  document.querySelectorAll('.panel').forEach((p,i)=>p.classList.toggle('active', i===idx));
}}

document.getElementById('swatches').innerHTML = Object.values(DATA.paleta).map(c => `
  <div class="card">
    <div class="swatch" style="background:${{c.hex}}; color:${{c.hex==='#F4F7FB'?'#0F294A':'#fff'}}; border:1px solid #DDE4EE;"
         onclick="navigator.clipboard?.writeText('${{c.hex}}'); this.innerText='¡Copiado ${{c.hex}}!';">${{c.hex}}</div>
    <b>${{c.nombre}}</b>
    <p style="font-size:12.5px; color:#475569; margin:6px 0 0;">${{c.uso}}</p>
  </div>
`).join('');

function verTermino(k) {{
  document.querySelectorAll('#term_pills .pill').forEach(el => el.classList.toggle('sel', el.dataset.k===k));
  const f = DATA.glosario[k];
  document.getElementById('term_detail').innerHTML = `
    <div style="font-size:12px; color:#1D4ED8; font-weight:700;">FAMILIA: ${{f.categoria.toUpperCase()}}</div>
    <h3 style="margin:4px 0 10px;">📘 ${{f.termino_tecnico}}</h3>
    <div class="oed-doc-card oed-doc-rojo"><b>❌ Jerga técnica fría que evitamos:</b> "${{f.como_no_decir}}"</div>
    <div class="oed-doc-card oed-doc-verde"><b>✅ Cómo lo explica tu Asesor Financiero de Confianza:</b> ${{f.lenguaje_claro}}</div>
    <div class="oed-rx-box"><b>🇨🇴 Ejemplo cotidiano en pesos:</b> ${{f.ejemplo_cotidiano}}</div>
  `;
}}

function filtrarTerminos() {{
  const q = document.getElementById('buscador').value.trim().toLowerCase();
  const ks = Object.keys(DATA.glosario).filter(k => {{
    const f = DATA.glosario[k];
    return !q || f.termino_tecnico.toLowerCase().includes(q) || f.lenguaje_claro.toLowerCase().includes(q) || f.categoria.toLowerCase().includes(q);
  }});
  document.getElementById('term_pills').innerHTML = ks.map(k =>
    `<span class="pill" data-k="${{k}}" onclick="verTermino('${{k}}')">${{DATA.glosario[k].termino_tecnico}}</span>`
  ).join('');
  if (ks.length) verTermino(ks[0]);
}}
filtrarTerminos();

function verCodigo(num) {{
  document.querySelectorAll('#code_pills .pill').forEach(el => el.classList.toggle('sel', Number(el.dataset.n)===num));
  const s = DATA.ruta.find(x => x.paso===num);
  document.getElementById('step_banner').innerHTML = `
    <div class="oed-header" style="margin-bottom:0;">
      <h1>${{s.icono}} Paso ${{s.paso}} — ${{s.titulo_ciudadano}}</h1>
      <p>💼 <i>"${{s.saludo_medico}}"</i> · Responsable OED: <b>${{s.responsable}}</b></p>
    </div>`;
  document.getElementById('code_box').textContent =
`from src.oed_design_system import (
    render_encabezado_modulo_oed,
    render_semaforo_ciudadano_oed,
    render_glosario_interactivo_oed,
    aplicar_estilo_plotly_oed,
)

def render_modulo_paso_${{s.paso}}():
    # 1. Encabezado OED + Barra de progreso (Pasos 0 al 6)
    render_encabezado_modulo_oed(paso_actual=${{s.paso}})

    # 2. Diagnóstico Financiero: auto-detecta términos (EA, UVR, IBC, Usura...) y agrega burbuja (?)
    render_semaforo_ciudadano_oed(
        nivel="verde",
        titulo_claro="Tus indicadores clave muestran viabilidad financiera",
        explicacion_humana="${{s.saludo_medico}}",
        siguiente_paso_accionable="Acción concreta en $ COP para ejecutar este mismo mes.",
    )

    # 3. Diccionario Financiero de las 5 familias siempre disponible
    render_glosario_interactivo_oed()`;
}}
document.getElementById('code_pills').innerHTML = DATA.ruta.map(s =>
  `<span class="pill" data-n="${{s.paso}}" onclick="verCodigo(${{s.paso}})">Paso ${{s.paso}}: ${{s.icono}} ${{s.responsable}}</span>`
).join('');
verCodigo(5);
</script>
</body>
</html>"""


def iniciar_manual_marca_web_local(puerto: int = 8505, abrir_navegador: bool = True) -> None:
    """Abre el Manual de Marca 'Asesor Financiero de Confianza' en `http://127.0.0.1:8505`."""
    cuerpo = _generar_html_manual_marca_interactivo().encode("utf-8")

    class BrandHandler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
            return

        def do_GET(self) -> None:  # noqa: N802
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(cuerpo)))
            self.end_headers()
            self.wfile.write(cuerpo)

    url = f"http://127.0.0.1:{puerto}"
    servidor = HTTPServer(("127.0.0.1", puerto), BrandHandler)
    print("=" * 72)
    print(f"MANUAL DE MARCA 'ASESOR FINANCIERO DE CONFIANZA' ACTIVO EN: {url}")
    print("Presiona Ctrl + C en la terminal cuando quieras cerrarlo.")
    print("=" * 72)
    if abrir_navegador:
        webbrowser.open(url)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nManual de marca detenido.")
    finally:
        servidor.server_close()


def verificar_sistema_diseno_oed() -> bool:
    """Autoprueba rápida de la plantilla y del diccionario sin tocar ningún otro archivo del proyecto."""
    assert len(RUTA_CLINICA_FINANCIERA_OED) == 7
    assert len(GLOSARIO_LENGUAJE_CLARO_OED) >= 24
    muestra = "Revisemos tu IBC, UVT, Cuenta AFC, Ley 546, UVR, Tasa de Usura y Monte Carlo al 10% EA."
    detectados = detectar_terminos_en_texto(muestra)
    assert {"IBC", "UVT", "CUENTA_AFC", "LEY_546", "UVR", "USURA", "MONTE_CARLO", "EA"}.issubset(set(detectados))
    html_seguro = enriquecer_texto_con_explicaciones(muestra)
    assert 'class="oed-term"' in html_seguro
    assert len(_generar_html_manual_marca_interactivo()) > 1000
    return True


if __name__ == "__main__":
    if "--check" in sys.argv:
        verificar_sistema_diseno_oed()
        print("OK: Plantilla y Manual de Marca 'Asesor Financiero de Confianza' verificados correctamente.")
    else:
        iniciar_manual_marca_web_local()
