import streamlit as st
import pandas as pd

from agents.ingestion    import ingest_pipeline
from agents.embedding    import embed_documents
from agents.retrieval    import RetrievalAgent
from agents.ranking      import RankingAgent
from agents.summarization import SummarizationAgent

st.set_page_config(page_title="RAG Demo", layout="wide")
st.title("🤖 RAG Pipeline: Ingest → Embed → Retrieve → Rank → Summarize")

mode = st.sidebar.radio("Choose step", ["1) Ingest & Embed", "2) Search & Rank", "3) Generate Summary"])

if mode == "1) Ingest & Embed":
    st.header("Step 1: Ingest & Embed")
    if "docs" not in st.session_state:
        store, docs = ingest_pipeline("data/reports")
        docs = embed_documents(docs)
        st.session_state.docs      = docs
        st.session_state.retriever = RetrievalAgent(docs)
        st.success("✅ Ingestion & Embedding done")
    st.write(f"Total chunks: {len(st.session_state.docs)}")

elif mode == "2) Search & Rank":
    st.header("Step 2: Search & Rank")
    if "docs" not in st.session_state:
        st.error("Complete Step 1 first!")
    else:
        agent      = st.session_state.retriever
        ranker     = RankingAgent()
        query = st.text_input("Enter search query:", "")
        if query:
            hits   = agent.retrieve(query, top_k=10)
            ranked = ranker.rank(query, hits)
            df = pd.DataFrame(ranked[:5])[["source","rank_score","content"]]
            df.columns = ["Source","Score","Content"]
            st.dataframe(df, use_container_width=True)

elif mode == "3) Generate Summary":
    st.header("Step 3: Summarize Top Passages")
    if "docs" not in st.session_state:
        st.error("Complete Step 1 and 2 first!")
    else:
        query = st.text_input("Enter the same query again:", "")
        if query:
            # retrieve + rank as before
            agent  = st.session_state.retriever
            hits   = agent.retrieve(query, top_k=10)
            ranked = RankingAgent().rank(query, hits)
            
            # summarize top 5
            summarizer = SummarizationAgent()
            summary = summarizer.summarize(ranked[:5])
            
            st.subheader("📝 Generated Summary")
            st.write(summary)
