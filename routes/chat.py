"""API de mensajería interna (RF06 y RF07)."""
from flask import Blueprint, g, jsonify, request

from services import mensajeria, seguridad

bp = Blueprint("chat", __name__, url_prefix="/api/conversaciones")


@bp.get("")
@seguridad.login_required
def listar():
    return jsonify(mensajeria.listar(g.usuario))


@bp.post("")
@seguridad.rol_requerido("comprador")
def iniciar():
    datos = request.get_json(silent=True) or {}
    try:
        vendedor_id = int(datos.get("vendedor_id"))
    except (TypeError, ValueError):
        vendedor_id = 0
    return jsonify(id=mensajeria.iniciar(g.usuario, vendedor_id)), 201


@bp.get("/<int:conversacion_id>/mensajes")
@seguridad.login_required
def ver_mensajes(conversacion_id):
    desde = request.args.get("desde", 0, type=int)
    return jsonify(mensajeria.mensajes(g.usuario, conversacion_id, desde))


@bp.post("/<int:conversacion_id>/mensajes")
@seguridad.login_required
def enviar(conversacion_id):
    datos = request.get_json(silent=True) or {}
    nuevos = mensajeria.enviar(g.usuario, conversacion_id, datos.get("contenido"), datos.get("producto_id"))
    return jsonify(mensajes=nuevos), 201
