# FastAPI 백엔드 API

클린 아키텍처(Clean Architecture)를 적용한 FastAPI 기반의 백엔드 API입니다.

## 프로젝트 구조

```
app/
├── main.py                      # FastAPI app 실행 엔트리포인트
├── config/
│   └── settings.py              # 환경변수, DB 설정
├── domain/
│   └── user/
│       ├── entities.py          # 도메인 엔티티 (예: User)
│       ├── value_objects.py     # 밸류 오브젝트
│       └── repository.py        # 추상 레포지토리 인터페이스
├── application/
│   └── user/
│       ├── use_cases.py         # 유스케이스 (서비스 레벨)
│       └── dto.py               # DTO (요청/응답 모델)
├── interfaces/
│   ├── api/                     # FastAPI 라우터
│   │   └── v1/
│   │       └── user_router.py   # /api/v1/user 엔드포인트
│   └── discord/                 # 디스코드 봇과 통신하는 어댑터
│       └── webhook_receiver.py
├── infrastructure/
│   ├── db/
│   │   ├── models.py            # ORM 모델
│   │   ├── repositories.py      # 실제 DB 접근 구현
│   │   └── session.py           # DB 세션 관리
│   └── external/
│       └── google_calendar.py   # 구글 API 구현체
└── shared/
    ├── utils.py
    └── exceptions.py
```

## 기능

- 사용자 관리 (CRUD)
- 디스코드 웹훅 수신
- 구글 캘린더 연동
- 클린 아키텍처 적용
- 비동기 처리
- 데이터 검증
- 예외 처리

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env.example` 파일을 `.env`로 복사하고 필요한 값들을 설정하세요.

```bash
cp .env.example .env
```

### 3. 데이터베이스 초기화

```bash
cd app
python -c "import asyncio; from infrastructure.db.session import init_db; asyncio.run(init_db())"
```

### 4. 애플리케이션 실행

```bash
cd app
python main.py
```

또는

```bash
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API 문서

애플리케이션이 실행된 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 엔드포인트

### 사용자 관리

- `POST /api/v1/users` - 사용자 생성
- `GET /api/v1/users` - 사용자 목록 조회
- `GET /api/v1/users/{user_id}` - 사용자 조회
- `GET /api/v1/users/username/{username}` - 사용자명으로 조회
- `PUT /api/v1/users/{user_id}` - 사용자 정보 수정
- `DELETE /api/v1/users/{user_id}` - 사용자 삭제
- `PATCH /api/v1/users/{user_id}/activate` - 사용자 활성화
- `PATCH /api/v1/users/{user_id}/deactivate` - 사용자 비활성화

### 디스코드 웹훅

- `POST /discord/webhook` - 디스코드 웹훅 수신
- `GET /discord/webhook/health` - 웹훅 상태 확인

### 기타

- `GET /` - 애플리케이션 상태 확인
- `GET /health` - 헬스 체크

## 아키텍처

이 프로젝트는 클린 아키텍처를 따라 구성되었습니다:

1. **Domain Layer**: 비즈니스 로직과 규칙을 포함하는 핵심 레이어
2. **Application Layer**: 애플리케이션 서비스와 유스케이스
3. **Interface Layer**: 외부 세계와의 인터페이스 (API, 웹훅 등)
4. **Infrastructure Layer**: 데이터베이스, 외부 API 등의 구현체

## 개발

### 코드 포맷팅

```bash
black app/
isort app/
```

### 타입 체크

```bash
mypy app/
```

### 테스트

```bash
pytest
```

## 환경변수

- `APP_NAME`: 애플리케이션 이름
- `DEBUG`: 디버그 모드 (true/false)
- `DATABASE_URL`: 데이터베이스 연결 URL
- `SECRET_KEY`: JWT 서명용 비밀키
- `GOOGLE_CALENDAR_API_KEY`: 구글 캘린더 API 키
- `DISCORD_WEBHOOK_URL`: 디스코드 웹훅 URL

## 라이센스

MIT License