from fastapi import APIRouter

router = APIRouter()

@router.post("/generate")
def generate(data: dict):
    return {"status": "ok", "tokens": []}

@router.post("/infill")
def infill(data: dict):
    return {"status": "ok"}