# pages/page_3_referentiel.py
import pandas as pd
import streamlit as st
from datetime import datetime

from src.supabase_client import get_supabase
from src.auth import require_auth
from src.ui import top_bar, tabs_nav

st.set_page_config(page_title="Référentiel Article", layout="wide")

require_auth()
top_bar("Référentiel Article")
tabs_nav(active="referentiel")
st.divider()

supabase = get_supabase()

st.markdown("## 📦 Déposer un référentiel article (Excel / CSV)")

uploaded = st.file_uploader(
    "Choisir un fichier Excel (.xlsx) ou CSV (.csv)",
    type=["xlsx", "csv"],
)

# Preview chemin cible
if uploaded:
    ext_preview  = uploaded.name.rsplit(".", 1)[-1].lower()
    preview_path = f"referentiel_{datetime.now().strftime('%y%m%d_%H%M%S')}.{ext_preview}"
    st.caption(f"📁 Chemin cible : `{preview_path}`")

    try:
        if ext_preview == "csv":
            df_preview = pd.read_csv(uploaded, sep=None, engine="python", nrows=5)
        else:
            df_preview = pd.read_excel(uploaded, nrows=5)
        st.markdown("**Aperçu — 5 premières lignes :**")
        st.dataframe(df_preview, use_container_width=True)
        uploaded.seek(0)
    except Exception as e:
        st.warning(f"Impossible d'afficher l'aperçu : {e}")

if st.button("⬆️ Uploader le référentiel", key="btn_upload_ref", type="primary"):
    if not uploaded:
        st.warning("Merci de choisir un fichier.")
        st.stop()

    with st.spinner("⏳ Upload en cours..."):
        try:
            ext          = uploaded.name.rsplit(".", 1)[-1].lower()
            object_path  = f"referentiel_{datetime.now().strftime('%y%m%d_%H%M%S')}.{ext}"
            uploader_email = st.session_state.get("sb_user", {}).get("email", "inconnu")

            content_type = (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                if ext == "xlsx"
                else "text/csv"
            )

            supabase.storage.from_("referentiel").upload(
                path=object_path,
                file=uploaded.getvalue(),
                file_options={"content-type": content_type, "upsert": "true"},
            )

            try:
                supabase.table("upload_logs").insert({
                    "uploader":   uploader_email,
                    "store_name": None,
                    "file_path":  object_path,
                    "file_type":  ext,
                }).execute()
            except Exception:
                pass

            st.success(f"✅ Upload réussi par **{uploader_email}** : `{object_path}`")

        except Exception as e:
            st.error(f"❌ Upload impossible : {e}")
