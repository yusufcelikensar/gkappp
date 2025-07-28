# 🛍️ Ürün Yönetimi API Dokümantasyonu

## 📋 Genel Bakış

Bu API, Girişimcilik Kulübü uygulamasının market sistemi için ürün yönetimi ve satın alım işlemlerini sağlar.

## 🗄️ Veritabanı Modelleri

### Product (Ürün)
```sql
- id: Integer (Primary Key)
- name: String(200) - Ürün adı
- description: Text - Ürün açıklaması
- image: String(500) - Ürün görseli URL'i
- points: Integer - Ürün puan değeri
- category: String(100) - Ürün kategorisi
- stock: Integer - Stok miktarı
- is_available: Boolean - Ürünün mevcut olup olmadığı
- created_at: DateTime - Oluşturulma tarihi
- updated_at: DateTime - Güncellenme tarihi
```

### Purchase (Satın Alım)
```sql
- id: Integer (Primary Key)
- user_name: String(100) - Kullanıcı adı
- product_id: Integer (Foreign Key) - Ürün ID'si
- points_spent: Integer - Harcanan puan
- created_at: DateTime - Satın alım tarihi
```

## 🔗 API Endpoint'leri

### 📦 Ürün Yönetimi

#### 1. Ürünleri Listele
```http
GET /api/products
```

**Response:**
```json
{
  "products": [
    {
      "id": "1",
      "name": "Girişimcilik Kulübü T-Shirt",
      "description": "Kulübümüzün özel tasarım t-shirt'ü",
      "image": "https://example.com/image.jpg",
      "points": 500,
      "category": "Giyim",
      "stock": 25,
      "isAvailable": true,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ]
}
```

#### 2. Yeni Ürün Ekle
```http
POST /api/products
```

**Request Body:**
```json
{
  "name": "Ürün Adı",
  "description": "Ürün açıklaması",
  "image": "https://example.com/image.jpg",
  "points": 500,
  "category": "Giyim",
  "stock": 25
}
```

**Response:**
```json
{
  "success": true,
  "product": {
    "id": "1",
    "name": "Ürün Adı",
    "description": "Ürün açıklaması",
    "image": "https://example.com/image.jpg",
    "points": 500,
    "category": "Giyim",
    "stock": 25,
    "isAvailable": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

#### 3. Ürün Güncelle
```http
PUT /api/products/{product_id}
```

**Request Body:**
```json
{
  "name": "Güncellenmiş Ürün Adı",
  "description": "Güncellenmiş açıklama",
  "image": "https://example.com/new-image.jpg",
  "points": 600,
  "category": "Giyim",
  "stock": 30,
  "isAvailable": true
}
```

**Response:**
```json
{
  "success": true,
  "product": {
    "id": "1",
    "name": "Güncellenmiş Ürün Adı",
    "description": "Güncellenmiş açıklama",
    "image": "https://example.com/new-image.jpg",
    "points": 600,
    "category": "Giyim",
    "stock": 30,
    "isAvailable": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

#### 4. Ürün Sil
```http
DELETE /api/products/{product_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Product deleted"
}
```

### 🛒 Satın Alım İşlemleri

#### 5. Ürün Satın Al
```http
POST /api/purchase
```

**Request Body:**
```json
{
  "user_name": "Kullanıcı Adı",
  "product_id": "1",
  "points": 500
}
```

**Response:**
```json
{
  "success": true,
  "message": "Purchase completed successfully",
  "purchase": {
    "id": 1,
    "user_name": "Kullanıcı Adı",
    "product_id": 1,
    "points_spent": 500,
    "created_at": "2024-01-01T00:00:00"
  }
}
```

## 🚀 Kurulum ve Çalıştırma

### 1. Gereksinimler
```bash
pip install -r requirements.txt
```

### 2. Veritabanı Tablolarını Oluştur
```bash
export CREATE_TABLES=1
python app.py
```

### 3. Uygulamayı Çalıştır
```bash
python app.py
```

## 🔧 Kategoriler

Desteklenen ürün kategorileri:
- Giyim
- Yemek & İçecek
- Kitap
- Etkinlik
- Mentorluk

## ⚠️ Hata Kodları

- `400` - Eksik veya geçersiz veri
- `404` - Ürün bulunamadı
- `500` - Sunucu hatası

## 📝 Notlar

1. **Görsel URL'leri:** Ürün görselleri için geçerli URL'ler kullanılmalıdır
2. **Puan Sistemi:** Puan kontrolü şu an basit tutulmuştur, ileride puan API'si ile entegre edilecektir
3. **Stok Yönetimi:** Satın alım sırasında stok otomatik olarak azaltılır
4. **Güvenlik:** Admin kontrolü eklenebilir

## 🔄 Güncelleme Geçmişi

- **v1.0** - Temel ürün yönetimi ve satın alım sistemi
- **v1.1** - Stok yönetimi eklendi
- **v1.2** - Satın alım geçmişi eklendi 