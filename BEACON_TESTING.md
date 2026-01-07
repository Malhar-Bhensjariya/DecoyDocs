# Beacon Testing Guide

## How Beacons Work

The pipeline now embeds **active beacon triggers** that AUTO-TRIGGER when documents are opened:

1. **DOCX files**: **Remote image reference** - When Word/LibreOffice opens the document, it automatically tries to load the remote image from the beacon URL, triggering the beacon!
2. **PDF files**: 
   - **Remote image reference** (primary method - works even if JavaScript is disabled)
   - Invisible link annotation (backup method)
   - JavaScript action (if JavaScript is enabled in PDF viewer)

**KEY INSIGHT**: Using remote images is the most reliable method because document viewers automatically try to load images when documents open, regardless of security settings!

## Testing Setup

### 1. Start Test Server

```bash
cd test-server
pip install -r requirements.txt
python app.py
```

Server runs on `http://localhost:5000` and will log all beacon hits to terminal.

### 2. Run Pipeline with Test Server

```bash
# Set environment variable to use test server
export API_BASE_URL=http://localhost:5000

# Delete old outputs and regenerate
rm -rf out/
python pipeline.py
```

### 3. Test Beacon Triggers

#### Option A: Manual Testing (DOCX and PDF)

1. **For DOCX**: Open a DOCX from `out/*/` folder in Word/LibreOffice
   - Beacon **automatically triggers** when document opens (remote image loads)
   - Check test server terminal for beacon hit

2. **For PDF**: Open a PDF from `out/*/` folder in a PDF viewer
   - Beacon **automatically triggers** when PDF opens (remote image loads)
   - Works even if JavaScript is disabled!

3. Check test server terminal for beacon hit logs:
   ```
   🔔 BEACON TRIGGERED [2025-01-XX XX:XX:XX]
      UUID: <uuid>
      Document: <name>
      IP: <ip>
      User-Agent: <user-agent>
      Method: GET
   ```

#### Option B: Automated Testing

```bash
# Use test_simulation.py to fire beacons explicitly
python test_simulation.py
```

This will:
- Read beacon URLs from `summary_*.json` files
- Explicitly call each beacon URL
- Show results in terminal

#### Option C: Manual URL Testing

```bash
# Get beacon URL from summary file
cat out/Strategy/summary_*.json | grep beacon_url

# Manually trigger (replace <uuid> with actual UUID)
curl "http://localhost:5000/api/beacon?resource_id=<uuid>"
```

## Important Notes

### Remote Image Method (PRIMARY)

The **remote image method** is the most reliable because:
- ✅ Works in DOCX (Word, LibreOffice)
- ✅ Works in PDFs (even with JavaScript disabled)
- ✅ Auto-triggers when document opens
- ✅ No user interaction required
- ✅ Works regardless of security settings

**How it works**: The document contains a reference to a remote image (the beacon URL). When the document opens, the viewer automatically tries to load the image, which triggers the beacon endpoint.

### PDF JavaScript (BACKUP)

JavaScript is a backup method. Many PDF viewers disable it by default, but the remote image method works regardless.

### DOCX Remote Images

Word and LibreOffice will automatically try to load remote images when documents open. This is the primary trigger method for DOCX files.

## Verification

### Check Test Server Logs

The test server terminal will show:
```
📄 Registered document: <uuid> -> <name>
🔔 BEACON TRIGGERED [timestamp]
   UUID: <uuid>
   Document: <name>
   IP: <ip>
   User-Agent: <user-agent>
```

### Check Database

```bash
cd test-server
sqlite3 test_honeypot.db

# View registered documents
SELECT cid, name, file_path FROM documents;

# View beacon hits
SELECT cid, timestamp, ip_address, user_agent FROM access_logs ORDER BY timestamp DESC;

# View statistics
SELECT cid, COUNT(*) as hits FROM access_logs GROUP BY cid;
```

### Check API Stats

```bash
curl http://localhost:5000/api/stats
```

## Production Mode

To switch back to production server:

```bash
unset API_BASE_URL
# or
export API_BASE_URL=https://fyp-backend-98o5.onrender.com
python pipeline.py
```

## Troubleshooting

### Beacons Not Triggering

1. **Check test server is running**: `curl http://localhost:5000/health`
2. **Check API_BASE_URL**: `echo $API_BASE_URL`
3. **Check PDF JavaScript**: Enable in PDF viewer settings
4. **Use test_simulation.py**: Explicitly fires beacons for testing
5. **Check network**: Ensure test server is accessible

### PDF JavaScript Not Working

- Many viewers disable JavaScript for security
- Use `test_simulation.py` as alternative
- Or manually click invisible link on first page
- Or enable JavaScript in PDF viewer settings

### Documents Not Registered

- Check pipeline output for registration errors
- Check test server logs for `/api/documents/create` requests
- Verify `API_BASE_URL` is set correctly
