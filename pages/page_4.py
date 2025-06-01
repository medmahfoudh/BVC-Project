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
st.title("Potential Opportunities Agent")

embedding_model = SentenceTransformerEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")

client = QdrantClient(
    url="https://88557973-d9d3-4a8e-a92b-a877815aff1f.eu-central-1-0.aws.cloud.qdrant.io:6333",
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.hTkGVX7aVObKDCE9iB9HBi_Cq_oBJgPJhmQEkqE9LeI"
)

# extract company names from database
# points, next_page = client.scroll(collection_name=collection_name, with_payload=True)
# company_names = [point.payload["metadata"]["company_name"] for point in points]
company_names = pd.read_excel("data/report_details.xlsx")

selected_company = st.selectbox("Select a company:", set(company_names['company_name']))
selected_country = st.selectbox("Select a country:", ["Germany", "Austria", "Switzerland"])
query = "Please highlight the risks and Opportunities in this visit" #st.text_input("Enter your query here:")
submit_btn = st.button("Get Risks and Opportunities")

if submit_btn:
    # embed the query
    query_vector = embedding_model.embed_query(query)
    collection_name="crm_reports_rag"

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
    print(results)

    
    # filter out results with low scores
    score_threshold = 0.09
    filtered_results = [r for r in results if r.score >= score_threshold]

    # if there are relevant chunks, generate the prompt and display the response
    if len(filtered_results) > 0:
        # for debugging
        st.write(f"Number of relevant chunks: {len(filtered_results)}")
        st.write(filtered_results)

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
    else:
        st.write("Unfortunately, I wasn’t able to find relevant data in my database to provide an accurate answer to your prompt. Please try again with a different prompt.")



