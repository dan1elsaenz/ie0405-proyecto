**Universidad de Costa Rica** | Escuela de Ingeniería Eléctrica <br>
*IE0405 - Modelos Probabilíticos de Señales y Sistemas* <br>
Profesores: Fabián Abarca Calderón y Sebastián Ramírez Sandí <br>
Asistente: Darío Guzmán Carranza <br>
Segundo ciclo de 2025

# Proyecto de programación

---

## Grupo 01

- Daniel Alberto Sáenz Obando, C37099

### Resumen

En este proyecto se analizó el comportamiento temporal de un flujo de datos recibido mediante un sistema MQTT, con el objetivo de caracterizar estadísticamente los **tiempos entre eventos** registrados y evaluar qué modelo probabilístico describe mejor el proceso.
A partir de los *timestamps* almacenados en una base de datos SQLite, se calcularon las diferencias temporales entre eventos consecutivos y se realizó un análisis que incluyó promedio, varianza, desviación estándar, inclinación y kurtosis.

Posteriormente, se aplicaron **pruebas de bondad de ajuste** utilizando el paquete `Fitter` de Python, la cual ajustó múltiples distribuciones y seleccionó el modelo óptimo.
Los resultados indicaron que la distribución **exponencial** es la que mejor representa los datos, coincidencia respaldada por la cercanía entre los momentos empíricos y los momentos teóricos del modelo.
Este hallazgo resultó en que el proceso observado se comporta de manera similar a un **proceso de Poisson** con tasa constante.


### Secciones

<div class="grid cards" markdown>

-   :material-help-circle:{ .lg .middle } __Problema__

    ---

    Planteamiento del problema a resolver.

    [:octicons-arrow-right-24: Ver problema](problema.md)

-   :material-play-box-outline:{ .lg .middle } __Instrucciones de uso y estructura__

    ---

    Contiene las instrucciones de uso para ejecutar el código, así como la explicación de la estructura del proyecto.

    [:octicons-arrow-right-24: Ver uso](uso.md)

-   :material-database-import:{ .lg .middle } __Datos__

    ---

    Descripción cualitativa, estadística descriptiva y gráficos de los datos obtenidos.

    [:octicons-arrow-right-24: Ver datos](datos.md)

-   :material-chart-bell-curve:{ .lg .middle } __Modelos__

    ---

    Ajustes de los modelos de probabilidad y sus parámetros para los datos.

    [:octicons-arrow-right-24: Ver modelos](modelos.md)

-   :material-database-search:{ .lg .middle } __Análisis__

    ---

    Resultados y análisis de la solución al problema planteado.

    [:octicons-arrow-right-24: Ver análisis](analisis.md)

-   :material-list-box:{ .lg .middle } __Conclusiones__

    ---

    Conclusiones del trabajo realizado.

    [:octicons-arrow-right-24: Ver conclusiones](conclusiones.md)

</div>

