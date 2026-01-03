# DecoyDocs

> Generate, deploy, and monitor realistic LLM-crafted decoy documents with covert tracking and real-time alerting — optimized for Linux and LibreOffice compatibility.

---

## Project Overview

This project produces **LLM-crafted honeytokens** — realistic fake documents (e.g., "2025 Employee Bonuses", HR reports, financial spreadsheets) designed to act as decoys in the event of data exfiltration. Each honeytoken is embedded with multiple covert, resilient triggers (UUID in metadata, beacon URL) and a unique per-file fingerprint. When a document is opened by an unauthorized user, the triggers silently notify a central honeypot server which logs metadata; a real-time dashboard presents alerts, maps geolocation data, and provides analyst workflows.

This repository contains specification, architecture, and an implementation roadmap to build the system. **This project is intended for defensive security teams, red teams running authorized tests, and controlled lab environments.** See the Ethics & Legal section below.

---

## Key Features

* **LLM-based Fake Documents**
  Use Google Gemini API to generate highly realistic, contextual decoy documents tailored to target environments.

* **Multi-layered Covert Triggers**
  Embed UUID and beacon URL in document metadata for stealthy tracking.

* **Per-file Unique Fingerprints**
  Embed a UUID in each generated document so that every file access is attributable to a specific honeytoken.

* **Similarity Enforcement**
  Generate documents with enforced uniqueness using Sentence-BERT embeddings and cosine similarity gates across all documents.

* **LibreOffice Compatibility**
  Documents are optimized for clean opening in LibreOffice Writer and Draw on Linux, using OOXML-compliant formats without Windows-specific features.

* **Real-time Dashboard**
  Visual dashboard (Flask + Grafana or Streamlit) showing live access events, charts, timelines, and logs.

* **Geo-IP Mapping**
  Resolve and display access origins on a map using IP geolocation.

* **Alerting**
  Webhook, email, or push notification integration to notify SOC analysts about suspicious access.

---

## Unique Advantages Over Traditional Honeypots

DecoyDocs differs from typical honeypot systems (e.g., network traps or basic file monitors) by specializing in **document exfiltration detection** with advanced stealth and multi-layered tracking. Key differentiators include:

* **Multi-Trigger Detection**: Combines metadata embedding, beacon URLs, and steganography for robust, hard-to-evade alerts—unlike single-method systems.
* **Per-File Attribution**: Unique UUIDs enable precise tracking of individual documents, providing detailed forensics (e.g., "Document X accessed by IP Y at time Z").
* **Global Similarity Enforcement**: Ensures all documents are unique via AI-powered checks, making decoys more realistic and scalable.
* **Linux & LibreOffice Optimized**: Designed for cross-platform reliability without Windows-specific features like macros, ensuring clean operation in enterprise Linux environments.
* **Decoupled Architecture**: Templates and folders are independent, allowing flexible organization without code changes—ideal for dynamic deployments.
* **Ethical & Passive**: No executable content or active code; focuses on passive tracking for defensive, authorized use only.

These features make DecoyDocs a sophisticated toolkit for blue teams, turning realistic decoy documents into proactive exfiltration detectors.

---

## Architecture Overview

1. **Document Generation**
   - Google Gemini API generates initial documents.
   - Sentence-BERT computes embeddings for similarity checks.
   - RAG-based regeneration ensures 3 unique documents.

2. **Similarity Validation**
   - Cosine similarity threshold (0.80) enforced.
   - Documents rejected if too similar to previous ones.

3. **Embedding**
   - UUID and beacon URL embedded in DOCX custom properties.
   - Only occurs after document acceptance.

4. **Honeypot / Collector Server**
   - Flask API endpoints to receive beacon pings and metadata.
   - Logs IP, timestamp, UUID, and available client metadata.

5. **Dashboard & Analytics**
   - Web UI with real-time event stream, charts, and per-file drilldowns.

6. **Alerting System**
   - Webhooks, email, or push notifications on suspicious events.

---

## Linux Execution Flow

1. Install dependencies: `pip install -r requirements.txt`
2. Set GEMINI_API_KEY in llm-docgen/.env
3. Run pipeline: `python pipeline.py`
4. Pipeline generates 5 unique documents (one per template), embeds metadata, outputs to out/ subfolders
5. Test documents: `libreoffice --headless out/*/*.docx` (should open cleanly)
6. Deploy honeypot server for beacon collection.

---

## Gemini-Based Generation

- Uses Gemini 2.5 Pro for document creation.
- Prompts enforce Markdown output, sanitized for DOCX conversion.
- Avoid lists prevent repetition in regeneration.

---

## Similarity Enforcement Logic

- Documents are generated with enforced uniqueness using Sentence-BERT embeddings and cosine similarity gates.
- Cosine similarity threshold (0.80) enforced across all generated documents, regardless of template or output folder.
- Similarity checks are global and decoupled from folder structure.

---

## Template and Folder Decoupling

- Templates in `llm-docgen/templates.py` are used for convenience in generating varied document types.
- Templates are not authoritative; they serve only the current simulation requirement of generating 5 documents (one per template).
- Output folder names represent logical document categories (e.g., Finance, HR) and are independent of template keys.
- A configurable mapping defines `template_key → output_folder` to place documents in appropriate directories.
- The system is designed to survive folder restructuring without code changes, as paths are resolved explicitly and no directory inference occurs.

---

## Why LibreOffice Compatibility Matters

- Documents must open cleanly in LibreOffice on Linux without warnings.
- Uses Liberation Serif fonts, OOXML-compliant structures.
- No macros, ActiveX, or Windows-specific fields.
- Ensures cross-platform reliability in honeypot deployments.

---

## Current Limitations

- No macros or executable content (ethical and compatibility reasons).
- No Windows triggers; optimized for Linux environments.
- Requires Gemini API key for generation.

---

## Requirements

* Python 3.9+
* Google Gemini API key
* LibreOffice (for testing)
* Linux environment (Ubuntu/Debian recommended)

---

## Usage

1. `pip install -r requirements.txt`
2. Set API key in `llm-docgen/.env`
3. `python pipeline.py`
4. Check `out/` for embedded documents and similarity matrix output.

---

## Ethics, Legal & Safety

* **Authorized Use Only** — Deploy only in controlled environments.
* **No Harm** — No malicious payloads.
* **Privacy** — Non-sensitive metadata only.

---

## Directory Structure

```
/DecoyDocs
├── pipeline.py          # Main orchestrator
├── similarity.py        # Embedding and similarity checks
├── llm-docgen/          # Gemini-based generation
├── embedder/            # Metadata embedding
├── generated_docs/      # Intermediate docs
├── out/                 # Final embedded docs in subfolders (e.g., Finance/, HR/)
│   ├── Finance/
│   ├── HR/
│   ├── Strategy/
│   ├── Sales/
│   └── Engineering/
└── tests/               # Validation scripts
```