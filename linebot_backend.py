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
from dotenv import load_dotenv
import os
import psycopg2
import pandas as pd
from sqlalchemy import create_engine


load_dotenv()
channel_token = os.getenv('YOUR_CHANNEL_ACCESS_TOKEN')
secret = os.getenv('YOUR_CHANNEL_SECRET')
host = os.getenv('dbhost')
dbname = os.getenv('dbname')
user = os.getenv('dbuser')
port = os.getenv('dbport')
password = os.getenv('dbpassword')
db_info = {'user': user, 'password': password, 'host': host, 'port': port, 'dbname': dbname}
# print(db_info)

app = Flask(__name__)
line_bot_api = LineBotApi(channel_token)
handler = WebhookHandler(secret)


@app.route('/')
def index():
    return "hello this is linebotjobfinder"


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
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    userid = event.source.user_id
    input_message = event.message.text
    msg_list = input_message.split()
    app.logger.info("user_id: ", userid)
    app.logger.info("Handle: reply_token: " + event.reply_token + ", message: " + input_message)
    # content = "{}: {}".format(event.source.user_id, event.message.text)
    # line_bot_api.reply_message(event.reply_token, TextSendMessage(text=content))
    area_list = get_area_list()
    try:
        if input_message.lower() == "cancel":
            cancel_register(userid)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=input_message))
        elif (len(msg_list) >= 2) & (msg_list[0] in area_list):
            save_to_db(userid, input_message)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=input_message))
        else:
            msg = "please follow the registration rule"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))
    except Exception as e:
        print("error:", e)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Error"))


def get_area_list():
    pg_conn = connect_pg_db(db_info)
    sql_ = "select target_location from location_code_ct"
    row = pg_conn.execute(sql_)
    area_list = pd.DataFrame(row.fetchall(), columns=row.keys())
    pg_conn.close()
    return area_list.target_location.values


def save_to_db(userid, input_message):
    pg_conn = connect_pg_db(db_info)
    app.logger.info(pg_conn)
    msg_list = input_message.split()
    location = msg_list[0]
    position = " ".join(msg_list[1:])
    sql_ = "select * from insert_registration('{}', '{}', '{}')".format(userid, location, position)
    app.logger.info(sql_)
    with pg_conn.begin() as a:
        pg_conn.execute(sql_)
    pg_conn.close()


def cancel_register(userid):
    pg_conn = connect_pg_db(db_info)
    app.logger.info(pg_conn)
    sql_ = "delete from registration_ct where user_id = '{}'".format(userid)
    app.logger.info(sql_)
    with pg_conn.begin() as a:
        pg_conn.execute(sql_)
    pg_conn.close()


def connect_pg_db(db_info):
    conn_str = "{}://{}:{}@{}:{}/{}".format(
        "postgresql+psycopg2",
        db_info["user"],
        db_info["password"],
        db_info["host"],
        db_info["port"],
        db_info["dbname"],
    )
    alchemyEngine = create_engine(conn_str, pool_recycle=3600)
    pg_connection = alchemyEngine.connect()
    return pg_connection



if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    # app.run()