import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Veritabanı bağlantı bilgileri
DB_CONFIG = {
    'host': 'ep-solitary-silence-a2tdicc0-pooler.eu-central-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_J3cztba8mNfo',
    'sslmode': 'require'
}

def create_mentor_tables():
    """Mentor ve MentorRequest tablolarını oluşturur"""
    
    # Mentor tablosu için SQL
    mentor_table_sql = """
    CREATE TABLE IF NOT EXISTS mentor (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        expertise VARCHAR(500) NOT NULL,
        company VARCHAR(200) NOT NULL,
        bio TEXT NOT NULL,
        email VARCHAR(100),
        phone VARCHAR(20),
        linkedin VARCHAR(200),
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # MentorRequest tablosu için SQL
    mentor_request_table_sql = """
    CREATE TABLE IF NOT EXISTS mentor_request (
        id SERIAL PRIMARY KEY,
        user_name VARCHAR(100) NOT NULL,
        user_email VARCHAR(100) NOT NULL,
        mentor_id INTEGER NOT NULL REFERENCES mentor(id),
        mentor_name VARCHAR(100) NOT NULL,
        subject VARCHAR(200) NOT NULL,
        message TEXT NOT NULL,
        status VARCHAR(20) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        responded_at TIMESTAMP,
        response_message TEXT,
        notes TEXT
    );
    """
    
    try:
        # Veritabanına bağlan
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("🔗 Veritabanına bağlandı")
        
        # Mentor tablosunu oluştur
        cursor.execute(mentor_table_sql)
        print("✅ Mentor tablosu oluşturuldu")
        
        # MentorRequest tablosunu oluştur
        cursor.execute(mentor_request_table_sql)
        print("✅ MentorRequest tablosu oluşturuldu")
        
        # Örnek mentor verileri ekle
        sample_mentors = [
            {
                'name': 'Dr. Ahmet Yılmaz',
                'expertise': 'Teknoloji,Startup,Yatırım',
                'company': 'TechVentures Inc.',
                'bio': '15 yıllık girişimcilik deneyimi ile 50+ startup\'a mentorluk yapmıştır. Özellikle teknoloji alanında uzmanlaşmıştır.',
                'email': 'ahmet.yilmaz@techventures.com',
                'phone': '+90 555 123 4567',
                'linkedin': 'linkedin.com/in/ahmetyilmaz'
            },
            {
                'name': 'Ayşe Demir',
                'expertise': 'E-ticaret,Pazarlama,İş Geliştirme',
                'company': 'DigitalGrowth Solutions',
                'bio': 'E-ticaret ve dijital pazarlama alanında 10 yıllık deneyime sahip. Birçok başarılı online işletmenin kuruluşunda rol almıştır.',
                'email': 'ayse.demir@digitalgrowth.com',
                'phone': '+90 555 234 5678',
                'linkedin': 'linkedin.com/in/aysedemir'
            },
            {
                'name': 'Mehmet Kaya',
                'expertise': 'Finans,Yatırım,Strateji',
                'company': 'Capital Partners',
                'bio': 'Finans ve yatırım alanında uzman. Venture capital firmasında yönetici olarak çalışmaktadır.',
                'email': 'mehmet.kaya@capitalpartners.com',
                'phone': '+90 555 345 6789',
                'linkedin': 'linkedin.com/in/mehmetkaya'
            },
            {
                'name': 'Zeynep Arslan',
                'expertise': 'Sağlık Teknolojisi,İnovasyon,Araştırma',
                'company': 'HealthTech Innovations',
                'bio': 'Sağlık teknolojileri alanında araştırmacı ve girişimci. Birçok sağlık startup\'ının geliştirilmesinde rol almıştır.',
                'email': 'zeynep.arslan@healthtech.com',
                'phone': '+90 555 456 7890',
                'linkedin': 'linkedin.com/in/zeyneparslan'
            },
            {
                'name': 'Can Özkan',
                'expertise': 'Yapay Zeka,Makine Öğrenmesi,Veri Bilimi',
                'company': 'AI Solutions Lab',
                'bio': 'Yapay zeka ve makine öğrenmesi alanında uzman. Birçok AI startup\'ının kurucusu ve danışmanıdır.',
                'email': 'can.ozkan@aisolutions.com',
                'phone': '+90 555 567 8901',
                'linkedin': 'linkedin.com/in/canozkan'
            }
        ]
        
        # Mevcut mentor sayısını kontrol et
        cursor.execute("SELECT COUNT(*) FROM mentor")
        mentor_count = cursor.fetchone()[0]
        
        if mentor_count == 0:
            # Örnek mentorları ekle
            for mentor in sample_mentors:
                cursor.execute("""
                    INSERT INTO mentor (name, expertise, company, bio, email, phone, linkedin)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    mentor['name'],
                    mentor['expertise'],
                    mentor['company'],
                    mentor['bio'],
                    mentor['email'],
                    mentor['phone'],
                    mentor['linkedin']
                ))
            print(f"✅ {len(sample_mentors)} örnek mentor eklendi")
        else:
            print(f"ℹ️  Zaten {mentor_count} mentor mevcut, örnek veriler eklenmedi")
        
        # Değişiklikleri kaydet
        conn.commit()
        print("💾 Değişiklikler kaydedildi")
        
        # Bağlantıyı kapat
        cursor.close()
        conn.close()
        print("🔌 Veritabanı bağlantısı kapatıldı")
        
        print("\n🎉 Mentor sistemi başarıyla kuruldu!")
        print("📊 Oluşturulan tablolar:")
        print("   - mentor")
        print("   - mentor_request")
        
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    print("🚀 Mentor tabloları oluşturuluyor...")
    create_mentor_tables() 