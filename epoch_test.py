from datetime import datetime, time
now = datetime.now()
now_time = now.time()
if now_time >= time(10,30) and now_time <= time(16,30):
    print "yes, within the interval"