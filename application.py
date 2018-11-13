from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os

app = Flask(__name__)

#環境変数取得
#YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
#YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi("NTMPGJFQFnQ0VDYOC8/KhRf3QjsM+n3d16zmz/a+M+s0G32q4jl+ymLcycn67Uay+OMPKoJRArDxm2fNrQFPf3USlriXfkOMU4yVYaprQOrX7F6c+Pox8r8KWLh63sot75WUepLg7WNqVHTG9jqCiwdB04t89/1O/w1cDnyilFU=")
handler = WebhookHandler("f51101ef56b44ff16b931e27ee488cc4")

@app.route("/")
def hello():
    text = YOUR_CHANNEL_ACCESS_TOKEN + YOUR_CHANNEL_SECRET
    return text

@app.route('/webhook', methods=['POST'])
def webhook():
    return '', 200, {}

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))

