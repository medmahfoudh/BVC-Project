import streamlit as st
from langchain.chains import RetrievalQA
from langchain.llms import LlamaCpp  # or use GPT4All, HuggingFaceHub, etc.
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from langchain.embeddings import SentenceTransformerEmbeddings
from qdrant_client.http import models
from langchain_ollama import OllamaLLM
import pandas as pd

# Page Title
st.title("IntelAsk")

# extract company names from database
# points, next_page = client.scroll(collection_name=collection_name, with_payload=True)
# company_names = [point.payload["metadata"]["company_name"] for point in points]
report_details = pd.read_excel("data/report_details.xlsx")

selected_company = st.selectbox("Select a company:", set(report_details['company_name']))
selected_country = st.selectbox("Select a country:", report_details[report_details['company_name'] == selected_company]['country'])
query = st.text_input("Enter your query here:")
submit_btn = st.button("Submit")

# instantiate the embedding model
embedding_model = SentenceTransformerEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")

# instantiate the qdrant client object
client = QdrantClient(
    url="https://94d74b83-c25c-4b39-b117-9aec9a65db4c.us-east4-0.gcp.cloud.qdrant.io",
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.Lt2YQ-IAfyBJAbRK6F2IxjnojnKSm72ENq-4z7-wqZY"
)

if submit_btn:
    with st.spinner("Please wait while I process your query..."):
        # embed the query
        query_vector = embedding_model.embed_query(query)

        collection_name="wieland_reports"

        # # create payload index
        # client.create_payload_index(
        #     collection_name=collection_name,
        #     field_name="metadata.company_name",
        #     field_schema=models.PayloadSchemaType.KEYWORD  # Exact match filtering
        # )

        # search for relevant chunks
        results = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=5,
            query_filter=Filter(must=[FieldCondition(key="metadata.company_name", match=MatchValue(value=selected_company))])
        )
        
        # filter out results with low scores
        score_threshold = 0.4
        filtered_results = [r for r in results if r.score >= score_threshold]

        # if there are relevant chunks, generate the prompt and display the response
        if len(filtered_results) > 0:
            context = "\n".join([result.payload["page_content"] for result in filtered_results])
            prompt = f"""
            Answer the question based only on the following context: \n
            {context}
            ----
            Answer the question based on the above context: \n{query}
            """

            # prompt LLM and display the response
            placeholder = st.empty()
            output_text = ""

            # "localhost:11434"
            llm = OllamaLLM(model="mistral")
            # llm.invoke("The first man on the moon was ...")
            for chunk in llm.stream(prompt):
                output_text += chunk
                placeholder.markdown(f"""{output_text}""")
        elif query == "":
            st.write("Please enter a valid query.")
        else:
            st.write("Unfortunately, I wasn’t able to find relevant data in my database to provide an accurate answer to your prompt. Please try again with a different prompt.")




