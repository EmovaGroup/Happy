# pages/page_1.py
import pandas as pd
import altair as alt
import streamlit as st
from datetime import date

from src.supabase_client import get_supabase
from src.auth import require_auth
from src.ui import top_bar, tabs_nav

# =============================================================================
# Page config
# =============================================================================
st.set_page_config(page_title="Tableau de bord Happy", layout="wide")

# Auth + header
require_auth()
top_bar("Tableau de bord Happy")
tabs_nav(active="matrix")

# =============================================================================
# CSS — PAGE ONLY (le global est dans src/ui.py)
# =============================================================================
def inject_page_css():
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
}

/* ============================================================================
TABLEAU HTML CUSTOM
============================================================================ */
.table-wrap{
  width:100%;
  overflow:auto;
  border:1px solid var(--emova-light);
  border-radius:12px;
  background:var(--emova-white);
}

.table-wrap table{
  border-collapse:separate;
  border-spacing:0;
  width:max-content;
  min-width:100%;
  font-size:12px;
}

.table-wrap thead th{
  position:sticky;
  top:0;
  z-index:5;
  background:var(--emova-green);
  color:var(--emova-white);
  padding:10px 12px;
  font-weight:900;
  border-right:1px solid rgba(255,255,255,0.18);
  white-space:nowrap;
  text-align:center !important;
  vertical-align:middle !important;
}

.table-wrap td{
  background:var(--emova-white);
  border-bottom:1px solid #eef2f7;
  border-right:1px solid #eef2f7;
  padding:8px 10px;
  text-align:center;
  color:var(--emova-dark);
  white-space:nowrap;
  vertical-align:middle !important;
  height:44px;
}

.table-wrap th.sticky-left,
.table-wrap td.sticky-left{
  position:sticky;
  left:0;
  z-index:6;
  background:var(--emova-soft) !important;
  font-weight:900;
  border-right:1px solid var(--emova-light) !important;
  color:var(--emova-dark) !important;
}

.table-wrap th.sticky-right,
.table-wrap td.sticky-right{
  position:sticky;
  right:0;
  z-index:6;
  background:var(--emova-soft) !important;
  font-weight:900;
  border-left:1px solid var(--emova-light) !important;
  color:var(--emova-dark) !important;
}

/* ============================================================================
PILLS
============================================================================ */
.pill{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  gap:6px;
  padding:7px 10px;
  border-radius:10px;
  font-weight:900;
  min-width:92px;
  min-height:34px;
  box-sizing:border-box;
  border:1px solid rgba(0,0,0,0.05);
  box-shadow:0 1px 0 rgba(0,0,0,0.03);
  color:var(--emova-dark);
}

.pill-up{
  background:rgba(46,204,113,.18) !important;
}

.pill-down{
  background:rgba(231,76,60,.18) !important;
}

.pill-neutral{
  background:rgba(127,127,127,.10) !important;
}

.arrow-up,
.arrow-down{
  font-size:11px;
  line-height:1;
  font-weight:900;
  color:var(--emova-dark);
}

/* TOTAL */
.tr-total td{
  background:#f5f8f7 !important;
  font-weight:900 !important;
}

.tr-total td.sticky-left{
  background:var(--emova-soft) !important;
}

/* ============================================================================
KPI CARDS
============================================================================ */
.emova-kpi-card{
  border:2px solid var(--emova-green);
  border-radius:14px;
  padding:18px 16px;
  text-align:center;
  background:var(--emova-white);
  height:112px;
  display:flex;
  flex-direction:column;
  justify-content:center;
  align-items:center;
  margin:6px 4px 10px 4px;
  box-shadow:0 4px 10px rgba(88,88,87,0.06);
}

.emova-kpi-title{
  font-size:13px;
  font-weight:800;
  color:var(--emova-dark);
  margin-bottom:8px;
}

.emova-kpi-value{
  font-size:28px;
  font-weight:900;
  color:var(--emova-green);
  line-height:1.1;
}

/* ============================================================================
RAYON CARDS
============================================================================ */
.rayon-card{
  border:2px solid var(--emova-green);
  border-radius:14px;
  padding:18px;
  background:var(--emova-white);
  box-shadow:0 4px 12px rgba(149,209,189,0.18);
}

.rayon-title{
  color:var(--emova-dark);
  font-weight:900;
  font-size:14px;
  margin-bottom:12px;
  text-align:center;
}

.rayon-center{
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  text-align:center;
  width:100%;
  margin-bottom:14px;
}

.rayon-sub{
  font-size:11px;
  color:var(--emova-dark);
  margin-bottom:6px;
  font-weight:700;
  text-transform:uppercase;
  letter-spacing:.4px;
}

.rayon-main-value{
  font-size:28px;
  font-weight:900;
  color:var(--emova-green);
  line-height:1.2;
}

.rayon-grid{
  display:flex;
  gap:12px;
  margin-top:10px;
}

.rayon-mini{
  flex:1;
  background:#f8f8f8;
  border:1px solid var(--emova-light);
  border-radius:10px;
  padding:10px;
  text-align:center;
}

.rayon-mini-label{
  font-size:11px;
  color:var(--emova-dark);
  font-weight:700;
  margin-bottom:6px;
}

.rayon-mini-value{
  font-size:20px;
  font-weight:900;
  color:var(--emova-green);
}

/* ============================================================================
Granularité buttons
============================================================================ */
.granularity-note{
  font-size: 0.001px;
}
</style>
        """,
        unsafe_allow_html=True,
    )


inject_page_css()

# =============================================================================
# Helpers
# =============================================================================
JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
JOURS_MAP = {
    0: "Lundi",
    1: "Mardi",
    2: "Mercredi",
    3: "Jeudi",
    4: "Vendredi",
    5: "Samedi",
    6: "Dimanche",
}


def fmt_eur(x):
    if pd.isna(x):
        return ""
    return f"{x:,.2f} €".replace(",", " ").replace(".", ",")


def fmt_int(x):
    if pd.isna(x):
        return ""
    return f"{int(round(x)):,.0f}".replace(",", " ")


def last_weeks(iso_keys, n=3):
    uniq = sorted(pd.Series(iso_keys).dropna().unique().tolist())
    return uniq[-n:] if len(uniq) >= n else uniq


def render_heat_table(df_wide: pd.DataFrame, euro: bool, title: str, dl_name: str):
    cols = list(df_wide.columns)
    if "Jour" not in cols or "Moyenne" not in cols:
        st.error("Tableau invalide : il manque Jour ou Moyenne.")
        return

    week_cols = [c for c in cols if c not in ("Jour", "Moyenne")]

    def cell_html(val, base):
        if pd.isna(val):
            return ""

        if base is None or pd.isna(base):
            cls = "pill pill-neutral"
            arrow = ""
        else:
            if val >= base:
                cls = "pill pill-up"
                arrow = '<span class="arrow-up">▲</span>'
            else:
                cls = "pill pill-down"
                arrow = '<span class="arrow-down">▼</span>'

        txt = fmt_eur(val) if euro else fmt_int(val)
        return f'<span class="{cls}">{txt} {arrow}</span>'

    thead = "<thead><tr>"
    thead += '<th class="sticky-left">Jour</th>'
    for c in week_cols:
        thead += f"<th>{c}</th>"
    thead += '<th class="sticky-right">Moyenne</th>'
    thead += "</tr></thead>"

    tbody = "<tbody>"
    for _, row in df_wide.iterrows():
        is_total = str(row["Jour"]).strip().upper() == "TOTAL"
        tr_cls = "tr-total" if is_total else ""
        base = row["Moyenne"] if "Moyenne" in row else None

        tbody += f'<tr class="{tr_cls}">'
        tbody += f'<td class="sticky-left">{row["Jour"]}</td>'

        for c in week_cols:
            tbody += f"<td>{cell_html(row[c], base)}</td>"

        moy_txt = fmt_eur(row["Moyenne"]) if euro else fmt_int(row["Moyenne"])
        tbody += f'<td class="sticky-right">{moy_txt}</td>'
        tbody += "</tr>"
    tbody += "</tbody>"

    html = (
        f'<div style="margin-top:10px;margin-bottom:8px;">'
        f'<h4 style="margin:8px 0 12px 0;color:#585857;">{title}</h4>'
        f'<div class="table-wrap">'
        f'<table>{thead}{tbody}</table>'
        f'</div>'
        f'</div>'
    )

    st.markdown(html, unsafe_allow_html=True)

    csv = df_wide.to_csv(index=False, sep=";", encoding="utf-8")
    st.download_button(
        label=f"📥 Télécharger {dl_name}",
        data=csv,
        file_name=f"{dl_name}.csv",
        mime="text/csv",
        key=f"download_{dl_name}",
        use_container_width=True,
    )


def sum_numeric_cols(df_in: pd.DataFrame, cols: list[str]) -> dict:
    return {c: pd.to_numeric(df_in[c], errors="coerce").sum() for c in cols}


def mean_numeric_cols(df_in: pd.DataFrame, cols: list[str]) -> dict:
    return {c: pd.to_numeric(df_in[c], errors="coerce").mean() for c in cols}


# =============================================================================
# Load filters
# =============================================================================
@st.cache_data(ttl=300)
def load_filters():
    supabase = get_supabase()

    r1 = (
        supabase.table("v_matrix")
        .select("period_date")
        .order("period_date", desc=False)
        .limit(1)
        .execute()
    )
    r2 = (
        supabase.table("v_matrix")
        .select("period_date")
        .order("period_date", desc=True)
        .limit(1)
        .execute()
    )

    batch_size = 1000
    offset = 0
    all_stores = []

    while True:
        res = (
            supabase.table("v_matrix")
            .select("store_name")
            .neq("store_name", "")
            .order("store_name", desc=False)
            .range(offset, offset + batch_size - 1)
            .execute()
        )

        if not res.data:
            break

        all_stores.extend(res.data)
        offset += batch_size

    if not r1.data or not r2.data:
        return None, None, []

    dmin = pd.to_datetime(r1.data[0]["period_date"]).date()
    dmax = pd.to_datetime(r2.data[0]["period_date"]).date()
    stores = sorted({row["store_name"] for row in all_stores if row.get("store_name")})

    return dmin, dmax, stores


dmin, dmax, stores = load_filters()
if dmin is None:
    st.warning("Aucune donnée dans v_matrix.")
    st.stop()

# =============================================================================
# Load data
# =============================================================================
@st.cache_data(ttl=300)
def load_data(dstart: date, dend: date, store_names: list[str]) -> pd.DataFrame:
    supabase = get_supabase()

    cols = (
        "store_name,period_date,code_article,libelle_final,"
        "famille_finale,rayon,code_rayon,qte,ventes_ht,ventes_ttc,marge_ht,marge_pct"
    )

    batch_size = 1000
    offset = 0
    all_data = []

    while True:
        query = (
            supabase.table("v_matrix")
            .select(cols)
            .gte("period_date", dstart.isoformat())
            .lte("period_date", dend.isoformat())
            .order("period_date", desc=False)
            .order("store_name", desc=False)
        )

        if store_names and "Tous les magasins" not in store_names:
            query = query.in_("store_name", store_names)

        res = query.range(offset, offset + batch_size - 1).execute()

        if not res.data:
            break

        all_data.extend(res.data)
        offset += batch_size

    df = pd.DataFrame(all_data or [])
    if df.empty:
        return df

    df["period_date"] = pd.to_datetime(df["period_date"])

    for c in ["qte", "ventes_ht", "ventes_ttc", "marge_ht", "marge_pct"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    iso = df["period_date"].dt.isocalendar()
    df["iso_year"] = iso.year.astype(int)
    df["iso_week"] = iso.week.astype(int)
    df["iso_key"] = (df["iso_year"] * 100 + df["iso_week"]).astype(int)
    df["iso_label"] = "S" + df["iso_week"].astype(str).str.zfill(2) + "-" + df["iso_year"].astype(str)
    df["jour"] = df["period_date"].dt.weekday.map(JOURS_MAP)

    return df


# =============================================================================
# UI Filters
# =============================================================================
st.markdown(
    """
    <h2 style="color:#585857;font-weight:900;margin-bottom:12px;">
        📊 Tableau de bord
    </h2>
    """,
    unsafe_allow_html=True,
)

col_filters = st.columns([2, 2, 3])

with col_filters[0]:
    st.markdown("**📅 Période**")
    drange = st.date_input(
        "",
        value=(dmin, dmax),
        min_value=dmin,
        max_value=dmax,
        label_visibility="collapsed",
    )

if isinstance(drange, tuple) and len(drange) == 2:
    dstart, dend = drange
else:
    dstart = dend = drange

with col_filters[1]:
    st.markdown("**⏱️ Granularité**")

    if "granularity_matrix" not in st.session_state:
        st.session_state["granularity_matrix"] = "Jour"

    g1, g2, g3 = st.columns(3)

    with g1:
        if st.button(
            "Jour",
            key="granularity_jour",
            use_container_width=True,
            type="primary" if st.session_state["granularity_matrix"] == "Jour" else "secondary",
        ):
            st.session_state["granularity_matrix"] = "Jour"

    with g2:
        if st.button(
            "Semaine",
            key="granularity_semaine",
            use_container_width=True,
            type="primary" if st.session_state["granularity_matrix"] == "Semaine" else "secondary",
        ):
            st.session_state["granularity_matrix"] = "Semaine"

    with g3:
        if st.button(
            "Mois",
            key="granularity_mois",
            use_container_width=True,
            type="primary" if st.session_state["granularity_matrix"] == "Mois" else "secondary",
        ):
            st.session_state["granularity_matrix"] = "Mois"

    granularity = st.session_state["granularity_matrix"]

with col_filters[2]:
    st.markdown("**🏬 Magasins à comparer**")
    store_options = ["Tous les magasins"] + stores
    selected_stores = st.multiselect(
        "",
        store_options,
        default=["Tous les magasins"],
        label_visibility="collapsed",
    )

if st.button("⚡ Charger / Actualiser les données", key="btn_load_matrix_data", type="primary"):
    st.session_state["stores_selected"] = selected_stores
    st.session_state["df"] = load_data(dstart, dend, selected_stores)

st.caption("Astuce : choisis 📅 la période, ⏱️ la granularité et 🏬 les magasins, puis clique sur ⚡ Charger.")

df = st.session_state.get("df")
if df is None:
    st.info("Clique sur ⚡ Charger / Actualiser les données pour afficher le dashboard.")
    st.stop()

if df.empty:
    st.warning("Aucune ligne pour ces filtres.")
    st.stop()

# =============================================================================
# KPIs
# =============================================================================
def kpi_card(title, value, emoji):
    return f"""
    <div class="emova-kpi-card">
        <div class="emova-kpi-title">{emoji} {title}</div>
        <div class="emova-kpi-value">{value}</div>
    </div>
    """


k1, k2, k3 = st.columns(3, gap="small")
k4, k5, k6 = st.columns(3, gap="small")

ca_ttc = df["ventes_ttc"].sum()
ca_ht = df["ventes_ht"].sum()
qte = df["qte"].sum()
commission_pct = 20
commission_carrefour = ca_ht * 0.20
prix_moy = (ca_ttc / qte) if qte else 0.0

with k1:
    st.markdown(kpi_card("CA TTC", fmt_eur(ca_ttc), "💰"), unsafe_allow_html=True)
with k2:
    st.markdown(kpi_card("Nombre d'articles vendus", fmt_int(qte), "🧾"), unsafe_allow_html=True)
with k3:
    st.markdown(kpi_card("Prix moyen d'article", fmt_eur(prix_moy), "📦"), unsafe_allow_html=True)
with k4:
    st.markdown(kpi_card("CA HT", fmt_eur(ca_ht), "📊"), unsafe_allow_html=True)
with k5:
    st.markdown(
        kpi_card("Commission Carrefour", "20 %", "🏬"),
        unsafe_allow_html=True,
    )
with k6:
    st.markdown(
        kpi_card("Commission estimée", fmt_eur(commission_carrefour), "💰"),
        unsafe_allow_html=True,
    )

st.divider()

# =============================================================================
# 1bis) KPIs Rayons (Plantes / Fleurs / Accessoires)
# =============================================================================
st.markdown(
    """
    <h2 style="color:#585857;font-weight:900;margin-top:10px;margin-bottom:18px;">
        🌿 KPIs — Plantes / Fleurs / Accessoires
    </h2>
    """,
    unsafe_allow_html=True,
)

RAYON_KEYS = {
    "Plantes": ["plante", "plantes", "plantes fleuries", "plantes vertes", "succulentes", "cactus"],
    "Fleurs": ["fleur", "fleurs", "bouquet", "bouquets", "bottes", "compositions", "rose"],
    "Accessoires": ["accessoire", "accessoires", "cache", "cache-pot", "vase", "emballage", "bougie", "terreau"],
}


def classify_rayon(r):
    if pd.isna(r):
        return "Autres"

    r = str(r).strip().lower()
    for label, keys in RAYON_KEYS.items():
        if any(k in r for k in keys):
            return label
    return "Autres"


df_r = df.copy()
df_r["rayon_norm"] = df_r["rayon"].apply(classify_rayon)
df_r3 = df_r[df_r["rayon_norm"].isin(["Plantes", "Fleurs", "Accessoires"])].copy()


def render_rayon_card(title, ca, qte):
    prix_moy = (ca / qte) if qte else 0

    html = (
        f'<div class="rayon-card">'
        f'<div class="rayon-title">{title}</div>'
        f'<div class="rayon-center">'
        f'<div class="rayon-sub">CA TTC</div>'
        f'<div class="rayon-main-value">{fmt_eur(ca)}</div>'
        f'</div>'
        f'<div class="rayon-grid">'
        f'<div class="rayon-mini">'
        f'<div class="rayon-mini-label">🧾 Qté</div>'
        f'<div class="rayon-mini-value">{fmt_int(qte)}</div>'
        f'</div>'
        f'<div class="rayon-mini">'
        f'<div class="rayon-mini-label">📦 Prix moyen</div>'
        f'<div class="rayon-mini-value">{fmt_eur(prix_moy)}</div>'
        f'</div>'
        f'</div>'
        f'</div>'
    )

    st.markdown(html, unsafe_allow_html=True)


order_rayons = ["Plantes", "Fleurs", "Accessoires"]

agg_rayon = df_r3.groupby("rayon_norm", as_index=False).agg(
    ca_ttc=("ventes_ttc", "sum"),
    qte=("qte", "sum"),
)

data_map = {row["rayon_norm"]: row for _, row in agg_rayon.iterrows()}

col1, col2, col3 = st.columns(3)
cols_map = {
    "Plantes": col1,
    "Fleurs": col2,
    "Accessoires": col3,
}

for r in order_rayons:
    row = data_map.get(r, {"ca_ttc": 0, "qte": 0})
    with cols_map[r]:
        render_rayon_card(
            r,
            float(row["ca_ttc"]),
            float(row["qte"]),
        )

# =============================================================================
# 1) Graph comparaison magasins (CA TTC)
# =============================================================================
st.markdown(
    """
    <h3 style="color:#585857;font-weight:900;margin-top:8px;">
        📈 Comparaison des magasins — CA TTC
    </h3>
    """,
    unsafe_allow_html=True,
)

df_plot = df.copy()

if "Tous les magasins" in (st.session_state.get("stores_selected") or []):
    df_plot["magasin"] = "Tous les magasins"
else:
    df_plot["magasin"] = df_plot["store_name"]

if granularity == "Jour":
    df_plot["period"] = df_plot["period_date"].dt.strftime("%Y-%m-%d")
    df_plot["period_order"] = df_plot["period_date"]
elif granularity == "Semaine":
    df_plot["period"] = df_plot["iso_label"]
    df_plot["period_order"] = df_plot["iso_key"]
else:
    df_plot["period"] = df_plot["period_date"].dt.to_period("M").astype(str)
    df_plot["period_order"] = df_plot["period_date"].dt.to_period("M").dt.to_timestamp()

agg_chart = (
    df_plot.groupby(["period", "magasin"], as_index=False)
    .agg(
        ventes_ttc=("ventes_ttc", "sum"),
        period_order=("period_order", "min"),
    )
)

chart = alt.Chart(agg_chart).mark_line(point=True).encode(
    x=alt.X(
        "period:N",
        title=f"Période ({granularity})",
        sort=alt.SortField(field="period_order", order="ascending"),
    ),
    y=alt.Y("ventes_ttc:Q", title="CA TTC"),
    color=alt.Color(
        "magasin:N",
        title="Magasin",
        scale=alt.Scale(range=["#95d1bd", "#585857", "#7fbda8", "#d1d3d4"]),
    ),
    tooltip=["magasin", "period", alt.Tooltip("ventes_ttc:Q", format=".2f")],
).properties(height=320)

st.altair_chart(chart, use_container_width=True)

st.divider()

# =============================================================================
# 2) Donut famille (CA TTC)
# =============================================================================
st.markdown(
    """
    <h3 style="color:#585857;font-weight:900;">
        🔥 Répartition du CA TTC par famille
    </h3>
    """,
    unsafe_allow_html=True,
)

stores_for_pie = ["Tous magasins"] + sorted(df["store_name"].dropna().unique().tolist())
pick_store = st.selectbox(
    "Choisir le magasin pour le donut",
    stores_for_pie,
    index=0,
    key="select_pie_store",
)

df_pie = df.copy()
if pick_store != "Tous magasins":
    df_pie = df_pie[df_pie["store_name"] == pick_store]

pie = df_pie.groupby("famille_finale", as_index=False)["ventes_ttc"].sum()
pie = pie[pd.notna(pie["famille_finale"])]

if pie.empty:
    st.info("Pas de données famille sur ce filtre.")
else:
    pie["pct"] = pie["ventes_ttc"] / pie["ventes_ttc"].sum()

    donut_chart = alt.Chart(pie).mark_arc(innerRadius=70).encode(
        theta=alt.Theta("ventes_ttc:Q"),
        color=alt.Color(
            "famille_finale:N",
            title="Famille",
            scale=alt.Scale(
                range=[
                    "#4c78a8",
                    "#f58518",
                    "#54a24b",
                    "#e45756",
                    "#72b7b2",
                    "#b279a2",
                    "#ff9da6",
                    "#9d755d",
                    "#bab0ab",
                ]
            ),
        ),
        tooltip=[
            "famille_finale",
            alt.Tooltip("ventes_ttc:Q", format=".2f"),
            alt.Tooltip("pct:Q", format=".1%"),
        ],
    ).properties(height=320)

    st.altair_chart(donut_chart, use_container_width=True)

st.divider()

# =============================================================================
# 3) Top articles (CA TTC)
# =============================================================================
st.markdown(
    """
    <h3 style="color:#585857;font-weight:900;">
        🏆 Top articles (par CA TTC)
    </h3>
    """,
    unsafe_allow_html=True,
)

top_n = st.slider("Top N", 5, 50, 15, key="slider_top_articles")

top_art = df.groupby(["libelle_final"], as_index=False)["ventes_ttc"].sum()
top_art = top_art.sort_values("ventes_ttc", ascending=False).head(top_n)

bar = alt.Chart(top_art).mark_bar(color="#95d1bd").encode(
    x=alt.X("ventes_ttc:Q", title="CA TTC"),
    y=alt.Y("libelle_final:N", sort="-x", title="Article"),
    tooltip=["libelle_final", alt.Tooltip("ventes_ttc:Q", format=".2f")],
).properties(height=420)

st.altair_chart(bar, use_container_width=True)

st.divider()

# =============================================================================
# 4) Synthèses semaine (3 tableaux)
# =============================================================================
st.markdown(
    """
    <h2 style="color:#585857;font-weight:900;">
        📊 Synthèse Articles & CA TTC
    </h2>
    """,
    unsafe_allow_html=True,
)

week_map = (
    df[["iso_key", "iso_label"]]
    .drop_duplicates()
    .sort_values("iso_key")
    .set_index("iso_key")["iso_label"]
    .to_dict()
)

# --- Articles (qte)
tmp = df.groupby(["jour", "iso_key"], as_index=False)["qte"].sum()
pivot_t = tmp.pivot(index="jour", columns="iso_key", values="qte").reindex(JOURS)
pivot_t = pivot_t.reindex(columns=sorted(pivot_t.columns, reverse=True))
pivot_t.columns = [week_map.get(int(c), str(c)) for c in pivot_t.columns]

tickets_tbl = pivot_t.copy()
tickets_tbl.insert(0, "Jour", tickets_tbl.index)
week_cols = [c for c in tickets_tbl.columns if c != "Jour"]
tickets_tbl["Moyenne"] = tickets_tbl[week_cols].apply(pd.to_numeric, errors="coerce").mean(axis=1)

tot = sum_numeric_cols(tickets_tbl, week_cols)
tot["Jour"] = "TOTAL"
tot["Moyenne"] = tickets_tbl[week_cols].apply(pd.to_numeric, errors="coerce").sum().mean()
tickets_tbl = pd.concat([tickets_tbl, pd.DataFrame([tot])], ignore_index=True)

render_heat_table(
    tickets_tbl,
    euro=False,
    title="🎟️ Synthèse des articles vendus (quantités) par semaine",
    dl_name="tickets",
)

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

# --- CA TTC
tmp = df.groupby(["jour", "iso_key"], as_index=False)["ventes_ttc"].sum()
pivot_ca = tmp.pivot(index="jour", columns="iso_key", values="ventes_ttc").reindex(JOURS)
pivot_ca = pivot_ca.reindex(columns=sorted(pivot_ca.columns, reverse=True))
pivot_ca.columns = [week_map.get(int(c), str(c)) for c in pivot_ca.columns]

ca_tbl = pivot_ca.copy()
ca_tbl.insert(0, "Jour", ca_tbl.index)
week_cols_ca = [c for c in ca_tbl.columns if c != "Jour"]
ca_tbl["Moyenne"] = ca_tbl[week_cols_ca].apply(pd.to_numeric, errors="coerce").mean(axis=1)

tot = sum_numeric_cols(ca_tbl, week_cols_ca)
tot["Jour"] = "TOTAL"
tot["Moyenne"] = ca_tbl[week_cols_ca].apply(pd.to_numeric, errors="coerce").sum().mean()
ca_tbl = pd.concat([ca_tbl, pd.DataFrame([tot])], ignore_index=True)

render_heat_table(
    ca_tbl,
    euro=True,
    title="💶 Synthèse CA TTC par semaine",
    dl_name="ca_ttc",
)

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

# --- Prix moyen d'article
tmp = df.groupby(["jour", "iso_key"], as_index=False).agg(
    tickets=("qte", "sum"),
    ca=("ventes_ttc", "sum"),
)
tmp["prix_moy"] = tmp["ca"] / tmp["tickets"].replace(0, pd.NA)

pivot_pm = tmp.pivot(index="jour", columns="iso_key", values="prix_moy").reindex(JOURS)
pivot_pm = pivot_pm.reindex(columns=sorted(pivot_pm.columns, reverse=True))
pivot_pm.columns = [week_map.get(int(c), str(c)) for c in pivot_pm.columns]

pm_tbl = pivot_pm.copy()
pm_tbl.insert(0, "Jour", pm_tbl.index)
week_cols_pm = [c for c in pm_tbl.columns if c != "Jour"]
pm_tbl["Moyenne"] = pm_tbl[week_cols_pm].apply(pd.to_numeric, errors="coerce").mean(axis=1)

tot = mean_numeric_cols(pm_tbl, week_cols_pm)
tot["Jour"] = "TOTAL"
tot["Moyenne"] = pm_tbl[week_cols_pm].apply(pd.to_numeric, errors="coerce").mean().mean()
pm_tbl = pd.concat([pm_tbl, pd.DataFrame([tot])], ignore_index=True)

render_heat_table(
    pm_tbl,
    euro=True,
    title="🛒 Synthèse Prix moyen d'article par semaine",
    dl_name="panier_moyen",
)

# =============================================================================
# 5) Graphiques — 3 dernières semaines + Moyenne
# =============================================================================
st.divider()
st.markdown(
    """
    <h2 style="color:#585857;font-weight:900;">
        📉 Graphiques — 3 dernières semaines + Moyenne
    </h2>
    """,
    unsafe_allow_html=True,
)

weeks = sorted(df["iso_key"].dropna().unique().tolist())
LAST = last_weeks(weeks, n=3)
LAST_LABELS = [week_map.get(int(w), str(w)) for w in LAST]
ORDER_DOMAIN = LAST_LABELS + ["Moyenne"]
MOY_LABEL = "Moyenne"

if len(LAST) == 0:
    st.info("Pas de semaines disponibles sur la période choisie.")
else:
    base = df.groupby(["iso_key", "jour"], as_index=False).agg(
        qte=("qte", "sum"),
        ca=("ventes_ttc", "sum"),
    )
    base["prix_moy"] = base["ca"] / base["qte"].replace(0, pd.NA)
    base["semaine"] = base["iso_key"].map(lambda x: week_map.get(int(x), str(x)))

    moy = base.groupby("jour", as_index=False).agg(
        qte=("qte", "mean"),
        ca=("ca", "mean"),
        prix_moy=("prix_moy", "mean"),
    )
    moy["semaine"] = MOY_LABEL

    sel = base[base["iso_key"].isin(LAST)].copy()
    plot_df = pd.concat([sel[["semaine", "jour", "qte", "ca", "prix_moy"]], moy], ignore_index=True)
    plot_df["jour"] = pd.Categorical(plot_df["jour"], categories=JOURS, ordered=True)
    plot_df["semaine"] = pd.Categorical(plot_df["semaine"], categories=ORDER_DOMAIN, ordered=True)
    plot_df = plot_df.sort_values(["semaine", "jour"])

    line_domain = [MOY_LABEL] + LAST_LABELS
    line_range = ["#95d1bd", "#4c78a8", "#f58518", "#e45756"]

    st.markdown(
        """
        <h3 style="color:#585857;font-weight:900;">
            📈 Évolution des Articles (qte) — 3 dernières semaines + Moyenne
        </h3>
        """,
        unsafe_allow_html=True,
    )
    ch1 = alt.Chart(plot_df).mark_line(point=True).encode(
        x=alt.X("jour:N", sort=JOURS, title="Jour de la semaine"),
        y=alt.Y("qte:Q", title="Articles vendus (qte)"),
        color=alt.Color(
            "semaine:N",
            title="Semaine",
            sort=ORDER_DOMAIN,
            scale=alt.Scale(domain=line_domain, range=line_range),
        ),
        tooltip=["semaine", "jour", alt.Tooltip("qte:Q", format=".0f")],
    ).properties(height=320)
    st.altair_chart(ch1, use_container_width=True)

    st.markdown(
        """
        <h3 style="color:#585857;font-weight:900;">
            📈 Évolution du CA TTC — 3 dernières semaines + Moyenne
        </h3>
        """,
        unsafe_allow_html=True,
    )
    ch2 = alt.Chart(plot_df).mark_line(point=True).encode(
        x=alt.X("jour:N", sort=JOURS, title="Jour de la semaine"),
        y=alt.Y("ca:Q", title="CA TTC"),
        color=alt.Color(
            "semaine:N",
            title="Semaine",
            sort=ORDER_DOMAIN,
            scale=alt.Scale(domain=line_domain, range=line_range),
        ),
        tooltip=["semaine", "jour", alt.Tooltip("ca:Q", format=".2f")],
    ).properties(height=320)
    st.altair_chart(ch2, use_container_width=True)

    st.markdown(
        """
        <h3 style="color:#585857;font-weight:900;">
            📈 Évolution du Prix moyen d'article — 3 dernières semaines + Moyenne
        </h3>
        """,
        unsafe_allow_html=True,
    )
    ch3 = alt.Chart(plot_df).mark_line(point=True).encode(
        x=alt.X("jour:N", sort=JOURS, title="Jour de la semaine"),
        y=alt.Y("prix_moy:Q", title="Prix moyen d'article (€)"),
        color=alt.Color(
            "semaine:N",
            title="Semaine",
            sort=ORDER_DOMAIN,
            scale=alt.Scale(domain=line_domain, range=line_range),
        ),
        tooltip=["semaine", "jour", alt.Tooltip("prix_moy:Q", format=".2f")],
    ).properties(height=320)
    st.altair_chart(ch3, use_container_width=True)

# =============================================================================
# 6) Détail lignes
# =============================================================================
st.divider()
st.markdown(
    """
    <h3 style="color:#585857;font-weight:900;">
        🧾 Détail des lignes (période sélectionnée)
    </h3>
    """,
    unsafe_allow_html=True,
)

show_cols = [
    "store_name",
    "period_date",
    "code_article",
    "libelle_final",
    "famille_finale",
    "qte",
    "ventes_ht",
    "ventes_ttc",
    "marge_ht",
    "marge_pct",
    "iso_year",
    "iso_week",
    "iso_key",
    "iso_label",
]

present = [c for c in show_cols if c in df.columns]

st.dataframe(
    df[present].sort_values(["period_date", "store_name"]).head(5000),
    use_container_width=True,
)
