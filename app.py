# app.py
import streamlit as st

st.set_page_config(page_title="Happy", layout="wide")

# Page d'entrée : on redirige vers la page 1
st.switch_page("pages/page_1.py")
