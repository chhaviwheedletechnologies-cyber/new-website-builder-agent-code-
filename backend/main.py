from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.mount("/output", StaticFiles(directory="output"), name="output")

import os

os.makedirs("output", exist_ok=True)

from routes import router

app = FastAPI(title="AI Website Generator Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")
app.mount("/output", StaticFiles(directory="output"), name="output")

@app.get("/health")
def health_check():
    return {"status": "ok", "agents_active": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001)
