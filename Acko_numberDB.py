from typing import Dict, TypedDict, Optional, List
from langgraph.graph import StateGraph, END

# poc_inlo_app.py
import streamlit as st
import requests
import io
from PIL import Image
import json
import openai
import requests

import localcompare_number

# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(
    page_title="INLO-APP – Crash Assist",
    page_icon="🚗",
    layout="centered"
)

# --------------------------
# Step 1: Graph State
# --------------------------
class GraphState(TypedDict):
    vehicle_number: Optional[str]
    inoperative: Optional[str]
    location: Optional[str]
    vehicle_owner: Optional[str]
    insurance_number: Optional[str]
    response: Optional[str]

# --------------------------
# Step 1: Email Data
# --------------------------
class EmailData(TypedDict):
    to: List[str]
    cc: List[str]
    subject: str
    body: str

class InsuranceSupport():
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        # Initialize with OpenRouter API credentials
        if not api_key:
            raise ValueError("API key is required")
        else:   
            print("API key provided")

        # self.client = openai.OpenAI(
        #     api_key=api_key,
        #     base_url=base_url
        # )
        # self.model = "openai/gpt-4o"
        self.app = self._build_graph()
    # --------------------------
    # Dummy Vehicle DB
    # --------------------------
    _vehicle_db = {
        "GJ01 JY0887": {"owner": "Shajee", "insurance": "INS123456"},
        "GJ01 JY0888": {"owner": "Anand", "insurance": "INS987655"},
    }

    _vehicle_info = {}
    # ---------------- CONFIGURE PATHS ----------------
    _reference_image = "Good4.jpg"   # <-- reference image path

    def _send_mail(self, mail: EmailData) -> bool:
        # Mock email sending function
        to = mail.get("to", [])
        cc = mail.get("cc", [])
        subject = mail.get("subject", "")
        body = mail.get("body", "")

        print(f"Sending email to: {to}, cc: {cc}, subject: {subject}, body: {body}")
        # Simulate sending email via n8n webhook
        url = "https://anand-outskill.app.n8n.cloud/webhook/a7c289d5-5b98-4105-b456-8e69fdaa1ea5"
        response = requests.post(url, json=mail)

        print(response.status_code)
        if response.status_code == 200:
            print(response.json())  # If the response is in JSON format

        return True
    # --------------------------
    # Node 1: Vehicle Verification
    # --------------------------
    def _verify_vehicle_node(self, state):
        vehicle_num = state.get("vehicle_number", "").upper()
        if vehicle_num in self._vehicle_db:
            info = self._vehicle_db[vehicle_num]
            return {
                "vehicle_owner": info["owner"],
                "insurance_number": info["insurance"],
                "response": f"Vehicle {vehicle_num} verified. Owner: {info['owner']}, Insurance: {info['insurance']}"
            }
        else:
            # Ask insurance opt-in; for simplicity, assume user accepts
            return {
                "vehicle_owner": None,
                "insurance_number": None,
                "response": f"Vehicle {vehicle_num} not found. Insurance opt-in accepted. Proceeding..."
            }

    # --------------------------
    # Node 2: Normalize inoperative input
    # --------------------------
    def _svrt_input_node(self, state):
        return {"inoperative": state.get("inoperative", "").strip().lower()}

    # --------------------------
    # Node 3: Inoperative = Yes
    # --------------------------
    def _handle_police_ambulance_service_agent_node(self, state):
        loc = state.get("location", "Unknown")
        owner = state.get("vehicle_owner", "Unknown")
        mail_dict: EmailData = {
            "to": [
                "grader_vaguely921@simplelogin.com",
                "Shajee.cloud@gmail.com",
                "m.urmishree@gmail.com"
            ],
            "subject": "reg: Accident Assistance Required",
            "body": f"{owner} met with Fatal & serious accident at {loc}. Arrange call to police, ambulance & service agent. "
        }
        self._send_mail(mail_dict)
        return {"response": f"Fatal & serious condition at {loc}. Arrange call to police, ambulance & service agent."}

    # --------------------------
    # Node 4: Inoperative = No
    # --------------------------
    def _handle_service_agent_node(self, state):
        loc = state.get("location", "Unknown")
        return {"response": f"Fatal but manageable condition at {loc}. Arrange call to service agent only."}

    # --------------------------
    # Node 5: Inoperative unknown
    # --------------------------
    def _handle_movable_node(self, state):
        inop = state.get("inoperative", "Unknown")
        loc = state.get("location", "Unknown")
        return {"response": f"Condition unclear: inoperative='{inop}' at {loc}. Please arrange manual assessment."}


    # --------------------------
    # Step 4: Conditional Edges
    # --------------------------

    # Decide after vehicle verification
    def _decide_after_vehicle_verification(self, state):
        # Proceed to inoperative check
        return "svrt_input"

    # Decide next node after inoperative input
    def _decide_next_node(self, state):
        inop = state.get("inoperative", "")
        if inop == "yes":
            return "handle_police_ambulance_service_agent_node"
        elif inop == "no":
            return "handle_service_agent_node"
        else:
            return "handle_movable"

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for dynamic story generation"""
        # --------------------------
        # Step 2: Create Workflow
        # --------------------------
        workflow = StateGraph(GraphState)
        
        # --------------------------
        # Step 3: Add Nodes
        # --------------------------
        workflow.add_node("verify_vehicle", self._verify_vehicle_node)
        workflow.add_node("svrt_input", self._svrt_input_node)
        workflow.add_node("handle_police_ambulance_service_agent_node", self._handle_police_ambulance_service_agent_node)
        workflow.add_node("handle_service_agent_node", self._handle_service_agent_node)
        workflow.add_node("handle_movable", self._handle_movable_node)

        workflow.add_conditional_edges(
            "verify_vehicle",
            self._decide_after_vehicle_verification,
            {
                "svrt_input": "svrt_input"
            }
        )

        workflow.add_conditional_edges(
            "svrt_input",
            self._decide_next_node,
            {
                "handle_police_ambulance_service_agent_node": "handle_police_ambulance_service_agent_node",
                "handle_service_agent_node": "handle_service_agent_node",
                "handle_movable": "handle_movable"
            }
        )

        # --------------------------
        # Step 5: Set Entry & End
        # --------------------------
        workflow.set_entry_point("verify_vehicle")
        workflow.add_edge("handle_police_ambulance_service_agent_node", END)
        workflow.add_edge("handle_service_agent_node", END)
        workflow.add_edge("handle_movable", END)
        workflow.add_edge("svrt_input", END)

        # --------------------------
        # Step 6: Compile
        # --------------------------
        app = workflow.compile()

        return app


    def _start_intialize_state(self):

        state = GraphState(
            vehicle_number="",
            inoperative="",
            location="Koramangala"
        )
        return state

    def start_vehicle_analysis(self, image):
        print("Starting vehicle analysis...")
        result = localcompare_number.compare_vehicle("broken4.jpg")

        state  = self._start_intialize_state()

        if image:
            print("Image received for analysis.")
            print(f"Image format: {image.format}, size: {image.size}, mode: {image.mode}")

        print(" vehicle number ", result.get("vehicle_number"))
        print(" is operative ", result.get("operative"))

        state["vehicle_number"] = result.get("vehicle_number", "Unknown")
        state["inoperative"] = result.get("operative", "unknown")

        return state

    def test_api(self, state):
        # --------------------------  
        # Step 7: Test Inputs  
        # --------------------------  
        # Vehicle exists, inoperative = Yes  
        print(self.app.invoke({
            "vehicle_number": state["vehicle_number"],
            "inoperative": state["inoperative"],
            "location": state["location"]
        }))

        # # # Vehicle exists, inoperative = No
        # print(self.app.invoke({
        #     "vehicle_number": "KA02CD5678",
        #     "inoperative": "No",
        #     "location": "Whitefield"
        # }))

        # # # Vehicle does not exist, inoperative = Maybe
        # print(self.app.invoke({
        #     "vehicle_number": "KA03EF9999",
        #     "inoperative": "Maybe",
        #     "location": "Indiranagar"
        # }))



# Streamlit integration - UI code
# ===========================================
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

    # Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key input
    api_key = st.text_input(
        "OpenRouter API Key",
        type="password",
        help="Get your API key from https://openrouter.ai/keys"
    )
    
    if not api_key:
        st.warning("Please enter your OpenRouter API key to begin!")
        st.info("👆 Enter your API key above, then configure your story settings and click 'Start New Story'")
        st.stop()
    
    st.success("✅ API Key entered! Configure your story below.")



if 'support' not in st.session_state:
    st.session_state["support"] = InsuranceSupport(api_key=api_key)
# if "isInitialized" not in st.session_state:
#     st.session_state["isInitialized"] = False

# -------------------------------
# Upload crashed car image
# -------------------------------

uploaded = st.file_uploader("Upload a crashed car image", type=["jpg","jpeg","png"])

if uploaded:
    st.session_state["image"] = Image.open(uploaded).convert("RGB")
    st.image(st.session_state["image"], caption="Uploaded Image", width='stretch')
    # st.session_state["isInitialized"] = False

    if st.button("Load Image"):
        try:
            st.success("Load Image successfull")
            st.session_state["support_state"] =  st.session_state["support"].start_vehicle_analysis(st.session_state["image"])
            print("Support state:", st.session_state["support_state"])
            # st.session_state["isInitialized"] = True
            # st.json(resp)
        except Exception as e:
            st.error(f"Backend error: {e}")

    if st.button("Analyze Damage"):
        try:
            st.session_state["support"].test_api(st.session_state["support_state"])
            st.success("Damage analysis started.")
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
