from dotenv import load_dotenv
from google import genai
import os
load_dotenv()
def AI_search(ques):
    api_key=os.getenv("API_Gemini_key")
    gem_obj=genai.Client(api_key=api_key)
    querry=ques+"?"+"explain in hardly 3 lines"
    response=gem_obj.models.generate_content(model="gemini-3-flash-preview",contents=querry)
    out=response.text    
    return out