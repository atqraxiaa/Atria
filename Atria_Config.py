from PyQt6.QtWidgets import QApplication, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget, QTextEdit
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import subprocess
import requests
import hashlib
import os
import sys
impor ttest
fse
fae
fs
fs
fs
ef

current_version = "beta 1.1"
bot_token_file = "bot_config.txt"
repo_api_url = "https://api.github.com/repos/mildndmystic/Atria/contents/"

# Thread class for updating the repository
class UpdateThread(QThread):
    log_signal = pyqtSignal(str)  # Signal to log messages

    def run(self):
        self.update_repository()

    # Method to update repository and log messages
    def update_repository(self):
        self.log_signal.emit("Checking for updates from the repository...")

        repo_items = get_files_from_repo()
        self.log_signal.emit(f"Fetched {len(repo_items)} items from the repository.")

        for item in repo_items:
            self.log_signal.emit(f"Processing item: {item['path']}")
            process_repo_item(item, self.log_signal.emit)

        self.log_signal.emit("Update completed.")

# Initialize GUI for bot configuration
class BotConfigGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        # Start the update thread
        self.update_thread = UpdateThread()
        self.update_thread.log_signal.connect(self.log)  # Connect log signal to the log method
        self.update_thread.start()  # Start the update process in a separate thread

    # UI setup for Atria configuration
    def initUI(self):
        self.setWindowTitle('Atria Configuration')
        self.setGeometry(100, 100, 500, 400)
        self.setWindowIcon(QIcon('assets/title.png'))
        self.config = self.load_configuration()

        version = self.config[2] if self.config[2] else 'Unknown'
        self.status_label = QLabel(f'Current Version: {version}', self)

        self.token_label = QLabel('Enter your Telegram bot token here:')
        self.token_input = QLineEdit(self)
        self.token_input.setText(self.config[0] if self.config[0] else '')

        self.chat_id_label = QLabel('Enter the Telegram chat ID to send messages to:')
        self.chat_id_input = QLineEdit(self)
        self.chat_id_input.setText(self.config[1] if self.config[1] else '')

        self.tutorial_label = QLabel(self)
        self.tutorial_label.setText('Don\'t know how to get these? <a href="https://github.com/mildndmystic/Atria?tab=readme-ov-file#configuration">Click here</a>')
        self.tutorial_label.setOpenExternalLinks(True)

        self.help_label = QLabel('Please save the configuration before compiling it.')

        self.save_button = QPushButton('Save Configuration', self)
        self.compile_button = QPushButton('Compile Script', self)
        self.save_button.clicked.connect(self.save_configuration)
        self.compile_button.clicked.connect(self.compile_script)

        self.console = QTextEdit(self)
        self.console.setReadOnly(True)
        self.console.setPlaceholderText('Console output will appear here...')
        self.console.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.token_label)
        layout.addWidget(self.token_input)
        layout.addWidget(self.chat_id_label)
        layout.addWidget(self.chat_id_input)
        layout.addWidget(self.tutorial_label)
        layout.addWidget(self.help_label)
        layout.addWidget(self.save_button)
        layout.addWidget(self.compile_button)
        layout.addWidget(self.console)
        self.setLayout(layout)

    # Append text to the console
    def log(self, message):
        self.console.append(message)

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

    # Get resource path based on execution mode
    def get_resource_path(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), bot_token_file)
        
    # Load and validate config file
    def load_configuration(self):
        global current_version
        config_path = self.get_resource_path()
        if not os.path.exists(config_path):
            print("Configuration file not found. Creating default configuration.", 'warning')
            self.create_default_config(config_path)
            return '', '', current_version
        try:
            with open(config_path, 'r') as file:
                config = file.readlines()
                if len(config) < 3:
                    return '', '', current_version
                bot_token = config[0].strip().split('=')[1]
                chat_id = config[1].strip().split('=')[1]
                current_version = config[2].strip().split('=')[1]
                return bot_token, chat_id, current_version
        except Exception as e:
            print(f"Error loading configuration: {e}", 'error')
            return '', '', current_version
        
    # Saves bot configuration and shows alerts
    def save_configuration(self):
        try:
            bot_token = self.token_input.text()
            chat_id = self.chat_id_input.text()

            if bot_token and chat_id:
                config_path = self.get_resource_path()
                with open(config_path, 'w') as file:
                    file.write(f"bot_token={bot_token}\n")
                    file.write(f"chat_id={chat_id}\n")
                    file.write(f"current_version={current_version}\n")
                QMessageBox.information(self, 'Success', 'Configuration saved successfully!')
            else:
                QMessageBox.warning(self, 'Warning', 'Bot token and chat ID cannot be empty.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to save configuration: {str(e)}')
        
    # Create a default configuration file
    def create_default_config(self, config_path):
        with open(config_path, 'w') as file:
            file.write("bot_token=\n")
            file.write("chat_id=\n")
            file.write(f"current_version={current_version}\n")

def get_files_from_repo(path=""):
    try:
        response = requests.get(repo_api_url + path, timeout=5)
        response.raise_for_status()
        items = response.json()
        return items
    except requests.exceptions.RequestException as e:
        print(f"Error fetching repository contents: {e}")
        return []

def get_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return None

def get_remote_file_hash(file_url):
    sha256_hash = hashlib.sha256()
    try:
        response = requests.get(file_url, timeout=5)
        response.raise_for_status()
        sha256_hash.update(response.content)
        return sha256_hash.hexdigest()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching remote file hash: {e}")
        return None

def download_file(file_url, file_path):
    try:
        response = requests.get(file_url, timeout=5)
        response.raise_for_status()
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as file:
            file.write(response.content)
            print(f"{file_path} downloaded and updated successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {file_path}: {e}")

def process_repo_item(item, logger):  # Add logger parameter
    try:
        item_path = item['path']
        raw_url = item['download_url']

        if item['type'] == 'file':
            local_file_path = os.path.join(os.getcwd(), item_path)

            local_hash = get_file_hash(local_file_path)
            remote_hash = get_remote_file_hash(raw_url)

            if local_hash is None:
                logger(f"File {local_file_path} is missing. Downloading the file...")  # Use logger
                download_file(raw_url, local_file_path)
            elif local_hash != remote_hash:
                logger(f"File {local_file_path} is outdated. Downloading the updated version...")  # Use logger
                download_file(raw_url, local_file_path)
            else:
                logger(f"File {local_file_path} is the latest version. Skipping download.")  # Use logger

        elif item['type'] == 'dir':
            directory_items = get_files_from_repo(item_path)
            for sub_item in directory_items:
                process_repo_item(sub_item, logger)  # Pass logger for sub-items

    except Exception as e:
        logger(f"Error processing item {item['path']}: {e}")  # Use logger

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BotConfigGUI()
    window.show()
    sys.exit(app.exec())
