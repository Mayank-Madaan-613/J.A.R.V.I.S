import openvino_genai as genai
from openvino import Core
import time

core=Core()
prompt="Explain vision transformers in simple words"
model="C:/OpenVINO-LLM/llama3.2-1b-q8_0.gguf"
def infer_device(device):
    print("="*35)
    print("Test Device: ",device)
    print("="*35)
    try:
        st_load=time.perf_counter()
        pipe=genai.LLMPipeline(model,device)
        load_time=time.perf_counter()-st_load
        config=genai.GenerationConfig()
        config.max_new_tokens=100
        start=time.perf_counter()
        res=pipe.generate(prompt,config)
        elapsed=time.perf_counter()-start
        print("Response:\n",res)
        print(f"Loading Time: {round(load_time,2)}")
        print(f"inference Time: {round(elapsed,2)}")
    except Exception as e:
        print(f"Error Occured while loading and inferencing: {str(e)}")
test_device="CPU"
infer_device(test_device)
test_device="GPU"
infer_device(test_device)



