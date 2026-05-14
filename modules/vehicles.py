# modules/vehicles.py - VERSIÓN CON ALERTAS DE VENCIMIENTO

import streamlit as st
import pandas as pd
from datetime import date

from database.db import SessionLocal
from database.models import Vehicle, Trailer, Driver


def vehicles_page():
    st.title("🚛 Vehículos")
    
    db = SessionLocal()
    
    # Orden: Listar, Registrar, Editar/Eliminar
    tab1, tab2, tab3 = st.tabs(["📋 Listar", "📝 Registrar", "✏️ Editar/Eliminar"])
    
    # ==================================================
    # TAB 1: LISTAR (con alertas de vencimiento)
    # ==================================================
    with tab1:
        st.subheader("Lista de Vehículos")
        
        vehicles = db.query(Vehicle).order_by(Vehicle.placa).all()
        
        if vehicles:
            hoy = date.today()
            data = []
            
            for v in vehicles:
                # Calcular estado de SOAT
                soat_estado = ""
                soat_color = ""
                if v.soat:
                    dias_soat = (v.soat - hoy).days
                    if dias_soat < 0:
                        soat_estado = f"⚠️ VENCIDO (hace {abs(dias_soat)} días)"
                        soat_color = "red"
                    elif dias_soat <= 30:
                        soat_estado = f"⚠️ {dias_soat} días"
                        soat_color = "orange"
                    else:
                        soat_estado = f"✅ Restan ({dias_soat} días)"
                        soat_color = "green"
                else:
                    soat_estado = "No registrado"
                    soat_color = "gray"
                
                # Calcular estado de Tecnomecánica
                tecno_estado = ""
                tecno_color = ""
                if v.tecnomecanica:
                    dias_tecno = (v.tecnomecanica - hoy).days
                    if dias_tecno < 0:
                        tecno_estado = f"⚠️ VENCIDO (hace {abs(dias_tecno)} días)"
                        tecno_color = "red"
                    elif dias_tecno <= 30:
                        tecno_estado = f"⚠️ {dias_tecno} días"
                        tecno_color = "orange"
                    else:
                        tecno_estado = f"✅ Restan ({dias_tecno} días)"
                        tecno_color = "green"
                else:
                    tecno_estado = "No registrado"
                    tecno_color = "gray"
                
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
                    "SOAT_ESTADO": soat_estado,
                    "TECNOMECANICA": v.tecnomecanica.strftime("%Y-%m-%d") if v.tecnomecanica else "-",
                    "TECNOMECANICA_ESTADO": tecno_estado,
                    "KILOMETRAJE": v.kilometraje_actual,
                    "TRAILER HABITUAL": trailer_habitual,
                    "CONDUCTOR HABITUAL": conductor_habitual,
                    "ESTADO": v.estado
                })
            
            df = pd.DataFrame(data)
            
            # Mostrar tabla con colores condicionales usando st.markdown
            st.dataframe(df, width="stretch", hide_index=True)
            
            # Mostrar leyenda de colores
            st.markdown("""
            **Leyenda de alertas:**
            - 🟢 **Verde:** Restan (más de 30 días para vencer)
            - 🟠 **Naranja:** Próximo a vencer (30 días o menos)
            - 🔴 **Rojo:** Vencido
            """)
        else:
            st.info("No hay vehículos registrados.")
    
    # ==================================================
    # TAB 2: REGISTRAR
    # ==================================================
    with tab2:
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
            
            st.divider()
            st.subheader("Asignaciones Habituales")
            
            col3, col4 = st.columns(2)
            
            with col3:
                trailers = db.query(Trailer).filter(Trailer.estado == "Activo").order_by(Trailer.placa).all()
                trailer_options = {"": "Sin trailer asignado"}
                trailer_options.update({t.id: f"{t.placa} - {t.marca}" for t in trailers})
                trailer_habitual_id = st.selectbox("Trailer habitual", options=list(trailer_options.keys()),
                                                    format_func=lambda x: trailer_options.get(x, ""), index=0)
            
            with col4:
                drivers = db.query(Driver).filter(Driver.estado == "Activo").order_by(Driver.nombre).all()
                driver_options = {"": "Sin conductor asignado"}
                driver_options.update({d.id: f"{d.nombre} - {d.identificacion}" for d in drivers})
                conductor_habitual_id = st.selectbox("Conductor habitual", options=list(driver_options.keys()),
                                                      format_func=lambda x: driver_options.get(x, ""), index=0)
            
            estado = st.selectbox("Estado", ["Activo", "Mantenimiento", "Inactivo"])
            
            submitted = st.form_submit_button("Guardar", use_container_width=True)
            
            if submitted:
                if not placa:
                    st.error("La placa es obligatoria")
                elif not marca:
                    st.error("La marca es obligatoria")
                else:
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
    
    # ==================================================
    # TAB 3: EDITAR/ELIMINAR
    # ==================================================
    with tab3:
        st.subheader("Editar/Eliminar Vehículo")
        
        vehicles = db.query(Vehicle).order_by(Vehicle.placa).all()
        
        if vehicles:
            vehicle_options = {v.id: f"{v.placa} - {v.marca} {v.linea}" for v in vehicles}
            selected_id = st.selectbox("Seleccionar vehículo", options=list(vehicle_options.keys()),
                                        format_func=lambda x: vehicle_options.get(x, ""))
            
            if selected_id:
                vehicle = db.query(Vehicle).filter(Vehicle.id == selected_id).first()
                
                if vehicle:
                    with st.form("edit_vehicle_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.text_input("Placa", value=vehicle.placa, disabled=True)
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
                        
                        st.divider()
                        st.subheader("Asignaciones Habituales")
                        
                        col3, col4 = st.columns(2)
                        
                        with col3:
                            trailers = db.query(Trailer).filter(Trailer.estado == "Activo").order_by(Trailer.placa).all()
                            trailer_options = {"": "Sin trailer asignado"}
                            trailer_options.update({t.id: f"{t.placa} - {t.marca}" for t in trailers})
                            current_trailer_index = list(trailer_options.keys()).index(vehicle.trailer_habitual_id) if vehicle.trailer_habitual_id in trailer_options else 0
                            edit_trailer_habitual = st.selectbox("Trailer habitual", options=list(trailer_options.keys()),
                                                                  format_func=lambda x: trailer_options.get(x, ""),
                                                                  index=current_trailer_index)
                        
                        with col4:
                            drivers = db.query(Driver).filter(Driver.estado == "Activo").order_by(Driver.nombre).all()
                            driver_options = {"": "Sin conductor asignado"}
                            driver_options.update({d.id: f"{d.nombre} - {d.identificacion}" for d in drivers})
                            current_driver_index = list(driver_options.keys()).index(vehicle.conductor_habitual_id) if vehicle.conductor_habitual_id in driver_options else 0
                            edit_conductor_habitual = st.selectbox("Conductor habitual", options=list(driver_options.keys()),
                                                                    format_func=lambda x: driver_options.get(x, ""),
                                                                    index=current_driver_index)
                        
                        edit_estado = st.selectbox("Estado", ["Activo", "Mantenimiento", "Inactivo"],
                                                   index=["Activo", "Mantenimiento", "Inactivo"].index(vehicle.estado) if vehicle.estado in ["Activo", "Mantenimiento", "Inactivo"] else 0)
                        
                        # Mostrar alertas en edición
                        hoy = date.today()
                        if vehicle.soat:
                            dias_soat = (vehicle.soat - hoy).days
                            if dias_soat < 0:
                                st.error(f"⚠️ SOAT VENCIDO hace {abs(dias_soat)} días")
                            elif dias_soat <= 30:
                                st.warning(f"⚠️ SOAT {dias_soat} días")
                            else:
                                st.success(f"✅ SOAT Restan ({dias_soat} días)")
                        
                        if vehicle.tecnomecanica:
                            dias_tecno = (vehicle.tecnomecanica - hoy).days
                            if dias_tecno < 0:
                                st.error(f"⚠️ Tecnomecánica VENCIDA hace {abs(dias_tecno)} días")
                            elif dias_tecno <= 30:
                                st.warning(f"⚠️ Tecnomecánica {dias_tecno} días")
                            else:
                                st.success(f"✅ Tecnomecánica Restan ({dias_tecno} días)")
                        
                        col_btn1, col_btn2 = st.columns(2)
                        
                        with col_btn1:
                            if st.form_submit_button("💾 Guardar Cambios", use_container_width=True):
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
                            if st.form_submit_button("🗑️ Eliminar Vehículo", use_container_width=True):
                                db.delete(vehicle)
                                db.commit()
                                st.success("Vehículo eliminado correctamente")
                                st.rerun()
        else:
            st.info("No hay vehículos para editar")
    
    db.close()
