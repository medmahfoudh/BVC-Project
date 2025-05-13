import streamlit as st
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.schema import Document
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue, PayloadSchemaType
from qdrant_client.http import models
import re

# Page Title
st.title("Upload a new reprot to the database")

# read pdf file
pdf = st.file_uploader("Upload a file", type=["pdf"])

if pdf is not None:
    # read the pdf
    pdf_reader = PyPDF2.PdfReader(pdf)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    # st.write(text)
    account_id = re.search(r'Account ID\s+([\d\s]+)', text).group(1).strip().replace(" ", "")
    visit_date = re.search(r'Date\s+(\d{1,2}\.\s\w+\.\s\d{4})', text).group(1)
    company_name = re.search(r"Account\s*\n\s*(.+)", text).group(1)
    doc_id = account_id + "_" + visit_date
    # st.write({
    #     "account_id": account_id,
    #     "visit_date": visit_date,
    #     "company_name": company_name.strip()
    # })

    data = Document(
        # id = account_id + "_" + visit_date,
        page_content = text,
        metadata = {
        "doc_id" : doc_id,
        "account_id": account_id,
        "visit_date": visit_date,
        "company_name": company_name.strip()
    }
    )

# Split the documents into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)

upload_btn = st.button("Upload Report")

if upload_btn:
    chunks = text_splitter.split_documents([data])
    # st.write(chunks[0])

    # embed the chunks in to vectors
    #  embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2") # only supports english
    embedding_model = SentenceTransformerEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")

    collection_name="crm_reports_rag"

    # add the chunks to the db
    # I have hardcoded the API KEY here, but it should be stored in a .env file
    client = QdrantClient(
        url="https://88557973-d9d3-4a8e-a92b-a877815aff1f.eu-central-1-0.aws.cloud.qdrant.io:6333",
        api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.hTkGVX7aVObKDCE9iB9HBi_Cq_oBJgPJhmQEkqE9LeI"
    )
    
    qdrant = Qdrant(
        client=client,
        collection_name=collection_name,
        embeddings=embedding_model
    )

    # The embedding dimension (384 for MiniLM-L6-v2)
    embedding_size = 384

    collections = [col.name for col in client.get_collections().collections]
    # create the collection if it doesn't exist
    if not collection_name in collections:
        client.recreate_collection(
            collection_name="crm_reports_rag",
            vectors_config=VectorParams(size=embedding_size, distance=Distance.COSINE)
        )

    # extract document ids
    points, next_page = client.scroll(collection_name=collection_name, with_payload=True)
    doc_ids = [point.payload["metadata"]["doc_id"] for point in points]

    # st.write(filtered_vectors)

    # If the report exists, don't add
    if doc_id in doc_ids:
        st.write(f"❌ Error: the report with ID '{doc_id}' already exists in database!")
    else:
        # Store the document chunks
        qdrant.add_documents(chunks)
        st.write("✅ Your report has been uploaded to the database!")

