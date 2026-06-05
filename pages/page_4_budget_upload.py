# pages/page_4_budget_upload.py
import pandas as pd
import streamlit as st
from datetime import datetime

from src.supabase_client import get_supabase
from src.auth import require_auth
from src.ui import top_bar, tabs_nav

st.set_page_config(page_title="Upload Budget", layout="wide")

require_auth()
top_bar("Upload Budget Magasin")
tabs_nav(active="budget")
st.divider()

supabase = get_supabase()


@st.cache_data(ttl=3600, show_spinner="⏳ Chargement des magasins...")
def load_stores_budget():
    res_codes = (
        supabase.table("v_budget_vs_ca_jour")
        .select("code_magasin,nom_ville")
        .order("code_magasin")
        .limit(500)
        .execute()
    )
    res_mag = supabase.table("magasins").select("store_name_pdf,nom_ville").execute()

    ville_to_store = {
        r["nom_ville"]: r["store_name_pdf"]
        for r in (res_mag.data or [])
        if r.get("nom_ville") and r.get("store_name_pdf")
    }

    seen: dict[str, str] = {}
    for r in res_codes.data or []:
        c, v = r.get("code_magasin"), r.get("nom_ville")
        if c and v and c not in seen:
            seen[c] = v

    stores = []
    for code, ville in seen.items():
        label = f"{code} – {ville}"
        stores.append({"code": code, "ville": ville, "label": label})

    stores.sort(key=lambda x: x["code"])
    return stores


stores = load_stores_budget()
store_labels = [s["label"] for s in stores]
label_to_code = {s["label"]: s["code"] for s in stores}
label_to_ville = {s["label"]: s["ville"] for s in stores}

# ── Modèle à télécharger ───────────────────────────────────────────────────────
st.markdown("## 📥 Télécharger le modèle de budget")

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_template() -> bytes | None:
    try:
        return get_supabase().storage.from_("budget").download("budget_0.csv")
    except Exception:
        return None

_template_bytes = fetch_template()
if _template_bytes:
    st.download_button(
        label="⬇️ Télécharger le modèle CSV (budget_0.csv)",
        data=_template_bytes,
        file_name="budget_0.csv",
        mime="text/csv",
        key="btn_dl_template",
    )
else:
    st.warning("Modèle introuvable dans le bucket (budget/budget_0.csv).")

st.divider()

# ── Sélection du magasin ───────────────────────────────────────────────────────
st.markdown("## 🏬 Sélection du magasin")

if not stores:
    st.warning("Aucun magasin disponible. Vérifiez la connexion à Supabase.")
    st.stop()

selected_label = st.selectbox(
    "Magasin cible",
    options=store_labels,
    index=0,
    key="budget_store_select",
    help="Choisissez le magasin pour lequel vous uploadez le fichier budget.",
)

selected_code = label_to_code[selected_label]
selected_ville = label_to_ville[selected_label]

st.info(f"📍 Magasin sélectionné : **{selected_label}**")

st.divider()

# ── Upload du fichier ──────────────────────────────────────────────────────────
st.markdown("## 📂 Fichier budget (Excel / CSV)")

uploaded = st.file_uploader(
    "Choisir un fichier Excel (.xlsx) ou CSV (.csv)",
    type=["xlsx", "csv"],
    key="budget_file_uploader",
)

if uploaded:
    ext_preview = uploaded.name.rsplit(".", 1)[-1].lower()
    object_path = f"{selected_code}/budget_{datetime.now().strftime('%y%m%d_%H%M%S')}.{ext_preview}"
    st.caption(f"📁 Chemin cible dans le bucket **budget** : `{object_path}`")

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

# ── Bouton upload ──────────────────────────────────────────────────────────────
if st.button("⬆️ Uploader le budget", key="btn_upload_budget", type="primary"):
    if not uploaded:
        st.warning("Merci de choisir un fichier avant d'uploader.")
        st.stop()

    with st.spinner("⏳ Upload en cours..."):
        try:
            ext = uploaded.name.rsplit(".", 1)[-1].lower()
            object_path = (
                f"{selected_code}/budget_{datetime.now().strftime('%y%m%d_%H%M%S')}.{ext}"
            )
            uploader_email = st.session_state.get("sb_user", {}).get("email", "inconnu")

            content_type = (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                if ext == "xlsx"
                else "text/csv"
            )

            supabase.storage.from_("budget").upload(
                path=object_path,
                file=uploaded.getvalue(),
                file_options={"content-type": content_type, "upsert": "true"},
            )

            try:
                supabase.table("upload_logs").insert({
                    "uploader":   uploader_email,
                    "store_name": selected_code,
                    "file_path":  object_path,
                    "file_type":  ext,
                }).execute()
            except Exception:
                pass

            st.success(
                f"✅ Budget uploadé avec succès par **{uploader_email}**\n\n"
                f"🏬 Magasin : **{selected_label}**\n\n"
                f"📁 Fichier : `{object_path}`"
            )

        except Exception as e:
            st.error(f"❌ Upload impossible : {e}")
