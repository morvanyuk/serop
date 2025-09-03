from pydantic import BaseModel
from typing import Dict
from pydantic import BaseModel, PositiveInt

class ItemCreate(BaseModel):
    name: str
    mod: str
    price: float | None
    graph: str

class ItemUpdate(BaseModel):
    id_element: str
    name: str
    mod: str
    price: PositiveInt | float
    graph: str

class ItemDelete(BaseModel):
    id_element: str
    graph: str


class UserData(BaseModel):
    username: str
    password: str

class GraphModel(BaseModel):
    name: str

class CraftModel(BaseModel):
    key: str
    parents : Dict[str, int]
    plus5 : bool
    graph: str
