import uuid

from fastapi import APIRouter

from app.schemas.auth import AuthRequest, AuthResponse

router = APIRouter(prefix="/auth", tags=["auth"])

# Stub account store: username -> account_id
_accounts: dict[str, str] = {}


@router.post("/login", response_model=AuthResponse)
async def authenticate(req: AuthRequest):
    """Stub authentication. Creates account on first login."""
    if req.username not in _accounts:
        _accounts[req.username] = str(uuid.uuid4())
    return AuthResponse(
        session_token=str(uuid.uuid4()),
        account_id=_accounts[req.username],
    )
