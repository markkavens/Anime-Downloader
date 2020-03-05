from tkinter import ttk
from tkinter import *
import time
import requests
import os
from tkinter import messagebox as m_box
import re

win = Tk()
win.title("Anime Downloader")
win.geometry("400x360")
win.minsize(400,360)
win.maxsize(400,360)
frame = ttk.LabelFrame(win, width=300)
frame.pack(padx=30, pady=20)
label1 = ttk.Label(frame, text="Enter The File URL : ")
label1.grid(row=0, column=0,sticky=W)
url = StringVar()
edit_txt = ttk.Entry(frame, width=50, textvariable=url)
edit_txt.grid(row=1, columnspan=4, padx=2, pady=3)
pb = ttk.Progressbar(win, orient="horizontal", length=300, mode="determinate")
pb.pack()
pb.start()
text = Text(win, height=20, width=40)
scroll = Scrollbar(win, command=text.yview)
text.configure(yscrollcommand=scroll.set)
text.pack(padx=30, pady=30)
scroll.pack(side=RIGHT, fill=Y)

def edit():
    pass

def onClick():
    pass

btn1 = ttk.Button(frame, text="Download", command=edit)
btn1.grid(row=4, column=0, pady=5)
btn2 = ttk.Button(frame, text="Stop", command=onClick)
btn2.grid(row=4, column=2, pady=5)
win.mainloop()