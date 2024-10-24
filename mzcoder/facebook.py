import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
import yt_dlp
from mzcoder.config import Config
from mzcoder.forcesub import handle_force_subscribe

@Client.on_message(filters.regex(r'https?:\/\/(www\.)?(facebook\.com|fb\.me)\/.*'))
async def process_facebook_video_link(client, message):
    if Config.CHANNEL:
        fsub = await handle_force_subscribe(client, message)
        if fsub == 400:
            return
            
    facebook_link = message.text
    video_file = None
    thumbnail_file = None
    try:
        downloading_msg = await message.reply_text("<b><i>Mengunduh video...</i></b>",  parse_mode=ParseMode.HTML)

        # Definisikan hook kemajuan kustom
        def progress_hook(d):
            if d['status'] == 'downloading':
                downloaded_bytes = d.get('downloaded_bytes', 0)
                total_bytes = d.get('total_bytes', 1)

                percent = (downloaded_bytes / total_bytes) * 100 if total_bytes > 0 else 0
                message_text = f"Mengunduh: {percent:.2f}% (Downloaded: {downloaded_bytes / (1024 * 1024):.2f} MB dari {total_bytes / (1024 * 1024):.2f} MB)"
                asyncio.create_task(downloading_msg.edit(message_text))

        # Definisikan opsi untuk yt-dlp
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'writethumbnail': True,
            'noplaylist': True,
            'progress_hooks': [progress_hook],
        }

        os.makedirs('downloads', exist_ok=True)

        # Unduh video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(facebook_link, download=True)
            video_file = ydl.prepare_filename(info_dict)
            thumbnail_file = f'downloads/{info_dict["id"]}.jpg'

        if not os.path.exists(video_file):
            raise FileNotFoundError("File video tidak ditemukan.")
        if not os.path.exists(thumbnail_file):
            raise FileNotFoundError("File thumbnail tidak ditemukan.")

        # Beri tahu bahwa unduhan telah selesai
        uploading_msg = await downloading_msg.edit("Proses upload...")
        await asyncio.sleep(1)

        # Unggah video ke Telegram dengan thumbnail
        with open(video_file, 'rb') as video, open(thumbnail_file, 'rb') as thumb:
            await client.send_video(
                chat_id=message.chat.id,
                video=video,
                thumb=thumb,
                caption=(
                    f"<b>Judul:</b> {info_dict.get('title')}\n"
                    f"<b>Size:</b> {os.path.getsize(video_file) / (1024 * 1024):.2f} MB\n"
                    f"<b>Upload by:</b> @FaceBookDownloadsRobot"
                ),
                parse_mode=ParseMode.HTML
            )

        await uploading_msg.delete()

    except Exception as e:
        if 'downloading_msg' in locals():
            await downloading_msg.edit(f"Terjadi kesalahan saat mengunduh atau mengunggah video: {str(e)}")
        print(f"Error: {e}")

    finally:
        if video_file and os.path.exists(video_file):
            os.remove(video_file)
        if thumbnail_file and os.path.exists(thumbnail_file):
            os.remove(thumbnail_file)

