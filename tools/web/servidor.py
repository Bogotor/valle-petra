"""Servidor local que imita a Cloudflare Pages: sirve site/ y aplica site/_headers.

Uso: python3 tools/web/servidor.py [--puerto 8766]

Sirve solo en 127.0.0.1 (no queda expuesto en tu red). Sirve para probar las
cabeceras de seguridad, sobre todo la Content-Security-Policy, antes de publicar:
si algo queda bloqueado, el navegador lo avisa en la consola.

Entiende el subconjunto de _headers que usa el sitio: una ruta por línea (exacta
o con *) y, debajo, líneas con sangría "Nombre: valor". Como Cloudflare, no sirve
el propio archivo _headers.
"""
import argparse
import fnmatch
import functools
import http.server
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITIO = os.path.join(RAIZ, "site")


def leer_reglas(ruta):
    """Devuelve [(patrón, [(cabecera, valor), ...]), ...] en el orden del archivo."""
    reglas = []
    with open(ruta, encoding="utf-8") as fh:
        for linea in fh:
            if not linea.strip() or linea.lstrip().startswith("#"):
                continue
            if not linea[0].isspace():
                reglas.append((linea.strip(), []))
            elif reglas:
                nombre, _, valor = linea.strip().partition(":")
                reglas[-1][1].append((nombre.strip(), valor.strip()))
    return reglas


class Manejador(http.server.SimpleHTTPRequestHandler):
    reglas = []

    def ruta(self):
        return self.path.split("?", 1)[0].split("#", 1)[0]

    def send_head(self):
        if os.path.basename(self.ruta()) == "_headers":
            self.send_error(404)
            return None
        return super().send_head()

    def end_headers(self):
        for patron, cabeceras in self.reglas:
            if fnmatch.fnmatchcase(self.ruta(), patron):
                for nombre, valor in cabeceras:
                    self.send_header(nombre, valor)
        super().end_headers()


def main():
    p = argparse.ArgumentParser(description="Sirve site/ con las cabeceras de site/_headers.")
    p.add_argument("--puerto", type=int, default=8766)
    a = p.parse_args()

    Manejador.reglas = leer_reglas(os.path.join(SITIO, "_headers"))
    manejador = functools.partial(Manejador, directory=SITIO)
    with http.server.ThreadingHTTPServer(("127.0.0.1", a.puerto), manejador) as servidor:
        print(f"http://127.0.0.1:{a.puerto}/  ({len(Manejador.reglas)} reglas de _headers)", flush=True)
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
