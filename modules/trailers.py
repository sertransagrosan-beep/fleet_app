import streamlit as st
import pandas as pd

from database.db import SessionLocal
from database.models import Trailer


def trailers_page():

    st.title("🚚 Trailers")

    db = SessionLocal()

    # ==================================================
    # CREAR
    # ==================================================

    st.subheader("➕ Registrar Trailer")

    with st.form("trailer_form"):

        placa = st.text_input("Placa")
        marca = st.text_input("Marca")
        modelo = st.text_input("Modelo")

        estado = st.selectbox(
            "Estado",
            ["Activo", "Inactivo"]
        )

        submitted = st.form_submit_button("Guardar")

        if submitted:

            placa = placa.upper().strip()

            existe = db.query(Trailer).filter(
                Trailer.placa == placa
            ).first()

            if existe:

                st.warning("La placa ya existe")

            else:

                trailer = Trailer(
                    placa=placa,
                    marca=marca,
                    modelo=modelo,
                    estado=estado
                )

                db.add(trailer)
                db.commit()

                st.success("Trailer registrado")

    st.divider()

    # ==================================================
    # BUSQUEDA
    # ==================================================

    buscar = st.text_input(
        "Buscar Trailer"
    )

    query = db.query(Trailer)

    if buscar:

        query = query.filter(
            Trailer.placa.contains(buscar)
        )

    trailers = query.all()

    st.subheader("📋 Listado")

    data = []

    for t in trailers:

        data.append({
            "ID": t.id,
            "Placa": t.placa,
            "Marca": t.marca,
            "Modelo": t.modelo,
            "Estado": t.estado
        })

    df = pd.DataFrame(data)

    st.dataframe(df, width="stretch")

    st.divider()

    # ==================================================
    # EDITAR
    # ==================================================

    trailer_options = {
        f"{t.placa} - {t.marca}": t.id
        for t in trailers
    }

    if trailer_options:

        st.subheader("✏️ Editar Trailer")

        selected = st.selectbox(
            "Seleccionar Trailer",
            list(trailer_options.keys())
        )

        trailer = db.query(Trailer).filter(
            Trailer.id == trailer_options[selected]
        ).first()

        with st.form("edit_trailer_form"):

            edit_placa = st.text_input(
                "Placa",
                value=trailer.placa
            )

            edit_marca = st.text_input(
                "Marca",
                value=trailer.marca
            )

            edit_modelo = st.text_input(
                "Modelo",
                value=trailer.modelo
            )

            edit_estado = st.selectbox(
                "Estado",
                ["Activo", "Inactivo"],
                index=0 if trailer.estado == "Activo" else 1
            )

            update = st.form_submit_button(
                "Actualizar"
            )

            if update:

                trailer.placa = edit_placa.upper()
                trailer.marca = edit_marca
                trailer.modelo = edit_modelo
                trailer.estado = edit_estado

                db.commit()

                st.success("Trailer actualizado")

    st.divider()

    # ==================================================
    # ELIMINAR
    # ==================================================

    st.subheader("🗑️ Eliminar Trailer")

    if trailer_options:

        delete_selected = st.selectbox(
            "Seleccionar Trailer",
            list(trailer_options.keys()),
            key="delete_trailer"
        )

        delete_id = trailer_options[delete_selected]

        if st.button("Eliminar Trailer"):

            trailer_delete = db.query(Trailer).filter(
                Trailer.id == delete_id
            ).first()

            db.delete(trailer_delete)
            db.commit()

            st.success("Trailer eliminado")

    db.close()