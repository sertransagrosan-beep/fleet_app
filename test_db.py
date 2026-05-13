# test_db_streamlit.py

import streamlit as st
from sqlalchemy import text
from database.db import get_engine, init_db

st.title("🔧 Prueba de conexión a Neon PostgreSQL")

try:
    engine = get_engine()
    with engine.connect() as conn:
        # Usar text() para SQL en SQLAlchemy 2.x
        result = conn.execute(text("SELECT 1"))
        data = result.fetchone()
        st.success("✅ Conexión exitosa a Neon PostgreSQL!")
        st.write(f"Resultado de prueba: {data[0]}")
    
    init_db()
    st.success("✅ Tablas creadas/verificadas correctamente")
    
except Exception as e:
    st.error(f"❌ Error: {e}")