# modules/maintenance.py - VERSIÓN COMPLETA CON EXPORTACIÓN A EXCEL CORREGIDA

import streamlit as st
import pandas as pd
from datetime import date
import io

from database.db import SessionLocal
from database.models import Maintenance, Vehicle, Trailer, Driver


# ==================================================
# FUNCIÓN AUXILIAR PARA EXPORTAR A EXCEL
# ==================================================

def exportar_a_excel(data, nombre_archivo, sheet_name="Datos"):
    """
    Exporta datos a Excel manejando correctamente caracteres especiales,
    saltos de línea y comillas.
    """
    df = pd.DataFrame(data)
    df = df.fillna("")
    
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        worksheet = writer.sheets[sheet_name]
        
        # Ajustar ancho de columnas
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # Permitir texto envuelto
        for row in worksheet.iter_rows():
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical='top')
    
    output.seek(0)
    
    return st.download_button(
        label="📥 Descargar Excel",
        data=output,
        file_name=f"{nombre_archivo}_{date.today()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )


def maintenance_page():
    st.title("🔧 Mantenimientos")
    
    db = SessionLocal()
    
    # Inicializar estados de sesión
    if "maintenance_form_submitted" not in st.session_state:
        st.session_state.maintenance_form_submitted = False
    if "show_edit_form" not in st.session_state:
        st.session_state.show_edit_form = False
    if "edit_maintenance_id" not in st.session_state:
        st.session_state.edit_maintenance_id = None
    
    # Orden: Listar, Consultar, Registrar, Editar/Eliminar
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Listar", "🔍 Consultar", "📝 Registrar", "✏️ Editar/Eliminar"])
    
    # ==================================================
    # TAB 1: LISTAR
    # ==================================================
    with tab1:
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
            
            # Exportar
            if st.button("📊 Exportar lista completa a Excel", use_container_width=True):
                data_full = []
                for m in maintenances:
                    data_full.append({
                        "ID": m.id,
                        "FECHA": m.fecha_ingreso.strftime("%Y-%m-%d") if m.fecha_ingreso else "",
                        "VEHÍCULO": m.vehicle.placa if m.vehicle else "",
                        "TRAILER": m.trailer.placa if m.trailer else "",
                        "CONDUCTOR": m.driver.nombre if m.driver else "",
                        "TIPO": m.tipo_mantenimiento if m.tipo_mantenimiento else "",
                        "TALLER": m.taller if m.taller else "",
                        "DESCRIPCIÓN": m.descripcion if m.descripcion else "",
                        "OBSERVACIONES": m.observaciones if m.observaciones else "",
                        "ESTADO": m.estado if m.estado else ""
                    })
                exportar_a_excel(data_full, "mantenimientos_completo", "Lista General")
        else:
            st.info("ℹ️ No hay mantenimientos registrados")
    
    # ==================================================
    # TAB 2: CONSULTAR
    # ==================================================
    with tab2:
        st.subheader("🔍 Consulta de Mantenimientos")
        
        st.markdown("---")
        st.markdown("### 🎯 Filtros de búsqueda (todos son opcionales)")
        
        # Filtros
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            vehicles_all = db.query(Vehicle).order_by(Vehicle.placa).all()
            vehicle_list = ["(Todos)"] + [f"{v.placa} - {v.marca} {v.linea}" for v in vehicles_all]
            vehicle_map = {f"{v.placa} - {v.marca} {v.linea}": v.id for v in vehicles_all}
            selected_vehicle_display = st.selectbox("🚛 Vehículo", options=vehicle_list, index=0)
            selected_vehicle_id = vehicle_map.get(selected_vehicle_display) if selected_vehicle_display != "(Todos)" else None
            
            trailers_all = db.query(Trailer).order_by(Trailer.placa).all()
            trailer_list = ["(Todos)"] + [f"{t.placa} - {t.marca}" for t in trailers_all]
            trailer_map = {f"{t.placa} - {t.marca}": t.id for t in trailers_all}
            selected_trailer_display = st.selectbox("🔗 Trailer", options=trailer_list, index=0)
            selected_trailer_id = trailer_map.get(selected_trailer_display) if selected_trailer_display != "(Todos)" else None
        
        with col_f2:
            tipo_list = ["(Todos)", "Preventivo", "Correctivo", "Predictivo", "SOAT", "Tecnomecánica", "Urgente"]
            selected_tipo = st.selectbox("🔧 Tipo de mantenimiento", options=tipo_list, index=0)
            
            estado_list = ["(Todos)", "Pendiente", "En curso", "Completado", "Cancelado"]
            selected_estado = st.selectbox("📊 Estado", options=estado_list, index=0)
        
        col_f3, col_f4 = st.columns(2)
        with col_f3:
            taller_search = st.text_input("🔍 Buscar taller", placeholder="Texto...")
        with col_f4:
            descripcion_search = st.text_input("📝 Buscar en descripción", placeholder="Texto...")
        
        col_f5, col_f6 = st.columns(2)
        with col_f5:
            fecha_desde = st.date_input("📅 Fecha desde", value=None)
        with col_f6:
            fecha_hasta = st.date_input("📅 Fecha hasta", value=None)
        
        st.markdown("---")
        
        # Construir consulta
        query = db.query(Maintenance)
        
        if selected_vehicle_id:
            query = query.filter(Maintenance.vehiculo_id == selected_vehicle_id)
        if selected_trailer_id:
            query = query.filter(Maintenance.trailer_id == selected_trailer_id)
        if selected_tipo != "(Todos)":
            query = query.filter(Maintenance.tipo_mantenimiento == selected_tipo)
        if selected_estado != "(Todos)":
            query = query.filter(Maintenance.estado == selected_estado)
        if taller_search:
            query = query.filter(Maintenance.taller.ilike(f"%{taller_search}%"))
        if descripcion_search:
            query = query.filter(Maintenance.descripcion.ilike(f"%{descripcion_search}%"))
        if fecha_desde:
            query = query.filter(Maintenance.fecha_ingreso >= fecha_desde)
        if fecha_hasta:
            query = query.filter(Maintenance.fecha_ingreso <= fecha_hasta)
        
        maintenances_filtered = query.order_by(Maintenance.fecha_ingreso.desc()).all()
        
        if maintenances_filtered:
            st.success(f"📊 **{len(maintenances_filtered)}** mantenimiento(s) encontrado(s)")
            
            # Mostrar resultados con botón de edición
            for m in maintenances_filtered:
                with st.container():
                    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 2, 1])
                    with col1:
                        st.write(f"**{m.fecha_ingreso}**")
                    with col2:
                        st.write(f"{m.vehicle.placa if m.vehicle else '-'}")
                    with col3:
                        st.write(f"{m.tipo_mantenimiento}")
                    with col4:
                        st.write(f"{m.taller if m.taller else '-'}")
                    with col5:
                        st.write(f"{m.estado}")
                    with col6:
                        if st.button(f"✏️ Editar", key=f"edit_{m.id}"):
                            st.session_state.show_edit_form = True
                            st.session_state.edit_maintenance_id = m.id
                            st.rerun()
                    st.divider()
            
            # Formulario de edición rápida
            if st.session_state.show_edit_form and st.session_state.edit_maintenance_id:
                m = db.query(Maintenance).filter(Maintenance.id == st.session_state.edit_maintenance_id).first()
                if m:
                    st.markdown("---")
                    st.subheader(f"✏️ Editando mantenimiento #{m.id} - {m.vehicle.placa}")
                    
                    with st.form("quick_edit_form"):
                        col_edit1, col_edit2 = st.columns(2)
                        
                        with col_edit1:
                            edit_fecha = st.date_input("Fecha", value=m.fecha_ingreso)
                            edit_tipo = st.selectbox("Tipo", ["Preventivo", "Correctivo", "Predictivo", "SOAT", "Tecnomecánica", "Urgente"],
                                                     index=["Preventivo", "Correctivo", "Predictivo", "SOAT", "Tecnomecánica", "Urgente"].index(m.tipo_mantenimiento))
                            edit_estado = st.selectbox("Estado", ["Pendiente", "En curso", "Completado", "Cancelado"],
                                                       index=["Pendiente", "En curso", "Completado", "Cancelado"].index(m.estado))
                        
                        with col_edit2:
                            edit_taller = st.text_input("Taller", value=m.taller if m.taller else "")
                            edit_descripcion = st.text_area("Descripción", value=m.descripcion if m.descripcion else "", height=100)
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.form_submit_button("💾 Guardar Cambios"):
                                m.fecha_ingreso = edit_fecha
                                m.tipo_mantenimiento = edit_tipo
                                m.estado = edit_estado
                                m.taller = edit_taller
                                m.descripcion = edit_descripcion
                                db.commit()
                                st.success("✅ Mantenimiento actualizado")
                                st.session_state.show_edit_form = False
                                st.rerun()
                        with col_btn2:
                            if st.form_submit_button("❌ Cancelar"):
                                st.session_state.show_edit_form = False
                                st.rerun()
            
            # Botones de exportación
            st.markdown("---")
            st.subheader("📊 Exportar resultados")
            
            col_exp1, col_exp2, col_exp3 = st.columns(3)
            
            with col_exp1:
                if st.button("📊 Exportar resultados a Excel", use_container_width=True):
                    data_full = []
                    for m in maintenances_filtered:
                        data_full.append({
                            "ID": m.id,
                            "FECHA": m.fecha_ingreso.strftime("%Y-%m-%d") if m.fecha_ingreso else "",
                            "VEHÍCULO": m.vehicle.placa if m.vehicle else "",
                            "TRAILER": m.trailer.placa if m.trailer else "",
                            "CONDUCTOR": m.driver.nombre if m.driver else "",
                            "TIPO": m.tipo_mantenimiento if m.tipo_mantenimiento else "",
                            "TALLER": m.taller if m.taller else "",
                            "DESCRIPCIÓN": m.descripcion if m.descripcion else "",
                            "OBSERVACIONES": m.observaciones if m.observaciones else "",
                            "ESTADO": m.estado if m.estado else ""
                        })
                    exportar_a_excel(data_full, "resultados", "Resultados")
            
            with col_exp2:
                if selected_vehicle_id and selected_vehicle_display != "(Todos)":
                    vehicle_plate = selected_vehicle_display.split(" - ")[0]
                    if st.button(f"📊 Exportar historial de {vehicle_plate} a Excel", use_container_width=True):
                        data_full = []
                        for m in maintenances_filtered:
                            data_full.append({
                                "ID": m.id,
                                "FECHA": m.fecha_ingreso.strftime("%Y-%m-%d") if m.fecha_ingreso else "",
                                "TRAILER": m.trailer.placa if m.trailer else "",
                                "CONDUCTOR": m.driver.nombre if m.driver else "",
                                "TIPO": m.tipo_mantenimiento if m.tipo_mantenimiento else "",
                                "TALLER": m.taller if m.taller else "",
                                "DESCRIPCIÓN": m.descripcion if m.descripcion else "",
                                "OBSERVACIONES": m.observaciones if m.observaciones else "",
                                "ESTADO": m.estado if m.estado else ""
                            })
                        exportar_a_excel(data_full, f"historial_{vehicle_plate}", f"Historial {vehicle_plate}")
                else:
                    st.info("ℹ️ Selecciona un vehículo específico")
            
            with col_exp3:
                if st.button("📊 Exportar resumen estadístico a Excel", use_container_width=True):
                    resumen_tipo = {}
                    resumen_estado = {}
                    for m in maintenances_filtered:
                        tipo = m.tipo_mantenimiento if m.tipo_mantenimiento else "Sin especificar"
                        estado = m.estado if m.estado else "Sin especificar"
                        resumen_tipo[tipo] = resumen_tipo.get(tipo, 0) + 1
                        resumen_estado[estado] = resumen_estado.get(estado, 0) + 1
                    
                    df_tipo = pd.DataFrame(resumen_tipo.items(), columns=["TIPO", "CANTIDAD"])
                    df_estado = pd.DataFrame(resumen_estado.items(), columns=["ESTADO", "CANTIDAD"])
                    
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df_tipo.to_excel(writer, sheet_name="Resumen por Tipo", index=False)
                        df_estado.to_excel(writer, sheet_name="Resumen por Estado", index=False)
                        
                        for sheet_name in writer.sheets:
                            worksheet = writer.sheets[sheet_name]
                            for column in worksheet.columns:
                                max_length = 0
                                column_letter = column[0].column_letter
                                for cell in column:
                                    try:
                                        if len(str(cell.value)) > max_length:
                                            max_length = len(str(cell.value))
                                    except:
                                        pass
                                adjusted_width = min(max_length + 2, 30)
                                worksheet.column_dimensions[column_letter].width = adjusted_width
                    
                    output.seek(0)
                    st.download_button(
                        label="📥 Descargar Excel",
                        data=output,
                        file_name=f"resumen_mantenimientos_{date.today()}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
        else:
            st.warning("⚠️ No hay mantenimientos que coincidan con los filtros seleccionados")
    
    # ==================================================
    # TAB 3: REGISTRAR (con limpieza automática)
    # ==================================================
    with tab3:
        st.subheader("Registrar Mantenimiento")
        
        vehicles = db.query(Vehicle).filter(Vehicle.estado == "Activo").order_by(Vehicle.placa).all()
        
        if not vehicles:
            st.warning("⚠️ No hay vehículos registrados.")
            db.close()
            return
        
        vehicle_options = {v.id: f"{v.placa} - {v.marca} {v.linea}" for v in vehicles}
        
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
        
        vehicle_selected = db.query(Vehicle).filter(Vehicle.id == selected_vehicle_id).first()
        
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
                
                trailer_id = st.selectbox("🔗 Trailer", options=list(trailer_options.keys()),
                                           format_func=lambda x: trailer_options.get(x, ""),
                                           index=default_trailer_index)
            
            with col2:
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
                
                conductor_id = st.selectbox("👨‍✈️ Conductor", options=list(driver_options.keys()),
                                             format_func=lambda x: driver_options.get(x, ""),
                                             index=default_driver_index)
            
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
                tipo_mantenimiento = st.selectbox("🔧 Tipo de mantenimiento",
                                                   ["Preventivo", "Correctivo", "Predictivo", "SOAT", "Tecnomecánica", "Urgente"])
                taller = st.text_input("🏪 Taller / Mecánico")
            with col4:
                estado = st.selectbox("📊 Estado", ["Pendiente", "En curso", "Completado", "Cancelado"])
                descripcion = st.text_area("📝 Descripción", height=100)
                observaciones = st.text_area("💬 Observaciones", height=100)
            
            submitted = st.form_submit_button("💾 Registrar Mantenimiento", use_container_width=True)
            
            if submitted:
                errores = []
                if not selected_vehicle_id:
                    errores.append("El vehículo es obligatorio")
                
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
                    
                    st.success(f"✅ ¡Mantenimiento registrado con éxito!\n\n"
                              f"**Vehículo:** {vehicle_selected.placa}\n"
                              f"**Fecha:** {fecha_ingreso}\n"
                              f"**Tipo:** {tipo_mantenimiento}")
                    
                    st.session_state.maintenance_form_submitted = True
                    st.rerun()
    
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
                            
                            edit_trailer_id = st.selectbox("Trailer", options=list(trailer_options_edit.keys()),
                                                           format_func=lambda x: trailer_options_edit.get(x, ""),
                                                           index=list(trailer_options_edit.keys()).index(maintenance.trailer_id) if maintenance.trailer_id in trailer_options_edit else 0)
                            
                            edit_fecha = st.date_input("Fecha", value=maintenance.fecha_ingreso)
                            
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
                                        st.success(f"✅ SOAT vigente")
                        
                        with col2:
                            drivers = db.query(Driver).filter(Driver.estado == "Activo").all()
                            driver_options_edit = {None: "Sin conductor"}
                            for d in drivers:
                                driver_options_edit[d.id] = f"{d.nombre} - {d.identificacion}"
                            
                            edit_conductor_id = st.selectbox("Conductor", options=list(driver_options_edit.keys()),
                                                              format_func=lambda x: driver_options_edit.get(x, ""),
                                                              index=list(driver_options_edit.keys()).index(maintenance.conductor_id) if maintenance.conductor_id in driver_options_edit else 0)
                            
                            edit_taller = st.text_input("Taller", value=maintenance.taller if maintenance.taller else "")
                            edit_estado = st.selectbox("Estado", ["Pendiente", "En curso", "Completado", "Cancelado"],
                                                       index=["Pendiente", "En curso", "Completado", "Cancelado"].index(maintenance.estado))
                            edit_tipo = st.selectbox("Tipo", ["Preventivo", "Correctivo", "Predictivo", "SOAT", "Tecnomecánica", "Urgente"],
                                                     index=["Preventivo", "Correctivo", "Predictivo", "SOAT", "Tecnomecánica", "Urgente"].index(maintenance.tipo_mantenimiento))
                        
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
