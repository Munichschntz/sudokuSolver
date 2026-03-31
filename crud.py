from sqlalchemy.orm import Session
from models import User, GameState
from schemas import UserCreate, GameStateCreate
import bcrypt
from typing import Optional, List

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user_in: UserCreate) -> User:
    hashed = bcrypt.hashpw(user_in.password.encode(), bcrypt.gensalt())
    db_user = User(username=user_in.username, hashed_password=hashed.decode())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def verify_password(user: User, password: str) -> bool:
    return bcrypt.checkpw(password.encode(), user.hashed_password.encode())

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