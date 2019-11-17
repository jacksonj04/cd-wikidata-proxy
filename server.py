from os import environ
from flask import Flask

print(environ.get('PORT'))

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello, World!"


app.run(
    port=environ.get('PORT')
)
