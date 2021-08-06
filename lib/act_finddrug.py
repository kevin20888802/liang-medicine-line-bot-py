#https://www.kingnet.com.tw/medicine/list?selectType=formulation&keyword=藥品名稱
# 
# 
# 1. 抓裡面tbody id = search-list
# 2. tbody裡面抓第一個tr 
# 3. tr裡面隨便抓一個a的href
# 4. 進入那個href網頁
# 5. 藥品名稱抓h1 id = medicine-name的 文字內容
#    適應症抓 div itemprop=description的 文字內容
#    藥品類型(用法與用量)抓 td == 藥品類型的那格的另外一個td的文字內容
#    

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, PostbackEvent, TextMessage, URIAction,PostbackTemplateAction, CarouselColumn,CarouselTemplate, TemplateSendMessage,)
from linebot.models.send_messages import TextSendMessage

from bs4 import BeautifulSoup
import requests
request_headers={
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
}

class FindDrugActions:

    def __init__(self,DBmanager,botapi,userstats):
        self.db_manager = DBmanager
        self.bot_api = botapi
        self.userstat = userstats
    pass

    # 尋找藥物步驟 0 - 輸入藥品名稱
    def finddrug_0(self,event):
        user_id = event.source.user_id # 使用者的內部id
        self.bot_api.reply_message(event.reply_token,TextSendMessage(text="請輸入藥品名稱"))
        self.userstat.SetUserStatus(user_id,"finddrug_1","")
    pass

    # 取得網頁原始碼
    def get_page(url):
        # 取得資料
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"}
        cookies = {"cookie":''}
        response = requests.get(url, headers=headers,cookies=cookies)
        if response.status_code == 200:
            return response.text
        return None
    pass

    # 尋找藥物步驟 1 - 爬蟲尋找藥品
    def finddrug_1(self,event):

    pass

pass