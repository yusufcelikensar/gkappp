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

def create_notifications_table():
    """Notifications tablosunu oluştur"""
    try:
        conn = get_db_connection()
        if conn is None:
            print("Veritabanı bağlantısı kurulamadı")
            return
        
        cursor = conn.cursor()
        
        # Notifications tablosunu oluştur
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                type VARCHAR(50) DEFAULT 'info',
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Örnek bildirimler ekle
        cursor.execute("""
            INSERT INTO notifications (title, message, type) 
            VALUES 
            ('Hoş Geldiniz!', 'Girişimcilik Kulübü uygulamasına hoş geldiniz!', 'info'),
            ('Yeni Etkinlik', 'Startup yarışması başvuruları açıldı!', 'success'),
            ('Önemli Duyuru', 'Mentor buluşması bu hafta gerçekleşecek.', 'warning')
            ON CONFLICT DO NOTHING
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Notifications tablosu başarıyla oluşturuldu!")
        print("✅ Örnek bildirimler eklendi!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    create_notifications_table() 