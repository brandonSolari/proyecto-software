"""API de administración de usuarios."""
from flask import Blueprint, g, jsonify, request

from services import seguridad, usuarios

bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@bp.get("/usuarios")
@seguridad.rol_requerido("administrador")
def listar():
    return jsonify(usuarios.listar_para_admin())


@bp.patch("/usuarios/<int:usuario_id>/estado")
@seguridad.rol_requerido("administrador")
def estado(usuario_id):
    datos = request.get_json(silent=True) or {}
    usuarios.cambiar_estado(g.usuario, usuario_id, datos.get("activo"))
    return "", 204
