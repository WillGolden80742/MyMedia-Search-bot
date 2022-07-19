import os
import logging
import requests
import json
import random

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from info import START_MSG, CHANNELS, ADMINS, INVITE_MSG, NEWSAPI_ID, GOOGLE_TRANSLATE_API_ID
from utils import Media, unpack_new_file_id

logger = logging.getLogger(__name__)

@Client.on_message(filters.command('start'))
async def start(bot, message):
    """Start command handler"""
    if len(message.command) > 1 and message.command[1] == 'subscribe':
        await message.reply(INVITE_MSG)
    else:
        buttons = [[
            InlineKeyboardButton('Search Here', switch_inline_query_current_chat=''),
            InlineKeyboardButton('Go Inline', switch_inline_query=''),
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(START_MSG, reply_markup=reply_markup)

async def graph(a,b,c):
    import matplotlib.pyplot as plt
    import base64
    import io    
    delta = b**2-4*a*c
    if delta >= 0:
        Yv = []
        Xv = []
        XVertice=-b/2*a
        YVertice=-(delta)/4*a
        if XVertice>0:
            x=-(XVertice)
        else:
            x=(XVertice)
        xi = int(x*2)
        xf = int(x*-2)
        yi = a*xi**2+b*xi+c
        for i in range(xi,xf+1):            
            y = a*i**2+b*i+c
            Yv.append(y)
            Xv.append(i)   
        plt.plot(Xv,Yv,color='g') 
        plt.ylabel('Y')
        plt.hlines(y=0, xmin=xi, xmax=xf, linewidth=1, color='b')   
        if a > 0:
            plt.plot([0,0],[yi,YVertice], linewidth=1, color='b')      
            plt.title("O gráfico pode apresentar imprecisão, mas os números estão corretos.\nx")
            plt.xlabel("Xv="+str(XVertice)+", Yv="+str(YVertice))
            plt.plot([XVertice,XVertice],[YVertice-0.25,YVertice+0.75], color='r')    
        else:
            plt.plot([0,0],[YVertice,y], linewidth=1, color='b')      
            plt.title("Xv="+str(XVertice)+", Yv="+str(YVertice))
            plt.xlabel("O gráfico pode apresentar imprecisão, mas os números estão corretos.\nx") 
            plt.plot([XVertice,XVertice],[YVertice-0.75,YVertice+0.5], color='r') 
        # get plt grafic and send it as a photo
        plt.savefig('graph.png')
        plt.close()
        with open('graph.png', 'rb') as f:
            b64 = base64.b64encode(f.read())
            b64 = b64.decode('utf-8') 
    else:  
        return None    

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

@Client.on_message(filters.command('gnews'))
async def gnews(bot, message):
    try:
        request = requests.get("https://newsapi.org/v2/top-headlines?country=br&apiKey="+NEWSAPI_ID)
        news = json.loads(request.content) 
        index = 0
        lengthArticleList = len(news['articles'])
        if len(message.command) > 1:
            #convert the string to integer
            #add module to the integer 
            index = int(message.command[1]) % (lengthArticleList)
            indexTitle=index   
        else:
            index = random.randint(0,lengthArticleList) % lengthArticleList
            indexTitle=index
        if indexTitle == 0:
            indexTitle = 20
        index-=1             
        msg = news['articles'][index]
        indexString = "\n\n("+str(indexTitle)+"/"+str(lengthArticleList)+")"
        #if to check if is NoneType object
        if msg['urlToImage']:
            await message.reply_photo(msg['urlToImage'], caption="<b>"+str(msg['title']).replace('None','')+"</b>"+"\n\n"+str(msg['description']).replace('None','')+"\n\n"+str(msg['url']).replace('None','')+indexString)
        else:
           await message.reply_text("Não há mensagem para mostrar no índice "+indexString)        
    except Exception as e:
        await message.reply(e)  

#by command 'bask' the bot will solve the equation of Baskara get the terms 'A', 'B' and 'C' and the bot will solve the equation
@Client.on_message(filters.command('bhask'))
async def bhask(bot, message):
    """Bask command handler"""
    if len(message.command) > 1:
        try:
            a = float(message.command[1])
            b = float(message.command[2])
            c = float(message.command[3])    
            delta = b**2 - 4*a*c        
            if delta >= 0:
                x1 = (-b + (delta)**0.5) / (2*a)
                x2 = (-b - (delta)**0.5) / (2*a)
                await graph(a,b,c)  
                await message.reply_photo(open('graph.png', 'rb'),caption=" <p>x1 = "+str(x1)+", x2 = "+str(x2))
            else:
                await message.reply("<p>Não há raiz real</p>")                    
        except  Exception as e:
            await message.reply("Digite o comando com os valores de a, b e c "+str(e))
    else:
        await message.reply('Invalid equation')


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

