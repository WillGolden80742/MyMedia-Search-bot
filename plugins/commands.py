import os
import traceback
import logging
import requests
import json
import random
import matplotlib.pyplot as plt
import base64 
import hashlib
import urllib.parse

from datetime import datetime
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
    number = str(int(a))+str(int(b))+str(int(c))
    n = number
    for i in range (3):
        n = str(n).replace('-','')
    houses = int(10**((len(n)/3)-1))
    a/=houses
    b/=houses
    c/=houses
    delta = b**2-4*a*c
    if delta >= 0:
        Xv=[]
        Yv=[]
        x1 = (-b + (delta)**0.5) / (2*a)
        x2 = (-b - (delta)**0.5) / (2*a) 
        XVertice=(x1+x2)/2
        YVertice=y=a*XVertice**2+b*XVertice+c
        xi = x1
        xf = x2
        xi*=2
        xf*=3 
        x=xi
        if xi > xf:
            while (x>=xf):
                Xv.append(x)
                y=a*x**2+b*x+c
                Yv.append(y)
                x-=1
        else:
            while (x<=xf):
                Xv.append(x)
                y=a*x**2+b*x+c
                Yv.append(y)
                x+=1
        plt.plot(Xv,Yv, color='r') 
        plt.plot([xi,xf],[0,0])
        plt.ylabel("y")
        if a > 0:  
            plt.xlabel("Xv="+str(XVertice)+", Yv="+str(YVertice))
            plt.title("O gráfico pode conter aproximações, mas os números estão certos\nx")
            plt.plot([XVertice,XVertice],[YVertice-0.25,YVertice+0.75], color='b')    
        else:     
            plt.title("Xv="+str(XVertice)+", Yv="+str(YVertice))
            plt.xlabel("x\nO gráfico pode conter aproximações, mas os números estão certos")
            plt.plot([XVertice,XVertice],[YVertice-0.75,YVertice+0.5], color='b') 
        plt.savefig('graph.png')
        plt.close()
        with open('graph.png', 'rb') as f:
            b64 = base64.b64encode(f.read())
            b64 = b64.decode('utf-8') 
        return b64    
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

#get @Client.on_message()
@Client.on_message(filters.command(''))
async def any(bot, message):
    await message.reply(message.command[0])    

@Client.on_message(filters.command('pt'))
async def pt(bot, message):
    try:
        msgToTranslate = "Sem mensagem para traduzir"
        if len(message.command) > 1:    
            msgToTranslate = " ".join(message.command[1:])
        else:             
            if message.reply_to_message.caption:
                msgToTranslate = message.reply_to_message.caption
            else:   
                msgToTranslate = message.reply_to_message.text
        msgToTranslate = urllib.parse.quote(msgToTranslate)       
        requestTranslate = requests.get("https://translation.googleapis.com/language/translate/v2?key="+GOOGLE_TRANSLATE_API_ID+"&q="+msgToTranslate+"&target=pt")
        translate = json.loads(requestTranslate.content)
        msg = translate['data']['translations'][0]['translatedText']     
        await message.reply(msg)  
    except Exception as e:
        await message.reply("Selecione mensagem para traduzir") 
        #show error and line of error
        traceback.print_exc()
        
@Client.on_message(filters.command(['en','es','pt']))
async def en(bot, message):
    try:
        msgToTranslate = "Without message to translate"
        if len(message.command) > 1:    
            msgToTranslate = " ".join(message.command[1:])
        else:     
            if message.reply_to_message.caption:
                msgToTranslate = message.reply_to_message.caption
            else:   
                msgToTranslate = message.reply_to_message.text
        msgToTranslate = urllib.parse.quote(msgToTranslate)                        
        requestTranslate = requests.get("https://translation.googleapis.com/language/translate/v2?key="+GOOGLE_TRANSLATE_API_ID+"&q="+msgToTranslate+"&target="+str(message.command[0]))
        translate = json.loads(requestTranslate.content)
        msg = translate['data']['translations'][0]['translatedText']        
        await message.reply(msg)  
    except Exception as e:
        await message.reply("Select message to translate") 
        #show error and line of error
        traceback.print_exc()

async def sumChar (char,key,op,x): 
    if op == "e":
        if x%2 == 0:
            return chr((int(ord(char))+int(ord(key)))%256)
        else:
            return chr((int(ord(char))-int(ord(key)))%256)
    elif op == "d":
        if x%2 == 0:
            return chr((int(ord(char))-int(ord(key)))%256)
        else:
            return chr((int(ord(char))+int(ord(key)))%256)  

async def crypt(text,key,option="e"):
    now = datetime.now()
    if option == "e":
        timestamp = datetime.timestamp(now)
    elif option == "d":
        decoded=base64.b64decode(text).decode()
        timestamp=decoded.split(",")[0]
        text=decoded.replace((str(timestamp)+","),"")
    key = hashlib.sha512( str( key+str(len(text))+str(timestamp) ).encode("utf-8") ).hexdigest()    
    key = list(key)
    keyPosition=0
    keySize=len(key)
    textCrypt=""
    x = 0
    for i in list(text):
        textCrypt+=await sumChar(i,key[keyPosition],option,x)
        keyPosition+=1
        if (keyPosition==keySize):
            key = list( hashlib.sha512( str( "".join(key)+str(x) ).encode("utf-8") ).hexdigest()  ) 
            keySize=len(key)
            keyPosition=0     
        x+=1        
    if option == "e":
        textCrypt = str(base64.b64encode(bytes(str(timestamp)+","+textCrypt,'utf-8')))
        textCrypt=textCrypt.replace("b'","")
        textCrypt=textCrypt[:-1]
        return textCrypt
    return textCrypt

@Client.on_message(filters.command('encrypt'))
async def encrypt(bot, message):
    #get all command and concatenate
    command = message.command
    key=""
    if len(command) > 1:
        key = " ".join(command[1:])
    else:
        await message.reply("Digite a chave de criptografia")
        return
    try:
        text = "Sem mensagem para encriptar"
        if message.reply_to_message.text:
            text = message.reply_to_message.text
        else:   
            text = message.reply_to_message.caption
        textCrypt = await crypt(text,key)
        await message.reply(textCrypt)
    except Exception as e:
        await message.reply("Selecione mensagem para encriptar")

@Client.on_message(filters.command('decrypt'))
async def decrypt(bot, message):
    #get all command and concatenate
    command = message.command
    key=""
    if len(command) > 1:
        key = " ".join(command[1:])
    else:
        await message.reply("Digite a chave de decriptografia")
        return
    try:
        text = "Sem mensagem para decriptografar"
        if message.reply_to_message.text:
            text = message.reply_to_message.text
        else:   
            text = message.reply_to_message.caption
        textCrypt = await crypt(text,key,"d")
        await message.reply(textCrypt)
    except Exception as e:
        #traceback to find line of error
        await message.reply("Selecione mensagem para decriptografar (no formato Base64)")

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

