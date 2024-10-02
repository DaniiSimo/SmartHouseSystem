from fastapi import FastAPI
#from app.moduleNeuralNetwork.routers import endpoints as moduleNeuralNetwork_endpoints
from sqlalchemy import create_engine

# строка подключения
SQLALCHEMY_DATABASE_URL = "sqlite:///./db.sqlite"

# создаем движок SqlAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# создаем таблицы
#Base.metadata.create_all(bind=engine)

app = FastAPI()

# Подключение маршрутов модулей
#app.include_router(moduleNeuralNetwork.router, prefix="/moduleNeuralNetwork")

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}