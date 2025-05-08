# agents/retrieval.py

from sentence_transformers import SentenceTransformer
import numpy as np

class RetrievalAgent:
    def __init__(self, documents, model_name="sentence-transformers/all-mpnet-base-v2"):
        """
        documents: list of Haystack Document objects (with .content and .meta)
        """
        # Load the embedding model
        self.model = SentenceTransformer(model_name)
        self.docs = documents

        # Pre-compute embeddings for all documents
        contents = [doc.content for doc in documents]
        self.embeddings = self.model.encode(contents, convert_to_tensor=True)

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Encode the query, compute cosine similarities against document embeddings,
        and return the top_k results as a list of dicts with 'source', 'content', and 'score'.
        """
        # Encode the query
        q_emb = self.model.encode(query, convert_to_tensor=True)

        # Convert embeddings to numpy
        emb_array = (
            self.embeddings.cpu().numpy()
            if hasattr(self.embeddings, "cpu")
            else np.array(self.embeddings)
        )
        q_array = (
            q_emb.cpu().numpy() if hasattr(q_emb, "cpu") else np.array(q_emb)
        )

        # Cosine similarity calculation
        norms = np.linalg.norm(emb_array, axis=1) * np.linalg.norm(q_array)
        cos_scores = (emb_array @ q_array) / norms

        # Select top_k highest scores
        top_idx = np.argsort(-cos_scores)[:top_k]

        # Build result list
        results = []
        for idx in top_idx:
            doc = self.docs[idx]
            score = float(cos_scores[idx])
            results.append({
                "source": doc.meta.get("source", "<unknown>"),
                "content": doc.content,
                "score": score
            })

        return results
