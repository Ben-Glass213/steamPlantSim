import tkinter as tk
from tkinter import Toplevel, messagebox
import pygame

# Initialize pygame mixer
pygame.mixer.init()

# Load the switch sound and alarm sound
switch_sound = pygame.mixer.Sound("switchOn.wav")
alarm_sound = pygame.mixer.Sound("alarmSound.wav")

def play_sound():
    switch_sound.play()

def play_alarm():
    alarm_sound.play(loops=-1)  # Loop the alarm sound indefinitely

def stop_alarm():
    alarm_sound.stop()  # Stop the alarm sound

def check_order():
    if order == correct_order:
        messagebox.showinfo("Success", "Correct order!")
        reset()
    else:
        messagebox.showerror("Error", "Incorrect order! Restarting...")
        reset()

def reset():
    global order, flashing
    order = []
    flashing = False
    stop_alarm()  # Stop the alarm sound when resetting
    for button in buttons:
        button.config(bg="SystemButtonFace")  # Reset button color to default

def retry():
    global flashing
    flashing = False
    stop_alarm()  # Stop the alarm sound when retrying
    if last_incorrect_button:
        last_incorrect_button.config(bg="SystemButtonFace")  # Reset the incorrect button color to default
    for name in order:
        index = button_names.index(name)
        buttons[index].config(bg="green")  # Set the correct buttons back to green
    retry_button.pack_forget()  # Hide the retry button after retrying

def flash_button(button):
    if flashing:
        current_color = button.cget("bg")
        next_color = "SystemButtonFace" if current_color == "red" else "red"
        button.config(bg=next_color)
        button.after(500, lambda: flash_button(button))  # Continue flashing every 500ms

def show_retry_window():
    retry_window = Toplevel(root)
    retry_window.title("Incorrect Order")
    retry_window.geometry("300x150")
    tk.Label(retry_window, text="Incorrect order! Try again...").pack(pady=10)
    tk.Button(retry_window, text="Go Back", command=lambda: [retry(), retry_window.destroy()]).pack(pady=5)
    tk.Button(retry_window, text="Reset", command=lambda: [reset(), retry_window.destroy()]).pack(pady=5)
    retry_window.grab_set()  # Make the retry window modal

def button_click(name, button):
    global last_incorrect_button, flashing
    play_sound()  # Play sound on button click
    if order and name == order[-1]:  # Check if the button is the last one in the order
        order.pop()
        button.config(bg="SystemButtonFace")  # Change the button color back to default if unselected
    else:
        if len(order) < len(correct_order) and name == correct_order[len(order)]:
            order.append(name)
            button.config(bg="green")  # Change the specific button color to green if correct
            if len(order) == len(correct_order):
                check_order()
        else:
            last_incorrect_button = button  # Store the reference to the incorrect button
            flashing = True
            flash_button(button)  # Start flashing the button
            play_alarm()  # Play the alarm sound
            show_retry_window()  # Show the custom retry window

############################ CREATE INSTANCE OF WINDOW ############################

root = tk.Tk()
root.title("QUB Steam Plant Simulator")
root.geometry('600x650')  # Adjusted to accommodate more buttons

################################## MAIN METHOD ##################################

button_names = [
    "V1", "V3", "V4", "V2", "P1", "P2", "V5", "V6", "P3", "F2", "V9", "F1",
    "V7", "V8", "P4", "F4", "V14", "F3", "V12", "V13", "P5", "V17", "V18", "P6",
    "V19", "V20", "V16", "V15", "V10", "P7", "V28", "V29", "P12", "V24", "V25",
    "P9", "V26", "V27", "P11", "V30", "P10", "V22", "V23", "V21", "P8", "V11"
]
correct_order = button_names[:]  # The correct order is the same as the button names list
order = []
buttons = []
last_incorrect_button = None
flashing = False

# Example positions for the buttons
positions = [
    (10, 10), (100, 10), (200, 10), (300, 10), (400, 10), (500, 10),
    (10, 80), (100, 80), (200, 80), (300, 80), (400, 80), (500, 80),
    (10, 150), (100, 150), (200, 150), (300, 150), (400, 150), (500, 150),
    (10, 220), (100, 220), (200, 220), (300, 220), (400, 220), (500, 220),
    (10, 290), (100, 290), (200, 290), (300, 290), (400, 290), (500, 290),
    (10, 360), (100, 360), (200, 360), (300, 360), (400, 360), (500, 360),
    (10, 430), (100, 430), (200, 430), (300, 430), (400, 430), (500, 430),
    (10, 500), (100, 500), (200, 500), (300, 500), (400, 500), (500, 600)
]

for i, name in enumerate(button_names):
    button = tk.Button(root, text=name)
    button.config(command=lambda name=name, b=button: button_click(name, b), height=2, width=4, font=5)
    button.place(x=positions[i][0], y=positions[i][1])
    buttons.append(button)

retry_button = tk.Button(root, text="Retry", command=retry)
retry_button.pack_forget()  # Hide the retry button initially

# Add the reset button at the bottom
reset_button = tk.Button(root, text="Reset", command=reset, bg="red", fg="white", height=2, width=10)
reset_button.place(x=250, y=600)  # Adjust the position as needed

root.mainloop()