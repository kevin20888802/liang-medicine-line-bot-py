from .act_notify import NotifyActions
from .act_takemedicine import TakeMedicineActions
from .act_showtakehistory import ShowTakeActions
from .act_shownotify import ShowNotifyActions
from .act_showmap import ShowMapActions
from .act_finddrug import FindDrugActions
from .act_hospital import HospitalActions
from .act_addhealthstat import AddHealthStatActions
from .act_showhealthstat import ShowHealthStatActions
from .act_showcamera import ShowCamera
from .db_manager import PostgresBaseManager as dbm

class User_Status_Manager:

    def __init__(self,DBmanager,botapi):
        self.db_manager = DBmanager
        self.line_bot_api = botapi
        self.notifyActs = NotifyActions(DBmanager,botapi,self)
        self.takeMedActs = TakeMedicineActions(DBmanager,botapi,self)
        self.showtakeActs = ShowTakeActions(DBmanager,botapi,self)
        self.showNotifyActions = ShowNotifyActions(DBmanager,botapi,self)
        self.showMapActions = ShowMapActions(DBmanager,botapi,self)
        self.findDrugActions = FindDrugActions(DBmanager,botapi,self)
        self.hospitalActions = HospitalActions(DBmanager,botapi,self)
        self.addHealthStatActions = AddHealthStatActions(DBmanager,botapi,self)
        self.showHealthStatActions = ShowHealthStatActions(DBmanager,botapi,self)
        self.showCamera = ShowCamera(DBmanager,botapi,self)
        self.statActions = {
            "notify_0_0":self.notifyActs.notify_0_0,
            "notify_0_1":self.notifyActs.notify_0_1,
            "notify_0_2":self.notifyActs.notify_0_2,
            "notify_0_3":self.notifyActs.notify_0_3,
            "notify_1_0":self.notifyActs.notify_1_0,
            "notify_1_1":self.notifyActs.notify_1_1,
            "notify_2_1":self.notifyActs.notify_2_1,
            "notify_2_3":self.notifyActs.notify_2_3,
            "notify_3_1":self.notifyActs.notify_3_1,
            "notify_4_1":self.notifyActs.notify_4_1,
            "takemed_0_0":self.takeMedActs.takemed_0_0,
            "takemed_0_1":self.takeMedActs.takemed_0_1,
            "showtakehistory":self.showtakeActs.showtakehistory,
            "shownotify_0_0":self.showNotifyActions.shownotify_0_0,
            "shownotify_0_1":self.showNotifyActions.shownotify_0_1,
            "showmap":self.showMapActions.showmap,
            "finddrug_0":self.findDrugActions.finddrug_0,
            "finddrug_1":self.findDrugActions.finddrug_1,
            "showhospital":self.hospitalActions.ShowHospital,
            "addhealthstat_0":self.addHealthStatActions.addhealthstat_0,
            "addhealthstat_1":self.addHealthStatActions.addhealthstat_1,
            "addhealthstat_2":self.addHealthStatActions.addhealthstat_2,
            "showhealthstat_0":self.showHealthStatActions.showhealthstat_0,
            "showhealthstat_1":self.showHealthStatActions.showhealthstat_1,
            "showcamera":self.showCamera.showcamera
        }
    pass

    # ?????????????????????
    def SetUserStatus(self,userid,stat,tmpval):
        self.db_manager.execute(f"Insert Into UserStatus(UserID, Stat) values ('{userid}', '') on conflict (UserID) do nothing;")
        self.db_manager.execute(f"Update UserStatus Set Stat = '{stat}' Where UserID = '{userid}'")
        if tmpval != None:
            self.db_manager.execute(f"Update UserStatus Set TempValue = '{tmpval}' Where UserID = '{userid}'")
        pass
    pass

    # ?????????????????????
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

    # ???????????????????????????
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

    # ?????????????????????????????????????????????
    def UserStatusExecute(self,event):
        user_id = event.source.user_id # ??????????????????id
        theStatus = self.GetUserStatus(user_id) # ?????????????????????
        print(theStatus)
        if theStatus in self.statActions:
            self.statActions[theStatus](event)
        pass
    pass

pass