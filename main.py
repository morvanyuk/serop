import uvicorn
from fastapi import FastAPI, Body, Depends, HTTPException, Response, Request, status
from datetime import timedelta
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
from starlette.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from schemas import *

from graph import *

from utils import verify_password, verify_user, create_token

from queries import get_user, update_item

import environ

env = environ.Env()
environ.Env.read_env()

app = FastAPI()


templates = Jinja2Templates(directory="templates")

# Auth

class TokenRefreshMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not request.url == '/': 
            access_token = request.cookies.get("access_token")
            refresh_token = request.cookies.get("refresh_token")

            new_access_token = None

            if access_token:
                if verify_user(access_token) == 401:
                    user = verify_user(refresh_token)
                    if type(user) == dict:
                        new_access_token = create_token(data={"username": user['username'], "password" : user['password']},
                                        expires_delta=timedelta(minutes=float(env('ACCESS_TOKEN_EXPIRE_MINUTES'))))
                        new_refresh_token = create_token(data={"username": user['username'], "password" : user['password'], "type" : "refresh"}, 
                                        expires_delta=timedelta(minutes=float(env('REFRESH_TOKEN_EXPIRE_MINUTES'))))
                        
            response: Response = await call_next(request)

            if new_access_token:
                response.set_cookie("access_token", new_access_token, httponly=True)
                response.set_cookie("refresh_token", new_refresh_token, httponly=True)

        return response

    


app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TokenRefreshMiddleware)

app.mount("/static", StaticFiles(directory="templates/static"), name="static")

def auth_for_apis(request: Request, response : Response):
    token = request.cookies.get("refresh_token")

    if not token or verify_user(token) == 401:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
def auth_for_page(request):
    token = request.cookies.get("access_token")
    token2 = request.cookies.get("refresh_token")

    if not token:
        return status.HTTP_401_UNAUTHORIZED
    
    if verify_user(token2) == 401:
        return status.HTTP_401_UNAUTHORIZED
    

@app.post('/login')
def login(data: UserData, response : Response, status_code=200):
    user = get_user(data.username)
    if user and verify_password(plain_password=data.password, hashed_password=user[0][1]):
        access_token = create_token(data={"username": data.username, "password" : user[0][1]},
                                     expires_delta=timedelta(minutes=float(env('ACCESS_TOKEN_EXPIRE_MINUTES'))))
        refresh_token = create_token(data={"username": data.username, "password" : user[0][1], "type" : "refresh"}, 
                                     expires_delta=timedelta(minutes=float(env('REFRESH_TOKEN_EXPIRE_MINUTES'))))
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

        return 200

    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get('/')
def main(request: Request, status_code=200):
    if auth_for_page(request) is not None:
        return FileResponse(path="templates/login.html")
    
    return templates.TemplateResponse(
        request=request, name="menu.html"
    )

@app.get('/get-all-graphs')
def get_all_graphs():
    return all_graphs()

@app.get('/crud/{name}')
def get_graph(request: Request):
    if auth_for_page(request) is not None:
        return FileResponse(path="templates/login.html")
    return templates.TemplateResponse(
        request=request, name="nodes.html"
    )

@app.post('/create-graph/')
def create_new_graph(graph: GraphModel = Body(), user: dict = Depends(auth_for_apis)):
    if isinstance(user, RedirectResponse):
        return user
    create_graph(graph.name)
    return status.HTTP_201_CREATED

@app.get('/search/')
def search(field: str = 'name' or 'mod', text: str = None, graph_name: str = None , user: dict = Depends(auth_for_apis)):
    if isinstance(user, RedirectResponse):
        return user
    return get_all_nodes_from_graph(graph_name=graph_name, field=field, text=text)
    
    
@app.get('/nodes/{name}')
def get_graph_nodes(name, user: dict = Depends(auth_for_apis)):
    if isinstance(user, RedirectResponse):
        return user
    return get_all_nodes_from_graph(name)
    
@app.post('/nodes/update/')
def update(node: ItemUpdate, user: dict = Depends(auth_for_apis)):
    if isinstance(user, RedirectResponse):
        return user
    update_node(node.model_dump())
    return 200

@app.post('/nodes/create/')
def create(item: ItemCreate, user: dict = Depends(auth_for_apis)):
    if isinstance(user, RedirectResponse):
        return user
    create_node(item.model_dump())
    return status.HTTP_201_CREATED

@app.post("/nodes/delete/")
def delete_item(item: ItemDelete, user: dict = Depends(auth_for_apis)):
    if isinstance(user, RedirectResponse):
        return user
    delete_node(item.model_dump())
    return status.HTTP_204_NO_CONTENT

@app.get('/craft/{graph}/', status_code=200)
def craftItem(graph: str, request: Request):
    if auth_for_page(request) is not None:
        return FileResponse(path="templates/login.html")
    return templates.TemplateResponse(
        request=request, name="main.html"
    )

@app.post('/craft/', status_code=200)
def craftItem(data: CraftModel):
    craft(data.model_dump())



if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info")