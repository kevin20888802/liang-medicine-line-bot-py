from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import LineBotApiError
from linebot.models import RichMenu,RichMenuResponse,RichMenuArea,RichMenuBounds,RichMenuSize,MessageAction
import json

class Menu_Manager:

    def __init__(self,DBmanager,botapi,userstats):
        self.db_manager = DBmanager
        self.line_bot_api = botapi
        self.userstat = userstats
        self.menu_ids = {}
        self.SetupMenus()
    pass

    def ClearMenus(self):
        rich_menu_list = self.line_bot_api.get_rich_menu_list()
        for menuItem in rich_menu_list:
            self.line_bot_api.delete_rich_menu(menuItem.as_json_dict()["richMenuId"])
        pass
    pass

    def SetupMenus(self):
        self.ClearMenus()

        main_menu_size = [2500,1686]
        main_menu = RichMenu(
        size=RichMenuSize(width=main_menu_size[0], height=main_menu_size[1]),
        selected=False,
        name="main_menu",
        chat_bar_text="主頁",
        areas=[
            RichMenuArea(bounds=RichMenuBounds(x=0, y=0, width=main_menu_size[0] / 3, height=main_menu_size[1]),action=MessageAction(label='act0', text='藥物選單')),
            RichMenuArea(bounds=RichMenuBounds(x=834, y=0, width=main_menu_size[0] / 3, height=main_menu_size[1]),action=MessageAction(label='act1', text='生理紀錄')),
            RichMenuArea(bounds=RichMenuBounds(x=1668, y=0, width=main_menu_size[0] / 3, height=main_menu_size[1]),action=MessageAction(label='act2', text='線上預約'))
            ])
        self.menu_ids["main_menu"] = self.line_bot_api.create_rich_menu(rich_menu=main_menu)
        with open("lib/MenuImg/richmenu_1628187718435_1.png", 'rb') as f:
            self.line_bot_api.set_rich_menu_image(self.menu_ids["main_menu"], "image/png", f)
        pass

        drug_menu_size = [2500,1686]
        drug_menu = RichMenu(
        size=RichMenuSize(width=drug_menu_size[0], height=drug_menu_size[1]),
        selected=False,
        name="drug_menu",
        chat_bar_text="藥物相關功能",
        areas=[
            RichMenuArea(bounds=RichMenuBounds(x=0, y=0, width=drug_menu_size[0] / 3, height=drug_menu_size[1] / 2),action=MessageAction(label='act0', text='提醒')),
            RichMenuArea(bounds=RichMenuBounds(x=834, y=0, width=drug_menu_size[0] / 3, height=drug_menu_size[1] / 2),action=MessageAction(label='act1', text='吃藥')),
            RichMenuArea(bounds=RichMenuBounds(x=1668, y=0, width=drug_menu_size[0] / 3, height=drug_menu_size[1] / 2),action=MessageAction(label='act2', text='查詢')),
            RichMenuArea(bounds=RichMenuBounds(x=0, y=843, width=drug_menu_size[0] / 3, height=drug_menu_size[1] / 2),action=MessageAction(label='act3', text='吃什麼藥')),
            RichMenuArea(bounds=RichMenuBounds(x=834, y=843, width=drug_menu_size[0] / 3, height=drug_menu_size[1] / 2),action=MessageAction(label='act4', text='吃藥紀錄')),
            RichMenuArea(bounds=RichMenuBounds(x=1668, y=843, width=drug_menu_size[0] / 3, height=drug_menu_size[1] / 2),action=MessageAction(label='act5', text='主選單'))
            ])
        self.menu_ids["drug_menu"] = self.line_bot_api.create_rich_menu(rich_menu=drug_menu)
        with open("lib/MenuImg/richmenu_1628187718435.png", 'rb') as f:
            self.line_bot_api.set_rich_menu_image(self.menu_ids["drug_menu"], "image/png", f)
        pass


        health_menu_size = [2500,1686]
        health_menu = RichMenu(
        size=RichMenuSize(width=health_menu_size[0], height=health_menu_size[1]),
        selected=False,
        name="health_menu",
        chat_bar_text="生理數值相關",
        areas=[
            RichMenuArea(bounds=RichMenuBounds(x=0, y=0, width=health_menu_size[0] / 3, height=health_menu_size[1]),action=MessageAction(label='act0', text='新增生理紀錄')),
            RichMenuArea(bounds=RichMenuBounds(x=834, y=0, width=health_menu_size[0] / 3, height=health_menu_size[1]),action=MessageAction(label='act1', text='查看生理紀錄')),
            RichMenuArea(bounds=RichMenuBounds(x=1668, y=0, width=health_menu_size[0] / 3, height=health_menu_size[1]),action=MessageAction(label='act2', text='主選單'))
            ])
        self.menu_ids["health_menu"] = self.line_bot_api.create_rich_menu(rich_menu=health_menu)
        with open("lib/MenuImg/richmenu_1628187718435_2.png", 'rb') as f:
            self.line_bot_api.set_rich_menu_image(self.menu_ids["health_menu"], "image/png", f)
        pass

        with open('menu_id.json', 'w') as f:
            json.dump(self.menu_ids, f)
        pass
    pass

    def SwitchMenuCheck(self,event):
        user_id = event.source.user_id # 使用者的內部id
        i_msg = event.message.text.replace(";","") 
        menu_names = {
            "主選單":"main_menu",
            "藥物選單":"drug_menu",
            "生理紀錄":"health_menu"
            }
         
        with open('menu_id.json', 'r') as f:
            self.menu_ids = json.load(f)
        pass  

        if i_msg in menu_names:
            if menu_names[i_msg] in self.menu_ids:
                self.line_bot_api.link_rich_menu_to_user(user_id, self.menu_ids[menu_names[i_msg]])
            pass
        pass
    pass

    def SwitchToMainMenu(self,event):
        user_id = event.source.user_id # 使用者的內部id
        self.line_bot_api.link_rich_menu_to_user(user_id, self.main_menu_id)
    pass

pass