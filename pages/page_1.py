import streamlit as st
from langchain.chains import RetrievalQA
from langchain.llms import LlamaCpp  # or use GPT4All, HuggingFaceHub, etc.
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from langchain.embeddings import SentenceTransformerEmbeddings
from qdrant_client.http import models
# from langchain.chat_models import ChatOpenAI
# from langchain.prompts import ChatPromptTemplate
# from transformers import pipeline

# Page Title
st.title("Chat with AI")

embedding_model = SentenceTransformerEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
collection_name="crm_reports_rag"

client = QdrantClient(
    url="https://88557973-d9d3-4a8e-a92b-a877815aff1f.eu-central-1-0.aws.cloud.qdrant.io:6333",
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.hTkGVX7aVObKDCE9iB9HBi_Cq_oBJgPJhmQEkqE9LeI"
)

# extract company names from database
points, next_page = client.scroll(collection_name=collection_name, with_payload=True)
company_names = [point.payload["metadata"]["company_name"] for point in points]


selected_company = st.selectbox("Select a company:", set(company_names))
query = st.text_input("Enter your query here:")
submit_btn = st.button("Submit")

if submit_btn:
    query_vector = embedding_model.embed_query(query)

    client.create_payload_index(
        collection_name=collection_name,  # Replace with your collection
        field_name="metadata.company_name",
        field_schema=models.PayloadSchemaType.KEYWORD  # Exact match filtering
    )

    results = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=3,
        query_filter=Filter(must=[FieldCondition(key="metadata.company_name", match=MatchValue(value=selected_company))])
    )

    context = "\n".join([result.payload["page_content"] for result in results])

    prompt_template = f"""
Answer the question based only on the following context: \n
{context}
----
Answer the question based on the above context: \n{query}
"""

    st.write(prompt_template)

    # model = pipeline("summarization", model="facebook/bart-large-cnn")
    # response = model(prompt_template)
