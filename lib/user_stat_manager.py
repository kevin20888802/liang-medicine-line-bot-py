from .act_notify import NotifyActions
from .act_takemedicine import TakeMedicineActions
from .act_showtakehistory import ShowTakeActions
from .act_shownotify import ShowNotifyActions
from .act_showmap import ShowMapActions
from .act_finddrug import FindDrugActions
from .db_manager import PostgresBaseManager as dbm


class User_Status_Manager:

    def __init__(self,DBmanager,botapi):
        self.db_manager = DBmanager
        self.line_bot_api = botapi
        notifyActs = NotifyActions(DBmanager,botapi,self)
        takeMedActs = TakeMedicineActions(DBmanager,botapi,self)
        showtakeActs = ShowTakeActions(DBmanager,botapi,self)
        showNotifyActions = ShowNotifyActions(DBmanager,botapi,self)
        showMapActions = ShowMapActions(DBmanager,botapi,self)
        findDrugActions = FindDrugActions(DBmanager,botapi,self)
        self.statActions = {
            "notify_0_0":notifyActs.notify_0_0,
            "notify_0_1":notifyActs.notify_0_1,
            "notify_0_2":notifyActs.notify_0_2,
            "notify_0_3":notifyActs.notify_0_3,
            "notify_1_0":notifyActs.notify_1_0,
            "notify_1_1":notifyActs.notify_1_1,
            "notify_2_1":notifyActs.notify_2_1,
            "notify_2_3":notifyActs.notify_2_3,
            "notify_3_1":notifyActs.notify_3_1,
            "notify_4_1":notifyActs.notify_4_1,
            "takemed_0_0":takeMedActs.takemed_0_0,
            "takemed_0_1":takeMedActs.takemed_0_1,
            "showtakehistory":showtakeActs.showtakehistory,
            "shownotify_0_0":showNotifyActions.shownotify_0_0,
            "shownotify_0_1":showNotifyActions.shownotify_0_1,
            "showmap":showMapActions.showmap,
            "finddrug_0":findDrugActions.finddrug_0,
            "finddrug_1":findDrugActions.finddrug_1
        }
    pass

    # 設定使用者狀態
    def SetUserStatus(self,userid,stat,tmpval):
        self.db_manager.execute(f"Insert Into UserStatus(UserID, Stat) values ('{userid}', '') on conflict (UserID) do nothing;")
        self.db_manager.execute(f"Update UserStatus Set Stat = '{stat}' Where UserID = '{userid}'")
        if tmpval != None:
            self.db_manager.execute(f"Update UserStatus Set TempValue = '{tmpval}' Where UserID = '{userid}'")
        pass
    pass

    # 取得使用者狀態
    def GetUserStatus(self,userid):
        result = self.db_manager.execute(f"Select * From UserStatus Where UserID = '{userid}'")
        if result != None:
            for stat in result:
                print(stat)
                return stat[1]
            pass
        else:
            print(f"can't find user status : userid={userid}")
        pass
    pass

    # 取得使用者暫存數值
    def GetUserTmpValue(self,userid):
        result = self.db_manager.execute(f"Select * From UserStatus Where UserID = '{userid}'")
        if result != None:
            for stat in result:
                print(stat)
                return stat[2]
            pass
        else:
            print(f"can't find user status : userid={userid}")
        pass
    pass

    # 根據使用者目前狀態執行對應動作
    def UserStatusExecute(self,event):
        user_id = event.source.user_id # 使用者的內部id
        theStatus = self.GetUserStatus(user_id) # 使用者目前狀態
        print(theStatus)
        if theStatus in self.statActions:
            self.statActions[theStatus](event)
        pass
    pass

pass