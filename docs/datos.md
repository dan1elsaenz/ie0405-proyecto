# Análisis exploratorio de los datos

En esta sección se presenta un análisis cualitativo y cuantitativo de los datos recolectados desde el tópico MQTT asignado.
El objetivo es caracterizar estadísticamente los **tiempos entre eventos**, representados por la variable aleatoria \(T\).

## Descripción cualitativa

Los datos fueron recibidos mediante un cliente MQTT implementado en Python y almacenados en una base de datos SQLite usando `SQLAlchemy`.
Cada registro corresponde a un evento individual del sistema remoto y contiene:

- `topic`: tópico MQTT desde el cual se recibió el mensaje.
- `first_name`: nombre del estudiante.
- `last_name`: apellido del estudiante.
- `timestamp`: instante temporal en el que se produjo el evento.

Estos fueron guardados en el modelo en la base de datos mostrado a continuación:


```python
class event(Base):
    """Definición de la tabla de eventos recibidos."""

    __tablename__ = "event"

    id = Column(Integer, primary_key=True) # (1)!
    topic = Column(String)                 # (2)!
    first_name = Column(String)            # (3)!
    last_name = Column(String)             # (4)!
    timestamp = Column(DateTime)           # (5)!
```

1. `id`: identificador único (autoincremental) para cada evento registrado.
2. `topic`: tópico MQTT donde se recibió el mensaje (carné estudiantil).
3. `first_name`: nombre del mensaje MQTT.
4. `last_name`: apellido del mensaje MQTT.
5. `timestamp`: instante en que se recibió el mensaje en el cliente MQTT.

Luego del almacenamiento, los registros se ordenan cronológicamente y se calcula el **tiempo entre eventos** como:

\[
T_i = t_i - t_{i-1}
\]

donde:

- \( t_i \) es el _timestamp_ del evento actual,
- \( t_{i-1} \) es el _timestamp_ del evento inmediatamente anterior.

> Esta operación genera un conjunto de diferencias temporales denominado `time_between_data`, en segundos. Esta variable es la base del análisis estadístico realizado.

## Descripción cuantitativa

La siguiente tabla presenta las estadísticas descriptivas experimentales obtenidas a partir de los **665 tiempos entre eventos** registrados, con la función `compute_descriptive_stats()`.

| Estadística | Valor |
|------------:|-------:|
| Número de datos (`n`) | 665 |
| Mínimo | 0.0060 s |
| Máximo | 230.6151 s |
| Media | 37.1053 s |
| Mediana | 26.7258 s |
| Desviación estándar | 36.4681 s |
| Cuartil 25% | 10.9562 s |
| Cuartil 75% | 50.0776 s |
| Inclinación | 1.8130 |
| Kurtosis | 4.1415 |

!!! note "Interpretación"

    - La separación significativa entre la media y la mediana revela una **asimetría** en la distribución.
    - La asimetría positiva (\(> 1.5\)) y la kurtosis (\(> 3\)) indican la presencia de colas largas.

## Gráfica descriptiva

La siguiente figura muestra un histograma con la densidad empírica de los valores de \(T\):

<div class="figure" align="center">
  <img src="../images/histograma_tiempos_entre_datos.svg" alt="Histograma simple de tiempos entre eventos" width="75%">
  <p class="caption">Figura 1. Histograma de los tiempos entre eventos obtenidos del flujo MQTT.</p>
</div>


!!! info "Número de _bins_"

    Para visualizar la distribución empírica de los tiempos entre eventos, se utilizaron histogramas construidos con un número de bins determinado mediante la **regla de Freedman–Diaconis**, que adapta la resolución horizontal según la dispersión real de los datos.

    Esto se realizó para cumplir con el criterio:

    > Adapta correctamente la escala horizontal (_bins_) del histograma de los datos.

