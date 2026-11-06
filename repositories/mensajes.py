"""Acceso a datos: tablas conversaciones y mensajes."""
from database import query, execute


def buscar_conversacion(comprador_id, vendedor_id):
    return query(
        "SELECT * FROM conversaciones WHERE comprador_id = ? AND vendedor_id = ?",
        (comprador_id, vendedor_id), one=True,
    )


def crear_conversacion(comprador_id, vendedor_id):
    return execute(
        "INSERT INTO conversaciones (comprador_id, vendedor_id) VALUES (?,?)", (comprador_id, vendedor_id)
    )


def obtener_conversacion(conversacion_id):
    return query("SELECT * FROM conversaciones WHERE id = ?", (conversacion_id,), one=True)


def conversaciones_de(usuario_id):
    sql = (
        "SELECT c.id, "
        "CASE WHEN c.comprador_id = :uid THEN COALESCE(v.nombre_negocio, v.nombre) ELSE cu.nombre END AS interlocutor, "
        "(SELECT contenido FROM mensajes m WHERE m.conversacion_id = c.id ORDER BY m.id DESC LIMIT 1) AS ultimo_mensaje, "
        "COALESCE((SELECT MAX(m.id) FROM mensajes m WHERE m.conversacion_id = c.id), 0) AS ultimo_id "
        "FROM conversaciones c "
        "JOIN usuarios cu ON cu.id = c.comprador_id "
        "JOIN usuarios v ON v.id = c.vendedor_id "
        "WHERE c.comprador_id = :uid OR c.vendedor_id = :uid "
        "ORDER BY ultimo_id DESC"
    )
    return [dict(f) for f in query(sql, {"uid": usuario_id})]


def mensajes_de(conversacion_id, desde_id=0):
    filas = query(
        "SELECT id, emisor_id, producto_id, contenido, es_automatico, fecha_envio "
        "FROM mensajes WHERE conversacion_id = ? AND id > ? ORDER BY id",
        (conversacion_id, desde_id),
    )
    return [dict(f) for f in filas]


def insertar(conversacion_id, emisor_id, contenido, producto_id=None, es_automatico=0):
    nuevo_id = execute(
        "INSERT INTO mensajes (conversacion_id, emisor_id, producto_id, contenido, es_automatico) VALUES (?,?,?,?,?)",
        (conversacion_id, emisor_id, producto_id, contenido, es_automatico),
    )
    fila = query(
        "SELECT id, emisor_id, producto_id, contenido, es_automatico, fecha_envio FROM mensajes WHERE id = ?",
        (nuevo_id,), one=True,
    )
    return dict(fila)
