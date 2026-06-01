# src/utils.py
import base64
from pathlib import Path
import streamlit as st

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_ASSETS_DIR = _PROJECT_ROOT / "assets"
_LOGO_FILENAME = "logo_emova_group.png"


@st.cache_data(ttl=3600, show_spinner=False)
def logo_data_uri() -> str | None:
    p = _ASSETS_DIR / _LOGO_FILENAME
    if not p.exists():
        return None
    data = p.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    ext = p.suffix.lower().lstrip(".") or "png"
    return f"data:image/{ext};base64,{b64}"


def inject_base_css():
    st.markdown(
        """
<style>
:root{
  --emova-green: #95d1bd;
  --emova-green-dark: #7fbda8;
  --emova-dark: #585857;
  --emova-light: #d1d3d4;
  --emova-white: #ffffff;
  --emova-soft: #edf7f3;
  --emova-input-bg: #f7f8fa;
}
</style>
        """,
        unsafe_allow_html=True,
    )
