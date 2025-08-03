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

def update_event_table():
    """Event tablosuna ticket_url kolonu ekle"""
    conn = get_db_connection()
    if not conn:
        print("Veritabanı bağlantısı kurulamadı!")
        return

    cursor = conn.cursor()

    try:
        print("Event tablosuna ticket_url kolonu ekleniyor...")
        cursor.execute("""
            ALTER TABLE "event"
            ADD COLUMN IF NOT EXISTS "ticket_url" VARCHAR(500) DEFAULT 'https://instagram.com'
        """)
        conn.commit()
        print("✅ Event tablosu başarıyla güncellendi!")
        print("📋 Eklenen kolon:")
        print("   - ticket_url (VARCHAR(500)) - Varsayılan: https://instagram.com")

    except Exception as e:
        print(f"❌ Hata: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    update_event_table() 