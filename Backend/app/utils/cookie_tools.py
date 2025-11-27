from fastapi import Response
from app.config import settings

def set_cookie(response: Response, key: str, value: str, max_age: int):
    response.set_cookie(
        key=key,
        value=value,
        httponly=True,
        samesite="none",
        secure=(settings.ENV == "prod"),
        max_age=max_age,
    )

def clear_cookie(response: Response, key: str):
    response.delete_cookie(
        key=key,
        samesite="none",
        secure=(settings.ENV == "prod")
    )
