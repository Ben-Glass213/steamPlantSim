import os
import sys
import tkinter as tk
from tkinter import Toplevel, messagebox
import pygame
from PIL import Image, ImageTk
import time

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Initialize pygame mixer
pygame.mixer.init()

# Load the switch sound and alarm sound
switch_sound = pygame.mixer.Sound(resource_path("sounds/switchOn.wav"))
alarm_sound = pygame.mixer.Sound(resource_path("sounds/alarmSound.wav"))

# Initialize the counter for wrong answers
wrong_counter = 0

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
    global order, flashing, wrong_counter
    order = []
    flashing = False
    wrong_counter = 0  # Reset the counter to zero
    update_counter_label()  # Update the counter label
    stop_alarm()  # Stop the alarm sound when resetting
    for button in buttons:
        button.config(bg="SystemButtonFace")  # Reset button color to default
    for light in lights:
        canvas.itemconfig(light, fill="grey")  # Reset light color to grey

def retry():
    global flashing
    flashing = False
    stop_alarm()  # Stop the alarm sound when retrying
    if last_incorrect_button:
        last_incorrect_button.config(bg="SystemButtonFace")  # Reset the incorrect button color to default
        # Reset the corresponding light color to grey
        index = buttons.index(last_incorrect_button)
        canvas.itemconfig(lights[index], fill="grey")
    for name in order:
        index = button_names.index(name)
        buttons[index].config(bg="#37eb34")  # Set the correct buttons back to #37eb34
        canvas.itemconfig(lights[index], fill="#37eb34")  # Set the corresponding light to #37eb34
    reset_button.pack_forget()  # Hide the retry button after retrying

def flash_button(button, light):
    if flashing:
        current_color = button.cget("bg")
        next_color = "SystemButtonFace" if current_color == "#ff3730" else "#ff3730"
        button.config(bg=next_color)
        light_color = canvas.itemcget(light, "fill")
        next_light_color = "grey" if light_color == "#ff3730" else "#ff3730"
        canvas.itemconfig(light, fill=next_light_color)
        button.after(500, lambda: flash_button(button, light))  # Continue flashing every 500ms

def show_retry_window():
    retry_window = Toplevel(root)
    retry_window.title("Incorrect Order")
    retry_window.geometry("300x150")
    
    # Bind the window close event to a custom function that calls reset and destroys the window
    def on_closing():
        reset()
        retry_window.destroy()
    
    retry_window.protocol("WM_DELETE_WINDOW", on_closing)  # Bind the window close event to the custom function
    retry_window.attributes("-toolwindow", True)  # Remove minimize and maximize buttons

    tk.Label(retry_window, text="Incorrect order! Try again...").pack(pady=10)
    tk.Button(retry_window, text="Go Back", command=lambda: [retry(), retry_window.destroy()]).pack(pady=5)
    tk.Button(retry_window, text="Reset", command=lambda: [reset(), retry_window.destroy()]).pack(pady=5)
    retry_window.grab_set()  # Make the retry window modal

def button_click(name, button, light):
    global last_incorrect_button, flashing, wrong_counter
    play_sound()  # Play sound on button click
    if order and name == order[-1]:  # Check if the button is the last one in the order
        order.pop()
        button.config(bg="SystemButtonFace")  # Change the button color back to default if unselected
        canvas.itemconfig(light, fill="grey")  # Change the light color back to grey if unselected
    else:
        if len(order) < len(correct_order) and name == correct_order[len(order)]:
            order.append(name)
            button.config(bg="#37eb34")  # Change the specific button color to #37eb34 if correct
            canvas.itemconfig(light, fill="#37eb34")  # Change the corresponding light color to #37eb34 if correct
            if len(order) == len(correct_order):
                check_order()
        else:
            last_incorrect_button = button  # Store the reference to the incorrect button
            flashing = True
            flash_button(button, light)  # Start flashing the button and light
            play_alarm()  # Play the alarm sound
            show_retry_window()  # Show the custom retry window
            wrong_counter += 1  # Increment the counter for wrong answers
            update_counter_label()  # Update the counter label

def update_counter_label():
    counter_label.config(text=f"Wrong Attempts: {wrong_counter}")

def resize_canvas(event):
    global last_resize_time
    current_time = time.time()
    if current_time - last_resize_time > 0.1:  # Resize at most every 100ms
        canvas.config(width=event.width, height=event.height)
        resized_bg_image = bg_image.resize((event.width, event.height), Image.LANCZOS)
        bg_photo = ImageTk.PhotoImage(resized_bg_image)
        canvas.itemconfig(bg_image_id, image=bg_photo)
        canvas.bg_photo = bg_photo  # Keep a reference to avoid garbage collection
        for i, pos in enumerate(light_positions):
            new_x = pos[0] * event.width / 1000
            new_y = pos[1] * event.height / 600
            canvas.coords(lights[i], new_x - light_radius, new_y - light_radius, new_x + light_radius, new_y + light_radius)
        last_resize_time = current_time

last_resize_time = time.time()

############################ CREATE INSTANCE OF WINDOW ############################

root = tk.Tk()
root.title("QUB Steam Plant Simulator")
root.state('zoomed')  # Maximize the window

# Set a minimum window size
root.minsize(800, 600)

# Load Logo
logo_image = Image.open(resource_path("images/logo2.png"))
logo_image = logo_image.resize((64, 64), Image.LANCZOS)
logo_photo = ImageTk.PhotoImage(logo_image)

root.iconphoto(False, logo_photo)

# Create a frame for the background image and lights
frame_image = tk.Frame(root)
frame_image.grid(row=0, column=0, sticky="nsew")

# Create a canvas to hold the background image and other widgets
canvas = tk.Canvas(frame_image)
canvas.pack(fill=tk.BOTH, expand=True)

# Load the background image
bg_image = Image.open(resource_path("images/background.jpg"))
bg_photo = ImageTk.PhotoImage(bg_image)

# Place the background image on the canvas
bg_image_id = canvas.create_image(0, 0, anchor=tk.NW, image=bg_photo)

# Bind the canvas resize event
canvas.bind("<Configure>", resize_canvas)

# Create a frame for the buttons
frame_buttons = tk.Frame(root)
frame_buttons.grid(row=1, column=0, sticky="nsew")

# Configure grid weights to make the frames resize proportionally
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

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
lights = []
last_incorrect_button = None
flashing = False

# Calculate the number of buttons per section
num_buttons = len(button_names)
num_sections = 3
buttons_per_section = num_buttons // num_sections
extra_buttons = num_buttons % num_sections

# Split buttons into different sections
section1_buttons = button_names[:buttons_per_section + (1 if extra_buttons > 0 else 0)]
section2_buttons = button_names[buttons_per_section + (1 if extra_buttons > 0 else 0):2 * buttons_per_section + (1 if extra_buttons > 1 else 0)]
section3_buttons = button_names[2 * buttons_per_section + (1 if extra_buttons > 1 else 0):]

# Place buttons in section 1
for i, name in enumerate(section1_buttons):
    button = tk.Button(frame_buttons, text=name)
    button.config(command=lambda name=name, b=button, l=None: button_click(name, b, l), height=1, width=3, font=5)
    button.grid(row=i//6, column=i%6, padx=5, pady=5, sticky="nsew")
    buttons.append(button)

# Place buttons in section 2
for i, name in enumerate(section2_buttons):
    button = tk.Button(frame_buttons, text=name)
    button.config(command=lambda name=name, b=button, l=None: button_click(name, b, l), height=1, width=3, font=5)
    button.grid(row=(i + len(section1_buttons))//6, column=(i + len(section1_buttons))%6, padx=5, pady=5, sticky="nsew")
    buttons.append(button)

# Place buttons in section 3
for i, name in enumerate(section3_buttons):
    button = tk.Button(frame_buttons, text=name)
    button.config(command=lambda name=name, b=button, l=None: button_click(name, b, l), height=1, width=3, font=5)
    button.grid(row=(i + len(section1_buttons) + len(section2_buttons))//6, column=(i + len(section1_buttons) + len(section2_buttons))%6, padx=5, pady=5, sticky="nsew")
    buttons.append(button)

# Create lights on the canvas
light_radius = 10  # Radius of the circular lights
light_positions = [
    (700, 40), (750, 40), (800, 40), (850, 40), (900, 40), (950, 40),
    (700, 90), (750, 90), (800, 90), (850, 90), (900, 90), (950, 90),
    (700, 140), (750, 140), (800, 140), (850, 140), (900, 140), (950, 140),
    (700, 190), (750, 190), (800, 190), (850, 190), (900, 190), (950, 190),
    (700, 240), (750, 240), (800, 240), (850, 240), (900, 240), (950, 240),
    (700, 290), (750, 290), (800, 290), (850, 290), (900, 290), (950, 290),
    (700, 340), (750, 340), (800, 340), (850, 340), (900, 340), (950, 340),
    (700, 390), (750, 390), (800, 390), (850, 390)
]

for pos in light_positions:
    light = canvas.create_oval(
        pos[0] - light_radius, pos[1] - light_radius,
        pos[0] + light_radius, pos[1] + light_radius,
        fill="grey"
    )
    lights.append(light)

# Update button commands to include corresponding lights
for i, button in enumerate(buttons):
    button.config(command=lambda name=button_names[i], b=button, l=lights[i]: button_click(name, b, l))

# Configure grid weights for buttons to make them resize proportionally
for i in range(6):
    frame_buttons.grid_columnconfigure(i, weight=1)
for i in range((len(button_names) + 5) // 6):  # Number of rows needed
    frame_buttons.grid_rowconfigure(i, weight=1)

# Add a label to display the counter for wrong attempts
counter_label = tk.Label(frame_buttons, text=f"Wrong Attempts: {wrong_counter}", font=("Helvetica", 16))
counter_label.grid(row=8, column=0, columnspan=6, pady=10)

# Add the reset button at the bottom
reset_button = tk.Button(frame_buttons, text="Reset", command=reset, bg="#ff3730", fg="white", height=2, width=10)
reset_button.grid(row=9, column=0, columnspan=6, pady=10)  # Adjust the position as needed

root.mainloop()