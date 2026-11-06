/* Casero · utilidades compartidas del frontend */
const Sesion = {
  token() { return localStorage.getItem("casero_token"); },
  usuario() {
    try { return JSON.parse(localStorage.getItem("casero_usuario")); } catch (e) { return null; }
  },
  guardar(token, usuario) {
    localStorage.setItem("casero_token", token);
    localStorage.setItem("casero_usuario", JSON.stringify(usuario));
  },
  limpiar() {
    localStorage.removeItem("casero_token");
    localStorage.removeItem("casero_usuario");
  },
  cerrar() { Sesion.limpiar(); location.href = "/"; },
};

/* Llamada a la API REST; agrega el token JWT si hay sesión. */
async function api(metodo, ruta, cuerpo) {
  const cabeceras = { "Content-Type": "application/json" };
  if (Sesion.token()) cabeceras["Authorization"] = "Bearer " + Sesion.token();
  const resp = await fetch("/api" + ruta, {
    method: metodo,
    headers: cabeceras,
    body: cuerpo ? JSON.stringify(cuerpo) : undefined,
  });
  let datos = null;
  if (resp.status !== 204) {
    try { datos = await resp.json(); } catch (e) { datos = null; }
  }
  if (!resp.ok) {
    if (resp.status === 401 && Sesion.token() && !ruta.startsWith("/auth/login")) {
      Sesion.limpiar();
      location.href = "/login";
    }
    throw new Error((datos && datos.error) || "Error " + resp.status);
  }
  return datos;
}

/* Escapa texto antes de insertarlo como HTML (evita XSS). */
function esc(valor) {
  return String(valor ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function bs(n) { return "Bs " + Number(n).toFixed(2); }

function aviso(texto, malo = false) {
  const el = document.getElementById("aviso");
  el.textContent = texto;
  el.className = "aviso" + (malo ? " mal" : "");
  el.hidden = false;
  clearTimeout(aviso.t);
  aviso.t = setTimeout(() => { el.hidden = true; }, 3000);
}

/* Redirige al login si no hay sesión o el rol no corresponde. */
function exigirRol(...roles) {
  const u = Sesion.usuario();
  if (!u || !Sesion.token()) { location.href = "/login"; return null; }
  if (!roles.includes(u.rol)) { location.href = "/"; return null; }
  return u;
}

function renderNav() {
  const u = Sesion.usuario();
  const enlaces = [["/", "Inicio"]];
  if (u && u.rol === "comprador") enlaces.push(["/favoritos", "Favoritos"], ["/chat", "Mensajes"]);
  if (u && u.rol === "vendedor") enlaces.push(["/panel", "Mi panel"], ["/chat", "Mensajes"]);
  if (u && u.rol === "administrador") enlaces.push(["/admin", "Usuarios"]);
  let html = enlaces.map(([ruta, texto]) =>
    `<a href="${ruta}" class="${location.pathname === ruta ? "activo" : ""}">${texto}</a>`).join("");
  if (u) {
    html += `<span class="saludo">Hola, ${esc(u.nombre.split(" ")[0])}</span>` +
            `<button class="btn-link" id="btn-salir">Salir</button>`;
  } else {
    html += '<a href="/login">Iniciar sesión</a><a href="/registro" class="btn btn-sm">Crear cuenta</a>';
  }
  document.getElementById("nav").innerHTML = html;
  const salir = document.getElementById("btn-salir");
  if (salir) salir.addEventListener("click", Sesion.cerrar);
  const q = new URLSearchParams(location.search).get("q");
  if (q) document.getElementById("q-global").value = q;
}

const EMOJI = { "Hogar": "🏠", "Ropa": "👕", "Gamer": "🎮", "Artesanías": "🧺", "Electrónica": "🔌" };

function imagenProducto(p) {
  if (p.imagen_url) return `<img src="${esc(p.imagen_url)}" alt="${esc(p.nombre)}" loading="lazy">`;
  return `<div class="img-vacia">${EMOJI[p.categoria] || "📦"}</div>`;
}

function etiquetaEstado(p) {
  return p.disponible ? '<span class="estado ok">Disponible</span>' : '<span class="estado no">Agotado</span>';
}

function tarjetaProducto(p, esFavorito, conCorazon) {
  const corazon = conCorazon
    ? `<button class="fav ${esFavorito ? "activo" : ""}" data-id="${p.id}" title="Favorito" aria-label="Favorito">♥</button>` : "";
  return `<article class="tarjeta">
    <a class="tarjeta-img" href="/producto/${p.id}">${imagenProducto(p)}</a>
    <div class="tarjeta-cuerpo">
      <h3><a href="/producto/${p.id}">${esc(p.nombre)}</a></h3>
      <p class="vendedor">${esc(p.vendedor)}</p>
      <div class="tarjeta-pie"><span class="precio">${bs(p.precio)}</span>${etiquetaEstado(p)}</div>
    </div>${corazon}</article>`;
}

/* Alterna favorito (PUT/DELETE). Devuelve el nuevo estado. */
async function alternarFavorito(boton) {
  if (!Sesion.token()) { location.href = "/login"; return null; }
  const activo = boton.classList.contains("activo");
  await api(activo ? "DELETE" : "PUT", "/favoritos/" + boton.dataset.id);
  boton.classList.toggle("activo", !activo);
  aviso(activo ? "Quitado de favoritos" : "Guardado en favoritos");
  return !activo;
}
