
# Atria - Telegram Bot Automation

Atria is a versatile Python-based tool designed to control a computer via a Telegram bot. It provides functionalities like task management, file manipulation, screen recording, and system monitoring. This bot is intended for educational purposes and should not be used for any malicious activities.

## Features
- **System Control**: Shutdown, restart, or control Task Manager.
- **File Operations**: Upload/download files, list directories, and execute shell commands.
- **Screen & Audio Recording**: Capture screenshots, record screen, webcam, and microphone.
- **User & Network Info**: Retrieve user accounts, system info, and saved Wi-Fi passwords.
- **Chrome Password Retrieval**: Decrypt and retrieve passwords saved in Google Chrome.
- **Security Control**: Disable Windows security features (Task Manager, UAC, Defender, etc.).
- **Keylogging**: Record key presses and monitor active windows.

## Prerequisites

Before using Atria, ensure you have the following installed:
- Python 3.12.5 (run `Install Atria.bat` to automatically install or to update to the latest version)
- Telegram bot token (created via [BotFather](https://core.telegram.org/bots#botfather))
- Chat ID from Telegram bot

### Dependencies
It is recommended that you run the `Install Atria.bat` script to install the dependencies automatically. However, if you prefer to install them manually, follow these steps:

```bash
python -m venv %~dp0\Atria
cd %~dp0\Atria
.\Scripts\Activate
pip install -r requirements.txt
```

## Configuration

### 1. Getting the Bot Token
To get the **bot token**, follow these steps:
1. Open the Telegram app and search for **BotFather**.
2. Start a chat with **BotFather** and send the command `/newbot`.
3. Follow the instructions to name your bot and get a **token**. It will look something like this: `123456789:ABCdefGhIJKlmNOpQrsTUVwXYZabcDEFgHI`.

### 2. Getting the Chat ID
To get your **chat ID**, follow these steps:
1. Search for the bot you just created and start a conversation with it.
2. Send any message to the bot.
3. Visit the following URL in your browser, replacing `<YOUR_BOT_TOKEN>` with the token you received from BotFather: 
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
4. Look for `"chat":{"id":` in the response. The number that follows is your chat ID.

### 3. Running the Bot
1. After you have the **bot token** and **chat ID**, run the `Run Atria.bat` file to start the Atria GUI.
2. Enter the bot token and chat ID into the fields in the GUI and click **Save Configuration**.

### 4. Compile Script (Optional)
If you wish to compile the script to an executable:
- Run the following command to compile:
    ```bash
    pyinstaller --onefile --noconsole --add-data "bot_config.txt;." Atria.py
    ```
- Or use the GUI feature by clicking **Compile Script** after doing Step 3.


## How to Use

Once you have configured your bot, start the script and send commands via the Telegram bot. Below are some available commands:

### System Control
- `/shutdown`: Shuts down user's PC.
- `/restart`: Restart user's PC.
- `/dtaskmgr`: Disables Task Manager.
- `/drun`: Disables Run command.
- `/dregistry`: Disables Registry Tools.

### File Operations
- `/screenshot`: Captures and sends a screenshot.
- `/webscreenshot`: Takes a screenshot from the user's webcam.
- `/upload`: Uploads a file from the user's PC.
- `/download <filename>`: Downloads a file from the user's PC.

### Screen and Audio Recording
- `/screenrecord <seconds>`: Records the screen for the specified duration.
- `/mic <seconds>`: Records audio from the microphone for the specified duration.
- `/webcam <seconds>`: Records video from the webcam for the specified duration.

### Security and User Info
- `/info`: Shows PC info including IP, location, and more.
- `/users`: Shows all user accounts on the user's PC.
- `/whoami`: Displays the currently logged-on user.
- `/passwords`: Retrieve saved Chrome passwords.
- `/wifilist`: List all saved Wi-Fi networks.
- `/wifipass <network_name>`: Show Wi-Fi password for a specific network.
- `/robloxcookie`: Attempts to retrieve Roblox cookies from various browsers.

### Miscellaneous
- `/help`: List all available commands.
- `/hide`: Hides the compiled Python script by adding the hidden attribute.
- `/tasklist`: List all running tasks.
- `/taskkill <process>`: Kill a specific process by name or PID.
- `/shell <command>`: Execute commands in a hidden shell.

## Disclaimer

**Important**: This tool is intended for educational purposes only. Ensure you have permission to control the system where Atria is used. Misuse of this tool may violate local laws and regulations.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.
