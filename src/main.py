import os
from flask import Flask, request
import telebot
import time
from helper.log import log
from helper.api import apc, get_comic_images, get_comic_info, search, images_to_pdf

app = Flask(__name__)
bot = telebot.TeleBot(os.getenv('bot_token'), threaded=False)
previous_message_ids = []

# Bot route to handle incoming messages
@app.route('/bot', methods=['POST'])
def telegram():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200

# Handler for the '/start' command
@bot.message_handler(commands=['start'])
def start_command(message):
    response_text = "Hello! Welcome to this bot!\n\n"
    response_text += "For help, use the command /help."
    bot.reply_to(message, response_text)

# Handler for the '/help' command
@bot.message_handler(commands=['help'])
def help_command(message):
    response_text = "Here are the available commands:\n\n"
    response_text += "/start - Start the bot.\n"
    response_text += "/help - Show this help message.\n"
    response_text += "/new - View latest Comics.\n"
    response_text += "/s query - search for Comics.\n"
    bot.reply_to(message, response_text)

@bot.message_handler(commands=['new'])
def handle_com(message):
    if message.message_id in previous_message_ids:  
         return  
    previous_message_ids.append(message.message_id)
    full_list = apc()
    for item in full_list:
        cap = item['title'] + '\n' + item['rating'] + '⭐' + '\n' + item['link'] +  '\n\nLatest Chapter\n' + item['chapter'] + '\n' + item['chapter_url']
        image = item['img']
        bot.send_photo(message.chat.id, image, caption = str(cap))
    

@bot.message_handler(func=lambda message: message.text.startswith('https://allporncomic.com/porncomic/'))
def handle_singles(message):
    if message.message_id in previous_message_ids:  
         return  
    previous_message_ids.append(message.message_id)
    
    url = message.text
    parts = url.replace('https://allporncomic.com/porncomic/', '').split('/')
    if len(parts) == 2:
        title, image, summary, rating, genres, chapters = get_comic_info(url)
        bot.send_photo(message.chat.id, image, caption = f'⭕{title}⭕\n\n📖Summary \n{summary} \n\n⭐Rating \n{rating}\n\n🛑Genres\n{genres}')
        response = 'LATEST MANGA RELEASES -> \n\n\n'
        n = 0
        for chapter in chapters:
            n+=1
            response += chapter['title'] + '\n' + chapter['url'] + '\n\n'
            if n % 10 == 0:
                bot.send_message(message.chat.id, response)
                response = ''
        if response != '':
            bot.reply_to(message, response)
            
    if len(parts) == 3:
        images = get_comic_images(url)
        pages = str(len(images)) + ' Pages'
        bot.reply_to(message, pages)
        pdf, passed = images_to_pdf(images, parts[-2])
        caption = f"{passed} Pages were passed" if passed != 0 else "Complete"
        with open(pdf, 'rb') as pdf_file:
            bot.send_document(message.chat.id, pdf_file, caption = caption)
'''     n = 0
        for img in images:
            n+=1
            time.sleep(0.2)
            try:
                bot.send_photo(message.chat.id, img)
            except:
                bot.send_message(message.chat.id, 'pass')
            if n%20 == 0:
                bot.send_message(message.chat.id, f'{n} Pages Completed')
        bot.send_message(message.chat.id, 'Comic Completed')
'''


@bot.message_handler(func=lambda message: message.text.startswith('/s'))
def handle_search(message):
    text = message.text
    query = text.replace('_', ' ').split()
    try:
        n = int(query[0].replace('/s', ''))
    except ValueError:
        n = 1
    query = '+'.join(query[1:]).strip()
    if not query:
        return

    heading, results = search(query, n)
    if not results:
        bot.reply_to(message, "No results found.")
        return

    bot.reply_to(message, heading)  # Assuming results[0] contains the heading

    for item in results:
        caption = f"⭕{item['title']}⭕\n{item['rating']}⭐\n{item['url']}\n\nStatus: {item['status']}\n\n🛑Genres\n{item['genres']}\n\nLatest Chapter\n{item['chapter']}\n{item['chapter_url']}"
        bot.send_photo(message.chat.id, item['image'], caption=caption)

    next_page_command = f"/s{n+1}_{query.replace('+', '_')}"
    bot.reply_to(message, next_page_command)

    
# Handler for any other message
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.reply_to(message, message.text)
