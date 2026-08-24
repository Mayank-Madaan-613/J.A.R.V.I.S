
import joblib 

class Predict:
    def __init__(self):
        self.model=joblib.load("intent_model.pkl")
        self.vectorizer=joblib.load("vectorizer.pkl")
    def predict(self,inp):
        vector=self.vectorizer.transform([inp])
        prediction=self.model.predict(vector)
        return prediction[0]

cmd="wave silicon systems"
obj=Predict()
print(obj.predict(cmd))