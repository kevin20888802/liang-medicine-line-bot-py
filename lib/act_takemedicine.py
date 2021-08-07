from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, PostbackEvent, TextMessage, TextSendMessage ,PostbackTemplateAction, CarouselColumn,CarouselTemplate, TemplateSendMessage,)

from datetime import datetime

class TakeMedicineActions:

    def __init__(self,DBmanager,botapi,userstats):
        self.db_manager = DBmanager
        self.bot_api = botapi
        self.userstat = userstats
    pass

    # 吃藥步驟 0-0 - 詢問吃什麼藥?
    def takemed_0_0(self,event):
        user_id = event.source.user_id # 使用者的內部id
        takeMedMenu = CarouselTemplate(columns=[])
        userNotifyList = self.db_manager.execute(f"Select * From Notify Where UserID = '{user_id}'")

        if userNotifyList != None:
            now_time = datetime.now()
            now_time_str = now_time.strftime("%Y/%m/%d")
            for notify in userNotifyList:
                if notify[5] != notify[6] and notify[6] != now_time_str: # 如果上次提醒日期不等於吃藥日期並且吃藥日期不是今天就加入列表
                    medicine_type = ""
                    medicine_find = self.db_manager.execute(f"Select MedType From UserMedicine Where UserID = '{notify[1]}' and MedicineName = '{notify[3]}'")
                    for mediType in medicine_find:
                        medicine_type = mediType[0]
                        break
                    pass
                    MedMenuItem = CarouselColumn(
                            thumbnail_image_url="https://i.imgur.com/YRGlJWm.png",
                            title=f'{medicine_type}',
                            text=f'{notify[3]}({notify[4]})\n\n上次吃藥日期為{notify[6]}',
                            actions=[
                                PostbackTemplateAction(
                                    label='吃藥',
                                    text=f'吃藥 - {notify[3]}({notify[4]})',
                                    data=f'{notify[0]}'
                                )
                            ]
                        )
                    takeMedMenu.columns.append(MedMenuItem)
                pass
            pass
        pass

        if len(takeMedMenu.columns) > 0:
            self.bot_api.reply_message(event.reply_token,TemplateSendMessage(alt_text="吃藥列表\n（電腦版可能無法顯示所以請使用手機）", template=takeMedMenu))
            self.userstat.SetUserStatus(user_id,"takemed_0_1","")
        else:
            self.bot_api.reply_message(event.reply_token,TextSendMessage(text="不錯喔，有乖乖吃藥...，還是說你還沒設定吃藥提醒所以才沒有需要吃的藥？哈哈哈"))
            self.userstat.SetUserStatus(user_id,"","")
        pass
    pass

    # 吃藥步驟 0-1 - 計算吃藥距離使用者選擇的提醒的時間差為多少後登記到吃藥紀錄表
    def takemed_0_1(self,event):
        user_id = event.source.user_id # 使用者的內部id

        now_time = datetime.now()
        now_time_str = now_time.strftime("%Y/%m/%d")

        # 選定的提醒id
        if event.type != "postback":
            return
        pass
        selected_notify_id = event.postback.data
        notifyList = self.db_manager.execute(f"Select * From Notify Where UserID = '{user_id}' and ID = '{selected_notify_id}'")
        history_str = ""
        target_med = ""
        if notifyList != None:
            for notify in notifyList:
                notifyTime = now_time.replace(hour=int(notify[4].split(":")[0]), minute=int(notify[4].split(":")[1]))
                time_delta = int((now_time - notifyTime).total_seconds()) # 吃藥的時間差
                early_or_late = ""
                if time_delta > 0:
                    early_or_late = "晚"
                    time_delta = int(abs(time_delta) / 60)
                elif time_delta < 0:
                    early_or_late = "提早"
                    time_delta = int(abs(time_delta) / 60)
                else:
                    early_or_late = "準時吃藥不多不少"
                pass
                history_str += f"{now_time_str}\n{notify[3]}({notify[4]})\n吃藥時間: {early_or_late}{time_delta}分鐘 "
                target_med = notify[3]
            pass
        pass

        # 把提醒的吃藥日期設定成今日
        self.db_manager.execute(f"Update Notify Set TakeDate = '{now_time_str}' Where UserID = '{user_id}' and ID = '{selected_notify_id}'")

        # 藥品的數量減少
        medicine_left = 0
        onetime_take_amount = 0
        result = self.db_manager.execute(f"Select * From UserMedicine Where UserID = '{user_id}' and MedicineName = '{target_med}'")
        print(target_med)
        if result != None:
            for row in result:
                print(row)
                onetime_take_amount = int(row[4])
                medicine_left = int(row[3])
            pass
        pass
        self.db_manager.execute(f"Update UserMedicine Set Amount = Amount - {onetime_take_amount} Where UserID = '{user_id}' and MedicineName = '{target_med}'")
        medicine_left -= onetime_take_amount

        # 加入一筆吃藥記錄到吃藥紀錄表
        self.db_manager.execute(f"Insert Into TakeMedicineHistory(UserID,Description,AnwTime) Values('{user_id}','{history_str}','{now_time_str}')")

        # reply msg
        self.bot_api.reply_message(event.reply_token,TextSendMessage(text=f"已紀錄吃藥：\n{history_str} \n剩餘藥品數量：{medicine_left}"))
    pass

pass