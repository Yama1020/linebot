from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    FollowEvent, MessageEvent, TextMessage, TextSendMessage,
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
    text = "Hello World!"
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

@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='初めまして')
    )

    profile = line_bot_api.get_profile(event.source.user_id)
    user_id = event.source.user_id
    user_disp_name = profile.display_name
    
    dbinfo = os.environ['CUSTOMCONNSTR_dbconn']
    
    # DB接続
    conn = pyodbc.connect(dbinfo)
    cursor = conn.cursor()
    
    # SQL実行
    sql = "INSERT into AssetMng.UserID (UserID, UserName) VALUES (?, ?)"
    cursor.execute(sql, (user_id, user_disp_name))
    result = cursor.fetchall()

    # DB切断
    conn.close()
    
