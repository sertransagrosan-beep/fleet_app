# diagnosticar.py

from sqlalchemy import text
from database.db import get_engine

engine = get_engine()

print("=== DIAGNÓSTICO DE CONEXIÓN A NEON ===\n")

with engine.connect() as conn:
    # 1. Qué base de datos estamos usando
    result = conn.execute(text("SELECT current_database();"))
    db = result.fetchone()[0]
    print(f"1. Base de datos actual: {db}")
    
    # 2. Listar todas las tablas
    result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """))
    tablas = [row[0] for row in result]
    print(f"2. Tablas encontradas: {tablas}")
    
    # 3. Contar registros si las tablas existen
    for tabla in ['vehicles', 'trailers', 'drivers', 'maintenances']:
        if tabla in tablas:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {tabla};"))
            count = result.fetchone()[0]
            print(f"   - {tabla}: {count} registros")
        else:
            print(f"   - {tabla}: ❌ NO EXISTE")
    
    # 4. Verificar URL (sin contraseña)
    url = str(engine.url)
    # Ocultar contraseña
    import re
    url_clean = re.sub(r'://[^:]+:([^@]+)@', '://usuario:***@', url)
    print(f"\n3. URL de conexión: {url_clean}")

print("\n=== FIN DEL DIAGNÓSTICO ===")