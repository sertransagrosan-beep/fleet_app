from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text
from sqlalchemy.orm import relationship

from database.db import Base


# =========================
# VEHICULOS
# =========================

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)

    placa = Column(String, unique=True, nullable=False)
    marca = Column(String)
    modelo = Column(String)
    tipo_motor = Column(String)
    anio = Column(Integer)
    estado = Column(String)

    maintenances = relationship("Maintenance", back_populates="vehicle")


# =========================
# TRAILERS
# =========================

class Trailer(Base):
    __tablename__ = "trailers"

    id = Column(Integer, primary_key=True, index=True)

    placa = Column(String, unique=True, nullable=False)
    marca = Column(String)
    modelo = Column(String)
    estado = Column(String)

    maintenances = relationship("Maintenance", back_populates="trailer")


# =========================
# CONDUCTORES
# =========================

class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(String, nullable=False)
    cedula = Column(String, unique=True)
    telefono = Column(String)
    estado = Column(String)

    maintenances = relationship("Maintenance", back_populates="driver")


# =========================
# MANTENIMIENTOS
# =========================

class Maintenance(Base):
    __tablename__ = "maintenances"

    id = Column(Integer, primary_key=True, index=True)

    fecha_ingreso = Column(Date)

    vehiculo_id = Column(Integer, ForeignKey("vehicles.id"))
    trailer_id = Column(Integer, ForeignKey("trailers.id"))
    conductor_id = Column(Integer, ForeignKey("drivers.id"))

    tipo_mantenimiento = Column(String)

    descripcion = Column(Text)
    observaciones = Column(Text)

    taller = Column(String)

    estado = Column(String)

    vehicle = relationship("Vehicle", back_populates="maintenances")
    trailer = relationship("Trailer", back_populates="maintenances")
    driver = relationship("Driver", back_populates="maintenances")