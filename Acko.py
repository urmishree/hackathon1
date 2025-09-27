from typing import Dict, TypedDict, Optional
from langgraph.graph import StateGraph, END

class GraphState(TypedDict):
    inoperative: Optional[str]
    response: Optional[str]
    location: Optional[str]

workflow = StateGraph(GraphState)

def svrt_input_node(state):
    return {"inoperative": state.get("inoperative", "").strip().lower()}

def handle_police_ambulance_service_agent_node(state):
    loc = state.get("location", "Unknown")
    return {"response": f"Fatal & serious condition at {loc}. Arrange call to police, ambulance & service agent"}

def handle_service_agent_node(state):
    loc = state.get("location", "Unknown")
    return {"response": f"Fatal but manageable condition at {loc}. Arrange call to service agent only."}

def handle_movable_node(state):
    inop = state.get("inoperative", "Unknown")
    loc = state.get("location", "Unknown")
    return {"response": f"Condition unclear: inoperative='{inop}' at {loc}. Please arrange manual assessment."}

workflow.add_node("svrt_input", svrt_input_node)
workflow.add_node("handle_police_ambulance_service_agent_node", handle_police_ambulance_service_agent_node)
workflow.add_node("handle_service_agent_node", handle_service_agent_node)
workflow.add_node("handle_movable", handle_movable_node)

def decide_next_node(state):
    inop = state.get("inoperative", "").lower()   
    print("value of inop:", inop)
    
    if inop == "yes":
        return "handle_police_ambulance_service_agent_node"
    elif inop == "no":
        return "handle_service_agent_node"
    else:
        return "handle_movable"

workflow.add_conditional_edges(
    "svrt_input",
    decide_next_node,
    {
        "handle_police_ambulance_service_agent_node": "handle_police_ambulance_service_agent_node",
        "handle_service_agent_node": "handle_service_agent_node",
        "handle_movable": "handle_movable"
    }
)

workflow.set_entry_point("svrt_input")
workflow.add_edge("handle_police_ambulance_service_agent_node", END)
workflow.add_edge("handle_service_agent_node", END)
workflow.add_edge("handle_movable", END)

app = workflow.compile()

# Test cases
#print(app.invoke({"inoperative": "Yes", "location": "Koramangala"}))
print(app.invoke({"inoperative": "No", "location": "Koramangala"}))
print(app.invoke({"inoperative": "Maybe", "location": "Koramangala"}))
