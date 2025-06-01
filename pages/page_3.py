import streamlit as st
from langchain.chains import RetrievalQA
from langchain.llms import LlamaCpp 
from langchain.vectorstores import Qdrant
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain_ollama import OllamaLLM
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from qdrant_client.http import models
import pandas as pd
import time

# Page Title
st.title("Report Summarization Agent")

# extract company names from database
report_details = pd.read_excel("data/report_details.xlsx")

selected_company = st.selectbox("Select a company:", set(report_details['company_name']))

report_dates = report_details[report_details.company_name == selected_company]['report_date']
selected_report_date = st.selectbox("Select a Visit Date:", report_dates)

report_id = report_details[(report_details.company_name == selected_company) & (report_details['report_date'] == selected_report_date)]['report_id'].values[0]

summarise_btn = st.button("Summarise Report")

# embedding model
embedding_model = SentenceTransformerEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")

# qdrant client object
client = QdrantClient(
    url="https://88557973-d9d3-4a8e-a92b-a877815aff1f.eu-central-1-0.aws.cloud.qdrant.io:6333",
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.hTkGVX7aVObKDCE9iB9HBi_Cq_oBJgPJhmQEkqE9LeI"
)

# Clicked the summarise button
if summarise_btn:
    collection_name = "crm_reports_rag"
    
    # Create the payload index for doc_id
    client.create_payload_index(
    collection_name=collection_name,
    field_name="metadata.doc_id",
    field_schema=models.PayloadSchemaType.KEYWORD
    )
    
    # Scroll to retrieve all matching points
    scroll_result, _ = client.scroll(
        collection_name = "crm_reports_rag",
        scroll_filter=Filter(must=[FieldCondition(key="metadata.doc_id", match=MatchValue(value=report_id))]),
        limit=100 
    )
    
    # Extract the page content from the retrieved points
    context = "\n".join([result.payload["page_content"] for result in scroll_result])
    
    # Design the prompt
    prompt = f"""
    Summarize the visit report of company {selected_company} that was conducted on {selected_report_date} using only the below context on detailed manner: \n
    {context}
    """

    with st.spinner("Please wait while I summarise your report...", show_time=True):
        # prompt LLM and display the response
        placeholder = st.empty()
        output_text = ""

        llm = OllamaLLM(model="mistral")
        for chunk in llm.stream(prompt):
            output_text += chunk
            placeholder.markdown(f"""{output_text}""")
        
    st.success("Done! Here is the summary of your report.")


