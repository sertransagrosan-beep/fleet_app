# app.py

import streamlit as st

from database.db import init_db, engine
import database.models

from modules.vehicles import vehicles_page
from modules.trailers import trailers_page
from modules.drivers import drivers_page
from modules.maintenance import maintenance_page
from modules.import_data import import_page

# Configurar la página (debe ir primero)
st.set_page_config(
    page_title="Fleet App",
    page_icon="🚛",
    layout="wide"
)

# Inicializar la base de datos
try:
    init_db()
    st.sidebar.success("✅ Conectado a Neon PostgreSQL")
except Exception as e:
    st.sidebar.error(f"❌ Error de conexión: {e}")

# Menú lateral - NUEVO ORDEN
st.sidebar.title("🚛 Fleet App")

menu = st.sidebar.radio(
    "Menú",
    [
        "Mantenimientos",
        "Vehículos",
        "Trailers",
        "Conductores",
        "Importar Excel"
    ]
)

# Navegación
if menu == "Mantenimientos":
    maintenance_page()
elif menu == "Vehículos":
    vehicles_page()
elif menu == "Trailers":
    trailers_page()
elif menu == "Conductores":
    drivers_page()
elif menu == "Importar Excel":
    import_page()
