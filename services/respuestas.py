"""Respuestas rápidas automáticas (RF07): reglas simples por palabras clave."""
import unicodedata


def _normalizar(texto):
    """Minúsculas y sin tildes, para comparar palabras clave."""
    sin_tildes = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn")


def _precio(p):
    return f"El precio de {p['nombre']} es Bs {p['precio']:.2f}."


def _disponibilidad(p):
    if p["stock"] > 0:
        return f"Sí, {p['nombre']} está disponible. Quedan {p['stock']} unidades."
    return f"Por ahora {p['nombre']} está agotado. Escríbenos y te avisamos cuando haya stock."


def _caracteristicas(p):
    return f"Sobre {p['nombre']}: {p['descripcion'] or 'consúltanos y te damos más detalles.'}"


# Tabla de reglas: (palabras clave, función que arma la respuesta).
REGLAS = [
    (("precio", "cuesta", "cuanto", "costo", "vale"), _precio),
    (("disponible", "stock", "quedan", "hay ", "tienen", "tienes", "agotado"), _disponibilidad),
    (("caracteristica", "descripcion", "detalle", "medida", "material", "color", "talla"), _caracteristicas),
]


def responder(texto, producto):
    """Devuelve la respuesta automática o None si no hay regla aplicable."""
    if not producto:
        return None
    limpio = _normalizar(texto)
    for claves, construir in REGLAS:
        if any(clave in limpio for clave in claves):
            return construir(producto)
    return None
