# Casero

Plataforma web para que compradores y vendedores de pequeños negocios se comuniquen
en un solo lugar: catálogo, inventario, favoritos y chat interno con respuestas rápidas.

**Tecnologías:** Python · Flask · SQLite · PyJWT · HTML/CSS/JavaScript

## Cómo ejecutarlo (Windows)

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abrir en el navegador: http://127.0.0.1:5000

La primera vez se crea solo el archivo `casero.db` con datos de prueba.
Para reiniciar la base de datos: `python init_db.py`

## Cuentas de prueba (clave de todas: `Casero123`)

| Rol            | Correo             |
|----------------|--------------------|
| Administrador  | admin@casero.bo    |
| Vendedor       | carlos@casero.bo   |
| Vendedor       | luz@casero.bo      |
| Comprador      | alan@casero.bo     |
| Comprador      | ana@casero.bo      |

## Pruebas automáticas

```
python -m unittest -v
```

## Estructura

```
casero/
├── app.py            # fábrica de la aplicación (create_app)
├── config.py         # configuración
├── database.py       # conexión SQLite y helpers
├── schema.sql        # script de creación de la base de datos
├── seed.py           # datos de prueba
├── init_db.py        # reinicia la base de datos
├── routes/           # capa API REST (Blueprints) y páginas
├── services/         # capa de lógica de negocio
├── repositories/     # capa de acceso a datos (SQL)
├── templates/        # páginas HTML (Jinja2)
├── static/           # CSS y JavaScript
└── tests/            # pruebas automáticas
```
