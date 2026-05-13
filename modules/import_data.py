# modules/import_data.py

import streamlit as st
import pandas as pd
from datetime import datetime

from database.db import SessionLocal
from database.models import Vehicle, Trailer, Driver


def limpiar_fecha(valor):
    """Convierte fechas de Excel a objetos date"""
    if pd.isna(valor) or valor == "" or valor is None:
        return None
    try:
        if isinstance(valor, datetime):
            return valor.date()
        if isinstance(valor, str):
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"]:
                try:
                    return datetime.strptime(valor.split()[0], fmt).date()
                except:
                    continue
        return valor
    except:
        return None


def limpiar_texto(valor):
    """Limpia texto eliminando NaN y espacios"""
    if pd.isna(valor):
        return ""
    return str(valor).strip()


def importar_vehiculos_desde_excel(df_raw):
    """Extrae vehículos del Excel incluyendo trailer y conductor habitual"""
    vehicles = []
    
    # Mapeo de filas
    ROW_PLACA = 0
    ROW_MARCA = 1
    ROW_LINEA = 2
    ROW_MODELO = 3
    ROW_COLOR = 4
    ROW_SOAT = 5
    ROW_TECNOMECANICA = 6
    
    # Buscar filas de trailer y conductor habitual
    trailer_habitual_row = None
    conductor_habitual_row = None
    
    for row_idx in range(df_raw.shape[0]):
        cell_value = limpiar_texto(df_raw.iloc[row_idx, 0])
        if "PLACA REMOLQUE" in cell_value.upper():
            trailer_habitual_row = row_idx
        elif "CONDUCTOR" in cell_value.upper():
            conductor_habitual_row = row_idx
    
    for col_idx in range(1, df_raw.shape[1]):
        placa = limpiar_texto(df_raw.iloc[ROW_PLACA, col_idx])
        
        if not placa:
            continue
        
        vehicle_data = {
            "placa": placa.upper(),
            "marca": limpiar_texto(df_raw.iloc[ROW_MARCA, col_idx]) if ROW_MARCA < df_raw.shape[0] else "",
            "linea": limpiar_texto(df_raw.iloc[ROW_LINEA, col_idx]) if ROW_LINEA < df_raw.shape[0] else "",
            "modelo": limpiar_texto(df_raw.iloc[ROW_MODELO, col_idx]) if ROW_MODELO < df_raw.shape[0] else "",
            "color": limpiar_texto(df_raw.iloc[ROW_COLOR, col_idx]) if ROW_COLOR < df_raw.shape[0] else "",
            "soat": limpiar_fecha(df_raw.iloc[ROW_SOAT, col_idx]) if ROW_SOAT < df_raw.shape[0] else None,
            "tecnomecanica": limpiar_fecha(df_raw.iloc[ROW_TECNOMECANICA, col_idx]) if ROW_TECNOMECANICA < df_raw.shape[0] else None,
            "kilometraje_actual": 0,
            "trailer_habitual_placa": "",
            "conductor_habitual_nombre": ""
        }
        
        # Obtener trailer habitual si existe
        if trailer_habitual_row and trailer_habitual_row < df_raw.shape[0]:
            vehicle_data["trailer_habitual_placa"] = limpiar_texto(df_raw.iloc[trailer_habitual_row, col_idx])
        
        # Obtener conductor habitual si existe
        if conductor_habitual_row and conductor_habitual_row < df_raw.shape[0]:
            vehicle_data["conductor_habitual_nombre"] = limpiar_texto(df_raw.iloc[conductor_habitual_row, col_idx])
        
        vehicles.append(vehicle_data)
    
    return pd.DataFrame(vehicles)


def importar_trailers_desde_excel(df_raw):
    """Extrae trailers del Excel"""
    trailers = []
    
    trailer_start_row = None
    for row_idx in range(df_raw.shape[0]):
        cell_value = limpiar_texto(df_raw.iloc[row_idx, 0])
        if "PLACA REMOLQUE" in cell_value.upper():
            trailer_start_row = row_idx
            break
    
    if trailer_start_row is None:
        st.warning("No se encontró la sección de trailers en el archivo")
        return pd.DataFrame()
    
    for col_idx in range(1, df_raw.shape[1]):
        placa = limpiar_texto(df_raw.iloc[trailer_start_row, col_idx])
        
        if not placa:
            continue
        
        trailer_data = {
            "placa": placa.upper(),
            "marca": limpiar_texto(df_raw.iloc[trailer_start_row + 1, col_idx]) if trailer_start_row + 1 < df_raw.shape[0] else "",
            "modelo": limpiar_texto(df_raw.iloc[trailer_start_row + 2, col_idx]) if trailer_start_row + 2 < df_raw.shape[0] else "",
            "carroceria": limpiar_texto(df_raw.iloc[trailer_start_row + 3, col_idx]) if trailer_start_row + 3 < df_raw.shape[0] else "PLATAFORMA ESTACAS DESMONTABLES",
            "numero_ejes": 3
        }
        
        if trailer_start_row + 4 < df_raw.shape[0]:
            ejes = limpiar_texto(df_raw.iloc[trailer_start_row + 4, col_idx])
            if ejes and ejes.isdigit():
                trailer_data["numero_ejes"] = int(ejes)
        
        trailers.append(trailer_data)
    
    return pd.DataFrame(trailers)


def importar_conductores_desde_excel(df_raw):
    """
    Extrae conductores del Excel incluyendo:
    - Nombre (fila CONDUCTOR)
    - Identificación (fila IDENTIFICACION)
    - Celular (fila CELULAR)
    - Licencia Conducción (fila LICENCIA CONDUCCION)
    """
    drivers = []
    
    # Buscar la fila donde comienza la sección de conductores
    driver_start_row = None
    for row_idx in range(df_raw.shape[0]):
        cell_value = limpiar_texto(df_raw.iloc[row_idx, 0])
        if cell_value.upper() == "CONDUCTOR":
            driver_start_row = row_idx
            break
    
    if driver_start_row is None:
        # Intentar búsqueda más amplia
        for row_idx in range(df_raw.shape[0]):
            cell_value = limpiar_texto(df_raw.iloc[row_idx, 0])
            if "CONDUCTOR" in cell_value.upper():
                driver_start_row = row_idx
                break
    
    if driver_start_row is None:
        st.warning("No se encontró la sección de conductores en el archivo")
        return pd.DataFrame()
    
    nombre_row = driver_start_row
    identificacion_row = driver_start_row + 1
    celular_row = driver_start_row + 2
    licencia_row = driver_start_row + 3
    
    for col_idx in range(1, df_raw.shape[1]):
        nombre = limpiar_texto(df_raw.iloc[nombre_row, col_idx]) if nombre_row < df_raw.shape[0] else ""
        
        if not nombre:
            continue
        
        identificacion = ""
        if identificacion_row < df_raw.shape[0]:
            identificacion = limpiar_texto(df_raw.iloc[identificacion_row, col_idx])
        
        # Leer celular
        celular = ""
        if celular_row < df_raw.shape[0]:
            celular = limpiar_texto(df_raw.iloc[celular_row, col_idx])
        
        # Leer fecha de vencimiento de licencia - manejar NaN correctamente
        vencimiento_licencia = None
        if licencia_row < df_raw.shape[0]:
            fecha_valor = df_raw.iloc[licencia_row, col_idx]
            # Verificar si es un valor válido (no NaN)
            if pd.notna(fecha_valor):
                vencimiento_licencia = limpiar_fecha(fecha_valor)
            # Si es NaN, dejar como None
        
        driver_data = {
            "nombre": nombre.upper(),
            "identificacion": identificacion,
            "telefono": celular,
            "vencimiento_licencia": vencimiento_licencia,
            "estado": "Activo"
        }
        
        drivers.append(driver_data)
    
    return pd.DataFrame(drivers)


def import_page():
    st.title("📥 Importar Excel")
    
    archivo = st.file_uploader(
        "Selecciona archivo Excel",
        type=["xlsx"]
    )
    
    if archivo is not None:
        df_raw = pd.read_excel(archivo, header=None)
        
        # Mostrar estructura del Excel para debug (opcional)
        with st.expander("Ver estructura del Excel"):
            st.write(f"Dimensiones: {df_raw.shape[0]} filas x {df_raw.shape[1]} columnas")
            st.dataframe(df_raw.iloc[:25, :10], width="stretch")
        
        tipo = st.selectbox(
            "Tipo de importación",
            ["Vehículos", "Trailers", "Conductores"]
        )
        
        if tipo == "Vehículos":
            df = importar_vehiculos_desde_excel(df_raw)
        elif tipo == "Trailers":
            df = importar_trailers_desde_excel(df_raw)
        else:
            df = importar_conductores_desde_excel(df_raw)
        
        if df.empty:
            st.warning("No se encontraron datos para importar")
            return
        
        st.subheader("Vista previa")
        st.dataframe(df.astype(str), width="stretch", hide_index=True)
        st.write(f"**Registros detectados:** {len(df)}")
        
        if st.button("🚀 Importar Datos", use_container_width=True):
            db = SessionLocal()
            registros = 0
            omitidos = 0
            errores = []
            
            try:
                if tipo == "Vehículos":
                    for _, row in df.iterrows():
                        try:
                            existe = db.query(Vehicle).filter(Vehicle.placa == row["placa"]).first()
                            if existe:
                                omitidos += 1
                                continue
                            
                            # Buscar trailer habitual por placa
                            trailer_habitual_id = None
                            if row.get("trailer_habitual_placa"):
                                trailer = db.query(Trailer).filter(Trailer.placa == row["trailer_habitual_placa"]).first()
                                if trailer:
                                    trailer_habitual_id = trailer.id
                            
                            # Buscar conductor habitual por nombre
                            conductor_habitual_id = None
                            if row.get("conductor_habitual_nombre"):
                                conductor = db.query(Driver).filter(Driver.nombre.like(f"%{row['conductor_habitual_nombre']}%")).first()
                                if conductor:
                                    conductor_habitual_id = conductor.id
                            
                            nuevo = Vehicle(
                                placa=row["placa"],
                                marca=row["marca"],
                                linea=row["linea"],
                                modelo=str(row["modelo"]),
                                color=row["color"],
                                soat=row["soat"] if pd.notna(row["soat"]) else None,
                                tecnomecanica=row["tecnomecanica"] if pd.notna(row["tecnomecanica"]) else None,
                                kilometraje_actual=0,
                                estado="Activo",
                                trailer_habitual_id=trailer_habitual_id,
                                conductor_habitual_id=conductor_habitual_id
                            )
                            db.add(nuevo)
                            registros += 1
                        except Exception as e:
                            errores.append(f"{row['placa']}: {str(e)}")
                
                elif tipo == "Trailers":
                    for _, row in df.iterrows():
                        try:
                            existe = db.query(Trailer).filter(Trailer.placa == row["placa"]).first()
                            if existe:
                                omitidos += 1
                                continue
                            
                            nuevo = Trailer(
                                placa=row["placa"],
                                marca=row["marca"],
                                modelo=str(row["modelo"]),
                                carroceria=row["carroceria"],
                                numero_ejes=row["numero_ejes"],
                                estado="Activo"
                            )
                            db.add(nuevo)
                            registros += 1
                        except Exception as e:
                            errores.append(f"{row['placa']}: {str(e)}")
                
                else:  # Conductores
                    for _, row in df.iterrows():
                        try:
                            if not row["identificacion"]:
                                omitidos += 1
                                continue
                            
                            existe = db.query(Driver).filter(Driver.identificacion == row["identificacion"]).first()
                            if existe:
                                omitidos += 1
                                continue
                            
                            # Manejar vencimiento_licencia - convertir NaN a None
                            vencimiento = row.get("vencimiento_licencia", None)
                            if pd.isna(vencimiento):
                                vencimiento = None
                            
                            nuevo = Driver(
                                nombre=row["nombre"],
                                identificacion=row["identificacion"],
                                telefono=row.get("telefono", ""),
                                vencimiento_licencia=vencimiento,
                                estado="Activo"
                            )
                            db.add(nuevo)
                            registros += 1
                        except Exception as e:
                            errores.append(f"{row['nombre']}: {str(e)}")
                
                db.commit()
                
                if registros > 0:
                    st.success(f"✅ {registros} registros importados correctamente")
                if omitidos > 0:
                    st.info(f"ℹ️ {omitidos} registros omitidos (ya existían)")
                if errores:
                    st.warning(f"⚠️ {len(errores)} errores:")
                    for err in errores[:5]:
                        st.write(f"- {err}")
                
            except Exception as e:
                db.rollback()
                st.error(f"❌ Error general: {e}")
            finally:
                db.close()