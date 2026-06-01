# src/ui.py
import re
import streamlit as st
from .auth import logout
from .utils import logo_data_uri, inject_base_css


def _extract_lastname_from_email(email: str | None) -> str:
    if not email:
        return "!"
    local = email.split("@")[0].strip().lower()
    if not local:
        return "!"
    parts = [p for p in local.split(".") if p]
    candidate = parts[-1] if parts else local
    candidate = re.sub(r"[^a-z\-]", "", candidate).strip()
    return candidate.upper() if candidate else "!"


def _inject_topbar_css():
    inject_base_css()
    st.markdown(
        """
<style>
/* ============================================================================
TOPBAR
============================================================================ */
.topbar-wrap{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:14px;
  margin-top:4px;
  margin-bottom:6px;
}

.topbar-left{
  display:flex;
  align-items:center;
  gap:14px;
  min-width:0;
}

.topbar-logo{
  height:42px;
  width:auto;
  display:block;
}

.topbar-welcome{
  font-weight:900;
  font-size:22px;
  line-height:1;
  color:var(--emova-dark);
  white-space:nowrap;
}

@media (max-width: 720px){
  .topbar-welcome{ font-size:18px; }
  .topbar-logo{ height:36px; }
}

/* ============================================================================
TITRES
============================================================================ */
h1, h2, h3, h4, h5, h6{
  color: var(--emova-dark) !important;
  font-weight: 900 !important;
}

/* ============================================================================
BOUTONS GLOBAUX
============================================================================ */
.stButton > button,
.stDownloadButton > button{
  width:100%;
  border-radius:10px !important;
  border:1px solid var(--emova-light) !important;
  background:var(--emova-green) !important;
  color:var(--emova-white) !important;
  font-weight:900 !important;
  box-shadow:0 2px 8px rgba(88,88,87,0.08) !important;
  transition:all .18s ease !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover{
  background:var(--emova-green-dark) !important;
  border:1px solid var(--emova-green-dark) !important;
  color:var(--emova-white) !important;
}

.stButton > button:focus,
.stDownloadButton > button:focus{
  box-shadow:0 0 0 .18rem rgba(149,209,189,.35) !important;
  outline:none !important;
}

/* styles pour les boutons secondary */
.stButton > button[kind="secondary"]{
  background:var(--emova-white) !important;
  color:var(--emova-dark) !important;
  border:1px solid var(--emova-light) !important;
  font-weight:800 !important;
  box-shadow:none !important;
}

.stButton > button[kind="secondary"]:hover{
  background:#f6faf8 !important;
  border-color:var(--emova-green) !important;
  color:var(--emova-dark) !important;
}

/* ============================================================================
NAVIGATION
============================================================================ */
.nav-row{
  margin-top:6px;
  margin-bottom:10px;
}

/* ============================================================================
SELECTBOX / MULTISELECT
============================================================================ */
div[data-baseweb="select"] > div{
  border-radius:10px !important;
  border:1px solid var(--emova-light) !important;
  min-height:42px !important;
  box-shadow:none !important;
}

div[data-baseweb="select"] > div:hover{
  border-color:var(--emova-green) !important;
}

div[data-baseweb="select"] *{
  color:var(--emova-dark) !important;
}

div[data-baseweb="tag"]{
  background:var(--emova-soft) !important;
  border:1px solid var(--emova-light) !important;
  border-radius:8px !important;
}

div[data-baseweb="tag"] span{
  color:var(--emova-dark) !important;
  font-weight:700 !important;
}

div[data-baseweb="tag"] svg{
  fill:var(--emova-dark) !important;
  color:var(--emova-dark) !important;
}

/* fallback multiselect */
[data-testid="stMultiSelect"] [data-baseweb="tag"]{
  background:var(--emova-soft) !important;
  border:1px solid var(--emova-light) !important;
}

[data-testid="stMultiSelect"] [data-baseweb="tag"] *{
  color:var(--emova-dark) !important;
  fill:var(--emova-dark) !important;
}

/* ============================================================================
DATE INPUT
============================================================================ */
.stDateInput > div > div{
  border-radius:10px !important;
  border:1px solid var(--emova-light) !important;
}

.stDateInput > div > div:hover{
  border-color:var(--emova-green) !important;
}

/* ============================================================================
RADIO
============================================================================ */
div[role="radiogroup"] label{
  color:var(--emova-dark) !important;
  font-weight:700 !important;
}

div[role="radiogroup"] input[type="radio"]{
  accent-color: var(--emova-green) !important;
}

/* ============================================================================
SLIDER
============================================================================ */
.stSlider{
  padding-top:4px;
}

.stSlider label{
  color:var(--emova-dark) !important;
  font-weight:800 !important;
}

.stSlider span{
  color:var(--emova-dark) !important;
  font-weight:900 !important;
}

.stSlider [data-baseweb="slider"]{
  padding-top:8px;
  padding-bottom:8px;
}

.stSlider [data-baseweb="slider"] > div{
  background:transparent !important;
}

.stSlider [data-baseweb="slider"] > div > div{
  background-color:var(--emova-light) !important;
  height:4px !important;
  border-radius:999px !important;
}

.stSlider [data-baseweb="slider"] div[role="slider"] ~ div{
  background-color:var(--emova-green) !important;
  height:4px !important;
  border-radius:999px !important;
}

.stSlider [data-baseweb="slider"] div[role="slider"]{
  background-color:var(--emova-white) !important;
  border:3px solid var(--emova-green) !important;
  box-shadow:0 0 0 1px var(--emova-green) !important;
}

/* ============================================================================
DATAFRAME
============================================================================ */
[data-testid="stDataFrame"]{
  border:1px solid var(--emova-light);
  border-radius:12px;
  overflow:hidden;
}

[data-testid="stDataFrame"] [role="columnheader"]{
  background:var(--emova-green) !important;
  color:var(--emova-white) !important;
  font-weight:900 !important;
}

[data-testid="stDataFrame"] [role="gridcell"]{
  color:var(--emova-dark) !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )


def top_bar(title: str):
    _inject_topbar_css()

    user = st.session_state.get("sb_user", {})
    email = user.get("email", "")
    lastname = _extract_lastname_from_email(email)
    logo_uri = logo_data_uri()

    left, right = st.columns([6, 2], vertical_alignment="center")

    with left:
        if logo_uri:
            st.markdown(
                f"""
                <div class="topbar-wrap" style="justify-content:flex-start;">
                  <div class="topbar-left">
                    <img class="topbar-logo" src="{logo_uri}" alt="logo" />
                    <div class="topbar-welcome">👋&nbsp;Bienvenue&nbsp;{lastname}&nbsp;!</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="topbar-wrap" style="justify-content:flex-start;">
                  <div class="topbar-left">
                    <div class="topbar-welcome">👋&nbsp;Bienvenue&nbsp;{lastname}&nbsp;!</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        if st.button(
            "Déconnexion",
            key="btn_logout_topbar",
            use_container_width=True,
            type="primary",
        ):
            logout()

    st.title(title)


def tabs_nav(active: str = "nvsn1"):
    c1, c2, c3 = st.columns(3, gap="large")

    with c1:
        if st.button(
            "📈 N vs N-1",
            key="nav_nvsn1_btn",
            use_container_width=True,
            type="primary" if active == "nvsn1" else "secondary",
        ):
            st.switch_page("pages/page_1.py")

    with c2:
        if st.button(
            "📄 Upload PDF",
            key="nav_upload_btn",
            use_container_width=True,
            type="primary" if active == "upload" else "secondary",
        ):
            st.switch_page("pages/page_2_upload_pdf.py")

    with c3:
        if st.button(
            "📦 Référentiel",
            key="nav_referentiel_btn",
            use_container_width=True,
            type="primary" if active == "referentiel" else "secondary",
        ):
            st.switch_page("pages/page_3_referentiel.py")
