#https://www.kingnet.com.tw/medicine/list?selectType=formulation&keyword=藥品名稱
# 
# 
# 1. 抓裡面tbody id = search-list
# 2. tbody裡面抓第一個tr 
# 3. tr裡面隨便抓一個a的href
# 4. 進入那個href網頁
# 5. 藥品名稱抓h1 id = medicine-name的 文字內容
#    適應症抓 div itemprop=description的 文字內容
#    藥品類型(用法與用量)抓tbody id = merchandise-inf-content 表格裡面抓 td == 藥品類型的那格的另外一個td的文字內容
#    

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, PostbackEvent, TextMessage, URIAction,PostbackTemplateAction, CarouselColumn,CarouselTemplate, TemplateSendMessage,)
from linebot.models.send_messages import TextSendMessage
from linebot.models.actions import CameraAction
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
        
        theMenu = CarouselTemplate(columns=[])
    
        MenuItem_0 = CarouselColumn(
                thumbnail_image_url="https://i.imgur.com/uMyD6TA.png",
                title=f'藥名',
                text=f'請問您要尋找的的藥是？請使用相機滑到最左邊的文字辨識功能或者用畫面左下的鍵盤按鈕打字讓我看看！',
                actions=[
                    CameraAction(label="開啟相機")
                ]
            )
        theMenu.columns.append(MenuItem_0)

        self.bot_api.reply_message(event.reply_token,TemplateSendMessage(alt_text="藥品名稱輸入\n（電腦版可能無法顯示請直接輸入名稱）", template=theMenu))
        self.userstat.SetUserStatus(user_id,"finddrug_1","")
    pass

    # 取得網頁原始碼
    def get_page(self,url):
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
        # 傳入的訊息+過濾分割用字元
        i_msg = event.message.text.replace(";","") 
        o_msg = ""
        msg_splitLine = "------------"
        # 是否找到
        hasDrug = True

        # 搜尋
        #try:
        SearchSoup = BeautifulSoup(self.get_page(f"https://www.kingnet.com.tw/medicine/list?selectType=formulation&keyword=" + i_msg), 'html.parser')
        search_table = SearchSoup.find("tbody",id='search-list') # 1. 抓裡面tbody id = search-list
        result_list = search_table.find_all("tr") # 2. tbody裡面抓第一個tr 
        if len(result_list) > 0: # 3. tr裡面隨便抓一個a的href 
            drug_uri = result_list[0].find_all("td")[1].find("a")['href']
            drug_uri = "https://www.kingnet.com.tw" + drug_uri
            # 4. 進入那個href網頁
            drug_soup =  BeautifulSoup(self.get_page(drug_uri), 'html.parser')

            print(drug_soup)
            # 藥品名稱抓h1 id = medicine-name的 文字內容
            medicine_name = drug_soup.find("h1",id='medicine-name').getText()

            # 適應症抓 div itemprop=description的 文字內容
            drug_indications = drug_soup.find("div",attrs={'itemprop': 'description'}).getText()

            # 藥品類型(用法與用量)抓tbody id = merchandise-inf-content 表格裡面抓 td == 藥品類型的那格的另外一個td的文字內容
            drug_type = "暫無"
            drug_detail_table = drug_soup.find(id='merchandise-inf-content')
            drug_detail_list = drug_detail_table.find_all("tr")
            for row in drug_detail_list:
                row_td = row.find_all("td")
                row_title = row_td[0].getText()
                row_content = row_td[1].getText()
                if row_title == "藥品類別":
                    drug_type = row_content
                    break
                pass
            pass
            o_msg = f"藥品名稱:\n{medicine_name}\n{msg_splitLine}\n適應症:\n{drug_indications}\n{msg_splitLine}\n藥品類型(用法與用量):\n{drug_type}"
            o_msg += f"\n{msg_splitLine}\n\n詳細內容請洽:{drug_uri}"

        else:
            hasDrug = False
        pass
        #except Exception as e:
        #     hasDrug = False
        #     print(str(e))
        #pass

        if hasDrug == False:
            o_msg = "查無此藥"
        pass

        self.bot_api.reply_message(event.reply_token,TextSendMessage(text=o_msg))
    pass

pass