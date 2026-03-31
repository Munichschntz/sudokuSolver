from pathlib import Path
import logging

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User
from crud import (
    get_user_by_username,
    create_user,
    verify_password,
    create_game_state,
    get_game_states,
    get_game_state,
    get_user,
)
from schemas import UserCreate, UserOut, GameStateCreate, GameStateOut, SolveRequest, SolveResponse
from solver import GRID_SIZE, generate_puzzle as generate_sudoku_puzzle, grid_to_json, solve
from ui_config import get_ui_config

DATABASE_URL = "sqlite:///./sudoku.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sudoku Solver Web App")

PROJECT_ROOT = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "webapp" / "templates"))
app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "webapp" / "static")), name="static")

logger = logging.getLogger("sudoku.app")
logger.setLevel(logging.INFO)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log request status and full stack traces for unhandled errors."""
    try:
        response = await call_next(request)
        logger.info("%s %s -> %s", request.method, request.url.path, response.status_code)
        return response
    except Exception:
        logger.exception("Unhandled error while processing %s %s", request.method, request.url.path)
        raise

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Simple token storage in memory for demo.
tokens: dict[str, int] = {}  # token -> user_id

@app.post("/register", response_model=UserOut)
async def register(user_in: UserCreate, db: SessionLocal = Depends(get_db)):
    if get_user_by_username(db, user_in.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    user = create_user(db, user_in)
    return UserOut(id=user.id, username=user.username)

@app.post("/token", response_model=dict[str, str])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: SessionLocal = Depends(get_db)):
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(user, form_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Generate simple token using UUID
    import uuid
    token = str(uuid.uuid4())
    tokens[token] = user.id
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme), db: SessionLocal = Depends(get_db)):
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = tokens[token]
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "ui_config": get_ui_config(),
            "grid_size": GRID_SIZE,
        },
    )

@app.post("/save_game", response_model=GameStateOut)
async def save_game(game_in: GameStateCreate, current_user: User = Depends(get_current_user), db: SessionLocal = Depends(get_db)):
    state = create_game_state(db, current_user.id, game_in)
    return GameStateOut(
        id=state.id,
        grid=state.grid,
        cell_colors=state.cell_colors,
        solved=state.solved,
        timestamp=state.timestamp
    )

@app.get("/games", response_model=list[GameStateOut])
async def list_games(current_user: User = Depends(get_current_user), db: SessionLocal = Depends(get_db)):
    states = get_game_states(db, current_user.id)
    return [
        GameStateOut(
            id=s.id,
            grid=s.grid,
            cell_colors=s.cell_colors,
            solved=s.solved,
            timestamp=s.timestamp
        )
        for s in states
    ]

@app.get("/games/{game_id}", response_model=GameStateOut)
async def get_game(game_id: int, current_user: User = Depends(get_current_user), db: SessionLocal = Depends(get_db)):
    state = get_game_state(db, game_id)
    if not state or state.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Game not found")
    return GameStateOut(
        id=state.id,
        grid=state.grid,
        cell_colors=state.cell_colors,
        solved=state.solved,
        timestamp=state.timestamp
    )

# Optional: endpoint to generate puzzle
@app.get("/generate_puzzle", response_model=dict[str, List[List[int]]])
async def generate_puzzle(difficulty: str = "Easy"):
    puzzle = generate_sudoku_puzzle(difficulty)
    return {"puzzle": puzzle}

# Public endpoint by design to support anonymous puzzle solving.
@app.post("/solve", response_model=SolveResponse)
async def solve_puzzle(puzzle: SolveRequest):
    """
    Solves the Sudoku puzzle provided in the request. The puzzle must be a 9x9 grid.
    Returns the solved grid if possible; otherwise raises an HTTPException.
    """
    # Deep copy to avoid mutating input
    original_grid = [row[:] for row in puzzle.grid]
    grid_copy = [row[:] for row in puzzle.grid]
    try:
        solved_grid = solve(grid_copy)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Puzzle could not be solved: {e}")

    user_entered = [[original_grid[r][c] != 0 for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]
    return grid_to_json(solved_grid, user_entered)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)