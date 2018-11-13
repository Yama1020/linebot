from flask import Flask
import os
app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

@app.route("/")
def hello():
    text = YOUR_CHANNEL_ACCESS_TOKEN + YOUR_CHANNEL_SECRET
    return text
