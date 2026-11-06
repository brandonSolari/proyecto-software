"""API de autenticación (RF01)."""
from flask import Blueprint, g, jsonify, request

from services import seguridad, usuarios

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/registro")
def registro():
    usuario = usuarios.registrar(request.get_json(silent=True) or {})
    return jsonify(token=seguridad.crear_token(usuario), usuario=usuarios.publico(usuario)), 201


@bp.post("/login")
def login():
    datos = request.get_json(silent=True) or {}
    usuario = usuarios.autenticar(datos.get("correo"), datos.get("password"))
    return jsonify(token=seguridad.crear_token(usuario), usuario=usuarios.publico(usuario))


@bp.get("/yo")
@seguridad.login_required
def yo():
    return jsonify(usuario=usuarios.publico(g.usuario))
