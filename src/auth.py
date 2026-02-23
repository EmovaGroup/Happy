# src/auth.py
import streamlit as st
from .supabase_client import get_supabase


def logout():
    st.session_state["sb_user"] = None
    st.rerun()


def _inject_login_css():
    st.markdown(
        """
<style>
/* Centre le bloc de login */
.login-wrap {
  max-width: 520px;
  margin: 80px auto 0 auto;
  padding: 26px 26px 18px 26px;
  border: 1px solid rgba(120,120,120,0.25);
  border-radius: 16px;
  background: rgba(255,255,255,0.6);
}
[data-theme="dark"] .login-wrap,
body.dark .login-wrap,
html[data-theme="dark"] .login-wrap {
  background: rgba(14,17,23,0.55);
}

.login-title {
  font-size: 22px;
  font-weight: 900;
  margin-bottom: 10px;
}

.login-sub {
  opacity: 0.75;
  margin-bottom: 16px;
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

    st.markdown(
        """
<div class="login-wrap">
  <div class="login-title">🔐 Connexion sécurisée</div>
  <div class="login-sub">Merci de vous connecter pour accéder au dashboard.</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    # on met les inputs juste sous le bloc (mais visuellement centré)
    c = st.container()
    with c:
        left, mid, right = st.columns([1, 2, 1])
        with mid:
            email = st.text_input("Email", key="login_email")
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
