from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, PostbackEvent, TextMessage, URIAction,PostbackTemplateAction, CarouselColumn,CarouselTemplate, TemplateSendMessage,)
from linebot.models.send_messages import TextSendMessage
from linebot.models.actions import CameraAction

class ShowCamera:   

    def __init__(self,DBmanager,botapi,userstats):
        self.db_manager = DBmanager
        self.bot_api = botapi
        self.userstat = userstats
    pass

    def showcamera(self,event):
        theMenu = CarouselTemplate(columns=[])
    
        MenuItem_0 = CarouselColumn(
                thumbnail_image_url="https://i.imgur.com/uMyD6TA.png",
                title=f'掃描',
                text=f'開啟相機拍下QR Code',
                actions=[
                    CameraAction(label="開啟相機")
                ]
            )
        theMenu.columns.append(MenuItem_0)

        self.bot_api.reply_message(event.reply_token,TemplateSendMessage(alt_text="掃描\n（電腦版可能無法顯示請直接上傳圖片）", template=theMenu))
    pass
pass