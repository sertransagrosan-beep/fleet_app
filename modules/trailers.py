# modules/trailers.py

import streamlit as st
import pandas as pd

from database.db import SessionLocal
from database.models import Trailer


def trailers_page():
    st.title("🚚 Trailers")
    
    db = SessionLocal()
    
    # Pestañas para organizar mejor
    tab1, tab2, tab3 = st.tabs(["📋 Listar", "📝 Registrar", "✏️ Editar/Eliminar"])
    
    with tab1:
        st.subheader("Registrar Trailer")
        
        with st.form("trailer_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                placa = st.text_input("Placa *").upper()
                marca = st.text_input("Marca *")
                modelo = st.text_input("Modelo")
                carroceria = st.text_input("Carrocería")
            
            with col2:
                numero_ejes = st.number_input("Número de ejes", min_value=1, value=2)
                estado = st.selectbox("Estado", ["Activo", "Mantenimiento", "Inactivo"])
            
            submitted = st.form_submit_button("Guardar", use_container_width=True)
            
            if submitted:
                if not placa:
                    st.error("La placa es obligatoria")
                elif not marca:
                    st.error("La marca es obligatoria")
                else:
                    # Verificar si ya existe
                    existe = db.query(Trailer).filter(Trailer.placa == placa).first()
                    if existe:
                        st.error(f"Ya existe un trailer con placa {placa}")
                    else:
                        nuevo = Trailer(
                            placa=placa,
                            marca=marca,
                            modelo=modelo,
                            carroceria=carroceria,
                            numero_ejes=numero_ejes,
                            estado=estado
                        )
                        db.add(nuevo)
                        db.commit()
                        st.success(f"Trailer {placa} registrado correctamente")
                        st.rerun()
    
    with tab2:
        st.subheader("Lista de Trailers")
        
        trailers = db.query(Trailer).order_by(Trailer.placa).all()
        
        if trailers:
            data = []
            for t in trailers:
                data.append({
                    "ID": t.id,
                    "PLACA": t.placa,
                    "MARCA": t.marca,
                    "MODELO": t.modelo if t.modelo else "-",
                    "CARROCERIA": t.carroceria if t.carroceria else "-",
                    "EJES": t.numero_ejes,
                    "ESTADO": t.estado
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, width="stretch", hide_index=True)
        else:
            st.info("No hay trailers registrados. Importa desde Excel o crea uno nuevo.")
    
    with tab3:
        st.subheader("Editar/Eliminar Trailer")
        
        trailers = db.query(Trailer).order_by(Trailer.placa).all()
        
        if trailers:
            # Selector de trailer
            trailer_options = {t.id: f"{t.placa} - {t.marca}" for t in trailers}
            selected_id = st.selectbox("Seleccionar trailer", options=list(trailer_options.keys()),
                                        format_func=lambda x: trailer_options.get(x, ""))
            
            if selected_id:
                trailer = db.query(Trailer).filter(Trailer.id == selected_id).first()
                
                if trailer:
                    with st.form("edit_trailer_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edit_placa = st.text_input("Placa", value=trailer.placa, disabled=True)
                            st.caption("La placa no se puede editar")
                            edit_marca = st.text_input("Marca", value=trailer.marca)
                            edit_modelo = st.text_input("Modelo", value=trailer.modelo if trailer.modelo else "")
                        
                        with col2:
                            edit_carroceria = st.text_input("Carrocería", value=trailer.carroceria if trailer.carroceria else "")
                            edit_ejes = st.number_input("Número de ejes", min_value=1, value=trailer.numero_ejes)
                            edit_estado = st.selectbox("Estado", ["Activo", "Mantenimiento", "Inactivo"],
                                                       index=["Activo", "Mantenimiento", "Inactivo"].index(trailer.estado) if trailer.estado in ["Activo", "Mantenimiento", "Inactivo"] else 0)
                        
                        col_btn1, col_btn2 = st.columns(2)
                        
                        with col_btn1:
                            if st.form_submit_button("💾 Guardar Cambios", use_container_width=True):
                                trailer.marca = edit_marca
                                trailer.modelo = edit_modelo
                                trailer.carroceria = edit_carroceria
                                trailer.numero_ejes = edit_ejes
                                trailer.estado = edit_estado
                                db.commit()
                                st.success("Trailer actualizado correctamente")
                                st.rerun()
                        
                        with col_btn2:
                            if st.form_submit_button("🗑️ Eliminar Trailer", use_container_width=True):
                                db.delete(trailer)
                                db.commit()
                                st.success("Trailer eliminado correctamente")
                                st.rerun()
        else:
            st.info("No hay trailers para editar")
    
    db.close()
