from pydantic import BaseModel, Field
from typing import List
import datetime

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)

class UserOut(BaseModel):
    id: int
    username: str

class GameStateBase(BaseModel):
    grid: List[List[int]]
    cell_colors: List[List[str]]
    solved: bool

class GameStateCreate(GameStateBase):
    pass

class GameStateOut(GameStateBase):
    id: int
    timestamp: datetime.datetime

# New schema for solving request
class SolveRequest(BaseModel):
    """
    Request payload containing a Sudoku puzzle grid.
    The grid must be a 9x9 list of lists with integers from 0-9,
    where 0 represents an empty cell.
    """
    grid: List[List[int]]


class SolveResponse(BaseModel):
    """Solved grid payload consumed by the web UI."""

    grid: List[List[int]]
    cell_colors: List[List[str]]