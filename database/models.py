# database/models.py

from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from database.db import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True)
    placa = Column(String(20), unique=True, nullable=False)
    marca = Column(String(100))
    linea = Column(String(100))
    modelo = Column(String(10))
    color = Column(String(100))
    capacidad_carga = Column(String(50))
    tipo_combustible = Column(String(50))
    soat = Column(Date)
    tecnomecanica = Column(Date)
    kilometraje_actual = Column(Integer)
    estado = Column(String(20))
    
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
    placa = Column(String(20), unique=True, nullable=False)
    marca = Column(String(100))
    modelo = Column(String(10))
    carroceria = Column(String(100))
    numero_ejes = Column(Integer)
    estado = Column(String(20))

    maintenances = relationship("Maintenance", back_populates="trailer")
    # Relación inversa: trailers asignados como habituales
    assigned_vehicles = relationship("Vehicle", foreign_keys=[Vehicle.trailer_habitual_id], back_populates="trailer_habitual")


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(200), nullable=False)
    identificacion = Column(String(50), unique=True)
    telefono = Column(String(20))
    vencimiento_licencia = Column(Date)
    estado = Column(String(20))

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
    
    tipo_mantenimiento = Column(String(50))
    descripcion = Column(Text)
    observaciones = Column(Text)
    taller = Column(String(200))
    estado = Column(String(20))

    vehicle = relationship("Vehicle", back_populates="maintenances")
    trailer = relationship("Trailer", back_populates="maintenances")
    driver = relationship("Driver", back_populates="maintenances")