# WhatsmyPasswd

안전한 자격 증명 관리 시스템입니다. 서버 접속 정보, 데이터베이스 계정, FTP/S3 자격 증명 등을 암호화하여 안전하게 저장하고 관리할 수 있습니다.

## 주요 기능

- **자격 증명 관리**: Oracle DB, Linux Server, FTP, S3 등 다양한 유형의 자격 증명 저장
- **AES-256 암호화**: 민감한 정보(호스트, 사용자명, 비밀번호)는 AES-256으로 암호화
- **카테고리 분류**: 자격 증명을 카테고리별로 구분하여 관리
- **태그 시스템**: 유연한 태그 기반 검색 및 필터링
- **감사 로그**: 모든 조회/복사/수정/삭제 작업 기록
- **데이터 내보내기**: JSON/CSV 형식으로 자격 증명 내보내기
- **마스터 비밀번호**: 단일 마스터 비밀번호로 접근 제어

## 기술 스택

### Backend
- **Framework**: FastAPI
- **Database**: SQLite (aiosqlite)
- **ORM**: SQLAlchemy 2.0 (async)
- **인증**: JWT 기반 인증
- **암호화**: AES-256 (cryptography)

### Frontend
- **Framework**: Vue 3 (Composition API)
- **빌드 도구**: Vite
- **상태 관리**: Pinia
- **스타일링**: Tailwind CSS v4
- **라우팅**: Vue Router
- **HTTP 클라이언트**: Axios

### 인프라
- **컨테이너**: Docker
- **오케스트레이션**: Kubernetes
- **웹서버**: Nginx (Frontend)
- **리버스 프록시**: Nginx Ingress

## 빠른 시작

### Docker Compose (로컬 개발)

```bash
# 저장소 클론
git clone https://github.com/nineking424/whatsmypasswd.git
cd whatsmypasswd

# Docker Compose로 실행
docker-compose up -d

# 접속
# Frontend: http://localhost
# Backend API: http://localhost:8000
# 기본 비밀번호: admin123
```

### Kubernetes 배포

```bash
# 네임스페이스 및 리소스 생성
kubectl apply -f k8s/

# 배포 상태 확인
kubectl -n whatsmypasswd get pods

# 시크릿 설정 (필수)
kubectl -n whatsmypasswd create secret generic whatsmypasswd-secret \
  --from-literal=MASTER_PASSWORD=your-master-password \
  --from-literal=SECRET_KEY=your-secret-key-min-32-chars \
  --from-literal=ENCRYPTION_KEY=your-encryption-key-32-chars
```

## 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `MASTER_PASSWORD` | 로그인 마스터 비밀번호 | `admin123` |
| `SECRET_KEY` | JWT 서명용 비밀키 (32자 이상) | - |
| `ENCRYPTION_KEY` | AES-256 암호화 키 (32자) | - |
| `DATABASE_URL` | 데이터베이스 연결 URL | `sqlite+aiosqlite:///./data/whatsmypasswd.db` |
| `CORS_ORIGINS` | 허용할 CORS 출처 | `["http://localhost:5173"]` |
| `DEBUG` | 디버그 모드 | `false` |

## API 엔드포인트

### 인증
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/auth/login` | 로그인 (마스터 비밀번호) |
| POST | `/api/auth/verify` | 토큰 검증 |

### 자격 증명
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/credentials` | 목록 조회 (페이징, 필터) |
| GET | `/api/credentials/{id}` | 상세 조회 |
| POST | `/api/credentials` | 생성 |
| PUT | `/api/credentials/{id}` | 수정 |
| DELETE | `/api/credentials/{id}` | 삭제 |
| POST | `/api/credentials/{id}/copy` | 복사 로그 기록 |

### 카테고리
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/categories` | 목록 조회 |
| POST | `/api/categories` | 생성 |
| PUT | `/api/categories/{id}` | 수정 |
| DELETE | `/api/categories/{id}` | 삭제 |

### 감사 로그
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/audit-logs` | 로그 조회 (필터링) |

### 내보내기
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/export/json` | JSON 형식 내보내기 |
| GET | `/api/export/csv` | CSV 형식 내보내기 |

### 헬스체크
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/health` | 서버 상태 확인 |

## 개발 가이드

### Backend 개발

```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
export MASTER_PASSWORD=admin123
export SECRET_KEY=your-secret-key-min-32-chars-long
export ENCRYPTION_KEY=your-encryption-key-min-32-chars

# 개발 서버 실행
uvicorn app.main:app --reload --port 8000
```

### Frontend 개발

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 프로덕션 빌드
npm run build
```

## 자격 증명 유형

### Oracle DB
- Host, Port (기본: 1521)
- Username, Password
- Service Name, TNS Entry

### Linux Server
- Host, Port (기본: 22)
- Username, Password

### FTP
- Host, Port (기본: 21)
- Username, Password

### S3
- Endpoint, Region
- Access Key, Secret Key
- Bucket

## 보안 고려사항

- 모든 민감한 필드는 AES-256으로 암호화되어 저장됩니다
- 마스터 비밀번호는 서버에서 검증되며 저장되지 않습니다
- JWT 토큰은 24시간 후 만료됩니다
- 모든 CRUD 작업은 감사 로그에 기록됩니다
- HTTPS 사용을 강력히 권장합니다

## Docker 이미지

```bash
# Backend
docker pull nineking424/whatsmypassword:backend

# Frontend
docker pull nineking424/whatsmypassword:frontend
```

## 라이선스

MIT License