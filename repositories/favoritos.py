"""Acceso a datos: tabla favoritos."""
from database import query, execute
from repositories.productos import BASE


def agregar(usuario_id, producto_id):
    execute("INSERT OR IGNORE INTO favoritos (usuario_id, producto_id) VALUES (?,?)", (usuario_id, producto_id))


def quitar(usuario_id, producto_id):
    execute("DELETE FROM favoritos WHERE usuario_id = ? AND producto_id = ?", (usuario_id, producto_id))


def listar(usuario_id):
    sql = BASE + "JOIN favoritos f ON f.producto_id = p.id WHERE f.usuario_id = ? AND u.activo = 1 ORDER BY f.fecha DESC"
    return [dict(f) for f in query(sql, (usuario_id,))]
