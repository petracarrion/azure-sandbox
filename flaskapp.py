from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    return jsonify({"message": "python-wsgi-function-samples-flask"})


@app.route("/hello/<name>")
def hello(name: str):
    return jsonify({"message": f"Hello, {name} from python-wsgi-function-samples-flask"})
