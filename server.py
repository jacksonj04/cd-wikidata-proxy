from os import environ
from flask import Flask

print(environ.get('PORT'))

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello, World!"


app.run(
    host='0.0.0.0',
    port=environ.get('PORT')
)
