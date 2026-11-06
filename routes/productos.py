"""API de catálogo, búsqueda e inventario (RF02 a RF05)."""
from flask import Blueprint, g, jsonify, request

from services import catalogo, seguridad, usuarios

bp = Blueprint("productos", __name__, url_prefix="/api")


def _entero(valor):
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


@bp.get("/categorias")
def categorias():
    return jsonify(catalogo.categorias())


@bp.get("/vendedores")
def vendedores():
    return jsonify(usuarios.listar_vendedores(request.args.get("q", "").strip()))


@bp.get("/productos")
def listar():
    return jsonify(catalogo.buscar(
        texto=request.args.get("q", "").strip(),
        categoria_id=_entero(request.args.get("categoria")),
        vendedor_id=_entero(request.args.get("vendedor")),
    ))


@bp.get("/productos/<int:producto_id>")
def detalle(producto_id):
    return jsonify(catalogo.detalle(producto_id))


@bp.get("/mis-productos")
@seguridad.rol_requerido("vendedor")
def mis_productos():
    return jsonify(catalogo.de_vendedor(g.usuario))


@bp.post("/productos")
@seguridad.rol_requerido("vendedor")
def crear():
    return jsonify(catalogo.crear(g.usuario, request.get_json(silent=True) or {})), 201


@bp.put("/productos/<int:producto_id>")
@seguridad.rol_requerido("vendedor")
def actualizar(producto_id):
    return jsonify(catalogo.actualizar(g.usuario, producto_id, request.get_json(silent=True) or {}))


@bp.patch("/productos/<int:producto_id>/stock")
@seguridad.rol_requerido("vendedor")
def stock(producto_id):
    datos = request.get_json(silent=True) or {}
    return jsonify(catalogo.cambiar_stock(g.usuario, producto_id, datos.get("stock")))


@bp.delete("/productos/<int:producto_id>")
@seguridad.rol_requerido("vendedor")
def eliminar(producto_id):
    catalogo.eliminar(g.usuario, producto_id)
    return "", 204
