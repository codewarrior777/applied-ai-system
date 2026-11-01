# 🐾 PawPal+ — Applied AI System

[![Live Demo](https://img.shields.io/badge/demo-LIVE-brightgreen?style=for-the-badge&logo=streamlit)](https://pawpal-plus-esqzqdlgrnnjsezv6a7r4f.streamlit.app)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/codewarrior777/applied-ai-system/actions)
[![Lint](https://img.shields.io/badge/lint-passing-brightgreen)](https://github.com/codewarrior777/applied-ai-system/actions)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/codewarrior777/applied-ai-system)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://github.com/codewarrior777/applied-ai-system)
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/codewarrior777/applied-ai-system)

A CLI-first and Web-based Python application for managing pets, their care tasks, and scheduling them intelligently. 

This project is an evolution of **PawPal+ (Module 2)**, upgraded for the **Applied AI System Capstone (Module 4)**. It integrates a true **Agentic AI Workflow** to parse natural language, protected by a robust **Guardrail Architecture**.

**Course:** AI 110 — Foundations of AI Engineering
**Project:** Capstone (Applied AI System)

---

## 🌐 Try It Live

**[▶ Open the Applied AI System on Streamlit Cloud](https://pawpal-plus-esqzqdlgrnnjsezv6a7r4f.streamlit.app)**

No installation needed — just click and use it in your browser.

---

## 📌 What It Does

PawPal+ lets a pet owner:

- Register multiple pets under their name.
- Add care tasks to each pet (walks, feeding, meds, vet visits).
- **Parse tasks from natural language using an LLM Agent** (via OpenRouter).
- View a **combined daily schedule** across all pets.
- **Sort** tasks chronologically by time or by priority.
- **Detect scheduling conflicts** and overlapping 30-minute windows.
- **Find the next available slot** in the day for a new task.

---

## 🧠 The Capstone AI Upgrade (Agentic Workflow & Guardrails)

For this Capstone, the original Regex-based parser was upgraded to an **AI Agent**. 

### How It Works
1. **The Agent:** When you type a task (e.g., *"Take Cooper for a walk at 6:30pm daily, it's urgent"*), the app sends it to a free LLM via **OpenRouter**.
2. **The JSON Parser:** The LLM is strictly prompted to return a structured JSON object (description, time, frequency, priority, pet_name).
3. **The Guardrails:** To make this "production-ready", we built three layers of safety:
   - **Markdown Stripping:** Cleans any accidental ` ```json ` formatting the LLM adds.
   - **Strict Time Validation:** A Python Regex checks the LLM's output to ensure the time is a valid `HH:MM` format. It rejects hallucinations like "25:00".
   - **Hallucination Check:** Ensures the pet name extracted by the AI actually exists in the user's database.

### The Ultimate Reliability Test: The Fallback
During development, the free LLM API suffered massive outages (Error 429, 404, 503). Because of our **Guardrail Architecture**, the app never crashed. 
If the API fails, the system logs the error and instantly executes the original **Deterministic Regex Parser** (`nl_parser.py`). **The user never sees an error screen and still gets their task parsed.**

---

## 🏗️ System Architecture

The system has five core modules (see `architecture/diagram.mmd` for the Mermaid diagram):

| Module | Responsibility |
|---|---|
| **Task / Pet / Owner** | Data classes that represent the domain entities. |
| **Scheduler** | The "brain" — sorts, filters, detects conflicts, finds gaps. |
| **NL Parser** | Deterministic Regex fallback for parsing tasks offline. |
| **AI Agent (`llm_agent.py`)** | Handles OpenRouter API calls, JSON validation, and Guardrails. |
| **UI / API** | Streamlit interface and FastAPI REST endpoints. |

---

## 🚀 How to Run

### Prerequisites
- Python 3.12+

### Setup
```bash
# Clone the repository
git clone https://github.com/codewarrior777/applied-ai-system.git
cd applied-ai-system

# Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows PowerShell
# source .venv/bin/activate     # macOS / Linux

# Install dependencies
pip install -r requirements.txt
pip install openai python-dotenv