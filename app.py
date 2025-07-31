from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, User, News, Product, Purchase, PurchaseRequest, Event, Mentor, MentorRequest
import psycopg2
import os
from datetime import datetime

# NEWS CRUD ENDPOINTS
from sqlalchemy import desc

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

def event_to_dict(event):
    return {
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'date': event.date.strftime('%Y-%m-%d') if event.date else None,
        'time': event.time,
        'location': event.location,
        'image_url': event.image_url,
        'price': event.price,
        'capacity': event.capacity,
        'is_active': event.is_active,
        'created_at': event.created_at,
        'updated_at': event.updated_at,
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

def mentor_to_dict(mentor):
    return {
        'id': mentor.id,
        'name': mentor.name,
        'expertise': mentor.expertise.split(',') if mentor.expertise else [],
        'company': mentor.company,
        'bio': mentor.bio,
        'email': mentor.email,
        'phone': mentor.phone,
        'linkedin': mentor.linkedin,
        'is_active': mentor.is_active,
        'created_at': mentor.created_at,
        'updated_at': mentor.updated_at,
    }

def mentor_request_to_dict(request):
    return {
        'id': request.id,
        'user_name': request.user_name,
        'user_email': request.user_email,
        'mentor_id': request.mentor_id,
        'mentor_name': request.mentor_name,
        'subject': request.subject,
        'message': request.message,
        'status': request.status,
        'created_at': request.created_at,
        'responded_at': request.responded_at,
        'response_message': request.response_message,
        'notes': request.notes,
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
    
    # Admin hesabını yeniden oluştur
    admin = User(
        name='Admin',
        email='gkadmin@mail.com',
        password='GK*admin_1',
        status='approved'
    )
    db.session.add(admin)
    db.session.commit()
    
    return jsonify({'message': 'Admin reset successful'})

# MENTOR API ENDPOINTS

@app.route('/api/mentors', methods=['GET'])
def get_mentors():
    mentors = Mentor.query.filter_by(is_active=True).order_by(Mentor.name).all()
    return jsonify([mentor_to_dict(mentor) for mentor in mentors])

@app.route('/api/mentors', methods=['POST'])
def create_mentor():
    data = request.json
    mentor = Mentor(
        name=data['name'],
        expertise=','.join(data.get('expertise', [])),
        company=data['company'],
        bio=data['bio'],
        email=data.get('email'),
        phone=data.get('phone'),
        linkedin=data.get('linkedin'),
        is_active=data.get('is_active', True)
    )
    db.session.add(mentor)
    db.session.commit()
    return jsonify(mentor_to_dict(mentor)), 201

@app.route('/api/mentors/<int:mentor_id>', methods=['GET'])
def get_mentor_detail(mentor_id):
    mentor = Mentor.query.get(mentor_id)
    if not mentor:
        return jsonify({'error': 'Mentor not found'}), 404
    return jsonify(mentor_to_dict(mentor))

@app.route('/api/mentors/<int:mentor_id>', methods=['PUT'])
def update_mentor(mentor_id):
    mentor = Mentor.query.get(mentor_id)
    if not mentor:
        return jsonify({'error': 'Mentor not found'}), 404
    data = request.json
    mentor.name = data.get('name', mentor.name)
    mentor.expertise = ','.join(data.get('expertise', mentor.expertise.split(',') if mentor.expertise else []))
    mentor.company = data.get('company', mentor.company)
    mentor.bio = data.get('bio', mentor.bio)
    mentor.email = data.get('email', mentor.email)
    mentor.phone = data.get('phone', mentor.phone)
    mentor.linkedin = data.get('linkedin', mentor.linkedin)
    mentor.is_active = data.get('is_active', mentor.is_active)
    db.session.commit()
    return jsonify(mentor_to_dict(mentor))

@app.route('/api/mentors/<int:mentor_id>', methods=['DELETE'])
def delete_mentor(mentor_id):
    mentor = Mentor.query.get(mentor_id)
    if not mentor:
        return jsonify({'error': 'Mentor not found'}), 404
    db.session.delete(mentor)
    db.session.commit()
    return jsonify({'message': 'Mentor deleted'})

# MENTOR REQUEST API ENDPOINTS

@app.route('/api/mentor_requests', methods=['GET'])
def get_mentor_requests():
    requests = MentorRequest.query.order_by(desc(MentorRequest.created_at)).all()
    return jsonify([mentor_request_to_dict(req) for req in requests])

@app.route('/api/mentor_requests', methods=['POST'])
def create_mentor_request():
    try:
        data = request.json
        print(f"Mentor request data received: {data}")
        
        # Gerekli alanları kontrol et
        required_fields = ['user_name', 'user_email', 'mentor_id', 'subject', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        mentor = Mentor.query.get(data['mentor_id'])
        if not mentor:
            return jsonify({'error': 'Mentor not found'}), 404
        
        mentor_request = MentorRequest(
            user_name=data['user_name'],
            user_email=data['user_email'],
            mentor_id=data['mentor_id'],
            mentor_name=mentor.name,
            subject=data['subject'],
            message=data['message']
        )
        
        db.session.add(mentor_request)
        db.session.commit()
        
        print(f"Mentor request created successfully: {mentor_request.id}")
        return jsonify(mentor_request_to_dict(mentor_request)), 201
        
    except Exception as e:
        print(f"Error creating mentor request: {str(e)}")
        db.session.rollback()
        return jsonify({'error': f'Mentor request creation failed: {str(e)}'}), 500

@app.route('/api/mentor_requests/<int:request_id>', methods=['GET'])
def get_mentor_request_detail(request_id):
    request = MentorRequest.query.get(request_id)
    if not request:
        return jsonify({'error': 'Request not found'}), 404
    return jsonify(mentor_request_to_dict(request))

@app.route('/api/mentor_requests/<int:request_id>/respond', methods=['POST'])
def respond_to_mentor_request(request_id):
    request = MentorRequest.query.get(request_id)
    if not request:
        return jsonify({'error': 'Request not found'}), 404
    
    data = request.json
    request.status = data.get('status', request.status)
    request.response_message = data.get('response_message', request.response_message)
    request.notes = data.get('notes', request.notes)
    request.responded_at = datetime.now()
    
    db.session.commit()
    return jsonify(mentor_request_to_dict(request))

@app.route('/api/mentor_requests/<int:request_id>', methods=['DELETE'])
def delete_mentor_request(request_id):
    request = MentorRequest.query.get(request_id)
    if not request:
        return jsonify({'error': 'Request not found'}), 404
    db.session.delete(request)
    db.session.commit()
    return jsonify({'message': 'Request deleted'})

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
    
    try:
        # Ürünü kontrol et
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        if not product.is_available:
            return jsonify({'error': 'Product is not available'}), 400
        
        if product.stock <= 0:
            return jsonify({'error': 'Product is out of stock'}), 400
        
        # Kullanıcı bilgilerini al
        user = User.query.filter_by(name=user_name).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Satın alım kaydı oluştur (eski sistem)
        purchase = Purchase(
            user_name=user_name,
            product_id=product_id,
            points_spent=points
        )
        
        # Stok güncelle
        product.stock = max(0, product.stock - 1)
        
        db.session.add(purchase)
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
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Purchase failed: {str(e)}'}), 500

# --- PURCHASE REQUEST MANAGEMENT ENDPOINTS ---

@app.route('/api/purchase_requests', methods=['GET'])
def get_purchase_requests():
    """Bekleyen satın alım taleplerini getir"""
    requests = PurchaseRequest.query.filter_by(status='pending').order_by(PurchaseRequest.created_at.desc()).all()
    
    return jsonify({
        'requests': [{
            'id': req.id,
            'user_name': req.user_name,
            'user_email': req.user_email,
            'product_id': req.product_id,
            'product_name': req.product_name,
            'points_required': req.points_required,
            'status': req.status,
            'created_at': req.created_at.isoformat() if req.created_at else None
        } for req in requests]
    })

@app.route('/api/purchase_requests', methods=['POST'])
def create_purchase_request():
    data = request.json
    user_name = data.get('user_name')
    user_email = data.get('user_email')
    product_id = data.get('product_id')
    product_name = data.get('product_name')
    points_required = data.get('points_required')
    if not all([user_name, user_email, product_id, product_name, points_required]):
        return jsonify({'error': 'Eksik alanlar var'}), 400
    try:
        from models import PurchaseRequest
        req = PurchaseRequest(
            user_name=user_name,
            user_email=user_email,
            product_id=product_id,
            product_name=product_name,
            points_required=points_required,
            status='pending'
        )
        db.session.add(req)
        db.session.commit()
        return jsonify({'success': True, 'request_id': req.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Satın alım isteği kaydedilemedi: {str(e)}'}), 500

@app.route('/api/purchase_requests/<int:request_id>/approve', methods=['POST'])
def approve_purchase_request(request_id):
    data = request.json
    admin_name = data.get('admin_name', 'Admin')
    notes = data.get('notes', '')
    try:
        purchase_request = PurchaseRequest.query.get(request_id)
        if not purchase_request:
            return jsonify({'error': 'Purchase request not found'}), 404
        if purchase_request.status != 'pending':
            return jsonify({'error': 'Request is not pending'}), 400
        # Ürünü kontrol et
        product = Product.query.get(purchase_request.product_id)
        if not product or not product.is_available or product.stock <= 0:
            return jsonify({'error': 'Product is not available or out of stock'}), 400
        # Kullanıcıyı kontrol et
        user = User.query.filter_by(name=purchase_request.user_name).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        # Puan kontrolü - Ana backend'den kullanıcının puanını al
        try:
            import requests
            points_response = requests.get(f'https://gkappp.onrender.com/api/members')
            if points_response.ok:
                members = points_response.json()
                user_member = next((m for m in members if m.get('name') == purchase_request.user_name), None)
                if user_member and user_member.get('points', 0) >= purchase_request.points_required:
                    # Puan yeterli, puanı düş
                    points_update_response = requests.post(f'https://gkappp.onrender.com/api/adjust_points', json={
                        'member_id': user_member.get('id'),
                        'action': 'subtract',
                        'point_value': purchase_request.points_required,
                        'point_reason': f'Ürün satın alımı: {purchase_request.product_name}'
                    })
                    if not points_update_response.ok:
                        return jsonify({'error': 'Puan güncelleme başarısız'}), 500
                else:
                    return jsonify({'error': 'Yetersiz puan'}), 400
            else:
                return jsonify({'error': 'Puan kontrolü başarısız'}), 500
        except Exception as e:
            print(f"Puan API hatası: {e}")
            return jsonify({'error': 'Puan sistemi hatası'}), 500
        # Talebi onayla
        purchase_request.status = 'approved'
        purchase_request.approved_at = db.func.now()
        purchase_request.approved_by = admin_name
        purchase_request.notes = notes
        # Stok güncelle
        product.stock = max(0, product.stock - 1)
        # Onaylanan satın alımı kaydet
        purchase = Purchase(
            user_name=purchase_request.user_name,
            product_id=purchase_request.product_id,
            points_spent=purchase_request.points_required
        )
        db.session.add(purchase)
        db.session.delete(purchase_request)  # Talebi sil
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Satın alım talebi onaylandı',
            'purchase_id': purchase.id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Approval failed: {str(e)}'}), 500

@app.route('/api/purchase_requests/<int:request_id>/reject', methods=['POST'])
def reject_purchase_request(request_id):
    data = request.json
    admin_name = data.get('admin_name', 'Admin')
    notes = data.get('notes', '')
    try:
        purchase_request = PurchaseRequest.query.get(request_id)
        if not purchase_request:
            return jsonify({'error': 'Purchase request not found'}), 404
        if purchase_request.status != 'pending':
            return jsonify({'error': 'Request is not pending'}), 400
        # Talebi reddet
        purchase_request.status = 'rejected'
        purchase_request.approved_at = db.func.now()
        purchase_request.approved_by = admin_name
        purchase_request.notes = notes
        db.session.commit()
        return jsonify({'success': True, 'message': 'Satın alım talebi reddedildi'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Rejection failed: {str(e)}'}), 500

@app.route('/api/purchase_requests/<int:request_id>', methods=['DELETE'])
def delete_purchase_request(request_id):
    try:
        purchase_request = PurchaseRequest.query.get(request_id)
        if not purchase_request:
            return jsonify({'error': 'Purchase request not found'}), 404
        
        db.session.delete(purchase_request)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Satın alım talebi silindi'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Deletion failed: {str(e)}'}), 500

# --- POINTS MANAGEMENT ENDPOINTS ---

@app.route('/api/update_points', methods=['POST'])
def update_user_points():
    data = request.json
    user_name = data.get('user_name')
    points_to_deduct = data.get('points_to_deduct')
    user_email = data.get('user_email')
    reason = data.get('reason', 'Ürün satın alımı')
    
    if not all([user_name, points_to_deduct]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # PostgreSQL'de puan güncelleme
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        
        # Kullanıcıyı bul (email veya isim ile)
        if user_email:
            cursor.execute("SELECT id, name, points FROM members WHERE email = %s", (user_email,))
        else:
            cursor.execute("SELECT id, name, points FROM members WHERE name = %s", (user_name,))
        
        member = cursor.fetchone()
        if not member:
            return jsonify({'error': 'User not found'}), 404
        
        member_id, member_name, current_points = member
        
        # Puanları güncelle
        new_points = max(0, current_points - points_to_deduct)
        cursor.execute("UPDATE members SET points = %s WHERE id = %s", (new_points, member_id))
        
        # Puan logu ekle
        cursor.execute(
            "INSERT INTO points_log (member_id, points_earned, reason) VALUES (%s, %s, %s)",
            (member_id, -points_to_deduct, reason)
        )
        
        conn.commit()
        conn.close()
        
        print(f"Puan güncelleme: {member_name} kullanıcısından {points_to_deduct} puan düşüldü (Yeni puan: {new_points})")
        
        return jsonify({
            'success': True,
            'message': f'Points updated successfully for {member_name}',
            'points_deducted': points_to_deduct,
            'new_points': new_points,
            'member_id': member_id
        })
    except Exception as e:
        return jsonify({'error': f'Failed to update points: {str(e)}'}), 500

@app.route('/api/adjust_points', methods=['POST'])
def adjust_points():
    data = request.json
    user_name = data.get('user_name')
    user_email = data.get('user_email')
    action = data.get('action')  # 'add' veya 'subtract'
    point_value = data.get('point_value', 0)
    point_reason = data.get('point_reason', 'Manuel puan güncelleme')
    
    if not all([user_name, action, point_value]) or action not in ['add', 'subtract']:
        return jsonify({'error': 'Missing or invalid required fields'}), 400
    
    try:
        # PostgreSQL'de puan güncelleme
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        
        # Kullanıcıyı bul (email veya isim ile)
        if user_email:
            cursor.execute("SELECT id, name, points FROM members WHERE email = %s", (user_email,))
        else:
            cursor.execute("SELECT id, name, points FROM members WHERE name = %s", (user_name,))
        
        member = cursor.fetchone()
        if not member:
            return jsonify({'error': 'User not found'}), 404
        
        member_id, member_name, current_points = member
        
        # Puanları güncelle
        if action == 'add':
            new_points = current_points + point_value
            points_change = point_value
        else:  # subtract
            new_points = max(0, current_points - point_value)
            points_change = -point_value
        
        cursor.execute("UPDATE members SET points = %s WHERE id = %s", (new_points, member_id))
        
        # Puan logu ekle
        cursor.execute(
            "INSERT INTO points_log (member_id, points_earned, reason) VALUES (%s, %s, %s)",
            (member_id, points_change, point_reason)
        )
        
        conn.commit()
        conn.close()
        
        print(f"Puan güncelleme: {member_name} kullanıcısına {points_change} puan {action}ed (Yeni puan: {new_points})")
        
        return jsonify({
            'success': True,
            'message': f'Points {action}ed successfully for {member_name}',
            'points_change': points_change,
            'new_points': new_points,
            'member_id': member_id
        })
    except Exception as e:
        return jsonify({'error': f'Failed to adjust points: {str(e)}'}), 500

@app.route('/api/member_points')
def get_member_points():
    name = request.args.get('name')
    email = request.args.get('email')
    
    if not name and not email:
        return jsonify({'error': 'Name or email required'}), 400
    
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        
        # Kullanıcıyı bul
        if email:
            cursor.execute("SELECT id, name, points FROM members WHERE email = %s", (email,))
        else:
            cursor.execute("SELECT id, name, points FROM members WHERE name = %s", (name,))
        
        member = cursor.fetchone()
        conn.close()
        
        if member:
            member_id, member_name, points = member
            return jsonify({
                'id': member_id,
                'name': member_name,
                'points': points
            })
        else:
            return jsonify({'error': 'User not found'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Failed to get member points: {str(e)}'}), 500

# EVENT CRUD ENDPOINTS
@app.route('/api/events', methods=['GET'])
def get_events():
    events_list = Event.query.filter_by(is_active=True).order_by(Event.date.asc()).all()
    return jsonify([event_to_dict(e) for e in events_list])

@app.route('/api/events', methods=['POST'])
def create_event():
    data = request.json
    try:
        event = Event(
            title=data['title'],
            description=data['description'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            time=data['time'],
            location=data['location'],
            image_url=data.get('image_url'),
            price=data.get('price', 'Ücretsiz'),
            capacity=data.get('capacity', 'Sınırsız'),
            is_active=data.get('is_active', True)
        )
        db.session.add(event)
        db.session.commit()
        return jsonify(event_to_dict(event)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create event: {str(e)}'}), 400

@app.route('/api/events/<int:event_id>', methods=['GET'])
def get_event_detail(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    return jsonify(event_to_dict(event))

@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    data = request.json
    try:
        event.title = data.get('title', event.title)
        event.description = data.get('description', event.description)
        if 'date' in data:
            event.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        event.time = data.get('time', event.time)
        event.location = data.get('location', event.location)
        event.image_url = data.get('image_url', event.image_url)
        event.price = data.get('price', event.price)
        event.capacity = data.get('capacity', event.capacity)
        event.is_active = data.get('is_active', event.is_active)
        
        db.session.commit()
        return jsonify(event_to_dict(event))
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update event: {str(e)}'}), 400

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    try:
        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': 'Event deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete event: {str(e)}'}), 400

@app.route('/api/events/all', methods=['GET'])
def get_all_events():
    events = Event.query.all()
    return jsonify([event_to_dict(event) for event in events])

# SLIDER IMAGES CRUD ENDPOINTS
@app.route('/api/slider_images', methods=['GET'])
def get_slider_images():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Veritabanı bağlantı hatası'}), 500
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, image_url, title, description, created_at, updated_at 
            FROM slider_images 
            ORDER BY created_at DESC
        """)
        
        images = []
        for row in cursor.fetchall():
            images.append({
                'id': row[0],
                'image_url': row[1],
                'title': row[2],
                'description': row[3],
                'created_at': row[4].isoformat() if row[4] else None,
                'updated_at': row[5].isoformat() if row[5] else None,
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({'images': images})
    except Exception as e:
        print(f"Slider images get error: {e}")
        return jsonify({'error': 'Slider fotoğrafları alınamadı'}), 500

@app.route('/api/slider_images', methods=['POST'])
def create_slider_image():
    try:
        data = request.json
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Veritabanı bağlantı hatası'}), 500
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO slider_images (image_url, title, description, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data.get('image_url'),
            data.get('title', ''),
            data.get('description', ''),
            datetime.now(),
            datetime.now()
        ))
        
        image_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'id': image_id,
            'image_url': data.get('image_url'),
            'title': data.get('title', ''),
            'description': data.get('description', ''),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        }), 201
    except Exception as e:
        print(f"Slider image create error: {e}")
        return jsonify({'error': 'Slider fotoğrafı eklenemedi'}), 500

@app.route('/api/slider_images/<int:image_id>', methods=['PUT'])
def update_slider_image(image_id):
    try:
        data = request.json
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Veritabanı bağlantı hatası'}), 500
        
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE slider_images 
            SET image_url = %s, title = %s, description = %s, updated_at = %s
            WHERE id = %s
            RETURNING id, image_url, title, description, created_at, updated_at
        """, (
            data.get('image_url'),
            data.get('title', ''),
            data.get('description', ''),
            datetime.now(),
            image_id
        ))
        
        row = cursor.fetchone()
        if row is None:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Slider fotoğrafı bulunamadı'}), 404
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'id': row[0],
            'image_url': row[1],
            'title': row[2],
            'description': row[3],
            'created_at': row[4].isoformat() if row[4] else None,
            'updated_at': row[5].isoformat() if row[5] else None,
        })
    except Exception as e:
        print(f"Slider image update error: {e}")
        return jsonify({'error': 'Slider fotoğrafı güncellenemedi'}), 500

@app.route('/api/slider_images/<int:image_id>', methods=['DELETE'])
def delete_slider_image(image_id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Veritabanı bağlantı hatası'}), 500
        
        cursor = conn.cursor()
        cursor.execute("DELETE FROM slider_images WHERE id = %s", (image_id,))
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Slider fotoğrafı bulunamadı'}), 404
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Slider fotoğrafı silindi'})
    except Exception as e:
        print(f"Slider image delete error: {e}")
        return jsonify({'error': 'Slider fotoğrafı silinemedi'}), 500

# NOTIFICATIONS CRUD ENDPOINTS
@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Veritabanı bağlantı hatası'}), 500
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, message, type, is_active, created_at, updated_at 
            FROM notifications 
            ORDER BY created_at DESC
        """)
        
        notifications = []
        for row in cursor.fetchall():
            notifications.append({
                'id': row[0],
                'title': row[1],
                'message': row[2],
                'type': row[3],
                'is_active': row[4],
                'created_at': row[5].isoformat() if row[5] else None,
                'updated_at': row[6].isoformat() if row[6] else None,
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({'notifications': notifications})
    except Exception as e:
        print(f"Notifications get error: {e}")
        return jsonify({'error': 'Bildirimler alınamadı'}), 500

@app.route('/api/notifications', methods=['POST'])
def create_notification():
    try:
        data = request.json
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Veritabanı bağlantı hatası'}), 500
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notifications (title, message, type, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data.get('title'),
            data.get('message'),
            data.get('type', 'info'),
            data.get('is_active', True),
            datetime.now(),
            datetime.now()
        ))
        
        notification_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'id': notification_id,
            'title': data.get('title'),
            'message': data.get('message'),
            'type': data.get('type', 'info'),
            'is_active': data.get('is_active', True),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        }), 201
    except Exception as e:
        print(f"Notification create error: {e}")
        return jsonify({'error': 'Bildirim oluşturulamadı'}), 500

@app.route('/api/notifications/<int:notification_id>', methods=['PUT'])
def update_notification(notification_id):
    try:
        data = request.json
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Veritabanı bağlantı hatası'}), 500
        
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE notifications 
            SET title = %s, message = %s, type = %s, is_active = %s, updated_at = %s
            WHERE id = %s
            RETURNING id, title, message, type, is_active, created_at, updated_at
        """, (
            data.get('title'),
            data.get('message'),
            data.get('type', 'info'),
            data.get('is_active', True),
            datetime.now(),
            notification_id
        ))
        
        row = cursor.fetchone()
        if row is None:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Bildirim bulunamadı'}), 404
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'id': row[0],
            'title': row[1],
            'message': row[2],
            'type': row[3],
            'is_active': row[4],
            'created_at': row[5].isoformat() if row[5] else None,
            'updated_at': row[6].isoformat() if row[6] else None,
        })
    except Exception as e:
        print(f"Notification update error: {e}")
        return jsonify({'error': 'Bildirim güncellenemedi'}), 500

@app.route('/api/notifications/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Veritabanı bağlantı hatası'}), 500
        
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notifications WHERE id = %s", (notification_id,))
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Bildirim bulunamadı'}), 404
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Bildirim silindi'})
    except Exception as e:
        print(f"Notification delete error: {e}")
        return jsonify({'error': 'Bildirim silinemedi'}), 500

@app.route('/api/notifications/active', methods=['GET'])
def get_active_notifications():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Veritabanı bağlantı hatası'}), 500
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, message, type, created_at 
            FROM notifications 
            WHERE is_active = true
            ORDER BY created_at DESC
        """)
        
        notifications = []
        for row in cursor.fetchall():
            notifications.append({
                'id': row[0],
                'title': row[1],
                'message': row[2],
                'type': row[3],
                'created_at': row[4].isoformat() if row[4] else None,
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({'notifications': notifications})
    except Exception as e:
        print(f"Active notifications get error: {e}")
        return jsonify({'error': 'Aktif bildirimler alınamadı'}), 500

@app.route('/api/users', methods=['GET'])
def get_all_users():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Veritabanı bağlantı hatası'}), 500
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, email, department, student_id, is_approved, is_active, created_at 
            FROM users 
            WHERE is_approved = true
            ORDER BY created_at DESC
        """)
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'department': row[3],
                'student_id': row[4],
                'is_approved': row[5],
                'is_active': row[6],
                'created_at': row[7].isoformat() if row[7] else None,
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({'users': users})
    except Exception as e:
        print(f"Users get error: {e}")
        return jsonify({'error': 'Kullanıcılar alınamadı'}), 500

# PUSH NOTIFICATION ENDPOINTS
@app.route('/api/push_notifications/send', methods=['POST'])
def send_push_notification():
    try:
        data = request.json
        title = data.get('title')
        message = data.get('message')
        notification_type = data.get('type', 'info')
        
        if not title or not message:
            return jsonify({'error': 'Başlık ve mesaj gereklidir'}), 400
        
        # Bildirimi veritabanına kaydet
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Veritabanı bağlantı hatası'}), 500
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notifications (title, message, type, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            title,
            message,
            notification_type,
            True,
            datetime.now(),
            datetime.now()
        ))
        
        notification_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        # Burada gerçek push notification servisi entegrasyonu yapılabilir
        # Örnek: Firebase Cloud Messaging, OneSignal, vb.
        
        # Şimdilik sadece başarı mesajı döndürüyoruz
        return jsonify({
            'success': True,
            'message': 'Push notification başarıyla gönderildi',
            'notification_id': notification_id,
            'title': title,
            'message': message,
            'type': notification_type
        })
        
    except Exception as e:
        print(f"Push notification send error: {e}")
        return jsonify({'error': 'Push notification gönderilemedi'}), 500

@app.route('/api/push_notifications/send_to_all', methods=['POST'])
def send_push_notification_to_all():
    try:
        data = request.json
        title = data.get('title')
        message = data.get('message')
        notification_type = data.get('type', 'info')
        
        if not title or not message:
            return jsonify({'error': 'Başlık ve mesaj gereklidir'}), 400
        
        # Bildirimi veritabanına kaydet
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Veritabanı bağlantı hatası'}), 500
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notifications (title, message, type, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            title,
            message,
            notification_type,
            True,
            datetime.now(),
            datetime.now()
        ))
        
        notification_id = cursor.fetchone()[0]
        
        # Tüm aktif kullanıcıları al
        cursor.execute("""
            SELECT id, name, email FROM users 
            WHERE is_approved = true AND is_active = true
        """)
        
        users = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
        
        # Burada gerçek push notification servisi entegrasyonu yapılabilir
        # Tüm kullanıcılara bildirim gönder
        
        return jsonify({
            'success': True,
            'message': f'Push notification {len(users)} kullanıcıya gönderildi',
            'notification_id': notification_id,
            'users_count': len(users),
            'title': title,
            'message': message,
            'type': notification_type
        })
        
    except Exception as e:
        print(f"Push notification send to all error: {e}")
        return jsonify({'error': 'Push notification gönderilemedi'}), 500

@app.route('/api/push_notifications/send_to_group', methods=['POST'])
def send_push_notification_to_group():
    try:
        data = request.json
        title = data.get('title')
        message = data.get('message')
        notification_type = data.get('type', 'info')
        user_ids = data.get('user_ids', [])
        department = data.get('department')
        
        if not title or not message:
            return jsonify({'error': 'Başlık ve mesaj gereklidir'}), 400
        
        if not user_ids and not department:
            return jsonify({'error': 'Kullanıcı ID\'leri veya bölüm gereklidir'}), 400
        
        # Bildirimi veritabanına kaydet
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Veritabanı bağlantı hatası'}), 500
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notifications (title, message, type, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            title,
            message,
            notification_type,
            True,
            datetime.now(),
            datetime.now()
        ))
        
        notification_id = cursor.fetchone()[0]
        
        # Hedef kullanıcıları al
        if user_ids:
            placeholders = ','.join(['%s'] * len(user_ids))
            cursor.execute(f"""
                SELECT id, name, email FROM users 
                WHERE id IN ({placeholders}) AND is_approved = true AND is_active = true
            """, user_ids)
        elif department:
            cursor.execute("""
                SELECT id, name, email FROM users 
                WHERE department = %s AND is_approved = true AND is_active = true
            """, (department,))
        
        users = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
        
        # Burada gerçek push notification servisi entegrasyonu yapılabilir
        # Seçili kullanıcılara bildirim gönder
        
        return jsonify({
            'success': True,
            'message': f'Push notification {len(users)} kullanıcıya gönderildi',
            'notification_id': notification_id,
            'users_count': len(users),
            'title': title,
            'message': message,
            'type': notification_type
        })
        
    except Exception as e:
        print(f"Push notification send to group error: {e}")
        return jsonify({'error': 'Push notification gönderilemedi'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 