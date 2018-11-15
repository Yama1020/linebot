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
import sys
import json
import pyodbc

app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/")
def hello():
    # DB接続情報を環境変数から取得
    dbinfo = os.environ['CUSTOMCONNSTR_dbconn']
    # DB接続
    #conn = pyodbc.connect(dbinfo)
    #cursor = conn.cursor()
    # SQL実行(貸し出し期限を過ぎた本と借りている人を抽出)
    #sql = "SELECT title from AssetMng.BookList"
    #cursor.execute(sql)
    #result = cursor.fetchall()
    # DB切断
    #conn.close()
    
    return dbinfo

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
        TextSendMessage(text=event.source.user_id))

