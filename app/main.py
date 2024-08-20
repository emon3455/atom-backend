from fastapi import FastAPI
from app.routers import property

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome! The server is running."}

# property
app.include_router(property.router, prefix="/property", tags=["Property"])


# for locally run(we have to remove this before deploy)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
