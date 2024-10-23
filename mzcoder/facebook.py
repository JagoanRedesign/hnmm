import os
from pyrogram import Client, filters
import yt_dlp

@Client.on_message(filters.regex(r'^https?:\/\/(www\.)?facebook\.com\/(share\/v|[0-9]+\/videos)\/[A-Za-z0-9]+\/\??.*$'))
async def process_facebook_video_link(client, message):
    facebook_link = message.text
    try:
        # Notify the user that the download is starting
        downloading_msg = await message.reply_text("Downloading video...")

        # Define options for yt-dlp
        ydl_opts = {
            'format': 'best',  # Download the best available quality
            'outtmpl': 'downloads/%(id)s.%(ext)s',  # Save in the downloads folder
            'noplaylist': True,  # Do not download playlists
        }

        # Create downloads directory if it doesn't exist
        os.makedirs('downloads', exist_ok=True)

        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(facebook_link, download=True)
            video_file = ydl.prepare_filename(info_dict)

        # Notify that the download is complete
        await downloading_msg.edit("Upload in progress...")

        # Upload the video to Telegram
        await client.send_video(chat_id=message.chat.id, video=video_file)

        # Notify the user of successful upload
        await message.reply_text("Video uploaded successfully!")

    except Exception as e:
        await downloading_msg.edit("An error occurred while downloading or uploading the video.")
        print(e)

    finally:
        # Clean up the downloaded video file
        if os.path.exists(video_file):
            os.remove(video_file)
