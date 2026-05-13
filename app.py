import streamlit as st

from database.db import engine, Base
import database.models

from modules.vehicles import vehicles_page
from modules.trailers import trailers_page
from modules.drivers import drivers_page
from modules.maintenance import maintenance_page
from modules.import_data import import_page

Base.metadata.create_all(bind=engine)

st.set_page_config(
    page_title="Fleet App",
    layout="wide"
)

st.sidebar.title("🚛 Fleet App")

menu = st.sidebar.radio(
    "Menú",
    [
        "Importar Excel",
        "Vehículos",
        "Trailers",
        "Conductores",
        "Mantenimientos"
    ]
)

if menu == "Importar Excel":
    import_page()

elif menu == "Vehículos":
    vehicles_page()

elif menu == "Trailers":
    trailers_page()

elif menu == "Conductores":
    drivers_page()

elif menu == "Mantenimientos":
    maintenance_page()
