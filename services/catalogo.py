"""Lógica de negocio: catálogo, inventario y favoritos."""
from repositories import productos as repo
from repositories import favoritos as repo_fav
from services.errores import ErrorNegocio


def _presentar(p):
    p["disponible"] = bool(p["disponible"])
    return p


def _limpiar(datos):
    """Valida y normaliza los datos de un producto."""
    nombre = (datos.get("nombre") or "").strip()
    descripcion = (datos.get("descripcion") or "").strip()
    imagen = (datos.get("imagen_url") or "").strip() or None
    try:
        precio = float(datos.get("precio"))
        stock = int(datos.get("stock", 0))
        categoria_id = int(datos.get("categoria_id"))
    except (TypeError, ValueError):
        raise ErrorNegocio("Precio, stock y categoría deben ser números válidos.")

    if len(nombre) < 3:
        raise ErrorNegocio("El nombre del producto debe tener al menos 3 caracteres.")
    if precio < 0:
        raise ErrorNegocio("El precio no puede ser negativo.")
    if stock < 0:
        raise ErrorNegocio("El stock no puede ser negativo.")
    if not repo.categoria_existe(categoria_id):
        raise ErrorNegocio("La categoría no existe.")
    if imagen and not imagen.lower().startswith(("http://", "https://")):
        raise ErrorNegocio("La imagen debe ser un enlace que empiece con http:// o https://")
    return {"nombre": nombre, "descripcion": descripcion, "precio": round(precio, 2),
            "stock": stock, "categoria_id": categoria_id, "imagen_url": imagen}


def _producto_propio(vendedor, producto_id):
    producto = repo.obtener(producto_id)
    if not producto:
        raise ErrorNegocio("Producto no encontrado.", 404)
    if producto["vendedor_id"] != vendedor["id"]:
        raise ErrorNegocio("Este producto pertenece a otro vendedor.", 403)
    return producto


def categorias():
    return repo.categorias()


def buscar(texto=None, categoria_id=None, vendedor_id=None):
    return [_presentar(p) for p in repo.buscar(texto, categoria_id, vendedor_id)]


def detalle(producto_id):
    producto = repo.obtener(producto_id)
    if not producto:
        raise ErrorNegocio("Producto no encontrado.", 404)
    return _presentar(producto)


def de_vendedor(vendedor):
    return [_presentar(p) for p in repo.de_vendedor(vendedor["id"])]


def crear(vendedor, datos):
    nuevo_id = repo.crear(vendedor["id"], _limpiar(datos))
    return detalle(nuevo_id)


def actualizar(vendedor, producto_id, datos):
    _producto_propio(vendedor, producto_id)
    repo.actualizar(producto_id, _limpiar(datos))
    return detalle(producto_id)


def cambiar_stock(vendedor, producto_id, stock):
    _producto_propio(vendedor, producto_id)
    try:
        stock = int(stock)
    except (TypeError, ValueError):
        raise ErrorNegocio("El stock debe ser un número entero.")
    if stock < 0:
        raise ErrorNegocio("El stock no puede ser negativo.")
    repo.actualizar_stock(producto_id, stock)
    return detalle(producto_id)


def eliminar(vendedor, producto_id):
    _producto_propio(vendedor, producto_id)
    repo.eliminar(producto_id)


# ---- Favoritos -------------------------------------------------------
def listar_favoritos(usuario):
    return [_presentar(p) for p in repo_fav.listar(usuario["id"])]


def marcar_favorito(usuario, producto_id):
    detalle(producto_id)  # lanza 404 si no existe
    repo_fav.agregar(usuario["id"], producto_id)


def quitar_favorito(usuario, producto_id):
    repo_fav.quitar(usuario["id"], producto_id)
