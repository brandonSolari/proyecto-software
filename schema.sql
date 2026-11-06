-- Casero · Esquema de base de datos (SQLite)
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS mensajes;
DROP TABLE IF EXISTS conversaciones;
DROP TABLE IF EXISTS favoritos;
DROP TABLE IF EXISTS productos;
DROP TABLE IF EXISTS categorias;
DROP TABLE IF EXISTS usuarios;

CREATE TABLE usuarios (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre          TEXT    NOT NULL,
    correo          TEXT    NOT NULL UNIQUE,
    password_hash   TEXT    NOT NULL,
    rol             TEXT    NOT NULL CHECK (rol IN ('comprador', 'vendedor', 'administrador')),
    nombre_negocio  TEXT,
    activo          INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1)),
    fecha_registro  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE categorias (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre  TEXT NOT NULL UNIQUE
);

CREATE TABLE productos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    vendedor_id     INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    categoria_id    INTEGER NOT NULL REFERENCES categorias(id),
    nombre          TEXT    NOT NULL,
    descripcion     TEXT    NOT NULL DEFAULT '',
    precio          REAL    NOT NULL CHECK (precio >= 0),
    stock           INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    imagen_url      TEXT,
    fecha_creacion  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE favoritos (
    usuario_id   INTEGER NOT NULL REFERENCES usuarios(id)  ON DELETE CASCADE,
    producto_id  INTEGER NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
    fecha        TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    PRIMARY KEY (usuario_id, producto_id)
);

CREATE TABLE conversaciones (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    comprador_id    INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    vendedor_id     INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    fecha_creacion  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    UNIQUE (comprador_id, vendedor_id),
    CHECK (comprador_id <> vendedor_id)
);

CREATE TABLE mensajes (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    conversacion_id  INTEGER NOT NULL REFERENCES conversaciones(id) ON DELETE CASCADE,
    emisor_id        INTEGER NOT NULL REFERENCES usuarios(id),
    producto_id      INTEGER REFERENCES productos(id) ON DELETE SET NULL,
    contenido        TEXT    NOT NULL,
    es_automatico    INTEGER NOT NULL DEFAULT 0 CHECK (es_automatico IN (0, 1)),
    fecha_envio      TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE INDEX idx_productos_vendedor  ON productos(vendedor_id);
CREATE INDEX idx_productos_categoria ON productos(categoria_id);
CREATE INDEX idx_mensajes_conv       ON mensajes(conversacion_id);
