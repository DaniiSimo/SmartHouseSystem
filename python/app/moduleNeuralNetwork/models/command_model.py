from python.app.base_model import BaseModel
from sqlalchemy import  Column, Integer, String


class CommandModel(BaseModel):
    __tablename__ = "commands"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, unique=True)
    device = Column(String)
    command = Column(String)
    device = Column(String)
    device = Column(String)
