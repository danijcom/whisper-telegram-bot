# Whisper Speech To Text Telegram bot
(just a small and simple bot I've created for myself)

# Installation
1. Clone this repository to your local machine
2. Use [this guide](https://docs.pyrogram.org/intro/quickstart) to obtain api_id and api_hash.
3. Message `@BotFather` to create a new bot and get its token. Also you can use `@userinfobot` to get your telegram id (admin id).
4. Edit `config-example.ini` file and rename it to `config.ini`
5. You should disable privacy mode for groups for your bot using @BotFather (to allow your bot work in Telegram groups).
6. [Optional] use venv to avoid conflicts because of packages versions. Install requirements from `requirements.txt` file (for Windows it `py -m pip install -r requirements.txt`).
7. Run the `main.py` file, send a `/commands` command to your bot from your (admin) account to set up the commands menu.

# Usage
To allow transcribing voice messages in some chats, you should add the id of this chat to the allowed list using `/allow` command. 

The bot will message you when it's added to some group so you can easily get its id.

To remove chat from allowed - use `/disallow` command.
