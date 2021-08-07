from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, PostbackEvent, TextMessage,MessageAction,PostbackTemplateAction, TextSendMessage,TemplateSendMessage, ButtonsTemplate, DatetimePickerTemplateAction,CarouselColumn,CarouselTemplate,)
from linebot.models.actions import CameraAction
from linebot.models.messages import Message

class NotifyActions:

    def __init__(self,DBmanager,botapi,userstats):
        self.db_manager = DBmanager
        self.bot_api = botapi
        self.userstat = userstats
    pass

    # 提醒步驟 0-0 - 詢問藥名
    def notify_0_0(self,event):
        user_id = event.source.user_id # 使用者的內部id
        theMenu = CarouselTemplate(columns=[])
    
        MenuItem_0 = CarouselColumn(
                thumbnail_image_url="https://i.imgur.com/uMyD6TA.png",
                title=f'藥名',
                text=f'請問您吃的藥是（全部的藥）？請使用相機滑到最左邊的的文字辨識功能或者用畫面左下的鍵盤按鈕打字讓我看看！',
                actions=[
                    CameraAction(label="開啟相機")
                ]
            )
        theMenu.columns.append(MenuItem_0)

        self.bot_api.reply_message(event.reply_token,TemplateSendMessage(alt_text="藥品名稱輸入\n（電腦版可能無法顯示請直接輸入名稱）", template=theMenu))
        self.userstat.SetUserStatus(user_id,"notify_0_1","")
    pass

    # 提醒步驟 0-1 - 收到藥名
    def notify_0_1(self,event):  
        _msg = event.message.text.replace(";","") # 傳入的訊息+過濾分割用字元
        user_id = event.source.user_id # 使用者的內部id
        
        # 在使用者藥品表增加使用者的藥名如果沒有的話 (數量先設定為0如果是新的藥品)
        findCount = self.db_manager.execute(f"Select Count(*) From UserMedicine Where UserID = '{user_id}' and MedicineName = '{_msg}'") 
        if findCount == None or findCount[0][0] <= 0:
            self.db_manager.execute(f"Insert Into UserMedicine(UserID,MedicineName,Amount,TakeAmount) Values('{user_id}','{_msg}',0,1)")
        pass

        self.userstat.SetUserStatus(user_id,"notify_0_3",_msg)
        self.notify_0_2(event)
    pass

    # 提醒步驟 0-2 - 詢問藥品類型
    def notify_0_2(self,event):
        user_id = event.source.user_id # 使用者的內部id
        theMenu = CarouselTemplate(columns=[])
        MenuItem_0 = CarouselColumn(
                thumbnail_image_url="https://i.imgur.com/uMyD6TA.png",
                title=f'藥品類型',
                text=f'請問藥品的類型是？',
                actions=[
                    MessageAction(label='藥',text='藥'),
                    MessageAction(label='保健食品', text='保健食品')
                ]
            )
        theMenu.columns.append(MenuItem_0)
        self.bot_api.reply_message(event.reply_token,TemplateSendMessage(alt_text="藥品類型輸入\n（電腦版可能無法顯示請直接輸入名稱）", template=theMenu))
        self.userstat.SetUserStatus(user_id,"notify_0_3",self.userstat.GetUserTmpValue(user_id))
    pass

    # 提醒步驟 0-3 - 收到藥品類型
    def notify_0_3(self,event):
        _msg = event.message.text # 傳入的訊息
        user_id = event.source.user_id # 使用者的內部id
        theName = self.userstat.GetUserTmpValue(user_id)
        self.db_manager.execute(f"Update UserMedicine Set MedType = '{_msg}' Where UserID = '{user_id}' and MedicineName = '{theName}'")
        self.userstat.SetUserStatus(user_id,"notify_1_1",theName)
        self.notify_1_0(event)
    pass

    # 提醒步驟 1-0 - 詢問目前藥品數量
    def notify_1_0(self,event):
        self.bot_api.reply_message(event.reply_token,TextSendMessage(text="請問現在這個藥有多少（幾包）？\n麻煩請用畫面左下的鍵盤按鈕打字讓我看看！"))
    pass

    # 提醒步驟 1-1 - 收到藥品目前數量
    def notify_1_1(self,event):
        _msg = event.message.text # 傳入的訊息
        user_id = event.source.user_id # 使用者的內部id
        try: 
            theAmount = int(_msg)
            theName = self.userstat.GetUserTmpValue(user_id)
            self.db_manager.execute(f"Update UserMedicine Set Amount = {theAmount} Where UserID = '{user_id}' and MedicineName = '{theName}'")
            self.userstat.SetUserStatus(user_id,"notify_2_1",theName)
            self.notify_2_0(event)
        except ValueError:
            self.bot_api.reply_message(event.reply_token,TextSendMessage(text="不好意思，請幫我打入正確的數字，謝謝。"))
        pass
    pass

    # 提醒步驟 2-0 - 詢問一次都吃多少
    def notify_2_0(self,event):
        self.bot_api.reply_message(event.reply_token,TextSendMessage(text="請問一次都吃多少（一次幾包）？\n麻煩請用畫面左下的鍵盤按鈕打字讓我看看！"))
    pass

    # 提醒步驟 2-1 - 收到一次服用數量
    def notify_2_1(self,event):
        _msg = event.message.text # 傳入的訊息
        user_id = event.source.user_id # 使用者的內部id
        try: 
            theAmount = int(_msg)
            if theAmount <= 0:
                raise ValueError("less or equal to zero...")
            pass
            theName = self.userstat.GetUserTmpValue(user_id)
            self.db_manager.execute(f"Update UserMedicine Set TakeAmount = {theAmount} Where UserID = '{user_id}' and MedicineName = '{theName}'")
            self.notify_2_2(event)
            self.userstat.SetUserStatus(user_id,"notify_2_3",theName)
        except ValueError:
            self.bot_api.reply_message(event.reply_token,TextSendMessage(text="不好意思，請幫我打入正確的數字，謝謝。"))
        pass
    pass
    
    # 提醒步驟 2-2 - 詢問吃藥時間　
    # 三餐飯前（6:30,11:30,17:30)
    # 三餐飯後（7:50,13:20,19:00）
    # 睡前 (21:00)
    # 或是自訂
    def notify_2_2(self,event):
        user_id = event.source.user_id # 使用者的內部id
        theMenu = CarouselTemplate(columns=[])
    
        MenuItem_0 = CarouselColumn(
                thumbnail_image_url="https://i.imgur.com/tyoj3xL.png",
                title=f'設定吃藥時間',
                text=f'三餐飯前（6:30,11:30,17:30)',
                actions=[
                    MessageAction(label='送出',text='三餐飯前')
                ]
            )
        theMenu.columns.append(MenuItem_0)
        MenuItem_1 = CarouselColumn(
                thumbnail_image_url="https://i.imgur.com/tyoj3xL.png",
                title=f'設定吃藥時間',
                text=f'三餐飯後（7:50,13:20,19:00）',
                actions=[
                    MessageAction(label='送出',text='三餐飯後')
                ]
            )
        theMenu.columns.append(MenuItem_1)
        MenuItem_2 = CarouselColumn(
                thumbnail_image_url="https://i.imgur.com/tyoj3xL.png",
                title=f'設定吃藥時間',
                text=f'睡前 (21:00)',
                actions=[
                    MessageAction(label='送出',text='睡前')
                ]
            )
        theMenu.columns.append(MenuItem_2)
        MenuItem_3 = CarouselColumn(
                thumbnail_image_url="https://i.imgur.com/tyoj3xL.png",
                title=f'設定吃藥時間',
                text=f'自訂',
                actions=[
                    MessageAction(label='送出',text='自訂')
                ]
            )
        theMenu.columns.append(MenuItem_3)

        self.bot_api.reply_message(event.reply_token,TemplateSendMessage(alt_text="提醒時間輸入\n（電腦版可能無法顯示請直接輸入\"自訂\"）", template=theMenu))
    pass

    # 提醒步驟 2-3 - 收到吃藥時間
    # 依據送出訊息做相對應提醒設定或者
    # 如果選擇自訂時間則繼續下面步驟
    # 否則結束並設定完成　
    def notify_2_3(self,event):
        _msg = event.message.text # 傳入的訊息
        user_id = event.source.user_id # 使用者的內部id
        theName = self.userstat.GetUserTmpValue(user_id)
        if _msg == "三餐飯前": # 三餐飯前（6:30,11:30,17:30)
            notify_times = {"06:30","11:30","17:30"}
            for _t in notify_times:
                self.db_manager.execute(f"Insert Into Notify(UserID,Description,TargetMedicine,TargetTime,LastNotifyDate,TakeDate) Values('{user_id}','','{theName}','{_t}','','尚未吃過藥')")
            pass
            self.userstat.SetUserStatus(user_id,"","")
            self.bot_api.reply_message(event.reply_token,TextSendMessage(text=f"吃藥時間：{_msg}\n設定完成。"))
        elif _msg == "三餐飯後": # 三餐飯後（7:50,13:20,19:00）
            notify_times = {"07:50","13:20","19:00"}
            for _t in notify_times:
                self.db_manager.execute(f"Insert Into Notify(UserID,Description,TargetMedicine,TargetTime,LastNotifyDate,TakeDate) Values('{user_id}','','{theName}','{_t}','','尚未吃過藥')")
            pass
            self.userstat.SetUserStatus(user_id,"","")
            self.bot_api.reply_message(event.reply_token,TextSendMessage(text=f"吃藥時間：{_msg}\n設定完成。"))
        elif _msg == "睡前": # 睡前 (21:00)
            notify_times = {"21:00"}
            for _t in notify_times:
                self.db_manager.execute(f"Insert Into Notify(UserID,Description,TargetMedicine,TargetTime,LastNotifyDate,TakeDate) Values('{user_id}','','{theName}','{_t}','','尚未吃過藥')")
            pass
            self.userstat.SetUserStatus(user_id,"","")
            self.bot_api.reply_message(event.reply_token,TextSendMessage(text=f"吃藥時間：{_msg}\n設定完成。"))
        else: # 自訂            
            self.notify_3_0(event)
            self.userstat.SetUserStatus(user_id,"notify_3_1",theName)
        pass
    pass

    # 提醒步驟 3-0 - 詢問幾次
    def notify_3_0(self,event):
        self.bot_api.reply_message(event.reply_token,TextSendMessage(text="請問一天要提醒幾次？\n麻煩請用畫面左下的鍵盤按鈕打字讓我看看！"))
    pass

    # 提醒步驟 3-1 - 收到一天幾次
    def notify_3_1(self,event):
        _msg = event.message.text # 傳入的訊息
        user_id = event.source.user_id # 使用者的內部id
        try: 
            theAmount = int(_msg)
            if theAmount <= 0:
                raise ValueError("less or equal to zero...")
            pass
            theName = self.userstat.GetUserTmpValue(user_id)
            # tmpvalue now : 藥品名稱；提醒次數；已經設定完成的次數
            self.userstat.SetUserStatus(user_id,"notify_4_1",f"{theName};{theAmount};1")
            self.notify_4_0(event)
        except ValueError:
            self.bot_api.reply_message(event.reply_token,TextSendMessage(text="不好意思，請幫我打入正確的數字，謝謝。"))
        pass
    pass

    def notify_4_0(self,event):
        user_id = event.source.user_id # 使用者的內部id
        tmp_values = self.userstat.GetUserTmpValue(user_id).split(";")
        now_set_times = int(tmp_values[2])
        date_picker = TemplateSendMessage(
            alt_text='幾點吃藥',
            template=ButtonsTemplate(
                text='請設定幾點要吃藥',
                title=f'設定第{now_set_times}次吃藥時間',
                actions=[
                    DatetimePickerTemplateAction(
                        label='選擇時間',
                        data='action=buy&itemid=1',
                        mode='time',
                        max='23:59',
                        min='00:00',
                        initial='00:00'
                    )
                ]
            )
        )
        self.bot_api.reply_message(event.reply_token,date_picker)
    pass

    # 提醒步驟 4-1 - 收到時間如果還有其他次沒設定就回到上一步驟再次設定時間
    def notify_4_1(self,event):
        user_id = event.source.user_id # 使用者的內部id
        tmp_values = self.userstat.GetUserTmpValue(user_id).split(";")
        theName = tmp_values[0]
        target_set_times = int(tmp_values[1])
        now_set_times = int(tmp_values[2]) + 1

        # 上次設定的時間
        notify_time = event.postback.params['time']
        self.db_manager.execute(f"Insert Into Notify(UserID,Description,TargetMedicine,TargetTime,LastNotifyDate,TakeDate) Values('{user_id}','','{theName}','{notify_time}','','尚未吃過藥')")

        if now_set_times <= target_set_times:
            self.userstat.SetUserStatus(user_id,"notify_4_1",f"{theName};{target_set_times};{now_set_times}")
            self.notify_4_0(event)
        else:
            self.userstat.SetUserStatus(user_id,"","")
            self.bot_api.reply_message(event.reply_token,TextSendMessage(text="設定完成。"))
        pass
    pass

pass