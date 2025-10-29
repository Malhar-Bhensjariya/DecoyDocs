# DecoyDocs

> Generate, deploy, and monitor realistic LLM-crafted decoy documents with covert tracking and real-time alerting — ethically, safely, and for defensive use only.

---

## Project Overview

This project produces **LLM-crafted honeytokens** — realistic fake documents (e.g., “2025 Employee Bonuses”, HR reports, financial spreadsheets) designed to act as decoys in the event of data exfiltration. Each honeytoken is embedded with multiple covert, resilient triggers (macro, beacon image, stego URL) and a unique per-file fingerprint. When a document is opened by an unauthorized user, the triggers silently notify a central honeypot server which logs metadata; a real-time dashboard presents alerts, maps geolocation data, and provides analyst workflows.

This repository contains specification, architecture, and an implementation roadmap to build the system. **This project is intended for defensive security teams, red teams running authorized tests, and controlled lab environments.** See the Ethics & Legal section below.

---

## Key Features

* **LLM-based Fake Documents**
  Use GPT-4 (or equivalent LLM) to generate highly realistic, contextual decoy documents tailored to target environments.

* **Multi-layered Covert Triggers**
  Embed multiple, redundant triggers in each file (macro, embedded beacon image, stego URL in metadata/images) to increase the chance of detection when the document is opened.

* **Per-file Unique Fingerprints**
  Embed a UUID or unique identifier in each generated document so that every file access is attributable to a specific honeytoken.

* **Tool & System Fingerprinting**
  When triggered, the system collects non-sensitive metadata (Office/app version, basic OS fingerprint, access timestamp, user-agent-like string) to help profile access patterns.

* **Real-time Dashboard**
  Visual dashboard (Flask + Grafana or Streamlit) showing live access events, charts, timelines, and logs.

* **Geo-IP Mapping**
  Resolve and display access origins on a map using IP geolocation.

* **Alerting**
  Webhook, email, or push notification integration to notify SOC analysts about suspicious access.

* **Decay Mechanism (Optional)**
  Optionally make the document unusable after first (or N) access to prevent repeated analysis by a malicious actor.

* **ML-powered Detection Add-ons**

  * Unsupervised anomaly detection on access patterns (e.g., Isolation Forest).
  * Supervised classifier to label accesses (benign vs malicious).
  * LLM-based inference to suggest likely motives for access.
  * Embedding-based document similarity checks (e.g., Sentence-BERT) to ensure honeytokens are distinct and realistic.

---

## Project Novelty

* **LLM-driven Realism** — Most honeytokens are hand-crafted or templated; using modern LLMs allows generation of context-aware, believable decoy content that adapts to target environments.

* **Multi-layered Covert Triggers** — Combining macro + image beacon + stego URL in the same document increases stealth and resilience compared with single-trigger approaches.

* **Integrated Monitoring & Attribution** — A complete pipeline from LLM-generated decoys to per-file attribution, geo-tracking, and analyst alerting — focused specifically on document-based honeypots rather than network-only honeypots.

* **Practical & Deployable** — Designed to be deployable in SMB or enterprise environments (shared drives, email attachments, cloud storage), with an emphasis on safe testing and analyst workflow.

---

## Project Architecture

1. **Document Generator**

   * LLM-driven content generation engine that produces labeled fake documents (titles, bodies, tables, metadata).
   * Adds unique UUID per generated file.

2. **Document Embedder**

   * Embeds covert triggers: macros, beacon references in images, stego payloads in images/metadata.
   * (Implementation notes: embedment methods should be implemented with secure, ethical constraints and sanitized for lab usage.)

3. **Honeypot / Collector Server**

   * Flask (or similar) API endpoints to receive beacon pings and metadata.
   * Logs IP, timestamp, UUID, and available client metadata.

4. **Dashboard & Analytics**

   * Real-time web UI (Streamlit, Grafana, or custom Flask + front-end) to visualize events, maps, and logs.
   * ML services for anomaly detection and classification.

5. **Alerting System**

   * Webhooks, email, or push notifications to SOC tools on suspicious events.

---

## Requirements

* Python 3.9+ (Flask / Streamlit / ML libs)
* Access to an LLM (GPT-4 or equivalent) — use API keys and follow provider terms.
* Secure server (public-facing honeypot endpoint) with TLS for beacon collection.
* GeoIP database or geolocation API for IP -> location resolution.
* Data store (Postgres / SQLite / ELK) for logs.
* Optional: Grafana for dashboards or Streamlit for quick interactive UI.

> **Important:** Do **not** deploy any collection endpoints or beacons that collect sensitive personal data without proper legal review and authorization. Use lab IPs or anonymized data when testing.

---

## Usage (conceptual)

1. **Generate honeytokens** with the LLM generator, specifying document type, tone, and target context.
2. **Embed unique UUID** and covert triggers into each file via the embedder pipeline.
3. **Place honeytokens** into monitored locations (approved shared drives, decoy email recipients in controlled tests).
4. **Monitor dashboard** for alerts when a file is opened — investigate events, geolocation, and fingerprints.
5. **Respond per policy** — ensure incident response and legal teams are engaged for any confirmed adversary behavior.

> Implementation details of embedding triggers are intentionally high-level here. This README focuses on design, ethical deployment, and monitoring. Never use trigger mechanisms to collect private, sensitive, or unlawful data.

---

## Implementation Roadmap (≈ 20 Weeks)

| Phase                                    | Timeline (Weeks) | Deliverables                                                                                                                                             |
| ---------------------------------------- | ---------------: | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Phase 1 — Research & Setup               |         Week 1–2 | Study honeytokens, document macro safety, and steganography techniques; create lab environment and threat model.                                         |
| Phase 2 — LLM Document Generation        |         Week 3–4 | Prototype scripts to generate fake HR/finance documents using an LLM; template library and content controls.                                             |
| Phase 3 — Steganography & Macro Triggers |         Week 5–7 | Implement safe embedder that inserts non-sensitive beacon references and stego markers; macro scaffolding prepared (ethically constrained, non-harmful). |
| Phase 4 — Honeypot Server                |         Week 8–9 | Flask-based collector to receive beacon pings and store events; secure TLS and logging.                                                                  |
| Phase 5 — Fingerprinting & Logging       |       Week 10–11 | Extraction/normalization of available metadata (Office/app version, OS hints); UUID mapping to files.                                                    |
| Phase 6 — Dashboard Development          |       Week 12–14 | Web UI with real-time event stream, charts, and per-file drilldowns (Streamlit/Grafana).                                                                 |
| Phase 7 — Geo-IP Mapping & Alerts        |       Week 15–16 | Integrate GeoIP resolution; implement webhooks/email alerting and alert management.                                                                      |
| Phase 8 — Testing & Red Team Simulation  |       Week 17–18 | Simulated attacker scenarios (authorized), measure detection, false positives, and stealth.                                                              |
| Phase 9 — Reporting & Packaging          |       Week 19–20 | Final report, usage guide, deployment checklist, sanitized demo artifacts and screenshots.                                                               |

---

## Testing & Evaluation

* Run all tests in an isolated lab / VM environment.
* Use synthetic access events and authorized red-team scenarios only.
* Evaluate detection metrics: true positive rate, false positive rate, time-to-alert.
* Test resilience of triggers (document opened in various viewers, platforms).
* Validate ML models with labeled/annotated test logs; avoid using real personal data.

---

## Ethics, Legal & Safety

This project has strong dual-use potential. Please adhere to the following:

* **Authorized Use Only** — Deploy honeytokens only in environments where you have explicit authorization (your organization’s assets with management approval, dedicated test labs, or formal red-team engagements).
* **Privacy Compliance** — Do not collect, store, or transmit personally identifiable information (PII) or sensitive data without legal authorization and appropriate controls.
* **No Harm Policy** — Do not embed payloads that could harm or compromise systems (malware, ransomware, backdoors). The triggers should be benign beacons that report non-sensitive metadata only.
* **Clear Policies** — Ensure SOC, legal, and HR teams are aligned on policy, escalation, and investigative workflows before deployment.
* **Audit & Retention** — Log access for forensic purposes but define retention policies and access controls to logs and dashboards.

If you are unsure whether a deployment is permitted, **do not proceed** without written authorization from your organization’s legal or security leadership.

---

## Extensibility & Add-ons

* Add ML pipelines (Isolation Forest, Random Forest) for anomaly detection and classification.
* Add embedding services for document similarity checks (Sentence-BERT or provider embeddings).
* Integrate with SIEMs (Splunk, Elastic) and SOAR platforms for automated playbooks.
* Add granular quarantining or automated containment workflows (ethical / approved only).

---

## Directory / Component Suggestions

(Implementation maintainers can adopt this structure)

```
/docs
/src
  /generator        # LLM generation scripts (templates, prompt library)
  /embedder         # Non-destructive embedder that adds UUIDs and beacon references
  /collector        # Flask server to receive beacons/log events
  /dashboard        # Streamlit/Grafana configs and UI code
  /ml               # Models for anomaly detection and classification
/tests
/config
README.md
LICENSE
```

---

