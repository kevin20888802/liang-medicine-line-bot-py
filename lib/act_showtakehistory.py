from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, PostbackEvent, TextMessage, TextSendMessage,)

class ShowTakeActions:

    def __init__(self,DBmanager,botapi,userstats):
        self.db_manager = DBmanager
        self.bot_api = botapi
        self.userstat = userstats
    pass

    # 顯示吃藥紀錄步驟0 - 顯示吃藥紀錄
    def showtakehistory(self,event):
        user_id = event.source.user_id # 使用者的內部id
        result = self.db_manager.execute(f"Select * From TakeMedicineHistory Where UserID = '{user_id}'")
        _msg = ""
        if result != None:
            for row in result:
                _msg += f"--------------------\n{row[2]}\n"
            pass
        pass
        if _msg == "":
            _msg = "尚無任何吃藥紀錄"
        pass
        self.bot_api.reply_message(event.reply_token,TextSendMessage(text=f"以下是您的吃藥紀錄\n\n{_msg}"))
        self.userstat.SetUserStatus(user_id,"","")
    pass

pass