"""Datos de prueba para demostrar el sistema (clave de todas las cuentas: Casero123)."""
from database import get_db
from services.seguridad import hashear

CLAVE_DEMO = "Casero123"


def cargar_datos_demo():
    db = get_db()
    h = hashear(CLAVE_DEMO)

    db.executemany(
        "INSERT INTO usuarios (nombre, correo, password_hash, rol, nombre_negocio) VALUES (?,?,?,?,?)",
        [
            ("Administrador Casero", "admin@casero.bo", h, "administrador", None),
            ("Carlos Mendoza", "carlos@casero.bo", h, "vendedor", "Tienda Carlos"),
            ("Luz Mamani", "luz@casero.bo", h, "vendedor", "Artesanías Luz"),
            ("Alan Quispe", "alan@casero.bo", h, "comprador", None),
            ("Ana García", "ana@casero.bo", h, "comprador", None),
        ],
    )
    db.executemany(
        "INSERT INTO categorias (nombre) VALUES (?)",
        [("Hogar",), ("Ropa",), ("Gamer",), ("Artesanías",), ("Electrónica",)],
    )
    # (vendedor, categoría, nombre, descripción, precio, stock)
    db.executemany(
        "INSERT INTO productos (vendedor_id, categoria_id, nombre, descripcion, precio, stock) VALUES (?,?,?,?,?,?)",
        [
            (2, 1, "Freidora de aire 4L", "Capacidad de 4 litros, control digital de temperatura, cesta antiadherente.", 380.0, 5),
            (2, 2, "Chamarra para el frío", "Chamarra acolchada impermeable, tallas S a XL, color negro.", 250.0, 12),
            (2, 2, "Canguro de algodón", "Canguro 100% algodón con capucha, disponible en azul y gris.", 160.0, 8),
            (2, 3, "Consola portátil", "Consola portátil con pantalla de 7 pulgadas y un control incluido.", 2500.0, 3),
            (2, 3, "Control inalámbrico", "Control inalámbrico recargable compatible con consola y PC.", 450.0, 0),
            (2, 5, "Afeitadora eléctrica", "Afeitadora recargable con tres cabezales, resistente al agua.", 150.0, 10),
            (3, 4, "Jarra artesanal de cerámica", "Jarra hecha a mano por artesanos de El Alto, 1 litro.", 60.0, 6),
            (3, 4, "Llaveros artesanales", "Llaveros tejidos con motivos andinos. Precio por unidad.", 15.0, 40),
            (3, 1, "Manta de alpaca", "Manta tejida en lana de alpaca, 1.5 x 2 metros.", 280.0, 4),
        ],
    )
    db.executemany("INSERT INTO favoritos (usuario_id, producto_id) VALUES (?,?)", [(4, 1), (4, 4), (4, 7)])

    db.execute("INSERT INTO conversaciones (comprador_id, vendedor_id) VALUES (4, 2)")
    db.executemany(
        "INSERT INTO mensajes (conversacion_id, emisor_id, producto_id, contenido, es_automatico) VALUES (?,?,?,?,?)",
        [
            (1, 4, 4, "Hola, vengo del live. ¿Aún tienes disponible la consola?", 0),
            (1, 2, 4, "¡Hola Alan! Sí, nos quedan unidades. ¿Te la separo?", 0),
        ],
    )
