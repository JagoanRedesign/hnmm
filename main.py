from pyrogram import Client, filters
from mzcoder.config import Config

# Create a Pyrogram client
app = Client(
    "my_bot",
    api_id=Config.API_ID, 
    api_hash=Config.API_HASH, 
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="mzcoder")
)



# Start the bot
print("I AM ALIVE")
app.run()
