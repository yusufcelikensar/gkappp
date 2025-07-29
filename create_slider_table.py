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

def create_slider_table():
    """Slider images tablosunu oluştur"""
    try:
        conn = get_db_connection()
        if conn is None:
            print("Veritabanı bağlantısı kurulamadı")
            return
        
        cursor = conn.cursor()
        
        # Slider images tablosunu oluştur
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS slider_images (
                id SERIAL PRIMARY KEY,
                image_url TEXT NOT NULL,
                title VARCHAR(255),
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Örnek veriler ekle
        cursor.execute("""
            INSERT INTO slider_images (image_url, title, description) 
            VALUES 
            ('https://via.placeholder.com/400x200/FF6B6B/FFFFFF?text=Startup+Yarışması', 'Startup Yarışması', '50.000 TL ödül havuzu'),
            ('https://via.placeholder.com/400x200/4ECDC4/FFFFFF?text=Mentor+Buluşması', 'Mentor Buluşması', 'Uzmanlarla tanışın'),
            ('https://via.placeholder.com/400x200/45B7D1/FFFFFF?text=Proje+Sergisi', 'Proje Sergisi', 'Projelerinizi sergileyin')
            ON CONFLICT DO NOTHING
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Slider images tablosu başarıyla oluşturuldu!")
        print("✅ Örnek veriler eklendi!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    create_slider_table() 