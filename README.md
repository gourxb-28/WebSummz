# Webpage Summarizer Chrome Extension

A Chrome extension that summarizes the webpage you are reading. It extracts the page text, sends it to a FastAPI backend, selects the most relevant parts of the page using a RAG pipeline, and asks Google Gemini to write a short summary.


## Features

- One-click summary of the current tab
- RAG pipeline: chunking, BGE embeddings, FAISS similarity search
- Gemini generates the final summary from the selected context
- Gemini API key stays on the backend, never in the extension
- Input validation, size limits, CORS, and friendly error messages
- Loading state and error display in the popup
- Minimal permissions (`activeTab` and `scripting`): the extension only touches a page when you click it

## Architecture

```
Chrome Extension (popup)
        |
        |  injects content.js into the active tab (on click)
        v
Content Script
        |
        | 
        v
FastAPI Backend
        |
        v
Text cleaning
        |
        v
FAISS index
        |
        v
Select best chunk from each section of the page
        |
        v
Gemini (summary prompt + selected context)
        |
        v
{ "summary": "..." }
```

## Tech Stack

| Layer | Technology |
|---|---|
| Extension | Chrome Manifest V3, HTML, CSS, JavaScript, content script |
| Backend | Python, FastAPI, Pydantic, Uvicorn |
| Chunking | LangChain `RecursiveCharacterTextSplitter` (`langchain-text-splitters`) |
| Embeddings | Sentence Transformers with `BAAI/bge-small-en-v1.5` |
| Vector search | FAISS  |

## How It Works

1. You click **Summarize** in the popup.
2. The popup injects `content.js` into the active tab and asks it for the page text.
3. The content script picks text from `<article>`, then `<main>`, then `document.body`, and cleans extra whitespace.
4. The popup sends the text to the backend with a `POST` request.
5. The backend validates the request, then runs the RAG pipeline (below).
6. Gemini writes the summary from the selected context.
7. The popup displays the summary, or a friendly error message.

## RAG Pipeline

1. **Clean** the text.
2. **Chunk** it with `RecursiveCharacterTextSplitter` (1500 characters per chunk, 200 overlap).
3. **Embed** every chunk with `bge-small-en-v1.5` (384-dimensional normalized vectors).
4. **Index** the vectors in an in-memory FAISS `IndexFlatIP` (inner product = cosine similarity because the vectors are normalized).
5. **Query**: a fixed summary query ("Summarize the main points and key information of this webpage.") is embedded with the BGE query instruction prefix.
6. **Select**: the page is split into `TOP_K` consecutive sections, and the chunk with the highest similarity score in each section is chosen. This spreads the context across the whole page instead of picking only chunks from one area.
7. **Generate**: the selected chunks (in page order) are sent to Gemini with instructions to use only the provided excerpts.

Short pages (chunk count <= `TOP_K`) skip retrieval and send all chunks.

The FAISS index is built per request and is not saved to disk.

## Project Structure

```
webpage-summarizer-extension/
├── extension/
│   ├── manifest.json
│   ├── config.js
│   ├── popup.html
│   ├── popup.css
│   ├── popup.js
│   ├── content.js
│   └── icons/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── routes/summarize.py
│   │   ├── services/
│   │   │   ├── chunking.py
│   │   │   ├── embeddings.py
│   │   │   ├── vectorstore.py
│   │   │   ├── retriever.py
│   │   │   └── gemini.py
│   │   └── schemas/summarize.py
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── requirements.txt
│   └── .env
└──.gitignore 
```

## Local Setup


```powershell
git clone https://github.com/gourxb-28/WebSummz

cd webpage-summarizer-extension\backend
python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
```



## Environment Variables (.env)

| Variable | Example |
|---|---|
| `GEMINI_API_KEY` |  `your_api_key_here` |
| `GEMINI_MODEL` |  `gemini-3.8-flash` |
| `ALLOWED_ORIGINS` |  `*` |
| `MAX_TEXT_LENGTH` | `100000` |

Open `backend/.env` and paste your key `GEMINI_API_KEY=`.



## Running the Backend

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

## Loading the Chrome Extension

1. Open `chrome://extensions`.
2. Turn on **Developer mode** (top right).
3. Click **Load unpacked** and select the `extension` folder.
4. Open a normal article page, click the extension icon, and click **Summarize**.

