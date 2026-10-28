import time
from datetime import datetime
import re
import threading
class Clock:
    def time_rn(self):
        time_curr=time.time()
        dt_obj=datetime.fromtimestamp(time_curr)
        time_curr=dt_obj.strftime("%I %M %p")
        return time_curr
    def timer(self,counter_time):
            time.sleep(counter_time)
            print("times up!")
    def timer_call(self,query):
        pattern = re.compile(
            r"(?:(?P<hr>\d+)\s*(?:hours?|hour|hr?))?[^\d]*"
            r"(?:(?P<min>\d+)\s*(?:minutes?|minute|min?))?[^\d]*"
            r"(?:(?P<sec>\d+)\s*(?:seconds?|second|sec|secs?))?"
        )
        match=pattern.match(query)
        time_dict=match.groupdict()
        counter_time=0
        for x,y in time_dict.items():
            if y is None:
                time_dict[x]=0
        print(time_dict)
        for x,y in time_dict.items():
            if x=="min":
                counter_time+=int(y)*60
            if x=="hr":
                counter_time+=int(y)*3600
        counter_time+=int(time_dict["sec"])
        print(counter_time)
        threading.Thread(target=self.timer,args=(counter_time,),daemon=True).start()
        
