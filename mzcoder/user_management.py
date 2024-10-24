import sqlite3

# Membuat dan menghubungkan ke database SQLite
def create_connection():
    conn = sqlite3.connect('users.db')
    return conn

# Membuat tabel jika belum ada
def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()

# Menambahkan ID pengguna ke database
def add_user(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

# Mengambil semua ID pengguna dari database
def get_all_users():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users')
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

# Memanggil fungsi untuk membuat tabel saat plugin di-load
create_table()
