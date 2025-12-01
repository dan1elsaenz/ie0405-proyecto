# Descripción del problema

El proyecto tiene como objetivo analizar el comportamiento temporal de una secuencia de eventos publicados en un tópico MQTT del laboratorio SIMOVI de la Universidad de Costa Rica (`tcp://mqtt.simovi.org:1883`).

!!! abstract "Mensaje recibido"

    Cada uno corresponde a un evento del _broker_ en el tópico del carné personal y contiene, entre otros datos, un _timestamp_ que indica el instante exacto en el que dicho evento ocurrió.

La meta principal es **modelar la distribución probabilística de los tiempos de retraso entre eventos consecutivos**, con el fin de comprender la naturaleza estadística del proceso generador de dichos datos.

Para ello, se tiene una canalización de procesamiento (*data pipeline*) que inicia con la captura de los mensajes enviados al tópico MQTT asociado al carné estudiantil.
Los mensajes son recibidos por un cliente desarrollado en Python, procesados y almacenados en una base de datos relacional mediante `SQLAlchemy`.
Cada registro almacenado representa un evento individual y contiene un identificador, el tópico donde se recibió el mensaje (carné), el nombre (`first_name`) y apellido (`last_name`) y el instante temporal del evento.

Una vez recopilados los datos durante un período continuo de mínimo tres horas, se procede a extraer la secuencia de eventos desde la base de datos y ordenar los registros cronológicamente.
A partir de estos _timestamps_ se calcula la **diferencia temporal entre cada evento y el anterior**, lo cual genera el **tiempo de retraso** entre los datos.

El objetivo consiste en determinar qué **modelo de distribución** describe mejor estos tiempos de retraso.
Para ello se emplean herramientas de Python como `SciPy Stats` y `Fitter`, siguiendo las recomendaciones del curso para la selección de distribuciones.

