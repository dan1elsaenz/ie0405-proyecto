# Conclusiones

El análisis realizado permitió caracterizar de manera sólida el comportamiento de los tiempos entre eventos obtenidos del flujo MQTT, por medio de la combinación de herramientas estadísticas y métodos formales de ajuste probabilístico.
A partir de los datos recolectados, se determinó que la variable de interés presenta una distribución marcadamente asimétrica, con una concentración significativa de intervalos pequeños y una reducción progresiva en la densidad conforme aumenta el tiempo.
Estas características sirvieron para la evaluación de diversos modelos probabilísticos mediante un procedimiento sistemático basado en máxima verosimilitud y suma de errores cuadrados, con el paquete `Fitter` de Python.

Los resultados mostraron que la distribución **exponencial** proporciona el mejor ajuste a los datos experimentales.
La coincidencia entre los momentos experimentales y los teóricos (especialmente en la media y la desviación estándar) respalda la validez de este modelo para describir el proceso.

!!! note "Diferencia entre datos experimentales y modelo"

    Aunque se observaron diferencias en las colas (valores altos de diferencia temporal entre eventos), donde el proceso real muestra menor tendencia en estos puntos que la predicha por la exponencial ideal, estas diferencias no son significativos y no comprometen la validez del modelo.

En consecuencia, el flujo de eventos puede interpretarse como un proceso cercano a un **proceso de Poisson** con tasa constante aproximada de \(\lambda \approx 0.02695\ \text{s}^{-1}\).

# Evaluación docente

Como forma de demostración de la realización de la evaluación docente para el curso IE0405: Modelos probabilísticos de señales y sistemas con el docente Fabián Abarca Calderón, se adjunta la siguiente captura de pantalla tomada al finalizarla.

<div class="figure" align="center">
  <img src="../images/evaluacion_docente.jpg" alt="Evaluación docente" width="50%">
  <p class="caption">Figura 3. Captura de pantalla de evaluación docente realizada.</p>
</div>

