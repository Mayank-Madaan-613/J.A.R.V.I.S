from dotenv import load_dotenv
from google import genai
import os
load_dotenv()
class gemini:
    response=""
    def __init__(self,ques):
        api_key=os.getenv("API_Gemini_key")
        gem_obj=genai.Client(api_key=api_key)
        querry=ques+"?"+"explain extrermely short"
        response=gem_obj.models.generate_content(model="gemini-3-flash-preview",contents=querry)
        out=response.text 
        final_response=""
        for i in out:
            if i not in "*-#.!":
                final_response+=i
        self.response=final_response

