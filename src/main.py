import os
import asyncio
import nest_asyncio
from pyrogram import Client, filters
from helper.log import log
from helper.api import apc_home, apc_comic_images, apc_comic_info, apc_search, images_to_pdf, nh_comic_images, hr_comic_images

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
nest_asyncio.apply()  # Apply nest_asyncio to allow nested event loops

# Retrieve API ID, API Hash, and Bot Token from environment variables
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

previous_message_ids = []

@app.on_message(filters.command('start'))
async def start_command(client, message):
    response_text = "Hello! Welcome to this bot!\n\nFor help, use the command /help."
    await message.reply_text(response_text)

@app.on_message(filters.command('help'))
async def help_command(client, message):
    response_text = (
        "Here are the available commands:\n\n"
        "/start - Start the bot.\n"
        "/help - Show this help message.\n"
        "/new - View latest Comics.\n"
        "/s query - search for Comics.\n"
        "/all {n} comic - Fetch all volumes of the comic, from starting chapter n.\n"
    )
    await message.reply_text(response_text)

@app.on_message(filters.command('new'))
async def handle_com(client, message):
    if message.message_id in previous_message_ids:
        return
    previous_message_ids.append(message.message_id)
    full_list = apc_home()
    for item in full_list:
        cap = (
            f"{item['title']} \n{item['rating']}⭐\n\n"
            f"🌐 <code>{item['link']}</code>\n\n"
            f"Latest Chapter\n{item['chapter']}\n"
            f"📌 <code>{item['chapter_url']}</code>"
        )
        image = item['img']
        await client.send_photo(message.chat.id, image, caption=cap, parse_mode='HTML')

@app.on_message(filters.command('random'))
async def handle_nh_random(client, message):
    if message.message_id in previous_message_ids:
        return
    previous_message_ids.append(message.message_id)

    url = 'https://nhentai.to/random'
    try:
        images = nh_comic_images(url)
        pages = f"{len(images)} Pages"
        await message.reply_text(pages)

        pdf, passed = images_to_pdf(images, url.split('/')[-1])
        caption = f"{passed} Pages were passed" if passed != 0 else "Complete"
        await client.send_document(message.chat.id, pdf, caption=caption)
    except Exception as e:
        await message.reply_text(str(e))

@app.on_message(filters.regex('https://hentairead.com/hentai/'))
async def handle_hr(client, message):
    if message.message_id in previous_message_ids:
        return
    previous_message_ids.append(message.message_id)

    url = message.text
    try:
        images = hr_comic_images(url)
        pages = f"{len(images)} Pages"
        await message.reply_text(pages)

        pdf, passed = images_to_pdf(images, url.split('/')[-1])
        caption = f"{passed} Pages were passed" if passed != 0 else "Complete"
        await client.send_document(message.chat.id, pdf, caption=caption)
    except Exception as e:
        await message.reply_text(str(e))

@app.on_message(filters.regex('https://nhentai.to/g/'))
async def handle_nh(client, message):
    if message.message_id in previous_message_ids:
        return
    previous_message_ids.append(message.message_id)

    url = message.text
    images = nh_comic_images(url)
    pages = f"{len(images)} Pages"
    await message.reply_text(pages)

    pdf, passed = images_to_pdf(images, url.split('/')[-1])
    caption = f"{passed} Pages were passed" if passed != 0 else "Complete"
    await client.send_document(message.chat.id, pdf, caption=caption)

@app.on_message(filters.regex('https://allporncomic.com/porncomic/'))
async def handle_singles(client, message):
    if message.message_id in previous_message_ids:
        return
    previous_message_ids.append(message.message_id)

    url = message.text
    parts = url.replace('https://allporncomic.com/porncomic/', '').split('/')

    try:
        if len(parts) == 2:
            title, image, summary, rating, genres, chapters = apc_comic_info(url)
            await client.send_photo(
                message.chat.id,
                image,
                caption=f'⭕{title}⭕\n\n📖Summary \n{summary} \n\n⭐Rating \n{rating}\n\n🛑Genres\n{genres}'
            )
            response = 'LATEST MANGA RELEASES -> \n\n\n'
            n = 0
            for chapter in chapters:
                n += 1
                response += f"{chapter['title']} \n📌 <code>{chapter['url']}</code> \n\n"
                if n % 10 == 0:
                    await client.send_message(message.chat.id, response, parse_mode='HTML')
                    response = ''
            if response:
                await message.reply_text(response, parse_mode='HTML')

        if len(parts) == 3:
            images = apc_comic_images(url)
            pages = f"{len(images)} Pages"
            await message.reply_text(pages)
            pdf, passed = images_to_pdf(images, parts[-2])
            caption = f"{passed} Pages were passed" if passed != 0 else "Complete"
            await client.send_document(message.chat.id, pdf, caption=caption)
    except Exception as e:
        await message.reply_text(str(e))

@app.on_message(filters.command('s'))
async def handle_search(client, message):
    text = message.text
    query = text.replace('_', ' ').split()
    try:
        n = int(query[0].replace('/s', ''))
    except ValueError:
        n = 1
    query = '+'.join(query[1:]).strip()
    if not query:
        return

    heading, results = apc_search(query, n)
    if not results:
        await message.reply_text("No results found.")
        return

    await message.reply_text(heading)

    for item in results:
        caption = (
            f"⭕{item['title']}⭕\n{item['rating']}⭐\n\n"
            f"🌐 <code>{item['url']}</code>\n\nStatus: {item['status']}\n\n"
            f"🛑Genres\n{item['genres']}\n\n"
            f"Latest Chapter\n{item['chapter']}\n📌 <code>{item['chapter_url']}</code>"
        )
        await client.send_photo(message.chat.id, item['image'], caption=caption, parse_mode='HTML')

    next_page_command = f"/s{n+1}_{query.replace('+', '_')}"
    await message.reply_text(next_page_command)

@app.on_message(filters.command('all'))
async def handle_multiple(client, message):
    if message.message_id in previous_message_ids:
        return
    previous_message_ids.append(message.message_id)

    text = message.text
    query = text.replace('/all', '', 1).strip().split()

    if len(query) > 1:
        n = query[0]
        webcomic = query[1]
    else:
        n = 0
        webcomic = query[0]

    title, image, summary, rating, genres, chapters = apc_comic_info(webcomic)
    await client.send_photo(
        message.chat.id,
        image,
        caption=f'⭕{title}⭕\n\n📖Summary \n{summary} \n\n⭐Rating \n{rating}\n\n🛑Genres\n{genres}'
    )

    chapters.reverse()
    chapters = chapters[int(n):]

    try:
        await client.send_message(message.chat.id, f"{len(chapters)} Chapters")
        for chapter in chapters:
            url = chapter['url']
            title = chapter['title']
            images = apc_comic_images(url)
            pages = f"{title}\n📃 {len(images)} Pages"
            await client.send_message(message.chat.id, pages)
            pdf, passed = images_to_pdf(images, chapter['title'])
            caption = f"{passed} Pages were passed" if passed != 0 else "Complete"
            await client.send_document(message.chat.id, pdf, caption=caption)
    except Exception as e:
        await message.reply_text(str(e))

async def run_bot():
    await app.start()
    print("Bot started.")
    try:
        await asyncio.Event().wait()  # Keeps the bot running
    finally:
        await app.stop()
        print("Bot stopped.")

# Run the bot in the event loop
asyncio.run(run_bot())
