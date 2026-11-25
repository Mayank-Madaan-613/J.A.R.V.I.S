from ollama import chat
from ollama import ChatResponse
stream= chat(
  model='llama3.2:1b',
  messages=[{'role': 'user','content':'how to study deep learning.'}],stream=True)
for chunk in stream:
    print(chunk["message"]["content"],end="",flush=True)