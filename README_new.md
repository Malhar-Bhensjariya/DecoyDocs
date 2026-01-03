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
  Generate 3 documents with enforced uniqueness using Sentence-BERT embeddings and cosine similarity gates.

* **LibreOffice Compatibility**
  Documents are optimized for clean opening in LibreOffice Writer and Draw on Linux, using OOXML-compliant formats without Windows-specific features.

* **Real-time Dashboard**
  Visual dashboard (Flask + Grafana or Streamlit) showing live access events, charts, timelines, and logs.

* **Geo-IP Mapping**
  Resolve and display access origins on a map using IP geolocation.

* **Alerting**
  Webhook, email, or push notification integration to notify SOC analysts about suspicious access.

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
4. Pipeline generates 3 unique documents, embeds metadata, outputs to out/
5. Test documents: `libreoffice --headless out/*.docx` (should open cleanly)
6. Deploy honeypot server for beacon collection.

---

## Gemini-Based Generation

- Uses Gemini 2.5 Pro for document creation.
- Prompts enforce Markdown output, sanitized for DOCX conversion.
- Avoid lists prevent repetition in regeneration.

---

## Similarity Enforcement Logic

- Document 1: Generated freely.
- Document 2: If similarity >= 0.80 to Doc 1, regenerate with avoid lists from Doc 1.
- Document 3: Compare to Doc 1 and 2, aggregate avoid lists.
- Loop until 3 unique documents exist.

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
├── out/                 # Final embedded docs
└── tests/               # Validation scripts
```