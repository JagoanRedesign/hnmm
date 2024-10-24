import contextlib
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram import errors

YOUR_ADMIN_USER_ID = 5166575484  # Ganti dengan ID admin Anda

@Client.on_message(filters.command("broadcast") & filters.user(YOUR_ADMIN_USER_ID))
async def broadcast_command(client, message):
    # Ambil pesan dari perintah
    msg = message.reply_to_message or (message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None)
    
    if not msg:
        return await message.reply("Silakan berikan pesan atau balas pesan yang ada!")

    load = await message.reply("Proses broadcast kepada pengguna...")
    done = error = 0
    private_chat_ids = []

    # Hanya ambil ID chat dari private chat
    async for dialog in client.get_dialogs():
        if dialog.chat.type == ChatType.PRIVATE:  # Hanya ambil chat pribadi
            private_chat_ids.append(dialog.chat.id)

    async def send_broadcast(chat_id):
        nonlocal done, error
        try:
            if msg.reply_to_message:
                await msg.copy(chat_id)
            else:
                await client.send_message(chat_id, msg.text)  # Menggunakan .text untuk mengirim teks
            done += 1
            if done % 4 == 0:
                await asyncio.sleep(2)
        except errors.FloodWait as f:
            await asyncio.sleep(f.value + 1)  # Menunggu sesuai waktu yang diberikan
            await send_broadcast(chat_id)  # Mengulangi pengiriman setelah delay
        except Exception as e:
            print(f"Error sending to {chat_id}: {e}")
            error += 1

    for chat_id in private_chat_ids:
        await send_broadcast(chat_id)

    if done:
        return await load.edit(f"<i>Broadcast telah dikirim ke {done} pengguna, gagal dikirim ke {error} pengguna.</i>")
    else:
        await load.edit("Tidak ada pengguna untuk dikirimi broadcast.")
