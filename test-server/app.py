#!/usr/bin/env python3
"""
test-server/app.py
Simple Flask server that mimics the production API endpoints for local testing.
- /api/documents/create: Accepts a list of document dictionaries
- /api/beacon: Logs beacon triggers and stores in SQLite
"""

import sqlite3
import json
import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow CORS for local testing

DB_PATH = Path(__file__).parent / "test_honeypot.db"


def init_db():
    """Initialize SQLite database with documents and access_logs tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cid TEXT UNIQUE NOT NULL,
            name TEXT,
            file_path TEXT,
            pdf_path TEXT,
            created_at TEXT,
            metadata TEXT,
            registered_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Access logs table (beacon hits)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER,
            cid TEXT,
            endpoint TEXT,
            method TEXT,
            ip_address TEXT,
            user_agent TEXT,
            query_params TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents(id)
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


@app.route("/api/documents/create", methods=["POST"])
def create_documents():
    """
    Accept a list of document dictionaries and register them.
    Expected format: [{"uuid": "...", "file_path": "...", "document_name": "...", "created_at": "..."}, ...]
    """
    try:
        data = request.get_json()
        
        # Handle both single dict and list of dicts
        if isinstance(data, dict):
            documents = [data]
        elif isinstance(data, list):
            documents = data
        else:
            return jsonify({"error": "Expected JSON object or array of objects"}), 400

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        registered = []

        for doc_data in documents:
            uuid_val = doc_data.get("uuid")
            if not uuid_val:
                continue  # Skip invalid entries

            file_path = doc_data.get("file_path", "")
            pdf_path = doc_data.get("pdf_path", "")
            name = doc_data.get("document_name", "")
            created_at = doc_data.get("created_at", datetime.datetime.now().isoformat())
            metadata = json.dumps(doc_data.get("metadata", {}))

            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO documents (cid, name, file_path, pdf_path, created_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (uuid_val, name, file_path, pdf_path, created_at, metadata))
                registered.append(uuid_val)
                print(f"Registered document: {uuid_val} -> {name}")
            except sqlite3.Error as e:
                print(f"Error registering {uuid_val}: {e}")

        conn.commit()
        conn.close()

        return jsonify({
            "status": "ok",
            "registered_count": len(registered),
            "registered_uuids": registered
        }), 200

    except Exception as e:
        print(f"Error in /api/documents/create: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/beacon", methods=["GET", "POST"])
def beacon():
    """
    Beacon endpoint - logs document access.
    Expects 'resource_id' query parameter.
    """
    try:
        # Get resource_id from query params (GET) or form data (POST)
        resource_id = request.args.get("resource_id") or request.form.get("resource_id")
        
        if not resource_id:
            return jsonify({"error": "resource_id is required"}), 400

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if document exists
        cursor.execute("SELECT id, name FROM documents WHERE cid = ?", (resource_id,))
        doc = cursor.fetchone()

        if not doc:
            conn.close()
            return jsonify({"error": "Document not found"}), 404

        doc_id, doc_name = doc

        # Extract request info
        ip_address = request.remote_addr or request.headers.get("X-Forwarded-For", "unknown")
        user_agent = request.headers.get("User-Agent", "")
        method = request.method
        query_params = json.dumps(dict(request.args))

        # Log the access
        cursor.execute("""
            INSERT INTO access_logs (document_id, cid, endpoint, method, ip_address, user_agent, query_params)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (doc_id, resource_id, "/api/beacon", method, ip_address, user_agent, query_params))

        conn.commit()
        conn.close()

        # Print to terminal for visibility
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n🔔 BEACON TRIGGERED [{timestamp}]")
        print(f"   UUID: {resource_id}")
        print(f"   Document: {doc_name}")
        print(f"   IP: {ip_address}")
        print(f"   User-Agent: {user_agent[:80]}")
        print(f"   Method: {method}")
        print()

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print(f"Error in /api/beacon: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/stats", methods=["GET"])
def stats():
    """Get statistics about registered documents and beacon hits."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM documents")
    doc_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM access_logs")
    log_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT cid, COUNT(*) as hits 
        FROM access_logs 
        GROUP BY cid 
        ORDER BY hits DESC 
        LIMIT 10
    """)
    top_hits = [{"cid": row[0], "hits": row[1]} for row in cursor.fetchall()]

    conn.close()

    return jsonify({
        "documents_registered": doc_count,
        "total_beacon_hits": log_count,
        "top_triggered_documents": top_hits
    }), 200


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "server": "test-server"}), 200


if __name__ == "__main__":
    # Initialize database on startup
    init_db()
    
    print("\n" + "="*60)
    print("🚀 TEST SERVER STARTING")
    print("="*60)
    print(f"Database: {DB_PATH}")
    print("📡 Endpoints:")
    print("   POST /api/documents/create - Register documents")
    print("   GET  /api/beacon?resource_id=<uuid> - Trigger beacon")
    print("   GET  /api/stats - View statistics")
    print("   GET  /health - Health check")
    print("="*60 + "\n")
    
    # Run on all interfaces, port 5000
    app.run(host="0.0.0.0", port=5000, debug=True)
