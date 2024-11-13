from fastapi import FastAPI
from app.python_module1.routers import endpoints as module1_endpoints

app = FastAPI()

# Подключение маршрутов модулей
app.include_router(module1_endpoints.router, prefix="/module1")

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}