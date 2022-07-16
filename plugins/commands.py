import os
import logging
import json
import requests

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from info import START_MSG, CHANNELS, ADMINS, INVITE_MSG, NEWSAPI_ID, GOOGLE_TRANSLATE_API_ID, BOT_TOKEN
from utils import Media, unpack_new_file_id

logger = logging.getLogger(__name__)


@Client.on_message(filters.command('start'))
async def start(bot, message):
    """Start command handler"""
    if len(message.command) > 1 and message.command[1] == 'subscribe':
        await message.reply(INVITE_MSG)
    else:
        try:
            buttons = [[
                InlineKeyboardButton('Search Here', switch_inline_query_current_chat=''),
                InlineKeyboardButton('Go Inline', switch_inline_query=''),
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            await message.reply(START_MSG, reply_markup=reply_markup)
        except Exception as e:
            await message.reply(e)    

@Client.on_message(filters.command('dolar'))
async def dolar(bot, message):
    try:
        request = requests.get("https://economia.awesomeapi.com.br/json/last/USD-BRL")
        dolar = json.loads(request.content)
        msg = "Máxima : R$"+dolar['USDBRL']['high']+"\nMínima : R$"+dolar['USDBRL']['low']+"\nVariação : R$"+dolar['USDBRL']['varBid']+"\n"
        await message.reply(msg)
    except Exception as e:
        await message.reply(e)

@Client.on_message(filters.command('advice'))
async def advice(bot, message):
    try:
        request = requests.get("https://api.adviceslip.com/advice")
        advice = json.loads(request.content)
        msgAdvice = advice['slip']['advice']
        request = requests.get("https://translation.googleapis.com/language/translate/v2?key="+GOOGLE_TRANSLATE_API_ID+"&q="+msgAdvice+"&target=pt")
        translate = json.loads(request.content)
        msg = translate['data']['translations'][0]['translatedText']
        await message.reply(msg)
    except Exception as e:
        await message.reply(e)               


@Client.on_message(filters.command('gnews')) 
async def gnews(bot, message):
    try:
        request = requests.get("https://newsapi.org/v2/top-headlines?sources=google-news-br&apiKey="+NEWSAPI_ID)
        news = json.loads(request.content)
        #iterate each item of json array    
        for item in news['articles']:
            #get image of articles if exists and add title (bold) and description as caption and url if not exists send only title (bold) and description and url
            if item['urlToImage']:
                await message.reply_photo(item['urlToImage'], caption="<b>"+item['title']+"</b>"+"\n\n"+item['description']+"\n\n"+item['url'])
            else:
                await message.reply("<b>"+item['title']+"</b>\n\n"+item['description']+"\n\n"+item['url'])
    except Exception as e:
        await message.reply(e)        

@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = '📑 **Indexed channels/groups**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('total') & filters.user(ADMINS))
async def total(bot, message):
    """Show total files in database"""
    msg = await message.reply("Processing...⏳", quote=True)
    try:
        total = await Media.count_documents()
        await msg.edit(f'📁 Saved files: {total}')
    except Exception as e:
        logger.exception('Failed to check total files')
        await msg.edit(f'Error: {e}')

#by command /addMsg get message "document", "video", "audio" and his respective caption and add it to database mongoDB
@Client.on_message(filters.command('addMsg') & filters.user(ADMINS))
async def add_msg(bot, message):
    """Add message to database"""
    msg = await message.reply("Processing...⏳", quote=True)
    try:
        if message.reply_to_message:
            if message.reply_to_message.document:
                file_id = message.reply_to_message.document.file_id
                file_name = message.reply_to_message.document.file_name
                file_size = message.reply_to_message.document.file_size
                file_ext = message.reply_to_message.document.file_name.split('.')[-1]
                file_type = 'document'
            elif message.reply_to_message.video:
                file_id = message.reply_to_message.video.file_id
                file_name = message.reply_to_message.video.file_name
                file_size = message.reply_to_message.video.file_size
                file_ext = message.reply_to_message.video.file_name.split('.')[-1]
                file_type = 'video'
            elif message.reply_to_message.audio:
                file_id = message.reply_to_message.audio.file_id
                file_name = message.reply_to_message.audio.file_name
                file_size = message.reply_to_message.audio.file_size
                file_ext = message.reply_to_message.audio.file_name.split('.')[-1]
                file_type = 'audio'
            else:
                await msg.edit("Error: File type not supported")
                return
        else:
            await msg.edit("Error: No file selected")
            return
        if message.text.split(' ', 1)[1]:
            caption = message.text.split(' ', 1)[1]
        else:
            caption = None
        await Media.create_one(file_id=file_id, file_name=file_name, file_size=file_size, file_ext=file_ext, file_type=file_type, caption=caption)
        await msg
        await message.reply("File added to database")
    except Exception as e:
        logger.exception('Failed to add file')
        await msg.edit(f'Error: {e}')
        


@Client.on_message(filters.command('logger') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))


@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if not (reply and reply.media):
        await message.reply('Reply to file with /delete which you want to delete', quote=True)
        return

    msg = await message.reply("Processing...⏳", quote=True)

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('This is not supported file format')
        return

    file_id = unpack_new_file_id(media.file_id)[0]
    result = await Media.collection.delete_one({'file_id': file_id})

    if result.deleted_count:
        await msg.edit('File is successfully deleted from database')
    else:
        await msg.edit('File not found in database')
