# agents/ingestion.py

from pathlib import Path
import PyPDF2

from haystack import Document
from haystack.document_stores.in_memory import InMemoryDocumentStore


def extract_text_from_pdf(pdf_path: str) -> str:
    text = []
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            if page_text := page.extract_text():
                text.append(page_text)
    return "\n".join(text)


def load_and_chunk(directory: str = "data/reports") -> list[Document]:
    docs = []
    for path in Path(directory).iterdir():
        if not path.is_file():
            continue

        raw = (
            extract_text_from_pdf(str(path))
            if path.suffix.lower() == ".pdf"
            else path.read_text(encoding="utf-8", errors="ignore")
        )

        # split on blank lines (paragraphs)
        paras = [p.strip() for p in raw.split("\n\n") if p.strip()]
        for para in paras:
            docs.append(Document(content=para, meta={"source": path.name}))
    return docs


def ingest_pipeline(directory: str = "data/reports"):
    """
    - Loads & chunks your files into Haystack Documents
    - Writes them into an in-memory store
    - Returns both the store *and* the list of Documents
    """
    print(f"📥 Loading files from: {directory}")
    documents = load_and_chunk(directory)
    print(f"📝 Prepared {len(documents)} Document chunks.")

    store = InMemoryDocumentStore()
    store.write_documents(documents)
    print("✅ Ingestion complete — your DocumentStore is ready!")

    # Return BOTH so you can inspect the raw list easily
    return store, documents
