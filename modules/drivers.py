import streamlit as st
import pandas as pd

from database.db import SessionLocal
from database.models import Driver


def drivers_page():

    st.title("👨‍✈️ Conductores")

    db = SessionLocal()

    # ==================================================
    # CREAR
    # ==================================================

    st.subheader("➕ Registrar Conductor")

    with st.form("driver_form"):

        nombre = st.text_input("Nombre")
        cedula = st.text_input("Cédula")
        telefono = st.text_input("Teléfono")

        estado = st.selectbox(
            "Estado",
            ["Activo", "Inactivo"]
        )

        submitted = st.form_submit_button("Guardar")

        if submitted:

            cedula = cedula.strip()

            existe = db.query(Driver).filter(
                Driver.cedula == cedula
            ).first()

            if existe:

                st.warning("La cédula ya existe")

            else:

                driver = Driver(
                    nombre=nombre,
                    cedula=cedula,
                    telefono=telefono,
                    estado=estado
                )

                db.add(driver)
                db.commit()

                st.success("Conductor registrado")

    st.divider()

    # ==================================================
    # BUSQUEDA
    # ==================================================

    buscar = st.text_input(
        "Buscar conductor"
    )

    query = db.query(Driver)

    if buscar:

        query = query.filter(
            (Driver.nombre.contains(buscar)) |
            (Driver.cedula.contains(buscar))
        )

    drivers = query.all()

    st.subheader("📋 Listado")

    data = []

    for d in drivers:

        data.append({
            "ID": d.id,
            "Nombre": d.nombre,
            "Cédula": d.cedula,
            "Teléfono": d.telefono,
            "Estado": d.estado
        })

    df = pd.DataFrame(data)

    st.dataframe(df, width="stretch")

    st.divider()

    # ==================================================
    # EDITAR
    # ==================================================

    driver_options = {
        f"{d.nombre} - {d.cedula}": d.id
        for d in drivers
    }

    if driver_options:

        st.subheader("✏️ Editar Conductor")

        selected = st.selectbox(
            "Seleccionar Conductor",
            list(driver_options.keys())
        )

        driver = db.query(Driver).filter(
            Driver.id == driver_options[selected]
        ).first()

        with st.form("edit_driver_form"):

            edit_nombre = st.text_input(
                "Nombre",
                value=driver.nombre
            )

            edit_cedula = st.text_input(
                "Cédula",
                value=driver.cedula
            )

            edit_telefono = st.text_input(
                "Teléfono",
                value=driver.telefono
            )

            edit_estado = st.selectbox(
                "Estado",
                ["Activo", "Inactivo"],
                index=0 if driver.estado == "Activo" else 1
            )

            update = st.form_submit_button(
                "Actualizar"
            )

            if update:

                driver.nombre = edit_nombre
                driver.cedula = edit_cedula
                driver.telefono = edit_telefono
                driver.estado = edit_estado

                db.commit()

                st.success("Conductor actualizado")

    st.divider()

    # ==================================================
    # ELIMINAR
    # ==================================================

    st.subheader("🗑️ Eliminar Conductor")

    if driver_options:

        delete_selected = st.selectbox(
            "Seleccionar Conductor",
            list(driver_options.keys()),
            key="delete_driver"
        )

        delete_id = driver_options[delete_selected]

        if st.button("Eliminar Conductor"):

            driver_delete = db.query(Driver).filter(
                Driver.id == delete_id
            ).first()

            db.delete(driver_delete)
            db.commit()

            st.success("Conductor eliminado")

    db.close()