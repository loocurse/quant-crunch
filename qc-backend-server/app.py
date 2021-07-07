from fastapi import FastAPI
from redis import Redis

from database import init_db
from routers import api_router


def create_app():
    app = FastAPI()
    app.include_router(api_router, prefix="/api")

    @app.on_event("startup")
    def startup_event():
        app.redis = Redis()
        # app.db = init_db()

    @app.on_event("shutdown")
    def shutdown_event():
        # Cleanup if any
        pass

    return app
