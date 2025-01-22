import tkinter as tk
from tkinter import messagebox

def check_order():
    if order == correct_order:
        messagebox.showinfo("Success", "Correct order!")
        reset()
    else:
        messagebox.showerror("Error", "Incorrect order! Restarting...")
        reset()

def reset():
    global order
    order = []
    for button in buttons:
        button.config(bg="#f0f0f0")

def button_click(num, button):
    if len(order) < len(correct_order) and num == correct_order[len(order)]:
        order.append(num)
        button.config(bg='green')
        if len(order) == len(correct_order):
            check_order()

    else:
        button.config(bg="red")
        messagebox.showerror("Error", "Incorrect order! Restarting...")
        reset()


####################################     Main       ####################################

# Create the window
root = tk.Tk()
root.geometry('500x400')
# Set correct order
correct_order = [1, 2, 3]
# Place in the current order
order = []
# Create button list
buttons = []

# Create buttons
for i in range(1, 4):
    button = tk.Button(root,text=f"Button {i}")
    button.config(command=lambda i=i, b=button: button_click(i,b),
                    height=5,
                    width=15
                    )
    button.pack(padx=20, pady=20)
    buttons.append(button)

root.mainloop()