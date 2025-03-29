import streamlit as st
from streamlit_oauth import OAuth2Component
import json, base64, os

def handle_authentication():
    if "auth" not in st.session_state:
        st.title("🔐 Login with Google")
        google_oauth = OAuth2Component(
            os.getenv("GOOGLE_CLIENT_ID"),
            os.getenv("GOOGLE_CLIENT_SECRET"),
            "https://accounts.google.com/o/oauth2/v2/auth",
            "https://oauth2.googleapis.com/token",
            "https://oauth2.googleapis.com/token",
            "https://oauth2.googleapis.com/revoke"
        )
        result = google_oauth.authorize_button(
            name="Continue with Google",
            icon="https://www.google.com.tw/favicon.ico",
            redirect_uri=os.getenv("REDIRECT_URI", "http://localhost:8501"),
            scope="openid email profile",
            key="google_login_btn",
            extras_params={"prompt": "consent", "access_type": "offline"},
            use_container_width=True,
            pkce='S256'
        )

        if result and "token" in result:
            id_token = result["token"]["id_token"]
            payload = id_token.split(".")[1]
            payload += "=" * (-len(payload) % 4)
            decoded_payload = json.loads(base64.b64decode(payload))
            email = decoded_payload.get("email")

            if email:
                user_info = {
                    "email": email,
                    "name": decoded_payload.get("name"),
                    "picture": decoded_payload.get("picture")
                }
                st.session_state["auth"] = email
                st.session_state["user_info"] = user_info
                st.session_state["token"] = result["token"]
                st.rerun()
            else:
                st.error("Failed to retrieve email from ID token.")
        st.warning("🔐 Please log in to continue.")
        st.stop()

    return st.session_state.get("user_info", {})
