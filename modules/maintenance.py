import streamlit as st
import pandas as pd

from datetime import date

from database.db import SessionLocal
from database.models import (
    Vehicle,
    Trailer,
    Driver,
    Maintenance
)


def maintenance_page():

    st.title("🛠️ Mantenimientos")

    db = SessionLocal()

    vehicles = db.query(Vehicle).all()
    trailers = db.query(Trailer).all()
    drivers = db.query(Driver).all()

    # ==================================================
    # DICCIONARIOS
    # ==================================================

    vehicle_dict = {
        f"{v.placa} - {v.marca}": v.id
        for v in vehicles
    }

    trailer_dict = {
        f"{t.placa} - {t.marca}": t.id
        for t in trailers
    }

    driver_dict = {
        f"{d.nombre} - {d.cedula}": d.id
        for d in drivers
    }

    # ==================================================
    # CREAR
    # ==================================================

    st.subheader("➕ Registrar Mantenimiento")

    with st.form("maintenance_form"):

        fecha_ingreso = st.date_input(
            "Fecha Ingreso",
            value=date.today()
        )

        vehiculo = st.selectbox(
            "Vehículo",
            list(vehicle_dict.keys())
        )

        trailer = st.selectbox(
            "Trailer",
            list(trailer_dict.keys())
        )

        conductor = st.selectbox(
            "Conductor",
            list(driver_dict.keys())
        )

        tipo = st.selectbox(
            "Tipo",
            ["Preventivo", "Correctivo"]
        )

        descripcion = st.text_area(
            "Descripción"
        )

        observaciones = st.text_area(
            "Observaciones"
        )

        taller = st.text_input("Taller")

        estado = st.selectbox(
            "Estado",
            ["Pendiente", "En Proceso", "Finalizado"]
        )

        submitted = st.form_submit_button(
            "Guardar"
        )

        if submitted:

            maintenance = Maintenance(
                fecha_ingreso=fecha_ingreso,
                vehiculo_id=vehicle_dict[vehiculo],
                trailer_id=trailer_dict[trailer],
                conductor_id=driver_dict[conductor],
                tipo_mantenimiento=tipo,
                descripcion=descripcion,
                observaciones=observaciones,
                taller=taller,
                estado=estado
            )

            db.add(maintenance)
            db.commit()

            st.success(
                "Mantenimiento registrado"
            )

    st.divider()

    # ==================================================
    # FILTROS
    # ==================================================

    st.subheader("🔍 Filtros")

    filtro_estado = st.selectbox(
        "Estado",
        ["Todos", "Pendiente", "En Proceso", "Finalizado"]
    )

    filtro_tipo = st.selectbox(
        "Tipo",
        ["Todos", "Preventivo", "Correctivo"]
    )

    query = db.query(Maintenance)

    if filtro_estado != "Todos":

        query = query.filter(
            Maintenance.estado == filtro_estado
        )

    if filtro_tipo != "Todos":

        query = query.filter(
            Maintenance.tipo_mantenimiento == filtro_tipo
        )

    maintenances = query.all()

    # ==================================================
    # TABLA
    # ==================================================

    st.subheader("📋 Historial")

    data = []

    for m in maintenances:

        data.append({
            "ID": m.id,
            "Fecha": m.fecha_ingreso,
            "Vehículo": m.vehicle.placa,
            "Trailer": m.trailer.placa,
            "Conductor": m.driver.nombre,
            "Tipo": m.tipo_mantenimiento,
            "Taller": m.taller,
            "Estado": m.estado
        })

    df = pd.DataFrame(data)

    st.dataframe(
    df,
    width="stretch"
    )

    db.close()