import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Configuración central del sistema Casero."""
    SECRET_KEY = os.environ.get("CASERO_SECRET", "casero-clave-de-desarrollo-cambiar-en-produccion-2026")
    DATABASE = os.environ.get("CASERO_DB", os.path.join(BASE_DIR, "casero.db"))
    JWT_HORAS = 8
