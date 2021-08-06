from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, PostbackEvent, TextMessage, TextSendMessage,TemplateSendMessage, ButtonsTemplate, DatetimePickerTemplateAction,)

class NotifyActions:

    def __init__(self,DBmanager,botapi,userstats):
        self.db_manager = DBmanager
        self.bot_api = botapi
        self.userstat = userstats
    pass

    # 提醒步驟 0-0 - 詢問藥名
    def notify_0_0(self,event):
        user_id = event.source.user_id # 使用者的內部id
        self.bot_api.reply_message(event.reply_token,TextSendMessage(text="請問您吃的藥是（全部的藥）？\n麻煩請用畫面左下的鍵盤按鈕打字讓我看看！"))
        self.userstat.SetUserStatus(user_id,"notify_0_1","")
    pass

    # 提醒步驟 0-1 - 收到藥名
    def notify_0_1(self,event):  
        _msg = event.message.text.replace(";","") # 傳入的訊息+過濾分割用字元
        user_id = event.source.user_id # 使用者的內部id
        
        # 在使用者藥品表增加使用者的藥名如果沒有的話 (數量先設定為0如果是新的藥品)
        findCount = self.db_manager.execute(f"Select Count(*) From UserMedicine Where UserID = '{user_id}' and MedicineName = '{_msg}'") 
        #print(findCount)
        if findCount == None or findCount[0][0] <= 0:
            self.db_manager.execute(f"Insert Into UserMedicine(UserID,MedicineName,Amount,TakeAmount) Values('{user_id}','{_msg}',0,1)")
        pass

        self.userstat.SetUserStatus(user_id,"notify_1_1",_msg)
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
            self.notify_3_0(event)
            self.userstat.SetUserStatus(user_id,"notify_3_1",theName)
        except ValueError:
            self.bot_api.reply_message(event.reply_token,TextSendMessage(text="不好意思，請幫我打入正確的數字，謝謝。"))
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

    # 提醒步驟 4-0 - 針對每一次詢問吃藥時間
    def notify_4_0(self,event):
        user_id = event.source.user_id # 使用者的內部id

        tmp_values = self.userstat.GetUserTmpValue(user_id).split(";")
        theName = tmp_values[0]
        target_set_times = int(tmp_values[1])
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