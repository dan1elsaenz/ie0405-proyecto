# Análisis del comportamiento de los tiempos entre eventos

En esta sección se discuten los resultados obtenidos a partir de los datos experimentales y del modelo probabilístico seleccionado.

## Comparación entre datos experimentales y modelo

El análisis estadístico mostró que los tiempos entre eventos presentan:

- Inclinación positiva significativa (_skewness_ \(\approx 1.81\)).
- Kurtosis mayor que la normal (\(\approx 4.14\)), lo cual indica colas pesadas.
- Elevada dispersión (desviación estándar \(\approx 36.47\) s).
- Diferencia importante entre media y mediana, característica de distribuciones asimétricas (relacionada con la inclinación).

Al aplicar un procedimiento sistemático basado en máxima verosimilitud (MLE) y suma de errores cuadrados (SSE) con `Fitter`, la distribución **exponencial** obtuvo el mejor ajuste entre todas las alternativas evaluadas.

### Comparación cuantitativa

| Estadístico | Datos reales | Modelo exponencial |
|------------:|-------------:|-------------------:|
| Media | 37.1053 s | 37.1053 s |
| Varianza | 1329.9235 s\(^2\) | 1376.3614 s\(^2\) |
| Desviación estándar | 36.4681 s | 37.0993 s |
| Skewness | 1.8130 | 2.0 |
| Kurtosis | 4.1415 | 6.0 |

!!! info "Análisis entre datos reales y modelo"

    - **Media y desviación estándar:** presentan coincidencia casi exacta, lo cual es un indicador importante de compatibilidad entre datos y modelo.
    - **Varianza:** En este caso, el hecho de que la varianza empírica sea un poco menor que la del modelo indica que los tiempos entre eventos reales presentan ligeramente menos dispersión que la que predice una exponencial, pero la diferencia es poco significativa.
    - **Inclinación:** ambos valores indican un comportamiento asimétrico hacia la derecha.
    - **Kurtosis:** la exponencial teórica tiene colas más pesadas que las de los datos reales. Esto implica que el proceso observado tiene menor probabilidad de generar intervalos extremadamente grandes, aunque sigue mostrando un patrón general compatible con una exponencial.

En conjunto, el modelo exponencial describe adecuadamente el comportamiento promedio del proceso.

## Evaluación visual del ajuste

Los histogramas correspondientes muestran:

- Una concentración principal cercana a cero, esperable en un proceso donde los intervalos pequeños son frecuentes.
- Una caída progresiva en la densidad conforme aumenta el tiempo, coherente con una distribución exponencial.
- Diferencias leves en la región de colas largas (valores altos de diferencias temporales entre datos), donde los datos presentan menor dispersión que la predicha por el modelo.

## Interpretación del proceso

Si los tiempos entre eventos \(T\) se aproximan a una distribución exponencial, esto sugiere que el proceso generador es similar a un **proceso de Poisson con tasa constante**.
El parámetro estimado fue:

\[
\lambda \approx 0.02695\ \text{s}^{-1},
\]

lo cual implica un tiempo promedio entre eventos igual a:

\[
\frac{1}{\lambda} \approx 37.1\ \text{s}.
\]

