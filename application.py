from flask import Flask
import numpy
app = Flask(__name__)

@app.route("/")
def hello():
    test = str(numpy.random.rand())
    out = "Hello World" + test
    return out