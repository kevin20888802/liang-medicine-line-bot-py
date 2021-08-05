# app.py
# 要pip install 的套件 
# 請在根目錄底下的requirements.txt加一行然後打上所需套件名稱
# 一行一個套件

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

#-------- Line Developer上面的bot密碼資訊 --------
local_test = False # 自己電腦上用ngrok測試=True ; 放到Heroku上=False
_token = "" 
_secret = ""

if local_test == False:
    _token = os.environ['token']
    _secret = os.environ['secretcode']
else:
    _tokenFile = open("../secret_token_file.txt","r")
    _token = _tokenFile.readline().replace("\n","")
    _secret = _tokenFile.readline().replace("\n","")
pass
#------------------------------------------------

app = Flask(__name__)
line_bot_api = LineBotApi(_token)
handler = WebhookHandler(_secret)

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
    pass
    return 'OK'
pass

# 當訊息傳入
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    _msg = event.message.text # 傳入的訊息

    _return_str = "" # 傳出去的訊息
    _return_str = _msg
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=_return_str))

pass

if __name__ == "__main__":
    app.run()
pass