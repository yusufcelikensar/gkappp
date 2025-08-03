import psycopg2
import os

def get_db_connection():
    """PostgreSQL veritabanı bağlantısı"""
    try:
        conn = psycopg2.connect(
            host="ep-solitary-silence-a2tdicc0-pooler.eu-central-1.aws.neon.tech",
            database="neondb",
            user="neondb_owner",
            password="npg_J3cztba8mNfo",
            sslmode="require"
        )
        return conn
    except Exception as e:
        print(f"Veritabanı bağlantı hatası: {e}")
        return None

def update_user_table():
    """User tablosuna öğrenci bilgilerini ekle"""
    conn = get_db_connection()
    if not conn:
        print("Veritabanı bağlantısı kurulamadı!")
        return
    
    cursor = conn.cursor()
    
    try:
        # Öğrenci bilgilerini ekle
        print("User tablosuna öğrenci bilgileri ekleniyor...")
        
        # studentId kolonu ekle
        cursor.execute("""
            ALTER TABLE "user" 
            ADD COLUMN IF NOT EXISTS "studentId" VARCHAR(20)
        """)
        
        # department kolonu ekle
        cursor.execute("""
            ALTER TABLE "user" 
            ADD COLUMN IF NOT EXISTS "department" VARCHAR(100)
        """)
        
        # year kolonu ekle
        cursor.execute("""
            ALTER TABLE "user" 
            ADD COLUMN IF NOT EXISTS "year" INTEGER
        """)
        
        conn.commit()
        print("✅ User tablosu başarıyla güncellendi!")
        print("📋 Eklenen kolonlar:")
        print("   - studentId (VARCHAR(20))")
        print("   - department (VARCHAR(100))")
        print("   - year (INTEGER)")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    update_user_table() 