import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import serial
from threading import Thread
from pythonosc.udp_client import SimpleUDPClient
import serial.tools.list_ports
import sys
from pathlib import Path

# Handle PyInstaller and normal dev environment
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)  # PyInstaller runtime path
else:
    BASE_DIR = Path(__file__).resolve().parent

running = False  # Controls loop thread
ser = None

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def start_listening():
    global running, ser

    port = port_var.get()
    baud = baud_var.get()

    if not port or not baud:
        messagebox.showerror("Input Error", "Please select a COM port and enter a baud rate.")
        return

    if running:
        messagebox.showinfo("Already Running", "The listener is already running.")
        return

    try:
        if ser and ser.is_open:
            ser.close()

        ser = serial.Serial(port, int(baud), timeout=1)
        ser.reset_input_buffer()
    except serial.SerialException as e:
        messagebox.showerror("Serial Error", str(e))
        return

    client = SimpleUDPClient("127.0.0.1", 7000)

    running = True
    log_text.pack(side="bottom", fill=tk.X, padx=10, pady=5)
    log_text.configure(state='normal')
    log_text.delete(1.0, tk.END)
    log_text.insert(tk.END, f"Listening on {port} at {baud}...\n")
    log_text.see(tk.END)

    def read_loop():
        while running:
            try:
                if ser.in_waiting > 0:
                    raw = ser.readline()
                    try:
                        data = raw.decode('utf-8').strip()
                    except UnicodeDecodeError:
                        data = raw.decode('latin1').strip()

                    log_text.insert(tk.END, f"Received: {data}\n")
                    log_text.see(tk.END)

                    command_column_map = {
                        comand_1_var.get().strip(): column_1_var.get(),
                        comand_2_var.get().strip(): column_2_var.get(),
                        comand_3_var.get().strip(): column_3_var.get(),
                        comand_4_var.get().strip(): column_4_var.get(),
                        comand_5_var.get().strip(): column_5_var.get(),
                        comand_6_var.get().strip(): column_6_var.get(),
                    }

                    if data in command_column_map:
                        col = command_column_map[data]
                        client.send_message(f"/composition/columns/{col}/connect", 1)
                        log_text.insert(tk.END, f"\u2192 Triggered Resolume column {col} for input: {data}\n")
                        log_text.see(tk.END)

            except Exception as e:
                log_text.insert(tk.END, f"Error in reading loop: {str(e)}\n")
                log_text.see(tk.END)
                break

        if ser and ser.is_open:
            ser.close()

        log_text.insert(tk.END, "Stopped.\n")
        log_text.see(tk.END)
        log_text.configure(state='disabled')

    Thread(target=read_loop, daemon=True).start()

def stop_listening():
    global running, ser
    running = False

    if ser and ser.is_open:
        ser.close()
        ser = None

    log_text.insert(tk.END, "Serial port closed.\n")
    log_text.see(tk.END)
    log_text.pack_forget()

root = tk.Tk()
root.title("INTERACTIVE APP")
root.geometry("1920x1080")
root.iconbitmap(str(BASE_DIR / "icon.ico"))

image = Image.open(BASE_DIR / "app.jpg")
image = image.resize((1920, 1080), Image.Resampling.LANCZOS)
bg_image = ImageTk.PhotoImage(image)
bg_label = tk.Label(root, image=bg_image)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

title_label = tk.Label(root, text="INTERACTIVE", font=("Arial", 20, "bold"), fg="black", bg="#002796")
title_label.place(relx=0.5, y=30, anchor="n")

frame_logo_img = Image.open(BASE_DIR / "Logo.png")
frame_logo_img = frame_logo_img.resize((240, 60), Image.Resampling.LANCZOS)
frame_logo_photo = ImageTk.PhotoImage(frame_logo_img)

port_var = tk.StringVar()
baud_var = tk.StringVar()

control_frame = tk.Frame(root, bg="#050505", bd=5, relief="ridge")
control_frame.place(relx=0.5, rely=0.5, anchor="center", width=600, height=760)

logo_label = tk.Label(root, image=frame_logo_photo, bg="#050505")
logo_label.place(x=10, y=10)

frame_bg_image = Image.open(BASE_DIR / "lazulite_technology_services_llc_logo.jpg")
frame_bg_image = frame_bg_image.resize((600, 760), Image.Resampling.LANCZOS)
frame_bg_photo = ImageTk.PhotoImage(frame_bg_image)

bg_label_frame = tk.Label(control_frame, image=frame_bg_photo)
bg_label_frame.place(x=0, y=0, relwidth=1, relheight=1)

comand_1_var = tk.StringVar()
comand_2_var = tk.StringVar()
comand_3_var = tk.StringVar()
comand_4_var = tk.StringVar()
comand_5_var = tk.StringVar()
comand_6_var = tk.StringVar()

column_1_var = tk.StringVar(value="1")
column_2_var = tk.StringVar(value="2")
column_3_var = tk.StringVar(value="3")
column_4_var = tk.StringVar(value="4")
column_5_var = tk.StringVar(value="5")
column_6_var = tk.StringVar(value="6")

def entry_row(label, var, x, y):
    tk.Label(control_frame, text=label, bg="#ffffff", font=("Arial", 14, "bold")).place(x=80, y=y, anchor="w", width=180, height=30)
    tk.Entry(control_frame, textvariable=var, width=20).place(x=260, y=y - 15, width=200, height=30)

def combo_row(label, var, x, y):
    tk.Label(control_frame, text=label, bg="#ffffff", font=("Arial", 12, "bold")).place(x=10, y=y, anchor="w", width=200, height=30)
    ttk.Combobox(control_frame, textvariable=var, values=[str(i) for i in range(1, 11)]).place(x=260, y=y - 15, width=200, height=30)

tk.Label(control_frame, text="COM Port:", bg="#ffffff", font=("Arial", 14, "bold"), width=10).place(x=80, y=35, anchor="w", width=130, height=30)
port_dropdown = ttk.Combobox(control_frame, textvariable=port_var, values=list_serial_ports(), width=20)
port_dropdown.place(x=260, y=20, width=200, height=30)

tk.Label(control_frame, text="Baud Rate :", bg="#ffffff", font=("Arial", 14, "bold"), width=10).place(x=80, y=105, anchor="w", width=130, height=30)
baud_entry = tk.Entry(control_frame, textvariable=baud_var, width=20)
baud_entry.place(x=260, y=90, width=200, height=30)

entry_row("Command_1:", comand_1_var, 80, 165)
combo_row("Column for Command_1:", column_1_var, 10, 205)

entry_row("Command_2:", comand_2_var, 80, 245)
combo_row("Column for Command_2:", column_2_var, 10, 285)

entry_row("Command_3:", comand_3_var, 80, 325)
combo_row("Column for Command_3:", column_3_var, 10, 365)

entry_row("Command_4:", comand_4_var, 80, 405)
combo_row("Column for Command_4:", column_4_var, 10, 445)

entry_row("Command_5:", comand_5_var, 80, 485)
combo_row("Column for Command_5:", column_5_var, 10, 525)

entry_row("Command_6:", comand_6_var, 80, 565)
combo_row("Column for Command_6:", column_6_var, 10, 605)

start_button = tk.Button(control_frame, text="Start", command=start_listening, font=("Arial", 14, "bold"), bg="white", fg="black", borderwidth=3, relief="raised")
start_button.place(x=200, y=630, width=200, height=40)

stop_button = tk.Button(control_frame, text="Stop", command=stop_listening, font=("Arial", 14, "bold"), bg="white", fg="black", borderwidth=3, relief="raised")
stop_button.place(x=200, y=675, width=200, height=40)

log_text = tk.Text(root, height=10, state='disabled')

root.mainloop()
