import os

from flask import Flask

app = Flask(__name__)

COSMOS_HOST = os.environ.get('COSMOS_HOST', '${{ secrets.COSMOS_HOST }}')
COSMOS_KEY = os.environ.get('COSMOS_KEY', '${{ secrets.COSMOS_KEY }}')


@app.route("/")
def index():
    return (
        "Try /hello/Petra for parameterized Flask route.\n"
        f"Try /module for module import guidance {COSMOS_HOST} {COSMOS_KEY}"
    )


@app.route("/hello/<name>", methods=['GET'])
def hello(name: str):
    return f"hello {name}"


if __name__ == "__main__":
    app.run()
