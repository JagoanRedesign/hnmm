# Gunakan image Python yang ringan
FROM python:3.9-slim

# Set direktori kerja
WORKDIR /app

# Salin file requirements.txt
COPY requirements.txt .

# Update dan install FFmpeg (jika diperlukan) dan dependensi
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Salin sisa kode aplikasi
COPY . .

# Expose port yang digunakan Flask
EXPOSE 8000

# Jalankan aplikasi Flask dan bot dengan supervisord
CMD ["sh", "-c", "python web.py & python main.py"]
