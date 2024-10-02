from python.app.base_model import BaseModel
from sqlalchemy import  Column, Integer, String


class SynonymModel(BaseModel):
    __tablename__ = "synonyms"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, index=True, unique=True)
    value = Column(String)
