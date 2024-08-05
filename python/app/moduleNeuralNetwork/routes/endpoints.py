from fastapi import APIRouter

router = APIRouter()

@router.get("/predict")
def predict():
    return {"message": "Module 1 prediction"}
