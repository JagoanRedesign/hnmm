import asyncio
from flask import Flask, jsonify
import threading

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'



def run_flask():
    app.run(host='0.0.0.0', port=8000)

if __name__ == "__main__":
    # Menggunakan event loop default
    #loop = asyncio.get_event_loop()
    
    # Menjalankan Flask di thread terpisah
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    # Menjalankan bot di event loop utama
   # loop.run_until_complete(main())
    
    # Tunggu hingga thread Flask selesai sebelum keluar
    flask_thread.join()

