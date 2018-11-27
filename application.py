import os, sys, json

from flask import Flask, render_template, request, abort
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import FollowEvent, MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

database_uri = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
    dbuser=os.environ["DB_USER"],
    dbpass=os.environ["DB_PASS"],
    dbhost=os.environ["DB_HOST"],
    dbname=os.environ["DB_NAME"]
)

app.config.update(
    SQLALCHEMY_DATABASE_URI=database_uri,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# initialize the database connection
db = SQLAlchemy(app)

# initialize database migration management
migrate = Migrate(app, db)

class UserList(db.Model):
    __tablename__ = "userlist"
    username = db.Column(db.VARCHAR(), primary_key=True)
    userid = db.Column(db.VARCHAR(), nullable=False)


#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/")
def hello():
    dbq = UserList.query.all()
    dbst = dbq[0]
    return str(dbst)

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
    repmes = "こんにちは"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=repmes))

@handler.add(FollowEvent)
def handle_follow(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    followname = profile.display_name
    followid = event.source.user_id

    record = UserList(username=followname, userid=followid)
    db.session.add(record)
    db.session.commit()

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="thanks for your following"))
