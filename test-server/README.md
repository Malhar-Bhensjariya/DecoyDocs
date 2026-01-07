# Test Server

Simple Flask server that mimics the production API endpoints for local testing.

## Setup

1. Install dependencies:
```bash
cd test-server
pip install -r requirements.txt
```

## Running the Server

```bash
python app.py
```

The server will start on `http://localhost:5000` and initialize a SQLite database at `test-server/test_honeypot.db`.

## Endpoints

- **POST /api/documents/create** - Register documents (accepts a list of document dictionaries)
- **GET /api/beacon?resource_id=<uuid>** - Trigger beacon (logs to terminal and database)
- **GET /api/stats** - View statistics (document count, beacon hits)
- **GET /health** - Health check

## Usage with Pipeline

To use the test server with `pipeline.py`, set the environment variable:

```bash
export API_BASE_URL=http://localhost:5000
python pipeline.py
```

To switch back to production, unset the variable or set it to production URL:

```bash
unset API_BASE_URL
# or
export API_BASE_URL=https://fyp-backend-98o5.onrender.com
python pipeline.py
```

## Database

The SQLite database (`test_honeypot.db`) contains:
- `documents` table - Registered documents with UUIDs
- `access_logs` table - Beacon trigger events

You can inspect the database using:
```bash
sqlite3 test_honeypot.db
.tables
SELECT * FROM documents;
SELECT * FROM access_logs;
```
