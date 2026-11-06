"""Pruebas automáticas de la API de Casero.  Ejecutar:  python -m unittest -v"""
import os
import tempfile
import unittest

from app import create_app

CLAVE = "Casero123"


class CaseroApiTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        os.remove(self.tmp.name)  # create_app crea la BD si no existe
        self.app = create_app({"DATABASE": self.tmp.name, "TESTING": True})
        self.c = self.app.test_client()

    def tearDown(self):
        if os.path.exists(self.tmp.name):
            os.remove(self.tmp.name)

    # ---- utilidades ----------------------------------------------------
    def login(self, correo):
        r = self.c.post("/api/auth/login", json={"correo": correo, "password": CLAVE})
        self.assertEqual(r.status_code, 200)
        return {"Authorization": "Bearer " + r.get_json()["token"]}

    def producto_nuevo(self, **extra):
        datos = {"nombre": "Producto de prueba", "descripcion": "Descripción", "precio": 10,
                 "stock": 5, "categoria_id": 1}
        datos.update(extra)
        return datos

    # ---- RF01: autenticación -------------------------------------------
    def test_registro_comprador_y_correo_duplicado(self):
        datos = {"nombre": "Nuevo Cliente", "correo": "nuevo@correo.com", "password": "secreto1", "rol": "comprador"}
        r = self.c.post("/api/auth/registro", json=datos)
        self.assertEqual(r.status_code, 201)
        self.assertIn("token", r.get_json())
        self.assertEqual(self.c.post("/api/auth/registro", json=datos).status_code, 409)

    def test_registro_valida_datos(self):
        r = self.c.post("/api/auth/registro", json={"nombre": "Ab", "correo": "x", "password": "1", "rol": "comprador"})
        self.assertEqual(r.status_code, 400)
        r = self.c.post("/api/auth/registro", json={"nombre": "Vendedor Sin Negocio", "correo": "v@v.com",
                                                    "password": "secreto1", "rol": "vendedor"})
        self.assertEqual(r.status_code, 400)
        r = self.c.post("/api/auth/registro", json={"nombre": "Quiere Ser Admin", "correo": "a@a.com",
                                                    "password": "secreto1", "rol": "administrador"})
        self.assertEqual(r.status_code, 400)

    def test_login_correcto_e_incorrecto(self):
        self.login("alan@casero.bo")
        r = self.c.post("/api/auth/login", json={"correo": "alan@casero.bo", "password": "mala"})
        self.assertEqual(r.status_code, 401)

    def test_ruta_protegida_sin_token(self):
        self.assertEqual(self.c.get("/api/mis-productos").status_code, 401)
        self.assertEqual(self.c.get("/api/auth/yo", headers={"Authorization": "Bearer falso"}).status_code, 401)

    # ---- RF03 / RF04 / RF05: catálogo y búsqueda -----------------------
    def test_catalogo_publico_y_busqueda(self):
        todos = self.c.get("/api/productos").get_json()
        self.assertEqual(len(todos), 9)
        por_nombre = self.c.get("/api/productos?q=jarra").get_json()
        self.assertEqual([p["nombre"] for p in por_nombre], ["Jarra artesanal de cerámica"])
        por_categoria = self.c.get("/api/productos?categoria=3").get_json()
        self.assertTrue(all(p["categoria"] == "Gamer" for p in por_categoria))
        por_vendedor = self.c.get("/api/productos?vendedor=3").get_json()
        self.assertEqual(len(por_vendedor), 3)

    def test_detalle_y_no_encontrado(self):
        self.assertEqual(self.c.get("/api/productos/1").get_json()["vendedor"], "Tienda Carlos")
        self.assertEqual(self.c.get("/api/productos/999").status_code, 404)

    def test_disponibilidad_depende_del_stock(self):
        control = self.c.get("/api/productos/5").get_json()
        self.assertFalse(control["disponible"])
        h = self.login("carlos@casero.bo")
        r = self.c.patch("/api/productos/5/stock", json={"stock": 4}, headers=h)
        self.assertTrue(r.get_json()["disponible"])

    # ---- RF02 / RF03: gestión del vendedor -----------------------------
    def test_vendedor_crea_edita_y_elimina(self):
        h = self.login("luz@casero.bo")
        r = self.c.post("/api/productos", json=self.producto_nuevo(), headers=h)
        self.assertEqual(r.status_code, 201)
        pid = r.get_json()["id"]
        r = self.c.put(f"/api/productos/{pid}", json=self.producto_nuevo(nombre="Nombre editado", precio=25), headers=h)
        self.assertEqual(r.get_json()["precio"], 25)
        self.assertEqual(self.c.delete(f"/api/productos/{pid}", headers=h).status_code, 204)
        self.assertEqual(self.c.get(f"/api/productos/{pid}").status_code, 404)

    def test_validaciones_de_producto(self):
        h = self.login("luz@casero.bo")
        for malo in ({"precio": -5}, {"stock": -1}, {"nombre": "ab"}, {"categoria_id": 99}, {"precio": "abc"}):
            r = self.c.post("/api/productos", json=self.producto_nuevo(**malo), headers=h)
            self.assertEqual(r.status_code, 400, malo)

    def test_permisos_por_rol_y_propiedad(self):
        comprador = self.login("alan@casero.bo")
        self.assertEqual(self.c.post("/api/productos", json=self.producto_nuevo(), headers=comprador).status_code, 403)
        luz = self.login("luz@casero.bo")  # el producto 1 es de Carlos
        self.assertEqual(self.c.put("/api/productos/1", json=self.producto_nuevo(), headers=luz).status_code, 403)
        self.assertEqual(self.c.delete("/api/productos/1", headers=luz).status_code, 403)

    # ---- RF08: favoritos -----------------------------------------------
    def test_favoritos(self):
        h = self.login("ana@casero.bo")
        self.assertEqual(self.c.get("/api/favoritos", headers=h).get_json(), [])
        self.assertEqual(self.c.put("/api/favoritos/2", headers=h).status_code, 204)
        self.assertEqual(self.c.put("/api/favoritos/2", headers=h).status_code, 204)  # idempotente
        self.assertEqual([p["id"] for p in self.c.get("/api/favoritos", headers=h).get_json()], [2])
        self.c.delete("/api/favoritos/2", headers=h)
        self.assertEqual(self.c.get("/api/favoritos", headers=h).get_json(), [])
        self.assertEqual(self.c.put("/api/favoritos/999", headers=h).status_code, 404)

    # ---- RF06 / RF07: chat y respuestas automáticas --------------------
    def test_chat_con_respuesta_automatica_de_precio(self):
        h = self.login("ana@casero.bo")
        conv = self.c.post("/api/conversaciones", json={"vendedor_id": 2}, headers=h).get_json()["id"]
        r = self.c.post(f"/api/conversaciones/{conv}/mensajes",
                        json={"contenido": "¿Cuánto cuesta?", "producto_id": 1}, headers=h)
        msgs = r.get_json()["mensajes"]
        self.assertEqual(len(msgs), 2)
        self.assertEqual(msgs[1]["es_automatico"], 1)
        self.assertIn("Bs 380.00", msgs[1]["contenido"])

    def test_respuesta_automatica_de_disponibilidad_y_sin_regla(self):
        h = self.login("ana@casero.bo")
        conv = self.c.post("/api/conversaciones", json={"vendedor_id": 2}, headers=h).get_json()["id"]
        r = self.c.post(f"/api/conversaciones/{conv}/mensajes",
                        json={"contenido": "¿Tienen stock?", "producto_id": 5}, headers=h)
        self.assertIn("agotado", r.get_json()["mensajes"][1]["contenido"])
        r = self.c.post(f"/api/conversaciones/{conv}/mensajes",
                        json={"contenido": "Gracias, lo pienso", "producto_id": 5}, headers=h)
        self.assertEqual(len(r.get_json()["mensajes"]), 1)

    def test_conversacion_reutilizada_y_privada(self):
        h = self.login("alan@casero.bo")
        conv = self.c.post("/api/conversaciones", json={"vendedor_id": 2}, headers=h).get_json()["id"]
        self.assertEqual(conv, 1)  # Alan ya tenía conversación con Carlos
        ana = self.login("ana@casero.bo")
        self.assertEqual(self.c.get("/api/conversaciones/1/mensajes", headers=ana).status_code, 403)
        self.assertEqual(self.c.post("/api/conversaciones/1/mensajes", json={"contenido": "hola"}, headers=ana).status_code, 403)

    def test_vendedor_ve_y_responde_en_el_chat(self):
        h = self.login("carlos@casero.bo")
        self.assertEqual(len(self.c.get("/api/conversaciones", headers=h).get_json()), 1)
        r = self.c.post("/api/conversaciones/1/mensajes", json={"contenido": "Te espero mañana"}, headers=h)
        self.assertEqual(r.status_code, 201)
        nuevos = self.c.get("/api/conversaciones/1/mensajes?desde=2", headers=h).get_json()
        self.assertEqual([m["contenido"] for m in nuevos], ["Te espero mañana"])

    def test_mensaje_vacio_o_muy_largo(self):
        h = self.login("alan@casero.bo")
        self.assertEqual(self.c.post("/api/conversaciones/1/mensajes", json={"contenido": "  "}, headers=h).status_code, 400)
        self.assertEqual(self.c.post("/api/conversaciones/1/mensajes", json={"contenido": "x" * 501}, headers=h).status_code, 400)

    # ---- Administración ------------------------------------------------
    def test_admin_desactiva_vendedor(self):
        admin = self.login("admin@casero.bo")
        self.assertEqual(len(self.c.get("/api/admin/usuarios", headers=admin).get_json()), 5)
        self.assertEqual(self.c.patch("/api/admin/usuarios/3/estado", json={"activo": False}, headers=admin).status_code, 204)
        self.assertEqual(len(self.c.get("/api/productos").get_json()), 6)  # los 3 de Luz se ocultan
        r = self.c.post("/api/auth/login", json={"correo": "luz@casero.bo", "password": CLAVE})
        self.assertEqual(r.status_code, 403)
        self.assertEqual(self.c.patch("/api/admin/usuarios/1/estado", json={"activo": False}, headers=admin).status_code, 400)

    def test_admin_solo_para_administradores(self):
        h = self.login("alan@casero.bo")
        self.assertEqual(self.c.get("/api/admin/usuarios", headers=h).status_code, 403)

    def test_contrasena_no_se_expone(self):
        r = self.c.post("/api/auth/login", json={"correo": "alan@casero.bo", "password": CLAVE})
        self.assertNotIn("password", str(r.get_json()))


if __name__ == "__main__":
    unittest.main()
