import streamlit as st

def load_material_ui_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
    html, body, .main {font-family: 'Roboto', Arial, sans-serif;}
    .material-card {
        background: #fff;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(33,150,243,.08);
        padding: 2rem 2rem 1.5rem 2rem;
        margin: 32px 0 16px 0;
        border: 1px solid #eee;
    }
    .material-header {
        color: #1976d2;
        margin-bottom: 18px;
        font-weight: 600;
        letter-spacing: 1px;
    }
    .stButton>button {
        width: 100%;
        background: #1976d2;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 10px 0;
        font-weight: 600;
        font-size: 16px;
        margin-top: 8px;
    }
    .stButton>button:hover {background: #125ca0;}
    .material-success {
        background: #e8f5e9;
        border-left: 4px solid #43a047;
        padding: 12px; margin-bottom: 12px; border-radius: 8px;
        color: #256029;
    }
    .material-error {
        background: #ffebee;
        border-left: 4px solid #e53935;
        padding: 12px; margin-bottom: 12px; border-radius: 8px;
        color: #b71c1c;
    }
    .material-info {
        background: #e3f2fd;
        color: #0d47a1;
        padding: 12px; margin-bottom: 12px; border-radius: 8px;
        border-left: 4px solid #2196f3;
    }
    .material-table th {
        background: #e3f2fd;
        color: #1976d2;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)


def material_card(title: str, body: str):
    st.markdown(f"""
    <div class="material-card">
        <div class="material-header">{title}</div>
        <div>{body}</div>
    </div>
    """, unsafe_allow_html=True)
