from sqlalchemy.orm import Session
from models import User, GameState
from schemas import UserCreate, GameStateCreate
import base64
import hashlib
import hmac
import secrets
from typing import Optional, List

try:
    import bcrypt  # type: ignore
except ImportError:
    bcrypt = None

PBKDF2_PREFIX = "pbkdf2_sha256"
PBKDF2_ROUNDS = 200_000


def _hash_password(password: str) -> str:
    """Hash password with bcrypt when available, otherwise PBKDF2-SHA256."""
    if bcrypt is not None:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ROUNDS)
    salt_b64 = base64.b64encode(salt).decode("ascii")
    digest_b64 = base64.b64encode(digest).decode("ascii")
    return f"{PBKDF2_PREFIX}${PBKDF2_ROUNDS}${salt_b64}${digest_b64}"


def _verify_password(password: str, stored_hash: str) -> bool:
    """Verify bcrypt hashes and PBKDF2 fallback hashes."""
    if stored_hash.startswith(f"{PBKDF2_PREFIX}$"):
        try:
            _prefix, rounds_s, salt_b64, digest_b64 = stored_hash.split("$", 3)
            rounds = int(rounds_s)
            salt = base64.b64decode(salt_b64.encode("ascii"))
            expected = base64.b64decode(digest_b64.encode("ascii"))
            actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, rounds)
            return hmac.compare_digest(actual, expected)
        except (ValueError, TypeError):
            return False

    if bcrypt is None:
        return False

    return bcrypt.checkpw(password.encode(), stored_hash.encode())

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user_in: UserCreate) -> User:
    hashed = _hash_password(user_in.password)
    db_user = User(username=user_in.username, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def verify_password(user: User, password: str) -> bool:
    return _verify_password(password, user.hashed_password)

def create_game_state(db: Session, user_id: int, game_in: GameStateCreate) -> GameState:
    db_state = GameState(
        user_id=user_id,
        grid=game_in.grid,
        cell_colors=game_in.cell_colors,
        solved=game_in.solved
    )
    db.add(db_state)
    db.commit()
    db.refresh(db_state)
    return db_state

def get_game_states(db: Session, user_id: int) -> List[GameState]:
    return db.query(GameState).filter(GameState.user_id == user_id).order_by(GameState.timestamp.desc()).all()

def get_game_state(db: Session, state_id: int) -> Optional[GameState]:
    return db.query(GameState).filter(GameState.id == state_id).first()