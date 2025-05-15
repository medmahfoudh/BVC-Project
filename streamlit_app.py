import streamlit as st

# Add the logo to the sidebar
st.logo("assets/logo_wieland.svg", size = "large")


st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"]::before {
            content: "Wieland AI Assistant";
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
    st.Page("pages/page_1.py", title = "Chat with AI", icon = "💬"),
    st.Page("pages/page_2.py", title = "Upload New Reports", icon = "📂"),
    ])

pg.run()