"""Lógica de negocio: conversaciones y mensajes entre comprador y vendedor."""
from repositories import mensajes as repo
from repositories import productos as repo_productos
from repositories import usuarios as repo_usuarios
from services import respuestas
from services.errores import ErrorNegocio

MAX_CARACTERES = 500


def iniciar(comprador, vendedor_id):
    """Obtiene la conversación existente con el vendedor o crea una nueva."""
    vendedor = repo_usuarios.obtener(vendedor_id)
    if not vendedor or vendedor["rol"] != "vendedor" or not vendedor["activo"]:
        raise ErrorNegocio("El vendedor no existe.", 404)
    existente = repo.buscar_conversacion(comprador["id"], vendedor_id)
    return existente["id"] if existente else repo.crear_conversacion(comprador["id"], vendedor_id)


def listar(usuario):
    return repo.conversaciones_de(usuario["id"])


def _conversacion_de(usuario, conversacion_id):
    conv = repo.obtener_conversacion(conversacion_id)
    if not conv:
        raise ErrorNegocio("Conversación no encontrada.", 404)
    if usuario["id"] not in (conv["comprador_id"], conv["vendedor_id"]):
        raise ErrorNegocio("No participas en esta conversación.", 403)
    return conv


def mensajes(usuario, conversacion_id, desde_id=0):
    _conversacion_de(usuario, conversacion_id)
    return repo.mensajes_de(conversacion_id, desde_id)


def enviar(usuario, conversacion_id, contenido, producto_id=None):
    conv = _conversacion_de(usuario, conversacion_id)
    contenido = (contenido or "").strip()
    if not contenido:
        raise ErrorNegocio("El mensaje no puede estar vacío.")
    if len(contenido) > MAX_CARACTERES:
        raise ErrorNegocio(f"El mensaje no puede superar {MAX_CARACTERES} caracteres.")

    producto = repo_productos.obtener(producto_id) if producto_id else None
    # El producto consultado debe pertenecer al vendedor de la conversación.
    if producto and producto["vendedor_id"] != conv["vendedor_id"]:
        producto = None

    nuevos = [repo.insertar(conversacion_id, usuario["id"], contenido, producto["id"] if producto else None)]

    # Si escribe el comprador, el sistema puede responder en nombre del vendedor.
    if usuario["id"] == conv["comprador_id"]:
        auto = respuestas.responder(contenido, producto)
        if auto:
            nuevos.append(repo.insertar(conversacion_id, conv["vendedor_id"], auto, producto["id"], es_automatico=1))
    return nuevos
