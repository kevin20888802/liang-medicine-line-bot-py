# app.py
# 要pip install 的套件 
# 請在根目錄底下的requirements.txt加一行然後打上所需套件名稱
# 一行一個套件

# http模擬
from collections import UserString
from flask import Flask, request, abort

# line sdk
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, PostbackEvent, TextMessage, TextSendMessage,TemplateSendMessage, ButtonsTemplate, DatetimePickerTemplateAction,)
from linebot.models.messages import ImageMessage
from linebot.models.send_messages import ImageSendMessage

# 系統相關lib
from threading import Timer, local
import tempfile
import os
from os import environ
import io
from datetime import datetime

# 圖片相關lib
from pyzbar.pyzbar import decode
from PIL import Image


#------------------------------------------------
local_test = False # 自己電腦上用ngrok測試=True ; 放到Heroku上=False
#-------- Line Developer上面的bot密碼資訊 --------
_token = "" 
_secret = ""
#------------------------------------------------
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


#------------------------------------------------

from lib.db_manager import PostgresBaseManager as dbm
db_manager = dbm(local_test)
db_manager.connect()
db_manager.testConnection()
db_manager.executeFile("sql/setupAppDB.sql")
#db_manager.execute(db_manager.setupSQLCMD)

from lib.user_stat_manager import User_Status_Manager 
userstat = User_Status_Manager(db_manager,line_bot_api)

from lib.menu_manager import Menu_Manager
menu_manage = Menu_Manager(db_manager,line_bot_api,userstat)

#------------------------------------------------

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

# 當特殊訊息(Postback)傳入
@handler.add(PostbackEvent)
def handle_postback(event):    
    userstat.UserStatusExecute(event)
pass

# 當文字訊息傳入
@handler.add(MessageEvent, message=TextMessage)
def handle_message_text(event):

    _msg = event.message.text # 傳入的訊息
    user_id = event.source.user_id # 使用者的內部id

    menu_manage.SwitchMenuCheck(event)

    # 狀態對應表
    msgStatus = {"提醒":"notify_0_0"
    ,"吃藥":"takemed_0_0"
    ,"查詢":"finddrug_0"
    ,"拿藥":"showmap"
    ,"吃什麼藥":"shownotify_0_0"
    ,"吃藥紀錄":"showtakehistory"
    ,"線上預約":"showhospital"
    ,"新增生理紀錄":"addhealthstat_0"
    ,"查看生理紀錄":"showhealthstat_0"
    ,"掃描":"showcamera"}

    if _msg in msgStatus:
        userstat.SetUserStatus(user_id,msgStatus[_msg],None)
    pass

    userstat.UserStatusExecute(event)

pass

# 當圖片訊息傳入
@handler.add(MessageEvent, message=ImageMessage)
def handle_image_text(event):

    user_id = event.source.user_id # 使用者的內部id

    # 取得圖片訊息(byte)並轉換成圖片形式(image)
    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.TemporaryFile() as tmp:
        for chunk in message_content.iter_content():
            tmp.write(chunk)
        img = Image.open(tmp)
        o_msg = ""

        # QR Code 資訊
        QRText = decode(image=img)
        print(f"Decoding QR Code:\n----------------\n{QRText[0].data}\n----------------\n")

        QRData = QRText[0].data.decode("utf-8").split("\n")
        print(QRData)
        if QRData[0] == "QR新增提醒":
            o_msg += "已新增提醒:\n"
            for i in range(2,len(QRData)):
                #名稱,類型,數量,服用,時間
                NotifyData = QRData[i].split(",")
                _notifyName = NotifyData[0]
                _notifyType = NotifyData[1]
                _notifyAmount = NotifyData[2]
                _notifyTake = NotifyData[3]
                _notifyTime = NotifyData[4]
                
                # 在使用者藥品表增加使用者的藥名如果沒有的話 (數量先設定為0如果是新的藥品)
                findCount = db_manager.execute(f"Select Count(*) From UserMedicine Where UserID = '{user_id}' and MedicineName = '{_notifyName}'") 
                if findCount == None or findCount[0][0] <= 0:
                    db_manager.execute(f"Insert Into UserMedicine(UserID,MedicineName,Amount,TakeAmount) Values('{user_id}','{_notifyName}',0,1)")
                pass
                db_manager.execute(f"Update UserMedicine Set MedType = '{_notifyType}', Amount = {_notifyAmount}, TakeAmount = {_notifyTake} Where UserID = '{user_id}' and MedicineName = '{_notifyName}'")
                db_manager.execute(f"Insert Into Notify(UserID,Description,TargetMedicine,TargetTime,LastNotifyDate,TakeDate) Values('{user_id}','','{_notifyName}','{_notifyTime}','','尚未吃過藥')")
                o_msg += f"{_notifyTime} - [{_notifyType}]{_notifyName}\n(單次服用數量:{_notifyTake}/剩餘數量:{_notifyAmount})\n"
            pass
        pass
        #　回應
        if o_msg != "":
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=o_msg))
        pass
    pass
pass

# 每半分鐘執行的放這
def every_halfmin():
    Timer(30, every_halfmin, []).start()
    print("Check time : " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    notifyList = db_manager.execute("Select * From Notify")
    if notifyList != None:
        nowTime = datetime.now()
        nowDate = nowTime.strftime("%Y/%m/%d")
        for notify in notifyList:
            print(notify)
            notifyTime = nowTime.replace(hour=int(notify[4].split(":")[0]), minute=int(notify[4].split(":")[1]))
            # 如果時間有到或超過而且沒提醒過而且沒吃過藥就提醒該用戶一次（注意有爛死的500次推播限制大公司連個小Discord都比不上是怎？）
            if nowTime >= notifyTime and notify[5] != nowDate and notify[6] != nowDate:
                medicine_type = ""
                medicine_find = db_manager.execute(f"Select MedType From UserMedicine Where UserID = '{notify[1]}' and MedicineName = '{notify[3]}'")
                for mediType in medicine_find:
                    medicine_type = mediType[0]
                    break
                pass
                line_bot_api.push_message(notify[1], TextSendMessage(text=f"吃{medicine_type}時間！({notify[4]})\n\n{notify[3]}"))
                #　提醒過就把該提醒標記成有提醒過
                db_manager.execute(f"Update Notify Set LastNotifyDate = '{nowDate}' Where ID = '{notify[0]}'")
            pass
        pass
    pass
pass
every_halfmin()

# 開啟LineBot功能
if __name__ == "__main__":
    #db_manager.executeFile("sql/setupAppDB.sql")
    app.run(port=environ.get("PORT", 5000))
    db_manager.disconnect()
pass