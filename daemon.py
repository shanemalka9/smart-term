import sqlite3
import os
import time
from flask import Flask, request, jsonify

app = Flask(__name__)
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'history.db')

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # UPGRADE: We added 'context_path' to the primary key composite
    c.execute('''CREATE TABLE IF NOT EXISTS commands 
                 (cmd TEXT, context_path TEXT, count INTEGER, last_used REAL, 
                 PRIMARY KEY (cmd, context_path))''')
    conn.commit()
    conn.close()

init_db()

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    buffer = data.get('buffer', '')
    cwd = data.get('cwd', '')
    
    if not buffer: return jsonify({'suggestion': ''})

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    suggestion = None

    # SMART STRATEGY: Walk up the directory tree
    # If I am in /a/b/c, check /a/b/c, then /a/b, then /a
    current_path = cwd
    while True:
        c.execute("""
            SELECT cmd FROM commands 
            WHERE context_path = ? AND cmd LIKE ? 
            ORDER BY count DESC LIMIT 1
        """, (current_path, buffer + '%'))
        match = c.fetchone()
        
        if match:
            suggestion = match[0]
            break # Found a context-aware match! Stop looking.
        
        # Stop if we hit the root
        parent = os.path.dirname(current_path)
        if parent == current_path:
            break
        current_path = parent

    # FALLBACK STRATEGY: Global Check
    # Only if we found NOTHING in the entire folder tree
    if not suggestion:
        # Exclude dangerous commands from global suggestions (like git clone)
        # We only want 'safe' globals
        c.execute("""
            SELECT cmd FROM commands 
            WHERE context_path = '*' AND cmd LIKE ? 
            AND cmd NOT LIKE 'git clone%' 
            ORDER BY count DESC LIMIT 1
        """, (buffer + '%',))
        match = c.fetchone()
        if match:
            suggestion = match[0]

    conn.close()

    if suggestion and suggestion.startswith(buffer):
        return jsonify({'suggestion': suggestion[len(buffer):]})

    return jsonify({'suggestion': ''})

@app.route('/train', methods=['POST'])
def train():
    data = request.json
    cmd = data.get('cmd')
    cwd = data.get('cwd') # We now receive the folder path
    
    if not cmd: return jsonify({'status': 'error'})

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # LOGIC: 
    # Generic commands (ls, cd, clear) -> Save as Global ('*')
    # Specific commands (git, npm, docker) -> Save as Local (cwd)
    
    is_generic = cmd.split()[0] in ['ls', 'cd', 'clear', 'exit', 'whoami']
    save_path = '*' if is_generic else cwd

    # Upsert Logic
    c.execute("SELECT count FROM commands WHERE cmd = ? AND context_path = ?", (cmd, save_path))
    row = c.fetchone()
    
    if row:
        c.execute("UPDATE commands SET count = count + 1, last_used = ? WHERE cmd = ? AND context_path = ?", 
                  (time.time(), cmd, save_path))
    else:
        c.execute("INSERT INTO commands (cmd, context_path, count, last_used) VALUES (?, ?, 1, ?)", 
                  (cmd, save_path, time.time()))
        
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(port=5005)