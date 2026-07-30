# Knowledge Studio

A dark, premium Streamlit RAG app for lecture PDFs and document-grounded Q&A.

## What it does

- Upload a PDF and build a persistent Chroma index
- Reuse saved indexes without rebuilding embeddings every run
- Ask grounded questions about the active document
- Generate a structured summary from retrieved chunks
- Switch between MMR and similarity retrieval
- Inspect retrieved source chunks and metadata
- Review simple analytics and feedback signals
- Search saved documents and export complete conversations

## Stack

- Streamlit
- LangChain
- ChromaDB
- HuggingFace embeddings
- Groq
- PyMuPDF4LLM

## Python version

Use **Python 3.11 or 3.12**.

Do **not** use Python 3.14 because Chroma and the Pydantic v1 compatibility layer can fail there.

## Run locally

```bash
make setup
# create .env and add GROQ_API_KEY=your_real_groq_api_key
make run
```

Run `make help` to see all commands. The Makefile also provides `install`,
`compile`, `test`, `check`, and `clean` targets. It uses `python3.11` by
default; override it with `make setup PYTHON=python3.12`.

## Environment

Create a `.env` file in the project root and set:

```env
GROQ_API_KEY=your_real_groq_api_key
```

## Main pages

- Chat
- Documents
- Sources
- Analytics
- Settings

## Notes

- PDF indexing is fully implemented.
- Other file types are surfaced in the UI for future extension.
- Destructive index deletion actions require confirmation.
- The UI styling is adapted from the uploaded `knowledge_studio_ui.html` design reference.
