# Menggunakan image Python sebagai base
FROM python:3.9-slim

# Mengatur direktori kerja
WORKDIR /app

# Menyalin dependensi
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin kode aplikasi
COPY . .

# Menjalankan aplikasi Flask dan bot
CMD ["bash", "-c", "python web.py & python main.py"]
