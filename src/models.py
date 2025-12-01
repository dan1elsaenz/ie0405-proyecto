"""Módulo para definir el modelo ORM y crear la base de datos de eventos."""

import os

from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """Clase base para todos los modelos declarativos de SQLAlchemy."""

    pass


# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# URL de conexión a la base de datos (si no se define en .env)
database_url = os.getenv("DATABASE_URL", "sqlite:///events.db")


class Event(Base):
    """
    Modelo de la tabla de eventos recibidos vía MQTT

    Guarda:
    - id: Llave primaria autoincremental de DB
    - topic: Carné estudiantil
    - first_name: Nombre
    - last_name: Apellido
    - timestamp: Instante de tiempo en que se recibió el dato
    """

    __tablename__ = "event"

    # Clave primaria autoincremental del evento
    id = Column(Integer, primary_key=True)

    # Tópico MQTT desde el cual se recibió el mensaje
    topic = Column(String)

    # Nombre incluido en el payload del mensaje
    first_name = Column(String)

    # Apellido incluido en el payload del mensaje
    last_name = Column(String)

    # Marca de tiempo en que se registró el evento
    timestamp = Column(DateTime)


# Crear el motor de conexión a la base de datos (SQLite, según DATABASE_URL)
engine = create_engine(database_url)

# Crear la fábrica de sesiones vinculada al motor
Session = sessionmaker(bind=engine)

# Instancia de sesión para realizar operaciones con la base de datos
session = Session()

# Crear todas las tablas definidas en los modelos si aún no existen
Base.metadata.create_all(engine)
