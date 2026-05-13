# modules/drivers.py

import streamlit as st
import pandas as pd
from datetime import date

from database.db import SessionLocal
from database.models import Driver


def drivers_page():
    st.title("👨‍✈️ Conductores")
    
    db = SessionLocal()
    
    # Pestañas para organizar mejor
    tab1, tab2, tab3 = st.tabs(["📝 Registrar", "📋 Listar", "✏️ Editar/Eliminar"])
    
    with tab1:
        st.subheader("Registrar Conductor")
        
        with st.form("driver_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("Nombre completo *")
                identificacion = st.text_input("Identificación *")
            
            with col2:
                telefono = st.text_input("Teléfono")
                vencimiento_licencia = st.date_input("Vencimiento licencia", value=None)
                estado = st.selectbox("Estado", ["Activo", "Suspendido", "Inactivo"])
            
            submitted = st.form_submit_button("Guardar", use_container_width=True)
            
            if submitted:
                if not nombre:
                    st.error("El nombre es obligatorio")
                elif not identificacion:
                    st.error("La identificación es obligatoria")
                else:
                    # Verificar si ya existe
                    existe = db.query(Driver).filter(Driver.identificacion == identificacion).first()
                    if existe:
                        st.error(f"Ya existe un conductor con identificación {identificacion}")
                    else:
                        nuevo = Driver(
                            nombre=nombre.upper(),
                            identificacion=identificacion,
                            telefono=telefono,
                            vencimiento_licencia=vencimiento_licencia,
                            estado=estado
                        )
                        db.add(nuevo)
                        db.commit()
                        st.success(f"Conductor {nombre} registrado correctamente")
                        st.rerun()
    
    with tab2:
        st.subheader("Lista de Conductores")
        
        drivers = db.query(Driver).order_by(Driver.nombre).all()
        
        if drivers:
            data = []
            for d in drivers:
                data.append({
                    "ID": d.id,
                    "NOMBRE": d.nombre,
                    "IDENTIFICACION": d.identificacion,
                    "TELEFONO": d.telefono if d.telefono else "-",
                    "VENCIMIENTO LICENCIA": d.vencimiento_licencia.strftime("%Y-%m-%d") if d.vencimiento_licencia else "-",
                    "ESTADO": d.estado
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, width="stretch", hide_index=True)
        else:
            st.info("No hay conductores registrados. Importa desde Excel o crea uno nuevo.")
    
    with tab3:
        st.subheader("Editar/Eliminar Conductor")
        
        drivers = db.query(Driver).order_by(Driver.nombre).all()
        
        if drivers:
            # Selector de conductor
            driver_options = {d.id: f"{d.nombre} - {d.identificacion}" for d in drivers}
            selected_id = st.selectbox("Seleccionar conductor", options=list(driver_options.keys()),
                                        format_func=lambda x: driver_options.get(x, ""))
            
            if selected_id:
                driver = db.query(Driver).filter(Driver.id == selected_id).first()
                
                if driver:
                    with st.form("edit_driver_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edit_nombre = st.text_input("Nombre completo", value=driver.nombre)
                            edit_identificacion = st.text_input("Identificación", value=driver.identificacion, disabled=True)
                            st.caption("La identificación no se puede editar")
                        
                        with col2:
                            edit_telefono = st.text_input("Teléfono", value=driver.telefono if driver.telefono else "")
                            edit_licencia = st.date_input("Vencimiento licencia", 
                                                         value=driver.vencimiento_licencia if driver.vencimiento_licencia else date.today())
                            edit_estado = st.selectbox("Estado", ["Activo", "Suspendido", "Inactivo"],
                                                       index=["Activo", "Suspendido", "Inactivo"].index(driver.estado) if driver.estado in ["Activo", "Suspendido", "Inactivo"] else 0)
                        
                        col_btn1, col_btn2 = st.columns(2)
                        
                        with col_btn1:
                            if st.form_submit_button("💾 Guardar Cambios", use_container_width=True):
                                driver.nombre = edit_nombre.upper()
                                driver.telefono = edit_telefono
                                driver.vencimiento_licencia = edit_licencia
                                driver.estado = edit_estado
                                db.commit()
                                st.success("Conductor actualizado correctamente")
                                st.rerun()
                        
                        with col_btn2:
                            if st.form_submit_button("🗑️ Eliminar Conductor", use_container_width=True):
                                db.delete(driver)
                                db.commit()
                                st.success("Conductor eliminado correctamente")
                                st.rerun()
        else:
            st.info("No hay conductores para editar")
    
    db.close()