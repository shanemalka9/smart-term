import sqlite3
import os
import time
from flask import Flask, request, jsonify

app = Flask(__name__)
DB_FILE = os.path.join(os.getcwd(), 'history.db')

# --- 1. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Table: cmd (text), usage_count (int), last_used (timestamp), is_locked (bool)
    c.execute('''CREATE TABLE IF NOT EXISTS commands 
                 (cmd TEXT PRIMARY KEY, count INTEGER, last_used REAL, is_locked INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

# --- 2. CLEANUP LOGIC (Smart Delete) ---
def cleanup_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Delete commands used only ONCE that are older than 24 hours
    one_day_ago = time.time() - 86400
    c.execute("DELETE FROM commands WHERE count = 1 AND last_used < ?", (one_day_ago,))
    conn.commit()
    conn.close()

# Initialize on startup
init_db()
cleanup_db()

# --- 3. THE API (Logic) ---
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    buffer = data.get('buffer', '')
    cwd = data.get('cwd', '')

    if not buffer: return jsonify({'suggestion': ''})

    # LOGIC A: Context - Empty Folder
    # If folder is empty and user types 'g', suggest git clone
    try:
        if os.path.isdir(cwd) and not os.listdir(cwd):
            if buffer == 'g' or buffer == 'gi':
                return jsonify({'suggestion': 't clone '}) # completes to 'git clone '
    except Exception:
        pass

    # LOGIC B: History Lookup
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Find most frequent command matching input
    c.execute("SELECT cmd FROM commands WHERE cmd LIKE ? ORDER BY count DESC LIMIT 1", (buffer + '%',))
    result = c.fetchone()
    conn.close()

    if result:
        full_cmd = result[0]
        # Return only the part the user hasn't typed yet (ghost text)
        if full_cmd.startswith(buffer):
            return jsonify({'suggestion': full_cmd[len(buffer):]})

    return jsonify({'suggestion': ''})

@app.route('/train', methods=['POST'])
def train():
    data = request.json
    cmd = data.get('cmd')
    if not cmd: return jsonify({'status': 'error'})

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Upsert: Insert or Update count
    c.execute("SELECT count FROM commands WHERE cmd = ?", (cmd,))
    row = c.fetchone()
    if row:
        c.execute("UPDATE commands SET count = count + 1, last_used = ? WHERE cmd = ?", (time.time(), cmd))
    else:
        c.execute("INSERT INTO commands (cmd, count, last_used) VALUES (?, 1, ?)", (cmd, time.time()))
        
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    # Run on localhost port 5005
    app.run(port=5005)