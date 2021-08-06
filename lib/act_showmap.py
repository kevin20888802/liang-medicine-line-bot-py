#https://www.google.com.tw/maps/search/%E8%97%A5%E5%B1%80/

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, PostbackEvent, TextMessage, URIAction,PostbackTemplateAction, CarouselColumn,CarouselTemplate, TemplateSendMessage,)


class ShowMapActions:

    def __init__(self,DBmanager,botapi,userstats):
        self.db_manager = DBmanager
        self.bot_api = botapi
        self.userstat = userstats
    pass

    # 顯示藥物步驟 0-0 - 顯示所有提醒
    def showmap(self,event):
        user_id = event.source.user_id # 使用者的內部id
        theMenu = CarouselTemplate(columns=[])
        MenuItem = CarouselColumn(
                thumbnail_image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Google_Maps_Logo_2020.svg/1137px-Google_Maps_Logo_2020.svg.png",
                title=f'拿藥',
                text=f'前往地圖尋找距離最近的藥局',
                actions=[
                    URIAction(
                        label="前往",
                        uri="https://www.google.com.tw/maps/search/%E8%97%A5%E5%B1%80/",
                        alt_uri="https://www.google.com.tw/maps/search/%E8%97%A5%E5%B1%80/"
                    )
                ]
            )
        theMenu.columns.append(MenuItem)

        self.bot_api.reply_message(event.reply_token,TemplateSendMessage(alt_text="地圖按鈕\n（電腦版可能無法顯示所以請使用手機）", template=theMenu))
        self.userstat.SetUserStatus(user_id,"","")
    pass

pass