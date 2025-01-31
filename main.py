from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from queries import items_search_via_name, items_search_via_mod


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
def search(field: str = 'name' or 'mod', text: str = None):
    if field == "name":
        return items_search_via_name(text)
    elif field == "mod":
        return items_search_via_mod(text)
    
    else: 
        raise HTTPException(status_code=404, detail="Filter field not found")