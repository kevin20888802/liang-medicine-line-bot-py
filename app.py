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
from threading import Timer
import os
import io
from datetime import datetime
from pyzbar.pyzbar import decode
from PIL import Image
from linebot.models.messages import ImageMessage
from linebot.models.send_messages import ImageSendMessage

#-------- Line Developer上面的bot密碼資訊 --------
local_test = True # 自己電腦上用ngrok測試=True ; 放到Heroku上=False
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

# 當文字訊息傳入
@handler.add(MessageEvent, message=TextMessage)
def handle_message_text(event):
    _msg = event.message.text # 傳入的訊息
    _return_str = "" # 傳出去的訊息
    _return_str = _msg
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=_return_str))
pass

# 當圖片訊息傳入
@handler.add(MessageEvent, message=ImageMessage)
def handle_image_text(event):
    # 取得圖片訊息(byte)並轉換成圖片形式(image)
    value = bytearray()
    message_content = line_bot_api.get_message_content(event.message.id)
    for chunk in message_content.iter_content():
        value += chunk
    pass
    img = Image.open(io.BytesIO(value))

    # QR Code 資訊
    print(decode(img))

    #　回應
    #line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=_oriImgUrl,preview_image_url=_preImgUrl))
pass

# 每秒執行的放這
def every_sec():
    Timer(1, every_sec, []).start()
    print("Check time : " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
pass
every_sec()

# 開啟LineBot功能
if __name__ == "__main__":
    app.run()
pass