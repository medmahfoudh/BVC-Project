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
st.title("IntelBrief")

# extract company names from database
report_details = pd.read_excel("data/report_details.xlsx")

selected_company = st.selectbox("Select a company:", set(report_details['company_name']))

report_dates = report_details[report_details.company_name == selected_company]['report_date']
selected_report_date = st.selectbox("Select a Visit Date:", report_dates)

report_id = report_details[(report_details.company_name == selected_company) & (report_details['report_date'] == selected_report_date)]['report_id'].values[0]

summarise_btn = st.button("Summarise Report")
compare_results = st.checkbox("Compare Results With Other Companies")

# embedding model
embedding_model = SentenceTransformerEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")

# qdrant client object
client = QdrantClient(
    url="https://94d74b83-c25c-4b39-b117-9aec9a65db4c.us-east4-0.gcp.cloud.qdrant.io",
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.Lt2YQ-IAfyBJAbRK6F2IxjnojnKSm72ENq-4z7-wqZY"
)

# Clicked the summarise button
if summarise_btn:
    collection_name = "wieland_reports"
    
    # Create the payload index for doc_id
    client.create_payload_index(
    collection_name=collection_name,
    field_name="metadata.doc_id",
    field_schema=models.PayloadSchemaType.KEYWORD
    )
    
    # Scroll to retrieve all matching points
    scroll_result, _ = client.scroll(
        collection_name = "wieland_reports",
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

##### Compare Reports #####
if compare_results and summarise_btn:
    scroll_result, _ = client.scroll(
        collection_name = "wieland_reports",
        scroll_filter=Filter(must=[FieldCondition(key="metadata.doc_id", match=MatchValue(value=report_id))]),
        limit=100 
    )

    # st.write(scroll_result)
    # Extract the page content from the retrieved points
    context_other_companies = "\n".join([result.payload["page_content"] for result in scroll_result])

    # Design the prompt
    prompt = f"""
    Compare this report with other companies reports given here:
    {context_other_companies} in 10 points.
    """
    with st.spinner("Let me compare these points with other companeis' report", show_time=True):
        # prompt LLM and display the response
        placeholder_compare_results = st.empty()
        output_text = ""

        llm = OllamaLLM(model="mistral")
        for chunk in llm.stream(prompt):
            output_text += chunk
            placeholder_compare_results.markdown(f"""{output_text}""")
        
    st.success("Done! the comparison of results is ready.")