import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
from server import app as api_app

app = FastAPI()

# Mount the API app
app.mount("/api", api_app)

# Serve the index.html file
@app.get("/")
def read_index():
    return FileResponse('index.html')

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
