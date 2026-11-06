"""Acceso a datos: tabla usuarios."""
from database import query, execute


def crear(nombre, correo, password_hash, rol, nombre_negocio=None):
    return execute(
        "INSERT INTO usuarios (nombre, correo, password_hash, rol, nombre_negocio) VALUES (?,?,?,?,?)",
        (nombre, correo, password_hash, rol, nombre_negocio),
    )


def obtener(usuario_id):
    return query("SELECT * FROM usuarios WHERE id = ?", (usuario_id,), one=True)


def obtener_por_correo(correo):
    return query("SELECT * FROM usuarios WHERE correo = ?", (correo,), one=True)


def listar_vendedores(texto=None):
    sql = (
        "SELECT u.id, COALESCE(u.nombre_negocio, u.nombre) AS nombre, COUNT(p.id) AS total_productos "
        "FROM usuarios u LEFT JOIN productos p ON p.vendedor_id = u.id "
        "WHERE u.rol = 'vendedor' AND u.activo = 1"
    )
    params = []
    if texto:
        sql += " AND COALESCE(u.nombre_negocio, u.nombre) LIKE ?"
        params.append(f"%{texto}%")
    sql += " GROUP BY u.id ORDER BY nombre"
    return [dict(f) for f in query(sql, params)]


def listar_todos():
    filas = query(
        "SELECT id, nombre, correo, rol, nombre_negocio, activo, fecha_registro FROM usuarios ORDER BY id"
    )
    return [dict(f) for f in filas]


def cambiar_estado(usuario_id, activo):
    execute("UPDATE usuarios SET activo = ? WHERE id = ?", (1 if activo else 0, usuario_id))
