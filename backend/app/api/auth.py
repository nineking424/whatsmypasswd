from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.config import get_settings
from app.schemas.auth import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()
settings = get_settings()


def create_access_token() -> tuple[str, int]:
    """Create JWT access token."""
    expires_delta = timedelta(hours=settings.jwt_expire_hours)
    expire = datetime.now(timezone.utc) + expires_delta

    to_encode = {
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return encoded_jwt, int(expires_delta.total_seconds())


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> bool:
    """Verify JWT token from Authorization header."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        return True
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login with master password."""
    if request.password != settings.master_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )

    token, expires_in = create_access_token()

    return LoginResponse(
        access_token=token,
        expires_in=expires_in,
    )


@router.post("/verify")
async def verify(authenticated: bool = Depends(verify_token)):
    """Verify current token is valid."""
    return {"valid": True}
