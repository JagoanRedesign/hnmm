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
        # Beri tahu pengguna bahwa pengunduhan sedang dimulai        
        downloading_msg = await message.reply_text("<b><i>Mengunduh video...</i></b>", parse_mode='html')
       
        # Definisikan hook kemajuan kustom
        def progress_hook(d):
            if d['status'] == 'downloading':
                downloaded_bytes = d.get('downloaded_bytes', 0)
                total_bytes = d.get('total_bytes', 1)  # Menghindari pembagian dengan 0

                # Menghitung persentase
                percent = (downloaded_bytes / total_bytes) * 100 if total_bytes > 0 else 0

                # Memperbarui pesan dengan informasi dasar
                message_text = f"Mengunduh: {percent:.2f}% (Downloaded: {downloaded_bytes / (1024 * 1024):.2f} MB dari {total_bytes / (1024 * 1024):.2f} MB)"
                
                # Memperbarui pesan di thread utama
                try:
                    asyncio.create_task(downloading_msg.edit(message_text))
                except Exception as e:
                    print(f"Error editing message: {e}")

        # Definisikan opsi untuk yt-dlp
        ydl_opts = {
            'format': 'best',  # Unduh kualitas terbaik yang tersedia
            'outtmpl': 'downloads/%(id)s.%(ext)s',  # Simpan di folder unduhan
            'writethumbnail': True,  # Unduh thumbnail
            'noplaylist': True,  # Jangan unduh playlist
            'progress_hooks': [progress_hook],  # Tambahkan hook kemajuan kustom
        }

        # Buat direktori unduhan jika belum ada
        os.makedirs('downloads', exist_ok=True)

        # Unduh video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(facebook_link, download=True)
            video_file = ydl.prepare_filename(info_dict)
            thumbnail_file = f'downloads/{info_dict["id"]}.jpg'  # Mengasumsikan thumbnail disimpan sebagai .jpg

        # Periksa apakah file video dan thumbnail ada
        if not os.path.exists(video_file):
            raise FileNotFoundError("File video tidak ditemukan.")
        if not os.path.exists(thumbnail_file):
            raise FileNotFoundError("File thumbnail tidak ditemukan.")

        # Beri tahu bahwa unduhan telah selesai
        uploading_msg = await downloading_msg.edit("<i>Proses upload...</i>")
       
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
                parse_mode='html'
            )
        
        # Beri tahu pengguna bahwa upload berhasil
        await uploading_msg.delete()
        
    except Exception as e:
        if 'downloading_msg' in locals():  # Pastikan downloading_msg ada
            await downloading_msg.edit(f"Terjadi kesalahan saat mengunduh atau mengunggah video: {str(e)}")
        print(f"Error: {e}")  # Cetak kesalahan ke konsol untuk debugging

    finally:
        # Bersihkan file video yang diunduh
        if video_file and os.path.exists(video_file):
            os.remove(video_file)
        # Bersihkan file thumbnail jika ada
        if thumbnail_file and os.path.exists(thumbnail_file):
            os.remove(thumbnail_file)
