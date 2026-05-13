# database/models.py

from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from database.db import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True)
    placa = Column(String, unique=True, nullable=False)
    marca = Column(String)
    linea = Column(String)
    modelo = Column(String)
    color = Column(String)
    capacidad_carga = Column(String)
    tipo_combustible = Column(String)
    soat = Column(Date)
    tecnomecanica = Column(Date)
    kilometraje_actual = Column(Integer)
    estado = Column(String)
    
    # Trailer y conductor habitual
    trailer_habitual_id = Column(Integer, ForeignKey("trailers.id"), nullable=True)
    conductor_habitual_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    
    # Relaciones
    maintenances = relationship("Maintenance", back_populates="vehicle")
    trailer_habitual = relationship("Trailer", foreign_keys=[trailer_habitual_id])
    conductor_habitual = relationship("Driver", foreign_keys=[conductor_habitual_id])


class Trailer(Base):
    __tablename__ = "trailers"

    id = Column(Integer, primary_key=True)
    placa = Column(String, unique=True, nullable=False)
    marca = Column(String)
    modelo = Column(String)
    carroceria = Column(String)
    numero_ejes = Column(Integer)
    estado = Column(String)

    maintenances = relationship("Maintenance", back_populates="trailer")
    # Relación inversa: trailers asignados como habituales
    assigned_vehicles = relationship("Vehicle", foreign_keys=[Vehicle.trailer_habitual_id], back_populates="trailer_habitual")


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    identificacion = Column(String, unique=True)
    telefono = Column(String)
    vencimiento_licencia = Column(Date)
    estado = Column(String)

    maintenances = relationship("Maintenance", back_populates="driver")
    # Relación inversa: conductores asignados como habituales
    assigned_vehicles = relationship("Vehicle", foreign_keys=[Vehicle.conductor_habitual_id], back_populates="conductor_habitual")


class Maintenance(Base):
    __tablename__ = "maintenances"

    id = Column(Integer, primary_key=True)
    fecha_ingreso = Column(Date)
    
    vehiculo_id = Column(Integer, ForeignKey("vehicles.id"))
    trailer_id = Column(Integer, ForeignKey("trailers.id"), nullable=True)
    conductor_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    
    tipo_mantenimiento = Column(String)
    descripcion = Column(Text)
    observaciones = Column(Text)
    taller = Column(String)
    estado = Column(String)

    vehicle = relationship("Vehicle", back_populates="maintenances")
    trailer = relationship("Trailer", back_populates="maintenances")
    driver = relationship("Driver", back_populates="maintenances")