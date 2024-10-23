from pyrogram import Client, idle as idling

from mzcoder.config import Config

# Create a Pyrogram client
client = Client(
    "my_bot",
    api_id=Config.API_ID, 
    api_hash=Config.API_HASH, 
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="mzcoder")
)




idle = idling
