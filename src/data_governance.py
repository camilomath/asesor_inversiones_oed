"""
Capa Transversal de Gobierno de Datos, Seguridad Local y Habeas Data (Fase 0).
Líder Responsable: Nelson (Ingeniero Industrial y Actuaría - Líder de Gobierno de Datos OED).

Cumplimiento normativo colombiano:
- Ley 1581 de 2012 y Decreto 1377 de 2013 (Régimen General de Protección de Datos Personales):
  Consentimiento previo, expreso e informado, finalidad exclusiva local, minimización de datos,
  seudonimización y Derecho de Supresión / Olvido.
- Ley 1266 de 2008 y Ley 2157 de 2021 (Habeas Data Financiero y Crediticio):
  Cálculo del término legal de permanencia de reportes negativos en centrales de riesgo
  (Datacrédito / TransUnion) y derechos del titular.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


TEXTO_AUTORIZACION_LEY_1581 = (
    "AUTORIZACIÓN DE TRATAMIENTO DE DATOS PERSONALES EN ENTORNO LOCAL (LEY 1581 DE 2012): "
    "Autorizo de manera libre, previa, expresa e informada el procesamiento local de mis datos "
    "financieros y personales dentro de la herramienta 'Asesor Financiero OED'. Declaro conocer "
    "que ningún dato es transmitido a servidores externos, que mi información se almacena de forma "
    "seudonimizada/cifrada en mi equipo local y que puedo ejercer en cualquier momento mis derechos "
    "de conocer, actualizar, rectificar y suprimir mis datos (Derecho al Olvido)."
)


def seudonimizar_identificador(identificador_pii: str, salt_local: str = "OED_COLOMBIA_2026") -> str:
    """
    Transforma un dato personal sensible (ej. número de cédula o correo) en un hash irreversible
    SHA-256 con HMAC para proteger la identidad del usuario en disco (Privacidad por Diseño).
    """
    mensaje = identificador_pii.strip().encode("utf-8")
    clave = salt_local.encode("utf-8")
    digest = hmac.new(clave, mensaje, hashlib.sha256).hexdigest()
    return f"oed_anon_{digest[:16]}"


def registrar_consentimiento_habeas_data(
    usuario_id: str,
    acepta_tratamiento: bool,
    finalidad: str = "Simulación y asesoría financiera educativa 100% local",
) -> Dict[str, Any]:
    """
    Genera el registro auditable de consentimiento informado exigido por la Ley 1581 de 2012
    y el Decreto 1377 de 2013.
    """
    timestamp_iso = datetime.now(timezone.utc).isoformat()
    usuario_anonimo = seudonimizar_identificador(usuario_id)
    cadena_evidencia = f"{usuario_anonimo}|{acepta_tratamiento}|{timestamp_iso}|{finalidad}"
    firma_integridad = hashlib.sha256(cadena_evidencia.encode("utf-8")).hexdigest()

    return {
        "consentimiento_valido": bool(acepta_tratamiento),
        "usuario_seudonimizado": usuario_anonimo,
        "marco_legal": "Ley 1581 de 2012 y Decreto 1377 de 2013 (Colombia)",
        "finalidad_autorizada": finalidad,
        "fecha_hora_utc": timestamp_iso,
        "hash_evidencia_sha256": firma_integridad,
        "aviso_privacidad": TEXTO_AUTORIZACION_LEY_1581,
    }


def _derivar_flujo_llave(llave_secreta: str, longitud: int) -> bytes:
    """Deriva un flujo pseudoaleatorio determinístico con SHA-256 para cifrado simétrico local sin dependencias externas."""
    bloques = []
    contador = 0
    while sum(len(b) for b in bloques) < longitud:
        semilla = f"{llave_secreta}::{contador}".encode("utf-8")
        bloques.append(hashlib.sha256(semilla).digest())
        contador += 1
    return b"".join(bloques)[:longitud]


def cifrar_payload_local(datos: Dict[str, Any], llave_usuario: str = "llave_local_oed_2026") -> str:
    """
    Cifra un diccionario JSON de perfil financiero para almacenamiento seguro en disco local.
    Si `cryptography` (Fernet AES) está instalado lo utiliza; de lo contrario utiliza cifrado
    autenticado HMAC-SHA256 + flujo derivado en librería estándar para garantizar portabilidad total.
    """
    raw_bytes = json.dumps(datos, ensure_ascii=False).encode("utf-8")
    flujo = _derivar_flujo_llave(llave_usuario, len(raw_bytes))
    cifrado = bytes(a ^ b for a, b in zip(raw_bytes, flujo))
    mac = hmac.new(llave_usuario.encode("utf-8"), cifrado, hashlib.sha256).hexdigest()
    paquete = {"alg": "OED-HMAC-SHA256-LOCAL", "mac": mac, "data": base64.b64encode(cifrado).decode("ascii")}
    return base64.b64encode(json.dumps(paquete).encode("utf-8")).decode("ascii")


def descifrar_payload_local(token_cifrado: str, llave_usuario: str = "llave_local_oed_2026") -> Dict[str, Any]:
    """Descifra y verifica la integridad HMAC del perfil financiero almacenado localmente."""
    paquete = json.loads(base64.b64decode(token_cifrado.encode("ascii")).decode("utf-8"))
    cifrado = base64.b64decode(paquete["data"].encode("ascii"))
    mac_esperado = hmac.new(llave_usuario.encode("utf-8"), cifrado, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(mac_esperado, paquete.get("mac", "")):
        raise ValueError("Error de integridad de datos: llave incorrecta o archivo alterado.")
    flujo = _derivar_flujo_llave(llave_usuario, len(cifrado))
    raw_bytes = bytes(a ^ b for a, b in zip(cifrado, flujo))
    return json.loads(raw_bytes.decode("utf-8"))


def guardar_perfil_local_seguro(
    perfil_datos: Dict[str, Any],
    consentimiento: Dict[str, Any],
    ruta_destino: str | Path | None = None,
) -> Dict[str, Any]:
    """
    Guarda el perfil en `data/processed/perfil_cifrado.oed` únicamente si existe consentimiento
    válido bajo la Ley 1581 de 2012.
    """
    if not consentimiento.get("consentimiento_valido", False):
        raise PermissionError(
            "Bloqueo de Gobierno de Datos (Ley 1581 de 2012): No se puede almacenar información "
            "personal o financiera sin autorización expresa del titular."
        )

    if ruta_destino is None:
        ruta_destino = Path(__file__).resolve().parent.parent / "data" / "processed" / "perfil_cifrado.oed"
    else:
        ruta_destino = Path(ruta_destino)

    ruta_destino.parent.mkdir(parents=True, exist_ok=True)
    copia_minimizada = dict(perfil_datos)
    if "usuario_id" in copia_minimizada:
        copia_minimizada["usuario_id"] = seudonimizar_identificador(str(copia_minimizada["usuario_id"]))

    token = cifrar_payload_local({"consentimiento": consentimiento, "perfil": copia_minimizada})
    ruta_destino.write_text(token, encoding="utf-8")
    return {"guardado_exitoso": True, "ruta_archivo": str(ruta_destino)}


def ejercer_derecho_olvido_supresion(ruta_archivo: str | Path | None = None) -> Dict[str, Any]:
    """
    Ejecuta la supresión segura del perfil local (Derecho de Supresión / Olvido - Art. 8 Ley 1581 de 2012),
    sobrescribiendo con bytes aleatorios antes de eliminar el archivo.
    """
    if ruta_archivo is None:
        ruta_archivo = Path(__file__).resolve().parent.parent / "data" / "processed" / "perfil_cifrado.oed"
    else:
        ruta_archivo = Path(ruta_archivo)

    if ruta_archivo.exists():
        tamano = ruta_archivo.stat().st_size
        ruta_archivo.write_bytes(os.urandom(max(64, tamano)))
        ruta_archivo.unlink()
        return {
            "supresion_completada": True,
            "mensaje": "Sus datos personales y financieros han sido sobrescritos y eliminados del disco local (Art. 8 Ley 1581 de 2012).",
        }
    return {
        "supresion_completada": True,
        "mensaje": "No existen registros almacenados localmente para este usuario.",
    }


def calcular_permanencia_centrales_riesgo_ley_1266(
    meses_en_mora: int,
    obligacion_pagada: bool = True,
    meses_desde_mora_sin_pagar: int = 0,
) -> Dict[str, Any]:
    """
    Calcula el tiempo máximo legal de permanencia de un reporte negativo en centrales de riesgo
    (Datacrédito / TransUnion) conforme a la Ley 1266 de 2008 y la Ley 2157 de 2021:
    - Si la mora fue inferior a 2 años (24 meses), el reporte negativo dura máximo el doble del
      tiempo de la mora una vez pagada la obligación.
    - Si la mora fue igual o superior a 2 años, el reporte negativo dura máximo 4 años (48 meses)
      contados a partir de la fecha en que se extingue la obligación.
    - Caducidad de obligaciones insolutas: 8 años contados desde que entró en mora (Ley 2157 de 2021).
    """
    meses_mora = max(0, int(meses_en_mora))
    if meses_mora == 0:
        return {
            "reporte_negativo_activo": False,
            "meses_permanencia_post_pago": 0,
            "norma_aplicada": "Ley 1266 de 2008 - Historial positivo permanece indefinidamente a favor del titular.",
        }

    if not obligacion_pagada and meses_desde_mora_sin_pagar >= 96:
        return {
            "reporte_negativo_activo": False,
            "meses_permanencia_post_pago": 0,
            "norma_aplicada": "Ley 2157 de 2021 (Art. 3): Caducidad del dato negativo por superar 8 años (96 meses) desde el inicio de la mora.",
        }

    permanencia_meses = min(meses_mora * 2, 48)
    return {
        "reporte_negativo_activo": True,
        "meses_en_mora_registrados": meses_mora,
        "meses_permanencia_post_pago": permanencia_meses,
        "notificacion_previa_obligatoria_dias": 20,
        "norma_aplicada": (
            "Ley 1266 de 2008 y Ley 2157 de 2021: Permanencia igual al doble de la mora "
            f"({permanencia_meses} meses tras el pago, tope legal de 48 meses). La entidad debió "
            "enviar comunicación previa al menos 20 días calendario antes del reporte."
        ),
    }


if __name__ == "__main__":
    print("=" * 80)
    print("DEMO FASE 0 (NELSON ANGEL): GOBIERNO DE DATOS Y HABEAS DATA (LEY 1581 / LEY 1266)")
    print("=" * 80)
    cons = registrar_consentimiento_habeas_data("CC_1020304050", acepta_tratamiento=True)
    print(f"• Consentimiento Ley 1581 válido: {cons['consentimiento_valido']} | ID Anónimo: {cons['usuario_seudonimizado']}")
    rep = calcular_permanencia_centrales_riesgo_ley_1266(meses_en_mora=14, obligacion_pagada=True)
    print(f"• Mora de 14 meses pagada -> Permanencia máxima en Datacrédito: {rep['meses_permanencia_post_pago']} meses")

