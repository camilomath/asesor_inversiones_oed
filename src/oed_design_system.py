"""
SISTEMA DE DISEÑO, MANUAL DE MARCA Y VOZ DE "MÉDICO FINANCIERO AMIGO" — EQUIPO OED COLOMBIA.

Filosofía central ("Cero Palabras Huérfanas"):
1. Tono de Médico Financiero de Cabecera: cercano, cálido, empático y sin regaños.
   - Signos vitales -> Diagnóstico tranquilo -> Receta práctica del mes.
2. Ningún término financiero, legal, tributario, laboral o estadístico queda sin explicación:
   - `enriquecer_texto_con_explicaciones(texto)` detecta automáticamente siglas y tecnicismos dentro
     de cualquier párrafo y les incrusta una burbuja explicativa interactiva al pasar el mouse o tocar.
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
# 1. PALETA OFICIAL DEL CONSULTORIO FINANCIERO AMIGO OED
# ==============================================================================

PALETA_MARCA_OED: Dict[str, Dict[str, str]] = {
    "azul_confianza": {
        "nombre": "Azul Bata Médica (Confianza OED)",
        "hex": "#0F294A",
        "uso": "Encabezados del consultorio, títulos principales y serenidad visual.",
    },
    "azul_impulso": {
        "nombre": "Azul Cuidado Activo",
        "hex": "#1D4ED8",
        "uso": "Botones principales, burbujas de explicación (?) y curva base en gráficas.",
    },
    "naranja_calidez": {
        "nombre": "Naranja Receta Positiva",
        "hex": "#EA580C",
        "uso": "Paso activo de la consulta y tarjeta de 'Tu Receta Práctica del Mes'.",
    },
    "verde_meta": {
        "nombre": "Verde Signos Vitales Sanos",
        "hex": "#15803D",
        "uso": "Diagnóstico saludable: tus números cumplen la ley y cuidan tu tranquilidad.",
    },
    "ambar_ajuste": {
        "nombre": "Ámbar Chequeo Preventivo",
        "hex": "#B45309",
        "uso": "Prevención amable: funciona hoy, pero vigilemos un síntoma (ej. inflación).",
    },
    "rojo_protector": {
        "nombre": "Rojo Cuidado Intensivo (Sin Regaños)",
        "hex": "#B91C1C",
        "uso": "Pausa protectora para evitar sobreendeudamiento o cobros ilegales.",
    },
    "fondo_claro": {
        "nombre": "Blanco Consultorio Cálido",
        "hex": "#F4F7FB",
        "uso": "Fondo limpio y descansado para leer sin estrés financiero.",
    },
}

COLORES_GRAFICAS_OED: List[str] = [
    "#1D4ED8",  # Azul Cuidado Activo
    "#EA580C",  # Naranja Receta Positiva
    "#15803D",  # Verde Signos Vitales Sanos
    "#7C3AED",  # Violeta Comparativo (FIC / Escenario alterno)
    "#DC2626",  # Rojo Síntoma a Vigilar (Fugas / Inflación UVR / Usura)
    "#475569",  # Gris Referencia Legal (Topes de ley)
]


# ==============================================================================
# 2. LOS 7 PASOS DE LA CONSULTA CON TU MÉDICO FINANCIERO AMIGO (PASOS 0 A 6)
# ==============================================================================

RUTA_CLINICA_FINANCIERA_OED: List[Dict[str, Any]] = [
    {
        "paso": 0,
        "icono": "🩺",
        "titulo_ciudadano": "Bienvenida al Consultorio y Confidencialidad",
        "modulo_tecnico": "Habeas Data Local y Reglas Base",
        "responsable": "Nelson + Camilo",
        "archivo": "src/data_governance.py · src/finance.py",
        "saludo_medico": "Igual que en una historia clínica médica, tus datos son privados, se quedan cifrados en tu equipo y nadie más los ve.",
    },
    {
        "paso": 1,
        "icono": "🫀",
        "titulo_ciudadano": "Pulso Emocional ante el Riesgo",
        "modulo_tecnico": "Módulo 6: Educación Financiera y Probabilidad",
        "responsable": "Salin Avellaneda",
        "archivo": "src/mod6_educacion_financiera.py",
        "saludo_medico": "Antes de recetarte cualquier inversión, miremos qué tanta variación aguanta tu corazón durmiendo tranquilo.",
    },
    {
        "paso": 2,
        "icono": "🩻",
        "titulo_ciudadano": "Radiografía de tu Sueldo y Pequeñas Fugas",
        "modulo_tecnico": "Módulo 1: Presupuesto y Flujo de Caja",
        "responsable": "Nidia Velásquez",
        "archivo": "src/mod1_presupuesto.py",
        "saludo_medico": "Revisemos con lupa cuánto te llega libre después de descuentos de ley y por dónde se están escapando pesitos sin darte cuenta.",
    },
    {
        "paso": 3,
        "icono": "🩹",
        "titulo_ciudadano": "Alivio de Deudas que te Quitan Oxígeno",
        "modulo_tecnico": "Módulo 3: Optimización de Deudas",
        "responsable": "Catalina Moreno",
        "archivo": "src/mod3_gestion_deudas.py",
        "saludo_medico": "Si tienes créditos caros, primero bajemos esa fiebre pagando menos intereses y liberando flujo mensual para ti.",
    },
    {
        "paso": 4,
        "icono": "🌱",
        "titulo_ciudadano": "Vitaminas para Multiplicar tu Sueldo",
        "modulo_tecnico": "Módulo 2: Micro-Inversiones Salariales",
        "responsable": "Camilo Matson",
        "archivo": "src/mod2_inversiones_salario.py",
        "saludo_medico": "Con tus cuentas en orden, pongamos tus ahorros mensuales a crecer por encima del costo de vida desde montos pequeños.",
    },
    {
        "paso": 5,
        "icono": "🏡",
        "titulo_ciudadano": "Chequeo para Comprar Casa sin Ahogarte",
        "modulo_tecnico": "Módulo 4: Inversión Patrimonial en Finca Raíz",
        "responsable": "Jesi",
        "archivo": "src/mod4_finca_raiz.py",
        "saludo_medico": "Revisemos con calma si la cuota de esa vivienda cuida la tranquilidad de tu hogar y si te conviene más Pesos o UVR.",
    },
    {
        "paso": 6,
        "icono": "🛡️",
        "titulo_ciudadano": "Prueba de Esfuerzo para tus Grandes Planes",
        "modulo_tecnico": "Módulo 5: Viabilidad Actuarial de Decisiones de Vida",
        "responsable": "Nelson",
        "archivo": "src/mod5_decisiones_vida.py",
        "saludo_medico": "Hagamos una prueba de esfuerzo con 1.000 escenarios futuros para que casarte, tener hijos o estudiar te tome bien preparado.",
    },
]


# ==============================================================================
# 3. ENCICLOPEDIA DEL MÉDICO AMIGO: TODOS LOS TÉRMINOS EXPLICADOS FÁCIL
#    (Financieros · Leyes Colombianas · Nómina e Impuestos · Vivienda · Estadística)
# ==============================================================================

GLOSARIO_LENGUAJE_CLARO_OED: Dict[str, Dict[str, Any]] = {
    # --- FAMILIA 1: CONCEPTOS FINANCIEROS E INVERSIÓN ---
    "EA": {
        "categoria": "Financiero e Inversión",
        "termino_tecnico": "Tasa Efectiva Anual (EA)",
        "como_no_decir": "Tasa compuesta anualizada bajo convención de capitalización SFC.",
        "lenguaje_claro": "Piénsalo como la velocidad real a la que crece un ahorro (o una deuda) al cumplir 12 meses completos. En Colombia jamás se divide por 12.",
        "ejemplo_cotidiano": "$1.000.000 guardados al 10% EA se convierten en $1.100.000 al cabo de un año antes de impuestos.",
        "alias": ["EA", "Efectivo Anual", "Efectiva Anual"],
    },
    "EM": {
        "categoria": "Financiero e Inversión",
        "termino_tecnico": "Tasa Efectiva Mensual (EM)",
        "como_no_decir": "Raíz duodécima del factor de capitalización efectivo anual menos uno.",
        "lenguaje_claro": "Es el pedacito real de interés que te cobran o te pagan en un solo mes, calculado con interés sobre interés.",
        "ejemplo_cotidiano": "Un 12% EA equivale aproximadamente a 0,95% EM cada mes (no a 1%).",
        "alias": ["EM", "Efectiva Mensual", "Efectivo Mensual"],
    },
    "IPC": {
        "categoria": "Financiero e Inversión",
        "termino_tecnico": "Inflación / IPC DANE",
        "como_no_decir": "Variación porcentual interanual del Índice de Precios al Consumidor.",
        "lenguaje_claro": "Qué tanto subió el costo del mercado, el arriendo y la vida en Colombia durante el año según el DANE.",
        "ejemplo_cotidiano": "Si el IPC es 5,2% y tu plata guardada debajo del colchón gana 0%, perdiste 5,2% de poder de compra.",
        "alias": ["IPC", "IPC DANE", "inflación"],
    },
    "INTERES_COMPUESTO": {
        "categoria": "Financiero e Inversión",
        "termino_tecnico": "Interés Compuesto",
        "como_no_decir": "Capitalización exponencial por reinversión periódica de rendimientos.",
        "lenguaje_claro": "El efecto 'bola de nieve buena': los intereses que ganas este mes se quedan adentro y empiezan a ganar sus propios intereses el mes siguiente.",
        "ejemplo_cotidiano": "Ahorrar poquito pero constante durante 10 años termina sumando más por ganancias acumuladas que por tu propio bolsillo.",
        "alias": ["interés compuesto", "interes compuesto"],
    },
    "CDT": {
        "categoria": "Financiero e Inversión",
        "termino_tecnico": "CDT (Certificado de Depósito a Término)",
        "como_no_decir": "Título valor de renta fija a plazo emitido por establecimiento de crédito.",
        "lenguaje_claro": "Un pacto tranquilo con un banco vigilado: le dejas tu dinero quieto por unos meses (ej. 90 o 360 días) a cambio de una ganancia fija asegurada desde el día uno.",
        "ejemplo_cotidiano": "Ideal cuando sabes que no vas a necesitar esa plata antes de la fecha pactada.",
        "alias": ["CDT", "CDTs"],
    },
    "FIC": {
        "categoria": "Financiero e Inversión",
        "termino_tecnico": "FIC (Fondo de Inversión Colectiva)",
        "como_no_decir": "Vehículo fiduciario colectivo administrado por sociedad vigilada SFC.",
        "lenguaje_claro": "Una 'vaca' gigante y legal vigilada por el Estado donde expertos invierten el dinero de miles de personas juntas desde montos bajitos ($20.000 COP).",
        "ejemplo_cotidiano": "Te permite invertir como los grandes capitales aunque empieces con una parte pequeña de tu sueldo.",
        "alias": ["FIC", "FICs", "Fondo de Inversión Colectiva"],
    },
    "VPN_TIR": {
        "categoria": "Financiero e Inversión",
        "termino_tecnico": "VPN y TIR",
        "como_no_decir": "Valor Presente Neto descontado al COK y Tasa Interna de Retorno.",
        "lenguaje_claro": "Son los dos exámenes médicos de cualquier negocio: la TIR te dice qué porcentaje anual rinde, y el VPN te dice cuántos pesos ganas (o pierdes) frente a dejar esa plata tranquila en un fondo seguro.",
        "ejemplo_cotidiano": "Si el VPN es mayor a $0, el negocio vale el esfuerzo; si es menor a $0, ganas más sin complicarte en un CDT o FIC.",
        "alias": ["VPN", "TIR", "COK", "costo de oportunidad"],
    },
    # --- FAMILIA 2: VIVIENDA Y FINCA RAÍZ ---
    "VIS_VIP": {
        "categoria": "Vivienda y Finca Raíz",
        "termino_tecnico": "Vivienda VIP, VIS y No VIS",
        "como_no_decir": "Segmentación regulatoria habitacional según topes en salarios mínimos CONPES.",
        "lenguaje_claro": "Son las categorías de precio de vivienda en Colombia medidas en salarios mínimos: VIP (hasta 90 SMMLV), VIS (hasta 135 o 150 SMMLV, con acceso a subsidios) y No VIS (por encima de 150 SMMLV).",
        "ejemplo_cotidiano": "Si el apartamento es VIS y ganas hasta 4 salarios mínimos, tu Caja de Compensación puede darte subsidio para la cuota inicial.",
        "alias": ["VIS", "VIP", "No VIS"],
    },
    "UVR": {
        "categoria": "Vivienda y Finca Raíz",
        "termino_tecnico": "UVR (Unidad de Valor Real)",
        "como_no_decir": "Unidad de cuenta hipotecaria indexada al IPC certificada por el Banco de la República.",
        "lenguaje_claro": "Una modalidad de crédito de vivienda donde la deuda y las cuotas se mueven al ritmo de la inflación. Arranca con cuota más suave que en pesos, pero sube si sube el costo de vida.",
        "ejemplo_cotidiano": "Con inflación alta, durante los primeros años puedes sentir que pagas cumplidamente y aun así el saldo medido en pesos sube.",
        "alias": ["UVR"],
    },
    "LEY_546": {
        "categoria": "Vivienda y Finca Raíz",
        "termino_tecnico": "Ley 546 de 1999 (Regla del 30%)",
        "como_no_decir": "Límite legal de relación primera cuota hipotecaria sobre ingreso familiar comprobado.",
        "lenguaje_claro": "Nuestro cinturón de seguridad en vivienda: por ley colombiana, la primera cuota del crédito de tu casa (con seguros incluidos) jamás puede superar el 30% de los ingresos del hogar.",
        "ejemplo_cotidiano": "Si en casa entran $8.000.000 netos, la primera cuota no puede pasar de $2.400.000.",
        "alias": ["Ley 546", "Regla del 30%"],
    },
    "ENCARGO_FIDUCIARIO": {
        "categoria": "Vivienda y Finca Raíz",
        "termino_tecnico": "Encargo Fiduciario (Compra sobre Planos)",
        "como_no_decir": "Patrimonio autónomo de preventa inmobiliaria administrado por fiduciaria.",
        "lenguaje_claro": "Una cuenta custodia vigilada donde vas pagando mes a mes la cuota inicial mientras construyen el edificio: la constructora no toca tu plata hasta cumplir las metas del proyecto.",
        "ejemplo_cotidiano": "Te da entre 18 y 36 meses para reunir la cuota inicial sumando sueldo, primas y cesantías sin endeudarte antes de tiempo.",
        "alias": ["encargo fiduciario", "fiducia", "sobre planos"],
    },
    "LEASING": {
        "categoria": "Vivienda y Finca Raíz",
        "termino_tecnico": "Leasing Habitacional",
        "como_no_decir": "Contrato de arrendamiento financiero inmobiliario con opción de adquisición.",
        "lenguaje_claro": "Una forma de financiar vivienda donde el banco figura como dueño mientras pagas un 'canon' mensual y, al final del plazo, pasas la escritura a tu nombre pagando una opción pactada.",
        "ejemplo_cotidiano": "Suele pedir menos cuota inicial (15%–20%) y no te exige desembolsar gastos de escrituración el primer día.",
        "alias": ["Leasing Habitacional", "Leasing"],
    },
    "LEY_820": {
        "categoria": "Vivienda y Finca Raíz",
        "termino_tecnico": "Ley 820 de 2003 (Arrendamiento en Colombia)",
        "como_no_decir": "Tope normativo del canon mensual equivalente al 1% del valor comercial.",
        "lenguaje_claro": "La ley de arriendos de vivienda en Colombia: dice que el arriendo mensual nunca puede superar el 1% del valor comercial del inmueble y cada año sube máximo el IPC.",
        "ejemplo_cotidiano": "Por un apartamento de $200 millones, el arriendo legal máximo es $2.000.000 mensuales (en mercado suele rondar 0,55%–0,75%).",
        "alias": ["Ley 820"],
    },
    "CAP_RATE": {
        "categoria": "Vivienda y Finca Raíz",
        "termino_tecnico": "Cap Rate Neto y Cash-on-Cash",
        "como_no_decir": "Ingreso Operativo Neto (NOI) sobre valor del activo y retorno efectivo sobre equity.",
        "lenguaje_claro": "El Cap Rate Neto mide qué porcentaje libre al año te deja el arriendo (quitando predial, administración, vacancia y arreglos). El Cash-on-Cash mide cuánto te queda en caja frente a la plata que sacaste de tu bolsillo.",
        "ejemplo_cotidiano": "Te evita la ilusión de mirar solo el arriendo bruto olvidando los gastos reales del inmueble.",
        "alias": ["Cap Rate", "NOI", "Cash-on-Cash"],
    },
    # --- FAMILIA 3: NÓMINA, TRABAJO E IMPUESTOS ---
    "SMMLV": {
        "categoria": "Nómina e Impuestos",
        "termino_tecnico": "SMMLV (Salario Mínimo Mensual Legal Vigente)",
        "como_no_decir": "Remuneración mínima vital indexada por decreto anual en Colombia.",
        "lenguaje_claro": "El salario mínimo oficial del año en Colombia. Además de sueldos, sirve como regla para medir precios de vivienda VIS y subsidios.",
        "ejemplo_cotidiano": "Cuando decimos que una casa vale 140 SMMLV, multiplicamos 140 por el salario mínimo vigente.",
        "alias": ["SMMLV", "salarios mínimos"],
    },
    "IBC": {
        "categoria": "Nómina e Impuestos",
        "termino_tecnico": "IBC (Ingreso Base de Cotización)",
        "como_no_decir": "Base salarial o proporción del 40% de honorarios para liquidación PILA.",
        "lenguaje_claro": "La parte de tus ingresos sobre la cual se calculan tus aportes a Salud, Pensión y ARL. Si eres independiente por prestación de servicios, es el 40% de tus honorarios.",
        "ejemplo_cotidiano": "Si cobras $5.000.000 por cuenta de cobro, cotizas seguridad social sobre $2.000.000 (el 40%).",
        "alias": ["IBC"],
    },
    "UVT": {
        "categoria": "Nómina e Impuestos",
        "termino_tecnico": "UVT (Unidad de Valor Tributario)",
        "como_no_decir": "Unidad de medida tributaria reajustada anualmente por la DIAN.",
        "lenguaje_claro": "La moneda interna con la que la DIAN calcula a partir de qué monto pagas retención en la fuente o 4x1000.",
        "ejemplo_cotidiano": "Tu cuenta principal marcada está libre de 4x1000 hasta 350 UVT al mes.",
        "alias": ["UVT"],
    },
    "CUENTA_AFC": {
        "categoria": "Nómina e Impuestos",
        "termino_tecnico": "Cuenta AFC (Art. 126-4 Estatuto Tributario)",
        "como_no_decir": "Beneficio de renta exenta por ahorro con destinación específica habitacional.",
        "lenguaje_claro": "Una cuenta de ahorro para vivienda con premio tributario: lo que ahorras allí reduce la base sobre la que te descuentan retención en la fuente de tu salario.",
        "ejemplo_cotidiano": "Transformas plata que se iba en impuestos en ladrillos propios para tu cuota inicial o tus cuotas del crédito.",
        "alias": ["Cuenta AFC", "Cuentas AFC", "AFC"],
    },
    "GMF_4X1000": {
        "categoria": "Nómina e Impuestos",
        "termino_tecnico": "4x1000 (GMF — Gravamen a los Movimientos Financieros)",
        "como_no_decir": "Tributo indirecto de cuatro por mil sobre retiros y débitos bancarios.",
        "lenguaje_claro": "El impuesto donde por cada $1.000 que sacas o transfieres de una cuenta no exenta te descuentan $4 pesos.",
        "ejemplo_cotidiano": "En Colombia tienes derecho a marcar una cuenta bancaria exenta de 4x1000 hasta por 350 UVT mensuales.",
        "alias": ["4x1000", "GMF"],
    },
    # --- FAMILIA 4: DEUDAS Y PROTECCIÓN AL CONSUMIDOR ---
    "USURA": {
        "categoria": "Deudas y Leyes Protectoras",
        "termino_tecnico": "Tasa de Usura SFC",
        "como_no_decir": "Tope legal equivalente a 1.5 veces el Interés Bancario Corriente certificado.",
        "lenguaje_claro": "El límite máximo de intereses permitido por la ley en Colombia. Ninguna tarjeta ni prestamista puede cobrarte por encima de esa raya.",
        "ejemplo_cotidiano": "Si alguien te presta 'gota a gota' al 10% mensual, supera varias veces la usura y está cometiendo un delito.",
        "alias": ["Tasa de Usura", "Usura"],
    },
    "AVALANCHA_NIEVE": {
        "categoria": "Deudas y Leyes Protectoras",
        "termino_tecnico": "Método Avalancha vs. Bola de Nieve",
        "como_no_decir": "Heurísticas de amortización acelerada con reasignación de flujo liberado (roll-over).",
        "lenguaje_claro": "Dos recetas médicas para salir de deudas: 'Avalancha' ataca primero la deuda con tasa más cara (te ahorra más dinero); 'Bola de Nieve' liquida primero la deuda más chiquita (te da alivio emocional rápido).",
        "ejemplo_cotidiano": "En ambas recetas, apenas matas una deuda, usas esa cuota liberada para acelerar la siguiente.",
        "alias": ["Avalancha", "Bola de Nieve"],
    },
    "LEY_1328": {
        "categoria": "Deudas y Leyes Protectoras",
        "termino_tecnico": "Abono Extra a Capital (Ley 1328 de 2009)",
        "como_no_decir": "Derecho del consumidor financiero al prepago parcial o total sin sanción.",
        "lenguaje_claro": "Tu derecho legal en Colombia a abonar plata extra directo al capital de tus créditos cuando quieras, sin multas, eligiendo si bajas el tiempo de deuda o bajas el valor de la cuota.",
        "ejemplo_cotidiano": "Reducir plazo es el atajo que más millones de intereses te ahorra.",
        "alias": ["Ley 1328", "abono a capital", "abonos a capital"],
    },
    "FOGAFIN": {
        "categoria": "Deudas y Leyes Protectoras",
        "termino_tecnico": "Seguro de Depósitos Fogafín",
        "como_no_decir": "Garantía pública de depósitos en establecimientos adscritos.",
        "lenguaje_claro": "Un seguro automático y gratuito del Estado que responde por tus ahorros bancarios y CDTs hasta por $50.000.000 COP en cada banco inscrito.",
        "ejemplo_cotidiano": "Siempre verifica que la entidad donde ahorras tenga el sello 'Protegido por Fogafín' o sea vigilada por la SFC.",
        "alias": ["Fogafín", "Fogafin"],
    },
    "HABEAS_DATA": {
        "categoria": "Deudas y Leyes Protectoras",
        "termino_tecnico": "Habeas Data (Ley 1581 de 2012 y Ley 1266 de 2008)",
        "como_no_decir": "Régimen estatutario de protección de datos personales y reporte crediticio.",
        "lenguaje_claro": "Tu derecho dueño sobre tu información personal y tu historial en centrales de riesgo (Datacrédito / TransUnion): nadie puede usar tus datos sin tu permiso y los reportes negativos tras pagar caducan por ley.",
        "ejemplo_cotidiano": "Después de ponerte al día en una mora, el reporte negativo dura máximo el doble del tiempo de mora (tope 4 años).",
        "alias": ["Habeas Data", "Ley 1581", "Ley 1266"],
    },
    # --- FAMILIA 5: ESTADÍSTICA, PROBABILIDAD Y ACTUARÍA ---
    "VALOR_ESPERADO": {
        "categoria": "Probabilidad y Futuro",
        "termino_tecnico": "Valor Esperado Matemático E[X]",
        "como_no_decir": "Esperanza matemática ponderada por distribución discreta de probabilidades.",
        "lenguaje_claro": "El promedio real que ganarías o perderías si repitieras una apuesta o inversión miles de veces. En loterías, rifas y casinos siempre es negativo para tu bolsillo.",
        "ejemplo_cotidiano": "Jugar por diversión ocasional está bien con presupuesto pequeño, pero nunca como plan para salir de deudas.",
        "alias": ["Valor Esperado", "esperanza matemática"],
    },
    "MONTE_CARLO": {
        "categoria": "Probabilidad y Futuro",
        "termino_tecnico": "Simulación Actuarial de Monte Carlo",
        "como_no_decir": "Modelación estocástica multiescenario de solvencia de ciclo de vida.",
        "lenguaje_claro": "Una 'prueba de esfuerzo' igual a la que te hace el cardiólogo en banda caminadora: probamos las finanzas de tu familia en 1.000 futuros posibles (incluyendo inflación alta o meses sin trabajo) para ver qué tan firme resistes.",
        "ejemplo_cotidiano": "Si superas más de 850 escenarios de 1.000, tu corazón financiero está listo para ese gran paso.",
        "alias": ["Monte Carlo", "actuarial", "actuariales"],
    },
}


def explicar_termino_en_lenguaje_claro(clave_termino: str) -> Dict[str, Any]:
    """Busca un concepto por clave o por alias y devuelve su explicación estilo Médico Amigo."""
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
        "como_no_decir": "Explicación fría en jerga técnica.",
        "lenguaje_claro": "En nuestro consultorio explicamos primero qué efecto real tiene en tu tranquilidad y en tu bolsillo mensual.",
        "ejemplo_cotidiano": "Acompaña siempre el dato con un ejemplo aterrizado en pesos colombianos ($ COP).",
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
    del Médico Financiero Amigo al pasar el cursor o tocar en pantalla.
    """
    # Ordenamos alias del más largo al más corto para no partir frases compuestas (ej. 'Ley 546' antes que 'EA')
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
            tooltip = html.escape(f"🩺 {ficha['termino_tecnico']}: {ficha['lenguaje_claro']}")
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
# 4. COMPONENTES REUTILIZABLES EN STREAMLIT (VOZ DE MÉDICO AMIGO + BURBUJAS)
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
    """Inyecta en Streamlit el diseño del Consultorio Financiero Amigo y las burbujas explicativas."""
    import streamlit as st

    st.markdown(_CSS_MEDICO_AMIGO_OED, unsafe_allow_html=True)


def render_encabezado_modulo_oed(paso_actual: int, subtitulo_personalizado: str | None = None) -> None:
    """Dibuja la barra de los 7 pasos de la consulta y el saludo cálido del especialista OED."""
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
            <p>🩺 <i>"{saludo_con_ayudas}"</i><br>
            <small>Tu Médico Financiero en esta etapa: <b>{html.escape(info['responsable'])}</b> · {html.escape(info['modulo_tecnico'])}</small></p>
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
    Presenta el diagnóstico con voz de Médico Amigo, auto-explicando cualquier término
    financiero, legal o estadístico dentro del texto mediante burbujas interactivas (`?`),
    seguido de 'Tu Receta Práctica del Mes'.
    """
    import streamlit as st

    aplicar_tema_visual_oed()
    norm = nivel.strip().lower()
    if norm in ("verde", "success"):
        clase, icono, prefijo = "oed-doc-verde", "🩺💚", "Signos vitales saludables:"
    elif norm in ("azul", "info"):
        clase, icono, prefijo = "oed-doc-azul", "🩺💙", "Lectura tranquila de tu médico financiero:"
    elif norm in ("ambar", "amarillo", "warning"):
        clase, icono, prefijo = "oed-doc-ambar", "🩺🧡", "Chequeo preventivo a tiempo:"
    else:
        clase, icono, prefijo = "oed-doc-rojo", "🩺❤️‍🩹", "Pausa protectora para cuidar tu tranquilidad:"

    titulo_rico = enriquecer_texto_con_explicaciones(titulo_claro)
    explicacion_rica = enriquecer_texto_con_explicaciones(explicacion_humana)

    st.markdown(
        f"""
        <div class="oed-doc-card {clase}">
            <div><b>{icono} {prefijo} {titulo_rico}</b></div>
            <div style="margin-top:4px;">{explicacion_rica}</div>
            <div style="margin-top:6px; font-size:0.78rem; opacity:0.85;">
                💡 <i>Tip: Pasa el cursor sobre cualquier palabra subrayada con <b>?</b> para ver qué significa en sencillo.</i>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if siguiente_paso_accionable:
        receta_rica = enriquecer_texto_con_explicaciones(siguiente_paso_accionable)
        st.markdown(
            f"""
            <div class="oed-rx-box">
                <b>💊 Tu Receta Práctica para este Mes:</b> {receta_rica}
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_glosario_interactivo_oed(claves_terminos: List[str] | None = None) -> None:
    """
    Renderiza el Consultorio de Términos Claros (filtrable por categoría o enfocado en los términos del módulo)
    para que ningún término financiero, legal, laboral o estadístico quede sin explicación.
    """
    import streamlit as st

    with st.expander("🩺 ¿Alguna palabra te sonó a chino? Pregúntale aquí al Diccionario del Médico Amigo"):
        todas = list(GLOSARIO_LENGUAJE_CLARO_OED.keys())
        ver_todos = st.checkbox(
            "Ver las 5 familias completas de términos del proyecto (Finanzas, Vivienda, Nómina, Deudas y Probabilidad)",
            value=claves_terminos is None,
        )
        opciones = todas if (ver_todos or not claves_terminos) else [k for k in claves_terminos if k in GLOSARIO_LENGUAJE_CLARO_OED]
        if not opciones:
            opciones = todas

        seleccion = st.selectbox(
            "Selecciona el término que quieres que te expliquemos sin tecnicismos:",
            options=opciones,
            format_func=lambda k: f"[{GLOSARIO_LENGUAJE_CLARO_OED[k]['categoria']}] {GLOSARIO_LENGUAJE_CLARO_OED[k]['termino_tecnico']}",
        )
        ficha = explicar_termino_en_lenguaje_claro(seleccion)
        st.markdown(f"**🩺 Explicación de tu Médico Amigo:** {ficha['lenguaje_claro']}")
        st.info(f"🇨🇴 **Ejemplo en la vida real:** {ficha['ejemplo_cotidiano']}")


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
        "Revisando tus signos vitales con calma: tu crédito cumple la Ley 546 porque no supera el 30% "
        "de tus ingresos en SMMLV. Ahorrar tu cuota inicial en un encargo fiduciario usando tu Cuenta AFC "
        "baja impuestos medidos en UVT, evita el riesgo de inflación del IPC en UVR y mejora tu VPN y TIR "
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
<title>Manual de Marca: Tu Médico Financiero Amigo — Equipo OED</title>
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
    <h1>🩺 Manual de Marca: "Tu Médico Financiero Amigo" — Equipo OED</h1>
    <p>Tono cercano y cálido para <b>Camilo, Nidia, Nelson, Catalina, Jesi y Salin</b> con la regla de oro: <b>ninguna palabra financiera, legal o estadística se queda sin su explicación inmediata (?)</b>.</p>
  </div>

  <div class="tabs">
    <button class="tab active" onclick="verTab(0)">1. 🩺 Voz de Médico Amigo + Burbujas (?)</button>
    <button class="tab" onclick="verTab(1)">2. 📚 Diccionario Total (25+ Términos)</button>
    <button class="tab" onclick="verTab(2)">3. 🎨 Paleta del Consultorio</button>
    <button class="tab" onclick="verTab(3)">4. 👩‍💻 Plantilla por Integrante</button>
  </div>

  <div class="panel active" id="p0">
    <div class="card">
      <h3 style="margin-top:0;">Prueba en vivo las burbujas automáticas ("Cero Palabras Huérfanas")</h3>
      <p style="font-size:13.5px; color:#475569;">Pasa el mouse por encima de cualquier término con <b>?</b> — el sistema lo detecta solo dentro del párrafo de cualquier integrante:</p>
      <div class="oed-doc-card oed-doc-verde">
        <b>🩺💚 Lectura de tu Médico Financiero Amigo:</b><br>
        {frase_enriquecida}
      </div>
      <div class="oed-rx-box">
        <b>💊 Tu Receta Práctica para este Mes:</b> Separa tu cuota mensual el mismo día que te pagan nómina para cuidar tu tranquilidad sin sentir apretón a fin de mes.
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
      <h3 style="margin-top:0;">Haz clic en cualquier integrante para ver su saludo médico y copiar su código:</h3>
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
    <h3 style="margin:4px 0 10px;">🩺 ${{f.termino_tecnico}}</h3>
    <div class="oed-doc-card oed-doc-rojo"><b>❌ Tecnicismo frío que evitamos:</b> "${{f.como_no_decir}}"</div>
    <div class="oed-doc-card oed-doc-verde"><b>✅ Cómo te lo explica tu Médico Amigo:</b> ${{f.lenguaje_claro}}</div>
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
      <p>🩺 <i>"${{s.saludo_medico}}"</i> · Especialista: <b>${{s.responsable}}</b></p>
    </div>`;
  document.getElementById('code_box').textContent =
`from src.oed_design_system import (
    render_encabezado_modulo_oed,
    render_semaforo_ciudadano_oed,
    render_glosario_interactivo_oed,
    aplicar_estilo_plotly_oed,
)

def render_consulta_paso_${{s.paso}}():
    # 1. Saludo del Médico Amigo + Barra de progreso (Pasos 0 al 6)
    render_encabezado_modulo_oed(paso_actual=${{s.paso}})

    # 2. Diagnóstico cálido: auto-detecta términos (EA, UVR, IBC, Usura...) y les pone burbuja (?)
    render_semaforo_ciudadano_oed(
        nivel="verde",
        titulo_claro="Tus números cuidan tu tranquilidad",
        explicacion_humana="${{s.saludo_medico}}",
        siguiente_paso_accionable="Dosis práctica en $ COP para aplicar este mismo mes.",
    )

    # 3. Diccionario completo de las 5 familias siempre a un clic
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
    """Abre el Manual de Marca 'Tu Médico Financiero Amigo' en `http://127.0.0.1:8505`."""
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
    print(f"MANUAL DE MARCA 'TU MÉDICO FINANCIERO AMIGO' ACTIVO EN: {url}")
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
        print("OK: Plantilla y Manual de Marca 'Medico Financiero Amigo' verificados correctamente.")
    else:
        iniciar_manual_marca_web_local()
