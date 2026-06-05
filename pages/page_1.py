# pages/page_1.py
import io
import re
import pandas as pd
import altair as alt
import streamlit as st
from datetime import date, timedelta

from src.supabase_client import get_supabase
from src.auth import require_auth
from src.ui import top_bar, tabs_nav
from src.utils import inject_base_css

st.set_page_config(page_title="N vs N-1", layout="wide")
require_auth()
top_bar("Comparaison N vs N-1")
tabs_nav(active="nvsn1")
st.divider()

# =============================================================================
# CSS
# =============================================================================
def inject_page_css():
    inject_base_css()
    st.markdown(
        """
<style>
.table-wrap{
  width:100%;overflow:auto;
  border:1px solid var(--emova-light);
  border-radius:12px;background:var(--emova-white);
}
.table-wrap table{
  border-collapse:separate;border-spacing:0;
  width:max-content;min-width:100%;font-size:12px;
}
.table-wrap thead th{
  position:sticky;top:0;z-index:5;
  background:var(--emova-green);color:var(--emova-white);
  padding:10px 12px;font-weight:900;
  border-right:1px solid rgba(255,255,255,0.18);
  white-space:nowrap;text-align:center;
}
.table-wrap td{
  background:var(--emova-white);
  border-bottom:1px solid #eef2f7;border-right:1px solid #eef2f7;
  padding:8px 10px;text-align:center;
  color:var(--emova-dark);white-space:nowrap;height:40px;
}
.table-wrap th.sticky-left,
.table-wrap td.sticky-left{
  position:sticky;left:0;z-index:6;
  background:var(--emova-soft) !important;font-weight:900;
  border-right:2px solid var(--emova-light) !important;
  color:var(--emova-dark) !important;text-align:center !important;
}
.tr-week td{
  background:#f0f6f3 !important;font-weight:900 !important;
  border-top:2px solid var(--emova-green) !important;
  font-size:12px;
}
.tr-week td.sticky-left{
  background:#e2f0ea !important;color:var(--emova-green) !important;
}
.tr-total td{
  background:#e8f4ef !important;font-weight:900 !important;
  border-top:2px solid var(--emova-green) !important;
}
.cell-up   { color:#155724 !important;font-weight:900; }
.cell-down { color:#721c24 !important;font-weight:900; }
.pill{
  display:inline-flex;align-items:center;justify-content:center;
  gap:4px;padding:3px 8px;border-radius:8px;
  font-weight:900;font-size:11px;
}
.pill-up   { background:rgba(46,204,113,.18); }
.pill-down { background:rgba(231,76,60,.18); }
.pill-flat { background:rgba(127,127,127,.10); }
.sep-col{ border-left:2px solid var(--emova-green) !important; }
.kpi-card{
  border-radius:14px;padding:14px 16px;
  margin:4px 0 8px 0;
  display:flex;flex-direction:column;gap:6px;
  box-shadow:0 2px 8px rgba(88,88,87,0.08);
}
.kpi-card-up  { background:#e8f5e9;border:1.5px solid #a5d6a7; }
.kpi-card-down{ background:#fce4ec;border:1.5px solid #f48fb1; }
.kpi-card-flat{ background:#f5f5f5;border:1.5px solid #e0e0e0; }
.kpi-title{ font-size:12px;font-weight:800;color:#444;margin-bottom:2px; }
.kpi-row-n{
  display:flex;align-items:center;justify-content:space-between;gap:8px;
}
.kpi-label-n{ font-size:11px;font-weight:700;color:#555; }
.kpi-value-n{ font-size:20px;font-weight:900;color:#1a1a1a; }
.kpi-pill{
  min-width:64px;padding:6px 10px;border-radius:50px;
  font-size:12px;font-weight:900;text-align:center;
  display:flex;align-items:center;justify-content:center;gap:3px;
  flex-shrink:0;
}
.kpi-pill-up  { background:#2e7d32;color:#fff; }
.kpi-pill-down{ background:#c62828;color:#fff; }
.kpi-pill-flat{ background:#757575;color:#fff; }
.kpi-row-n1{ font-size:11px;color:#777;font-weight:600; }

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
  color:var(--emova-dark);font-weight:900;font-size:14px;
  margin-bottom:12px;text-align:center;
}
.rayon-center{
  display:flex;flex-direction:column;
  align-items:center;justify-content:center;
  text-align:center;width:100%;margin-bottom:14px;
}
.rayon-sub{
  font-size:11px;color:var(--emova-dark);margin-bottom:6px;
  font-weight:700;text-transform:uppercase;letter-spacing:.4px;
}
.rayon-main-value{
  font-size:26px;font-weight:900;color:var(--emova-green);line-height:1.2;
}
.rayon-n1-sub{ font-size:11px;color:#888;margin-top:3px; }
.rayon-grid{ display:flex;gap:12px;margin-top:10px; }
.rayon-mini{
  flex:1;background:#f8f8f8;
  border:1px solid var(--emova-light);
  border-radius:10px;padding:10px;text-align:center;
}
.rayon-mini-label{ font-size:11px;color:var(--emova-dark);font-weight:700;margin-bottom:6px; }
.rayon-mini-value{ font-size:20px;font-weight:900;color:var(--emova-green); }
.rayon-mini-n1{ font-size:10px;color:#888;margin-top:2px; }
</style>
        """,
        unsafe_allow_html=True,
    )

inject_page_css()

# =============================================================================
# Helpers
# =============================================================================
JOURS_ABR = {0: "L.", 1: "M.", 2: "M.", 3: "J.", 4: "V.", 5: "S.", 6: "D."}


def _strip_emoji(text: str) -> str:
    return re.sub(r"[^\x00-\x7FÀ-ɏ\s]", "", str(text)).strip()


def _df_to_pdf(df: pd.DataFrame, title: str) -> bytes:
    from fpdf import FPDF
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=12)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 9, _strip_emoji(title), ln=True, align="C")
    pdf.ln(3)

    cols = list(df.columns)
    page_w = pdf.w - 2 * pdf.l_margin
    col_w  = page_w / len(cols)

    pdf.set_font("Helvetica", "B", 7)
    pdf.set_fill_color(46, 125, 50)
    pdf.set_text_color(255, 255, 255)
    for c in cols:
        pdf.cell(col_w, 7, _strip_emoji(c)[:22], border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 6)
    pdf.set_text_color(0, 0, 0)
    for i, (_, row) in enumerate(df.iterrows()):
        if i % 2 == 0:
            pdf.set_fill_color(240, 248, 240)
        else:
            pdf.set_fill_color(255, 255, 255)
        for c in cols:
            pdf.cell(col_w, 6, _strip_emoji(str(row[c]))[:22], border=1, fill=True, align="C")
        pdf.ln()

    return bytes(pdf.output())


def export_buttons(df: pd.DataFrame, prefix: str):
    c1, c2, c3 = st.columns(3)
    with c1:
        buf = io.BytesIO()
        df.to_excel(buf, index=False, engine="openpyxl")
        st.download_button(
            "📊 Télécharger Excel", buf.getvalue(),
            f"{prefix}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True, key=f"xls_{prefix}",
        )
    with c2:
        st.download_button(
            "📥 Télécharger CSV",
            df.to_csv(index=False, sep=";", encoding="utf-8-sig"),
            f"{prefix}.csv", "text/csv",
            use_container_width=True, key=f"csv_{prefix}",
        )
    with c3:
        try:
            pdf_bytes = _df_to_pdf(df, prefix.replace("_", " ").title())
            st.download_button(
                "📄 Télécharger PDF", pdf_bytes,
                f"{prefix}.pdf", "application/pdf",
                use_container_width=True, key=f"pdf_{prefix}",
            )
        except Exception:
            st.button("📄 PDF (fpdf2 manquant)", disabled=True,
                      use_container_width=True, key=f"pdf_dis_{prefix}")


def fmt_eur(x):
    if x is None or pd.isna(x):
        return "—"
    return f"{x:,.0f} €".replace(",", " ")


def fmt_qte(x):
    if x is None or pd.isna(x):
        return "—"
    return f"{int(round(x)):,}".replace(",", " ")


def fmt_pct_val(x):
    if x is None or pd.isna(x):
        return "—"
    return f"{x:.1f} %"


def evol_pill(n_val, n1_val):
    if n_val is None or n1_val is None or pd.isna(n_val) or pd.isna(n1_val) or n1_val == 0:
        return '<span class="pill pill-flat">—</span>'
    pct = (n_val - n1_val) / abs(n1_val) * 100
    if pct > 0:
        return f'<span class="pill pill-up">▲ +{pct:.1f}&nbsp;%</span>'
    elif pct < 0:
        return f'<span class="pill pill-down">▼ {pct:.1f}&nbsp;%</span>'
    return f'<span class="pill pill-flat">= 0,0&nbsp;%</span>'


def safe_pct(n_val, n1_val):
    if n_val is None or n1_val is None or pd.isna(n_val) or pd.isna(n1_val) or n1_val == 0:
        return None
    return (n_val - n1_val) / abs(n1_val) * 100


# =============================================================================
# Load filters
# =============================================================================
@st.cache_data(ttl=300, show_spinner="⏳ Chargement des filtres...")
def load_filters():
    supabase = get_supabase()
    r1 = supabase.table("v_matrix").select("period_date").order("period_date", desc=False).limit(1).execute()
    r2 = supabase.table("v_matrix").select("period_date").order("period_date", desc=True).limit(1).execute()

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

    dmin = pd.to_datetime(r1.data[0]["period_date"]).date() if r1.data else date.today()
    dmax = pd.to_datetime(r2.data[0]["period_date"]).date() if r2.data else date.today()
    stores = sorted({row["store_name"] for row in all_stores if row.get("store_name")})
    return dmin, dmax, stores


dmin, dmax, stores = load_filters()

# =============================================================================
# Load data
# =============================================================================
@st.cache_data(ttl=300, show_spinner="⏳ Chargement des données N vs N-1...")
def load_period(dstart: date, dend: date, store_names: list[str]) -> pd.DataFrame:
    supabase = get_supabase()
    cols = "store_name,period_date,code_article,libelle_final,famille_finale,rayon,pvc,qte,ventes_ht,ventes_ttc,marge_ht,marge_pct"
    batch_size = 1000
    offset = 0
    all_data = []
    while True:
        query = (
            supabase.table("v_matrix")
            .select(cols)
            .gte("period_date", dstart.isoformat())
            .lte("period_date", dend.isoformat())
            .order("period_date",  desc=False)
            .order("store_name",   desc=False)
            .order("code_article", desc=False)
        )
        if store_names and "Tous les magasins" not in store_names:
            query = query.in_("store_name", store_names)
        res = query.range(offset, offset + batch_size - 1).execute()
        if not res.data:
            break
        all_data.extend(res.data)
        if len(res.data) < batch_size:
            break
        offset += batch_size

    df = pd.DataFrame(all_data or [])
    if df.empty:
        return df
    df = df.drop_duplicates(subset=["store_name", "period_date", "code_article", "libelle_final"], keep="first")
    df["period_date"] = pd.to_datetime(df["period_date"])
    for c in ["qte", "ventes_ht", "ventes_ttc", "marge_ht", "marge_pct", "pvc"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df["commission"] = df["ventes_ht"] * 0.20

    iso = df["period_date"].dt.isocalendar()
    df["iso_year"]       = iso.year.astype(int)
    df["iso_week"]       = iso.week.astype(int)
    df["iso_month"]      = df["period_date"].dt.month.astype(int)
    df["iso_month_label"]= df["period_date"].dt.strftime("%Y-%m")
    df["iso_label"]      = "S" + df["iso_week"].astype(str).str.zfill(2) + "-" + df["iso_year"].astype(str)
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def load_magasins_mapping() -> dict:
    supabase = get_supabase()
    res = supabase.table("magasins").select("store_name_pdf,nom_ville").execute()
    return {r["store_name_pdf"]: r.get("nom_ville") for r in (res.data or []) if r.get("store_name_pdf")}


@st.cache_data(ttl=300, show_spinner="⏳ Chargement budget vs CA...")
def load_budget_summary(dstart: date, dend: date, nom_villes: tuple) -> pd.DataFrame:
    supabase = get_supabase()
    cols = "jour,code_magasin,nom_ville,ca_ttc,ca_ht,qte,marge_ht,budget_ca,budget_qte_article,pct_budget_ca,ca_ttc_n1,ca_ht_n1,qte_n1,marge_ht_n1"
    batch_size = 1000
    offset = 0
    all_data = []
    while True:
        q = (supabase.table("v_budget_vs_ca_jour")
             .select(cols)
             .gte("jour", dstart.isoformat())
             .lte("jour", dend.isoformat())
             .order("jour", desc=False))
        if nom_villes:
            q = q.in_("nom_ville", list(nom_villes))
        res = q.range(offset, offset + batch_size - 1).execute()
        if not res.data:
            break
        all_data.extend(res.data)
        if len(res.data) < batch_size:
            break
        offset += batch_size
    df = pd.DataFrame(all_data or [])
    if df.empty:
        return df
    df["jour"] = pd.to_datetime(df["jour"])
    for c in ["ca_ttc","ca_ht","qte","marge_ht","budget_ca","budget_qte_article","pct_budget_ca","ca_ttc_n1","ca_ht_n1","qte_n1","marge_ht_n1"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


# =============================================================================
# UI — Filtres
# =============================================================================
st.markdown("## 📈 Comparaison N vs N-1 · Budget")

# ── Mode toggle ──────────────────────────────────────────────────────────────
if "nvsn1_mode" not in st.session_state:
    st.session_state["nvsn1_mode"] = "nvsn1"

_m1, _m2, _m3 = st.columns([2, 2, 5])
with _m1:
    if st.button("📈 N vs N-1", key="mode_nvsn1_btn", use_container_width=True,
                 type="primary" if st.session_state["nvsn1_mode"] == "nvsn1" else "secondary"):
        st.session_state["nvsn1_mode"] = "nvsn1"
with _m2:
    if st.button("💰 Budget", key="mode_budget_btn", use_container_width=True,
                 type="primary" if st.session_state["nvsn1_mode"] == "budget" else "secondary"):
        st.session_state["nvsn1_mode"] = "budget"

_mode = st.session_state["nvsn1_mode"]

# ── Filtres ───────────────────────────────────────────────────────────────────
col_f1, col_f2, col_f3 = st.columns([3, 2, 4])
with col_f1:
    st.markdown("**📅 Période N**")
    _default_start = max(date(2026, 5, 12), dmin)
    drange = st.date_input(
        "",
        value=(_default_start, dmax),
        min_value=dmin,
        max_value=dmax,
        label_visibility="collapsed",
        key="drange_nvsn1",
    )
with col_f2:
    st.markdown("**⏱️ Granularité**")
    if "gran_nvsn1" not in st.session_state:
        st.session_state["gran_nvsn1"] = "Jour"
    g1, g2, g3 = st.columns(3)
    with g1:
        if st.button("Jour",    key="gran_j", use_container_width=True,
                     type="primary" if st.session_state["gran_nvsn1"] == "Jour"    else "secondary"):
            st.session_state["gran_nvsn1"] = "Jour"
    with g2:
        if st.button("Semaine", key="gran_s", use_container_width=True,
                     type="primary" if st.session_state["gran_nvsn1"] == "Semaine" else "secondary"):
            st.session_state["gran_nvsn1"] = "Semaine"
    with g3:
        if st.button("Mois",    key="gran_m", use_container_width=True,
                     type="primary" if st.session_state["gran_nvsn1"] == "Mois"    else "secondary"):
            st.session_state["gran_nvsn1"] = "Mois"
with col_f3:
    st.markdown("**🏬 Magasins**")
    store_options = ["Tous les magasins"] + stores
    selected_stores = st.multiselect(
        "",
        store_options,
        default=["Tous les magasins"],
        label_visibility="collapsed",
        key="stores_nvsn1",
    )

if isinstance(drange, tuple) and len(drange) == 2:
    dstart_n, dend_n = drange
else:
    dstart_n = dend_n = drange

dstart_n1 = dstart_n - timedelta(days=364)
dend_n1   = dend_n   - timedelta(days=364)

st.caption(
    f"N : **{dstart_n.strftime('%d/%m/%Y')}** → **{dend_n.strftime('%d/%m/%Y')}** "
    f"| N-1 : **{dstart_n1.strftime('%d/%m/%Y')}** → **{dend_n1.strftime('%d/%m/%Y')}**"
)

# ── Bouton chargement ─────────────────────────────────────────────────────────
if st.button("⚡ Charger / Actualiser", key="btn_nvsn1", type="primary", use_container_width=True):
    _mapping = load_magasins_mapping()
    if selected_stores and "Tous les magasins" not in selected_stores:
        _nom_villes = tuple(v for s in selected_stores if (v := _mapping.get(s)))
    else:
        _nom_villes = ()

    with st.spinner("⏳ Budget en cours..."):
        st.session_state["nvsn1_dfbudget"] = load_budget_summary(dstart_n, dend_n, _nom_villes)

    if _mode == "nvsn1":
        with st.spinner("⏳ Chargement N vs N-1..."):
            st.session_state["nvsn1_dfn"]  = load_period(dstart_n,  dend_n,  selected_stores)
            st.session_state["nvsn1_dfn1"] = load_period(dstart_n1, dend_n1, selected_stores)
    else:
        # Budget mode : v_matrix chargé en arrière-plan pour les onglets détail
        if st.session_state.get("nvsn1_dfn") is None:
            st.session_state["nvsn1_dfn"]  = pd.DataFrame()
            st.session_state["nvsn1_dfn1"] = pd.DataFrame()

    st.session_state["nvsn1_dstart"] = dstart_n
    st.session_state["nvsn1_dend"]   = dend_n

df_n      = st.session_state.get("nvsn1_dfn")
df_n1     = st.session_state.get("nvsn1_dfn1")
df_budget = st.session_state.get("nvsn1_dfbudget")

if df_budget is None and (df_n is None or df_n1 is None):
    st.info("Sélectionne la période et clique sur ⚡ Charger / Actualiser.")
    st.stop()

# Initialise les df manquants pour éviter les erreurs
if df_n     is None: df_n     = pd.DataFrame()
if df_n1    is None: df_n1    = pd.DataFrame()
if df_budget is None: df_budget = pd.DataFrame()

if _mode == "nvsn1" and df_n.empty and df_n1.empty:
    st.warning("Aucune donnée N vs N-1 pour cette sélection.")
    st.stop()
if _mode == "budget" and df_budget.empty:
    st.warning("Aucune donnée budget pour cette sélection.")
    st.stop()


# =============================================================================
# KPIs globaux
# =============================================================================
def tot(df, col):
    return df[col].sum() if not df.empty else 0

def commission_pct_tot(df):
    return 20.0

def prix_unitaire(df):
    ttc = df["ventes_ttc"].sum()
    qte = df["qte"].sum()
    return ttc / qte if qte else 0

def fmt_kpi(v, fmt):
    if fmt == "eur":      return fmt_eur(v)
    if fmt == "qte":      return fmt_qte(v)
    if fmt == "pct":      return f"{v:.2f} %"
    if fmt == "eur_unit": return f"{v:.2f} €"
    return str(v)

year_n_label  = st.session_state.get("nvsn1_dstart", dstart_n).year
year_n1_label = year_n_label - 1

def kpi_card(label, vn, vn1, fmt):
    pct    = safe_pct(vn, vn1)
    vn_str  = fmt_kpi(vn,  fmt)
    vn1_str = fmt_kpi(vn1, fmt)
    if pct is None:
        card_cls, pill_cls, arrow, pct_str = "kpi-card-flat", "kpi-pill-flat", "=", "—"
    elif pct >= 0:
        card_cls, pill_cls, arrow, pct_str = "kpi-card-up",   "kpi-pill-up",   "↑", f"+{pct:.1f}%"
    else:
        card_cls, pill_cls, arrow, pct_str = "kpi-card-down", "kpi-pill-down", "↓", f"{pct:.1f}%"
    st.markdown(
        f"""
        <div class="kpi-card {card_cls}">
          <div class="kpi-title">{label}</div>
          <div class="kpi-row-n">
            <div>
              <div class="kpi-label-n">{year_n_label}</div>
              <div class="kpi-value-n">{vn_str}</div>
            </div>
            <div class="kpi-pill {pill_cls}">{arrow} {pct_str}</div>
          </div>
          <div class="kpi-row-n1">{year_n1_label} &nbsp; {vn1_str}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def kpi_card_budget(label, valeur, budget, fmt):
    pct = (valeur / budget * 100) if budget else None
    val_str = fmt_kpi(valeur, fmt)
    bud_str = fmt_kpi(budget, fmt)
    if pct is None:
        card_cls, pill_cls, pct_str = "kpi-card-flat", "kpi-pill-flat", "—"
    elif pct >= 100:
        card_cls, pill_cls, pct_str = "kpi-card-up",   "kpi-pill-up",   f"{pct:.1f}%"
    elif pct >= 80:
        card_cls, pill_cls, pct_str = "kpi-card-flat", "kpi-pill-flat", f"{pct:.1f}%"
    else:
        card_cls, pill_cls, pct_str = "kpi-card-down", "kpi-pill-down", f"{pct:.1f}%"
    st.markdown(
        f"""
        <div class="kpi-card {card_cls}">
          <div class="kpi-title">{label}</div>
          <div class="kpi-row-n">
            <div>
              <div class="kpi-label-n">Réalisé</div>
              <div class="kpi-value-n">{val_str}</div>
            </div>
            <div class="kpi-pill {pill_cls}">{pct_str}</div>
          </div>
          <div class="kpi-row-n1">Budget &nbsp; {bud_str}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("### 📊 KPIs Globaux — N vs N-1" if _mode == "nvsn1" else "### 📊 KPIs Globaux — Budget")

if _mode == "nvsn1":
    # Ligne 1 : CA TTC | Quantités | Prix unit. moy.
    row1 = st.columns(3)
    with row1[0]: kpi_card("💰 CA TTC",           tot(df_n, "ventes_ttc"), tot(df_n1, "ventes_ttc"), "eur")
    with row1[1]: kpi_card("🧾 Quantités",         tot(df_n, "qte"),        tot(df_n1, "qte"),        "qte")
    with row1[2]: kpi_card("🏷️ Prix unit. moy.",  prix_unitaire(df_n),     prix_unitaire(df_n1),     "eur_unit")

    # Ligne 2 : CA HT | Commission Carrefour | Taux commission
    row2 = st.columns(3)
    with row2[0]: kpi_card("📊 CA HT",                tot(df_n, "ventes_ht"),   tot(df_n1, "ventes_ht"),   "eur")
    with row2[1]: kpi_card("🏦 Commission Carrefour", tot(df_n, "commission"),  tot(df_n1, "commission"),  "eur")
    with row2[2]: kpi_card("🔥 Taux commission",       commission_pct_tot(df_n), commission_pct_tot(df_n1), "pct")
else:
    _bca  = df_budget["budget_ca"].sum()  if not df_budget.empty else 0
    _bqte = df_budget["budget_qte_article"].sum() if not df_budget.empty else 0
    _rca  = df_budget["ca_ttc"].sum()    if not df_budget.empty else 0
    _rht  = df_budget["ca_ht"].sum()     if not df_budget.empty else 0
    _rqte = df_budget["qte"].sum()       if not df_budget.empty else 0
    _rmarge = df_budget["marge_ht"].sum() if not df_budget.empty else 0
    row1 = st.columns(3)
    with row1[0]: kpi_card_budget("💰 CA TTC vs Budget",  _rca,   _bca,  "eur")
    with row1[1]: kpi_card_budget("🧾 Quantités vs Budget", _rqte, _bqte, "qte")
    with row1[2]: kpi_card("📊 CA HT", _rht, df_budget["ca_ht_n1"].sum() if not df_budget.empty else 0, "eur")

st.divider()

# =============================================================================
# KPIs par Rayon (Plantes / Fleurs / Accessoires) N vs N-1
# =============================================================================
if _mode == "nvsn1":
    st.markdown("### 🌿 KPIs par Rayon — N vs N-1")

_RAYON_KEYS = {
    "🌱 Plantes":     ["plante", "plantes", "plantes fleuries", "plantes vertes", "succulentes", "cactus"],
    "💐 Fleurs":      ["fleur", "fleurs", "bouquet", "bouquets", "bottes", "compositions", "rose"],
    "🪴 Accessoires": ["accessoire", "accessoires", "cache", "cache-pot", "vase", "emballage", "bougie", "terreau"],
}

def _classify_rayon(r):
    if pd.isna(r):
        return None
    r_low = str(r).strip().lower()
    for label, keys in _RAYON_KEYS.items():
        if any(k in r_low for k in keys):
            return label
    return None

def _agg_rayon(df):
    if df.empty:
        return {}
    d = df.copy()
    d["_cat"] = d["rayon"].apply(_classify_rayon)
    d = d.dropna(subset=["_cat"])
    out = {}
    for cat, grp in d.groupby("_cat"):
        ttc = grp["ventes_ttc"].sum()
        qte = grp["qte"].sum()
        out[cat] = {"ttc": ttc, "qte": qte, "prix": ttc / qte if qte else 0}
    return out

def render_rayon_nvsn1_card(title, vn, vn1):
    ttc_n   = vn.get("ttc",  0)
    ttc_n1  = vn1.get("ttc", 0)
    qte_n   = vn.get("qte",  0)
    qte_n1  = vn1.get("qte", 0)
    prix_n  = vn.get("prix", 0)
    prix_n1 = vn1.get("prix",0)

    def mini_pill(n_val, n1_val):
        if n1_val == 0:
            return '<span class="pill pill-flat" style="font-size:10px;padding:2px 6px;">—</span>'
        pct = (n_val - n1_val) / abs(n1_val) * 100
        if pct > 0:
            return f'<span class="pill pill-up" style="font-size:10px;padding:2px 6px;">▲ +{pct:.1f}%</span>'
        elif pct < 0:
            return f'<span class="pill pill-down" style="font-size:10px;padding:2px 6px;">▼ {pct:.1f}%</span>'
        return '<span class="pill pill-flat" style="font-size:10px;padding:2px 6px;">= 0,0%</span>'

    html = f"""
    <div class="rayon-card">
      <div class="rayon-title">{title}</div>
      <div class="rayon-center">
        <div class="rayon-sub">CA TTC</div>
        <div style="display:flex;align-items:center;gap:10px;justify-content:center;">
          <div class="rayon-main-value">{fmt_eur(ttc_n)}</div>
          {mini_pill(ttc_n, ttc_n1)}
        </div>
        <div class="rayon-n1-sub">N-1 : {fmt_eur(ttc_n1)}</div>
      </div>
      <div class="rayon-grid">
        <div class="rayon-mini">
          <div class="rayon-mini-label">🧾 Qté</div>
          <div class="rayon-mini-value">{fmt_qte(qte_n)}</div>
          <div class="rayon-mini-n1">N-1 : {fmt_qte(qte_n1)}</div>
          {mini_pill(qte_n, qte_n1)}
        </div>
        <div class="rayon-mini">
          <div class="rayon-mini-label">📦 Prix moy.</div>
          <div class="rayon-mini-value">{fmt_kpi(prix_n, "eur_unit")}</div>
          <div class="rayon-mini-n1">N-1 : {fmt_kpi(prix_n1, "eur_unit")}</div>
          {mini_pill(prix_n, prix_n1)}
        </div>
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

if _mode == "nvsn1":
    _rayon_n  = _agg_rayon(df_n)
    _rayon_n1 = _agg_rayon(df_n1)
    _rayon_order = ["🌱 Plantes", "💐 Fleurs", "🪴 Accessoires"]
    _rcols = st.columns(3)
    for _i, _rl in enumerate(_rayon_order):
        with _rcols[_i]:
            render_rayon_nvsn1_card(
                _rl,
                _rayon_n.get(_rl,  {"ttc": 0, "qte": 0, "prix": 0}),
                _rayon_n1.get(_rl, {"ttc": 0, "qte": 0, "prix": 0}),
            )
    st.divider()

# =============================================================================
# Graphique CA TTC
# =============================================================================
_gran_chart = st.session_state.get("gran_nvsn1", "Jour")
MOIS_ABR = {1:"Jan",2:"Fév",3:"Mar",4:"Avr",5:"Mai",6:"Jun",
            7:"Jul",8:"Aoû",9:"Sep",10:"Oct",11:"Nov",12:"Déc"}

if _mode == "nvsn1":
    st.markdown("### 📈 Évolution CA TTC — N vs N-1")

    def build_chart_data(dfn, dfn1, granularity, yn_label, yn1_label):
        if granularity == "Jour":
            def agg_jour(df):
                if df.empty:
                    return pd.DataFrame(columns=["period_date","ca_ttc"])
                return df.groupby("period_date", as_index=False).agg(ca_ttc=("ventes_ttc","sum"))
            dn  = agg_jour(dfn)
            dn1 = agg_jour(dfn1)
            dn["label"]  = dn["period_date"].dt.strftime("%d/%m")
            dn["order"]  = dn["period_date"].apply(lambda d: d.toordinal())
            dn["serie"]  = f"N ({yn_label})"
            shifted = dn1["period_date"] + timedelta(days=364)
            dn1["label"] = shifted.dt.strftime("%d/%m")
            dn1["order"] = shifted.apply(lambda d: d.toordinal())
            dn1["serie"] = f"N-1 ({yn1_label})"
        elif granularity == "Semaine":
            def agg_sem(df, serie):
                if df.empty:
                    return pd.DataFrame(columns=["label","order","ca_ttc","serie"])
                d = df.copy()
                d["iso_week"] = d["period_date"].dt.isocalendar().week.astype(int)
                agg = d.groupby("iso_week", as_index=False).agg(ca_ttc=("ventes_ttc","sum"))
                agg["label"] = "S" + agg["iso_week"].astype(str).str.zfill(2)
                agg["order"] = agg["iso_week"]
                agg["serie"] = serie
                return agg[["label","order","ca_ttc","serie"]]
            dn  = agg_sem(dfn,  f"N ({yn_label})")
            dn1 = agg_sem(dfn1, f"N-1 ({yn1_label})")
        else:
            def agg_mois(df, serie):
                if df.empty:
                    return pd.DataFrame(columns=["label","order","ca_ttc","serie"])
                d = df.copy()
                d["month"] = d["period_date"].dt.month.astype(int)
                agg = d.groupby("month", as_index=False).agg(ca_ttc=("ventes_ttc","sum"))
                agg["label"] = agg["month"].map(MOIS_ABR)
                agg["order"] = agg["month"]
                agg["serie"] = serie
                return agg[["label","order","ca_ttc","serie"]]
            dn  = agg_mois(dfn,  f"N ({yn_label})")
            dn1 = agg_mois(dfn1, f"N-1 ({yn1_label})")
        return pd.concat(
            [dn[["label","order","ca_ttc","serie"]], dn1[["label","order","ca_ttc","serie"]]],
            ignore_index=True,
        )

    chart_df = build_chart_data(df_n, df_n1, _gran_chart, year_n_label, year_n1_label)
    _serie_n  = f"N ({year_n_label})"
    _serie_n1 = f"N-1 ({year_n1_label})"
    _domain   = [_serie_n, _serie_n1]
    _range_c  = ["#95d1bd", "#585857"]

else:
    st.markdown("### 📈 Évolution CA TTC — Réalisé vs Budget")

    def _agg_budget_chart(df, gran):
        if df.empty:
            return pd.DataFrame(columns=["label","order","ca_ttc","serie"])
        d = df.copy()
        if gran == "Jour":
            d["label"] = d["jour"].dt.strftime("%d/%m")
            d["order"] = d["jour"].apply(lambda x: x.toordinal())
            agg_r = d.groupby(["label","order"], as_index=False).agg(ca=("ca_ttc","sum"))
            agg_b = d.groupby(["label","order"], as_index=False).agg(ca=("budget_ca","sum"))
        elif gran == "Semaine":
            d["wk"]    = d["jour"].dt.isocalendar().week.astype(int)
            d["label"] = "S" + d["wk"].astype(str).str.zfill(2)
            d["order"] = d["wk"]
            agg_r = d.groupby(["label","order"], as_index=False).agg(ca=("ca_ttc","sum"))
            agg_b = d.groupby(["label","order"], as_index=False).agg(ca=("budget_ca","sum"))
        else:
            d["mo"]    = d["jour"].dt.month.astype(int)
            d["label"] = d["mo"].map(MOIS_ABR)
            d["order"] = d["mo"]
            agg_r = d.groupby(["label","order"], as_index=False).agg(ca=("ca_ttc","sum"))
            agg_b = d.groupby(["label","order"], as_index=False).agg(ca=("budget_ca","sum"))
        agg_r["serie"] = "Réalisé"
        agg_b["serie"] = "Budget"
        out = pd.concat([agg_r, agg_b], ignore_index=True)
        out.rename(columns={"ca": "ca_ttc"}, inplace=True)
        return out

    chart_df  = _agg_budget_chart(df_budget, _gran_chart)
    _serie_n  = "Réalisé"
    _serie_n1 = "Budget"
    _domain   = ["Réalisé", "Budget"]
    _range_c  = ["#95d1bd", "#f5a623"]

if not chart_df.empty:
    _chart_type = st.radio(
        "Type de graphique",
        ["📈 Courbes", "📊 Histogramme"],
        horizontal=True,
        key="chart_type_cattc",
        label_visibility="collapsed",
    )
    _color = alt.Color("serie:N", title="Série",
                       scale=alt.Scale(domain=_domain, range=_range_c))
    _x = alt.X("label:N", title=f"Période ({_gran_chart})",
               sort=alt.SortField(field="order", order="ascending"))
    _y = alt.Y("ca_ttc:Q", title="CA TTC (€)")
    _tooltip = [
        alt.Tooltip("serie:N",  title="Série"),
        alt.Tooltip("label:N",  title="Période"),
        alt.Tooltip("ca_ttc:Q", title="CA TTC (€)", format=",.0f"),
    ]
    if _chart_type == "📈 Courbes":
        _chart = (alt.Chart(chart_df).mark_line(point=True)
                  .encode(x=_x, y=_y, color=_color, tooltip=_tooltip)
                  .properties(height=320))
    else:
        _chart = (alt.Chart(chart_df)
                  .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
                  .encode(x=_x, xOffset=alt.XOffset("serie:N", sort=_domain),
                          y=_y, color=_color, tooltip=_tooltip)
                  .properties(height=320))
    st.altair_chart(_chart, use_container_width=True)

st.divider()

# =============================================================================
# Histogramme groupé — CA TTC par Famille (N vs N-1 uniquement)
# =============================================================================
if _mode == "nvsn1":
    st.markdown("### 📊 CA TTC par Famille — N vs N-1")

    def _agg_famille(df, serie):
        if df.empty:
            return pd.DataFrame(columns=["famille_finale", "ca_ttc", "serie"])
        agg = (df.dropna(subset=["famille_finale"])
               .groupby("famille_finale", as_index=False)
               .agg(ca_ttc=("ventes_ttc", "sum")))
        agg["serie"] = serie
        return agg

    _fam_n  = _agg_famille(df_n,  f"N ({year_n_label})")
    _fam_n1 = _agg_famille(df_n1, f"N-1 ({year_n1_label})")
    _fam_df = pd.concat([_fam_n, _fam_n1], ignore_index=True)

    if not _fam_df.empty:
        _fam_order = (
            _fam_df[_fam_df["serie"] == f"N ({year_n_label})"]
            .sort_values("ca_ttc", ascending=False)["famille_finale"].tolist()
        )
        st.altair_chart(
            alt.Chart(_fam_df)
            .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
            .encode(
                x=alt.X("famille_finale:N", title="Famille", sort=_fam_order,
                         axis=alt.Axis(labelAngle=-35)),
                xOffset=alt.XOffset("serie:N", sort=[f"N ({year_n_label})", f"N-1 ({year_n1_label})"]),
                y=alt.Y("ca_ttc:Q", title="CA TTC (€)"),
                color=alt.Color("serie:N", title="Série",
                                scale=alt.Scale(domain=[f"N ({year_n_label})", f"N-1 ({year_n1_label})"],
                                                range=["#95d1bd","#585857"])),
                tooltip=[alt.Tooltip("famille_finale:N", title="Famille"),
                         alt.Tooltip("serie:N", title="Série"),
                         alt.Tooltip("ca_ttc:Q", title="CA TTC (€)", format=",.0f")],
            ).properties(height=360),
            use_container_width=True,
        )

st.divider()

# =============================================================================
# Tabs
# =============================================================================
tab_jour, tab_rayon, tab_article = st.tabs(["📅 Jour par Jour", "🌿 Par Rayon", "📦 Top Articles"])

# ─── TAB 1 : ÉVOLUTION ───────────────────────────────────────────────────────
with tab_jour:
    gran = st.session_state.get("gran_nvsn1", "Jour")
    if _mode == "budget":
        def _pct_pill(reel, bud):
            if not bud:
                return '<span class="pill pill-flat">—</span>'
            p = reel / bud * 100
            if p >= 100:
                return f'<span class="pill pill-up">✅ {p:.1f}%</span>'
            elif p >= 80:
                return f'<span class="pill pill-flat">⚠️ {p:.1f}%</span>'
            return f'<span class="pill pill-down">❌ {p:.1f}%</span>'

        BUDGET_THEAD = """
        <thead><tr>
          <th class="sticky-left">Période</th>
          <th>Date</th>
          <th>CA TTC Réalisé</th><th>Budget CA</th><th>% Atteinte CA</th>
          <th class="sep-col">Qté Réalisée</th><th>Budget Qté</th><th>% Atteinte Qté</th>
        </tr></thead>"""

        def _bud_total_row(label, rca, bca, rqte, bqte, cls="tr-total"):
            return f"""
            <tr class="{cls}">
              <td class="sticky-left">{label}</td>
              <td>—</td>
              <td>{fmt_eur(rca)}</td><td>{fmt_eur(bca)}</td><td>{_pct_pill(rca, bca)}</td>
              <td class="sep-col">{fmt_qte(rqte)}</td><td>{fmt_qte(bqte)}</td><td>{_pct_pill(rqte, bqte)}</td>
            </tr>"""

        if gran == "Jour":
            bdf = df_budget.copy()
            bdf["jour"] = pd.to_datetime(bdf["jour"])
            iso_b = bdf["jour"].dt.isocalendar()
            bdf["iso_year"] = iso_b.year.astype("Int64")
            bdf["iso_week"] = iso_b.week.astype("Int64")
            bdf["jour_abr"] = bdf["jour"].dt.weekday.map(JOURS_ABR)
            tbody_b = "<tbody>"
            for (yr, wk), wdf in bdf.groupby(["iso_year","iso_week"], sort=True):
                rca_w = wdf["ca_ttc"].sum(); bca_w = wdf["budget_ca"].sum()
                rq_w  = wdf["qte"].sum();    bq_w  = wdf["budget_qte_article"].sum()
                tbody_b += _bud_total_row(f"S{int(wk)}", rca_w, bca_w, rq_w, bq_w, cls="tr-week")
                for _, row in wdf.iterrows():
                    ds = row["jour"].strftime("%d/%m/%Y") if pd.notna(row["jour"]) else "—"
                    tbody_b += f"""
                    <tr>
                      <td class="sticky-left">{row['jour_abr']}</td>
                      <td>{ds}</td>
                      <td>{fmt_eur(row['ca_ttc'])}</td><td>{fmt_eur(row['budget_ca'])}</td>
                      <td>{_pct_pill(row['ca_ttc'], row['budget_ca'])}</td>
                      <td class="sep-col">{fmt_qte(row['qte'])}</td><td>{fmt_qte(row['budget_qte_article'])}</td>
                      <td>{_pct_pill(row['qte'], row['budget_qte_article'])}</td>
                    </tr>"""
            tbody_b += _bud_total_row("TOTAL", bdf["ca_ttc"].sum(), bdf["budget_ca"].sum(),
                                       bdf["qte"].sum(), bdf["budget_qte_article"].sum())
            tbody_b += "</tbody>"
            df_exp_b = bdf[["jour_abr","jour","ca_ttc","budget_ca","qte","budget_qte_article"]].copy()
            df_exp_b.columns = ["Jour","Date","CA TTC Réalisé","Budget CA","Qté Réalisée","Budget Qté"]

        elif gran == "Semaine":
            bdf = df_budget.copy()
            bdf["wk"] = bdf["jour"].dt.isocalendar().week.astype(int)
            bdf["yr"] = bdf["jour"].dt.isocalendar().year.astype(int)
            agg_b = bdf.groupby(["yr","wk"], as_index=False).agg(
                ca_ttc=("ca_ttc","sum"), budget_ca=("budget_ca","sum"),
                qte=("qte","sum"), budget_qte_article=("budget_qte_article","sum"))
            tbody_b = "<tbody>"
            for _, row in agg_b.iterrows():
                tbody_b += _bud_total_row(
                    f"S{int(row['wk'])} — {int(row['yr'])}",
                    row["ca_ttc"], row["budget_ca"], row["qte"], row["budget_qte_article"], cls="")
            tbody_b += _bud_total_row("TOTAL", agg_b["ca_ttc"].sum(), agg_b["budget_ca"].sum(),
                                       agg_b["qte"].sum(), agg_b["budget_qte_article"].sum())
            tbody_b += "</tbody>"
            df_exp_b = agg_b.rename(columns={"yr":"Année","wk":"Semaine","ca_ttc":"CA TTC Réalisé",
                                              "budget_ca":"Budget CA","qte":"Qté Réalisée","budget_qte_article":"Budget Qté"})

        else:  # Mois
            MOIS_FR2 = {1:"Janvier",2:"Février",3:"Mars",4:"Avril",5:"Mai",6:"Juin",
                        7:"Juillet",8:"Août",9:"Septembre",10:"Octobre",11:"Novembre",12:"Décembre"}
            bdf = df_budget.copy()
            bdf["mo"] = bdf["jour"].dt.month.astype(int)
            bdf["yr"] = bdf["jour"].dt.year.astype(int)
            agg_b = bdf.groupby(["yr","mo"], as_index=False).agg(
                ca_ttc=("ca_ttc","sum"), budget_ca=("budget_ca","sum"),
                qte=("qte","sum"), budget_qte_article=("budget_qte_article","sum"))
            tbody_b = "<tbody>"
            for _, row in agg_b.iterrows():
                tbody_b += _bud_total_row(
                    f"{MOIS_FR2.get(int(row['mo']),'')} {int(row['yr'])}",
                    row["ca_ttc"], row["budget_ca"], row["qte"], row["budget_qte_article"], cls="")
            tbody_b += _bud_total_row("TOTAL", agg_b["ca_ttc"].sum(), agg_b["budget_ca"].sum(),
                                       agg_b["qte"].sum(), agg_b["budget_qte_article"].sum())
            tbody_b += "</tbody>"
            df_exp_b = agg_b.rename(columns={"yr":"Année","mo":"Mois","ca_ttc":"CA TTC Réalisé",
                                              "budget_ca":"Budget CA","qte":"Qté Réalisée","budget_qte_article":"Budget Qté"})

        st.markdown(f'<div class="table-wrap"><table>{BUDGET_THEAD}{tbody_b}</table></div>',
                    unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        export_buttons(df_exp_b, f"budget_{gran.lower()}")

    else:
        COLS_THEAD = """
        <thead><tr>
          <th class="sticky-left">Période</th>
          <th>Date N</th>
          <th>CA TTC N</th><th>CA HT N</th><th>Qté N</th><th>Commission N</th>
          <th class="sep-col">Date N-1</th>
          <th>CA TTC N-1</th><th>% CA TTC</th>
          <th>Qté N-1</th><th>% Qté</th>
          <th>Commission N-1</th><th>% Commission</th>
        </tr></thead>"""

        def total_row(label, ttc_n, ht_n, qte_n, com_n, ttc_n1, qte_n1, com_n1, cls="tr-total"):
            return f"""
            <tr class="{cls}">
              <td class="sticky-left">{label}</td>
              <td>—</td>
              <td>{fmt_eur(ttc_n)}</td><td>{fmt_eur(ht_n)}</td>
              <td>{fmt_qte(qte_n)}</td><td>{fmt_eur(com_n)}</td>
              <td class="sep-col">—</td>
              <td>{fmt_eur(ttc_n1)}</td><td>{evol_pill(ttc_n, ttc_n1)}</td>
              <td>{fmt_qte(qte_n1)}</td><td>{evol_pill(qte_n, qte_n1)}</td>
              <td>{fmt_eur(com_n1)}</td><td>{evol_pill(com_n, com_n1)}</td>
            </tr>"""

        tbody = "<tbody>"

        if gran == "Jour":
            def agg_by_date(df):
                if df.empty:
                    return pd.DataFrame(columns=["period_date","ventes_ttc","ventes_ht","qte","commission"])
                return (df.groupby("period_date")
                        .agg(ventes_ttc=("ventes_ttc","sum"), ventes_ht=("ventes_ht","sum"),
                             qte=("qte","sum"), commission=("commission","sum"))
                        .reset_index())
            dn_day  = agg_by_date(df_n)
            dn1_day = agg_by_date(df_n1)
            dn1_day["date_n"] = dn1_day["period_date"] + timedelta(days=364)
            merged = pd.merge(
                dn_day.rename(columns={"period_date":"date_n","ventes_ttc":"ttc_n",
                                       "ventes_ht":"ht_n","qte":"qte_n","commission":"com_n"}),
                dn1_day.rename(columns={"period_date":"date_n1","ventes_ttc":"ttc_n1",
                                        "ventes_ht":"ht_n1","qte":"qte_n1","commission":"com_n1"})[
                    ["date_n","date_n1","ttc_n1","ht_n1","qte_n1","com_n1"]],
                on="date_n", how="outer",
            ).sort_values("date_n")
            merged["date_n"]  = pd.to_datetime(merged["date_n"])
            merged["date_n1"] = pd.to_datetime(merged["date_n1"])
            iso = merged["date_n"].dt.isocalendar()
            merged["iso_year"] = iso.year.astype("Int64")
            merged["iso_week"] = iso.week.astype("Int64")
            merged["jour_abr"] = merged["date_n"].dt.weekday.map(JOURS_ABR)
            for (yr, wk), wdf in merged.groupby(["iso_year","iso_week"], sort=True):
                tbody += total_row(f"S{int(wk)}",
                    wdf["ttc_n"].sum(), wdf["ht_n"].sum(), wdf["qte_n"].sum(), wdf["com_n"].sum(),
                    wdf["ttc_n1"].sum(), wdf["qte_n1"].sum(), wdf["com_n1"].sum(), cls="tr-week")
                for _, row in wdf.iterrows():
                    dn_str  = row["date_n"].strftime("%d/%m/%Y")  if pd.notna(row["date_n"])  else "—"
                    dn1_str = row["date_n1"].strftime("%d/%m/%Y") if pd.notna(row["date_n1"]) else "—"
                    tbody += f"""
                    <tr>
                      <td class="sticky-left">{row['jour_abr']}</td>
                      <td>{dn_str}</td>
                      <td>{fmt_eur(row['ttc_n'])}</td><td>{fmt_eur(row['ht_n'])}</td>
                      <td>{fmt_qte(row['qte_n'])}</td><td>{fmt_eur(row['com_n'])}</td>
                      <td class="sep-col">{dn1_str}</td>
                      <td>{fmt_eur(row['ttc_n1'])}</td><td>{evol_pill(row['ttc_n'], row['ttc_n1'])}</td>
                      <td>{fmt_qte(row['qte_n1'])}</td><td>{evol_pill(row['qte_n'], row['qte_n1'])}</td>
                      <td>{fmt_eur(row['com_n1'])}</td><td>{evol_pill(row['com_n'], row['com_n1'])}</td>
                    </tr>"""
            tbody += total_row("TOTAL",
                merged["ttc_n"].sum(), merged["ht_n"].sum(), merged["qte_n"].sum(), merged["com_n"].sum(),
                merged["ttc_n1"].sum(), merged["qte_n1"].sum(), merged["com_n1"].sum())
            df_export = merged[["jour_abr","date_n","date_n1","ttc_n","ht_n","qte_n","com_n",
                                 "ttc_n1","ht_n1","qte_n1","com_n1"]].copy()
            df_export.columns = ["Jour","Date N","Date N-1","CA TTC N","CA HT N","Qte N","Commission N",
                                  "CA TTC N-1","CA HT N-1","Qte N-1","Commission N-1"]

        elif gran == "Semaine":
            dfn_s  = df_n.copy()
            dfn1_s = df_n1.copy()
            for d, attr in [(dfn_s, "dfn_s"), (dfn1_s, "dfn1_s")]:
                if not d.empty:
                    _iso = d["period_date"].dt.isocalendar()
                    d["iso_year"] = _iso.year.astype(int)
                    d["iso_week"] = _iso.week.astype(int)
            an  = (dfn_s.groupby(["iso_year","iso_week"]).agg(
                       ttc_n=("ventes_ttc","sum"), ht_n=("ventes_ht","sum"),
                       qte_n=("qte","sum"), com_n=("commission","sum")).reset_index()
                   if not dfn_s.empty else pd.DataFrame())
            an1 = (dfn1_s.groupby(["iso_year","iso_week"]).agg(
                       ttc_n1=("ventes_ttc","sum"), ht_n1=("ventes_ht","sum"),
                       qte_n1=("qte","sum"), com_n1=("commission","sum")).reset_index()
                   if not dfn1_s.empty else pd.DataFrame())
            if not an.empty:
                an["iso_week_key"] = an["iso_week"]
            if not an1.empty:
                an1 = an1.rename(columns={"iso_year":"iso_year_n1","iso_week":"iso_week_key"})
            ws = (pd.merge(an, an1[["iso_week_key","ttc_n1","ht_n1","qte_n1","com_n1"]],
                           on="iso_week_key", how="outer").fillna(0)
                  .sort_values(["iso_year","iso_week"]) if not an.empty else pd.DataFrame())
            for _, row in ws.iterrows():
                tbody += total_row(f"S{int(row['iso_week'])} — {int(row['iso_year'])}",
                    row["ttc_n"], row["ht_n"], row["qte_n"], row["com_n"],
                    row["ttc_n1"], row["qte_n1"], row["com_n1"], cls="")
            tbody += total_row("TOTAL",
                ws["ttc_n"].sum(), ws["ht_n"].sum(), ws["qte_n"].sum(), ws["com_n"].sum(),
                ws["ttc_n1"].sum(), ws["qte_n1"].sum(), ws["com_n1"].sum())
            df_export = ws[["iso_year","iso_week","ttc_n","ht_n","qte_n","com_n",
                             "ttc_n1","ht_n1","qte_n1","com_n1"]].copy()
            df_export.columns = ["Annee","Semaine","CA TTC N","CA HT N","Qte N","Commission N",
                                  "CA TTC N-1","CA HT N-1","Qte N-1","Commission N-1"]

        else:  # Mois
            MOIS_FR = {1:"Janvier",2:"Février",3:"Mars",4:"Avril",5:"Mai",6:"Juin",
                       7:"Juillet",8:"Août",9:"Septembre",10:"Octobre",11:"Novembre",12:"Décembre"}
            def prep_mois(df):
                if df.empty:
                    return pd.DataFrame()
                d = df.copy()
                d["year"]  = d["period_date"].dt.year.astype(int)
                d["month"] = d["period_date"].dt.month.astype(int)
                return d.groupby(["year","month"]).agg(
                    ttc=("ventes_ttc","sum"), ht=("ventes_ht","sum"),
                    qte=("qte","sum"), com=("commission","sum")).reset_index()
            mn  = prep_mois(df_n).rename(columns={"ttc":"ttc_n","ht":"ht_n","qte":"qte_n","com":"com_n"})
            mn1 = prep_mois(df_n1).rename(columns={"ttc":"ttc_n1","ht":"ht_n1","qte":"qte_n1","com":"com_n1","year":"year_n1"})
            ms  = (pd.merge(mn, mn1[["month","ttc_n1","ht_n1","qte_n1","com_n1"]],
                            on="month", how="outer").fillna(0).sort_values(["year","month"])
                   if not mn.empty else pd.DataFrame())
            for _, row in ms.iterrows():
                tbody += total_row(f"{MOIS_FR.get(int(row['month']),'')} {int(row['year'])}",
                    row["ttc_n"], row["ht_n"], row["qte_n"], row["com_n"],
                    row["ttc_n1"], row["qte_n1"], row["com_n1"], cls="")
            tbody += total_row("TOTAL",
                ms["ttc_n"].sum(), ms["ht_n"].sum(), ms["qte_n"].sum(), ms["com_n"].sum(),
                ms["ttc_n1"].sum(), ms["qte_n1"].sum(), ms["com_n1"].sum())
            df_export = ms[["year","month","ttc_n","ht_n","qte_n","com_n",
                             "ttc_n1","ht_n1","qte_n1","com_n1"]].copy()
            df_export.columns = ["Annee","Mois","CA TTC N","CA HT N","Qte N","Commission N",
                                  "CA TTC N-1","CA HT N-1","Qte N-1","Commission N-1"]

        tbody += "</tbody>"
        st.markdown(f'<div class="table-wrap"><table>{COLS_THEAD}{tbody}</table></div>',
                    unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        export_buttons(df_export, f"evolution_{gran.lower()}")

# ─── TAB 2 : PAR RAYON ───────────────────────────────────────────────────────
with tab_rayon:
    def agg_rayon(df):
        if df.empty:
            return pd.DataFrame()
        return (
            df.groupby("rayon")
            .agg(ventes_ttc=("ventes_ttc", "sum"), ventes_ht=("ventes_ht", "sum"),
                 qte=("qte", "sum"), commission=("commission", "sum"))
            .reset_index()
            .sort_values("ventes_ttc", ascending=False)
        )

    rn  = agg_rayon(df_n).rename(columns={"ventes_ttc": "ttc_n", "ventes_ht": "ht_n",
                                            "qte": "qte_n", "commission": "com_n"})
    rn1 = agg_rayon(df_n1).rename(columns={"ventes_ttc": "ttc_n1", "ventes_ht": "ht_n1",
                                             "qte": "qte_n1", "commission": "com_n1"})
    rayon_df = pd.merge(rn, rn1, on="rayon", how="outer").fillna(0).sort_values("ttc_n", ascending=False)

    thead_r = """
    <thead><tr>
      <th class="sticky-left">Rayon</th>
      <th>CA TTC N</th><th>CA TTC N-1</th><th>% CA TTC</th>
      <th>Qté N</th><th>Qté N-1</th><th>% Qté</th>
      <th>Commission N</th><th>Commission N-1</th><th>% Commission</th>
    </tr></thead>"""
    tbody_r = "<tbody>"
    for _, row in rayon_df.iterrows():
        tbody_r += f"""
        <tr>
          <td class="sticky-left">{row['rayon'] or '—'}</td>
          <td>{fmt_eur(row['ttc_n'])}</td>
          <td>{fmt_eur(row['ttc_n1'])}</td>
          <td>{evol_pill(row['ttc_n'], row['ttc_n1'])}</td>
          <td>{fmt_qte(row['qte_n'])}</td>
          <td>{fmt_qte(row['qte_n1'])}</td>
          <td>{evol_pill(row['qte_n'], row['qte_n1'])}</td>
          <td>{fmt_eur(row['com_n'])}</td>
          <td>{fmt_eur(row['com_n1'])}</td>
          <td>{evol_pill(row['com_n'], row['com_n1'])}</td>
        </tr>"""
    tbody_r += "</tbody>"

    st.markdown(
        f'<div class="table-wrap"><table>{thead_r}{tbody_r}</table></div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    df_rayon_exp = rayon_df.rename(columns={
        "rayon":"Rayon","ttc_n":"CA TTC N","ht_n":"CA HT N","qte_n":"Qte N","com_n":"Commission N",
        "ttc_n1":"CA TTC N-1","ht_n1":"CA HT N-1","qte_n1":"Qte N-1","com_n1":"Commission N-1"})
    export_buttons(df_rayon_exp, "rayon_nvsn1")

# ─── TAB 3 : TOP ARTICLES ────────────────────────────────────────────────────
with tab_article:
    top_n = st.slider("Nombre d'articles à afficher", 10, 100, 30, 10, key="top_n_nvsn1")

    def agg_article(df):
        if df.empty:
            return pd.DataFrame()
        return (
            df.groupby("libelle_final")
            .agg(ventes_ttc=("ventes_ttc", "sum"), qte=("qte", "sum"), commission=("commission", "sum"))
            .reset_index()
        )

    an  = agg_article(df_n).rename(columns={"ventes_ttc": "ttc_n", "qte": "qte_n", "commission": "com_n"})
    an1 = agg_article(df_n1).rename(columns={"ventes_ttc": "ttc_n1", "qte": "qte_n1", "commission": "com_n1"})
    art_df = (
        pd.merge(an, an1, on="libelle_final", how="outer")
        .fillna(0)
        .sort_values("ttc_n", ascending=False)
        .head(top_n)
    )

    thead_a = """
    <thead><tr>
      <th class="sticky-left">Article</th>
      <th>CA TTC N</th><th>CA TTC N-1</th><th>% CA TTC</th>
      <th>Qté N</th><th>Qté N-1</th><th>% Qté</th>
      <th>Commission N</th><th>Commission N-1</th><th>% Commission</th>
    </tr></thead>"""
    tbody_a = "<tbody>"
    for _, row in art_df.iterrows():
        tbody_a += f"""
        <tr>
          <td class="sticky-left" style="text-align:left;padding-left:12px;">{row['libelle_final'] or '—'}</td>
          <td>{fmt_eur(row['ttc_n'])}</td>
          <td>{fmt_eur(row['ttc_n1'])}</td>
          <td>{evol_pill(row['ttc_n'], row['ttc_n1'])}</td>
          <td>{fmt_qte(row['qte_n'])}</td>
          <td>{fmt_qte(row['qte_n1'])}</td>
          <td>{evol_pill(row['qte_n'], row['qte_n1'])}</td>
          <td>{fmt_eur(row['com_n'])}</td>
          <td>{fmt_eur(row['com_n1'])}</td>
          <td>{evol_pill(row['com_n'], row['com_n1'])}</td>
        </tr>"""
    tbody_a += "</tbody>"

    st.markdown(
        f'<div class="table-wrap"><table>{thead_a}{tbody_a}</table></div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    df_art_exp = art_df.rename(columns={
        "libelle_final":"Article","ttc_n":"CA TTC N","qte_n":"Qte N","com_n":"Commission N",
        "ttc_n1":"CA TTC N-1","qte_n1":"Qte N-1","com_n1":"Commission N-1"})
    export_buttons(df_art_exp, "articles_nvsn1")

# =============================================================================
# Détail des lignes (période N sélectionnée)
# =============================================================================
st.divider()
st.markdown(
    """
    <h3 style="color:#585857;font-weight:900;">
        🧾 Détail des lignes (période N sélectionnée)
    </h3>
    """,
    unsafe_allow_html=True,
)

_show_cols = [
    "store_name", "period_date", "code_article", "libelle_final", "pvc",
    "famille_finale", "rayon",
    "ventes_ttc", "ventes_ht", "qte", "commission", "commission_pct",
    "iso_year", "iso_month", "iso_week", "iso_month_label", "iso_label",
]
_present = [c for c in _show_cols if c in df_n.columns]

df_detail = (
    df_n[_present]
    .sort_values(["period_date", "store_name"], ascending=[False, True])
    .copy()
)
df_detail["commission_pct"] = 20.0
df_detail = df_detail[[c for c in _show_cols if c in df_detail.columns]]

_libelle_norm = df_detail["libelle_final"].fillna("Inconnu").astype(str).str.strip() if "libelle_final" in df_detail.columns else pd.Series(["Inconnu"] * len(df_detail))
_n_avec  = int((_libelle_norm != "Inconnu").sum())
_n_sans  = int((_libelle_norm == "Inconnu").sum())

_filtre_ref = st.radio(
    "Filtrer par référence article",
    ["Tous", "✅ Avec référence", "❌ Sans référence (Inconnu)"],
    horizontal=True,
    key="radio_filtre_ref_nvsn1",
)
st.caption(
    f"Dataset chargé : **{_n_avec:,}** avec référence · **{_n_sans:,}** sans référence".replace(",", " ")
)

if _filtre_ref == "✅ Avec référence":
    df_detail = df_detail[_libelle_norm != "Inconnu"]
elif _filtre_ref == "❌ Sans référence (Inconnu)":
    df_detail = df_detail[_libelle_norm == "Inconnu"]

st.caption(f"{len(df_detail):,} lignes affichées.".replace(",", " "))

st.dataframe(
    df_detail,
    use_container_width=True,
    column_config={
        "store_name":       st.column_config.TextColumn("Magasin"),
        "period_date":      st.column_config.DateColumn("Date"),
        "code_article":     st.column_config.TextColumn("Code article (GTIN)"),
        "libelle_final":    st.column_config.TextColumn("Libellé article"),
        "famille_finale":   st.column_config.TextColumn("Famille"),
        "rayon":            st.column_config.TextColumn("Rayon"),
        "pvc":              st.column_config.NumberColumn("PVC (€)",        format="%.2f €"),
        "qte":              st.column_config.NumberColumn("Qté vendue",     format="%d"),
        "ventes_ht":        st.column_config.NumberColumn("CA HT (€)",               format="%.2f €"),
        "ventes_ttc":       st.column_config.NumberColumn("CA TTC (€)",              format="%.2f €"),
        "commission":       st.column_config.NumberColumn("Commission Carrefour (€)", format="%.2f €"),
        "commission_pct":   st.column_config.NumberColumn("Commission Carrefour %",  format="%.0f %%"),
        "iso_year":         st.column_config.NumberColumn("Année"),
        "iso_month":        st.column_config.NumberColumn("Mois (n°)"),
        "iso_week":         st.column_config.NumberColumn("Semaine (n°)"),
        "iso_month_label":  st.column_config.TextColumn("Mois"),
        "iso_label":        st.column_config.TextColumn("Semaine"),
    },
)

_col_xls, _col_csv = st.columns(2)
with _col_xls:
    _buf = io.BytesIO()
    df_detail.to_excel(_buf, index=False, engine="openpyxl")
    st.download_button(
        "📊 Télécharger Excel",
        _buf.getvalue(),
        "detail_lignes_n.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        key="xls_detail_n",
    )
with _col_csv:
    st.download_button(
        "📥 Télécharger CSV",
        df_detail.to_csv(index=False, sep=";", encoding="utf-8-sig"),
        "detail_lignes_n.csv",
        "text/csv",
        use_container_width=True,
        key="csv_detail_n",
    )
