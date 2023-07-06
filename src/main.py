import os
from flask import Flask, request
import telebot
from helper.log import log
from helper.api import fn_org, apc, get_comic

app = Flask(__name__)
bot = telebot.TeleBot(os.getenv('bot_token'), threaded=False)
bot.set_webhook(url=os.getenv('webhook_url'))

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
    bot.reply_to(message, response_text)

@bot.message_handler(commands=['com'])
def handle_com(message):
    full_list = apc()
    for item in full_list:
        caption = item['title'] + '\n' + item['rating'] + '⭐' + '\n' + item['link'] +  '\n\nLatest Chapter\n' + item['chapter'] + '\n' + item['chapter_url']
        image = item['img']
        bot.send_photo(message.chat.id, image, caption = caption)
    

@bot.message_handler(func=lambda message: message.text.startswith('https://allporncomic.com/porncomic/'))
def handle_singles(message):
    url = message.text
    parts = url.replace('https://allporncomic.com/porncomic/', '').split('/')
    if len(parts) == 2:
        bot.reply_to(message, 'Hello')
    if len(parts) == 3:
        images = get_comic(url)
        for img in images:
            bot.send_photo(message.chat.id, img)

@bot.message_handler(func=lambda message: message.text.startswith('/new'))
def handle_fn(message):
    query = message.text.split('_')
    if len(query) == 1:
        page = '1'
    else:
        page = query[1]
    full_list = fn_org(page)
    for item in full_list:
        title = item['title']
        image = item['img']
        bot.send_photo(message.chat.id, image, caption = title)
    try:
        bot.reply_to(message, f'/new_{(int(page) + 1)}')
    except:
        bot.reply_to(message, 'Usage : /new_<number>')

# Handler for any other message
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.reply_to(message, message.text)
