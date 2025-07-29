import os
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from flask_session import Session
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import func
import json
from io import BytesIO

from config import Config
from models import db, Menu, Order, OrderItem

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 데이터베이스 초기화
    db.init_app(app)
    
    # 세션 초기화
    Session(app)
    
    # 업로드 폴더 생성
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
    
    return app

app = create_app()

def allowed_file(filename):
    """허용된 파일 확장자인지 확인"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def admin_required(f):
    """관리자 인증이 필요한 라우트 데코레이터"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ====================== 메인 라우트 ======================

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/init_db')
def init_db():
    """데이터베이스 초기화"""
    try:
        db.create_all()
        
        # 기본 메뉴 데이터 추가 (없는 경우에만)
        if Menu.query.count() == 0:
            sample_menus = [
                Menu(name='아메리카노', category='커피', price=4000, description='깔끔한 맛의 아메리카노', temperature_option='both', display_order=1),
                Menu(name='카페라떼', category='커피', price=4500, description='부드러운 우유가 들어간 라떼', temperature_option='both', display_order=2),
                Menu(name='카푸치노', category='커피', price=4500, description='풍부한 거품의 카푸치노', temperature_option='both', display_order=3),
                Menu(name='녹차라떼', category='차', price=4000, description='진한 녹차의 맛', temperature_option='both', display_order=4),
                Menu(name='치즈케이크', category='디저트', price=5000, description='부드러운 치즈케이크', temperature_option='none', display_order=5),
                Menu(name='초콜릿 머핀', category='디저트', price=3500, description='달콤한 초콜릿 머핀', temperature_option='none', display_order=6),
            ]
            
            for menu in sample_menus:
                db.session.add(menu)
            
            db.session.commit()
        
        flash('데이터베이스가 초기화되었습니다.', 'success')
    except Exception as e:
        flash(f'데이터베이스 초기화 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/update_db_schema')
def update_db_schema():
    """데이터베이스 스키마 업데이트"""
    try:
        db.create_all()
        flash('데이터베이스 스키마가 업데이트되었습니다.', 'success')
    except Exception as e:
        flash(f'스키마 업데이트 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('index'))

# ====================== 사용자 라우트 ======================

@app.route('/user/menu')
def user_menu():
    """메뉴 조회"""
    category = request.args.get('category', '')
    
    if category:
        menus = Menu.query.filter_by(category=category).order_by(Menu.display_order, Menu.id).all()
    else:
        menus = Menu.query.order_by(Menu.display_order, Menu.id).all()
    
    categories = db.session.query(Menu.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    # 장바구니 아이템 수 계산
    cart_count = len(session.get('cart', []))
    
    return render_template('user/menu.html', menus=menus, categories=categories, selected_category=category, cart_count=cart_count)

@app.route('/user/add_to_cart', methods=['POST'])
def add_to_cart():
    """장바구니에 추가"""
    try:
        menu_id = int(request.form['menu_id'])
        quantity = int(request.form['quantity'])
        temperature = request.form.get('temperature', 'ice')
        special_request = request.form.get('special_request', '')
        
        menu = Menu.query.get_or_404(menu_id)
        
        if menu.is_soldout:
            flash('품절된 메뉴입니다.', 'error')
            return redirect(url_for('user_menu'))
        
        cart = session.get('cart', [])
        
        # 기존 아이템이 있는지 확인 (같은 메뉴, 같은 온도, 같은 요청사항)
        existing_item = None
        for item in cart:
            if (item['menu_id'] == menu_id and 
                item['temperature'] == temperature and 
                item['special_request'] == special_request):
                existing_item = item
                break
        
        if existing_item:
            existing_item['quantity'] += quantity
            existing_item['subtotal'] = existing_item['quantity'] * menu.price
        else:
            cart_item = {
                'menu_id': menu_id,
                'menu_name': menu.name,
                'price': menu.price,
                'quantity': quantity,
                'temperature': temperature,
                'special_request': special_request,
                'subtotal': quantity * menu.price
            }
            cart.append(cart_item)
        
        session['cart'] = cart
        flash(f'{menu.name}이(가) 장바구니에 추가되었습니다.', 'success')
        
    except Exception as e:
        flash(f'장바구니 추가 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('user_menu'))

@app.route('/user/view_cart')
def view_cart():
    """장바구니 조회"""
    cart = session.get('cart', [])
    total_amount = sum(item['subtotal'] for item in cart)
    
    return render_template('user/cart.html', cart=cart, total_amount=total_amount)

@app.route('/user/update_cart', methods=['POST'])
def update_cart():
    """장바구니 수정"""
    try:
        action = request.form.get('action')
        index = int(request.form.get('index'))
        cart = session.get('cart', [])
        
        if action == 'remove' and 0 <= index < len(cart):
            removed_item = cart.pop(index)
            flash(f'{removed_item["menu_name"]}이(가) 장바구니에서 제거되었습니다.', 'success')
        elif action == 'update' and 0 <= index < len(cart):
            quantity = int(request.form.get('quantity', 1))
            if quantity > 0:
                cart[index]['quantity'] = quantity
                cart[index]['subtotal'] = quantity * cart[index]['price']
                flash('수량이 업데이트되었습니다.', 'success')
            else:
                removed_item = cart.pop(index)
                flash(f'{removed_item["menu_name"]}이(가) 장바구니에서 제거되었습니다.', 'success')
        
        session['cart'] = cart
        
    except Exception as e:
        flash(f'장바구니 업데이트 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('view_cart'))

@app.route('/user/place_order', methods=['POST'])
def place_order():
    """주문하기"""
    try:
        cart = session.get('cart', [])
        if not cart:
            flash('장바구니가 비어있습니다.', 'error')
            return redirect(url_for('view_cart'))
        
        customer_name = request.form['customer_name']
        delivery_location = request.form['delivery_location']
        delivery_time = request.form.get('delivery_time', '')
        order_request = request.form.get('order_request', '')
        
        if not customer_name or not delivery_location:
            flash('고객명과 배달 위치는 필수입니다.', 'error')
            return redirect(url_for('view_cart'))
        
        total_amount = sum(item['subtotal'] for item in cart)
        
        # 주문 생성
        order = Order(
            customer_name=customer_name,
            delivery_location=delivery_location,
            delivery_time=delivery_time,
            order_request=order_request,
            total_amount=int(total_amount),
            status='pending'
        )
        
        db.session.add(order)
        db.session.flush()  # order.id를 얻기 위해
        
        # 주문 항목 생성
        for item in cart:
            order_item = OrderItem(
                order_id=order.id,
                menu_id=item['menu_id'],
                quantity=item['quantity'],
                subtotal=item['subtotal'],
                temperature=item['temperature'],
                special_request=item['special_request']
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        # 장바구니 비우기
        session['cart'] = []
        
        flash(f'주문이 완료되었습니다. 주문번호: {order.id}', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'주문 처리 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('view_cart'))

@app.route('/user/clear_cart', methods=['POST'])
def clear_cart():
    """장바구니 비우기"""
    session['cart'] = []
    flash('장바구니가 비워졌습니다.', 'success')
    return redirect(url_for('view_cart'))

# ====================== 관리자 라우트 ======================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """관리자 로그인"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            flash('관리자로 로그인되었습니다.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('아이디 또는 비밀번호가 잘못되었습니다.', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@admin_required
def admin_logout():
    """관리자 로그아웃"""
    session.pop('admin_logged_in', None)
    flash('로그아웃되었습니다.', 'success')
    return redirect(url_for('index'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    """관리자 대시보드"""
    # 오늘 주문 통계
    today = datetime.now().date()
    today_orders = Order.query.filter(func.date(Order.order_date) == today).all()
    today_sales = sum(order.total_amount for order in today_orders)
    today_count = len(today_orders)
    
    # 최근 주문 5개
    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(5).all()
    
    # 전체 통계
    total_orders = Order.query.count()
    total_sales = db.session.query(func.sum(Order.total_amount)).scalar() or 0
    
    return render_template('admin/sales.html', 
                         today_sales=today_sales, 
                         today_count=today_count,
                         recent_orders=recent_orders,
                         total_orders=total_orders,
                         total_sales=total_sales)

@app.route('/admin/sales')
@admin_required
def admin_sales():
    """매출 관리"""
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/sales/filter', methods=['POST'])
@admin_required
def filter_sales():
    """매출 필터링"""
    try:
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        query = Order.query
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(func.date(Order.order_date) >= start_date)
        
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(func.date(Order.order_date) <= end_date)
        
        orders = query.order_by(Order.order_date.desc()).all()
        total_sales = sum(order.total_amount for order in orders)
        
        return render_template('admin/order_list.html', 
                             orders=orders, 
                             total_sales=total_sales,
                             start_date=start_date,
                             end_date=end_date)
        
    except Exception as e:
        flash(f'필터링 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

# ====================== 메뉴 관리 ======================

@app.route('/admin/menu')
@admin_required
def admin_menu():
    """메뉴 관리"""
    category = request.args.get('category', '')
    
    if category:
        menus = Menu.query.filter_by(category=category).order_by(Menu.display_order, Menu.id).all()
    else:
        menus = Menu.query.order_by(Menu.display_order, Menu.id).all()
    
    categories = db.session.query(Menu.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('admin/menu.html', menus=menus, categories=categories, selected_category=category)

@app.route('/admin/menu/add', methods=['GET', 'POST'])
@admin_required
def add_menu():
    """메뉴 추가"""
    if request.method == 'POST':
        try:
            name = request.form['name']
            category = request.form['category']
            price = float(request.form['price'])
            description = request.form.get('description', '')
            temperature_option = request.form.get('temperature_option', 'both')
            display_order = int(request.form.get('display_order', 9999))
            
            # 이미지 업로드 처리
            image_filename = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # 고유한 파일명 생성
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = timestamp + filename
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    image_filename = filename
            
            menu = Menu(
                name=name,
                category=category,
                price=price,
                description=description,
                image=image_filename,
                temperature_option=temperature_option,
                display_order=display_order
            )
            
            db.session.add(menu)
            db.session.commit()
            
            flash('메뉴가 추가되었습니다.', 'success')
            return redirect(url_for('admin_menu'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'메뉴 추가 중 오류가 발생했습니다: {str(e)}', 'error')
    
    # 기존 카테고리 목록
    categories = db.session.query(Menu.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('admin/add_menu.html', categories=categories)

@app.route('/admin/menu/edit/<int:menu_id>', methods=['GET', 'POST'])
@admin_required
def edit_menu(menu_id):
    """메뉴 수정"""
    menu = Menu.query.get_or_404(menu_id)
    
    if request.method == 'POST':
        try:
            menu.name = request.form['name']
            menu.category = request.form['category']
            menu.price = float(request.form['price'])
            menu.description = request.form.get('description', '')
            menu.temperature_option = request.form.get('temperature_option', 'both')
            menu.display_order = int(request.form.get('display_order', 9999))
            
            # 이미지 업로드 처리
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '' and allowed_file(file.filename):
                    # 기존 이미지 삭제
                    if menu.image:
                        old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], menu.image)
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)
                    
                    # 새 이미지 저장
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = timestamp + filename
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    menu.image = filename
            
            menu.updated_at = datetime.now()
            db.session.commit()
            
            flash('메뉴가 수정되었습니다.', 'success')
            return redirect(url_for('admin_menu'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'메뉴 수정 중 오류가 발생했습니다: {str(e)}', 'error')
    
    # 기존 카테고리 목록
    categories = db.session.query(Menu.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('admin/edit_menu.html', menu=menu, categories=categories)

@app.route('/admin/menu/delete/<int:menu_id>')
@admin_required
def delete_menu(menu_id):
    """메뉴 삭제"""
    try:
        menu = Menu.query.get_or_404(menu_id)
        
        # 이미지 파일 삭제
        if menu.image:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], menu.image)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(menu)
        db.session.commit()
        
        flash('메뉴가 삭제되었습니다.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'메뉴 삭제 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('admin_menu'))

@app.route('/admin/menu/toggle_soldout/<int:menu_id>', methods=['POST'])
@admin_required
def toggle_soldout(menu_id):
    """품절 상태 토글"""
    try:
        menu = Menu.query.get_or_404(menu_id)
        menu.is_soldout = not menu.is_soldout
        menu.updated_at = datetime.now()
        db.session.commit()
        
        status = "품절" if menu.is_soldout else "판매중"
        return jsonify({'success': True, 'status': status, 'is_soldout': menu.is_soldout})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/menu/update_order', methods=['POST'])
@admin_required
def update_menu_order():
    """메뉴 순서 변경"""
    try:
        menu_orders = request.json.get('menu_orders', [])
        
        for item in menu_orders:
            menu = Menu.query.get(item['id'])
            if menu:
                menu.display_order = item['order']
        
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

# ====================== 카테고리 관리 ======================

@app.route('/admin/categories')
@admin_required
def admin_categories():
    """카테고리 관리"""
    categories = db.session.query(Menu.category).distinct().all()
    categories = [cat[0] for cat in categories]
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/categories', methods=['POST'])
@admin_required
def add_category():
    """카테고리 추가"""
    try:
        category_name = request.form['category_name'].strip()
        if category_name:
            # 이미 존재하는지 확인
            existing = db.session.query(Menu.category).filter_by(category=category_name).first()
            if not existing:
                flash(f'카테고리 "{category_name}"가 추가되었습니다.', 'success')
            else:
                flash('이미 존재하는 카테고리입니다.', 'error')
        else:
            flash('카테고리 이름을 입력해주세요.', 'error')
    except Exception as e:
        flash(f'카테고리 추가 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('admin_categories'))

@app.route('/admin/categories/delete/<category>', methods=['POST'])
@admin_required
def delete_category(category):
    """카테고리 삭제"""
    try:
        # 해당 카테고리의 메뉴가 있는지 확인
        menus_count = Menu.query.filter_by(category=category).count()
        if menus_count > 0:
            flash(f'카테고리 "{category}"에 {menus_count}개의 메뉴가 있습니다. 먼저 메뉴를 삭제하거나 다른 카테고리로 이동해주세요.', 'error')
        else:
            flash(f'카테고리 "{category}"가 삭제되었습니다.', 'success')
    except Exception as e:
        flash(f'카테고리 삭제 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('admin_categories'))

# ====================== 주문 관리 ======================

@app.route('/admin/get_recent_orders')
@admin_required
def get_recent_orders():
    """최근 주문 조회 (AJAX)"""
    try:
        orders = Order.query.order_by(Order.order_date.desc()).limit(10).all()
        orders_data = []
        
        for order in orders:
            orders_data.append({
                'id': order.id,
                'order_date': order.order_date.strftime('%Y-%m-%d %H:%M'),
                'customer_name': order.customer_name,
                'total_amount': order.total_amount,
                'status': order.status,
                'delivery_location': order.delivery_location
            })
        
        return jsonify({'success': True, 'orders': orders_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/update_order_status/<int:order_id>', methods=['POST'])
@admin_required
def update_order_status(order_id):
    """주문 상태 업데이트 (AJAX)"""
    try:
        order = Order.query.get_or_404(order_id)
        new_status = request.json.get('status')
        
        if new_status in ['pending', 'preparing', 'completed', 'cancelled']:
            order.status = new_status
            order.updated_at = datetime.now()
            db.session.commit()
            
            return jsonify({'success': True, 'status': new_status})
        else:
            return jsonify({'success': False, 'error': '잘못된 상태값입니다.'})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/delete_order/<int:order_id>', methods=['POST'])
@admin_required
def delete_order(order_id):
    """주문 삭제 (AJAX)"""
    try:
        order = Order.query.get_or_404(order_id)
        db.session.delete(order)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

# ====================== 데이터 가져오기/내보내기 ======================

@app.route('/admin/export_all_orders')
@admin_required
def export_all_orders():
    """전체 주문 내역 내보내기"""
    try:
        orders = Order.query.order_by(Order.order_date.desc()).all()
        
        data = []
        for order in orders:
            for item in order.order_items:
                data.append({
                    '주문번호': order.id,
                    '주문일시': order.order_date.strftime('%Y-%m-%d %H:%M:%S'),
                    '고객명': order.customer_name,
                    '배달위치': order.delivery_location,
                    '배달시간': order.delivery_time or '',
                    '메뉴명': item.menu.name if item.menu else '삭제된 메뉴',
                    '수량': item.quantity,
                    '온도': item.temperature,
                    '특별요청': item.special_request or '',
                    '소계': item.subtotal,
                    '총액': order.total_amount,
                    '상태': order.status,
                    '주문요청사항': order.order_request or ''
                })
        
        df = pd.DataFrame(data)
        
        # Excel 파일로 저장
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='주문내역', index=False)
        
        output.seek(0)
        
        filename = f"전체주문내역_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        flash(f'내보내기 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/export_period_orders', methods=['POST'])
@admin_required
def export_period_orders():
    """기간별 주문 내역 내보내기"""
    try:
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        query = Order.query
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(func.date(Order.order_date) >= start_date)
        
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(func.date(Order.order_date) <= end_date)
        
        orders = query.order_by(Order.order_date.desc()).all()
        
        data = []
        for order in orders:
            for item in order.order_items:
                data.append({
                    '주문번호': order.id,
                    '주문일시': order.order_date.strftime('%Y-%m-%d %H:%M:%S'),
                    '고객명': order.customer_name,
                    '배달위치': order.delivery_location,
                    '배달시간': order.delivery_time or '',
                    '메뉴명': item.menu.name if item.menu else '삭제된 메뉴',
                    '수량': item.quantity,
                    '온도': item.temperature,
                    '특별요청': item.special_request or '',
                    '소계': item.subtotal,
                    '총액': order.total_amount,
                    '상태': order.status,
                    '주문요청사항': order.order_request or ''
                })
        
        df = pd.DataFrame(data)
        
        # Excel 파일로 저장
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='주문내역', index=False)
        
        output.seek(0)
        
        filename = f"주문내역_{start_date}_{end_date}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        flash(f'내보내기 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/import_orders', methods=['GET', 'POST'])
@admin_required
def import_orders():
    """주문 데이터 가져오기"""
    if request.method == 'POST':
        try:
            if 'file' not in request.files:
                flash('파일을 선택해주세요.', 'error')
                return redirect(request.url)
            
            file = request.files['file']
            if file.filename == '':
                flash('파일을 선택해주세요.', 'error')
                return redirect(request.url)
            
            if file and file.filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)
                
                imported_count = 0
                error_count = 0
                
                for _, row in df.iterrows():
                    try:
                        # 필수 컬럼 확인
                        if pd.isna(row.get('고객명')) or pd.isna(row.get('배달위치')):
                            error_count += 1
                            continue
                        
                        order = Order(
                            customer_name=str(row['고객명']),
                            delivery_location=str(row['배달위치']),
                            delivery_time=str(row.get('배달시간', '')),
                            order_request=str(row.get('주문요청사항', '')),
                            total_amount=int(row.get('총액', 0)),
                            status=str(row.get('상태', 'pending'))
                        )
                        
                        db.session.add(order)
                        imported_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        continue
                
                db.session.commit()
                flash(f'총 {imported_count}개의 주문이 가져왔습니다. (오류: {error_count}개)', 'success')
                
            else:
                flash('Excel 파일(.xlsx, .xls)만 업로드 가능합니다.', 'error')
                
        except Exception as e:
            db.session.rollback()
            flash(f'파일 가져오기 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return render_template('admin/import_orders.html')

# ====================== 영수증 출력 ======================

@app.route('/admin/print_receipt/<int:order_id>')
@admin_required
def print_receipt(order_id):
    """영수증 출력"""
    order = Order.query.get_or_404(order_id)
    return render_template('admin/receipt.html', order=order)

@app.route('/admin/print_receipt_small/<int:order_id>')
@admin_required
def print_receipt_small(order_id):
    """작은 영수증 출력"""
    order = Order.query.get_or_404(order_id)
    return render_template('admin/receipt_small.html', order=order)

# ====================== 기타 기능 ======================

@app.context_processor
def inject_cart_count():
    """모든 템플릿에서 사용할 수 있는 장바구니 개수"""
    return dict(cart_count=len(session.get('cart', [])))

@app.template_filter('currency')
def currency_filter(amount):
    """통화 형식 필터"""
    return f"{amount:,}원"

@app.template_filter('status_badge')
def status_badge_filter(status):
    """상태 배지 클래스 필터"""
    status_classes = {
        'pending': 'bg-warning',
        'preparing': 'bg-info',
        'completed': 'bg-success',
        'cancelled': 'bg-danger'
    }
    return status_classes.get(status, 'bg-secondary')

@app.template_filter('status_text')
def status_text_filter(status):
    """상태 텍스트 필터"""
    status_texts = {
        'pending': '대기중',
        'preparing': '준비중',
        'completed': '완료',
        'cancelled': '취소'
    }
    return status_texts.get(status, status)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 