# 📊 Financial Analysis Assistant

> An AI-powered financial reporting tool that summarizes reports, explains variances, and generates executive commentary — built with **RAG + Claude (LLM) + Streamlit + FastAPI**.

---

## 🎯 Problem Statement

Finance teams spend significant time manually reviewing financial reports, transaction summaries, and variance explanations, delaying monthly close activities. This assistant automates that first-pass analysis using Retrieval-Augmented Generation (RAG) so finance teams get accurate, document-grounded insights in seconds.


## ✨ Features

- 📁 **Document upload** — supports PDF, Excel (.xlsx), CSV, and TXT financial reports
- 🔍 **RAG pipeline** — chunks, embeds, and retrieves only the most relevant context
- 🤖 **Claude-powered analysis** — grounded strictly in your uploaded document
- 📋 **Summary tab** — headline KPIs with trend indicators (revenue, EBITDA, net income, gross margin)
- 📊 **Variance analysis tab** — line-by-line budget vs actual with root cause explanations
- ✍️ **Executive commentary tab** — board-ready paragraphs, risks, and recommended actions
- ⬇️ **Export** — download executive commentary as a `.txt` file
- 🚫 **Hallucination prevention** — three-layer guard (retrieval filter + API block + prompt rules)

---

## 🏗️ Architecture

```
financial-assistant/
├── backend/
│   ├── main.py          # FastAPI — REST endpoints (/upload, /analyze)
│   ├── rag.py           # RAG pipeline — chunking, embedding, ChromaDB
│   ├── app.py           # Streamlit frontend
│   └── .env             # API keys (not committed)
```

### System flow

```
User uploads file
      │
      ▼
FastAPI /upload
      │
      ▼
RAG pipeline
  ├── Parse PDF / Excel / CSV
  ├── Chunk text (500 words, 50-word overlap)
  ├── Embed with sentence-transformers (all-MiniLM-L6-v2)
  └── Store vectors in ChromaDB
      │
      ▼
User asks a question
      │
      ▼
FastAPI /analyze
  ├── Embed query
  ├── Retrieve top-k relevant chunks (distance < 1.5)
  ├── Build grounded prompt
  └── Call Claude (claude-sonnet-4-20250514)
      │
      ▼
Streamlit renders JSON → Summary / Variance / Exec tabs
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI + Uvicorn |
| LLM | Anthropic Claude (claude-sonnet-4-20250514) |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| Vector DB | ChromaDB |
| PDF parsing | PyPDF |
| Excel parsing | openpyxl |
| Language | Python 3.11+ |

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.11+
- Anthropic API key → [console.anthropic.com](https://console.anthropic.com)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/financial-assistant.git
cd financial-assistant/backend
```

### 2. Create and activate virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn python-multipart anthropic chromadb \
  sentence-transformers pypdf openpyxl python-dotenv streamlit requests
```

### 4. Configure environment variables

Create a `.env` file inside the `backend/` folder:

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

> ⚠️ Never commit your `.env` file. It is already listed in `.gitignore`.

### 5. Run the application

Open **two terminals**:

**Terminal 1 — FastAPI backend**
```bash
cd backend
venv\Scripts\activate      # Windows
uvicorn main:app --reload --port 8000
```

**Terminal 2 — Streamlit frontend**
```bash
cd backend
venv\Scripts\activate      # Windows
streamlit run app.py
```

Open your browser at **http://localhost:8501**

---

## 🚀 Usage

1. **Upload** your financial report (PDF, Excel, or CSV) using the sidebar
2. **Select** the reporting period (e.g. April 2025, Q1 2025)
3. **Type a question** or pick a quick prompt from the sidebar
4. Click **Analyze** — results appear across three tabs
5. **Download** the executive commentary for your board pack

### Example prompts

```
Summarize revenue performance vs budget
Explain the OPEX variance this month
What drove the gross margin decline?
Write executive commentary for the board pack
```

---

## 🔒 Hallucination Prevention

This system uses three layers to ensure answers are grounded in your document only:

| Layer | What it does |
|---|---|
| **Retrieval filter** | Drops chunks with similarity distance > 1.5 (weak matches) |
| **API guard** | Returns a 400 error before calling Claude if no document is loaded or no relevant context is found |
| **Prompt rules** | System prompt instructs Claude to return `N/A` for any metric not found in the context — never estimate or assume |

---

## 📁 Sample Output

### Summary tab
- **Headline:** Revenue missed budget by 5.4% driven by delayed enterprise renewals
- **Metrics:** Revenue $11.82M (↓ vs $12.5M budget), Gross Margin 55.2% (↓ 4.8pp), EBITDA $640K (↓ 68%)

### Variance tab
| Line item | Budget | Actual | Variance | Status |
|---|---|---|---|---|
| Marketing | $1.2M | $1.58M | +$380K | Over |
| Services revenue | $3.5M | $3.17M | -$330K | Under |
| G&A | $600K | $540K | -$60K | Under |

### Executive commentary tab
Board-ready paragraphs with risk flags and recommended management actions, downloadable as `.txt`.


## 👤 Author

**Your Name**
- GitHub: [@your-username](https://github.com/sudasudheerkumar)
- LinkedIn: [your-linkedin](www.linkedin.com/in/sudasudheer)

---

## 🙏 Acknowledgements

- [Anthropic Claude](https://anthropic.com) — LLM backbone
- [ChromaDB](https://www.trychroma.com) — vector database
- [Sentence Transformers](https://www.sbert.net) — embedding model
- [Streamlit](https://streamlit.io) — frontend framework
- [FastAPI](https://fastapi.tiangolo.com) — backend framework
