# pages/page_2_upload_pdf.py
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

st.markdown("## 📄 Déposer un PDF (classé par magasin / date)")


@st.cache_data(ttl=3600, show_spinner="⏳ Chargement des magasins...")
def load_stores_pdf():
    res_codes = (
        get_supabase()
        .table("v_budget_vs_ca_jour")
        .select("code_magasin,nom_ville")
        .order("code_magasin")
        .limit(500)
        .execute()
    )
    seen: dict[str, str] = {}
    for r in res_codes.data or []:
        c, v = r.get("code_magasin"), r.get("nom_ville")
        if c and v and c not in seen:
            seen[c] = v

    stores = [{"code": c, "ville": v, "label": f"{c} – {v}"} for c, v in seen.items()]
    stores.sort(key=lambda x: x["code"])
    return stores


stores = load_stores_pdf()

if not stores:
    st.error("Aucun magasin trouvé. Vérifiez la connexion à Supabase.")
    st.stop()

store_labels   = [s["label"] for s in stores]
label_to_code  = {s["label"]: s["code"]  for s in stores}
label_to_ville = {s["label"]: s["ville"] for s in stores}

selected_label = st.selectbox(
    "🏬 Sélectionne le magasin",
    options=store_labels,
    index=0,
    key="pdf_store_select",
)
selected_code = label_to_code[selected_label]

date_code = st.text_input(
    "📅 Date du PDF (format YYMMDD)",
    placeholder="260219",
    max_chars=6,
)
uploaded = st.file_uploader("Choisir un fichier PDF", type=["pdf"])

# Aperçu du chemin cible
if selected_code and date_code and len(date_code) == 6 and date_code.isdigit():
    preview_path = f"{selected_code}/{selected_code.lower()}_{date_code}.pdf"
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
            object_path    = f"{selected_code}/{selected_code.lower()}_{date_code}.pdf"
            uploader_email = st.session_state.get("sb_user", {}).get("email", "inconnu")

            supabase.storage.from_("ventes").upload(
                path=object_path,
                file=uploaded.getvalue(),
                file_options={"content-type": "application/pdf", "upsert": "true"},
            )

            try:
                supabase.table("upload_logs").insert({
                    "uploader":   uploader_email,
                    "store_name": selected_code,
                    "file_path":  object_path,
                    "file_type":  "pdf",
                }).execute()
            except Exception:
                pass

            st.success(
                f"✅ Upload réussi par **{uploader_email}**\n\n"
                f"🏬 Magasin : **{selected_label}**\n\n"
                f"📁 Fichier : `{object_path}`"
            )

        except Exception as e:
            st.error(f"❌ Upload impossible : {e}")
