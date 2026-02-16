const express = require('express');
const fs = require('fs').promises;
const fSync = require('fs');
const path = require('path');
const { authenticateToken, authenticateTokenAllowDecoy, requireAdmin, requireAdminOrDecoy } = require('./auth');

const router = express.Router();
const STORAGE_DIR = path.join(__dirname, '../storage');

// Ensure storage directory exists
fs.mkdir(STORAGE_DIR, { recursive: true }).catch(console.error);

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
        decoyDocs.push({
          id: docData.id,
          title: docData.title,
          createdAt: docData.createdAt,
          status: docData.status,
          filePath: docData.filePath
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
      throw new Error(`Failed to parse generator output: ${generateOutput}`);
    }

    const generatedDocxPath = generationResult.path;
    if (!fSync.existsSync(generatedDocxPath)) {
      throw new Error(`Generated document not found at ${generatedDocxPath}`);
    }

    // Copy the generated document to storage
    const storageDocName = `${id}_document.docx`;
    const storageDocPath = path.join(STORAGE_DIR, storageDocName);
    fSync.copyFileSync(generatedDocxPath, storageDocPath);

    // Cleanup temp directory
    try {
      fSync.rmSync(tempGenDir, { recursive: true, force: true });
    } catch (e) {
      // Ignore cleanup errors
    }

    const decoyDoc = {
      id,
      title,
      template,
      createdAt: new Date().toISOString(),
      status: 'generated',
      filePath: fileName,
      documentPath: storageDocName,
      contentType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      accessCount: 0
    };

    // Save metadata to JSON file
    await fs.writeFile(filePath, JSON.stringify(decoyDoc, null, 2));

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

      // Delete associated files
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

      res.json({ message: 'DecoyDoc deleted successfully' });
    } catch (fileError) {
      res.status(404).json({ error: 'DecoyDoc not found' });
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