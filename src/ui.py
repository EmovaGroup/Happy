# src/ui.py  ✅ FIX DUPLICATE BUTTON IDs + ACTIVE STYLE
import base64
import re
from pathlib import Path
import streamlit as st
from .auth import logout

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_ASSETS_DIR = _PROJECT_ROOT / "assets"
_LOGO_FILENAME = "logo_emova_group.png"


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


@st.cache_data(ttl=3600)
def _logo_data_uri() -> str | None:
    p = _ASSETS_DIR / _LOGO_FILENAME
    if not p.exists():
        return None
    data = p.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    ext = p.suffix.lower().lstrip(".") or "png"
    return f"data:image/{ext};base64,{b64}"


def _inject_topbar_css():
    st.markdown(
        """
<style>
  .topbar-wrap { display:flex; align-items:center; justify-content:space-between; gap:14px; margin-top: 4px; margin-bottom: 6px; }
  .topbar-left { display:flex; align-items:center; gap:14px; min-width: 0; }
  .topbar-logo { height: 42px; width: auto; display:block; }
  .topbar-welcome { font-weight: 900; font-size: 22px; line-height: 1; color: #1f6feb; white-space: nowrap; }
  @media (max-width: 720px) { .topbar-welcome { font-size: 18px; } .topbar-logo { height: 36px; } }
</style>
        """,
        unsafe_allow_html=True,
    )


def top_bar(title: str):
    _inject_topbar_css()

    user = st.session_state.get("sb_user", {})
    email = user.get("email", "")
    lastname = _extract_lastname_from_email(email)
    logo_uri = _logo_data_uri()

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
        if st.button("Déconnexion", key="btn_logout_topbar", use_container_width=True):
            logout()

    st.title(title)


def tabs_nav(active: str = "matrix"):
    """
    active: "matrix" | "upload"
    ✅ Fix StreamlitDuplicateElementId via unique keys
    ✅ Active button background changes (no "Vous êtes sur ..." text)
    """

    # CSS: on applique une class wrapper à chaque bouton
    st.markdown(
        f"""
<style>
  .nav-row {{ margin-top: 6px; margin-bottom: 10px; }}

  .nav-active button {{
    background: #111827 !important;
    color: #ffffff !important;
    border: 1px solid #111827 !important;
    font-weight: 900 !important;
  }}
  .nav-active button:hover {{
    background: #0b1220 !important;
    border-color: #0b1220 !important;
  }}

  .nav-inactive button {{
    background: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #e5e7eb !important;
    font-weight: 900 !important;
  }}
  .nav-inactive button:hover {{
    background: #f3f4f6 !important;
  }}
</style>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown(
            f'<div class="{"nav-active" if active=="matrix" else "nav-inactive"} nav-row">',
            unsafe_allow_html=True,
        )
        if st.button("📊 Matrix", key="nav_matrix_btn", use_container_width=True):
            st.switch_page("pages/page_1.py")
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown(
            f'<div class="{"nav-active" if active=="upload" else "nav-inactive"} nav-row">',
            unsafe_allow_html=True,
        )
        if st.button("📄 Upload PDF", key="nav_upload_btn", use_container_width=True):
            st.switch_page("pages/page_2_upload_pdf.py")
        st.markdown("</div>", unsafe_allow_html=True)
