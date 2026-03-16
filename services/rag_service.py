import json
import os

# Carga el catálogo en memoria al iniciar — rápido, sin consultas a BD
_CATALOGO = []

def cargar_catalogo():
    global _CATALOGO
    ruta = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'catalogo.json')
    with open(ruta, 'r', encoding='utf-8') as f:
        _CATALOGO = json.load(f)
    print(f"✅ Catálogo cargado: {len(_CATALOGO)} productos")

cargar_catalogo()


def buscar_productos(query: str, limite: int = 6) -> list[dict]:
    """Busca productos relevantes en el catálogo JSON en memoria."""
    if not _CATALOGO:
        return []

    query_lower = query.lower()
    palabras = [p for p in query_lower.split() if len(p) > 2]

    if not palabras:
        return []

    resultados = []
    for producto in _CATALOGO:
        texto = f"{producto['nombre']} {producto['marca']} {producto['modelo']}".lower()
        score = sum(1 for p in palabras if p in texto)
        if score > 0:
            resultados.append((score, producto))

    # Ordenar por relevancia
    resultados.sort(key=lambda x: x[0], reverse=True)
    return [r[1] for r in resultados[:limite]]


def formatear_contexto(productos: list[dict]) -> str:
    if not productos:
        return ""

    lines = ["PRODUCTOS DISPONIBLES EN SEKAITECH (precios reales, usar EXACTAMENTE):"]
    for p in productos:
        lines.append(f"- {p['nombre']} | Precio EXACTO: {p['precio']} | Marca: {p['marca']} | Stock: disponible")

    lines.append("\nIMPORTANTE: Usa SOLO los precios de la lista anterior. No inventes precios.")
    return "\n".join(lines)
