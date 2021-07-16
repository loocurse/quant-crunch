from fastapi import FastAPI
from redis import Redis

from routers import api_router
from services import (
    get_tickers_metadata,
    init_db,
    init_polygon,
    init_socket,
    init_watcher,
)


def create_app():
    app = FastAPI()
    app.include_router(api_router, prefix="/api")

    @app.on_event("startup")
    def startup_event():
        app.redis = Redis()
        app.polygon = init_polygon()
        app.db = init_db()
        app.watcher = init_watcher(app)
        get_tickers_metadata(app)
        app.socket = None
        # app.socket = init_socket()

    @app.on_event("shutdown")
    def shutdown_event():
        # Cleanup if any
        if app.socket:
            app.socket.close_connection()
        app.polygon.close()
        app.watcher.event.set()
        pass

    return app
