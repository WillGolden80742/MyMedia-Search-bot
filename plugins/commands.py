import os
import logging
import json
import requests
import random

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from info import START_MSG, CHANNELS, ADMINS, INVITE_MSG, NEWSAPI_ID, GOOGLE_TRANSLATE_API_ID
from utils import Media, unpack_new_file_id  

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

@Client.on_message(filters.command('ptbr'))
async def ptbr(bot, message):
    try:
        msgToTranslate = "Sem mensagem para traduzir"
        if message.reply_to_message.text:
            msgToTranslate = message.reply_to_message.text
        else:   
            msgToTranslate = message.reply_to_message.caption
        requestTranslate = requests.get("https://translation.googleapis.com/language/translate/v2?key="+GOOGLE_TRANSLATE_API_ID+"&q="+msgToTranslate+"&target=pt")
        translate = json.loads(requestTranslate.content)
        msg = translate['data']['translations'][0]['translatedText']
        await message.reply(msg)  
    except Exception as e:
        await message.reply("Selecione mensagem para traduzir")   

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

#by command /gnews gives you a random news from google 
@Client.on_message(filters.command('gnews'))
async def gnews(bot, message):
    try:
        #if to verify se articleList is value atribute is null
        #declare articleList to global variable
        request = requests.get("https://newsapi.org/v2/top-headlines?country=br&apiKey="+NEWSAPI_ID)
        news = json.loads(request.content)      
        rand = random.randint(0,len(news['articles']))
        msg = news['articles'][rand]
        if msg['urlToImage']:
            await message.reply_photo(msg['urlToImage'], caption="<b>"+msg['title']+"</b>"+"\n\n"+msg['description']+"\n\n"+msg['url'])
        else:
           await message.reply_text("<b>"+msg['title']+"</b>"+"\n\n"+msg['description']+"\n\n"+msg['url'])        
        await message.reply(msg)
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
