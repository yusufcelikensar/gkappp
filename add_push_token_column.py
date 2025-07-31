import psycopg2
import os

def add_push_token_column():
    """User tablosuna push_token sütunu ekle"""
    try:
        # PostgreSQL bağlantısı
        conn = psycopg2.connect(
            host="ep-solitary-silence-a2tdicc0-pooler.eu-central-1.aws.neon.tech",
            database="neondb",
            user="neondb_owner",
            password="npg_J3cztba8mNfo",
            sslmode="require"
        )
        
        cursor = conn.cursor()
        
        # push_token sütununu ekle
        cursor.execute("""
            ALTER TABLE "user" 
            ADD COLUMN IF NOT EXISTS push_token VARCHAR(255)
        """)
        
        conn.commit()
        print("✅ push_token sütunu başarıyla eklendi!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    add_push_token_column() 