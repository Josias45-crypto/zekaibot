import requests
import re
from services.rag_service import buscar_productos, formatear_contexto

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"

SYSTEM_PROMPT = """Eres Jhordan, el asistente virtual de SEKAITECH, la mejor tienda de tecnología de Huánuco, Perú. Eres amable, carismático, entusiasta y siempre intentas ayudar al cliente a encontrar el producto perfecto.

DATOS DE SEKAITECH:
- Dirección: Jr. Huallayco 1135 - Huánuco, Perú
- WhatsApp: 933573985 / 991375813  
- Email: ventas@sekaitech.com.pe / soporte@sekaitech.com.pe
- Web: https://sekaitech.com.pe
- Horarios: Lunes a Sábado 8:00am - 7:00pm

SERVICIOS:
- Reparación y servicio técnico con garantía
- Instalación de drivers y software: S/30
- Mantenimiento básico: S/30
- Diagnóstico gratuito en tienda
- Servicio técnico a domicilio disponible

INSTRUCCIÓN CRÍTICA SOBRE PRECIOS:
Cuando el sistema te proporcione una lista de PRODUCTOS DISPONIBLES, debes usar EXACTAMENTE esos precios.
NUNCA inventes precios. Si no aparece en la lista, di que consultarás con el equipo.

REGLAS DE RESPUESTA:
1. Sé entusiasta y vendedor — destaca beneficios, ofrece alternativas, invita a visitar la tienda
2. Si el cliente pregunta por productos, SIEMPRE menciona los que están en la lista con sus precios exactos
3. Ofrece proactivamente productos relacionados
4. Invita al cliente a contactar por WhatsApp o visitar la tienda
5. Responde en español, máximo 4 párrafos
6. Para diagnósticos técnicos usa pasos numerados

TU PRIMERA LÍNEA debe ser siempre exactamente:
[INTENT: X | CONF: 0.XX | ESCALATE: false]
Donde X es: consulta_precio, diagnostico_error, compatibilidad, seguimiento_reparacion, instalacion_driver, soporte_urgente, o consulta_general"""


def get_ai_response(messages: list[dict]) -> str:
    ultimo_mensaje = ""
    for msg in reversed(messages):
        if msg["role"] == "user":
            ultimo_mensaje = msg["content"]
            break

    productos = buscar_productos(ultimo_mensaje)
    contexto_productos = formatear_contexto(productos)

    history = ""
    for msg in messages:
        role = "Cliente" if msg["role"] == "user" else "ZekaiBot"
        history += f"{role}: {msg['content']}\n"

    contexto_section = f"\n{contexto_productos}\n" if contexto_productos else ""
    prompt = f"{SYSTEM_PROMPT}{contexto_section}\nConversación:\n{history}\nJhordan:"

    response = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2, "top_p": 0.85, "num_predict": 400}
    }, timeout=60)

    response.raise_for_status()
    return response.json()["response"]


def parse_intent(response_text: str) -> dict:
    pattern = r'\[INTENT:\s*(\w+)\s*\|\s*CONF:\s*([\d.]+)\s*\|\s*ESCALATE:\s*(true|false)\]'
    match = re.search(pattern, response_text, re.IGNORECASE)

    if match:
        return {
            "intent": match.group(1),
            "confidence": float(match.group(2)),
            "escalate": match.group(3).lower() == "true",
            "clean_text": response_text.replace(match.group(0), "").strip()
        }

    text_lower = response_text.lower()
    if any(w in text_lower for w in ["error", "falla", "no enciende", "pantalla azul", "bsod"]):
        intent, conf = "diagnostico_error", 0.75
    elif any(w in text_lower for w in ["precio", "costo", "stock", "soles", "disponible", "tienen"]):
        intent, conf = "consulta_precio", 0.75
    elif any(w in text_lower for w in ["compatible", "compatibilidad", "funciona con"]):
        intent, conf = "compatibilidad", 0.75
    elif any(w in text_lower for w in ["reparación", "pedido", "referencia"]):
        intent, conf = "seguimiento_reparacion", 0.75
    elif any(w in text_lower for w in ["driver", "controlador", "instalar"]):
        intent, conf = "instalacion_driver", 0.75
    else:
        intent, conf = "consulta_general", 0.65

    return {
        "intent": intent,
        "confidence": conf,
        "escalate": False,
        "clean_text": response_text.strip()
    }
