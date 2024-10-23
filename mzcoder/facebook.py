import os
import asyncio
from pyrogram import Client, filters
import yt_dlp

@Client.on_message(filters.regex(r'^https?:\/\/(www\.)?facebook\.com\/(share\/v|[0-9]+\/videos)\/[A-Za-z0-9]+\/\??.*$'))
async def process_facebook_video_link(client, message):
    facebook_link = message.text
    video_file = None
    thumbnail_file = None
    try:
        # Notify the user that the download is starting
        downloading_msg = await message.reply_text("Downloading video...")

        # Define options for yt-dlp
        ydl_opts = {
            'format': 'best',  # Download the best available quality
            'outtmpl': 'downloads/%(id)s.%(ext)s',  # Save in the downloads folder
            'writethumbnail': True,  # Download the thumbnail
            'noplaylist': True,  # Do not download playlists
        }

        # Create downloads directory if it doesn't exist
        os.makedirs('downloads', exist_ok=True)

        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(facebook_link, download=True)
            video_file = ydl.prepare_filename(info_dict)
            thumbnail_file = f'downloads/{info_dict["id"]}.jpg'  # Assuming the thumbnail is saved as .jpg

        # Notify that the download is complete
        uploading_msg = await downloading_msg.edit("Upload in progress...")

        # Upload the video to Telegram with thumbnail
        await client.send_video(
            chat_id=message.chat.id,
            video=open(video_file, 'rb'),
            thumb=open(thumbnail_file, 'rb'),
            caption=f"Title: {info_dict.get('title')}\n"
                    f"Duration: {info_dict.get('duration')} seconds\n"
                    f"Size: {os.path.getsize(video_file) / (1024 * 1024):.2f} MB"
        )

        await asyncio.sleep(2)

        await uploading_msg.delete()
        # Notify the user of successful upload
        await message.reply_text("Video uploaded successfully!")

    except Exception as e:
        await downloading_msg.edit("An error occurred while downloading or uploading the video.")
        print(e)

    finally:
        # Clean up the downloaded video file
        if video_file and os.path.exists(video_file):
            os.remove(video_file)
        # Clean up the thumbnail file if it exists
        if thumbnail_file and os.path.exists(thumbnail_file):
            os.remove(thumbnail_file)
