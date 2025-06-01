import os
from haystack.document_stores import QdrantDocumentStore
from haystack.nodes import PDFToTextConverter, PreProcessor
from haystack.nodes import SentenceTransformersDocumentEmbedder, EmbeddingRetriever
from haystack import Pipeline
from haystack.nodes import TransformersSummarizer


# 1. Connect to your already-running Qdrant server:
document_store = QdrantDocumentStore(
    url="http://localhost:6333",   # matches the port you exposed
    prefer_grpc=False,
    index="reports",
    embedding_dim=384,
    similarity="cosine",
)

# 2. Ingest & split your PDFs:
converter = PDFToTextConverter()
preprocessor = PreProcessor(
    clean_empty_lines=True,
    clean_whitespace=True,
    split_by="word",
    split_length=500,
    split_overlap=50,
)

pdf_folder = "data/reports/"
docs = []
for fn in os.listdir(pdf_folder):
    if fn.lower().endswith(".pdf"):
        raw = converter.convert(file_path=os.path.join(pdf_folder, fn),
                                meta={"source": fn})
        docs.extend(preprocessor.process(raw))

# 3. Embed & write into Qdrant:
embedder  = SentenceTransformersDocumentEmbedder(model_name_or_path="all-MiniLM-L6-v2")
retriever = EmbeddingRetriever(
    document_store=document_store,
    embedder=embedder,
    use_gpu=False  # or True if you have a GPU
)

document_store.write_documents(docs)
document_store.update_embeddings(retriever)

# 4. Build a simple Retriever→Summarizer pipeline:
summarizer = TransformersSummarizer(
    model_name_or_path="facebook/bart-large-cnn",
    tokenizer="facebook/bart-large-cnn",
    use_gpu=False
)

pipe = Pipeline()
pipe.add_node(component=retriever, name="Retriever", inputs=["Query"])
pipe.add_node(component=summarizer, name="Summarizer", inputs=["Retriever"])

# 5. Try it out:
result = pipe.run(
    query="What were the key takeaways from the Fantasiefirma report?",
    params={
      "Retriever": {"top_k": 3},
      "Summarizer": {"min_length": 50, "max_length": 150}
    }
)
print("Summary:\n", result["documents"][0].content)
