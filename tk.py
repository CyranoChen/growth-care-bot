import tkinter as tk
from time import strftime

root = tk.Tk()
root.attributes('-fullscreen', True)
root.configure(bg='black')

label = tk.Label(root, font=('Arial', 40), fg='white', bg='black')
label.pack(expand=True)

def update_time():
    label.config(text=strftime('%H:%M:%S'))
    root.after(1000, update_time)

update_time()
root.mainloop()