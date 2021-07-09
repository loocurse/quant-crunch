import asyncio
import os

import uvicorn
from dotenv import load_dotenv

from app import create_app

load_dotenv()
app = create_app()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=5050,
        loop=loop,
        reload=os.getenv("MODE") == "DEV"
        and os.getenv("RELOAD"),  # doesn't seem to work
    )
    server = uvicorn.Server(config)
    loop.run_until_complete(server.serve())
