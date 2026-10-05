import streamlit as st


st.set_page_config(
    page_title="Machine Risk App",
    page_icon="⚙️",
    layout="wide",
)

pages = [
    st.Page(
        "pages/0_Home.py",
        title="Home",
        icon="🏠",
        default=True,
    ),
    st.Page(
        "pages/1_fields.py",
        title="Fields",
        icon="🧩",
    ),
    st.Page(
        "pages/2_Machines.py",
        title="Machines",
        icon="🏭",
    ),
    st.Page(
        "pages/3_predictions.py",
        title="Prediction",
        icon="📊",
    ),
]

navigation = st.navigation(pages, position="sidebar")
navigation.run()

