"""Capa de persistencia: conexión a SQLite y funciones auxiliares."""
import os
import sqlite3
from flask import g, current_app


def get_db():
    """Devuelve la conexión de la petición actual (una por petición)."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query(sql, params=(), one=False):
    """SELECT con parámetros (evita inyección SQL)."""
    cur = get_db().execute(sql, params)
    filas = cur.fetchall()
    cur.close()
    if one:
        return filas[0] if filas else None
    return filas


def execute(sql, params=()):
    """INSERT / UPDATE / DELETE con parámetros. Devuelve el id insertado."""
    db = get_db()
    cur = db.execute(sql, params)
    db.commit()
    return cur.lastrowid


def init_db(con_datos_demo=True):
    """Crea las tablas desde schema.sql y carga datos de prueba."""
    db = get_db()
    ruta = os.path.join(current_app.root_path, "schema.sql")
    with open(ruta, encoding="utf-8") as f:
        db.executescript(f.read())
    if con_datos_demo:
        from seed import cargar_datos_demo
        cargar_datos_demo()
    db.commit()
