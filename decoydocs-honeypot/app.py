from flask import Flask, request
from datetime import datetime
import sqlite3, json, requests

app = Flask(__name__)

# --- Initialize database ---
def init_db():
    conn = sqlite3.connect('honeypot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                 (uuid TEXT, ip TEXT, ua TEXT, time TEXT, country TEXT, city TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- Geo-IP helper ---
def geo_lookup(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}").json()
        return r.get("country", ""), r.get("city", "")
    except:
        return "", ""

# --- Beacon endpoint ---
@app.route('/beacon/<uuid>')
def beacon(uuid):
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    ua = request.headers.get('User-Agent')
    country, city = geo_lookup(ip)
    now = datetime.utcnow().isoformat()

    conn = sqlite3.connect('honeypot.db')
    c = conn.cursor()
    c.execute("INSERT INTO logs VALUES (?, ?, ?, ?, ?, ?)", (uuid, ip, ua, now, country, city))
    conn.commit()
    conn.close()

    return '', 204  # No content (silent)

@app.route('/')
def home():
    return "DECOYDOCS Honeypot Active"

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=443, ssl_context='adhoc')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)   # dev mode (no SSL here)
