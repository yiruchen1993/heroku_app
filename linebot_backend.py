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

load_dotenv()
channel_token = os.getenv('iwxjpGo33oFAcPliGCZhvKFag7Vd+yEYi/ekML5anCUh1yxs2hSJoKCo6j6M0rfi/xWFtD2NWbCtnEeMO2g/lckM83sMBDvlWslVamH5uZgNKEIlvkyrLgK416LXYEHHonMfl8kRFhHsFhR6UouM0gdB04t89/1O/w1cDnyilFU=')
secret = os.getenv('d913ea5f20d6456d0e78cdb9bdb8859f')

app = Flask(__name__)
line_bot_api = LineBotApi(channel_token)
handler = WebhookHandler(secret)


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
    # message = TextSendMessage(text=event.message.text)
    message = TextSendMessage(text='Hello World From Container!')
    line_bot_api.reply_message(event.reply_token, message)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)