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
        downloading_msg = await message.reply_text("Mengunduh video...")

        # Definisikan hook kemajuan kustom
        def progress_hook(d):
            print("Progress data:", d)  # Debugging: cetak data progress

            if d['status'] == 'downloading':
                downloaded_bytes = d.get('downloaded_bytes', 0)
                total_bytes = d.get('total_bytes', 1)  # Menghindari pembagian dengan 0
                speed = d.get('speed', 0) / 1024  # Mengonversi ke KB/detik
                eta = d.get('eta', 0)  # ETA dalam detik

                # Pastikan total_bytes bukan 0 sebelum melakukan pembagian
                if total_bytes > 0:
                    percent = (downloaded_bytes / total_bytes) * 100
                else:
                    percent = 0

                # Memastikan nilai tidak None
                downloaded_mb = downloaded_bytes / (1024 * 1024) if downloaded_bytes is not None else 0
                total_mb = total_bytes / (1024 * 1024) if total_bytes is not None else 1  # Hindari dibagi 0
                progress_bar = '█' * int(percent // 2) + '▒' * (50 - int(percent // 2))
                message_text = (f"Mengunduh: {percent:.2f}%\n"
                                f"[{progress_bar}]\n"
                                f"{downloaded_mb:.2f} MB dari {total_mb:.2f} MB\n"
                                f"Kecepatan: {speed:.2f} KB/detik\n"
                                f"ETA: {int(eta // 3600)}j, {int((eta % 3600) // 60)}m\n")

                # Memperbarui pesan menggunakan asyncio.run_coroutine_threadsafe
                asyncio.run_coroutine_threadsafe(downloading_msg.edit(message_text), client)

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
        uploading_msg = await downloading_msg.edit("Proses upload...")

        # Unggah video ke Telegram dengan thumbnail
        with open(video_file, 'rb') as video, open(thumbnail_file, 'rb') as thumb:
            await client.send_video(
                chat_id=message.chat.id,
                video=video,
                thumb=thumb,
                caption=f"Judul: {info_dict.get('title')}\n"
                        f"Durasi: {info_dict.get('duration')} detik\n"
                        f"Ukuran: {os.path.getsize(video_file) / (1024 * 1024):.2f} MB"
            )

        await asyncio.sleep(2)
        await uploading_msg.delete()
        # Beri tahu pengguna bahwa upload berhasil
        await message.reply_text("Video berhasil diunggah!")

    except Exception as e:
        await downloading_msg.edit(f"Terjadi kesalahan saat mengunduh atau mengunggah video: {str(e)}")
        print(f"Error: {e}")  # Cetak kesalahan ke konsol untuk debugging

    finally:
        # Bersihkan file video yang diunduh
        if video_file and os.path.exists(video_file):
            os.remove(video_file)
        # Bersihkan file thumbnail jika ada
        if thumbnail_file and os.path.exists(thumbnail_file):
            os.remove(thumbnail_file)
