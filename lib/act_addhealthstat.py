from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, PostbackEvent, TextMessage, URIAction,PostbackTemplateAction, CarouselColumn,CarouselTemplate, TemplateSendMessage,)
from linebot.models.send_messages import TextSendMessage
from linebot.models.actions import CameraAction, MessageAction, PostbackAction
from datetime import datetime

class AddHealthStatActions:

    def __init__(self,DBmanager,botapi,userstats):
        self.db_manager = DBmanager
        self.bot_api = botapi
        self.userstat = userstats
    pass

    def addhealthstat_0(self,event):
        user_id = event.source.user_id # 使用者的內部id
        
        theMenu = CarouselTemplate(columns=[])
    
        MenuItem_0 = CarouselColumn(
                thumbnail_image_url="https://i.imgur.com/3DRZNmT.png",
                title=f'生理數值類別',
                text=f'請問要記錄的是什麼數值？',
                actions=[
                    MessageAction(label="脈搏",text="脈搏"),
                    MessageAction(label="血壓",text="脈搏"),
                    MessageAction(label="血糖",text="血糖")
                ]
            )
        theMenu.columns.append(MenuItem_0)

        self.bot_api.reply_message(event.reply_token,TemplateSendMessage(alt_text="生理數值類別\n（電腦版可能無法顯示請直接輸入名稱）", template=theMenu))
        self.userstat.SetUserStatus(user_id,"addhealthstat_1","")
    pass

    def addhealthstat_1(self,event):
        user_id = event.source.user_id # 使用者的內部id
        i_msg = event.message.text.replace(";","")

        vaild_stat_type = {"脈搏","血壓","血糖"}

        if i_msg in vaild_stat_type:    
            theMenu = CarouselTemplate(columns=[])
            MenuItem_0 = CarouselColumn(
                    thumbnail_image_url="https://i.imgur.com/uMyD6TA.png",
                    title=f'數值',
                    text=f'請使用相機滑到最左邊的文字辨識功能拍下數字或者用畫面左下的鍵盤按鈕打字讓我看看！',
                    actions=[
                        CameraAction(label="開啟相機")
                    ]
                )
            theMenu.columns.append(MenuItem_0)
            self.bot_api.reply_message(event.reply_token,TemplateSendMessage(alt_text="數字輸入\n（電腦版可能無法顯示請直接輸入名稱）", template=theMenu))
            self.userstat.SetUserStatus(user_id,"addhealthstat_2",i_msg)    
        else:
            self.bot_api.reply_message(event.reply_token,TextSendMessage(text=f"{i_msg}這個數值暫時沒有紀錄，請選擇正確的生理數值。"))
        pass 
    pass

    def addhealthstat_2(self,event):
        _msg = event.message.text # 傳入的訊息
        user_id = event.source.user_id # 使用者的內部id
        try: 
            statValue = float(_msg)
            typeName = self.userstat.GetUserTmpValue(user_id)
            now_time = datetime.now()
            now_time_str = now_time.strftime("%Y/%m/%d %H:%M:%S")
            tableName = {
                "脈搏":"UserHealth_Purse",
                "血壓":"UserHealth_BloodPressure",
                "血糖":"UserHealth_Glycemic"
            }
            if typeName in tableName:
                self.db_manager.execute(f"Insert Into {tableName[typeName]}(UserID,UpdateTime,Stat) Values('{user_id}','{now_time_str}',{statValue})")
                self.bot_api.reply_message(event.reply_token,TextSendMessage(text=f"成功記錄生理數值:\n{now_time_str}\n{typeName} : {statValue}"))
            else:
                self.bot_api.reply_message(event.reply_token,TextSendMessage(text=f"奇怪...對不起我找不到紀錄表沒辦法紀錄"))
            pass
            self.userstat.SetUserStatus(user_id,"","")
        except ValueError:
            self.bot_api.reply_message(event.reply_token,TextSendMessage(text="請輸入正確的數字"))
        pass
    pass

pass