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
    url="https://94d74b83-c25c-4b39-b117-9aec9a65db4c.us-east4-0.gcp.cloud.qdrant.io",
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.Lt2YQ-IAfyBJAbRK6F2IxjnojnKSm72ENq-4z7-wqZY"
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
        collection_name="wieland_reports",
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

def compute_all_metrics(report_id=None):
    df = load_companies()

    if report_id:
        df = df[df["report_id"].fillna("") == report_id] # Only new row

    contexts = {c: get_context(c) for c in df["company_name"].unique()}

    records = []
    for _, row in df.iterrows():
        comp = row["company_name"]
        ctx = contexts[comp]
        prompt = f"""
        You are a multilingual AI assistant helping extract business metrics.

        Given ONLY the context below, extract 5 intelligence values for the company: {comp}.

        ---
        Context:
        {ctx}

        ---
        Instructions:
        - Output must be a SINGLE line with 5 values, separated by `|||`
        - No labels, no bullets, no line breaks
        - Output everything in **English**
        - Do NOT return "Customer Satisfaction:" or "Urgent Signals:" — just the values

        Format:
        <customer_satisfaction> ||| <opportunity_index> ||| <risk_score> ||| <forecast_accuracy> ||| <urgent_signals>

        Example:
        Satisfied ||| Expand into packaging, New supplier identified ||| Moderate Risk ||| 87% ||| High price, Delay

        Now extract and return your values in exactly that format:
        """

        output = ""
        for chunk in llm.stream(prompt):
            output += chunk
        print(f"[LLM raw output] {output}")

        # Make sure the output is 1 line with 5 parts
        raw_line = output.strip().splitlines()[0]
        parts = [x.strip().replace('"', '') for x in raw_line.split("|||")]
        parts = (parts + [None] * 5)[:5]  # ensure exactly 5



        records.append((row["report_id"], *parts))

    metrics_df = pd.DataFrame(records, columns=[
        "report_id",
        "customer_satisfaction",
        "opportunity_index",
        "risk_score",
        "forecast_accuracy",
        "urgent_signals"
    ])

    # Load and normalize the full Excel sheet
    full_df = load_companies()

    # Ensure all metric columns exist in full_df
    for col in metrics_df.columns[1:]:
        if col not in full_df.columns:
            full_df[col] = ""

    # Normalize report_id formats in both DataFrames
    metrics_df["report_id"] = metrics_df["report_id"].astype(str).str.strip().str.replace(".0", "", regex=False)
    full_df["report_id"] = full_df["report_id"].astype(str).str.strip().str.replace(".0", "", regex=False)

    # Apply updates row-by-row
    for idx, row in metrics_df.iterrows():
        rid = row["report_id"]
        mask = full_df["report_id"] == rid
        if mask.any():
            for col in metrics_df.columns[1:]:
                full_df.loc[mask, col] = row[col]
        else:
            print(f"⚠️ Warning: Report ID not found in full_df: {rid}")

    # Save the updated file
    save_companies(full_df)
    print("✅ Metrics updated for:", report_id if report_id else "ALL")



if __name__ == "__main__":
    compute_all_metrics()