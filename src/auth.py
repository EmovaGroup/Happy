# src/auth.py
import streamlit as st
from .supabase_client import get_supabase
from .utils import logo_data_uri, inject_base_css


def logout():
    st.session_state["sb_user"] = None
    st.rerun()


def _inject_login_css():
    inject_base_css()
    st.markdown(
        """
<style>
/* logo centré */
.login-logo{
  text-align:center;
  margin-bottom:16px;
}
.login-logo img{
  height:42px;
  width:auto;
}
/* carte logo */
.login-card{
  border: 2px solid #95d1bd;
  border-radius: 16px;
  padding: 24px 24px 18px 24px;
  background: #ffffff;
  box-shadow: 0 4px 16px rgba(149,209,189,0.18);
  margin-bottom: 20px;
}
.login-title{
  font-size:22px;
  font-weight:900;
  margin-bottom:10px;
  color:#585857;
  text-align:center;
}
.login-sub{
  opacity:0.8;
  margin-bottom:0;
  color:#585857;
  text-align:center;
}

/* labels des inputs */
[data-testid="stWidgetLabel"] label,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] {
  color: #585857 !important;
  font-weight: 700 !important;
}

/* champ input */
[data-testid="stTextInputRootElement"] div[data-baseweb="input"]{
  border-radius: 12px !important;
  border: 1px solid #d1d3d4 !important;
  min-height: 46px !important;
  box-shadow: none !important;
  background: #f7f8fa !important;
}
[data-testid="stTextInputRootElement"] div[data-baseweb="input"]:hover{
  border-color: #95d1bd !important;
}
[data-testid="stTextInputRootElement"] div[data-baseweb="input"]:focus-within{
  border-color: #95d1bd !important;
  box-shadow: 0 0 0 0.18rem rgba(149,209,189,0.25) !important;
}

/* texte dans l'input */
[data-testid="stTextInputRootElement"] input{
  color: #585857 !important;
  background: transparent !important;
}

/* bouton œil */
[data-testid="stTextInputRootElement"] button{
  background: #f7f8fa !important;
  border: none !important;
  box-shadow: none !important;
}
[data-testid="stTextInputRootElement"] svg{
  fill: #585857 !important;
}

/* bouton Se connecter */
.stButton > button{
  width:100%;
  border-radius:12px !important;
  border:1px solid #95d1bd !important;
  background: #95d1bd !important;
  color: #ffffff !important;
  font-weight:900 !important;
  min-height:46px !important;
  box-shadow: 0 4px 12px rgba(88,88,87,0.08) !important;
}
.stButton > button:hover{
  background: #7fbda8 !important;
  border-color: #7fbda8 !important;
  color: #ffffff !important;
}
.stButton > button:focus{
  box-shadow: 0 0 0 0.18rem rgba(149,209,189,0.35) !important;
  outline: none !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )


def require_auth():
    """
    - Affiche un login centré si pas connecté
    - Stocke l'user dans st.session_state["sb_user"] = {"email": "..."}
    """
    if "sb_user" not in st.session_state:
        st.session_state["sb_user"] = None

    if st.session_state["sb_user"]:
        return st.session_state["sb_user"]

    _inject_login_css()
    logo_uri = logo_data_uri()

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        logo_html = f"<div class='login-logo'><img src='{logo_uri}' alt='EMOVA Group'></div>" if logo_uri else ""
        st.markdown(
            f"""
            <div class="login-card">
              {logo_html}
              <div class="login-title">🔐 Connexion sécurisée</div>
              <div class="login-sub">Merci de vous connecter pour accéder au dashboard.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        email    = st.text_input("Email", key="login_email", placeholder="prenom.nom@emova-group.com")
        password = st.text_input("Mot de passe", type="password", key="login_password")
        if st.button("Se connecter", type="primary", use_container_width=True):
            supabase = get_supabase()
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state["sb_user"] = {"email": res.user.email}
                st.success("✅ Connexion réussie")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Identifiants invalides ou erreur : {e}")

    st.stop()
