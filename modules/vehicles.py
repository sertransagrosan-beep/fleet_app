import streamlit as st
import pandas as pd

from database.db import SessionLocal
from database.models import Vehicle


def vehicles_page():

    st.title("🚛 Vehículos")

    db = SessionLocal()

    # ==================================================
    # FORMULARIO CREAR
    # ==================================================

    st.subheader("➕ Registrar Vehículo")

    with st.form("vehicle_form"):

        placa = st.text_input("Placa")
        marca = st.text_input("Marca")
        modelo = st.text_input("Modelo")
        tipo_motor = st.text_input("Tipo Motor")

        anio = st.number_input(
            "Año",
            min_value=1900,
            max_value=2100,
            step=1
        )

        estado = st.selectbox(
            "Estado",
            ["Activo", "Inactivo"]
        )

        submitted = st.form_submit_button("Guardar")

        if submitted:

            placa = placa.upper().strip()

            # VALIDACIONES
            if placa == "":
                st.error("La placa es obligatoria")

            else:

                existe = db.query(Vehicle).filter(
                    Vehicle.placa == placa
                ).first()

                if existe:
                    st.warning("La placa ya existe")

                else:

                    vehicle = Vehicle(
                        placa=placa,
                        marca=marca,
                        modelo=modelo,
                        tipo_motor=tipo_motor,
                        anio=anio,
                        estado=estado
                    )

                    db.add(vehicle)
                    db.commit()

                    st.success("Vehículo registrado correctamente")

    st.divider()

    # ==================================================
    # BUSQUEDA
    # ==================================================

    st.subheader("🔍 Buscar Vehículos")

    buscar = st.text_input(
        "Buscar por placa o marca"
    )

    query = db.query(Vehicle)

    if buscar:

        query = query.filter(
            (Vehicle.placa.contains(buscar)) |
            (Vehicle.marca.contains(buscar))
        )

    vehicles = query.all()

    # ==================================================
    # TABLA
    # ==================================================

    st.subheader("📋 Listado")

    data = []

    for v in vehicles:

        data.append({
            "ID": v.id,
            "Placa": v.placa,
            "Marca": v.marca,
            "Modelo": v.modelo,
            "Motor": v.tipo_motor,
            "Año": v.anio,
            "Estado": v.estado
        })

    df = pd.DataFrame(data)

    st.dataframe(
    df,
    width="stretch"
    )

    st.divider()

    # ==================================================
    # EDITAR
    # ==================================================

    st.subheader("✏️ Editar Vehículo")

    vehicle_options = {
        f"{v.placa} - {v.marca}": v.id
        for v in vehicles
    }

    if vehicle_options:

        selected = st.selectbox(
            "Seleccionar Vehículo",
            list(vehicle_options.keys())
        )

        selected_id = vehicle_options[selected]

        vehicle = db.query(Vehicle).filter(
            Vehicle.id == selected_id
        ).first()

        with st.form("edit_vehicle_form"):

            edit_placa = st.text_input(
                "Placa",
                value=vehicle.placa
            )

            edit_marca = st.text_input(
                "Marca",
                value=vehicle.marca
            )

            edit_modelo = st.text_input(
                "Modelo",
                value=vehicle.modelo
            )

            edit_motor = st.text_input(
                "Tipo Motor",
                value=vehicle.tipo_motor
            )

            edit_anio = st.number_input(
                "Año",
                value=vehicle.anio,
                step=1
            )

            edit_estado = st.selectbox(
                "Estado",
                ["Activo", "Inactivo"],
                index=0 if vehicle.estado == "Activo" else 1
            )

            update = st.form_submit_button(
                "Actualizar"
            )

            if update:

                nueva_placa = edit_placa.upper().strip()

                duplicado = db.query(Vehicle).filter(
                    Vehicle.placa == nueva_placa,
                    Vehicle.id != vehicle.id
                ).first()

                if duplicado:

                    st.error(
                        "Ya existe otro vehículo con esa placa"
                    )

                else:

                    vehicle.placa = nueva_placa
                    vehicle.marca = edit_marca
                    vehicle.modelo = edit_modelo
                    vehicle.tipo_motor = edit_motor
                    vehicle.anio = edit_anio
                    vehicle.estado = edit_estado

                    db.commit()

                    st.success(
                        "Vehículo actualizado"
                    )

    st.divider()

    # ==================================================
    # ELIMINAR
    # ==================================================

    st.subheader("🗑️ Eliminar Vehículo")

    if vehicle_options:

        delete_selected = st.selectbox(
            "Seleccionar Vehículo a Eliminar",
            list(vehicle_options.keys()),
            key="delete_vehicle"
        )

        delete_id = vehicle_options[delete_selected]

        if st.button("Eliminar Vehículo"):

            vehicle_delete = db.query(Vehicle).filter(
                Vehicle.id == delete_id
            ).first()

            db.delete(vehicle_delete)
            db.commit()

            st.success("Vehículo eliminado")

    db.close()