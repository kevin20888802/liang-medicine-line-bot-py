from datetime import datetime
import time
 
a = datetime.now() #获得当前时间
time.sleep(2)      #睡眠两秒
b = datetime.now()  # 获取当前时间
durn = int((a-b).total_seconds() / 60)  #两个时间差，并以秒显示出来
print(durn)
 
timeshow = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))  #获取当前时间 ，并以当前格式显示
print(timeshow)