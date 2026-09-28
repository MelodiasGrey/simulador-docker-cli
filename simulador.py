#!/usr/bin/env python3
"""
Simulador básico de Docker en consola.
Comandos soportados: pull, images, run, ps, stop, rm, logs, help, exit/quit
"""

import random
import string
import hashlib
import time
import shlex
from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# Estructura de datos en memoria
# ---------------------------------------------------------------------------
contenedores = {}          # {id: {nombre, imagen, estado, logs: [str]}}
imagenes_descargadas = []  # lista de nombres de imágenes descargadas (con tag)


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def generar_id():
    """Genera un ID aleatorio único de 6 caracteres alfanuméricos."""
    while True:
        nuevo_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        if nuevo_id not in contenedores:
            return nuevo_id


def nombre_existe(nombre):
    """Comprueba si ya existe un contenedor con ese nombre."""
    return any(c['nombre'] == nombre for c in contenedores.values())


def normalizar_imagen(imagen):
    """Añade ':latest' si el usuario no especifica tag."""
    return imagen if ':' in imagen else f"{imagen}:latest"


def resolver_contenedor(ref):
    """
    Dado un ID o un nombre, devuelve (id, info) del contenedor o (None, None).
    Primero busca por ID exacto, luego por nombre.
    """
    if ref in contenedores:
        return ref, contenedores[ref]
    for cid, info in contenedores.items():
        if info['nombre'] == ref:
            return cid, info
    return None, None


def generar_logs_simulados(nombre, imagen):
    """
    Genera una lista de líneas de log ficticias pero realistas,
    con timestamps consecutivos.
    """
    base = datetime.now() - timedelta(seconds=random.randint(10, 300))
    eventos = [
        f"Starting {imagen}...",
        "Initializing application",
        "Loading configuration from /etc/app/config.yml",
        "Connecting to database...",
        "Database connection established",
        f"Service '{nombre}' listening on port 8080",
        "Health check endpoint ready at /healthz",
    ]
    lineas = []
    for i, ev in enumerate(eventos):
        ts = base + timedelta(seconds=i * random.uniform(0.3, 1.5))
        lineas.append(f"{ts.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z {ev}")
    return lineas


# ---------------------------------------------------------------------------
# Comandos
# ---------------------------------------------------------------------------

def cmd_pull(args):
    """Simula 'docker pull <imagen>'."""
    if len(args) != 1:
        print("Uso: pull <imagen[:tag]>")
        return

    imagen = normalizar_imagen(args[0])

    if imagen in imagenes_descargadas:
        print(f"Status: Image is up to date for {imagen}")
        return

    print(f"Pulling from {imagen.split(':')[0]}")
    digest = hashlib.sha256(imagen.encode()).hexdigest()

    for capa in ['a1b2c3d4e5f6', 'b2c3d4e5f6a1', 'c3d4e5f6a1b2']:
        print(f"{capa}: Downloading...")
        time.sleep(0.2)
        print(f"{capa}: Download complete")

    print(f"Digest: sha256:{digest}")
    print(f"Status: Downloaded newer image for {imagen}")

    imagenes_descargadas.append(imagen)


def cmd_images(_args=None):
    """Simula 'docker images'."""
    print(f"{'REPOSITORY':<25}{'TAG':<15}")
    for img in imagenes_descargadas:
        repo, tag = img.rsplit(':', 1)
        print(f"{repo:<25}{tag:<15}")


def cmd_run(args):
    """Simula 'docker run [opciones] <imagen>'."""
    if not args:
        print("Uso: run [--name <nombre>] [-p <puertos>] [-v <volumenes>] <imagen[:tag]>")
        return

    nombre = None
    puertos = None
    volumenes = None
    imagen = None

    i = 0
    while i < len(args):
        if args[i] == '--name' and i + 1 < len(args):
            nombre = args[i + 1]
            i += 2
        elif args[i] == '-p' and i + 1 < len(args):
            puertos = args[i + 1]
            i += 2
        elif args[i] == '-v' and i + 1 < len(args):
            volumenes = args[i + 1]
            i += 2
        elif imagen is None:
            imagen = args[i]
            i += 1
        else:
            print(f"Argumento no reconocido: {args[i]}")
            return

    if not imagen:
        print("Error: debes especificar una imagen")
        return

    imagen = normalizar_imagen(imagen)

    if nombre and nombre_existe(nombre):
        print(f"Error: ya existe un contenedor con el nombre '{nombre}'.")
        return

    # --- IMPORTANTE: hacer el pull ANTES de crear el contenedor ---
    if imagen not in imagenes_descargadas:
        print(f"Unable to find image '{imagen}' locally")
        cmd_pull([imagen])
        print()   # ← salto de línea extra para separar visualmente

    cid = generar_id()

    if not nombre:
        nombre = f"container_{cid}"

    contenedores[cid] = {
        'nombre': nombre,
        'imagen': imagen,
        'estado': 'Up',
        'puertos': puertos,
        'volumenes': volumenes,
        'logs': generar_logs_simulados(nombre, imagen),
    }

    print(cid, flush=True)   # ← flush explícito


def cmd_ps(_args=None):
    """Simula 'docker ps'."""
    print(f"{'CONTAINER ID':<14}{'NAME':<22}{'IMAGE':<22}{'STATUS':<8}{'PORTS':<15}{'VOLUMES'}")
    for cid, info in contenedores.items():
        puertos = info.get('puertos') or '-'
        volumenes = info.get('volumenes') or '-'
        print(f"{cid:<14}{info['nombre']:<22}{info['imagen']:<22}{info['estado']:<8}{puertos:<15}{volumenes}")

def cmd_stop(args):
    """
    Simula 'docker stop <id|nombre>'.
    Cambia el estado de 'Up' a 'Exited'.
    """
    if len(args) != 1:
        print("Uso: stop <id|nombre>")
        return

    cid, info = resolver_contenedor(args[0])
    if info is None:
        print(f"Error: no such container: {args[0]}")
        return

    if info['estado'] == 'Exited':
        print(f"Contenedor '{info['nombre']}' ya está detenido.")
        return

    info['estado'] = 'Exited'
    info['logs'].append(
        f"{datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z "
        f"Received SIGTERM, shutting down gracefully..."
    )
    print(info['nombre'])


def cmd_rm(args):
    """
    Simula 'docker rm <id|nombre>'.
    Solo permite eliminar contenedores en estado 'Exited'.
    """
    if len(args) != 1:
        print("Uso: rm <id|nombre>")
        return

    cid, info = resolver_contenedor(args[0])
    if info is None:
        print(f"Error: no such container: {args[0]}")
        return

    if info['estado'] == 'Up':
        print(
            f"Error: cannot remove container '{info['nombre']}' "
            f"because it is running. Stop it first."
        )
        return

    del contenedores[cid]
    print(info['nombre'])


def cmd_logs(args):
    """
    Simula 'docker logs <id|nombre>'.
    Muestra los mensajes de log almacenados para el contenedor.
    """
    if len(args) != 1:
        print("Uso: logs <id|nombre>")
        return

    _cid, info = resolver_contenedor(args[0])
    if info is None:
        print(f"Error: no such container: {args[0]}")
        return

    for linea in info['logs']:
        print(linea)


def cmd_help(_args=None):
    """Muestra la ayuda disponible."""
    print("Comandos disponibles:")
    print("  pull <imagen[:tag]>        Descarga una imagen al registro local")
    print("  images                     Lista las imágenes descargadas")
    print("  run <nombre> <imagen>      Crea y arranca un contenedor")
    print("  ps                         Lista los contenedores")
    print("  stop <id|nombre>           Detiene un contenedor (Up -> Exited)")
    print("  rm <id|nombre>             Elimina un contenedor detenido")
    print("  logs <id|nombre>           Muestra los logs de un contenedor")
    print("  help                       Muestra esta ayuda")
    print("  exit | quit                Salir del simulador")


# Mapa de comandos -> función manejadora
COMANDOS = {
    'pull': cmd_pull,
    'images': cmd_images,
    'run': cmd_run,
    'ps': cmd_ps,
    'stop': cmd_stop,
    'rm': cmd_rm,
    'logs': cmd_logs,
    'help': cmd_help,
}


# ---------------------------------------------------------------------------
# Bucle principal
# ---------------------------------------------------------------------------

def bucle_principal():
    """Bucle interactivo del prompt 'docker>'."""
    print("Simulador Docker (escribe 'help' para ver comandos, 'exit' para salir)\n")

    while True:
        try:
            linea = input("docker> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not linea:
            continue

        try:
            partes = shlex.split(linea)
        except ValueError as e:
            print(f"Error de sintaxis: {e}")
            continue

        comando, *args = partes

        if comando in ('exit', 'quit'):
            print("Saliendo del simulador...")
            break

        manejador = COMANDOS.get(comando)
        if manejador is None:
            print(f"Comando desconocido: '{comando}'. Escribe 'help' para ayuda.")
            continue

        manejador(args)


if __name__ == '__main__':
    bucle_principal()