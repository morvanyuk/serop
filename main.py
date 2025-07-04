import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Response, Request, status
from datetime import timedelta
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel, PositiveInt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
from starlette.requests import Request


from utils import verify_password, verify_user, create_token

from queries import get_user, items_search_via_name, items_search_via_mod, update_item

import environ

env = environ.Env()
environ.Env.read_env()

app = FastAPI()

class TokenRefreshMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
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

class Update_element(BaseModel):
    id_element: PositiveInt
    price: PositiveInt | float

class UserData(BaseModel):
    username: str
    password: str

def auth_for_apis(request: Request, response : Response):
    token = request.cookies.get("refresh_token")

    if not token or verify_user(token) == 401:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    

@app.post('/login')
def main(data: UserData, response : Response, status_code=200):
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
def main(request: Request, response : Response, status_code=200):
    token = request.cookies.get("access_token")
    token2 = request.cookies.get("refresh_token")

    if not token:
        return FileResponse(path="templates/login.html")
    
    if verify_user(token2) == 401:
        return FileResponse(path="templates/login.html")
    
    return FileResponse(path="templates/main.html")

@app.get('/search/')
def search(field: str = 'name' or 'mod', text: str = None, user: dict = Depends(auth_for_apis)):
    if isinstance(user, RedirectResponse):
        return user
    if field == "name":
        return items_search_via_name(text)
    elif field == "mod":
        return items_search_via_mod(text)
    
    else: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Filter field not found")
    
@app.post('/update/')
def update(item: Update_element, user: dict = Depends(auth_for_apis)):
    if isinstance(user, RedirectResponse):
        return user
    update_item(item)
    return 200

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info")