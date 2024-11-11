import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from yt_api import Youtube

TOKEN = "BOT TOKEN" # What is a token and how to get it: https://core.telegram.org/bots
BOT = Bot(token = TOKEN, default = DefaultBotProperties(parse_mode=ParseMode.HTML))
DP = Dispatcher()

API_KEY = "YOUTUBE API KEY" # What is an API key and how to get it: https://developers.google.com/youtube/v3/getting-started
YOUTUBE = Youtube(api_key = API_KEY)

@DP.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(text = html.bold("Hello, I am Search YouTube Playlists Bot! I was created for fast and convenient search of playlists on YouTube directly in Telegram. ▶️\n\nType any query and I will show you the best playlists on the topic that interests you! 🙂"))

ANSWER_MSG_FRST_PART = "Do you want to find a playlists for the query"

@DP.message()
async def answer_handler(message: Message) -> None:
    if message.chat.type == 'private' and message.text:
        query = message.text
        print(f"From user {message.from_user.full_name} with chat id - {message.chat.id}: '{query}'") # Information for host
        b_yes = InlineKeyboardButton(text = "Yes", callback_data = "yes")
        b_no = InlineKeyboardButton(text = "No", callback_data = "no")
        keyboard = InlineKeyboardMarkup(inline_keyboard = [[b_yes, b_no]])
        await message.answer(text = html.bold(ANSWER_MSG_FRST_PART) + html.italic(f' "{query}" ') + html.bold("?"), reply_markup = keyboard)

def get_query(message: Message) -> str: # Function that gets a query from message
    return message.text[(len(ANSWER_MSG_FRST_PART) + 2) : (len(message.text) - 3)]

def get_playlists_info(playlists: list) -> list:
    all_playlists_info = []
    for playlist in playlists['items']:
        all_playlists_info.append(Youtube.Playlist(playlist = playlist, api_key = API_KEY))
    return all_playlists_info

async def show_results(playlists_info: list, call: CallbackQuery) -> None:
    msg = ""
    number = 1
    for playlist_info in playlists_info:
        playlist_info : Youtube.Playlist 
        msg += f"{number}. {playlist_info.title}\n\n"
        msg += f"Number of videos: {playlist_info.video_count}\n"
        msg += f"Total number of likes: {playlist_info.summary_like_count}\n"
        msg += f"Total number of comments: {playlist_info.summary_comment_count}\n"
        msg += f"Total duration: {playlist_info.summary_duration_hours}h {playlist_info.summary_duration_minutes}m {playlist_info.summary_duration_seconds}s\n"
        msg += f"Link: {playlist_info.url}\n\n\n"
        number += 1
    await call.message.answer(text = html.bold(msg), disable_web_page_preview = True)
    
@DP.callback_query()
async def callback_handler(call: CallbackQuery) -> None:
    if call.data == "yes":
        query = get_query(message = call.message)
        await call.message.edit_text(text = html.bold(ANSWER_MSG_FRST_PART) + html.italic(f' "{query}" ') + html.bold("?") + html.bold("\n\nPlease, wait..."))
        playlists = YOUTUBE.search_playlists(query = query)
        playlists_validation_result = YOUTUBE.playlists_validator(playlists = playlists)
        match playlists_validation_result:
            case 2:
                await call.message.answer(text = html.bold("Something went wrong, most likely the quota was exhausted. Try again later!"))
            case 1:
                await call.message.answer(text = html.bold("Sorry, no playlists found for your query!"))
            case 0:
                try:
                    playlists_info = get_playlists_info(playlists = playlists)
                    await show_results(playlists_info = playlists_info, call = call)
                except Exception as e:
                    await call.message.answer(text = html.bold("Something is wrong, try again later!"))
                    print(f"Error: {e}")
        await call.message.edit_text(text = html.bold(ANSWER_MSG_FRST_PART) + html.italic(f' "{query}" ') + html.bold("?") + html.bold("\n\nResults for your query below..."))
    elif call.data == "no":
        await call.message.delete()
    await call.answer()

async def bot_stop() -> None:
    await BOT.session.close()
    await DP.stop_polling()
    print("The bot has been stopped")

async def await_stop_command() -> None: # Function that allows to stop a bot
    msg = "Print 'stop' to stop the bot"
    print(msg)
    while True:
        command = await asyncio.to_thread(input)
        if command.strip() == "stop":
            await bot_stop()
            break
        else:
            print(msg)

async def main() -> None:
    await asyncio.gather(DP.start_polling(BOT), await_stop_command())
    exit()

if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    asyncio.run(main())