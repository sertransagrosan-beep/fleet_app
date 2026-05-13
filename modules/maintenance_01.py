# modules/maintenance.py

import streamlit as st
import pandas as pd
from datetime import date

from database.db import SessionLocal
from database.models import Maintenance, Vehicle, Trailer, Driver


def maintenance_page():
    st.title("🔧 Mantenimientos")
    
    db = SessionLocal()
    
    # Pestañas
    tab1, tab2, tab3 = st.tabs(["📝 Registrar", "📋 Listar", "✏️ Editar/Eliminar"])
    
    with tab1:
        st.subheader("Registrar Mantenimiento")
        
        # Obtener todos los vehículos activos
        vehicles = db.query(Vehicle).filter(Vehicle.estado == "Activo").order_by(Vehicle.placa).all()
        
        if not vehicles:
            st.warning("⚠️ No hay vehículos registrados. Primero importa o crea vehículos.")
            db.close()
            return
        
        vehicle_options = {v.id: f"{v.placa} - {v.marca} {v.linea}" for v in vehicles}
        
        # IMPORTANTE: Usar session_state para mantener el vehículo seleccionado
        if "selected_vehicle_id" not in st.session_state:
            st.session_state.selected_vehicle_id = list(vehicle_options.keys())[0] if vehicle_options else None
        
        # Selector de vehículo FUERA del formulario para que actualice dinámicamente
        col_vehiculo, col_info = st.columns([2, 1])
        
        with col_vehiculo:
            selected_vehicle_id = st.selectbox(
                "🚛 Seleccione Vehículo",
                options=list(vehicle_options.keys()),
                format_func=lambda x: vehicle_options.get(x, ""),
                key="vehicle_selector"
            )
            st.session_state.selected_vehicle_id = selected_vehicle_id
        
        # Obtener el vehículo seleccionado
        vehicle_selected = db.query(Vehicle).filter(Vehicle.id == selected_vehicle_id).first()
        
        # Mostrar información del vehículo seleccionado
        with col_info:
            if vehicle_selected:
                st.info(f"**Vehículo:** {vehicle_selected.placa}\n\n**Marca:** {vehicle_selected.marca}\n\n**Modelo:** {vehicle_selected.modelo}")
        
        # Ahora el formulario con los datos que se actualizarán dinámicamente
        with st.form("maintenance_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Mostrar trailer habitual por defecto (pero permitir cambiar)
                default_trailer_id = None
                default_trailer_text = "Sin trailer asignado"
                
                if vehicle_selected and vehicle_selected.trailer_habitual_id:
                    default_trailer_id = vehicle_selected.trailer_habitual_id
                    default_trailer = db.query(Trailer).filter(Trailer.id == default_trailer_id).first()
                    if default_trailer:
                        default_trailer_text = f"🔄 {default_trailer.placa} - {default_trailer.marca} (Habitual)"
                
                # Selector de trailer
                trailers = db.query(Trailer).filter(Trailer.estado == "Activo").order_by(Trailer.placa).all()
                trailer_options = {None: "📦 Sin trailer"}
                for t in trailers:
                    trailer_options[t.id] = f"{t.placa} - {t.marca}"
                
                # Determinar índice por defecto
                default_trailer_index = list(trailer_options.keys()).index(None)
                if default_trailer_id in trailer_options:
                    default_trailer_index = list(trailer_options.keys()).index(default_trailer_id)
                
                trailer_id = st.selectbox(
                    "🔗 Trailer",
                    options=list(trailer_options.keys()),
                    format_func=lambda x: trailer_options.get(x, ""),
                    index=default_trailer_index
                )
            
            with col2:
                # Mostrar conductor habitual por defecto
                default_driver_id = None
                default_driver_text = "Sin conductor asignado"
                
                if vehicle_selected and vehicle_selected.conductor_habitual_id:
                    default_driver_id = vehicle_selected.conductor_habitual_id
                    default_driver = db.query(Driver).filter(Driver.id == default_driver_id).first()
                    if default_driver:
                        default_driver_text = f"👨‍✈️ {default_driver.nombre} (Habitual)"
                
                # Selector de conductor
                drivers = db.query(Driver).filter(Driver.estado == "Activo").order_by(Driver.nombre).all()
                driver_options = {None: "👤 Sin conductor"}
                for d in drivers:
                    driver_options[d.id] = f"{d.nombre} - {d.identificacion}"
                
                # Determinar índice por defecto
                default_driver_index = list(driver_options.keys()).index(None)
                if default_driver_id in driver_options:
                    default_driver_index = list(driver_options.keys()).index(default_driver_id)
                
                conductor_id = st.selectbox(
                    "👨‍✈️ Conductor",
                    options=list(driver_options.keys()),
                    format_func=lambda x: driver_options.get(x, ""),
                    index=default_driver_index
                )
            
            # Mostrar información de asignaciones habituales
            if vehicle_selected:
                info_text = []
                if vehicle_selected.trailer_habitual:
                    info_text.append(f"**Trailer habitual:** {vehicle_selected.trailer_habitual.placa} - {vehicle_selected.trailer_habitual.marca}")
                if vehicle_selected.conductor_habitual:
                    info_text.append(f"**Conductor habitual:** {vehicle_selected.conductor_habitual.nombre}")
                
                if info_text:
                    st.info(" | ".join(info_text))
            
            st.divider()
            
            col3, col4 = st.columns(2)
            
            with col3:
                fecha_ingreso = st.date_input("📅 Fecha de ingreso", value=date.today())
                tipo_mantenimiento = st.selectbox(
                    "🔧 Tipo de mantenimiento",
                    ["Preventivo", "Correctivo", "Predictivo", "SOAT", "Tecnomecánica", "Urgente"]
                )
                taller = st.text_input("🏪 Taller / Mecánico")
            
            with col4:
                estado = st.selectbox(
                    "📊 Estado",
                    ["Pendiente", "En curso", "Completado", "Cancelado"]
                )
                descripcion = st.text_area("📝 Descripción del trabajo realizado", height=100)
                observaciones = st.text_area("💬 Observaciones", height=100)
            
            submitted = st.form_submit_button("💾 Registrar Mantenimiento", use_container_width=True)
            
            if submitted:
                if not selected_vehicle_id:
                    st.error("El vehículo es obligatorio")
                else:
                    nuevo = Maintenance(
                        fecha_ingreso=fecha_ingreso,
                        vehiculo_id=selected_vehicle_id,
                        trailer_id=trailer_id if trailer_id != "None" else None,
                        conductor_id=conductor_id if conductor_id != "None" else None,
                        tipo_mantenimiento=tipo_mantenimiento,
                        descripcion=descripcion,
                        observaciones=observaciones,
                        taller=taller,
                        estado=estado
                    )
                    db.add(nuevo)
                    db.commit()
                    st.success(f"✅ Mantenimiento registrado para el vehículo {vehicle_selected.placa}")
                    st.rerun()
    
    with tab2:
        st.subheader("📋 Lista de Mantenimientos")
        
        maintenances = db.query(Maintenance).order_by(Maintenance.fecha_ingreso.desc()).all()
        
        if maintenances:
            data = []
            for m in maintenances:
                data.append({
                    "ID": m.id,
                    "FECHA": m.fecha_ingreso.strftime("%Y-%m-%d") if m.fecha_ingreso else "-",
                    "VEHÍCULO": m.vehicle.placa if m.vehicle else "-",
                    "TRAILER": m.trailer.placa if m.trailer else "-",
                    "CONDUCTOR": m.driver.nombre if m.driver else "-",
                    "TIPO": m.tipo_mantenimiento,
                    "TALLER": m.taller if m.taller else "-",
                    "ESTADO": m.estado
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, width="stretch", hide_index=True)
            
            # Ver detalles
            st.subheader("🔍 Ver detalles")
            mantenimiento_ids = [m.id for m in maintenances]
            sel_id = st.selectbox("Seleccionar mantenimiento", mantenimiento_ids)
            
            if sel_id:
                m = db.query(Maintenance).filter(Maintenance.id == sel_id).first()
                if m:
                    with st.expander("📄 Detalles completos", expanded=True):
                        st.write(f"**Descripción:** {m.descripcion if m.descripcion else 'No especificada'}")
                        st.write(f"**Observaciones:** {m.observaciones if m.observaciones else 'No especificadas'}")
        else:
            st.info("ℹ️ No hay mantenimientos registrados")
    
    with tab3:
        st.subheader("✏️ Editar/Eliminar Mantenimiento")
        
        maintenances = db.query(Maintenance).order_by(Maintenance.fecha_ingreso.desc()).all()
        
        if maintenances:
            maintenance_options = {m.id: f"#{m.id} - {m.vehicle.placa} - {m.fecha_ingreso} - {m.estado}" for m in maintenances}
            selected_id = st.selectbox("Seleccionar mantenimiento", options=list(maintenance_options.keys()),
                                        format_func=lambda x: maintenance_options.get(x, ""))
            
            if selected_id:
                maintenance = db.query(Maintenance).filter(Maintenance.id == selected_id).first()
                
                if maintenance:
                    with st.form("edit_maintenance_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Vehículo (solo mostrar, no editar)
                            st.text_input("Vehículo", value=f"{maintenance.vehicle.placa} - {maintenance.vehicle.marca}", disabled=True)
                            
                            # Trailer
                            trailers = db.query(Trailer).filter(Trailer.estado == "Activo").all()
                            trailer_options_edit = {None: "Sin trailer"}
                            for t in trailers:
                                trailer_options_edit[t.id] = f"{t.placa} - {t.marca}"
                            
                            edit_trailer_id = st.selectbox(
                                "Trailer",
                                options=list(trailer_options_edit.keys()),
                                format_func=lambda x: trailer_options_edit.get(x, ""),
                                index=list(trailer_options_edit.keys()).index(maintenance.trailer_id) if maintenance.trailer_id in trailer_options_edit else 0
                            )
                            
                            edit_fecha = st.date_input("Fecha", value=maintenance.fecha_ingreso)
                            edit_tipo = st.selectbox(
                                "Tipo de mantenimiento",
                                ["Preventivo", "Correctivo", "Predictivo", "SOAT", "Tecnomecánica", "Urgente"],
                                index=["Preventivo", "Correctivo", "Predictivo", "SOAT", "Tecnomecánica", "Urgente"].index(maintenance.tipo_mantenimiento) if maintenance.tipo_mantenimiento in ["Preventivo", "Correctivo", "Predictivo", "SOAT", "Tecnomecánica", "Urgente"] else 0
                            )
                        
                        with col2:
                            # Conductor
                            drivers = db.query(Driver).filter(Driver.estado == "Activo").all()
                            driver_options_edit = {None: "Sin conductor"}
                            for d in drivers:
                                driver_options_edit[d.id] = f"{d.nombre} - {d.identificacion}"
                            
                            edit_conductor_id = st.selectbox(
                                "Conductor",
                                options=list(driver_options_edit.keys()),
                                format_func=lambda x: driver_options_edit.get(x, ""),
                                index=list(driver_options_edit.keys()).index(maintenance.conductor_id) if maintenance.conductor_id in driver_options_edit else 0
                            )
                            
                            edit_taller = st.text_input("Taller", value=maintenance.taller if maintenance.taller else "")
                            edit_estado = st.selectbox(
                                "Estado",
                                ["Pendiente", "En curso", "Completado", "Cancelado"],
                                index=["Pendiente", "En curso", "Completado", "Cancelado"].index(maintenance.estado) if maintenance.estado in ["Pendiente", "En curso", "Completado", "Cancelado"] else 0
                            )
                        
                        edit_descripcion = st.text_area("Descripción", value=maintenance.descripcion if maintenance.descripcion else "", height=100)
                        edit_observaciones = st.text_area("Observaciones", value=maintenance.observaciones if maintenance.observaciones else "", height=100)
                        
                        col_btn1, col_btn2 = st.columns(2)
                        
                        with col_btn1:
                            if st.form_submit_button("💾 Guardar Cambios", use_container_width=True):
                                maintenance.fecha_ingreso = edit_fecha
                                maintenance.trailer_id = edit_trailer_id if edit_trailer_id != "None" else None
                                maintenance.conductor_id = edit_conductor_id if edit_conductor_id != "None" else None
                                maintenance.tipo_mantenimiento = edit_tipo
                                maintenance.descripcion = edit_descripcion
                                maintenance.observaciones = edit_observaciones
                                maintenance.taller = edit_taller
                                maintenance.estado = edit_estado
                                db.commit()
                                st.success("✅ Mantenimiento actualizado correctamente")
                                st.rerun()
                        
                        with col_btn2:
                            if st.form_submit_button("🗑️ Eliminar Mantenimiento", use_container_width=True):
                                db.delete(maintenance)
                                db.commit()
                                st.success("✅ Mantenimiento eliminado correctamente")
                                st.rerun()
        else:
            st.info("ℹ️ No hay mantenimientos para editar")
    
    db.close()