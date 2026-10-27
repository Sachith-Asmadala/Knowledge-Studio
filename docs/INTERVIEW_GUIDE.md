# Knowledge Studio: code learning and interview guide

Reviewed default-branch snapshot: `fcfef471db551c7c6320572b13abbf7501a7b04c`. This guide describes source code; it does not certify a running deployment or new test results.

## Problem and scope

Knowledge Studio helps a student ask questions about an uploaded lecture PDF and inspect the text used to answer. It implements retrieval-augmented generation (RAG): retrieve relevant document passages, then send those passages and a question to a language model. Python, Streamlit, LangChain, Chroma, Hugging Face embeddings, PyMuPDF4LLM, and Groq appear in the implementation. It indexes documents rather than training its own language model.

## Startup and component map

Streamlit runs [app.py](https://github.com/Sachith-Asmadala/Knowledge-Studio/blob/fcfef471db551c7c6320572b13abbf7501a7b04c/app.py). At module load, `get_app_config()` reads environment-backed settings and ensures local data/index directories exist. `main()` initializes `st.session_state`, lists saved indexes, renders navigation, and selects a page. Streamlit reruns the script on interactions; session state retains the active document, messages, and settings. Embedding and LLM resource constructors are cached with `st.cache_resource` and called when needed.

| Component | Responsibility |
| --- | --- |
| `app.py` | User interactions, active index, page rendering, orchestration |
| [src/pdf_processor.py](https://github.com/Sachith-Asmadala/Knowledge-Studio/blob/fcfef471db551c7c6320572b13abbf7501a7b04c/src/pdf_processor.py) | Convert readable PDF pages into LangChain `Document` objects |
| [src/chunking.py](https://github.com/Sachith-Asmadala/Knowledge-Studio/blob/fcfef471db551c7c6320572b13abbf7501a7b04c/src/chunking.py) | Split text while preserving page and chunk metadata |
| [src/vectordb.py](https://github.com/Sachith-Asmadala/Knowledge-Studio/blob/fcfef471db551c7c6320572b13abbf7501a7b04c/src/vectordb.py) | Build/reopen persistent Chroma indexes and their metadata |
| [src/retriever.py](https://github.com/Sachith-Asmadala/Knowledge-Studio/blob/fcfef471db551c7c6320572b13abbf7501a7b04c/src/retriever.py) | Configure similarity or MMR retrieval |
| [src/qa_chain.py](https://github.com/Sachith-Asmadala/Knowledge-Studio/blob/fcfef471db551c7c6320572b13abbf7501a7b04c/src/qa_chain.py) | Build grounded prompts and invoke Groq |
| `src/summarizer.py`, `src/utils.py` | Summarization, validation, hashing, source labels, conversation export |

## Walkthrough: upload a PDF, then ask one question

1. `handle_uploaded_pdf()` reads bytes, calls `validate_uploaded_pdf()`, derives a content-based document ID, and saves the PDF under that ID.
2. If an index exists and a rebuild was not requested, `create_or_load_vectorstore()` reopens it. Otherwise `extract_pdf_pages()` extracts text; empty pages are skipped and an entirely unreadable PDF raises `PDFProcessingError`.
3. `chunk_documents()` uses `RecursiveCharacterTextSplitter`. Each chunk retains its filename/page and gains a chunk index and ID. Overlap helps preserve context across chunk boundaries.
4. Chroma stores the chunk embeddings on disk. `activate_document()` makes that store the active knowledge base.
5. `ask_question()` rejects a missing active store or missing `GROQ_API_KEY`. It calls `retrieve_for_qa()` for the active document. MMR can trade some similarity for more diverse passages; similarity mode passes only the supported `k` option.
6. `answer_question()` constructs a context string from the retrieved documents and invokes the LLM. With no usable context it returns a fallback without invoking the model.
7. The UI stores the answer and serialized sources in session state and shows source labels. The sources expose retrieval evidence; they do not automatically prove every generated sentence is correct.

For example, asking “What is a transaction?” should retrieve passages from the active lecture PDF. There is no guarantee that those passages contain the answer. Previous chat messages are displayed/stored, but this Q&A function sends the current question and retrieved context, not the complete conversation history.

## Data structures and engineering decisions

- A `Document` pairs `page_content` with a metadata dictionary, so text can be retrieved without losing its origin.
- Lists preserve page/chunk/message order. A `defaultdict(int)` in chunking counts chunks per page.
- A SHA-256-derived ID identifies identical uploaded bytes for index reuse. A differently encoded PDF can have a different ID despite similar text.
- Metadata dictionaries and JSON files describe indexes; Chroma handles vector search. A normal Python list is not performing nearest-neighbor search here.
- Cached resources avoid repeatedly initializing expensive model clients. Persistent indexes avoid re-embedding unchanged uploaded bytes.

## Errors, limitations, and useful improvements

Custom exceptions in `src/utils.py` distinguish PDF, embedding, vector-store, and LLM failures. UI handlers catch `AppError` and also have general exception handlers. Some messages include underlying exception text, so errors deserve a review before a shared deployment.

The active retrieval target is one document index. Summaries use retrieved chunks, which may omit parts of a long PDF. The “rerank” toggle sorts by passage length; it is not a learned relevance reranker. Existing index reuse does not validate all embedding/chunking configuration against saved metadata. Forced rebuilding deletes the old index before the replacement has succeeded. Resource limits and scanned-PDF behavior need explicit tests.

Focused future work: test unreadable PDFs, chunk metadata, index/model mismatch, failed rebuild recovery, and empty-context/provider errors. Existing [tests/test_retriever.py](https://github.com/Sachith-Asmadala/Knowledge-Studio/blob/fcfef471db551c7c6320572b13abbf7501a7b04c/tests/test_retriever.py) and `tests/test_utils.py` exercise retrieval configuration and conversation export; they do not establish end-to-end answer quality. Split UI modules only after identifying stable boundaries and preserving behavior.

## Contribution evidence and honest interview wording

GitHub attributes [commit 6e2efab](https://github.com/Sachith-Asmadala/Knowledge-Studio/commit/6e2efab483cd3f1b17c431e918ba0f0b51a6497c) to `Sachith-Asmadala`. Its diff includes retrieval modes, document search, chat export, Makefile changes, deletion confirmations, and focused tests. This records account attribution, not which parts were independently written or how assistance was used. Confirm your role before claiming ownership of those changes or the entire application.

## Five interview questions and model answers

1. **How is this different from sending the whole PDF to an LLM?** The code extracts pages, chunks text, stores embeddings in Chroma, and retrieves a limited set of chunks for each question. This controls the context sent, but retrieval can miss relevant material.
2. **Why include overlap between chunks?** A definition may begin near a boundary and finish in the next chunk. Overlap retains nearby context; excessive overlap increases duplicated text and indexing work.
3. **What does MMR add?** `build_retriever()` passes `fetch_k` and `lambda_mult` in MMR mode to balance similarity and diversity. Similarity mode uses `k` alone. The application's length sort is a separate heuristic.
4. **Does the prompt guarantee there are no hallucinations?** No. The prompt requests evidence-only answers and the function handles empty context, but the LLM can still make unsupported claims. Source inspection and evaluation are needed.
5. **What happens after uploading the same file again?** Its content ID is the same, so an existing index can be reused unless rebuilding is requested. Configuration changes are a reason to validate compatibility rather than assuming reuse is always correct.

## Practice before an interview

Trace one `Document` from page extraction to a displayed source label. Predict what happens for an empty question context, a missing API key, and an existing index. Explain the difference between the UI chat history and the context actually sent to the model. Use your own words before practicing the model answers.
