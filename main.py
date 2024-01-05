# -*- coding: utf8 -*-
import os
import sys
import configparser

from loguru import logger
from pyrogram import Client, filters, enums
from pyrogram.types import BotCommand, BotCommandScopeChat

import mySTT

os.chdir(os.path.dirname(os.path.abspath(__file__)))

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

logger.add("app.log", rotation="5 MB")
app = Client(
    name='whisperSTT',
    api_id=config['pyrogram']['api_id'],
    api_hash=config['pyrogram']['api_hash'],
    bot_token=config['pyrogram']['bot_token']
)
my_stt = mySTT.MySTT(config['chat_gpt']['api_key'])


@logger.catch
@app.on_message(filters.voice)
async def voice_to_text(client, message):
    is_allowed = False

    allow_list = config.items('allowed_ids')
    for allowed_name, allowed_id in allow_list:
        if str(message.chat.id) == allowed_id:
            logger.info('Got message from {}'.format(allowed_name))
            is_allowed = True
            break

    if not is_allowed:
        logger.info('Message from {} is not in allowed'.format(message.chat.id))
        return
    else:
        voice_path = '{}_{}.ogg'.format(message.chat.id, message.id)
        voice_path = await message.download(voice_path)

        await app.send_chat_action(message.chat.id, enums.ChatAction.TYPING)

        try:
            w_text = my_stt.stt_whisper(voice_path)
        except Exception as ex:
            logger.error(ex)
        else:
            await message.reply("**🎤 [Whisper]**\n__{}__".format(w_text), quote=True)

        try:
            os.remove(voice_path)
        except:
            pass


@logger.catch
@app.on_message(filters.command('log'))
async def get_log(client, message):
    if message.chat.id != int(config['private']['admin_id']):
        return
    else:
        await message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
        await message.reply_document(document='app.log')


@logger.catch
@app.on_message(filters.command('commands'))
async def set_commands(client, message):
    if message.chat.id != int(config['private']['admin_id']):
        return
    else:
        await set_commands()


@logger.catch
@app.on_message(filters.command('allow'))
async def add_allowed(client, message):
    if message.chat.id != int(config['private']['admin_id']):
        return
    else:
        data = message.text.split(' ')
        if len(data) != 3:
            await message.reply('❕ **Format:**\n/allow [some_name] [telegram_id]')
        else:
            config.set('allowed_ids', data[1], data[2])
            with open('config.ini', 'w') as config_file:
                config.write(config_file)
            await message.reply('➕ ID `{}` is allowed with name **{}**'.format(data[2], data[1]))


@logger.catch
@app.on_message(filters.command('disallow'))
async def remove_allowed(client, message):
    if message.chat.id != int(config['private']['admin_id']):
        return
    else:
        data = message.text.split(' ')
        if len(data) != 2:
            await message.reply('➖ **Format:**\n/disallow [name]')
        else:
            config.set('allowed_ids', data[1], '0')
            with open('config.ini', 'w') as config_file:
                config.write(config_file)
            await message.reply('➕ ID for name {} is set to 0'.format(data[1]))


@logger.catch
@app.on_message(filters.command('allowed'))
async def check_allowed(client, message):
    if message.chat.id != int(config['private']['admin_id']):
        return
    else:
        msg_text = '📄 **Allowed list**\n'

        allow_list = config.items('allowed_ids')
        for allowed_name, allowed_id in allow_list:
            msg_text += '\n**{}**: `{}`'.format(allowed_name, allowed_id)

        await message.reply(msg_text)


@logger.catch()
@app.on_chat_member_updated()
async def added_to_chat(client, chat_member_updated):
    me = await app.get_me()
    if chat_member_updated.new_chat_member and chat_member_updated.new_chat_member.user.id == me.id:

        if chat_member_updated.chat.username is not None:
            chat_name = '@' + chat_member_updated.chat.username
        elif chat_member_updated.chat.title is not None:
            chat_name = chat_member_updated.chat.title
        elif chat_member_updated.chat.first_name is not None:
            chat_name = chat_member_updated.chat.first_name
        else:
            chat_name = '?'

        msg_text = '🆕 **Bot was added to {}**\n\nChat name: **{}**\nChat id: `{}`'.format(
            chat_member_updated.chat.type, chat_name, chat_member_updated.chat.id
        )
        logger.info('Added to some {}: {} | {}'.format(
            chat_member_updated.chat.type, chat_name, chat_member_updated.chat.id)
        )
        if chat_member_updated.from_user is not None:
            msg_text += '\n\nInvited by: {}'.format(chat_member_updated.from_user.mention())
            logger.info('Added by: {}'.format(chat_member_updated.from_user.mention()))

        await app.send_message(config['private']['admin_id'], msg_text)


@logger.catch
async def set_commands():
    utils_command = {
        'allowed': 'Check allowed list',
        'allow': 'Allow a chat [some_name] [chat_id]',
        'disallow': 'Delete from allowed list [some_name]',
        'log': 'Get the log file'
    }
    full_commands_list = []

    for command in utils_command:
        full_commands_list.append(
            BotCommand(
                command,
                utils_command.get(command)
            )
        )

    await app.set_bot_commands(
        full_commands_list,
        BotCommandScopeChat(config['private']['admin_id'])
    )

    logger.info('Commands set!')


if __name__ == "__main__":
    logger.info('App started')
    sys.stdout.flush()
    app.run()