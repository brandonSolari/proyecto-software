"""Páginas HTML (capa de presentación). Los datos llegan desde la API REST."""
from flask import Blueprint, render_template

bp = Blueprint("paginas", __name__)


@bp.get("/")
def inicio():
    return render_template("index.html")


@bp.get("/producto/<int:producto_id>")
def producto(producto_id):
    return render_template("producto.html", producto_id=producto_id)


@bp.get("/login")
def login():
    return render_template("login.html")


@bp.get("/registro")
def registro():
    return render_template("registro.html")


@bp.get("/panel")
def panel():
    return render_template("panel.html")


@bp.get("/favoritos")
def favoritos():
    return render_template("favoritos.html")


@bp.get("/chat")
def chat():
    return render_template("chat.html")


@bp.get("/admin")
def admin():
    return render_template("admin.html")
