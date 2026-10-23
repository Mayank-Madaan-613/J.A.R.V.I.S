import nltk 
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression 
import joblib
df=pd.read_csv("ds.csv")
corpus=df["command"].to_list()
y=df["intent"].to_list()
vectorizer=TfidfVectorizer()
x=vectorizer.fit_transform(corpus)
model=LogisticRegression()
model.fit(x,y)
joblib.dump(model,"intent_model.pkl")
joblib.dump(vectorizer,"vectorizer.pkl")
print("model saved")


