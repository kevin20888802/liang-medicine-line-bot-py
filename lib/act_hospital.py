from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, PostbackEvent, TextMessage, URIAction,PostbackTemplateAction, CarouselColumn,CarouselTemplate, TemplateSendMessage,)


class HospitalActions:

    def __init__(self,DBmanager,botapi,userstats):
        self.db_manager = DBmanager
        self.bot_api = botapi
        self.userstat = userstats
    pass

    def ShowHospital(self,event):
        user_id = event.source.user_id # 使用者的內部id
        theMenu = CarouselTemplate(columns=[])
        MenuItem_0 = CarouselColumn(
                thumbnail_image_url="https://reg.chgh.org.tw/assets/img/title_1m.png",
                title=f'振興醫院',
                text=f'前往振興醫院線上掛號',
                actions=[
                    URIAction(
                        label="前往掛號",
                        uri="https://reg.chgh.org.tw/registc_cload.aspx",
                        alt_uri="https://reg.chgh.org.tw/registc_cload.aspx"
                    )
                ]
            )
        theMenu.columns.append(MenuItem_0)
        MenuItem_1 = CarouselColumn(
                thumbnail_image_url="https://www.vghtpe.gov.tw/img/logo.png",
                title=f'臺北榮民總醫院',
                text=f'前往臺北榮民總醫院線上掛號',
                actions=[
                    URIAction(
                        label="前往掛號",
                        uri="https://www6.vghtpe.gov.tw/reg/sectList.do?type=return",
                        alt_uri="https://www6.vghtpe.gov.tw/reg/sectList.do?type=return"
                    )
                ]
            )
        theMenu.columns.append(MenuItem_1)

        self.bot_api.reply_message(event.reply_token,TemplateSendMessage(alt_text="掛號按鈕\n（電腦版可能無法顯示所以請使用手機）", template=theMenu))
        self.userstat.SetUserStatus(user_id,"","")
    pass

pass