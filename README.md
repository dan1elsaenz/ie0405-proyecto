# ie0405: Proyecto final

Este repositorio corresponde al proyecto final del curso IE0405: Modelos probabilísticos de señales y sistemas.
En este se realizó el análisis estadístico de una serie de datos obtenidos a partir de un _broker_ MQTT proporcionado por el profesor.
A partir de estos, se modeló el tiempo entre los datos (_interarrival times_) como un proceso de Poisson para analizar la frecuencia con la que estos llegaban.

> Para acceder a la documentación realizada, ingrese a [este enlace](https://dan1elsaenz.github.io/ie0405-proyecto/).

## Instrucciones de ejecución

A continuación, se muestra cómo realizar la ejecución del código fuente desarrollado y el acceso a la documentación de forma local.

### Instalar `uv`

Seguir las [instrucciones de instalación](https://docs.astral.sh/uv/getting-started/installation/) de `uv` según el sistema operativo.
Luego, seguir los primeros pasos de configuración, incluyendo la instalación de una versión de Python con `uv python install`.

> [!IMPORTANT]
> La versión de Python instalada con `uv` no estará disponible localmente. En cambio, ahora es necesario ejecutar comandos como `uv run python` para abrir la línea de comandos interactiva o `uv run python [script.py]` para ejecutar un archivo.

### Crear un ambiente virtual de Python con `uv`

En una terminal, en el directorio raíz del repositorio, utilizar:

```bash
uv sync
```

Esto creará un ambiente virtual (directorio `.venv/`) e instalará las dependencias indicadas en `pyproject.toml`.

#### Instalación o remoción de paquetes

Para ser ejecutado correctamente, cada vez que un paquete nuevo sea utilizado debe ser agregado con `uv` al ambiente virtual usando:

```sh
uv add [nombre-del-paquete]
```

y para eliminarlo:

```sh
uv remove [nombre-del-paquete]
```

### Para visualizar la documentación

En una terminal, en el directorio raíz del repositorio, utilizar:

```bash
uv run mkdocs serve
```

Abrir en un navegador web la página del "servidor local" en el puerto 8000, en [http://127.0.0.1:8000/](http://127.0.0.1:8000/) o en [http://localhost:8000/](http://localhost:8000/).

Cada cambio en los documentos de la carpeta `docs/` o en el archivo `mkdocs.yml` genera un _refresh_ de la página.

### Para ejecutar el proyecto

> Ejecute los comandos desde la raíz del repositorio.

1. Copiar los contenidos del archivo `.env.example` en otro archivo `.env` y modificar los valores necesarios.
2. Para ejecutar el script para la obtención de datos vía el tópico MQTT:

```sh
uv run src/client.py
```

3. Para el script de análisis de los datos, utilice:

```sh
uv run src/analysis.py
```
