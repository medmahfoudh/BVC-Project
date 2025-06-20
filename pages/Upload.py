import streamlit as st
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.schema import Document
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from langchain_ollama import OllamaLLM
import re
import pandas as pd
from pages.analytics import compute_all_metrics # <-- import analytics function
from datetime import datetime, timedelta

# Load existing report details
report_details_path = "data/report_details.xlsx"
report_details = pd.read_excel(report_details_path)

st.title("Upload a new report to the database")

# Upload and read PDF file
pdf = st.file_uploader("Upload a file", type=["pdf"])

if pdf:
    pdf_reader = PyPDF2.PdfReader(pdf)
    text = "".join(page.extract_text() for page in pdf_reader.pages)

    account_id = re.search(r'Account ID\s+([\d\s]+)', text).group(1).strip().replace(" ", "")
    visit_date = re.search(r'Date\s+(\d{1,2}\.\s\w+\.\s\d{4})', text).group(1)
    company_name = re.search(r"Account\s*\n\s*(.+)", text).group(1).strip()
    doc_id = account_id + "_" + visit_date
    country = "Germany"  # Modify if needed

    data = Document(
        page_content=text,
        metadata={
            "doc_id": doc_id,
            "account_id": account_id,
            "visit_date": visit_date,
            "company_name": company_name
        }
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, length_function=len
    )

    chunks = text_splitter.split_documents([data])
    embedding_model = SentenceTransformerEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")

    client = QdrantClient(
        url="https://94d74b83-c25c-4b39-b117-9aec9a65db4c.us-east4-0.gcp.cloud.qdrant.io",
        api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.Lt2YQ-IAfyBJAbRK6F2IxjnojnKSm72ENq-4z7-wqZY"
    )

    collection_name = "wieland_reports"

    # Ensure collection exists with correct embedding size
    collections = [col.name for col in client.get_collections().collections]
    if collection_name not in collections:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )

        client.create_payload_index(
            collection_name=collection_name,
            field_name="metadata.company_name",
            field_schema="keyword"
        )

    # Add documents to Qdrant
    qdrant = Qdrant(client=client, collection_name=collection_name, embeddings=embedding_model)
    qdrant.add_documents(chunks)

    # Update report details with basic metadata first
    new_entry = {
        "report_id": doc_id,
        "company_name": company_name,
        "country": country,
        "report_date": pd.to_datetime(visit_date, dayfirst=True)
    }

    report_details = pd.concat([report_details, pd.DataFrame([new_entry])], ignore_index=True)
    report_details.to_excel(report_details_path, index=False)

    # Trigger metric extraction
    with st.spinner("Extracting additional metrics..."):
        compute_all_metrics(report_id=doc_id)

    # Re-load the updated report details after metrics extraction
    report_details = pd.read_excel(report_details_path)

    # Calculate visits completed last 30 days
    today = datetime.now()
    past_30_days = today - timedelta(days=30)
    visits_last_30_days = report_details[pd.to_datetime(report_details['report_date'], dayfirst=True) >= past_30_days].shape[0]

    # Calculate red flags (accounts with 'High Risk' or certain signals)
    red_flags = report_details[
        report_details['risk_score'].fillna("").str.lower().str.contains("high risk")
    ].shape[0]


    # Append the calculated measures directly
    report_details['visit_completed_last_30_days'] = visits_last_30_days
    report_details['red_flags'] = f"{red_flags} flagged accounts"

    # Save back to excel
    report_details.to_excel(report_details_path, index=False)

    st.success("Your report and metrics have been successfully uploaded and updated!")

