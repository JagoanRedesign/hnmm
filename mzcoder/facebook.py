import os
import asyncio
import requests
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from mzcoder.config import Config
from mzcoder.forcesub import handle_force_subscribe
from moviepy.editor import VideoFileClip

def get_url(vid_url):
    # ... (fungsi ini tetap sama)

def extract_thumbnail(video_file, thumbnail_file):
    with VideoFileClip(video_file) as video:
        # Ambil frame pada detik ke-1 sebagai thumbnail
        video.save_frame(thumbnail_file, t=1)

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
        # Notify the user that the download is starting
        downloading_msg = await message.reply_text("<b><i>Mengunduh video...</i></b>", parse_mode=ParseMode.HTML)

        # Fetch the high-quality download link
        high_quality_link = get_url(facebook_link)
        if not high_quality_link:
            await downloading_msg.edit("Gagal mendapatkan link unduhan.")
            return

        # Download video using the high-quality link
        downloading_msg = await downloading_msg.edit("<b><i>Video sedang diunduh...</i></b>", parse_mode=ParseMode.HTML)
        video_file = "downloads/video.mp4"
        os.makedirs('downloads', exist_ok=True)

        # Download the video file
        response = requests.get(high_quality_link)
        if response.status_code == 200:
            with open(video_file, 'wb') as f:
                f.write(response.content)
        else:
            await downloading_msg.edit("Gagal mengunduh video dari link yang diberikan.")
            return

        # Ekstrak thumbnail dari video
        thumbnail_file = "downloads/thumbnail.jpg"
        extract_thumbnail(video_file, thumbnail_file)

        # Mengambil durasi video
        duration = None
        with VideoFileClip(video_file) as video:
            duration = video.duration  # Durasi dalam detik

        # Notify that the download is complete
        uploading_msg = await downloading_msg.edit("Proses upload...")
        await asyncio.sleep(1)

        # Upload video to Telegram with thumbnail
        with open(video_file, 'rb') as video:
            with open(thumbnail_file, 'rb') as thumb:
                await client.send_video(
                    chat_id=message.chat.id,
                    video=video,
                    thumb=thumb,
                    caption=(
                        f"<b>Size:</b> {os.path.getsize(video_file) / (1024 * 1024):.2f} MB\n"
                        f"<b>Duration:</b> {duration:.2f} seconds\n"
                        f"<b>Upload by:</b> @FaceBookDownloadsRobot"
                    ),
                    parse_mode=ParseMode.HTML
                )

        await uploading_msg.delete()

    except Exception as e:
        if 'downloading_msg' in locals():  # Ensure downloading_msg exists
            print(f"Error: {e}")  # Print error to console for debugging
            await downloading_msg.edit(f"Terjadi kesalahan saat mengunduh atau mengunggah video: {str(e)}")
        
    finally:
        # Clean up the downloaded video file
        if video_file and os.path.exists(video_file):
            os.remove(video_file)
        # Clean up the thumbnail file if it exists
        if thumbnail_file and os.path.exists(thumbnail_file):
            os.remove(thumbnail_file)
