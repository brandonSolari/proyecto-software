"""API de favoritos (RF08, parte de favoritos)."""
from flask import Blueprint, g, jsonify

from services import catalogo, seguridad

bp = Blueprint("favoritos", __name__, url_prefix="/api/favoritos")


@bp.get("")
@seguridad.rol_requerido("comprador")
def listar():
    return jsonify(catalogo.listar_favoritos(g.usuario))


@bp.put("/<int:producto_id>")
@seguridad.rol_requerido("comprador")
def marcar(producto_id):
    catalogo.marcar_favorito(g.usuario, producto_id)
    return "", 204


@bp.delete("/<int:producto_id>")
@seguridad.rol_requerido("comprador")
def quitar(producto_id):
    catalogo.quitar_favorito(g.usuario, producto_id)
    return "", 204
