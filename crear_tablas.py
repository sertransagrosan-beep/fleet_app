# crear_tablas_seguro.py

from database.db import engine, Base
import database.models  # Importar todos los modelos

print("=== CREANDO TABLAS EN NEON ===\n")

# Verificar qué tablas va a crear
print(f"Clases registradas en Base: {Base.metadata.tables.keys()}")

# Crear las tablas
Base.metadata.create_all(bind=engine)
print("✅ Comando create_all() ejecutado")

# Verificar que se crearon
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """))
    tablas = [row[0] for row in result]
    print(f"\n📋 Tablas creadas en neondb: {tablas}")

print("\n=== FIN ===")