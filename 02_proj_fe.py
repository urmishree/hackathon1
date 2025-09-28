# poc_inlo_app.py
import streamlit as st
import requests
import io
from PIL import Image

# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(
    page_title="INLO-APP – Crash Assist",
    page_icon="🚗",
    layout="centered"
)

# Minimal CSS inspired by ACKO’s clean look
st.markdown("""
<style>
    .main {background-color: #f9fbfd;}
    h1 {color: #5a2ec2; text-align: center;}
    .stButton>button {
        background-color: #5a2ec2;
        color: white;
        border-radius: 6px;
        padding: .6rem 1.2rem;
        font-weight: 600;
    }
    .stTextInput>div>div>input, .stTextArea textarea {
        border-radius: 6px;
        border: 1px solid #d0d7de;
        padding: .5rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚗 INLO-APP – Crash Assist")

# -------------------------------
# Upload crashed car image
# -------------------------------
uploaded = st.file_uploader("Upload a crashed car image", type=["jpg","jpeg","png"])

if uploaded:
    image = Image.open(uploaded).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # (Optional) send to backend
    if st.button("Analyze Damage"):
        try:
            # Mock: pretend backend call
            # Replace with: requests.post("http://backend/analyze", files={"file": uploaded})
            resp = {"status":"ok","damage_level":"High","recommendation":"Tow required"}
            st.session_state["last_response"] = resp
            st.success("Image analyzed successfully")
            st.json(resp)
        except Exception as e:
            st.error(f"Backend error: {e}")

# -------------------------------
# Prompt user based on response
# -------------------------------
if "last_response" in st.session_state:
    st.subheader("Ask INLO-APP for Next Steps")
    user_prompt = st.text_area("Enter your query (e.g., 'Nearest tow truck?', 'Estimated cost?')")

    if st.button("Submit Prompt"):
        # Mock backend reply
        # Replace with requests.post("http://backend/prompt", json={"prompt":user_prompt, "context": st.session_state["last_response"]})
        reply = f"Mock reply for: '{user_prompt}'"
        st.info(reply)
