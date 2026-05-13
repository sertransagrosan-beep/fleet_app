# database/db.py

import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


def get_engine():
    """Retorna el engine de SQLAlchemy para Neon PostgreSQL"""
    try:
        DATABASE_URL = st.secrets["neon"]["DATABASE_URL"]
    except:
        DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://usuario:contraseña@host:5432/dbname")
    
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args={
            "sslmode": "require",
        }
    )
    return engine


# Crear engine global
engine = get_engine()

# Crear fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()


def init_db():
    """Crea todas las tablas si no existen"""
    Base.metadata.create_all(bind=engine)