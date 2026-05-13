# reset_db.py

from sqlalchemy import text
from database.db import get_engine

def reset_database():
    engine = get_engine()
    
    with engine.connect() as conn:
        with conn.begin() as trans:
            try:
                # Verificar qué tablas existen
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                tablas = [row[0] for row in result]
                print(f"Tablas encontradas: {tablas}")
                
                # Vaciar tablas en orden (solo las que existen)
                if 'maintenances' in tablas:
                    conn.execute(text("TRUNCATE TABLE maintenances RESTART IDENTITY CASCADE;"))
                    print("✅ maintenances vaciada")
                
                if 'vehicles' in tablas:
                    conn.execute(text("TRUNCATE TABLE vehicles RESTART IDENTITY CASCADE;"))
                    print("✅ vehicles vaciada")
                
                if 'trailers' in tablas:
                    conn.execute(text("TRUNCATE TABLE trailers RESTART IDENTITY CASCADE;"))
                    print("✅ trailers vaciada")
                
                if 'drivers' in tablas:
                    conn.execute(text("TRUNCATE TABLE drivers RESTART IDENTITY CASCADE;"))
                    print("✅ drivers vaciada")
                
                trans.commit()
                print("\n✅ Todas las tablas han sido vaciadas exitosamente!")
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    reset_database()