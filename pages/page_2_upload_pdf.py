# pages/page_2_upload_pdf.py
import re
import streamlit as st
from datetime import datetime

from src.supabase_client import get_supabase
from src.auth import require_auth
from src.ui import top_bar, tabs_nav

st.set_page_config(page_title="Upload PDF", layout="wide")

require_auth()
top_bar("Upload PDF")
tabs_nav(active="upload")
st.divider()

supabase = get_supabase()

st.markdown("## 📄 Déposer un PDF (classé par magasin /date)")

@st.cache_data(ttl=3600, show_spinner="⏳ Chargement des magasins...")
def load_store_names() -> list[str]:
    table = (
        get_supabase()
        .table("v_matrix")
        .select("store_name")
        .neq("store_name", "")
        .order("store_name", desc=False)
    )

    batch_size = 1000
    offset = 0
    all_rows = []
    while True:
        res = table.range(offset, offset + batch_size - 1).execute()
        if not res.data:
            break
        all_rows.extend(res.data)
        offset += batch_size

    return sorted({r["store_name"] for r in all_rows if r.get("store_name")})

def _parse_store_city_code(store_name: str) -> tuple[str, str]:
    """
    Ex: "Magasin ANGLET 0047" -> ("ANGLET", "0047")
    Gère aussi "MAGASIN_ANGLET_0047" etc.
    """
    s = (store_name or "").strip()

    # retire "Magasin" si présent
    s = re.sub(r"(?i)\bmagasin\b", "", s).strip()

    # remplace underscores par espaces pour parser
    s = s.replace("_", " ").strip()

    m = re.search(r"(.+?)\s*(\d{4})\s*$", s)
    if m:
        city = m.group(1).strip()
        code = m.group(2).strip()
    else:
        city = s.strip()
        code = ""

    # normalise ville
    city = re.sub(r"\s+", " ", city).strip()
    return city, code

def build_object_path(store_name: str, date_code: str) -> str:
    """
    Structure demandée exemple:
      magasin_ANGLET_0047/anglet_0047_260219.pdf
    """
    city, code = _parse_store_city_code(store_name)

    city_upper = re.sub(r"\s+", "_", city.upper())
    city_lower = re.sub(r"\s+", "_", city.lower())

    folder = f"magasin_{city_upper}_{code}" if code else f"magasin_{city_upper}"
    filename_base = f"{city_lower}_{code}" if code else f"{city_lower}"

    filename = f"{filename_base}_{date_code}.pdf"
    return f"{folder}/{filename}"

stores = load_store_names()
if not stores:
    st.error("Aucun magasin trouvé dans v_matrix (colonne store_name).")
    st.stop()

store_selected = st.selectbox("🏬 Sélectionne le magasin", stores)
date_code = st.text_input("📅 Date du PDF (format YYMMDD)", placeholder="260219", max_chars=6)
uploaded = st.file_uploader("Choisir un fichier PDF", type=["pdf"])

# Preview chemin cible
preview_path = None
if store_selected and date_code and len(date_code) == 6 and date_code.isdigit():
    preview_path = build_object_path(store_selected, date_code)
    st.caption(f"📁 Chemin cible : `{preview_path}`")

if st.button("⬆️ Uploader le PDF", key="btn_upload_pdf", type="primary"):
    if not uploaded:
        st.warning("Merci de choisir un PDF.")
        st.stop()

    if not (date_code and len(date_code) == 6 and date_code.isdigit()):
        st.error("❌ Date invalide. Mets exactement 6 chiffres au format YYMMDD (ex: 260219).")
        st.stop()

    with st.spinner("⏳ Upload en cours..."):
        try:
            object_path = build_object_path(store_selected, date_code)
            uploader_email = st.session_state.get("sb_user", {}).get("email", "inconnu")

            supabase.storage.from_("ventes").upload(
                path=object_path,
                file=uploaded.getvalue(),
                file_options={
                    "content-type": "application/pdf",
                    "upsert": "true",
                },
            )

            try:
                supabase.table("upload_logs").insert({
                    "uploader": uploader_email,
                    "store_name": store_selected,
                    "file_path": object_path,
                    "file_type": "pdf",
                }).execute()
            except Exception:
                pass

            st.success(f"✅ Upload réussi par **{uploader_email}** : `{object_path}`")

        except Exception as e:
            st.error(f"❌ Upload impossible : {e}")
