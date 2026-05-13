import streamlit as st

from database.db import engine
from database.models import Base

from modules.vehicles import vehicles_page
from modules.trailers import trailers_page
from modules.drivers import drivers_page
from modules.maintenance import maintenance_page


# =========================
# CREAR BASE DE DATOS
# =========================

Base.metadata.create_all(bind=engine)


# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="Fleet Maintenance",
    layout="wide"
)


# =========================
# SIDEBAR
# =========================

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


# =========================
# PAGINAS
# =========================

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
