"""Acceso a datos: tablas productos y categorias."""
from database import query, execute

# Consulta base: une producto, categoría y vendedor. La disponibilidad se
# calcula a partir del stock (no se almacena, para evitar datos redundantes).
BASE = (
    "SELECT p.id, p.nombre, p.descripcion, p.precio, p.stock, p.imagen_url, "
    "(p.stock > 0) AS disponible, c.id AS categoria_id, c.nombre AS categoria, "
    "u.id AS vendedor_id, COALESCE(u.nombre_negocio, u.nombre) AS vendedor "
    "FROM productos p "
    "JOIN categorias c ON c.id = p.categoria_id "
    "JOIN usuarios u ON u.id = p.vendedor_id "
)


def categorias():
    return [dict(f) for f in query("SELECT id, nombre FROM categorias ORDER BY nombre")]


def categoria_existe(categoria_id):
    return query("SELECT 1 FROM categorias WHERE id = ?", (categoria_id,), one=True) is not None


def buscar(texto=None, categoria_id=None, vendedor_id=None):
    sql = BASE + "WHERE u.activo = 1"
    params = []
    if texto:
        sql += " AND (p.nombre LIKE ? OR p.descripcion LIKE ?)"
        params += [f"%{texto}%", f"%{texto}%"]
    if categoria_id:
        sql += " AND p.categoria_id = ?"
        params.append(categoria_id)
    if vendedor_id:
        sql += " AND p.vendedor_id = ?"
        params.append(vendedor_id)
    sql += " ORDER BY p.id DESC"
    return [dict(f) for f in query(sql, params)]


def obtener(producto_id):
    fila = query(BASE + "WHERE p.id = ?", (producto_id,), one=True)
    return dict(fila) if fila else None


def de_vendedor(vendedor_id):
    return [dict(f) for f in query(BASE + "WHERE p.vendedor_id = ? ORDER BY p.id DESC", (vendedor_id,))]


def crear(vendedor_id, d):
    return execute(
        "INSERT INTO productos (vendedor_id, categoria_id, nombre, descripcion, precio, stock, imagen_url) "
        "VALUES (?,?,?,?,?,?,?)",
        (vendedor_id, d["categoria_id"], d["nombre"], d["descripcion"], d["precio"], d["stock"], d["imagen_url"]),
    )


def actualizar(producto_id, d):
    execute(
        "UPDATE productos SET categoria_id=?, nombre=?, descripcion=?, precio=?, stock=?, imagen_url=? WHERE id=?",
        (d["categoria_id"], d["nombre"], d["descripcion"], d["precio"], d["stock"], d["imagen_url"], producto_id),
    )


def actualizar_stock(producto_id, stock):
    execute("UPDATE productos SET stock = ? WHERE id = ?", (stock, producto_id))


def eliminar(producto_id):
    execute("DELETE FROM productos WHERE id = ?", (producto_id,))
