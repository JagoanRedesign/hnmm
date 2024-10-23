from pyrogram import Client
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
if __name__ == "__main__":
    print("Bot is running...")
    app.run()
