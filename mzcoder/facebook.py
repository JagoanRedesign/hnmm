import os
import asyncio
import requests
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from mzcoder.config import Config
from mzcoder.forcesub import handle_force_subscribe
from moviepy.editor import VideoFileClip

def get_url(vid_url):
    try:
        base_url = "https://facebook-video-downloader.fly.dev/app/main.php"
        payload = {'url': vid_url}
        
        response = requests.post(base_url, data=payload)
        print(f"Response status code: {response.status_code}")  # Log status kode

        if response.status_code == 200:
            response_data = response.json()
            download_links = response_data.get("links", {})
            high_quality_link = download_links.get("Download High Quality")
            return high_quality_link
        else:
            print("Error: Unable to fetch data from the server.")
            return None

    except Exception as e:
        print(f"😴 Gagal mengambil data url: {e}")
        return None

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

        # Download the video file with progress tracking
        response = requests.get(high_quality_link, stream=True)  # Gunakan stream=True untuk pelacakan kemajuan
        total_size = int(response.headers.get('content-length', 0))  # Dapatkan ukuran total video
        downloaded_size = 0

        with open(video_file, 'wb') as f:
            for data in response.iter_content(chunk_size=4096):
                f.write(data)
                downloaded_size += len(data)
                
                # Update pesan setiap 4 MB
                if downloaded_size % (4 * 1024 * 1024) < len(data):  # Cek apakah sudah mencapai 4 MB
                    await downloading_msg.edit(f"Sedang mengunduh... {downloaded_size / (1024 * 1024):.2f} MB dari {total_size / (1024 * 1024):.2f} MB")

        # Ekstrak thumbnail dari video
        thumbnail_file = "downloads/thumbnail.jpg"
        extract_thumbnail(video_file, thumbnail_file)

        # Mengambil durasi video
        duration = None
        with VideoFileClip(video_file) as video:
            duration = video.duration  # Durasi dalam detik

        # Notify that the upload is starting
        uploading_msg = await downloading_msg.edit("Proses upload...")
        await asyncio.sleep(1)

        # Upload video to Telegram with thumbnail
        caption = (
            f"<b>Size:</b> {os.path.getsize(video_file) / (1024 * 1024):.2f} MB\n"
            f"<b>Duration:</b> {duration:.2f} seconds\n"
            f"<b>Upload by:</b> @FaceBookDownloadsRobot"
        )

        uploaded_size = 0
        await client.send_video(
            chat_id=message.chat.id,
            video=video_file,  # Path file video
            thumb=thumbnail_file,
            caption=caption,
            parse_mode=ParseMode.HTML,
            supports_streaming=True
        )

        await uploading_msg.delete()

    except Exception as e:
        if 'downloading_msg' in locals():  # Pastikan downloading_msg ada
            print(f"Error: {e}")  # Cetak kesalahan ke konsol untuk debugging
            await downloading_msg.edit(f"Terjadi kesalahan saat mengunduh atau mengunggah video: {str(e)}")

    finally:
        # Hapus file video yang diunduh
        if video_file and os.path.exists(video_file):
            os.remove(video_file)
        # Hapus file thumbnail jika ada
        if thumbnail_file and os.path.exists(thumbnail_file):
            os.remove(thumbnail_file)
