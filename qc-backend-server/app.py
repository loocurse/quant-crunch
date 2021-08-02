from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import api_router
from services import (
    init_alpaca,
    init_db,
    init_polygon,
    init_redis,
    init_redis_data,
    init_socket,
    init_watcher,
)


def create_app():
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
    )
    app.include_router(api_router, prefix="/api")

    @app.on_event("startup")
    async def startup_event():
        app.redis = init_redis()
        app.polygon = init_polygon()
        app.db = init_db()
        app.watcher = init_watcher(app)
        # alpaca_stream = alpaca_trade_api.Stream()
        # alpaca_stream.subscribe_trade_updates(trade_updates_callback)
        # task = asyncio.create_task(alpaca_stream._run_forever())
        app.alpaca = init_alpaca(app)
        app.alpaca.run()
        init_redis_data(app)
        app.socket = None
        # app.socket = init_socket(app)

    @app.on_event("shutdown")
    def shutdown_event():
        # Cleanup if any
        if app.socket:
            app.socket.close_connection()
        app.polygon.close()
        app.watcher.event.set()
        pass

    return app
