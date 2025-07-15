from fastapi import FastAPI, HTTPException, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from queries import (
    items_search_via_name,
    items_search_via_mod,
    get_servers,
    add_server,
    add_item,
    get_recipe,
    get_item_price,
    add_recipe,
)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="templates/static"), name="static")


@app.get('/')
def main():
    return FileResponse(path="templates/main.html", status_code=200)

@app.get('/search/')
def search(field: str, text: str, server_id: int = None):
    if server_id is None:
        return []
    if field == "name":
        return items_search_via_name(text, server_id)
    elif field == "mod":
        return items_search_via_mod(text, server_id)
    
    else: 
        raise HTTPException(status_code=404, detail="Filter field not found")

@app.get('/servers/')
def get_all_servers():
    return get_servers()

@app.post('/servers/')
def create_server(name: str = Form(...)):
    add_server(name)
    return JSONResponse(content={"status": "success"})

@app.post('/items/')
def create_item(
    name: str = Form(...),
    is_mods: str = Form(...),
    price: float = Form(...),
    server_id: int = Form(...)
):
    add_item(name, is_mods, price, server_id)
    return JSONResponse(content={"status": "success"})

@app.post('/calculate/')
def calculate_cost(
    items: list = Body(...),
    server_id: int = Body(...),
    craft_type: str = Body(...)
):
    total_cost = 0
    for item in items:
        total_cost += calculate_item_cost(item['id'], item['quantity'], server_id)

    if craft_type == 'percentage':
        total_cost *= 1.05

    return {"total_cost": total_cost}

def calculate_item_cost(item_id, quantity, server_id):
    recipe = get_recipe(item_id, server_id)
    if not recipe:
        return get_item_price(item_id, server_id) * quantity

    total_cost = 0
    for ingredient in recipe:
        total_cost += calculate_item_cost(
            ingredient['ingredient_id'],
            ingredient['quantity'] * quantity,
            server_id
        )
    return total_cost

@app.post('/recipes/')
def create_recipe(
    item_id: int = Body(...),
    server_id: int = Body(...),
    ingredients: list = Body(...)
):
    for ingredient in ingredients:
        add_recipe(item_id, ingredient['ingredient_id'], ingredient['quantity'], server_id)
    return JSONResponse(content={"status": "success"})