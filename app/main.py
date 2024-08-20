from fastapi import FastAPI
from app.routers import property

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome! The server is running."}

# property
app.include_router(property.router, prefix="/property", tags=["Property"])


