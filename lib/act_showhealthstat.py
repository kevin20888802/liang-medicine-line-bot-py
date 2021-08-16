from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, PostbackEvent, TextMessage, URIAction,PostbackTemplateAction, CarouselColumn,CarouselTemplate, TemplateSendMessage,)
from linebot.models.send_messages import ImageSendMessage, TextSendMessage
from linebot.models.actions import CameraAction, MessageAction, PostbackAction

import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import pyimgur
import os
import pathlib
from pylab import mpl

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
            dates = []
            health_values = []
            if result != None:
                for row in result:
                    _msg += f"{row[2]} : {row[3]}\n"
                    dates.append(row[2])
                    health_values.append(row[3])
                pass
            pass
            if _msg == "":
                _msg = "尚無任何紀錄"
            pass
            #dates = ['01/02/1991','01/03/1991','01/04/1991']
            x = [dt.datetime.strptime(d,'%Y/%m/%d %H:%M:%S') for d in dates]
            y = health_values
            mpl.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] # 指定默认字体
            mpl.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题
            plt.plot_date(x,y,linestyle ='solid')
            plt.title(typeName,fontsize=30)
            #now_dir = os.getcwd()
            PATH = f"healthstat_{user_id}.png"
            plt.savefig(PATH)
            CLIENT_ID = "18290f38ca7a80f"
            im = pyimgur.Imgur(CLIENT_ID)
            uploaded_image = im.upload_image(PATH, title="HealthStat with PyImgur")
            img_link = uploaded_image.link
            os.remove(PATH)
            self.bot_api.reply_message(event.reply_token,[TextSendMessage(text=f"以下是您的{typeName}紀錄\n\n{_msg}"),
            ImageSendMessage(original_content_url=img_link,preview_image_url=img_link)])
            self.userstat.SetUserStatus(user_id,"","")
        else:
            self.bot_api.reply_message(event.reply_token,TextSendMessage(text=f"奇怪...對不起我找不到紀錄表沒辦法給你看看"))
        pass
    pass

pass