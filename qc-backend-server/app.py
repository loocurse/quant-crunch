from fastapi import FastAPI

from routers import api_router
from services import (
    init_db,
    init_polygon,
    init_redis,
    init_redis_data,
    init_socket,
    init_watcher,
)


def create_app():
    app = FastAPI()
    app.include_router(api_router, prefix="/api")

    @app.on_event("startup")
    def startup_event():
        app.redis = init_redis()
        app.polygon = init_polygon()
        app.db = init_db()
        app.watcher = init_watcher(app)
        init_redis_data(app)
        app.socket = init_socket(app)

    @app.on_event("shutdown")
    def shutdown_event():
        # Cleanup if any
        if app.socket:
            app.socket.close_connection()
        app.polygon.close()
        app.watcher.event.set()
        pass

    return app
