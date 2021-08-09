from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, PostbackEvent, TextMessage, URIAction,PostbackTemplateAction, CarouselColumn,CarouselTemplate, TemplateSendMessage,)
from linebot.models.send_messages import TextSendMessage
from linebot.models.actions import CameraAction, MessageAction, PostbackAction

class ShowHealthStatActions:

    def __init__(self,DBmanager,botapi,userstats):
        self.db_manager = DBmanager
        self.bot_api = botapi
        self.userstat = userstats
    pass

    def showhealthstat_0(self,event):
        user_id = event.source.user_id # 使用者的內部id
        
        theMenu = CarouselTemplate(columns=[])
    
        MenuItem_0 = CarouselColumn(
                thumbnail_image_url="https://i.imgur.com/3DRZNmT.png",
                title=f'生理數值類別',
                text=f'請問要查看的是什麼數值？',
                actions=[
                    MessageAction(label="脈搏",text="脈搏"),
                    MessageAction(label="血壓",text="脈搏"),
                    MessageAction(label="血糖",text="血糖")
                ]
            )
        theMenu.columns.append(MenuItem_0)

        self.bot_api.reply_message(event.reply_token,TemplateSendMessage(alt_text="生理數值類別\n（電腦版可能無法顯示請直接輸入名稱）", template=theMenu))
        self.userstat.SetUserStatus(user_id,"showhealthstat_1","")
    pass

    def showhealthstat_1(self,event):
        user_id = event.source.user_id # 使用者的內部id
        i_msg = event.message.text # 傳入的訊息
        _msg = ""
        typeName = i_msg
        tableName = {
            "脈搏":"UserHealth_Purse",
            "血壓":"UserHealth_BloodPressure",
            "血糖":"UserHealth_Glycemic"
        }
        if typeName in tableName:
            result = self.db_manager.execute(f"Select * From {tableName[typeName]} Where UserID = '{user_id}'")
            if result != None:
                for row in result:
                    _msg += f"{row[2]} : {row[3]}\n"
                pass
            pass
            if _msg == "":
                _msg = "尚無任何紀錄"
            pass
            self.bot_api.reply_message(event.reply_token,TextSendMessage(text=f"以下是您的{typeName}紀錄\n\n{_msg}"))
            self.userstat.SetUserStatus(user_id,"","")
        else:
            self.bot_api.reply_message(event.reply_token,TextSendMessage(text=f"奇怪...對不起我找不到紀錄表沒辦法給你看看"))
        pass
    pass

pass