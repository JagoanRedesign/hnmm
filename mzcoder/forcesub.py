import asyncio
from pyrogram import Client, enums
from mzcoder.config import Config
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

async def handle_force_subscribe(bot: Client, message: Message) -> int:
    try:
        # Create an invite link for the channel
        invite_link = await bot.create_chat_invite_link(int(Config.CHANNEL))
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return 400

    try:
        # Check if the user is a member of the channel
        user = await bot.get_chat_member(int(Config.CHANNEL), message.from_user.id)
        if user.status == "kicked":
            await bot.send_message(
                chat_id=message.from_user.id,
                text="Maaf, Anda telah dibanned. Hubungi [Grup Support](https://t.me/DutabotSupport).",
                disable_web_page_preview=True,
            )
            return 400
    except UserNotParticipant:
        # If the user is not a participant, send them a message
        await bot.send_message(
            chat_id=message.from_user.id,
            text="Halo,\n\nAnda harus bergabung di Channel untuk menggunakan bot.\n\nSilakan join ke channel terlebih dahulu.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Bergabung dengan CHANNEL", url=invite_link.invite_link)
                    ],
                ]
            ),
        )
        return 400
    except Exception as e:
        # Log the exception for debugging
        print(f"Error occurred: {str(e)}")
        await bot.send_message(
            chat_id=message.from_user.id,
            text="Terjadi kesalahan. Hubungi [Grup Support](https://t.me/DutabotSupport).",
            disable_web_page_preview=True,
        )
        return 400
