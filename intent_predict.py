
import joblib 

class Predict:
    def __init__(self):
        self.model=joblib.load("intent_model.pkl")
        self.vectorizer=joblib.load("vectorizer.pkl")
    def predict(self,inp):
        vector=self.vectorizer.transform([inp])
        prediction=self.model.predict(vector)
        return prediction[0]
    
if __name__=="__main__":
    #test
    cmds=["fire up visual studio code real quick",
    "can you check what time is it in mumbai right now",
    "put a timmer for fifteen minutes and thirty seconds",
    "google search how to fix a memory leak in python",
    "send a msg on what's app to ankit that says call me back urgent",
    "what is forty five times twelve divided by six",
    "turn on computer vision hand tracking mode",
    "start up the camera application",
    "do you have the current time please",
    "set a countdown for forty five seconds",
    "look up distance between delhi and jaipur on the web",
    "tell mom on whatapp that i reached home safely",
    "calculate eighteen percent tax on twelve hundred dollars",
    "disable hand gesture navigation",
    "launch task manager",
    "what does the clock say right now",
    "run a timer for two hours",
    "who won the match yesterday search online",
    "text rahul on whatsapp saying meeting is postponed",
    "what is two to the power of eight",
    "activate vision gestures",
    "switch to spotify",
    "search for best budget wireless earbuds in 2026",
    "whatsapp papa that i will be late for dinner",
    "square root of six hundred twenty five"]
    
    out=["open_app", "time_rn", "timer", "web_search", "what_msg", "calculate", "gesture_mode",
    "open_app", "time_rn", "timer", "web_search", "what_msg", "calculate", "gesture_mode",
    "open_app", "time_rn", "timer", "web_search", "what_msg", "calculate", "gesture_mode",
    "open_app", "web_search", "what_msg", "calculate"]
    flag=True
    obj=Predict()
    for i,j in zip(cmds,out):
        a=obj.predict(i)
        if a!=j:flag=False
        print(a)

