# agents/embedding.py

from sentence_transformers import SentenceTransformer, util
import numpy as np
embeddings =""
model =""
convert_to_numpy: bool = True

def embed_documents(
    documents: list,
    model_name: str = "sentence-transformers/all-mpnet-base-v2",
    convert_to_numpy: bool = True
) -> list:
    """
    For each Document in `documents`, compute a dense embedding of its `.content`
    and store it in doc.meta["embedding"].

    Returns the same list of Documents, now enriched with embeddings.
    """
    # 1) Load the Sentence-Transformers model
    model = SentenceTransformer(model_name)

    # 2) Extract all texts and encode them in one batch
    texts = [doc.content for doc in documents]
    embeddings = model.encode(texts, convert_to_numpy=convert_to_numpy)

    # 3) Attach each embedding back to its Document
    for doc, emb in zip(documents, embeddings):
        # if it’s an np.array, convert to list so it’s JSON-serializable if needed
        doc.meta["embedding"] = emb.tolist() if hasattr(emb, "tolist") else emb

    print(f"✅ Embedded {len(documents)} documents with model '{model_name}'")
    run_Querey(documents, embeddings)
    return documents


def run_Querey(docs, embeddings1):
    print(f"✅ Querey {len(docs)} documents with model ")

    query = "who are the attendies?"
    model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

    # Convert to embeddings
    query_embedding = model.encode(query, convert_to_numpy=convert_to_numpy)
    doc_embeddings = embeddings1

    # Compute cosine similarities
    scores = util.cos_sim(query_embedding, doc_embeddings)

    # Rank documents
    ranking = sorted(zip(scores[0], docs), key=lambda x: x[0], reverse=True)
    for score, doc in ranking:
        print(f"Score: {score:.4f} | Document: {doc.content}")