import os, sys, json

from flask import Flask, render_template, request, abort
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import FollowEvent, UnfollowEvent, MessageEvent, TextMessage, TextSendMessage

# Flaskアプリケーション初期化
app = Flask(__name__)

# DB接続設定(セキュリティの為、各値は環境変数に記載)
database_uri = 'postgresql://{dbuser}:{dbpass}@{dbhost}/{dbname}?client_encoding=utf8'.format(
    dbuser=os.environ["DB_USER"],
    dbpass=os.environ["DB_PASS"],
    dbhost=os.environ["DB_HOST"],
    dbname=os.environ["DB_NAME"]
)

# Flaskアプリケーションに、DB接続設定を付与
app.config.update(
    SQLALCHEMY_DATABASE_URI=database_uri,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# DB接続初期化
db = SQLAlchemy(app)

# DB移行管理ツール初期化(未使用だが念の為)
migrate = Migrate(app, db)

# userlistテーブルのカラム設定
class UserList(db.Model):
    __tablename__ = "userlist"
    username = db.Column(db.VARCHAR(), primary_key=True)
    userid = db.Column(db.VARCHAR(), nullable=False)

    # UserListの引数設定をしておくと、データ追加や削除時に便利
    def __init__(self, username, userid):
        self.username = username
        self.userid = userid

# LineBot環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

# LineBotAPI初期化
line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

# GETメソッド試験用
@app.route("/")
def hello():
    return "Hello World"

# DB接続試験用(SELECT文確認)
@app.route("/query")
def query():
    dbquery = db.session.query(UserList.username).all()
    ret = str(dbquery)
    return ret

# DB接続試験用(INSERT文確認)
@app.route("/dbadd")
def dbadd():
    record = UserList("UserY", "bbbbbbbb")
    db.session.add(record)
    db.session.commit()
    return "OK"

# POSTメソッド試験用
@app.route('/webhook', methods=['POST'])
def webhook():
    return '', 200, {}

# LineBotのWEBHOOK用
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

# LineBotにテキスト送信があった際の挙動(”こんにちは”と返すだけ)
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    repmes = event.message.id
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=repmes))

# LineBotを友達追加orブロック解除した際の挙動(UserListテーブルに相手のLINEの表示名、IDを追加しつつ応答を返す)
@handler.add(FollowEvent)
def handle_follow(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    followname = profile.display_name
    followid = event.source.user_id

    record = UserList(followname, followid)
    db.session.add(record)
    db.session.commit()

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="thanks for your following"))

# LineBotをブロックした際の挙動(UserListテーブルから相手のLINEの表示名、IDを削除する)
@handler.add(UnfollowEvent)
def handle_unfollow(event):
    unfollowid = event.source.user_id

    db.session.query(UserList).filter(UserList.userid==unfollowid).delete()
    db.session.commit()
