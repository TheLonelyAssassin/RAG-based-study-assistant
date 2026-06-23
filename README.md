# RAG Study Assistant

A local **Retrieval-Augmented Generation (RAG)** study assistant built **from scratch without LangChain**. Upload PDF or DOCX documents and ask questions — answers are grounded strictly in the uploaded content, with a built-in faithfulness evaluator scoring every answer.

Built with a **separated frontend / backend architecture**: a **FastAPI** backend serves the RAG pipeline over HTTP, and a **Streamlit** frontend acts as an HTTP client. The AI logic lives entirely in the backend — the same backend could serve a web app, a mobile app, or another system, not just this UI.

---

## Architecture

```
                          ┌─────────────────────────┐
                          │      Streamlit UI        │
                          │      (frontend)          │
                          │  upload box · chat box   │
                          └───────────┬─────────────┘
                                      │  HTTP (requests)
                          ┌───────────┴─────────────┐
                          │   POST /upload           │
                          │   POST /query            │
                          │   DELETE /documents      │
                          └───────────┬─────────────┘
                                      │
                          ┌───────────▼─────────────┐
                          │     FastAPI backend      │
                          │        (main.py)         │
                          │  validation · routing    │
                          └───────────┬─────────────┘
                                      │
                ┌─────────────────────┴──────────────────────┐
                │                RAG engine                    │
                │                                              │
                │   INGEST PATH              QUERY PATH        │
                │   ──────────               ──────────        │
                │   read PDF/DOCX            embed question    │
                │   sentence chunking        FAISS retrieval   │
                │   embed (MiniLM)           build context     │
                │   store in FAISS           Mistral generate  │
                │                            faithfulness eval │
                └──────────────────────────────────────────────┘
```

**Flow in words:**

- **Upload path:** User uploads a document in the Streamlit UI → UI sends it to `POST /upload` → backend extracts text (PyMuPDF / python-docx), chunks it (sentence-aware, NLTK), embeds the chunks (SentenceTransformers), and indexes them in FAISS. State is held in the backend.
- **Query path:** User asks a question → UI sends it to `POST /query` → backend embeds the question, retrieves the most similar chunks from FAISS, builds a grounded prompt, and generates an answer with Mistral (via Ollama). The answer returns as JSON and the UI displays it.
- **Evaluation:** A second LLM call scores each answer 0–10 for faithfulness to the retrieved context (LLM-as-a-judge).

---

## API Endpoints (FastAPI)

| Method | Endpoint       | Description                                            |
|--------|----------------|--------------------------------------------------------|
| `GET`  | `/`            | Health check — returns `{"status": "Alive"}`          |
| `POST` | `/upload`      | Upload and index one or more PDF/DOCX documents        |
| `POST` | `/query`       | Ask a question; returns a grounded answer as JSON      |
| `DELETE` | `/documents` | Clear all indexed documents                            |

The API includes:
- **Pydantic** request validation (typed request bodies)
- **Async** file-upload handling (`await file.read()`)
- **Proper HTTP error handling** — e.g. returns `400` if a query arrives before any document is indexed, instead of crashing
- **Auto-generated interactive docs** at `/docs`

---

## How the RAG Pipeline Works

| Stage          | Tool                                   | Detail                                              |
|----------------|----------------------------------------|-----------------------------------------------------|
| Text extraction| PyMuPDF (PDF), python-docx (DOCX)       | Reads raw text from uploaded files                  |
| Chunking       | NLTK `sent_tokenize`                    | Sentence-aware, 10 sentences/chunk, 2 overlap       |
| Embeddings     | SentenceTransformers `all-MiniLM-L6-v2`| 384-dimensional vectors, GPU-accelerated            |
| Retrieval      | FAISS `IndexFlatL2`                     | Fast L2 similarity search over chunk embeddings     |
| Generation     | Mistral via Ollama                      | Grounded prompt; answers strictly from context      |
| Evaluation     | Mistral (second call)                   | LLM-as-a-judge faithfulness score, 0–10             |

Chunk size (10 sentences, 2 overlap) was tuned through experimentation to balance context retention against retrieval precision. Tested on a 400-page NLP textbook (Jurafsky's *Speech and Language Processing*), achieving faithfulness scores of 8–10/10.

---

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) installed and running locally
- Mistral model pulled via Ollama

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/TheLonelyAssassin/-RAG-based-study-assistant.git
cd -RAG-based-study-assistant

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download the NLTK tokenizer (first run only)
python -c "import nltk; nltk.download('punkt')"

# 4. Pull the Mistral model and start Ollama
ollama pull mistral
ollama serve
```

---

## Running the Application

The backend and frontend run as **two separate processes** in **two terminals**.

**Terminal 1 — start the FastAPI backend:**
```bash
uvicorn main:app --reload
```
Backend runs at `http://127.0.0.1:8000` (interactive API docs at `http://127.0.0.1:8000/docs`).

**Terminal 2 — start the Streamlit frontend:**
```bash
streamlit run app.py
```

Then open the Streamlit URL shown in the terminal, upload a document, and start asking questions. The UI communicates with the backend over HTTP.

> **Note:** Start the backend first — the Streamlit frontend depends on it being available.

---

## Project Structure

```
.
├── main.py          # FastAPI backend — API endpoints
├── app.py           # Streamlit frontend — HTTP client of the API
├── RaG.py           # Pipeline orchestration (ingest + query helpers)
├── chunking.py      # Sentence-aware chunking + embedding
├── retriever.py     # FAISS indexing and retrieval
├── generator.py     # Mistral generation via Ollama
├── evaluate.py      # LLM-as-a-judge faithfulness evaluator
├── requirements.txt
└── README.md
```

---

## Tech Stack

**Python · FastAPI · Streamlit · FAISS · SentenceTransformers · Mistral (Ollama) · NLTK · PyMuPDF · python-docx · NumPy**

---

## Notes & Possible Improvements

- The FAISS index is currently rebuilt per query; a production version would build it once at ingest time and reuse it.
- Document state is held in memory in the backend; a production version would persist the index to disk or a vector database.
- Ollama calls are synchronous (`requests`); moving to an async HTTP client (`httpx`) would enable true concurrency under load.
- An `/evaluate` endpoint could expose the faithfulness scorer over the API as well.

*These are known trade-offs, kept simple deliberately for a clear, understandable implementation.*
