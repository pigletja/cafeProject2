# 카페 주문 관리 시스템

Flask 기반의 카페 주문 관리 시스템입니다. 사용자 주문과 관리자 메뉴 관리 기능을 제공하는 웹 애플리케이션입니다.

## 🚀 주요 기능

### 사용자 기능
- 📋 **메뉴 조회**: 카테고리별 메뉴 목록, 품절 상태 표시
- 🛒 **장바구니 관리**: 메뉴 추가/수정/삭제, 수량 조정, 특별 요청사항
- 📦 **주문하기**: 고객 정보 입력, 배달 정보, 주문 완료

### 관리자 기능
- 🔐 **인증**: 관리자 로그인/로그아웃
- 📊 **매출 관리**: 일/주/월 매출 통계, 주문 목록 조회
- 🍽️ **메뉴 관리**: 메뉴 추가/수정/삭제, 이미지 업로드, 품절 상태 관리
- 🏷️ **카테고리 관리**: 카테고리 추가/삭제
- 📁 **데이터 관리**: Excel 파일 가져오기/내보내기
- 🧾 **영수증 출력**: 주문 영수증 생성

## 🛠️ 기술 스택

- **백엔드**: Flask (Python)
- **데이터베이스**: SQLite (SQLAlchemy ORM)
- **프론트엔드**: Bootstrap 5, HTML5, CSS3, JavaScript
- **아이콘**: Font Awesome
- **세션 관리**: Flask-Session
- **파일 처리**: Werkzeug

## 📁 프로젝트 구조

```
cafe_management/
├── app.py                 # 메인 Flask 애플리케이션
├── models.py              # 데이터베이스 모델
├── config.py              # 설정 파일
├── requirements.txt       # Python 패키지 의존성
├── README.md              # 프로젝트 문서
├── cafe.db                # SQLite 데이터베이스 (실행 후 생성)
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
│       ├── receipt.html   # 영수증 출력
│       └── receipt_small.html # 작은 영수증
└── flask_session/         # 세션 파일 저장소 (실행 후 생성)
```

## 🔧 설치 및 실행

### 1. 필수 요구사항
- Python 3.7 이상
- pip (Python 패키지 관리자)

### 2. 프로젝트 클론 및 이동
```bash
cd cafe_management
```

### 3. 가상환경 생성 및 활성화 (권장)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. 패키지 설치
```bash
pip install -r requirements.txt
```

### 5. 데이터베이스 초기화
```bash
python app.py
```
또는 웹 브라우저에서 `http://localhost:5000/init_db` 접속

### 6. 애플리케이션 실행
```bash
python app.py
```

웹 브라우저에서 `http://localhost:5000` 접속

## 👤 기본 관리자 계정

- **아이디**: admin
- **비밀번호**: admin123

> ⚠️ **보안 주의사항**: 프로덕션 환경에서는 반드시 기본 비밀번호를 변경하세요!

## 📝 사용 방법

### 사용자 (고객)
1. 메인 페이지에서 "메뉴 보기 & 주문하기" 클릭
2. 카테고리별로 메뉴 확인
3. 원하는 메뉴를 장바구니에 추가
4. 장바구니에서 주문 정보 입력 후 주문 완료

### 관리자
1. 메인 페이지에서 "관리자 로그인" 클릭
2. 관리자 계정으로 로그인
3. 사이드바 메뉴를 통해 각종 관리 기능 이용
   - 대시보드: 매출 현황 및 최근 주문 확인
   - 메뉴 관리: 메뉴 추가/수정/삭제
   - 카테고리 관리: 메뉴 카테고리 관리
   - 데이터 가져오기: Excel 파일로 주문 데이터 가져오기

## 🔧 설정 변경

### 관리자 계정 변경
`config.py` 파일에서 다음 설정을 변경:
```python
ADMIN_USERNAME = '새로운_아이디'
ADMIN_PASSWORD = '새로운_비밀번호'
```

### 파일 업로드 설정
```python
UPLOAD_FOLDER = 'static/uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

### 데이터베이스 설정
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///cafe.db'
```

## 📊 데이터베이스 스키마

### Menu (메뉴) 테이블
- id: 메뉴 ID
- name: 메뉴명
- category: 카테고리
- price: 가격
- description: 설명
- image: 이미지 파일명
- temperature_option: 온도 옵션 (hot/ice/both/none)
- display_order: 표시 순서
- is_soldout: 품절 여부

### Order (주문) 테이블
- id: 주문 ID
- order_date: 주문일시
- status: 주문 상태 (pending/preparing/completed/cancelled)
- total_amount: 총 금액
- customer_name: 고객명
- delivery_location: 배달 위치
- delivery_time: 배달 시간
- order_request: 주문 요청사항

### OrderItem (주문항목) 테이블
- id: 주문항목 ID
- order_id: 주문 ID (외래키)
- menu_id: 메뉴 ID (외래키)
- quantity: 수량
- subtotal: 소계
- special_request: 특별 요청사항
- temperature: 온도 (hot/ice)

## 🚀 배포

### 프로덕션 환경 설정
1. `config.py`에서 SECRET_KEY 변경
2. 관리자 계정 정보 변경
3. DEBUG 모드 비활성화
4. HTTPS 설정 권장
5. 정기 백업 설정

### 환경 변수 설정 예시
```bash
export SECRET_KEY="your-secret-key-here"
export ADMIN_USERNAME="your-admin-username"
export ADMIN_PASSWORD="your-secure-password"
export DATABASE_URL="sqlite:///production.db"
```

## 🐛 문제 해결

### 자주 발생하는 문제

1. **데이터베이스 오류**
   ```bash
   # 데이터베이스 재초기화
   rm cafe.db
   python app.py
   # 브라우저에서 /init_db 접속
   ```

2. **패키지 설치 오류**
   ```bash
   # 가상환경 재생성
   rm -rf venv
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. **파일 업로드 오류**
   - uploads 폴더 권한 확인
   - 파일 크기 제한 확인 (기본 16MB)

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 제공됩니다.

## 🤝 기여

프로젝트 개선을 위한 기여를 환영합니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 등록해 주세요.

**즐거운 카페 운영되세요! ☕️** 