from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, User, News, Product, Purchase

# NEWS CRUD ENDPOINTS
from sqlalchemy import desc

def news_to_dict(news):
    return {
        'id': news.id,
        'title': news.title,
        'summary': news.summary,
        'category': news.category,
        'tags': news.tags.split(',') if news.tags else [],
        'cover_image_url': news.cover_image_url,
        'created_at': news.created_at,
        'updated_at': news.updated_at,
    }

def product_to_dict(product):
    return {
        'id': str(product.id),
        'name': product.name,
        'description': product.description,
        'image': product.image,
        'points': product.points,
        'category': product.category,
        'stock': product.stock,
        'isAvailable': product.is_available,
        'created_at': product.created_at,
        'updated_at': product.updated_at,
    }

app = Flask(__name__)
CORS(app)

# NeonDB bağlantı adresi (kullanıcının verdiği)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://neondb_owner:npg_J3cztba8mNfo@ep-solitary-silence-a2tdicc0-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
db.init_app(app)

import os
with app.app_context():
    if os.environ.get("CREATE_TABLES", "0") == "1":
        db.create_all()

# --- Tüm route'lar bundan sonra başlıyor ---

@app.route('/api/news', methods=['GET'])
def get_news():
    news_list = News.query.order_by(desc(News.created_at)).all()
    return jsonify([news_to_dict(n) for n in news_list])

@app.route('/api/news', methods=['POST'])
def create_news():
    data = request.json
    news = News(
        title=data['title'],
        summary=data['summary'],
        category=data['category'],
        tags=','.join(data.get('tags', [])),
        cover_image_url=data.get('cover_image_url')
    )
    db.session.add(news)
    db.session.commit()
    return jsonify(news_to_dict(news)), 201

@app.route('/api/news/<int:news_id>', methods=['GET'])
def get_news_detail(news_id):
    news = News.query.get(news_id)
    if not news:
        return jsonify({'error': 'News not found'}), 404
    return jsonify(news_to_dict(news))

@app.route('/api/news/<int:news_id>', methods=['PUT'])
def update_news(news_id):
    news = News.query.get(news_id)
    if not news:
        return jsonify({'error': 'News not found'}), 404
    data = request.json
    news.title = data.get('title', news.title)
    news.summary = data.get('summary', news.summary)
    news.category = data.get('category', news.category)
    news.tags = ','.join(data.get('tags', news.tags.split(',') if news.tags else []))
    news.cover_image_url = data.get('cover_image_url', news.cover_image_url)
    db.session.commit()
    return jsonify(news_to_dict(news))

@app.route('/api/news/<int:news_id>', methods=['DELETE'])
def delete_news(news_id):
    news = News.query.get(news_id)
    if not news:
        return jsonify({'error': 'News not found'}), 404
    db.session.delete(news)
    db.session.commit()
    return jsonify({'message': 'News deleted'})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    # Admin hesabı için otomatik onay ve sabit şifre
    if data['email'] == 'gkadmin@mail.com':
        user = User(
            name=data['name'],
            email=data['email'],
            password='GK*admin_1',
            status='approved'
        )
    else:
        user = User(
            name=data['name'],
            email=data['email'],
            password=data['password'],
            status='pending'
        )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered', 'user': {'id': user.id, 'name': user.name, 'email': user.email, 'status': user.status}})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email'], password=data['password']).first()
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email, 'status': user.status})

@app.route('/api/pending_users', methods=['GET'])
def pending_users():
    users = User.query.filter_by(status='pending').all()
    return jsonify([
        {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'createdAt': user.created_at,
            'studentId': getattr(user, 'studentId', None),
            'department': getattr(user, 'department', None),
        }
        for user in users
    ])

@app.route('/api/approve_user', methods=['POST'])
def approve_user():
    data = request.json
    user = User.query.get(data['user_id'])
    if user:
        user.status = 'approved'
        db.session.commit()
        return jsonify({'message': 'User approved'})
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/reject_user', methods=['POST'])
def reject_user():
    data = request.json
    user = User.query.get(data['user_id'])
    if user:
        user.status = 'rejected'
        db.session.commit()
        return jsonify({'message': 'User rejected'})
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/reset_admin', methods=['POST'])
def reset_admin():
    # Tüm kullanıcıları sil
    User.query.delete()
    db.session.commit()
    # Yeni admin hesabı ekle
    admin = User(
        name='Admin',
        email='gkadmin@mail.com',
        password='GK*admin_1',
        status='approved'
    )
    db.session.add(admin)
    db.session.commit()
    return jsonify({'message': 'Tüm kullanıcılar silindi ve admin hesabı eklendi.',
                    'admin': {'email': admin.email, 'password': admin.password}}), 200

# --- PRODUCT MANAGEMENT ENDPOINTS ---

@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.filter_by(is_available=True).order_by(desc(Product.created_at)).all()
    return jsonify({'products': [product_to_dict(p) for p in products]})

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.json
    product = Product(
        name=data['name'],
        description=data['description'],
        image=data['image'],
        points=data['points'],
        category=data['category'],
        stock=data.get('stock', 0)
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'success': True, 'product': product_to_dict(product)}), 201

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    data = request.json
    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.image = data.get('image', product.image)
    product.points = data.get('points', product.points)
    product.category = data.get('category', product.category)
    product.stock = data.get('stock', product.stock)
    product.is_available = data.get('isAvailable', product.is_available)
    
    db.session.commit()
    return jsonify({'success': True, 'product': product_to_dict(product)})

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Product deleted'})

# --- PURCHASE ENDPOINTS ---

@app.route('/api/purchase', methods=['POST'])
def purchase_product():
    data = request.json
    user_name = data.get('user_name')
    product_id = data.get('product_id')
    points = data.get('points')
    
    if not all([user_name, product_id, points]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Ürünü kontrol et
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    if not product.is_available:
        return jsonify({'error': 'Product is not available'}), 400
    
    if product.stock <= 0:
        return jsonify({'error': 'Product is out of stock'}), 400
    
    # Kullanıcının puanını kontrol et (bu kısım puan API'si ile entegre edilecek)
    # Şimdilik başarılı kabul ediyoruz
    
    # Satın alım kaydı oluştur
    purchase = Purchase(
        user_name=user_name,
        product_id=product_id,
        points_spent=points
    )
    db.session.add(purchase)
    
    # Stok güncelle
    product.stock = max(0, product.stock - 1)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Purchase completed successfully',
        'purchase': {
            'id': purchase.id,
            'user_name': purchase.user_name,
            'product_id': purchase.product_id,
            'points_spent': purchase.points_spent,
            'created_at': purchase.created_at
        }
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 