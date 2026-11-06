"""Lógica de negocio: registro, autenticación y administración de usuarios."""
import re

from repositories import usuarios as repo
from services import seguridad
from services.errores import ErrorNegocio

CORREO_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def publico(u):
    """Datos del usuario que sí se pueden enviar al navegador (sin el hash)."""
    return {k: u[k] for k in ("id", "nombre", "correo", "rol", "nombre_negocio")}


def registrar(datos):
    nombre = (datos.get("nombre") or "").strip()
    correo = (datos.get("correo") or "").strip().lower()
    password = datos.get("password") or ""
    rol = datos.get("rol")
    negocio = (datos.get("nombre_negocio") or "").strip() or None

    if len(nombre) < 3:
        raise ErrorNegocio("El nombre debe tener al menos 3 caracteres.")
    if not CORREO_RE.match(correo):
        raise ErrorNegocio("El correo no es válido.")
    if len(password) < 6:
        raise ErrorNegocio("La contraseña debe tener al menos 6 caracteres.")
    if rol not in ("comprador", "vendedor"):
        raise ErrorNegocio("Rol no permitido.")
    if rol == "vendedor" and not negocio:
        raise ErrorNegocio("El vendedor debe indicar el nombre de su negocio.")
    if repo.obtener_por_correo(correo):
        raise ErrorNegocio("Ya existe una cuenta con ese correo.", 409)

    nuevo_id = repo.crear(nombre, correo, seguridad.hashear(password), rol, negocio if rol == "vendedor" else None)
    return repo.obtener(nuevo_id)


def autenticar(correo, password):
    usuario = repo.obtener_por_correo((correo or "").strip().lower())
    if not usuario or not seguridad.verificar(usuario["password_hash"], password or ""):
        raise ErrorNegocio("Correo o contraseña incorrectos.", 401)
    if not usuario["activo"]:
        raise ErrorNegocio("Tu cuenta está desactivada.", 403)
    return usuario


def listar_vendedores(texto=None):
    return repo.listar_vendedores(texto)


def listar_para_admin():
    return repo.listar_todos()


def cambiar_estado(admin, usuario_id, activo):
    destino = repo.obtener(usuario_id)
    if not destino:
        raise ErrorNegocio("Usuario no encontrado.", 404)
    if destino["id"] == admin["id"]:
        raise ErrorNegocio("No puedes desactivar tu propia cuenta.", 400)
    repo.cambiar_estado(usuario_id, bool(activo))
