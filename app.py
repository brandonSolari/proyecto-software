"""Punto de entrada de Casero: fábrica de la aplicación Flask."""
import os

from flask import Flask, jsonify, request

import database
from config import Config
from services.errores import ErrorNegocio


def create_app(overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if overrides:
        app.config.update(overrides)

    app.teardown_appcontext(database.close_db)

    # Cada módulo funcional es un Blueprint independiente.
    from routes import paginas, auth, productos, favoritos, chat, admin
    for modulo in (paginas, auth, productos, favoritos, chat, admin):
        app.register_blueprint(modulo.bp)

    @app.errorhandler(ErrorNegocio)
    def error_negocio(e):
        return jsonify(error=e.mensaje), e.codigo

    @app.errorhandler(404)
    def no_encontrado(e):
        if request.path.startswith("/api/"):
            return jsonify(error="Recurso no encontrado."), 404
        return "Página no encontrada", 404

    # Primera ejecución: crea la base de datos con datos de prueba.
    if not os.path.exists(app.config["DATABASE"]):
        with app.app_context():
            database.init_db(con_datos_demo=True)

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
