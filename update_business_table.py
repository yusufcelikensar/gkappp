import psycopg2
from datetime import datetime

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

def update_business_table():
    """İşletmeler tablosunu güncelle"""
    conn = get_db_connection()
    if conn is None:
        print("Veritabanı bağlantısı kurulamadı!")
        return
    
    cursor = conn.cursor()
    
    try:
        # Mevcut tabloyu sil ve yeniden oluştur
        cursor.execute("DROP TABLE IF EXISTS business CASCADE")
        
        # Yeni tabloyu oluştur
        cursor.execute("""
            CREATE TABLE business (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                discount INTEGER NOT NULL,
                category VARCHAR(100) NOT NULL,
                address TEXT NOT NULL,
                latitude FLOAT NOT NULL,
                longitude FLOAT NOT NULL,
                description TEXT,
                logo_url VARCHAR(500),
                phone VARCHAR(20),
                website VARCHAR(200),
                google_maps_url VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Örnek veriler ekle
        sample_businesses = [
            {
                'name': 'Starbucks',
                'discount': 20,
                'category': 'Kahve & İçecek',
                'address': 'Kadıköy, İstanbul',
                'latitude': 40.9909,
                'longitude': 29.0303,
                'description': 'Öğrenci kartı ile %20 indirim',
                'logo_url': 'https://via.placeholder.com/100x100/007AFF/FFFFFF?text=S',
                'phone': '+90 212 555 0123',
                'website': 'https://www.starbucks.com.tr',
                'google_maps_url': 'https://maps.google.com/?q=40.9909,29.0303'
            },
            {
                'name': 'McDonald\'s',
                'discount': 15,
                'category': 'Fast Food',
                'address': 'Beşiktaş, İstanbul',
                'latitude': 41.0422,
                'longitude': 29.0083,
                'description': 'Öğrenci menüsü %15 indirimli',
                'logo_url': 'https://via.placeholder.com/100x100/FFC107/FFFFFF?text=M',
                'phone': '+90 212 555 0124',
                'website': 'https://www.mcdonalds.com.tr',
                'google_maps_url': 'https://maps.google.com/?q=41.0422,29.0083'
            },
            {
                'name': 'Domino\'s Pizza',
                'discount': 25,
                'category': 'Pizza',
                'address': 'Şişli, İstanbul',
                'latitude': 41.0602,
                'longitude': 28.9877,
                'description': 'Öğrenci kartı ile %25 indirim',
                'logo_url': 'https://via.placeholder.com/100x100/E74C3C/FFFFFF?text=D',
                'phone': '+90 212 555 0125',
                'website': 'https://www.dominos.com.tr',
                'google_maps_url': 'https://maps.google.com/?q=41.0602,28.9877'
            }
        ]
        
        for business in sample_businesses:
            cursor.execute("""
                INSERT INTO business (name, discount, category, address, latitude, longitude, 
                                    description, logo_url, phone, website, google_maps_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                business['name'],
                business['discount'],
                business['category'],
                business['address'],
                business['latitude'],
                business['longitude'],
                business['description'],
                business['logo_url'],
                business['phone'],
                business['website'],
                business['google_maps_url']
            ))
        
        conn.commit()
        print("✅ İşletmeler tablosu başarıyla güncellendi!")
        print("✅ Örnek işletmeler eklendi!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Hata: {e}")
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    update_business_table() 