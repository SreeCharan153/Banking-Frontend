from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.middleware import attach_supabase_middleware
from app.core.security import refresh_cookie_middleware
from app.routes.auth_routes import router as auth_router
from app.routes.account_routes import router as account_router
from app.routes.transaction_routes import router as transaction_router
from app.routes.update_routes import router as update_router
from app.routes.history_routes import router as history_router
from app.routes.debug_routes import router as debug_router
from app.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title="RupeeWave API", version="3.0")

    # -------------------- CORS --------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "https://rupeewave.vercel.app",
            "https://rupeewave.onrender.com",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---------------- Middlewares ----------------
    app.middleware("http")(attach_supabase_middleware)
    app.middleware("http")(refresh_cookie_middleware)

    # ------------------- Routers -------------------
    app.include_router(auth_router, prefix="/auth", tags=["Auth"])
    app.include_router(account_router, prefix="/account", tags=["Account"])
    app.include_router(transaction_router, prefix="/transaction", tags=["Transaction"])
    app.include_router(update_router, prefix="/update", tags=["Update"])
    app.include_router(history_router, prefix="/history", tags=["History"])
    app.include_router(debug_router, prefix="/debug", tags=["Debug"])

    return app
