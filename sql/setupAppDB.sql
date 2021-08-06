-- 使用者藥品表
--Drop Table If Exists UserMedicine;
Create Table If Not Exists UserMedicine
(
    ID int GENERATED ALWAYS AS IDENTITY Primary Key,
    UserID varchar(1024),
    MedicineName varchar(1024),
    Amount int,
    TakeAmount int
);

-- 提醒時間表
--Drop Table If Exists Notify;
Create Table If Not Exists Notify 
(
    ID int GENERATED ALWAYS AS IDENTITY Primary Key,
    UserID varchar(1024),
    Description text,
    TargetMedicine varchar(1024),
    TargetTime varchar(128),
    LastNotifyDate varchar(512),
    TakeDate varchar(512)
);

-- 吃藥紀錄表
--Drop Table If Exists TakeMedicineHistory;
Create Table If Not Exists TakeMedicineHistory 
(
    ID int GENERATED ALWAYS AS IDENTITY Primary Key,
    UserID varchar(1024),
    Description text,
    AnwTime varchar(128)
);

-- 使用者狀態表
--Drop Table If Exists UserStatus;
Create Table If Not Exists UserStatus 
(
    UserID varchar(1024) Primary Key,
    Stat varchar(1024),
    TempValue text
);