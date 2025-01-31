import os
import sys
import tkinter as tk
from tkinter import Toplevel, messagebox
import pygame
from PIL import Image, ImageTk

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
default = "#c9c9c9"

# Initialize variables
current_mode = "startup"
correct_order = []
order = []
lights = []
last_incorrect_light = None
flashing = False
wrong_attempts = {"startup": 0, "shutdown": 0}  # Separate counters for each mode

def play_sound():
    switch_sound.play()

def play_alarm():
    alarm_sound.play(loops=-1)

def stop_alarm():
    alarm_sound.stop()

def check_order():
    global order, flashing
    if order == correct_order:
        if current_mode == "shutdown":
            for light in lights:
                canvas.itemconfig(light, fill="#ff3730")
            messagebox.showinfo("Success", "Correct shutdown order!")
        else:
            messagebox.showinfo("Success", "Correct startup order!")
        return_to_main_menu()
    else:
        messagebox.showerror("Error", "Incorrect order! Restarting...")
        reset_current_mode()

def reset_current_mode():
    global order, flashing
    order = []
    flashing = False
    wrong_attempts[current_mode] = 0
    update_counter_label()
    stop_alarm()
    initial_color = "#37eb34" if current_mode == "shutdown" else default
    for light in lights:
        canvas.itemconfig(light, fill=initial_color)

def return_to_main_menu():
    global order, flashing
    order = []
    flashing = False
    stop_alarm()
    simulation_frame.pack_forget()
    start_menu.pack(fill=tk.BOTH, expand=True)
    footer_label.pack(side='bottom', pady=10)  # Show footer
    update_counter_label()

def retry():
    global flashing
    flashing = False
    stop_alarm()
    if last_incorrect_light:
        initial_color = "#37eb34" if current_mode == "shutdown" else default
        canvas.itemconfig(last_incorrect_light, fill=initial_color)
    for name in order:
        index = light_names.index(name)
        correct_color = "#ff3730" if current_mode == "shutdown" else "#37eb34"
        canvas.itemconfig(lights[index], fill=correct_color)
    reset_button.pack_forget()

def flash_light(light):
    if flashing:
        light_color = canvas.itemcget(light, "fill")
        next_light_color = default if light_color == "#ff3730" else "#ff3730"
        canvas.itemconfig(light, fill=next_light_color)
        canvas.after(500, lambda: flash_light(light))

def show_retry_window():
    retry_window = Toplevel(root)
    retry_window.title("Incorrect Order")
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 300
    window_height = 150
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    
    retry_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def on_closing():
        reset_current_mode()
        retry_window.destroy()
    
    retry_window.protocol("WM_DELETE_WINDOW", on_closing)
    retry_window.attributes("-toolwindow", True)

    tk.Label(retry_window, text="Incorrect order! Try again...").pack(pady=10)
    tk.Button(retry_window, text="Go Back", command=lambda: [retry(), retry_window.destroy()]).pack(pady=5)
    tk.Button(retry_window, text="Reset", command=lambda: [reset_current_mode(), retry_window.destroy()]).pack(pady=5)
    retry_window.grab_set()

def light_click(event, name, light):
    global last_incorrect_light, flashing
    play_sound()
    initial_color = "#37eb34" if current_mode == "shutdown" else default
    correct_color = "#ff3730" if current_mode == "shutdown" else "#37eb34"
    
    if order and name == order[-1]:
        order.pop()
        canvas.itemconfig(light, fill=initial_color)
    else:
        if len(order) < len(correct_order) and name == correct_order[len(order)]:
            order.append(name)
            canvas.itemconfig(light, fill=correct_color)
            if len(order) == len(correct_order):
                check_order()
        else:
            last_incorrect_light = light
            flashing = True
            flash_light(light)
            play_alarm()
            show_retry_window()
            wrong_attempts[current_mode] += 1
            update_counter_label()

def update_counter_label():
    counter_label.config(text=f"Wrong Attempts: {wrong_attempts[current_mode]}")

def select_mode(mode):
    global current_mode, correct_order
    current_mode = mode
    correct_order = light_names[:] if mode == "startup" else list(reversed(light_names))
    
    start_menu.pack_forget()
    footer_label.pack_forget()  # Hide footer
    simulation_frame.pack(fill=tk.BOTH, expand=True)
    
    # Reset counters and lights for the selected mode
    wrong_attempts[current_mode] = 0
    initial_color = "#37eb34" if mode == "shutdown" else default
    for light in lights:
        canvas.itemconfig(light, fill=initial_color)
    
    update_counter_label()

############################ CREATE WINDOWS AND FRAMES ############################

root = tk.Tk()
root.title("QUB Steam Plant Simulator")
root.attributes('-fullscreen', True)
root.minsize(800, 600)

# Create footer label (initially hidden)
footer_label = tk.Label(
    root, 
    text="Created by IT HUB CHEM-ENG",
    font=("Helvetica", 10),
    fg="gray"
)

# Start Menu Frame
start_menu = tk.Frame(root)

# Add Logo to Start Menu
logo_main_image = Image.open(resource_path("images/image.png"))
logo_main_image = logo_main_image.resize((800, 200), Image.LANCZOS)
logo_main_photo = ImageTk.PhotoImage(logo_main_image)
logo_label = tk.Label(start_menu, image=logo_main_photo)
logo_label.image = logo_main_photo  # Keep reference
logo_label.pack(pady=(80, 20))  # Add padding at top and bottom

title_label = tk.Label(start_menu, text="Steam Plant Simulator", font=("Helvetica", 24))
title_label.pack(pady=20)

startup_btn = tk.Button(start_menu, text="Startup", command=lambda: select_mode("startup"), width=15, height=2)
startup_btn.pack(pady=20)

shutdown_btn = tk.Button(start_menu, text="Shutdown", command=lambda: select_mode("shutdown"), width=15, height=2)
shutdown_btn.pack(pady=20)

exit_btn = tk.Button(start_menu, text="Exit", command=root.destroy, width=15, height=2)
exit_btn.pack(pady=20)

# Simulation Frame
simulation_frame = tk.Frame(root)

# Load Window Logo
logo_image = Image.open(resource_path("images/logo2.png"))
logo_image = logo_image.resize((64, 64), Image.LANCZOS)
logo_photo = ImageTk.PhotoImage(logo_image)
root.iconphoto(False, logo_photo)

# Create canvas and widgets inside simulation_frame
frame_image = tk.Frame(simulation_frame)
frame_image.pack(fill=tk.BOTH, expand=True)
canvas = tk.Canvas(frame_image)
canvas.pack(fill=tk.BOTH, expand=True)

# Background Image
bg_image = Image.open(resource_path("images/background.png"))
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
bg_image = bg_image.resize((screen_width, screen_height), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)
canvas.create_image(0, 0, anchor=tk.NW, image=bg_photo)

# Control Buttons
exit_button = tk.Button(simulation_frame, text="Exit", command=root.destroy, bg="red", fg="white", height=2, width=10, font=10)
exit_button.place(relx=1.0, rely=0.0, anchor='ne')

main_menu_btn = tk.Button(simulation_frame, text="Main Menu", command=return_to_main_menu, bg="blue", fg="white", height=2, width=10)
main_menu_btn.place(relx=0.65, rely=0.95, anchor='s')

reset_button = tk.Button(simulation_frame, text="Reset", command=reset_current_mode, bg="#ff3730", fg="white", height=2, width=10)
reset_button.place(relx=0.5, rely=0.95, anchor='s')

counter_label = tk.Label(simulation_frame, text=f"Wrong Attempts: 0", font=("Helvetica", 16))
counter_label.place(relx=0.5, rely=0.9, anchor='s')


# Light configuration
light_names = [
    "V1", "V3", "V4", "V2", "P1", "P2", "V5", "V6", "P3", "F2", "V9", "F1",
    "V7", "V8", "P4", "F4", "V14", "F3", "V12", "V13", "P5", "V17", "V18", "P6",
    "V19", "V20", "V16", "V15", "V10", "P7", "V28", "V29", "P12", "V24", "V25",
    "P9", "V26", "V27", "P11", "V30", "P10", "V22", "V23", "V21", "P8", "V11"
]

light_radius = 13
light_positions = [
    (114, 111), (223, 202), (274, 354), (177, 104), (147, 120), (227, 305),
    (616, 221), (684, 215), (651, 233), (778, 106), (666, 387), (700, 399),
    (616, 324), (683, 318), (650, 336), (1329, 142), (1177, 392), (1222, 404),
    (1152, 328), (1206, 321), (1176, 344), (1578, 800), (1666, 794), (1620, 810),
    (1558, 870), (1668, 877), (1726, 692), (1695,292 ), (1067,192 ), (1619,888 ),
    (82,477 ), (182,435 ), (117,487 ), (686, 882), (757,872 ), (717,894 ),
    (556,1021 ), (664, 961), (603,1032 ), (115, 528), (812, 932), (973,848 ),
    (1045,842 ), (960,805 ), (1007,859 ), (871,112 )
]

# Create lights on the canvas
lights = []
for i, pos in enumerate(light_positions):
    light = canvas.create_oval(
        pos[0] - light_radius, pos[1] - light_radius,
        pos[0] + light_radius, pos[1] + light_radius,
        fill=default
    )
    lights.append(light)
    text = canvas.create_text(pos[0], pos[1], text=light_names[i], fill="black", font=("Helvetica", 10))
    canvas.tag_bind(light, '<Button-1>', lambda event, name=light_names[i], l=light: light_click(event, name, l))
    canvas.tag_bind(text, '<Button-1>', lambda event, name=light_names[i], l=light: light_click(event, name, l))

start_menu.pack(fill=tk.BOTH, expand=True)
footer_label.pack(side='bottom', pady=10)
root.mainloop()