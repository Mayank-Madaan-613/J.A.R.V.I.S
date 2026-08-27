import time
from datetime import datetime
import re

class Clock:
    def time_rn(self):
        time_curr=time.time()
        dt_obj=datetime.fromtimestamp(time_curr)
        time_curr=dt_obj.strftime("%I %M %p")
        return time_curr
    def timmer(self,user_time):

        pattern = re.compile(
    r"(?:(?P<hr>\d+)\s*(?:hours?|hour?))?[^\d]*"
    r"(?:(?P<min>\d+)\s*(?:minutes?|minute?))?[^\d]*"
    r"(?:(?P<sec>\d+)\s*(?:seconds?|second|sec|secs?))?"
)
        
        match=pattern.match(user_time)
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
        timmer_init=time.time()
        while(True):
            if int(time.time())-timmer_init >=counter_time:
                print("times up!")
                break
a=Clock()
print(a.timmer("2 hours and 10 seconds"))