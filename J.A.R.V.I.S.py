from PIL import Image

def trim_whitespace(img_path, save_as):
    img = Image.open(img_path)
    img = img.convert("RGBA")          # ensure transparency support
    # get bounding box of non-empty pixels
    bbox = img.getbbox()
    # crop to that box
    trimmed = img.crop(bbox)
    trimmed.save(save_as)
    return trimmed

trim_whitespace("microphone.png", "microphone_trimmed.png")
import customtkinter as ct
from PIL import Image
from customtkinter import CTkImage
img=Image.open('macos-big-sur-apple-layers-fluidic-colorful-wwdc-stock-3840x2160-1455.jpg')
app = ct.CTk()
app.geometry("400x500")
app.grid_columnconfigure((0,1,2),weight=1)
app.grid_rowconfigure((0,1,2),weight=1)
bg_label=ct.CTkLabel(app,text='',image=ct.CTkImage(img,size=(400,500)))
bg_label.place(x=0,y=0,relwidth=1,relheight=1)
# load trimmed mic
mic_img = Image.open("microphone_trimmed.png")

mic_icon = CTkImage(mic_img, size=(40,40))
btn = ct.CTkButton(app, text='', image=mic_icon)
btn.grid(row=1, column=1)

app.mainloop()
