# import customtkinter as ct
# from utility import main
# from PIL import Image
# from customtkinter import CTkImage
# img=Image.open('power.png')
# app=ct.CTk()
# bg=Image.open('ChatGPT Image Nov 18, 2025, 11_13_25 AM.png')
# app.title('JARVIS')
# app.geometry('400x500')
# app.grid_columnconfigure((0,1,2),weight=1)
# app.grid_rowconfigure((0,1,2),weight=1)
# back=ct.CTkImage(bg,size=(400,500))
# back_label=ct.CTkLabel(app,text='',image=back)
# back_label.place(x=0,y=0,relwidth=1,relheight=1)
# frame = ct.CTkFrame(app,fg_color="transparent").place()
# label_something = ct.CTkLabel(frame,text='Tap to speak', font=("Segoe UI", 24))
# label_something.place()
# speak_btn=ct.CTkButton(app,text='',image=CTkImage(img,size=(40,40)),width=50,height=50,command=main,fg_color='white',hover_color='white')
# speak_btn.grid(row=1,column=1,padx=20,pady=20)
# app.mainloop()
# # import customtkinter


# # def button_callback():
# #     print("button pressed")

# # app = customtkinter.CTk()
# # app.title("my app")
# # app.geometry("400x150")

# # button = customtkinter.CTkButton(app, text="my button", command=button_callback)
# # button.grid(row=0, column=0, padx=20, pady=20)

# # app.mainloop()

from ursina import *

app = Ursina()

car = Entity(model='cube', color=color.red, scale=(2,1,4), position=(0,0,0))

def update():
    if held_keys['w']:
        car.z -= 0.1
    if held_keys['s']:
        car.z += 0.1
    if held_keys['a']:
        car.x -= 0.1
    if held_keys['d']:
        car.x += 0.1

app.run()
