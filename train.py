import nltk 
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression 
import joblib

corpus=['open youtube','launch youtube','what time is it ?','time right now ?','set timmer for 10 minutes','put a timmer for 20 seconds','where is agra ?','distance between agra and delhi','how to study python?','send a whatsapp message to aman that says hello there!',"send a message on whatapp to rahul saying bye"]
vectorizer=TfidfVectorizer()
x=vectorizer.fit_transform(corpus)
y=["open_app","open_app","time_rn","time_rn","timer","timer","web_search","web_search","web_search","web_open","what_msg","what_msg"]
model=LogisticRegression()
model.fit(x,y)
joblib.dump(model,"intent_model.pkl")
joblib.dump(vectorizer,"vectorizer.pkl")
print("model saved")


