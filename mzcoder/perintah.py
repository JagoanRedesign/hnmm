from pyrogram import Client, filters
import datetime
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from mzcoder.config import Config
from mzcoder.text import Translation
from .user_management import add_user, get_all_users
#from mzcoder.forcesub import handle_force_subscribe



# Calculate current time greeting
currentTime = datetime.datetime.now()
if currentTime.hour < 12:
    wish = "Good morning 🌞"
elif 12 <= currentTime.hour < 18:
    wish = "Good afternoon 🌤️"
else:
    wish = "Good evening 🌝"



@Client.on_callback_query(filters.regex("cancel"))
async def cancel(client, callback_query):
    await callback_query.message.delete()

# About command handler
@Client.on_message(filters.private & filters.command("about"))
async def about(client, message):
   # if Config.CHANNEL:
     # fsub = await handle_force_subscribe(client, message)
      #if fsub == 400:
      #  return
    add_user(message.from_user.id)
    await message.reply_text(
        text=Translation.ABOUT_TXT,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('Close', callback_data='cancel')]
        ]
    ))


# Start command handler
@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):

    #if Config.CHANNEL:
      #fsub = await handle_force_subscribe(client, message)
      #if fsub == 400:
        #return
    #user = message.from_user
    add_user(message.from_user.id)
    await message.reply_text(
        text=Translation.START_TEXT.format(message.from_user.first_name),
        reply_markup=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('Update Channel', url='https://t.me/dutabotid'),
            ],
            [
                InlineKeyboardButton('Developer', url='https://t.me/MzCoder'),
                InlineKeyboardButton('Support Group', url='https://t.me/DutabotSupport'),
            ],
            [
                InlineKeyboardButton('Close', callback_data='cancel')
            ]
        ]
    ))

# Help command handler
@Client.on_message(filters.command("help"))
async def help(client, message):
    add_user(message.from_user.id)
    await message.reply_text(text=Translation.HELP_TEXT)
                   
