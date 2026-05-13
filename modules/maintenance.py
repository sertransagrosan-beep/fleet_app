# modules/maintenance.py

import streamlit as st
import pandas as pd
from datetime import date

from database.db import SessionLocal
from database.models import Maintenance, Vehicle, Trailer, Driver


def maintenance_page():
    st.title("🔧 Mantenimientos")
    
    db = SessionLocal()
    
    # Inicializar estado de sesión para limpiar formulario
    if "maintenance_form_submitted" not in st.session_state:
        st.session_state.maintenance_form_submitted = False
    
    # Pestañas
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Registrar", "📋 Listar", "🔍 Consultar", "✏️ Editar/Eliminar"])
    
    # ==================================================
    # TAB 1: REGISTRAR MANTENIMIENTO (con limpieza)
    # ==================================================
    with tab1:
        st.subheader("Registrar Mantenimiento")
        
        # Obtener todos los vehículos activos
        vehicles = db.query(Vehicle).filter(Vehicle.estado == "Activo").order_by(Vehicle.placa).all()
        
        if not vehicles:
            st.warning("⚠️ No hay vehículos registrados. Primero importa o crea vehículos.")
            db.close()
            return
        
        vehicle_options = {v.id: f"{v.placa} - {v.marca} {v.linea}" for v in vehicles}
        
        # Resetear selección si se acaba de guardar
        if st.session_state.maintenance_form_submitted:
            st.session_state.selected_vehicle_id = list(vehicle_options.keys())[0] if vehicle_options else None
            st.session_state.maintenance_form_submitted = False
        
        if "selected_vehicle_id" not in st.session_state:
            st.session_state.selected_vehicle_id = list(vehicle_options.keys())[0] if vehicle_options else None
        
        selected_vehicle_id = st.selectbox(
            "🚛 Seleccione Vehículo",
            options=list(vehicle_options.keys()),
            format_func=lambda x: vehicle_options.get(x, ""),
            key="vehicle_selector"
        )
        st.session_state.selected_vehicle_id = selected_vehicle_id
        
        # Obtener el vehículo seleccionado
        vehicle_selected = db.query(Vehicle).filter(Vehicle.id == selected_vehicle_id).first()
        
        # Mostrar información del vehículo
        if vehicle_selected:
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.metric("Vehículo", vehicle_selected.placa)
            with col_info2:
                st.metric("Marca", vehicle_selected.marca)
            with col_info3:
                st.metric("Modelo", vehicle_selected.modelo if vehicle_selected.modelo else "-")
        
        with st.form("maintenance_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Trailer habitual
                default_trailer_id = None
                if vehicle_selected and vehicle_selected.trailer_habitual_id:
                    default_trailer_id = vehicle_selected.trailer_habitual_id
                
                trailers = db.query(Trailer).filter(Trailer.estado == "Activo").order_by(Trailer.placa).all()
                trailer_options = {None: "📦 Sin trailer"}
                for t in trailers:
                    trailer_options[t.id] = f"{t.placa} - {t.marca}"
                
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
                # Conductor habitual
                default_driver_id = None
                if vehicle_selected and vehicle_selected.conductor_habitual_id:
                    default_driver_id = vehicle_selected.conductor_habitual_id
                
                drivers = db.query(Driver).filter(Driver.estado == "Activo").order_by(Driver.nombre).all()
                driver_options = {None: "👤 Sin conductor"}
                for d in drivers:
                    driver_options[d.id] = f"{d.nombre} - {d.identificacion}"
                
                default_driver_index = list(driver_options.keys()).index(None)
                if default_driver_id in driver_options:
                    default_driver_index = list(driver_options.keys()).index(default_driver_id)
                
                conductor_id = st.selectbox(
                    "👨‍✈️ Conductor",
                    options=list(driver_options.keys()),
                    format_func=lambda x: driver_options.get(x, ""),
                    index=default_driver_index
                )
            
            # Mostrar asignaciones habituales
            if vehicle_selected:
                info_text = []
                if vehicle_selected.trailer_habitual:
                    info_text.append(f"**Trailer habitual:** {vehicle_selected.trailer_habitual.placa}")
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
                descripcion = st.text_area("📝 Descripción", height=100)
                observaciones = st.text_area("💬 Observaciones", height=100)
            
            submitted = st.form_submit_button("💾 Registrar Mantenimiento", use_container_width=True)
            
            if submitted:
                # Validaciones
                errores = []
                
                if not selected_vehicle_id:
                    errores.append("El vehículo es obligatorio")
                
                # Verificar duplicado
                duplicado = db.query(Maintenance).filter(
                    Maintenance.vehiculo_id == selected_vehicle_id,
                    Maintenance.fecha_ingreso == fecha_ingreso,
                    Maintenance.tipo_mantenimiento == tipo_mantenimiento
                ).first()
                
                if duplicado:
                    errores.append(f"Ya existe un mantenimiento del tipo '{tipo_mantenimiento}' para este vehículo en la fecha {fecha_ingreso}")
                
                if errores:
                    for error in errores:
                        st.error(f"❌ {error}")
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
                    
                    # Mostrar mensaje de éxito
                    st.success(f"✅ ¡Mantenimiento registrado con éxito!\n\n"
                              f"**Vehículo:** {vehicle_selected.placa}\n"
                              f"**Fecha:** {fecha_ingreso}\n"
                              f"**Tipo:** {tipo_mantenimiento}")
                    
                    # Marcar para limpiar el formulario y recargar
                    st.session_state.maintenance_form_submitted = True
                    st.rerun()
    
    # ==================================================
    # TAB 2: LISTAR MANTENIMIENTOS (con columna Descripción)
    # ==================================================
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
                    "DESCRIPCIÓN": (m.descripcion[:80] + "...") if m.descripcion and len(m.descripcion) > 80 else (m.descripcion if m.descripcion else "-"),
                    "ESTADO": m.estado
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, width="stretch", hide_index=True)
            
            # Exportar lista completa
            if st.button("📎 Exportar lista completa a Excel", use_container_width=True):
                # Exportar con datos completos (descripción sin truncar)
                data_full = []
                for m in maintenances:
                    data_full.append({
                        "ID": m.id,
                        "FECHA": m.fecha_ingreso.strftime("%Y-%m-%d") if m.fecha_ingreso else "-",
                        "VEHÍCULO": m.vehicle.placa if m.vehicle else "-",
                        "TRAILER": m.trailer.placa if m.trailer else "-",
                        "CONDUCTOR": m.driver.nombre if m.driver else "-",
                        "TIPO": m.tipo_mantenimiento,
                        "TALLER": m.taller if m.taller else "-",
                        "DESCRIPCIÓN": m.descripcion if m.descripcion else "-",
                        "OBSERVACIONES": m.observaciones if m.observaciones else "-",
                        "ESTADO": m.estado
                    })
                df_full = pd.DataFrame(data_full)
                df_full.to_excel("mantenimientos_completo.xlsx", index=False)
                st.success("✅ Lista completa exportada a 'mantenimientos_completo.xlsx'")
        else:
            st.info("ℹ️ No hay mantenimientos registrados")
    
    # ==================================================
    # TAB 3: CONSULTAR (con descripción en exportación)
    # ==================================================
    with tab3:
        st.subheader("🔍 Consulta de Mantenimientos")
        
        st.markdown("---")
        st.markdown("### 🎯 Filtros de búsqueda (todos son opcionales)")
        
        # Organizar filtros en columnas
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            # Filtro por vehículo
            vehicles_all = db.query(Vehicle).order_by(Vehicle.placa).all()
            vehicle_list = ["(Todos)"] + [f"{v.placa} - {v.marca} {v.linea}" for v in vehicles_all]
            vehicle_map = {f"{v.placa} - {v.marca} {v.linea}": v.id for v in vehicles_all}
            
            selected_vehicle_display = st.selectbox(
                "🚛 Vehículo",
                options=vehicle_list,
                index=0
            )
            
            selected_vehicle_id = vehicle_map.get(selected_vehicle_display) if selected_vehicle_display != "(Todos)" else None
            
            # Filtro por trailer
            trailers_all = db.query(Trailer).order_by(Trailer.placa).all()
            trailer_list = ["(Todos)"] + [f"{t.placa} - {t.marca} (Modelo: {t.modelo})" for t in trailers_all]
            trailer_map = {f"{t.placa} - {t.marca} (Modelo: {t.modelo})": t.id for t in trailers_all}
            
            selected_trailer_display = st.selectbox(
                "🔗 Trailer",
                options=trailer_list,
                index=0
            )
            
            selected_trailer_id = trailer_map.get(selected_trailer_display) if selected_trailer_display != "(Todos)" else None
        
        with col_f2:
            # Filtro por tipo de mantenimiento
            tipo_list = ["(Todos)", "Preventivo", "Correctivo", "Predictivo", "SOAT", "Tecnomecánica", "Urgente"]
            selected_tipo = st.selectbox(
                "🔧 Tipo de mantenimiento",
                options=tipo_list,
                index=0
            )
            
            # Filtro por estado
            estado_list = ["(Todos)", "Pendiente", "En curso", "Completado", "Cancelado"]
            selected_estado = st.selectbox(
                "📊 Estado",
                options=estado_list,
                index=0
            )
        
        # Segunda fila de filtros
        col_f3, col_f4 = st.columns(2)
        
        with col_f3:
            taller_search = st.text_input(
                "🔍 Buscar taller (búsqueda inteligente)",
                placeholder="Ej: Taller Central, Mecánico Pérez, etc."
            )
        
        with col_f4:
            descripcion_search = st.text_input(
                "📝 Buscar en descripción (búsqueda inteligente)",
                placeholder="Palabra clave en la descripción..."
            )
        
        # Tercera fila: Fechas
        col_f5, col_f6 = st.columns(2)
        
        with col_f5:
            fecha_desde = st.date_input("📅 Fecha desde", value=None)
        
        with col_f6:
            fecha_hasta = st.date_input("📅 Fecha hasta", value=None)
        
        st.markdown("---")
        
        # Construir consulta dinámica
        query = db.query(Maintenance)
        filtros_activos = []
        
        if selected_vehicle_id:
            query = query.filter(Maintenance.vehiculo_id == selected_vehicle_id)
            filtros_activos.append(f"Vehículo: {selected_vehicle_display}")
        
        if selected_trailer_id:
            query = query.filter(Maintenance.trailer_id == selected_trailer_id)
            filtros_activos.append(f"Trailer: {selected_trailer_display}")
        
        if selected_tipo != "(Todos)":
            query = query.filter(Maintenance.tipo_mantenimiento == selected_tipo)
            filtros_activos.append(f"Tipo: {selected_tipo}")
        
        if selected_estado != "(Todos)":
            query = query.filter(Maintenance.estado == selected_estado)
            filtros_activos.append(f"Estado: {selected_estado}")
        
        if taller_search:
            query = query.filter(Maintenance.taller.ilike(f"%{taller_search}%"))
            filtros_activos.append(f"Taller contiene: '{taller_search}'")
        
        if descripcion_search:
            query = query.filter(Maintenance.descripcion.ilike(f"%{descripcion_search}%"))
            filtros_activos.append(f"Descripción contiene: '{descripcion_search}'")
        
        if fecha_desde:
            query = query.filter(Maintenance.fecha_ingreso >= fecha_desde)
            filtros_activos.append(f"Desde: {fecha_desde}")
        
        if fecha_hasta:
            query = query.filter(Maintenance.fecha_ingreso <= fecha_hasta)
            filtros_activos.append(f"Hasta: {fecha_hasta}")
        
        if filtros_activos:
            st.info(f"🔍 **Filtros aplicados ({len(filtros_activos)}):** " + " | ".join(filtros_activos))
        else:
            st.info("🔍 **Mostrando todos los mantenimientos** (sin filtros aplicados)")
        
        maintenances_filtered = query.order_by(Maintenance.fecha_ingreso.desc()).all()
        
        if maintenances_filtered:
            st.success(f"📊 **{len(maintenances_filtered)}** mantenimiento(s) encontrado(s)")
            
            data = []
            for m in maintenances_filtered:
                data.append({
                    "ID": m.id,
                    "FECHA": m.fecha_ingreso.strftime("%Y-%m-%d") if m.fecha_ingreso else "-",
                    "VEHÍCULO": m.vehicle.placa if m.vehicle else "-",
                    "TRAILER": m.trailer.placa if m.trailer else "-",
                    "CONDUCTOR": m.driver.nombre if m.driver else "-",
                    "TIPO": m.tipo_mantenimiento,
                    "TALLER": m.taller if m.taller else "-",
                    "DESCRIPCIÓN": (m.descripcion[:50] + "...") if m.descripcion and len(m.descripcion) > 50 else (m.descripcion if m.descripcion else "-"),
                    "ESTADO": m.estado
                })
            
            df_filtered = pd.DataFrame(data)
            st.dataframe(df_filtered, width="stretch", hide_index=True)
            
            # Botones de exportación
            st.markdown("---")
            st.subheader("📎 Exportar resultados")
            
            col_exp1, col_exp2, col_exp3 = st.columns(3)
            
            with col_exp1:
                if st.button("📎 Exportar resultados actuales a Excel", use_container_width=True):
                    data_full = []
                    for m in maintenances_filtered:
                        data_full.append({
                            "ID": m.id,
                            "FECHA": m.fecha_ingreso.strftime("%Y-%m-%d") if m.fecha_ingreso else "-",
                            "VEHÍCULO": m.vehicle.placa if m.vehicle else "-",
                            "TRAILER": m.trailer.placa if m.trailer else "-",
                            "CONDUCTOR": m.driver.nombre if m.driver else "-",
                            "TIPO": m.tipo_mantenimiento,
                            "TALLER": m.taller if m.taller else "-",
                            "DESCRIPCIÓN": m.descripcion if m.descripcion else "-",
                            "OBSERVACIONES": m.observaciones if m.observaciones else "-",
                            "ESTADO": m.estado
                        })
                    df_full = pd.DataFrame(data_full)
                    df_full.to_excel("mantenimientos_exportados.xlsx", index=False)
                    st.success("✅ Resultados exportados a 'mantenimientos_exportados.xlsx'")
            
            with col_exp2:
                if selected_vehicle_id and selected_vehicle_display != "(Todos)":
                    vehicle_plate = selected_vehicle_display.split(" - ")[0]
                    if st.button(f"📎 Exportar historial de {vehicle_plate}", use_container_width=True):
                        data_full = []
                        for m in maintenances_filtered:
                            data_full.append({
                                "ID": m.id,
                                "FECHA": m.fecha_ingreso.strftime("%Y-%m-%d") if m.fecha_ingreso else "-",
                                "TRAILER": m.trailer.placa if m.trailer else "-",
                                "CONDUCTOR": m.driver.nombre if m.driver else "-",
                                "TIPO": m.tipo_mantenimiento,
                                "TALLER": m.taller if m.taller else "-",
                                "DESCRIPCIÓN": m.descripcion if m.descripcion else "-",
                                "OBSERVACIONES": m.observaciones if m.observaciones else "-",
                                "ESTADO": m.estado
                            })
                        df_historial = pd.DataFrame(data_full)
                        df_historial.to_excel(f"historial_{vehicle_plate}.xlsx", index=False)
                        st.success(f"✅ Historial exportado a 'historial_{vehicle_plate}.xlsx'")
                else:
                    st.info("ℹ️ Selecciona un vehículo específico para exportar su historial")
            
            with col_exp3:
                if st.button("📊 Exportar resumen estadístico", use_container_width=True):
                    resumen_tipo = df_filtered.groupby('TIPO').size().reset_index(name='CANTIDAD')
                    resumen_estado = df_filtered.groupby('ESTADO').size().reset_index(name='CANTIDAD')
                    
                    with pd.ExcelWriter("resumen_mantenimientos.xlsx") as writer:
                        df_filtered.to_excel(writer, sheet_name='Detalle', index=False)
                        resumen_tipo.to_excel(writer, sheet_name='Resumen por Tipo', index=False)
                        resumen_estado.to_excel(writer, sheet_name='Resumen por Estado', index=False)
                    
                    st.success("✅ Resumen exportado a 'resumen_mantenimientos.xlsx'")
            
            # Ver detalles
            st.markdown("---")
            st.subheader("🔍 Ver detalles completos")
            
            mantenimiento_ids = [m.id for m in maintenances_filtered]
            sel_id = st.selectbox("Seleccionar mantenimiento para ver detalles", mantenimiento_ids)
            
            if sel_id:
                m = db.query(Maintenance).filter(Maintenance.id == sel_id).first()
                if m:
                    with st.expander("📄 Detalles completos", expanded=True):
                        col_d1, col_d2 = st.columns(2)
                        with col_d1:
                            st.write(f"**ID:** {m.id}")
                            st.write(f"**Fecha de ingreso:** {m.fecha_ingreso}")
                            st.write(f"**Vehículo:** {m.vehicle.placa} - {m.vehicle.marca} {m.vehicle.linea}")
                            st.write(f"**Trailer:** {m.trailer.placa if m.trailer else 'No aplica'}")
                            st.write(f"**Conductor:** {m.driver.nombre if m.driver else 'No aplica'}")
                        with col_d2:
                            st.write(f"**Tipo:** {m.tipo_mantenimiento}")
                            st.write(f"**Taller:** {m.taller if m.taller else 'No especificado'}")
                            st.write(f"**Estado:** {m.estado}")
                        
                        st.write(f"**Descripción:**")
                        st.info(m.descripcion if m.descripcion else "Sin descripción")
                        
                        st.write(f"**Observaciones:**")
                        st.info(m.observaciones if m.observaciones else "Sin observaciones")
        else:
            st.warning("⚠️ No hay mantenimientos que coincidan con los filtros seleccionados")
            
            if filtros_activos:
                st.info("💡 **Sugerencia:** Prueba quitando algunos filtros para ampliar la búsqueda")
    
    # ==================================================
    # TAB 4: EDITAR/ELIMINAR
    # ==================================================
    with tab4:
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
                            st.text_input("Vehículo", value=f"{maintenance.vehicle.placa} - {maintenance.vehicle.marca}", disabled=True)
                            
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
                            
                            # Alertas de vencimiento
                            if maintenance.vehicle:
                                st.divider()
                                st.subheader("⚠️ Alertas")
                                
                                hoy = date.today()
                                if maintenance.vehicle.soat:
                                    dias_soat = (maintenance.vehicle.soat - hoy).days
                                    if dias_soat < 0:
                                        st.error(f"❌ SOAT vencido hace {abs(dias_soat)} días")
                                    elif dias_soat < 30:
                                        st.warning(f"⚠️ SOAT vence en {dias_soat} días")
                                    else:
                                        st.success(f"✅ SOAT vigente (vence en {dias_soat} días)")
                                
                                if maintenance.vehicle.tecnomecanica:
                                    dias_tecno = (maintenance.vehicle.tecnomecanica - hoy).days
                                    if dias_tecno < 0:
                                        st.error(f"❌ Tecnomecánica vencida hace {abs(dias_tecno)} días")
                                    elif dias_tecno < 30:
                                        st.warning(f"⚠️ Tecnomecánica vence en {dias_tecno} días")
                                    else:
                                        st.success(f"✅ Tecnomecánica vigente (vence en {dias_tecno} días)")
                        
                        with col2:
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
                            edit_tipo = st.selectbox(
                                "Tipo de mantenimiento",
                                ["Preventivo", "Correctivo", "Predictivo", "SOAT", "Tecnomecánica", "Urgente"],
                                index=["Preventivo", "Correctivo", "Predictivo", "SOAT", "Tecnomecánica", "Urgente"].index(maintenance.tipo_mantenimiento) if maintenance.tipo_mantenimiento in ["Preventivo", "Correctivo", "Predictivo", "SOAT", "Tecnomecánica", "Urgente"] else 0
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
