from fastapi import FastAPI
from app.routers import property
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Welcome! The server is running."}

# property
app.include_router(property.router, prefix="/property", tags=["Property"])

