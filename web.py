from flask import Flask

# Membuat instance aplikasi Flask
app = Flask(__name__)

# Mendefinisikan endpoint root (/) yang akan merespons permintaan HTTP GET
@app.route('/')
def hello():
    return jsonify({"message": "Bot is running! by Mz"})
  # Mengembalikan pesan dan kode status 200

# Mendefinisikan endpoint /health untuk pemeriksaan kesehatan

# Menjalankan aplikasi Flask pada host dan port tertentu
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
