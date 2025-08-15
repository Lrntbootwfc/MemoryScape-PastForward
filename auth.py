import bcrypt
import streamlit as st
from db import init_db, get_user_by_email, create_user

def ensure_db():
    init_db()

def signup(email: str, name: str, password: str) -> bool:
    pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    ok, err = create_user(email, name, pw_hash)
    if not ok:
        st.error(err)
    return ok

def login(email: str, password: str):
    row = get_user_by_email(email)
    if not row:
        st.error("No account for this email.")
        return None
    user_id, email, name, password_hash, _created_at = row
    if bcrypt.checkpw(password.encode("utf-8"), password_hash):
        return {"id": user_id, "email": email, "name": name}
    st.error("Incorrect password.")
    return None

def logout():
    for k in ["user", "page", "theme"]:
        if k in st.session_state:
            del st.session_state[k]

