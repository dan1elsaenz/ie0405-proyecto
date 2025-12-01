# Instrucciones para la ejecución del código

En esta sección, se describen los pasos a seguir para la ejecución del programa desarrollado para el proyecto.

> Para la ejecución del código localmente, asegúrese de tener instalado WSL (en caso de trabajar en Windows).

## Clonar repositorio

Utilice el comando:

```sh
git clone https://github.com/improbabilidades/proyecto-dan1elsaenz.git  # (1)!
```

1. O cualquier alternativa si utiliza SSH o GitHub CLI.

## Instalación de paquetes con `uv`

En la raíz del repositorio:

```
uv sync
```

!!! info "En caso de error por dependencia..."

    En caso de requerir agregar algún paquete, utilice:

    ```
    uv add <nombre_paquete>
    ```

    > Es posible que `Fitter` no se haya instalado, entonces puede utilizarlo para este paquete, pero idealmente no debería pasar.

## Configuración de entorno virtual

En el archivo `.venv`, debe colocar el siguiente contenido utilizado en el caso personal:

```sh
MQTT_HOST=mqtt.simovi.org
MQTT_PORT=1883
MQTT_USER=admin
MQTT_PASS=admin
MQTT_TOPIC=C37099 # (1)!
DATABASE_URL=sqlite:///events.db
```

1. Carné estudiantil

## Ejecución del código

!!! abstract "Sobre la dirección de ejecución"

    Ejecute todos los comandos desde la raíz del repositorio.

Para ejecutar el cliente usado para la recolección de datos:

```sh
uv run src/client.py
```

Para ejecutar el código de análisis con la base de datos `events.db`:

```sh
uv run src/analysis.py
```

---

# Estructura del proyecto

Los archivos de código (`.py`) principales son los siguientes:

### `analysis.py`

Este módulo realiza el análisis estadístico de los tiempos entre eventos recibidos vía MQTT.
Extrae *timestamps* desde una base de datos, calcula los intervalos entre eventos, calcula momentos experimentales, ajusta distribuciones de probabilidad usando *Fitter*, calcula momentos teóricos y produce histogramas.

#### `load_time_between_data(...)`

Carga *timestamps* desde la base de datos, los ordena y calcula los intervalos entre eventos en segundos.
Valida errores comunes: tabla vacía, columna no existente, poca cantidad de datos o errores de conexión.

#### `compute_descriptive_stats(...)`

Recibe un arreglo con los tiempos entre eventos y devuelve estadísticas como media, mediana, desviación estándar, cuartiles, inclinación y kurtosis.

#### `fit_candidate_distributions(...)`

Utiliza `Fitter` para evaluar múltiples distribuciones de probabilidad y seleccionar la de menor error cuadrático.
Devuelve el nombre de la distribución y sus parámetros ajustados.

#### `compute_model_moments(...)`

Calcula los momentos teóricos (media, varianza, desviación estándar, inclinación, kurtosis) del modelo elegido usando `scipy.stats`.

#### `_freedman_diaconis_bins(...)`

Implementa la regla de *Freedman–Diaconis* para determinar el número adecuado de *bins* de un histograma.

#### `plot_histograma_datos(...)`

Genera un histograma con estilo clásico y lo exporta como archivo `svg` en la ruta especificada.

#### `plot_histograma_mejor_ajuste(...)`

Superpone la función de densidad (*PDF*) de la distribución ajustada sobre el histograma, para visualizar el ajuste realizado.

#### `_print_descriptive_stats_table(...)`

Imprime en la terminal una tabla con las estadísticas descriptivas calculadas.

#### `_print_comparison_table(...)`

Compara los momentos experimentales con los del modelo teórico.

#### `_check_sqlite_file(...)`

Verifica que exista el archivo de la base de datos cuando la URL utiliza el prefijo `sqlite:///`.

#### `main()`

Función principal que:

- Carga la configuración desde archivo `.env`
- Extrae los datos desde la base
- Calcula estadísticas experimentales
- Ajusta distribuciones mediante `Fitter`
- Calcula momentos teóricos
- Genera histogramas en formato `svg`
- Muestra resumen para distribución `expon`

### `client.py`

Este módulo implementa un suscriptor MQTT que escucha mensajes en un tópico definido mediante variables de entorno y almacena eventos válidos en una base de datos.
Maneja reconexión automática, ciclo principal y el registro usando `SQLAlchemy`.

#### Variables de entorno

- `MQTT_HOST`
- `MQTT_PORT`
- `MQTT_USER`
- `MQTT_PASS`
- `MQTT_TOPIC`

Estas variables configuran la conexión al *broker* MQTT y el tópico al que suscribirse.

#### `on_connect(client, rc)`

*Callback* ejecutado al conectar con el *broker*.  
Si `rc == 0`, se suscribe al tópico definido; de lo contrario, registra un error.

#### `on_message(msg)`

Procesa un mensaje recibido:

- Decodifica el mensaje (UTF-8 o Latin-1)
- Intenta parsearlo como `json`
- Si contiene `first_name` y `last_name`, registra el evento en la base de datos con *timestamp*
- Maneja excepciones con `logging`

#### `on_disconnect(rc)`

Distingue entre desconexión esperada (`rc == 0`) e inesperada.
Registra el estado correspondiente en el *logger*.

#### `main()`

Configura y ejecuta el suscriptor MQTT:

- Crea un identificador único para el cliente (*client ID*)
- Configura credenciales y _callbacks_
- Implementa reintentos de conexión
- Ejecuta el ciclo principal `client.loop_forever()`
- Permite detener el servicio con `Ctrl+C`

### `models.py`

Este módulo define el modelo ORM utilizado para almacenar eventos recibidos vía MQTT.
Configura la conexión a la base de datos mediante `SQLAlchemy`, gestiona la sesión y crea automáticamente las tablas si no existen.

#### `class Base(DeclarativeBase)`

Clase base que define el comportamiento de los modelos ORM.

#### `database_url`

Variable que contiene la URL de conexión a la base de datos, extraída desde `.env` o por defecto `sqlite:///events.db`.

#### `class Event(Base)`

Modelo ORM correspondiente a la tabla `event`.
Contiene los siguientes campos:

- `id`: llave primaria autoincremental
- `topic`: tópico MQTT donde se recibió el mensaje
- `first_name`: nombre recibido
- `last_name`: apellido recibido
- `timestamp`: instante en que se recibió el evento

---

Asimismo, a continuación se muestra la estructura completa del proyecto como referencia:

```
.
├── docs                             # Documentación del proyecto
│   ├── analisis.md                  # Análisis del comportamiento estadístico
│   ├── conclusiones.md              # Conclusiones finales del proyecto
│   ├── datos.md                     # Explicación de los datos recolectados
│   ├── images                       # Imágenes generadas por el análisis
│   │   ├── evaluacion_docente.jpg
│   │   ├── histograma_mejor_ajuste.svg
│   │   ├── histograma_tiempos_entre_datos.svg
│   │   └── plot.png
│   ├── index.md                     # Página principal de la documentación
│   ├── instrucciones.md             # Instrucciones de uso del sistema
│   ├── modelos.md                   # Ajuste de distribuciones y parámetros
│   ├── problema.md                  # Planteamiento del problema
│   └── uso.md                       # Guía de ejecución y comandos
├── events.db                        # Base de datos utilizada
├── LICENSE                          # Licencia del proyecto
├── mkdocs.yml                       # Configuración de MkDocs y Material for MkDocs
├── playground.ipynb                 # Notebook de pruebas y experimentación
├── pyproject.toml                   # Configuración del proyecto
├── README.md                        # Instrucciones dadas por el profesor
├── src                              # Código fuente principal del proyecto
│   ├── analysis.py                  # Análisis estadístico y ajuste de modelos
│   ├── client.py                    # Suscriptor MQTT para obtener y almacenar datos
│   └── models.py                    # Definición ORM de la base de datos
└── uv.lock                          # Archivo de bloqueo de dependencias para uv
```

