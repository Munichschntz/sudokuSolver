from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from crud import (
    get_user_by_username,
    create_user,
    verify_password,
    create_game_state,
    get_game_states,
    get_game_state,
    get_user,  # <-- added import for user lookup
)
from schemas import UserCreate, UserOut, GameStateCreate, GameStateOut, SolveRequest

DATABASE_URL = "sqlite:///./sudoku.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sudoku Solver Web App")

templates = Jinja2Templates(directory="templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Simple token storage in memory for demo
tokens: dict[str, tuple[int, str]] = {}  # token -> (user_id, expiry)

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
    tokens[token] = (user.id, "infinite")  # no expiry for demo
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme), db: SessionLocal = Depends(get_db)):
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id, _ = tokens[token]
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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
    from solver import generate_puzzle
    puzzle = generate_puzzle(difficulty)
    return {"puzzle": puzzle}

# New endpoint to solve a given puzzle
@app.post("/solve", response_model=List[List[int]])
async def solve_puzzle(puzzle: SolveRequest, db: SessionLocal = Depends(get_db)):
    """
    Solves the Sudoku puzzle provided in the request. The puzzle must be a 9x9 grid.
    Returns the solved grid if possible; otherwise raises an HTTPException.
    """
    # Deep copy to avoid mutating input
    grid_copy = [row[:] for row in puzzle.grid]
    try:
        from solver import solve
        solved_grid = solve(grid_copy)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Puzzle could not be solved: {e}")
    return solved_grid

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)