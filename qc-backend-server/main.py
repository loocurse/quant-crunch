import os
from dotenv import load_dotenv
from flask import Flask, request

load_dotenv()


def create_app():
    app = Flask(__name__)

    @app.get("/")
    def index_get():
        return {"hello": "this returns a json object"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=os.getenv("MODE") == "DEVELOPMENT")
