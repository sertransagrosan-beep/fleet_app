# modules/vehicles.py

import streamlit as st
import pandas as pd
from datetime import date

from database.db import SessionLocal
from database.models import Vehicle, Trailer, Driver


def vehicles_page():
    st.title("🚛 Vehículos")
    
    db = SessionLocal()
    
    # Pestañas para organizar mejor
    tab1, tab2, tab3 = st.tabs(["📋 Listar", "📝 Registrar", "✏️ Editar/Eliminar"])
    
    with tab1:
        st.subheader("Registrar Vehículo")
        
        with st.form("vehicle_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                placa = st.text_input("Placa *").upper()
                marca = st.text_input("Marca *")
                linea = st.text_input("Línea")
                modelo = st.text_input("Modelo")
                color = st.text_input("Color")
            
            with col2:
                capacidad_carga = st.text_input("Capacidad de carga (toneladas)")
                tipo_combustible = st.selectbox(
                    "Tipo combustible",
                    ["Diesel", "Gasolina", "Gas", "Eléctrico", "Híbrido"]
                )
                soat = st.date_input("SOAT", value=None)
                tecnomecanica = st.date_input("Tecnomecánica", value=None)
                kilometraje_actual = st.number_input("Kilometraje actual", min_value=0, value=0)
            
            # Asignaciones habituales
            st.divider()
            st.subheader("Asignaciones Habituales")
            
            col3, col4 = st.columns(2)
            
            with col3:
                # Obtener trailers activos
                trailers = db.query(Trailer).filter(Trailer.estado == "Activo").order_by(Trailer.placa).all()
                trailer_options = {"": "Sin trailer asignado"}
                trailer_options.update({t.id: f"{t.placa} - {t.marca}" for t in trailers})
                
                trailer_habitual_id = st.selectbox(
                    "Trailer habitual",
                    options=list(trailer_options.keys()),
                    format_func=lambda x: trailer_options.get(x, ""),
                    index=0
                )
            
            with col4:
                # Obtener conductores activos
                drivers = db.query(Driver).filter(Driver.estado == "Activo").order_by(Driver.nombre).all()
                driver_options = {"": "Sin conductor asignado"}
                driver_options.update({d.id: f"{d.nombre} - {d.identificacion}" for d in drivers})
                
                conductor_habitual_id = st.selectbox(
                    "Conductor habitual",
                    options=list(driver_options.keys()),
                    format_func=lambda x: driver_options.get(x, ""),
                    index=0
                )
            
            estado = st.selectbox("Estado", ["Activo", "Mantenimiento", "Inactivo"])
            
            submitted = st.form_submit_button("Guardar", width="stretch")
            
            if submitted:
                if not placa:
                    st.error("La placa es obligatoria")
                elif not marca:
                    st.error("La marca es obligatoria")
                else:
                    # Verificar si ya existe
                    existe = db.query(Vehicle).filter(Vehicle.placa == placa).first()
                    if existe:
                        st.error(f"Ya existe un vehículo con placa {placa}")
                    else:
                        nuevo = Vehicle(
                            placa=placa,
                            marca=marca,
                            linea=linea,
                            modelo=modelo,
                            color=color,
                            capacidad_carga=capacidad_carga,
                            tipo_combustible=tipo_combustible,
                            soat=soat,
                            tecnomecanica=tecnomecanica,
                            kilometraje_actual=kilometraje_actual,
                            estado=estado,
                            trailer_habitual_id=int(trailer_habitual_id) if trailer_habitual_id and trailer_habitual_id != "" else None,
                            conductor_habitual_id=int(conductor_habitual_id) if conductor_habitual_id and conductor_habitual_id != "" else None
                        )
                        db.add(nuevo)
                        db.commit()
                        st.success(f"Vehículo {placa} registrado correctamente")
                        st.rerun()
    
    with tab2:
        st.subheader("Lista de Vehículos")
        
        vehicles = db.query(Vehicle).order_by(Vehicle.placa).all()
        
        if vehicles:
            data = []
            for v in vehicles:
                # Obtener nombres de trailer y conductor habitual
                trailer_habitual = v.trailer_habitual.placa if v.trailer_habitual else "-"
                conductor_habitual = v.conductor_habitual.nombre if v.conductor_habitual else "-"
                
                data.append({
                    "ID": v.id,
                    "PLACA": v.placa,
                    "MARCA": v.marca,
                    "LINEA": v.linea if v.linea else "-",
                    "MODELO": v.modelo if v.modelo else "-",
                    "COLOR": v.color if v.color else "-",
                    "SOAT": v.soat.strftime("%Y-%m-%d") if v.soat else "-",
                    "TECNOMECANICA": v.tecnomecanica.strftime("%Y-%m-%d") if v.tecnomecanica else "-",
                    "KILOMETRAJE": v.kilometraje_actual,
                    "TRAILER HABITUAL": trailer_habitual,
                    "CONDUCTOR HABITUAL": conductor_habitual,
                    "ESTADO": v.estado
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, width="stretch", hide_index=True)
        else:
            st.info("No hay vehículos registrados. Importa desde Excel o crea uno nuevo.")
    
    with tab3:
        st.subheader("Editar/Eliminar Vehículo")
        
        vehicles = db.query(Vehicle).order_by(Vehicle.placa).all()
        
        if vehicles:
            # Selector de vehículo
            vehicle_options = {v.id: f"{v.placa} - {v.marca} {v.linea}" for v in vehicles}
            selected_id = st.selectbox("Seleccionar vehículo", options=list(vehicle_options.keys()),
                                        format_func=lambda x: vehicle_options.get(x, ""))
            
            if selected_id:
                vehicle = db.query(Vehicle).filter(Vehicle.id == selected_id).first()
                
                if vehicle:
                    with st.form("edit_vehicle_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edit_placa = st.text_input("Placa", value=vehicle.placa, disabled=True)
                            st.caption("La placa no se puede editar")
                            edit_marca = st.text_input("Marca", value=vehicle.marca)
                            edit_linea = st.text_input("Línea", value=vehicle.linea if vehicle.linea else "")
                            edit_modelo = st.text_input("Modelo", value=vehicle.modelo if vehicle.modelo else "")
                            edit_color = st.text_input("Color", value=vehicle.color if vehicle.color else "")
                        
                        with col2:
                            edit_capacidad = st.text_input("Capacidad de carga", value=vehicle.capacidad_carga if vehicle.capacidad_carga else "")
                            edit_combustible = st.selectbox("Tipo combustible", 
                                                           ["Diesel", "Gasolina", "Gas", "Eléctrico", "Híbrido"],
                                                           index=["Diesel", "Gasolina", "Gas", "Eléctrico", "Híbrido"].index(vehicle.tipo_combustible) if vehicle.tipo_combustible in ["Diesel", "Gasolina", "Gas", "Eléctrico", "Híbrido"] else 0)
                            edit_soat = st.date_input("SOAT", value=vehicle.soat if vehicle.soat else date.today())
                            edit_tecnomecanica = st.date_input("Tecnomecánica", value=vehicle.tecnomecanica if vehicle.tecnomecanica else date.today())
                            edit_kilometraje = st.number_input("Kilometraje actual", value=vehicle.kilometraje_actual if vehicle.kilometraje_actual else 0)
                        
                        # Asignaciones habituales
                        st.divider()
                        st.subheader("Asignaciones Habituales")
                        
                        col3, col4 = st.columns(2)
                        
                        with col3:
                            # Obtener trailers activos
                            trailers = db.query(Trailer).filter(Trailer.estado == "Activo").order_by(Trailer.placa).all()
                            trailer_options = {"": "Sin trailer asignado"}
                            trailer_options.update({t.id: f"{t.placa} - {t.marca}" for t in trailers})
                            
                            # Encontrar índice actual
                            current_trailer_index = 0
                            if vehicle.trailer_habitual_id:
                                trailer_keys = list(trailer_options.keys())
                                if vehicle.trailer_habitual_id in trailer_keys:
                                    current_trailer_index = trailer_keys.index(vehicle.trailer_habitual_id)
                            
                            edit_trailer_habitual = st.selectbox(
                                "Trailer habitual",
                                options=list(trailer_options.keys()),
                                format_func=lambda x: trailer_options.get(x, ""),
                                index=current_trailer_index
                            )
                        
                        with col4:
                            # Obtener conductores activos
                            drivers = db.query(Driver).filter(Driver.estado == "Activo").order_by(Driver.nombre).all()
                            driver_options = {"": "Sin conductor asignado"}
                            driver_options.update({d.id: f"{d.nombre} - {d.identificacion}" for d in drivers})
                            
                            # Encontrar índice actual
                            current_driver_index = 0
                            if vehicle.conductor_habitual_id:
                                driver_keys = list(driver_options.keys())
                                if vehicle.conductor_habitual_id in driver_keys:
                                    current_driver_index = driver_keys.index(vehicle.conductor_habitual_id)
                            
                            edit_conductor_habitual = st.selectbox(
                                "Conductor habitual",
                                options=list(driver_options.keys()),
                                format_func=lambda x: driver_options.get(x, ""),
                                index=current_driver_index
                            )
                        
                        edit_estado = st.selectbox("Estado", ["Activo", "Mantenimiento", "Inactivo"],
                                                   index=["Activo", "Mantenimiento", "Inactivo"].index(vehicle.estado) if vehicle.estado in ["Activo", "Mantenimiento", "Inactivo"] else 0)
                        
                        col_btn1, col_btn2 = st.columns(2)
                        
                        with col_btn1:
                            if st.form_submit_button("💾 Guardar Cambios", width="stretch"):
                                vehicle.marca = edit_marca
                                vehicle.linea = edit_linea
                                vehicle.modelo = edit_modelo
                                vehicle.color = edit_color
                                vehicle.capacidad_carga = edit_capacidad
                                vehicle.tipo_combustible = edit_combustible
                                vehicle.soat = edit_soat
                                vehicle.tecnomecanica = edit_tecnomecanica
                                vehicle.kilometraje_actual = edit_kilometraje
                                vehicle.estado = edit_estado
                                vehicle.trailer_habitual_id = int(edit_trailer_habitual) if edit_trailer_habitual and edit_trailer_habitual != "" else None
                                vehicle.conductor_habitual_id = int(edit_conductor_habitual) if edit_conductor_habitual and edit_conductor_habitual != "" else None
                                db.commit()
                                st.success("Vehículo actualizado correctamente")
                                st.rerun()
                        
                        with col_btn2:
                            if st.form_submit_button("🗑️ Eliminar Vehículo", width="stretch"):
                                db.delete(vehicle)
                                db.commit()
                                st.success("Vehículo eliminado correctamente")
                                st.rerun()
        else:
            st.info("No hay vehículos para editar")
    
    db.close()
