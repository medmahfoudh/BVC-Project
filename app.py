import streamlit as st

# 1️⃣ This must come first, before any st.* calls:
st.set_page_config(
    page_title="IntelFlow",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2️⃣ Now you can do your other Streamlit stuff:
# Add the logo to the sidebar
st.logo("assets/logo_wieland.svg", size="large")

st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"]::before {
            content: "IntelFlow";
            margin-left: 20px;
            margin-bottom: 20px;
            font-size: 30px;
            font-weight: bold;
        }
        
        [data-testid="stSidebarNav"]{
            margin-top: 30px;
        }

        [data-testid="stSidebarNav"] > *{
            margin-top: 50px;
        }

    </style>
    """,
    unsafe_allow_html=True,
)

# Navigation pages
pg = st.navigation([
    st.Page("pages/dashboard.py",        title="Dashboard",                    icon="📊"),
    st.Page("pages/IntelAsk.py",           title="IntelAsk",                    icon="💬"),
    st.Page("pages/IntelBrief.py",           title="IntelBrief",   icon="📝"),
    st.Page("pages/IntelSignal.py",           title="IntelSignal",icon="📈"),
    st.Page("pages/Upload.py",           title="Upload New Reports",           icon="📂"),
])

pg.run()
