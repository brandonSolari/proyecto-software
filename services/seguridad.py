"""Seguridad: hash de contraseñas, tokens JWT y control de acceso por rol."""
import datetime
from functools import wraps

import jwt
from flask import current_app, g, request
from werkzeug.security import generate_password_hash, check_password_hash

from repositories import usuarios as repo_usuarios
from services.errores import ErrorNegocio


def hashear(password):
    return generate_password_hash(password, method="pbkdf2:sha256")


def verificar(password_hash, password):
    return check_password_hash(password_hash, password)


def crear_token(usuario):
    ahora = datetime.datetime.now(datetime.timezone.utc)
    carga = {
        "sub": str(usuario["id"]),
        "rol": usuario["rol"],
        "iat": ahora,
        "exp": ahora + datetime.timedelta(hours=current_app.config["JWT_HORAS"]),
    }
    return jwt.encode(carga, current_app.config["SECRET_KEY"], algorithm="HS256")


def _usuario_desde_token():
    cabecera = request.headers.get("Authorization", "")
    if not cabecera.startswith("Bearer "):
        return None
    try:
        datos = jwt.decode(cabecera[7:], current_app.config["SECRET_KEY"], algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    usuario = repo_usuarios.obtener(int(datos["sub"]))
    return usuario if usuario and usuario["activo"] else None


def login_required(funcion):
    """Decorador: exige un token JWT válido y deja el usuario en g.usuario."""
    @wraps(funcion)
    def envoltura(*args, **kwargs):
        usuario = _usuario_desde_token()
        if usuario is None:
            raise ErrorNegocio("Debes iniciar sesión.", 401)
        g.usuario = usuario
        return funcion(*args, **kwargs)
    return envoltura


def rol_requerido(*roles):
    """Decorador: además de iniciar sesión, exige uno de los roles indicados."""
    def decorador(funcion):
        @wraps(funcion)
        @login_required
        def envoltura(*args, **kwargs):
            if g.usuario["rol"] not in roles:
                raise ErrorNegocio("No tienes permiso para esta acción.", 403)
            return funcion(*args, **kwargs)
        return envoltura
    return decorador
