from flask import Flask
import numpy
app = Flask(__name__)

@app.route("/")
def hello():
    test = numpy.random.rand()
    return test