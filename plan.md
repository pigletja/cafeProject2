

## 프로젝트 개요
Flask 기반의 카페 주문 관리 시스템을 개발합니다. 사용자 주문과 관리자 메뉴 관리 기능을 제공하는 웹 애플리케이션입니다.

## 기술 스택
- **백엔드**: Flask (Python)
- **데이터베이스**: SQLite (SQLAlchemy ORM)
- **프론트엔드**: Bootstrap 5, HTML5, CSS3, JavaScript
- **아이콘**: Font Awesome
- **세션 관리**: Flask-Session
- **파일 처리**: Werkzeug

## 프로젝트 구조

### 디렉토리 구조
```
cafe_management/
├── app.py                 # 메인 Flask 애플리케이션
├── models.py              # 데이터베이스 모델
├── config.py              # 설정 파일
├── cafe.db                # SQLite 데이터베이스
├── static/
│   ├── css/               # CSS 파일들
│   ├── js/                # JavaScript 파일들
│   ├── images/            # 기본 이미지들
│   └── uploads/           # 업로드된 메뉴 이미지들
├── templates/
│   ├── base.html          # 기본 템플릿
│   ├── index.html         # 메인 페이지
│   ├── user/              # 사용자 페이지들
│   │   ├── menu.html      # 메뉴 주문 페이지
│   │   └── cart.html      # 장바구니 페이지
│   └── admin/             # 관리자 페이지들
│       ├── login.html     # 관리자 로그인
│       ├── sales.html     # 매출 관리
│       ├── menu.html      # 메뉴 관리
│       ├── add_menu.html  # 메뉴 추가
│       ├── edit_menu.html # 메뉴 수정
│       ├── categories.html # 카테고리 관리
│       ├── import_orders.html # 주문 데이터 가져오기
│       ├── order_list.html # 주문 목록
│       ├── receipt.html   # 영수증 출력
│       └── receipt_small.html # 작은 영수증
└── flask_session/         # 세션 파일 저장소
```

## 데이터베이스 모델

### Menu (메뉴) 테이블
```python
class Menu(db.Model):
    __tablename__ = 'cafe_menu'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))
    temperature_option = db.Column(db.String(20), default='both')
    display_order = db.Column(db.Integer, default=9999)
    is_soldout = db.Column(db.Boolean, default=False)
```

### Order (주문) 테이블
```python
class Order(db.Model):
    __tablename__ = 'cafe_order'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    status = db.Column(db.String(20), nullable=False)
    total_amount = db.Column(db.Integer, nullable=False)
    customer_name = db.Column(db.String(50), nullable=False)
    delivery_location = db.Column(db.String(100), nullable=False)
    delivery_time = db.Column(db.String(50), nullable=True)
    order_request = db.Column(db.Text, nullable=True)
```

### OrderItem (주문항목) 테이블
```python
class OrderItem(db.Model):
    __tablename__ = 'cafe_order_item'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('cafe_order.id'), nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('cafe_menu.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    special_request = db.Column(db.Text)
    temperature = db.Column(db.String(10), default='ice')
```

## 주요 기능

### 1. 사용자 기능
- **메뉴 조회**: 카테고리별 메뉴 목록, 품절 상태 표시
- **장바구니 관리**: 메뉴 추가/수정/삭제, 수량 조정, 특별 요청사항
- **주문하기**: 고객 정보 입력, 배달 정보, 주문 완료

### 2. 관리자 기능
- **인증**: 관리자 로그인/로그아웃
- **매출 관리**: 일/주/월 매출 통계, 주문 목록 조회
- **메뉴 관리**: 메뉴 추가/수정/삭제, 이미지 업로드, 품절 상태 관리
- **카테고리 관리**: 카테고리 추가/삭제
- **데이터 관리**: Excel 파일 가져오기/내보내기
- **영수증 출력**: 주문 영수증 생성

## 라우트 구조

### 메인 라우트
- `GET /` - 메인 페이지 (사용자/관리자 선택)
- `GET /init_db` - 데이터베이스 초기화
- `GET /update_db_schema` - 데이터베이스 스키마 업데이트

### 사용자 라우트
- `GET /user/menu` - 메뉴 조회
- `POST /user/add_to_cart` - 장바구니에 추가
- `GET /user/view_cart` - 장바구니 조회
- `POST /user/update_cart` - 장바구니 수정
- `POST /user/place_order` - 주문하기
- `POST /user/clear_cart` - 장바구니 비우기

### 관리자 라우트
- `GET /admin/login` - 관리자 로그인 페이지
- `POST /admin/login` - 관리자 로그인 처리
- `GET /admin/logout` - 관리자 로그아웃
- `GET /admin` - 관리자 대시보드
- `GET /admin/sales` - 매출 관리
- `POST /admin/sales/filter` - 매출 필터링
- `GET /admin/export_all_orders` - 전체 주문 내역 내보내기
- `POST /admin/export_period_orders` - 기간별 주문 내역 내보내기
- `GET /admin/menu` - 메뉴 관리
- `GET /admin/menu/add` - 메뉴 추가 페이지
- `POST /admin/menu/add` - 메뉴 추가 처리
- `GET /admin/menu/edit/<id>` - 메뉴 수정 페이지
- `POST /admin/menu/edit/<id>` - 메뉴 수정 처리
- `GET /admin/menu/delete/<id>` - 메뉴 삭제
- `POST /admin/menu/toggle_soldout/<id>` - 품절 상태 토글
- `POST /admin/menu/update_order` - 메뉴 순서 변경
- `GET /admin/categories` - 카테고리 관리
- `POST /admin/categories` - 카테고리 추가
- `POST /admin/categories/delete/<category>` - 카테고리 삭제
- `GET /admin/import_orders` - 주문 데이터 가져오기 페이지
- `POST /admin/import_orders` - 주문 데이터 가져오기 처리
- `GET /admin/print_receipt/<id>` - 영수증 출력
- `GET /admin/get_recent_orders` - 최근 주문 조회 (AJAX)
- `POST /admin/update_order_status/<id>` - 주문 상태 업데이트 (AJAX)
- `POST /admin/delete_order/<id>` - 주문 삭제 (AJAX)

## 템플릿 구조

### 기본 템플릿 (base.html)
- Bootstrap 5 CSS/JS 포함
- Font Awesome 아이콘
- 반응형 네비게이션 바
- 사이드바 스타일 (관리자용)
- 세션 기반 장바구니 표시

### 사용자 템플릿
- **menu.html**: 카테고리별 메뉴 표시, 장바구니 추가 기능
- **cart.html**: 장바구니 관리, 주문 완료 기능

### 관리자 템플릿
- **login.html**: 관리자 로그인 폼
- **sales.html**: 매출 대시보드, 통계 표시
- **menu.html**: 메뉴 목록, CRUD 기능
- **add_menu.html**: 메뉴 추가 폼
- **edit_menu.html**: 메뉴 수정 폼
- **categories.html**: 카테고리 관리
- **import_orders.html**: Excel 파일 업로드
- **order_list.html**: 주문 목록 표시
- **receipt.html**: 영수증 출력
- **receipt_small.html**: 작은 영수증 출력

## 설정 파일 (config.py)
```python
# 데이터베이스 설정
SQLALCHEMY_DATABASE_URI = 'sqlite:///cafe.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 파일 업로드 설정
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# 세션 설정
PERMANENT_SESSION_LIFETIME = timedelta(days=1)
SESSION_TYPE = 'filesystem'
```

## 주요 기능 구현 요구사항

### 1. 세션 관리
- Flask-Session을 사용한 세션 관리
- 장바구니 데이터 세션 저장
- 관리자 로그인 상태 유지

### 2. 파일 업로드
- 메뉴 이미지 업로드 기능
- 안전한 파일명 처리 (secure_filename)
- 파일 형식 및 크기 검증

### 3. 데이터베이스 관리
- SQLAlchemy ORM 사용
- 관계 설정 (Order-OrderItem, Menu-OrderItem)
- 트랜잭션 처리 및 오류 핸들링

### 4. AJAX 기능
- 장바구니 실시간 업데이트
- 주문 상태 변경
- 메뉴 순서 변경

### 5. Excel 파일 처리
- pandas를 사용한 Excel 파일 읽기/쓰기
- 주문 데이터 가져오기/내보내기
- 데이터 검증 및 오류 처리

### 6. 반응형 디자인
- Bootstrap 5 그리드 시스템
- 모바일 친화적 UI
- 사이드바 반응형 처리

## 개발 시 주의사항

### 1. 보안
- 관리자 인증 필수
- 파일 업로드 보안 처리
- SQL 인젝션 방지
- XSS 방지

### 2. 성능
- 데이터베이스 쿼리 최적화
- 이미지 파일 크기 제한
- 세션 데이터 관리

### 3. 사용자 경험
- 직관적인 UI/UX
- 실시간 피드백
- 오류 메시지 명확화
- 로딩 상태 표시

### 4. 데이터 무결성
- 외래키 제약 조건
- 트랜잭션 처리
- 데이터 검증

## 배포 고려사항
- 프로덕션 환경 설정
- 로그 관리
- 백업 전략
- 보안 강화
- 성능 모니터링

