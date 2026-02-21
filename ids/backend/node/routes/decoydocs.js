const express = require('express');
const fs = require('fs').promises;
const fSync = require('fs');
const path = require('path');
const { authenticateToken, authenticateTokenAllowDecoy, requireAdmin, requireAdminOrDecoy } = require('./auth');

const router = express.Router();
const STORAGE_DIR = path.join(__dirname, '../../storage');

// Ensure storage directory exists (persistent location outside the node app folder)
fs.mkdir(STORAGE_DIR, { recursive: true }).catch(console.error);

// External documents registration (optional) and local beacon helpers
const API_BASE_URL = process.env.API_BASE_URL || 'https://fyp-backend-98o5.onrender.com';
const DOCUMENTS_API_URL = `${API_BASE_URL}/api/documents/create`;
const crypto = require('crypto');

function genUUID() {
  if (crypto.randomUUID) return crypto.randomUUID();
  const bytes = crypto.randomBytes(16);
  bytes[6] = (bytes[6] & 0x0f) | 0x40;
  bytes[8] = (bytes[8] & 0x3f) | 0x80;
  return [...bytes].map(b => b.toString(16).padStart(2, '0')).join('').replace(/^(........)(....)(....)(....)(............)$/, '$1-$2-$3-$4-$5');
}

function buildBeaconUrl(uuid, domain = `${API_BASE_URL}/api/beacon`, pathSuffix = '') {
  const nonce = crypto.randomBytes(4).toString('hex').slice(0, 8);
  const q = new URLSearchParams({ resource_id: uuid, nonce });
  return `${domain}${pathSuffix}?${q.toString()}`;
}

function buildFontsBeaconUrl(uuid, domain = `${API_BASE_URL}/fonts`) {
  const fontnames = ["inter-regular.woff2", "roboto-regular.woff2", "opensans-regular.woff2", "lato-regular.woff2"];
  const font = fontnames[Math.floor(Math.random() * fontnames.length)];
  const nonce = crypto.randomBytes(4).toString('hex').slice(0, 8);
  return `${domain}/${font}?${new URLSearchParams({ resource_id: uuid, nonce }).toString()}`;
}

function buildAssetsBeaconUrl(uuid, domain = `${API_BASE_URL}/assets`) {
  const filenames = ["logo.png", "icon.svg", "banner.jpg", "profile.webp", "avatar.png"];
  const file = filenames[Math.floor(Math.random() * filenames.length)];
  const nonce = crypto.randomBytes(4).toString('hex').slice(0, 8);
  return `${domain}/media/${file}?${new URLSearchParams({ resource_id: uuid, nonce }).toString()}`;
}

function buildMixedBeaconUrls(uuid) {
  return {
    beacon: buildBeaconUrl(uuid),
    fonts: buildFontsBeaconUrl(uuid),
    assets: buildAssetsBeaconUrl(uuid)
  };
}

// Get DecoyDocs list (admin only — non-admin/suspicious users are silently served the decoy list)
router.get('/', authenticateTokenAllowDecoy, requireAdminOrDecoy, async (req, res) => {
  try {
    const files = await fs.readdir(STORAGE_DIR);
    const decoyDocs = [];

    for (const file of files) {
      if (file.endsWith('.json')) {
        const filePath = path.join(STORAGE_DIR, file);
        const content = await fs.readFile(filePath, 'utf8');
        const docData = JSON.parse(content);
        // Include beacon-related fields (if present) so decoy clients/attackers can discover them
        decoyDocs.push({
          id: docData.id,
          uuid: docData.uuid || null,
          title: docData.title,
          createdAt: docData.createdAt,
          status: docData.status,
          filePath: docData.filePath,
          beacon: docData.beacon || null,
          beacon_urls: docData.beacon_urls || null
        });
      }
    }

    res.json(decoyDocs);
  } catch (error) {
    console.error('Error reading decoy docs:', error);
    res.status(500).json({ error: error.message });
  }
});

// Create new DecoyDoc (admin only)
// Suspicious/non-admin requests will be rejected for creation
router.post('/create', authenticateToken, requireAdmin, async (req, res) => {
  try {
    const { title, template = 'generic_report' } = req.body;

    if (!title) {
      return res.status(400).json({ error: 'Title is required' });
    }

    console.log(`DecoyDocs.create - request received (title="${title}", template="${template}", user=${req.user?.username || 'unknown'})`);

    const id = Date.now().toString();
    const fileName = `${id}.json`;
    const filePath = path.join(STORAGE_DIR, fileName);

    // Choose Python executable: prefer env PYTHON, then Windows 'py', then 'python'
    const pythonCmd = process.env.PYTHON || (process.platform === 'win32' ? 'py' : 'python3');

    // Generate document using lightweight LLM generator (no heavy dependencies)
    const { spawn } = require('child_process');
    const generatorPath = path.join(__dirname, '../../../../llm-docgen/simple_generate.py');

    // Create temp output directory for this document
    const tempGenDir = path.join(__dirname, '../../../../temp_gen');
    if (!fSync.existsSync(tempGenDir)) {
      fSync.mkdirSync(tempGenDir, { recursive: true });
    }

    const generateProcess = spawn(pythonCmd, [
      generatorPath,
      title,
      template,
      tempGenDir
    ], {
      cwd: path.join(__dirname, '../../../../llm-docgen/'),
      stdio: ['pipe', 'pipe', 'pipe']
    });

    let generateOutput = '';
    let generateError = '';

    generateProcess.stdout.on('data', (data) => {
      generateOutput += data.toString();
    });

    generateProcess.stderr.on('data', (data) => {
      generateError += data.toString();
    });

    await new Promise((resolve, reject) => {
      generateProcess.on('close', (code) => {
        if (code === 0) {
          resolve();
        } else {
          reject(new Error(`Document generation failed: ${generateError}`));
        }
      });
      generateProcess.on('error', reject);
    });

    // Parse the JSON output from simple_generate.py
    let generationResult;
    try {
      generationResult = JSON.parse(generateOutput);
      if (!generationResult.success) {
        throw new Error(generationResult.error || 'Generation failed');
      }
    } catch (parseError) {
      console.error('DecoyDocs.create - failed to parse generator output', parseError, generateOutput);
      throw new Error(`Failed to parse generator output: ${generateOutput}`);
    }

    const generatedDocxPath = generationResult.path;
    if (!fSync.existsSync(generatedDocxPath)) {
      throw new Error(`Generated document not found at ${generatedDocxPath}`);
    }

    console.log('DecoyDocs.create - document generated at', generatedDocxPath);

    // Copy the generated document to storage
    const storageDocName = `${id}_document.docx`;
    const storageDocPath = path.join(STORAGE_DIR, storageDocName);
    fSync.copyFileSync(generatedDocxPath, storageDocPath);
    console.log('DecoyDocs.create - copied generated document to', storageDocPath);

    // Cleanup temp directory
    try {
      fSync.rmSync(tempGenDir, { recursive: true, force: true });
    } catch (e) {
      // Ignore cleanup errors
    }

    // Generate a stable Honey UUID and beacon URLs, embed into DOCX, and register mapping
    const honeyUuid = genUUID();
    const beaconUrls = buildMixedBeaconUrls(honeyUuid);

    const decoyDoc = {
      id,
      uuid: honeyUuid,
      title,
      template,
      createdAt: new Date().toISOString(),
      status: 'generated',
      filePath: fileName,
      documentPath: storageDocName,
      contentType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      accessCount: 0,
      // Expose beacon information for storage- / manifest-based extraction
      beacon: beaconUrls.beacon,
      beacon_urls: beaconUrls
    };

    // Embed HoneyUUID + BeaconURL into the DOCX core properties using the Python helper
    try {
      const pythonCmd = process.env.PYTHON || (process.platform === 'win32' ? 'py' : 'python3');
      const { spawn } = require('child_process');
      const metadataCli = path.join(__dirname, '../../../../embedder/metadata_cli.py');

      // HoneyUUID
      await new Promise((resolve, reject) => {
        const p = spawn(pythonCmd, [metadataCli, storageDocPath, storageDocPath, 'HoneyUUID', honeyUuid]);
        let err = '';
        p.stderr.on('data', d => { err += d.toString(); });
        p.on('error', (e) => reject(e));
        p.on('close', code => code === 0 ? resolve() : reject(new Error(err || 'write HoneyUUID failed')));
      });
      console.log('DecoyDocs.create - embedded HoneyUUID into DOCX');

      // BeaconURL
      await new Promise((resolve, reject) => {
        const p2 = spawn(pythonCmd, [metadataCli, storageDocPath, storageDocPath, 'BeaconURL', beaconUrls.beacon]);
        let err = '';
        p2.stderr.on('data', d => { err += d.toString(); });
        p2.on('error', (e) => reject(e));
        p2.on('close', code => code === 0 ? resolve() : reject(new Error(err || 'write BeaconURL failed')));
      });
      console.log('DecoyDocs.create - embedded BeaconURL into DOCX');

    } catch (e) {
      console.warn('Could not embed DOCX metadata:', e && e.message ? e.message : e);
      // continue — document still stored and registered
    }

    // Save metadata to JSON file (includes uuid + beacon_urls)
    await fs.writeFile(filePath, JSON.stringify(decoyDoc, null, 2));
    console.log('DecoyDocs.create - saved metadata JSON to', filePath);

    // Register mapping with external documents API (best-effort)
    try {
      // NOTE: production expects an array of document objects — we send a list with a single entry
      const registerPayload = [{
        uuid: decoyDoc.uuid,
        file_path: decoyDoc.filePath,
        pdf_path: '',
        document_name: decoyDoc.title,
        created_at: decoyDoc.createdAt
      }];

      const maxAttempts = 3;
      let resp = null;
      let lastErr = null;

      for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        try {
          console.log(`DecoyDocs.create - documents API register attempt ${attempt}/${maxAttempts} payloadSize=${JSON.stringify(registerPayload).length}`);

          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 5000);

          resp = await fetch(DOCUMENTS_API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(registerPayload),
            signal: controller.signal
          });

          clearTimeout(timeoutId);

          // Retry on 5xx (transient server error)
          if (!resp.ok && resp.status >= 500 && attempt < maxAttempts) {
            const t = await resp.text().catch(() => '');
            console.warn(`DecoyDocs.create - documents API returned ${resp.status}, retrying: ${t}`);
            await new Promise(r => setTimeout(r, 300 * Math.pow(2, attempt - 1)));
            continue;
          }

          break; // success or non-retriable status
        } catch (e) {
          lastErr = e;
          console.warn(`DecoyDocs.create - documents API fetch attempt ${attempt} failed: ${e && e.message ? e.message : e}`);
          if (attempt < maxAttempts) await new Promise(r => setTimeout(r, 300 * Math.pow(2, attempt - 1)));
        }
      }

      if (!resp && lastErr) throw lastErr;

      const respText = resp ? await resp.text().catch(() => null) : null;
      let respJson = null;
      try { respJson = respText ? JSON.parse(respText) : null; } catch (e) { respJson = null; }

      console.log('DecoyDocs.create - documents API response:', resp ? resp.status : 'NO_RESPONSE', respText || '');

      // Try to extract returned IDs (support multiple server formats)
      let registeredIds = [];
      if (respJson && typeof respJson === 'object') {
        if (Array.isArray(respJson.resource_ids)) registeredIds = respJson.resource_ids;
        else if (Array.isArray(respJson.registered_uuids)) registeredIds = respJson.registered_uuids;
        else if (respJson.resource_id) registeredIds = [respJson.resource_id];
      }

      if (resp && resp.ok) {
        if (registeredIds.length) {
          console.log('DecoyDocs.create - registered IDs returned by API:', registeredIds);
        } else {
          console.log('DecoyDocs.create - registration OK; no explicit IDs returned by API');
        }

        // Lightweight verification: check beacon endpoint for the new UUID
        try {
          const beaconCheck = await fetch(`${API_BASE_URL}/api/beacon?resource_id=${decoyDoc.uuid}`);
          if (beaconCheck.ok) {
            console.log(`DecoyDocs.create - verification ok: UUID ${decoyDoc.uuid} present on remote server (beacon 200).`);
          } else {
            console.warn(`DecoyDocs.create - verification warning: UUID ${decoyDoc.uuid} not found via beacon (status ${beaconCheck.status}).`);
          }
        } catch (verErr) {
          console.warn('DecoyDocs.create - could not verify UUID via beacon endpoint:', verErr && verErr.message ? verErr.message : verErr);
        }
      } else {
        console.warn('DecoyDocs.create - failed to register with documents API', resp ? resp.status : 'no-response', respText || '');
      }
    } catch (err) {
      console.warn('Error registering decoy doc with documents API:', err && err.message ? err.message : err);
    }

    console.log(`DecoyDocs.create - completed successfully id=${id} uuid=${decoyDoc.uuid}`);

    // Return created doc metadata to caller
    res.status(201).json(decoyDoc);
  } catch (error) {
    console.error('Error creating decoy doc:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get DecoyDoc details (admin only)
router.get('/:id', authenticateToken, requireAdmin, async (req, res) => {
  try {
    const filePath = path.join(STORAGE_DIR, `${req.params.id}.json`);

    try {
      const content = await fs.readFile(filePath, 'utf8');
      const decoyDoc = JSON.parse(content);
      res.json(decoyDoc);
    } catch (fileError) {
      res.status(404).json({ error: 'DecoyDoc not found' });
    }
  } catch (error) {
    console.error('Error reading decoy doc:', error);
    res.status(500).json({ error: error.message });
  }
});

// Update DecoyDoc (admin only)
router.put('/:id', authenticateToken, requireAdmin, async (req, res) => {
  try {
    const { title, content, status } = req.body;
    const filePath = path.join(STORAGE_DIR, `${req.params.id}.json`);

    try {
      const existingContent = await fs.readFile(filePath, 'utf8');
      const decoyDoc = JSON.parse(existingContent);

      // Update fields
      if (title) decoyDoc.title = title;
      if (content) decoyDoc.content = content;
      if (status) decoyDoc.status = status;
      decoyDoc.updatedAt = new Date().toISOString();

      // Save updated metadata
      await fs.writeFile(filePath, JSON.stringify(decoyDoc, null, 2));

      // Update document file if content changed
      if (content && decoyDoc.documentPath) {
        const docFilePath = path.join(STORAGE_DIR, decoyDoc.documentPath);
        await fs.writeFile(docFilePath, content);
      }

      res.json(decoyDoc);
    } catch (fileError) {
      res.status(404).json({ error: 'DecoyDoc not found' });
    }
  } catch (error) {
    console.error('Error updating decoy doc:', error);
    res.status(500).json({ error: error.message });
  }
});

// Delete DecoyDoc (admin only)
router.delete('/:id', authenticateToken, requireAdmin, async (req, res) => {
  try {
    const jsonFilePath = path.join(STORAGE_DIR, `${req.params.id}.json`);

    try {
      const content = await fs.readFile(jsonFilePath, 'utf8');
      const decoyDoc = JSON.parse(content);

      // Delete associated files (JSON + stored document)
      const filesToDelete = [jsonFilePath];
      if (decoyDoc.documentPath) {
        filesToDelete.push(path.join(STORAGE_DIR, decoyDoc.documentPath));
      }

      for (const filePath of filesToDelete) {
        try {
          await fs.unlink(filePath);
        } catch (unlinkError) {
          console.warn(`Could not delete file ${filePath}:`, unlinkError.message);
        }
      }

      // Best-effort: deregister from external documents API if we previously registered a UUID
      if (decoyDoc.uuid) {
        try {
          // Try RESTful delete first (may not be supported by remote)
          const deleteUrl = `${API_BASE_URL}/api/documents/${decoyDoc.uuid}`;
          const delResp = await fetch(deleteUrl, { method: 'DELETE' });
          const delText = await delResp.text().catch(() => null);

          if (delResp.ok) {
            console.log(`DecoyDocs.delete - remote deregistered UUID ${decoyDoc.uuid} via DELETE (status ${delResp.status})`);
          } else {
            console.warn(`DecoyDocs.delete - remote DELETE returned ${delResp.status}: ${delText || ''}`);

            // Fallback: mark as deleted via create endpoint (server may upsert)
            try {
              const fallbackResp = await fetch(DOCUMENTS_API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify([{
                  uuid: decoyDoc.uuid,
                  file_path: '',
                  pdf_path: '',
                  document_name: decoyDoc.title,
                  created_at: decoyDoc.createdAt,
                  metadata: { deleted: true }
                }])
              });

              const fbText = await fallbackResp.text().catch(() => null);
              if (fallbackResp.ok) {
                console.log(`DecoyDocs.delete - fallback deregistration via POST succeeded (status ${fallbackResp.status})`);
              } else {
                console.warn(`DecoyDocs.delete - fallback deregistration failed (${fallbackResp.status}): ${fbText || ''}`);
              }
            } catch (fbErr) {
              console.warn('DecoyDocs.delete - fallback deregistration error:', fbErr && fbErr.message ? fbErr.message : fbErr);
            }
          }
        } catch (err) {
          console.warn('Remote deregistration attempt failed:', err && err.message ? err.message : err);
        }
      }

      console.log(`DecoyDocs.delete - deleted successfully id=${req.params.id} (removed files: ${filesToDelete.join(', ')})`);
      res.json({ message: 'DecoyDoc deleted successfully' });
    } catch (fileError) {
      console.warn(`DecoyDoc delete requested but not found: id=${req.params.id} (${fileError && fileError.message ? fileError.message : fileError})`);
      // If the metadata file is missing treat the DELETE as idempotent (already deleted)
      if (fileError && fileError.code === 'ENOENT') {
        return res.status(200).json({ message: 'DecoyDoc not found (treated as deleted)' });
      }

      // Otherwise surface a server error
      return res.status(500).json({ error: 'Failed to delete DecoyDoc' });
    }
  } catch (error) {
    console.error('Error deleting decoy doc:', error);
    res.status(500).json({ error: error.message });
  }
});

// Download DecoyDoc files (admin only)
router.get('/:id/download/:type', authenticateToken, requireAdmin, async (req, res) => {
  try {
    const jsonFilePath = path.join(STORAGE_DIR, `${req.params.id}.json`);

    try {
      const content = await fs.readFile(jsonFilePath, 'utf8');
      const decoyDoc = JSON.parse(content);

      let filePath, fileName, contentType;

      if (req.params.type === 'json') {
        filePath = jsonFilePath;
        fileName = `${decoyDoc.title.replace(/[^a-zA-Z0-9]/g, '_')}_metadata.json`;
        contentType = 'application/json';
      } else if (req.params.type === 'docx' && decoyDoc.documentPath) {
        filePath = path.join(STORAGE_DIR, decoyDoc.documentPath);
        fileName = `${decoyDoc.title.replace(/[^a-zA-Z0-9]/g, '_')}.docx`;
        contentType = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
      } else if (req.params.type === 'txt' && decoyDoc.documentPath) {
        filePath = path.join(STORAGE_DIR, decoyDoc.documentPath);
        fileName = `${decoyDoc.title.replace(/[^a-zA-Z0-9]/g, '_')}.txt`;
        contentType = 'text/plain';
      } else {
        return res.status(400).json({ error: 'Invalid file type requested' });
      }

      // Check if file exists
      await fs.access(filePath);

      res.setHeader('Content-Type', contentType);
      res.setHeader('Content-Disposition', `attachment; filename="${fileName}"`);

      const fileStream = require('fs').createReadStream(filePath);
      fileStream.pipe(res);

    } catch (fileError) {
      res.status(404).json({ error: 'File not found' });
    }
  } catch (error) {
    console.error('Error downloading file:', error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;