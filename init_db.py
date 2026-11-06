"""Reinicia la base de datos (BORRA todo) y carga los datos de prueba.
Uso:  python init_db.py
"""
from app import create_app
import database

app = create_app()
with app.app_context():
    database.init_db(con_datos_demo=True)
    print("Base de datos reiniciada con datos de prueba.")
