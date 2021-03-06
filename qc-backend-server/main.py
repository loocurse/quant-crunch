import os
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

load_dotenv()

from app import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        f"{Path(__file__).stem}:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5050)),
        reload=os.getenv("MODE") == "DEV" and os.getenv("RELOAD"),
        root_path=os.getenv("ROOT_PATH", "/"),
    )
