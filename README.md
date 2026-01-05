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
   - Iterative prompt refinement with similarity feedback ensures unique documents.

2. **Similarity Validation**
   - Cosine similarity threshold (0.80) enforced.
   - Documents rejected if too similar to previous ones.

3. **Embedding**
   - UUID and beacon URL embedded in DOCX custom properties.
   - Only occurs after document acceptance.

4. **Honeypot / Collector Server**
   - Django REST Framework API endpoints that masquerade as SaaS asset servers (fonts, images, configs).
   - Logs every access with detailed client fingerprinting, IP geolocation, and metadata.
   - Provides a real-time dashboard for monitoring access events.

5. **Dashboard & Analytics**
   - Web UI with real-time event stream, charts, and per-file drilldowns.

6. **Alerting System**
   - Webhooks, email, or push notifications on suspicious events.

---

## Honeypot Server

The honeypot server is a Django-based web application that acts as a stealth document tracking system. It provides API endpoints that appear to be standard SaaS infrastructure (asset delivery, configuration, telemetry) but actually log and analyze document access events with comprehensive client fingerprinting.

### Server Features

* **Stealth Endpoints**: Masquerades as normal SaaS traffic (fonts, images, CSS, JSON configs, telemetry).
* **Comprehensive Logging**: Captures IP address, geolocation, user agent parsing, OS/browser detection, client application info, and request metadata.
* **Real-time Dashboard**: Web interface showing access events, statistics, charts, and document drilldowns.
* **API Documentation**: Interactive Swagger/ReDoc interfaces for all endpoints.
* **Deployment Ready**: Supports Heroku, Render, and traditional server deployments with PostgreSQL.

### Key Endpoints

- `/assets/media/{filename}` - Serves transparent PNGs while logging access
- `/config/runtime.json` - Returns fake UI configs
- `/telemetry/events` - Accepts telemetry data
- `/fonts/{fontname}.woff2` - Serves minimal font files
- `/dashboard/` - Monitoring dashboard

### Data Captured

Each access event logs:
- Network: IP, ASN, ISP, geolocation, proxy/TOR detection
- Application: User-Agent, Accept headers, OS/browser/client details
- Request: Endpoint, method, query params, body
- Correlation: Document CID, first access flag, session tracking

---

## Full Project Implementation Flow

## Linux Execution Flow

1. Install dependencies: `pip install -r requirements.txt`
2. Set GEMINI_API_KEY in llm-docgen/.env
3. Run pipeline: `python pipeline.py`
4. Pipeline generates 5 unique documents (one per template), embeds metadata, outputs to out/ subfolders
5. Test documents: `libreoffice --headless out/*/*.docx` (should open cleanly)
6. Deploy honeypot server: `cd honeypot-server && pip install -r requirements.txt && python manage.py migrate && python manage.py runserver`
7. Update embedder with live server URLs and re-embed documents
8. Deploy documents to target environments and monitor via dashboard at `/dashboard/`

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
* Google Gemini API key (for document generation)
* LibreOffice (for testing document compatibility)
* Linux environment (Ubuntu/Debian recommended)
* PostgreSQL (for production honeypot server deployment)
* Cloud hosting platform (Heroku, Render, etc. for server deployment)

---

## Usage

1. `pip install -r requirements.txt`
2. Set API key in `llm-docgen/.env`
3. `python pipeline.py`
4. Check `out/` for embedded documents and similarity matrix output.
5. Deploy honeypot server: `cd honeypot-server && pip install -r requirements.txt && python manage.py migrate && python manage.py runserver`
6. Access dashboard at `http://localhost:8000/dashboard/`

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
├── honeypot-server/     # Django tracking server
├── generated_docs/      # Intermediate docs
├── out/                 # Final embedded docs in subfolders (e.g., Finance/, HR/)
│   ├── Finance/
│   ├── HR/
│   ├── Strategy/
│   ├── Sales/
│   └── Engineering/
└── tests/               # Validation scripts
```