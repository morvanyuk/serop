from pydantic import BaseModel
from typing import List, Dict

class Item(BaseModel):
    name: str
    price: float | None
    # childNodes: list

class CraftModel(BaseModel):
    key: int
    parents : Dict[str, int]
    plus_5_percent : bool
