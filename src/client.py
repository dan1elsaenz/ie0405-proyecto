"""Suscriptor MQTT que almacena eventos en una base de datos.

Este módulo:
- Se conecta a un broker MQTT.
- Se suscribe a un tópico configurado mediante variables de entorno.
- Recibe mensajes, los parsea (JSON cuando es posible).
- Inserta en la base de datos los eventos que contienen nombre y apellido.
"""

import json
import logging
import os
import time
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion

from models import session, Event

# Cargar variables de entorno desde archivo .env
load_dotenv()

# Configuración del broker MQTT desde variables de entorno
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USER = os.getenv("MQTT_USER", "admin")
MQTT_PASS = os.getenv("MQTT_PASS", "admin")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "test")

# Configurar logging para mostrar información en la terminal
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def on_connect(client, rc):
    """Maneja el evento de conexión del cliente al broker MQTT.

    Si la conexión es exitosa (rc == 0), se suscribe al tópico configurado.
    En caso contrario, registra el código de error.
    """
    if rc == 0:
        logger.info("Conectado al broker MQTT en %s:%d", MQTT_HOST, MQTT_PORT)
        client.subscribe(MQTT_TOPIC)
        logger.info("Suscrito al tópico: %s", MQTT_TOPIC)
    else:
        logger.error("Fallo al conectar al broker MQTT: %d", rc)


def on_message(msg):
    """Maneja la recepción de un mensaje desde el broker MQTT.

    - Decodifica el payload (UTF-8 o Latin-1 como respaldo).
    - Intenta parsear JSON; si falla, guarda el texto crudo.
    - Si el mensaje contiene 'first_name' y 'last_name', lo almacena
      en la base de datos junto con el tópico y la marca de tiempo.
    """
    try:
        topic = msg.topic

        # Intentar decodificar el payload como UTF-8; si falla, usar Latin-1
        try:
            payload = msg.payload.decode("utf-8")
        except UnicodeDecodeError:
            payload = msg.payload.decode("latin-1")

        logger.info(
            "Mensaje recibido en el tópico '%s': %s...",
            topic,
            payload[:100],
        )

        # Intentar interpretar el payload como JSON
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            # Si no es JSON, almacenar el contenido crudo
            data = {"raw": payload}

        # Solo insertar en la DB si se encuentran las claves esperadas
        if "first_name" in data and "last_name" in data:
            # Añadir metadatos de tiempo y tópico
            data["timestamp"] = datetime.now(ZoneInfo("America/Costa_Rica"))
            data["topic"] = topic

            # Crear registro ORM y guardarlo en la base de datos
            record = Event(
                topic=data["topic"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                timestamp=data["timestamp"],
            )
            session.add(record)
            session.commit()

            logger.info("Datos añadidos a la base de datos, id=%s", record.id)

    except Exception as e:
        # Registrar error inesperado durante el procesamiento del mensaje
        logger.error("Error al procesar mensaje: %s", e, exc_info=True)


def on_disconnect(rc):
    """Maneja el evento de desconexión del cliente del broker MQTT.

    Distingue entre una desconexión esperada (rc == 0) y una inesperada.
    """
    if rc != 0:
        logger.warning(
            "Desconexión inesperada del broker MQTT, código de retorno: %d", rc
        )
    else:
        logger.info("Desconectado del broker MQTT")


def main():
    """Función principal que configura y ejecuta el suscriptor MQTT.

    - Configura el cliente MQTT y sus callbacks.
    - Aplica lógica de reintentos para la conexión al broker.
    - Inicia el bucle principal de recepción de mensajes.
    """
    logger.info("Iniciando servicio de suscriptor MQTT...")

    # Crear un ID de cliente único para evitar colisiones en el broker
    client_id = f"subscriber-{uuid.uuid4()}"
    logger.info("Usando ID de cliente: %s", client_id)

    # Crear cliente MQTT usando la API de callbacks versión 2
    client = mqtt.Client(
        client_id=client_id,
        callback_api_version=CallbackAPIVersion.VERSION2,
    )

    # Configurar credenciales para autenticación en el broker
    client.username_pw_set(MQTT_USER, MQTT_PASS)

    # Habilitar reconexión automática con un retardo progresivo
    client.reconnect_delay_set(min_delay=1, max_delay=120)

    # Asociar funciones callback a los eventos relevantes
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    # Parámetros de reintento de conexión
    max_retries = 5
    retry_delay = 5  # segundos

    # Intentar conectar al broker con reintentos
    for attempt in range(max_retries):
        try:
            logger.info(
                "Intentando conectar al broker MQTT (intento %d/%d)...",
                attempt + 1,
                max_retries,
            )
            # Usar un keepalive mayor (reducir desconexiones por inactividad)
            client.connect(MQTT_HOST, MQTT_PORT, keepalive=120)
            break
        except Exception as e:
            logger.warning(
                "Intento de conexión MQTT %d/%d fallido: %s",
                attempt + 1,
                max_retries,
                e,
            )
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error(
                    "Fallo al conectar al broker después del máximo intentos"
                )
                return

    # Iniciar el bucle principal de recepción de mensajes
    try:
        logger.info("Iniciando bucle principal del cliente MQTT...")
        client.loop_forever()
    except KeyboardInterrupt:
        # Permitir detener el servicio con Ctrl+C de forma controlada
        logger.info("Señal de apagado recibida (KeyboardInterrupt)")
    finally:
        # Asegurar la desconexión del broker al finalizar
        client.disconnect()
        logger.info("Servicio de suscriptor finalizado")


# Ejecutar la función principal si este archivo se ejecuta directamente
if __name__ == "__main__":
    main()
