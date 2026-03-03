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
st.set_page_config(page_title="Matrix — Ventes & Marge", layout="wide")

# Auth + header
require_auth()
top_bar("Matrix — Ventes & Marge")
tabs_nav(active="matrix")

# =============================================================================
# CSS — TABLES EXACT LOOK (comme ton screenshot)
# =============================================================================
def inject_tables_css():
    st.markdown(
        """
<style>
/* WRAP */
.table-wrap{
  width:100%;
  overflow:auto;
  border:1px solid #e5e7eb;
  border-radius:10px;
  background:#ffffff;
}

/* TABLE */
.table-wrap table{
  border-collapse:separate;
  border-spacing:0;
  width:max-content;
  min-width:100%;
  font-size:12px;
  background:#ffffff;
}

/* HEADER */
.table-wrap thead th{
  position:sticky;
  top:0;
  z-index:5;
  background:#f3f4f6;
  border-bottom:1px solid #e5e7eb;
  border-right:1px solid #e5e7eb;
  padding:10px 12px;
  white-space:nowrap;
  text-align:center !important;
  vertical-align:middle !important;
  font-weight:900;
}

/* CELLS */
.table-wrap td{
  background:#ffffff;
  border-bottom:1px solid #eef2f7;
  border-right:1px solid #eef2f7;
  padding:8px 10px;
  white-space:nowrap;
  text-align:center !important;
  vertical-align:middle !important;
  height:44px;
}

/* LEFT STICKY (Jour) */
.table-wrap th.sticky-left,
.table-wrap td.sticky-left{
  position:sticky;
  left:0;
  z-index:6;
  background:#f3f4f6 !important;
  border-right:1px solid #e5e7eb !important;
  font-weight:900;
}

/* RIGHT STICKY (Moyenne) */
.table-wrap th.sticky-right,
.table-wrap td.sticky-right{
  position:sticky;
  right:0;
  z-index:6;
  background:#f3f4f6 !important;
  border-left:1px solid #e5e7eb !important;
  font-weight:900;
}

/* PILLS */
.pill{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  gap:6px;
  padding:7px 10px;
  border-radius:10px;
  font-weight:900;
  min-width:92px;
  height:34px;
  box-sizing:border-box;
  border:1px solid rgba(0,0,0,0.06);
  box-shadow: 0 1px 0 rgba(0,0,0,0.04);
}

.pill-up{
  background: rgba(46, 204, 113, 0.18) !important;
}

.pill-down{
  background: rgba(231, 76, 60, 0.18) !important;
}

.pill-neutral{
  background: rgba(127,127,127,0.10) !important;
}

.arrow-up, .arrow-down{
  font-size:11px;
  line-height:1;
  font-weight:900;
  color:#111;
}

/* TOTAL row */
.tr-total td{
  background:#f9fafb !important;
  font-weight:900 !important;
}
.tr-total td.sticky-left{
  background:#f3f4f6 !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )

inject_tables_css()

# =============================================================================
# Helpers
# =============================================================================
JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
JOURS_MAP = {0: "Lundi", 1: "Mardi", 2: "Mercredi", 3: "Jeudi", 4: "Vendredi", 5: "Samedi", 6: "Dimanche"}

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
    """
    df_wide attendu = colonnes: Jour + semaines... + Moyenne
    Style = identique au screenshot (pills + fond + sticky)
    """
    cols = list(df_wide.columns)
    if "Jour" not in cols or "Moyenne" not in cols:
        st.error("Tableau invalide : il manque Jour ou Moyenne.")
        return

    week_cols = [c for c in cols if c not in ("Jour", "Moyenne")]

    def cell_html(val, base):
        if pd.isna(val):
            return ""

        # si pas de base => neutre
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

    st.markdown(
        f"""
        <div style="margin-top:10px;margin-bottom:8px;">
          <h4 style="margin:8px 0 12px 0;">{title}</h4>
          <div class="table-wrap">
            <table>
              {thead}
              {tbody}
            </table>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    csv = df_wide.to_csv(index=False, sep=";", encoding="utf-8")
    st.download_button(
        label=f"📥 Télécharger {dl_name}",
        data=csv,
        file_name=f"{dl_name}.csv",
        mime="text/csv",
    )

# =============================================================================
# Load filters (min/max + stores)  ✅ FIX: supabase créé dans le cache
# =============================================================================
@st.cache_data(ttl=300)
def load_filters():
    supabase = get_supabase()

    r1 = supabase.table("v_matrix").select("period_date").order("period_date", desc=False).limit(1).execute()
    r2 = supabase.table("v_matrix").select("period_date").order("period_date", desc=True).limit(1).execute()

    table = (
        supabase.table("v_matrix")
        .select("store_name")
        .neq("store_name", "")
        .order("store_name", desc=False)
    )

    batch_size = 1000
    offset = 0
    all_stores = []
    while True:
        res = table.range(offset, offset + batch_size - 1).execute()
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
# Load data  ✅ FIX: supabase créé dans le cache
# =============================================================================
@st.cache_data(ttl=300)
def load_data(dstart: date, dend: date, store_names: list[str]) -> pd.DataFrame:
    supabase = get_supabase()

    cols = "store_name,period_date,code_article,libelle_final,famille_finale,rayon,code_rayon,qte,ventes_ht,ventes_ttc,marge_ht,marge_pct"

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

    batch_size = 1000
    offset = 0
    all_data = []
    while True:
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
st.markdown("### 📊 Matrix — Ventes & Marge")

col_filters = st.columns([2, 2, 3])

with col_filters[0]:
    st.markdown("**📅 Période**")
    drange = st.date_input("", value=(dmin, dmax), min_value=dmin, max_value=dmax, label_visibility="collapsed")

if isinstance(drange, tuple) and len(drange) == 2:
    dstart, dend = drange
else:
    dstart = dend = drange

with col_filters[1]:
    st.markdown("**⏱️ Granularité**")
    granularity = st.radio("", ["Jour", "Semaine", "Mois"], horizontal=True, label_visibility="collapsed")

with col_filters[2]:
    st.markdown("**🏬 Magasins à comparer**")
    store_options = ["Tous les magasins"] + stores
    selected_stores = st.multiselect("", store_options, default=["Tous les magasins"], label_visibility="collapsed")

if st.button("⚡ Charger / Actualiser les données", type="primary"):
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
    <div style="
        border: 2px solid #e00000;
        border-radius: 14px;
        padding: 22px 20px;
        text-align: center;
        background-color: #ffffff;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin: 12px 8px 20px 8px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.04);
    ">
        <div style="
            font-size: 14px;
            font-weight: 800;
            color: #b00000;
            margin-bottom: 10px;
        ">
            {emoji} {title}
        </div>
        <div style="
            font-size: 30px;
            font-weight: 900;
            color: #111;
        ">
            {value}
        </div>
    </div>
    """

k1, k2, k3 = st.columns(3, gap="large")
k4, k5, k6 = st.columns(3, gap="large")

ca_ttc = df["ventes_ttc"].sum()
ca_ht = df["ventes_ht"].sum()
qte = df["qte"].sum()
marge_ht = df["marge_ht"].sum()
marge_pct = (marge_ht / ca_ht * 100) if ca_ht else 0.0
prix_moy = (ca_ttc / qte) if qte else 0.0

with k1: st.markdown(kpi_card("CA TTC", fmt_eur(ca_ttc), "💰"), unsafe_allow_html=True)
with k2: st.markdown(kpi_card("Nombre d'articles vendus", fmt_int(qte), "🧾"), unsafe_allow_html=True)
with k3: st.markdown(kpi_card("Prix moyen d'article", fmt_eur(prix_moy), "📦"), unsafe_allow_html=True)
with k4: st.markdown(kpi_card("CA HT", fmt_eur(ca_ht), "📊"), unsafe_allow_html=True)
with k5: st.markdown(kpi_card("Marge HT", fmt_eur(marge_ht), "🏦"), unsafe_allow_html=True)
with k6: st.markdown(kpi_card("Marge %", f"{marge_pct:,.2f} %".replace(",", " ").replace(".", ","), "🔥"), unsafe_allow_html=True)

st.divider()

# =============================================================================
# 1bis) KPIs Rayons (Plantes / Fleurs / Accessoires) — CA / Qte / Prix moyen
# =============================================================================
st.markdown("## 🌿 KPIs — Plantes / Fleurs / Accessoires")

RAYON_KEYS = {
    "Plantes": ["plante", "plantes", "plantes fleuries", "plantes vertes", "succulentes", "cactées", "cactee", "cactus"],
    "Fleurs": ["fleur", "fleurs", "bouquet", "bouquets", "bottes", "brassées", "brassees", "compositions", "piquées", "piquees"],
    "Accessoires": ["accessoire", "accessoires", "cache", "cache-pot", "cache pot", "vase", "emballage", "ruban", "carte", "bougie", "terreau", "engrais"]
}

def classify_rayon(r: str) -> str:
    if not isinstance(r, str) or not r.strip():
        return "Autres"
    rr = r.strip().lower()
    for label, keys in RAYON_KEYS.items():
        if any(k in rr for k in keys):
            return label
    return "Autres"

df_r = df.copy()
df_r["rayon_norm"] = df_r.get("rayon", pd.Series([None] * len(df_r))).apply(classify_rayon)

df_r3 = df_r[df_r["rayon_norm"].isin(["Plantes", "Fleurs", "Accessoires"])].copy()

def _kpi_rayon_card(rayon_name: str, ca_ttc: float, qte: float):
    prix_moy = (ca_ttc / qte) if qte else 0.0
    return f"""
    <div style="border:2px solid #e00000;border-radius:14px;padding:16px 18px;background:#fff;
                display:flex;align-items:center;justify-content:space-between;gap:18px;">
      <div style="min-width:180px;">
        <div style="font-size:15px;font-weight:900;color:#b00000;">{rayon_name}</div>
        <div style="font-size:22px;font-weight:900;color:#000;margin-top:4px;">{fmt_eur(ca_ttc)}</div>
        <div style="font-size:12px;opacity:0.75;margin-top:2px;">CA TTC</div>
      </div>

      <div style="display:flex;gap:14px;flex-wrap:wrap;justify-content:flex-end;">
        <div style="border:1px solid rgba(0,0,0,0.12);border-radius:12px;padding:10px 12px;min-width:150px;text-align:center;">
          <div style="font-size:12px;font-weight:800;opacity:0.8;">🧾 Qté</div>
          <div style="font-size:18px;font-weight:900;">{fmt_int(qte)}</div>
        </div>
        <div style="border:1px solid rgba(0,0,0,0.12);border-radius:12px;padding:10px 12px;min-width:150px;text-align:center;">
          <div style="font-size:12px;font-weight:800;opacity:0.8;">📦 Prix moyen</div>
          <div style="font-size:18px;font-weight:900;">{fmt_eur(prix_moy)}</div>
        </div>
      </div>
    </div>
    """

if df_r3.empty:
    st.info("Pas de données sur les rayons Plantes / Fleurs / Accessoires pour ces filtres.")
else:
    order_rayons = ["Plantes", "Fleurs", "Accessoires"]
    agg = df_r3.groupby("rayon_norm", as_index=False).agg(
        ca_ttc=("ventes_ttc", "sum"),
        qte=("qte", "sum"),
    )
    agg["rayon_norm"] = pd.Categorical(agg["rayon_norm"], categories=order_rayons, ordered=True)
    agg = agg.sort_values("rayon_norm")

    c1, c2, c3 = st.columns(3, gap="large")

    # Remplit chaque colonne (si un rayon manque, on affiche 0)
    data_map = {r["rayon_norm"]: r for _, r in agg.iterrows()}
    cols_map = {"Plantes": c1, "Fleurs": c2, "Accessoires": c3}

    for rname in order_rayons:
        row = data_map.get(rname, {"ca_ttc": 0.0, "qte": 0.0})
        with cols_map[rname]:
            st.markdown(_kpi_rayon_card(rname, float(row["ca_ttc"]), float(row["qte"])), unsafe_allow_html=True)

st.divider()

# =============================================================================
# 1) Graph comparaison magasins (CA TTC)
# =============================================================================
st.markdown("### 📈 Comparaison des magasins — CA TTC")

df_plot = df.copy()
if "Tous les magasins" in (st.session_state.get("stores_selected") or []):
    df_plot["magasin"] = "Tous les magasins"
else:
    df_plot["magasin"] = df_plot["store_name"]

# Ajoute une clé de tri "period_order" (date/nombre) + un label "period" (affichage)
if granularity == "Jour":
    df_plot["period"] = df_plot["period_date"].dt.strftime("%Y-%m-%d")
    df_plot["period_order"] = df_plot["period_date"]  # datetime -> tri OK

elif granularity == "Semaine":
    df_plot["period"] = df_plot["iso_label"]
    df_plot["period_order"] = df_plot["iso_key"]      # tri OK (année + semaine)

else:  # Mois
    df_plot["period"] = df_plot["period_date"].dt.to_period("M").astype(str)
    df_plot["period_order"] = df_plot["period_date"].dt.to_period("M").dt.to_timestamp()    # datetime -> tri OK

# On garde period_order dans l'agg (min suffit car constant par période)
agg = (
    df_plot.groupby(["period", "magasin"], as_index=False)
    .agg(
        ventes_ttc=("ventes_ttc", "sum"),
        period_order=("period_order", "min"),
    )
)

chart = alt.Chart(agg).mark_line(point=True).encode(
    x=alt.X(
        "period:N",
        title=f"Période ({granularity})",
        sort=alt.SortField(field="period_order", order="ascending"),
    ),
    y=alt.Y("ventes_ttc:Q", title="CA TTC"),
    color=alt.Color("magasin:N", title="Magasin"),
    tooltip=["magasin", "period", alt.Tooltip("ventes_ttc:Q", format=".2f")]
).properties(height=320)

st.altair_chart(chart, use_container_width=True)

st.divider()

# =============================================================================
# 2) Camembert famille (CA TTC)
# =============================================================================
st.markdown("### 🔥 Répartition du CA TTC par famille")

stores_for_pie = ["Tous magasins"] + sorted(df["store_name"].dropna().unique().tolist())
pick_store = st.selectbox("Choisir le magasin pour le camembert", stores_for_pie, index=0)

df_pie = df.copy()
if pick_store != "Tous magasins":
    df_pie = df_pie[df_pie["store_name"] == pick_store]

pie = df_pie.groupby("famille_finale", as_index=False)["ventes_ttc"].sum()
pie = pie[pd.notna(pie["famille_finale"])]

if pie.empty:
    st.info("Pas de données famille sur ce filtre.")
else:
    pie["pct"] = pie["ventes_ttc"] / pie["ventes_ttc"].sum()
    pie_chart = alt.Chart(pie).mark_arc().encode(
        theta=alt.Theta("ventes_ttc:Q"),
        color=alt.Color("famille_finale:N", title="Famille"),
        tooltip=["famille_finale", alt.Tooltip("ventes_ttc:Q", format=".2f"), alt.Tooltip("pct:Q", format=".1%")]
    ).properties(height=320)
    st.altair_chart(pie_chart, use_container_width=True)

st.divider()

# =============================================================================
# 3) Top articles (CA TTC)
# =============================================================================
st.markdown("### 🏆 Top articles (par CA TTC)")
top_n = st.slider("Top N", 5, 50, 15)

top_art = df.groupby(["libelle_final"], as_index=False)["ventes_ttc"].sum()
top_art = top_art.sort_values("ventes_ttc", ascending=False).head(top_n)

bar = alt.Chart(top_art).mark_bar().encode(
    x=alt.X("ventes_ttc:Q", title="CA TTC"),
    y=alt.Y("libelle_final:N", sort="-x", title="Article"),
    tooltip=["libelle_final", alt.Tooltip("ventes_ttc:Q", format=".2f")]
).properties(height=420)

st.altair_chart(bar, use_container_width=True)

st.divider()

# =============================================================================
# 4) Synthèses semaine (3 tableaux)
# =============================================================================
st.markdown("## 📊 Synthèse Articles & CA TTC")

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
tickets_tbl["Moyenne"] = tickets_tbl[week_cols].mean(axis=1)

tot = {c: tickets_tbl[c].sum(numeric_only=True) for c in week_cols}
tot["Jour"] = "TOTAL"
tot["Moyenne"] = pd.Series(tickets_tbl[week_cols].sum(numeric_only=True)).mean()
tickets_tbl = pd.concat([tickets_tbl, pd.DataFrame([tot])], ignore_index=True)

render_heat_table(tickets_tbl, euro=False, title="🎟️ Synthèse des articles vendus (quantités) par semaine", dl_name="tickets")

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

# --- CA TTC
tmp = df.groupby(["jour", "iso_key"], as_index=False)["ventes_ttc"].sum()
pivot_ca = tmp.pivot(index="jour", columns="iso_key", values="ventes_ttc").reindex(JOURS)
pivot_ca = pivot_ca.reindex(columns=sorted(pivot_ca.columns, reverse=True))
pivot_ca.columns = [week_map.get(int(c), str(c)) for c in pivot_ca.columns]

ca_tbl = pivot_ca.copy()
ca_tbl.insert(0, "Jour", ca_tbl.index)
week_cols_ca = [c for c in ca_tbl.columns if c != "Jour"]
ca_tbl["Moyenne"] = ca_tbl[week_cols_ca].mean(axis=1)

tot = {c: ca_tbl[c].sum(numeric_only=True) for c in week_cols_ca}
tot["Jour"] = "TOTAL"
tot["Moyenne"] = pd.Series(ca_tbl[week_cols_ca].sum(numeric_only=True)).mean()
ca_tbl = pd.concat([ca_tbl, pd.DataFrame([tot])], ignore_index=True)

render_heat_table(ca_tbl, euro=True, title="💶 Synthèse CA TTC par semaine", dl_name="ca_ttc")

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
pm_tbl["Moyenne"] = pm_tbl[week_cols_pm].mean(axis=1)

tot = {c: pm_tbl[c].mean(numeric_only=True) for c in week_cols_pm}
tot["Jour"] = "TOTAL"
tot["Moyenne"] = pm_tbl[week_cols_pm].mean().mean()
pm_tbl = pd.concat([pm_tbl, pd.DataFrame([tot])], ignore_index=True)

render_heat_table(pm_tbl, euro=True, title="🛒 Synthèse Prix moyen d'article par semaine", dl_name="panier_moyen")

# =============================================================================
# 5) Graphiques — 3 dernières semaines + Moyenne
# =============================================================================
st.divider()
st.markdown("## 📉 Graphiques — 3 dernières semaines + Moyenne")

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

    st.markdown("### 📈 Évolution des Articles (qte) — 3 dernières semaines + Moyenne")
    ch1 = alt.Chart(plot_df).mark_line(point=True).encode(
        x=alt.X("jour:N", sort=JOURS, title="Jour de la semaine"),
        y=alt.Y("qte:Q", title="Articles vendus (qte)"),
        color=alt.Color("semaine:N", title="Semaine", sort=ORDER_DOMAIN),
        strokeDash=alt.condition(alt.datum.semaine == MOY_LABEL, alt.value([5, 5]), alt.value([1, 0])),
        tooltip=["semaine", "jour", alt.Tooltip("qte:Q", format=".0f")]
    ).properties(height=320)
    st.altair_chart(ch1, use_container_width=True)

    st.markdown("### 📈 Évolution du CA TTC — 3 dernières semaines + Moyenne")
    ch2 = alt.Chart(plot_df).mark_line(point=True).encode(
        x=alt.X("jour:N", sort=JOURS, title="Jour de la semaine"),
        y=alt.Y("ca:Q", title="CA TTC"),
        color=alt.Color("semaine:N", title="Semaine", sort=ORDER_DOMAIN),
        strokeDash=alt.condition(alt.datum.semaine == MOY_LABEL, alt.value([5, 5]), alt.value([1, 0])),
        tooltip=["semaine", "jour", alt.Tooltip("ca:Q", format=".2f")]
    ).properties(height=320)
    st.altair_chart(ch2, use_container_width=True)

    st.markdown("### 📈 Évolution du Prix moyen d'article — 3 dernières semaines + Moyenne")
    ch3 = alt.Chart(plot_df).mark_line(point=True).encode(
        x=alt.X("jour:N", sort=JOURS, title="Jour de la semaine"),
        y=alt.Y("prix_moy:Q", title="Prix moyen d'article (€)"),
        color=alt.Color("semaine:N", title="Semaine", sort=ORDER_DOMAIN),
        strokeDash=alt.condition(alt.datum.semaine == MOY_LABEL, alt.value([5, 5]), alt.value([1, 0])),
        tooltip=["semaine", "jour", alt.Tooltip("prix_moy:Q", format=".2f")]
    ).properties(height=320)
    st.altair_chart(ch3, use_container_width=True)

# =============================================================================
# 6) Détail lignes
# =============================================================================
st.divider()
st.markdown("### 🧾 Détail des lignes (période sélectionnée)")

show_cols = [
    "store_name", "period_date", "code_article", "libelle_final", "famille_finale",
    "qte", "ventes_ht", "ventes_ttc", "marge_ht", "marge_pct",
    "iso_year", "iso_week", "iso_key", "iso_label"
]
present = [c for c in show_cols if c in df.columns]
st.dataframe(
    df[present].sort_values(["period_date", "store_name"]).head(5000),
    use_container_width=True
)
