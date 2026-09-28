# Simulador CLI de Docker

Se realizo un simulador interactivo de terminal para Docker, desarrollado en Python.

Paso a paso

Inicialmente se hizo la creación de un repositorio publico con el nombre de simulador-docker-cli

Se realizo el registro de el usuario global y el email global

Se inicializo el repositorio local en la terminal, se crearón los archivos .gitignore, README.md y simulador.py

Para el desarrollo del simulador Estructuré la CLI implementando un bucle interactivo con shlex para procesar los comandos respetando comillas, un diccionario para mapear las funciones sin saturar de if/else, y el estado en memoria para gestionar imágenes y contenedores.

El primer comando fue run, así que escribí generar_id() con random.choices y reintento en caso de colisión, nombre_existe() para validar unicidad, y la creación de la entrada con estado Up. Para poder ver lo creado agregué ps con tabla alineada a ancho fijo.

Luego vino pull, y antes de escribirlo agregue normalizar_imagen() para que nginx y nginx:latest no quedaran duplicadas. Dentro del comando puse la verificación de duplicados, la simulación de capas y un digest con hashlib.sha256 a partir del nombre. Agregué images separando repo y tag con rsplit(':', 1), y conecté run con pull para descargar automáticamente si la imagen no estaba en local.

Con stop, rm y logs extraje resolver_contenedor(ref) para no repetir la lógica de aceptar ID o nombre tres veces. Metí generar_logs_simulados() con timestamps RFC3339 consecutivos, y guardé los logs dentro del propio dict del contenedor para que sobrevivieran al stop y desaparecieran con el rm. stop cambia el estado y añade una línea de SIGTERM, rm valida que esté Exited antes de borrar, y logs imprime la lista.

Al final corregí ps: sin flags debía mostrar solo los Up y con -a/--all incluir los Exited. Filtré con list comprehension, di error con flags desconocidos y extraje el formateo a imprimir_tabla_ps() porque la llamaba con dos conjuntos distintos. Cerré actualizando help.

Se realizarón un total de 5 commits descriptivos en cada paso previamente mencionado

Finalmente de genero el push a la rama main de github.com/MelodiasGrey/simulador-docker-cli

Diccionario de terminos:

    CLI = Command Line Interface (Interfaz de Línea de Comandos), un mecanismo de software que permite interactuar con el sistema operativo mediante la escritura de comandos de texto en lugar de usar elementos gráficos.

    Docker = Plataforma de código abierto que permite a los desarrolladores crear, implementar y ejecutar aplicaciones utilizando contenedores.

## Integrantes

- [Jorge Romero]
- [Nombre de mi compañero: Deepseek, Gemini, Copilot, ChatGPT, OpenCode, ClaudeCode, Delcy Rodriguez, Corpoelec, Maria corina Machado, Simon Bolivar, Las bolas del dragon, El buen Buey, Frutipipa tropical, Maltin polar vida y mas na, Maracaibo es la pepa del queso]
- [Hola]

## Instrucciones de Ejecución

```bash
python3 simulador.py
```
