from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, PostbackEvent,FlexSendMessage, TextMessage, TextSendMessage ,PostbackTemplateAction, CarouselColumn,CarouselTemplate, TemplateSendMessage,)

from datetime import datetime
import json 

class ShowNotifyActions:

    def __init__(self,DBmanager,botapi,userstats):
        self.db_manager = DBmanager
        self.bot_api = botapi
        self.userstat = userstats
    pass

    # 顯示藥物步驟 0-0 - 顯示所有提醒
    def shownotify_0_0(self,event):
        user_id = event.source.user_id # 使用者的內部id
        takeMedMenu = CarouselTemplate(columns=[])
        userNotifyList = self.db_manager.execute(f"Select * From Notify Where UserID = '{user_id}'")

        if userNotifyList != None:
            for notify in userNotifyList:
                medcine_name = ""
                medicine_type = ""
                medicine_find = self.db_manager.execute(f"Select * From UserMedicine Where UserID = '{notify[1]}' and MedicineName = '{notify[3]}'")
                medcine_amount = 0
                for result in medicine_find:
                    medcine_name = result[2]
                    medicine_type = result[5]
                    medcine_amount = int(result[3])
                    break
                pass
                MedMenuItem = CarouselColumn(
                        thumbnail_image_url="https://i.imgur.com/YRGlJWm.png",
                        title=f'{medicine_type}',
                        text=f'{notify[3]}({notify[4]})\n\n上次吃藥日期為{notify[6]}',
                        actions=[
                            PostbackTemplateAction(label='刪除',text=f'刪除提醒 - {notify[3]}({notify[4]})',data=f'delete;{notify[0]}'),
                            PostbackTemplateAction(label='藥量',text=f'查看藥量 - {notify[3]}({notify[4]})',data=f'amount;{notify[0]};{medcine_name};{medcine_amount}')
                        ]
                    )
                takeMedMenu.columns.append(MedMenuItem)
                if len(takeMedMenu.columns) >= 10:
                    break
                pass
            pass
        pass

        if len(takeMedMenu.columns) > 0:
            self.bot_api.reply_message(event.reply_token,TemplateSendMessage(alt_text="吃藥提醒列表\n（電腦版可能無法顯示所以請使用手機）", template=takeMedMenu))
            self.userstat.SetUserStatus(user_id,"shownotify_0_1","")
        else:
            self.bot_api.reply_message(event.reply_token,TextSendMessage(text="不錯喔，有乖乖吃藥...，還是說你還沒設定吃藥提醒所以才沒有需要吃的藥？哈哈哈"))
            self.userstat.SetUserStatus(user_id,"","")
        pass
    pass

    # 顯示藥物步驟 0-1 - 對提醒執行動作例如刪除
    def shownotify_0_1(self,event):
        user_id = event.source.user_id # 使用者的內部id
        _msg = ""

        # 選定的提醒id
        if event.type != "postback":
            return
        pass
        input_datas = event.postback.data.split(";")
        theAct = input_datas[0]
        selected_notify_id = input_datas[1]
        if theAct == "delete":
            _msg += "已刪除提醒"
            self.db_manager.execute(f"Delete From Notify Where UserID = '{user_id}' and ID = '{selected_notify_id}'")
            self.bot_api.reply_message(event.reply_token,TextSendMessage(text=f"{_msg}"))
        elif theAct == "amount":
            _msg += f"{input_datas[2]}"
            _msg += "剩餘藥量"
            with open('./msg_progessbar.json', 'r') as f:
                progess_msg = json.load(f)
                progess_msg['body']['contents'][0]['contents'][0]['contents'][0]['text'] = f"{input_datas[2]}"
                progess_msg['body']['contents'][0]['contents'][0]['contents'][1]['text'] = f"剩下{input_datas[3]}個"
                progess_msg['body']['contents'][0]['contents'][1]['text'] = f"{float(input_datas[3]) / 100.0}%"
                progess_msg['body']['contents'][1]['width'] = f"{float(input_datas[3]) / 100.0}%"
                self.bot_api.reply_message(event.reply_token,[TextSendMessage(text=f"{_msg}")
                ,FlexSendMessage(alt_text="藥量顯示",contents=progess_msg)])
            pass
        pass

        # reply msg
    pass

    # Print iterations progress
    def ProgressBarStr (self,iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        o_str = f'\r{prefix} |{bar}| {percent}% {suffix}'
        return o_str
    pass

pass