import os
import re
from pathlib import Path
import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain_ollama import OllamaLLM

# Determine project root and data path
script_dir = Path(__file__).resolve().parent
if (script_dir / "data" / "report_details.xlsx").exists():
    BASE_DIR = script_dir
elif (script_dir.parent / "data" / "report_details.xlsx").exists():
    BASE_DIR = script_dir.parent
else:
    BASE_DIR = script_dir  # fallback

DATA_DIR = BASE_DIR / "data"
COMPANY_FILE = DATA_DIR / "report_details.xlsx"

if not COMPANY_FILE.exists():
    raise FileNotFoundError(f"Excel file not found at {COMPANY_FILE}")

# Initialize Qdrant and models
client = QdrantClient(
    url="https://88557973-d9d3-4a8e-a92b-a877815aff1f.eu-central-1-0.aws.cloud.qdrant.io:6333",
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.hTkGVX7aVObKDCE9iB9HBi_Cq_oBJgPJhmQEkqE9LeI"
)
embedding_model = SentenceTransformerEmbeddings(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)
llm = OllamaLLM(model="mistral")

def load_companies(path: Path = COMPANY_FILE) -> pd.DataFrame:
    return pd.read_excel(path)

def save_companies(df: pd.DataFrame, path: Path = COMPANY_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(path, index=False)

def get_context(company: str, top_k: int = 3) -> str:
    query_vector = embedding_model.embed_query(company)
    results = client.search(
        collection_name="crm_reports_rag",
        query_vector=query_vector,
        limit=top_k,
        query_filter=Filter(
            must=[FieldCondition(
                key="metadata.company_name",
                match=MatchValue(value=company)
            )]
        )
    )
    return "\n".join([pt.payload.get("page_content", "") for pt in results])

def compute_all_metrics():
    df = load_companies()
    contexts = {c: get_context(c) for c in df["company_name"].unique()}

    records = []
    for comp in df["company_name"]:
        ctx = contexts[comp]
        prompt = f"""
You are a precise assistant. Based ONLY on the context below, extract five business intelligence metrics for the company: {comp}.

Context:
{ctx}

---
INSTRUCTIONS:
Return exactly FIVE values, separated by "|||". Do NOT add labels, bullet points, or explanations.

Strict format:
1. Customer Satisfaction: one of these phrases — "Very Satisfied", "Satisfied", "Not Satisfied", "Very Bad"
2. Opportunity Index: exactly two short sentences.
3. Risk Score: one short phrase like "Low Risk", "Moderate Risk", or "High Risk"
4. Forecast Accuracy: percentage or short phrase (e.g., "82%" or "Uncertain")
5. Urgent Signals: exactly two words only.

Return only this one line:
<value1> ||| <value2> ||| <value3> ||| <value4> ||| <value5>
"""
        output = ""
        for chunk in llm.stream(prompt):
            output += chunk
        parts = [x.strip() for x in output.strip().split("|||")]
        parts = (parts + [None] * 5)[:5]  # Ensure 5 elements
        records.append(parts)

    cols = [
        "customer_satisfaction",
        "opportunity_index",
        "risk_score",
        "forecast_accuracy",
        "urgent_signals"
    ]

    metrics_df = pd.DataFrame(records, columns=cols)

    for col in cols:
        if col in df.columns:
            df[col] = metrics_df[col]
        else:
            df[col] = metrics_df[col]

    save_companies(df)
    print("✅ Metrics updated in report_details.xlsx")

if __name__ == "__main__":
    compute_all_metrics()