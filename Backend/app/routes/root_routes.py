from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {"status": "OK", "message": "RupeeWave API Running"}
