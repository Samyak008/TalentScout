import streamlit as st
from TalentScout.database import initialize_database, get_all_candidates, get_conversations_by_candidate_id
from TalentScout.chat_capabilities import ChatManager

# Initialize the database
initialize_database()

# --- Helper Functions ---
def candidate_registration():
    st.header("Candidate Registration")
    with st.form("registration_form", clear_on_submit=True):
        full_name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number")
        years_of_experience = st.number_input("Years of Experience", min_value=0, step=1)
        desired_position = st.text_input("Desired Position")
        current_location = st.text_input("Current Location")
        tech_stack = st.text_input("Tech Stack (e.g., Python, Django, React)")
        submitted = st.form_submit_button("Submit")
    
        if submitted and all([full_name, email, phone, desired_position, current_location, tech_stack]):
            candidate_data = {
                "full_name": full_name,
                "email": email,
                "phone": phone,
                "years_of_experience": years_of_experience,
                "desired_position": desired_position,
                "current_location": current_location,
                "tech_stack": tech_stack
            }
            # Store candidate details in session for use in chat flow
            st.session_state.candidate_data = candidate_data
            st.session_state.show_proceed_button = True
            st.success("Registration complete!")
        elif submitted:
            st.error("Please fill in all required fields.")

def candidate_chat():
    st.header("Chat with TalentScout Hiring Assistant")
    
    # Initialize chat manager if not present
    if "chat_manager" not in st.session_state:
        st.session_state.chat_manager = ChatManager()
        # Initialize the chat manager with candidate data
        st.session_state.chat_manager.candidate_data = st.session_state.candidate_data
    
    # Initialize message history if not present
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "👋 Welcome to the technical assessment! I'll be asking you some questions based on your tech stack."}]
    
    # Display candidate's registration info in sidebar
    with st.sidebar:
        st.header("Your Profile")
        for key, value in st.session_state.candidate_data.items():
            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if user_input := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Get bot response
        bot_response = st.session_state.chat_manager.process_message(user_input)
        
        # Add bot response to chat history
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        
        # Force a rerun to update the chat immediately
        st.rerun()

def agency_dashboard():
    st.header("Agency Dashboard")
    st.write("Welcome, Agency Representative!")
    # Simple password authentication (in production, use secure methods)
    password = st.text_input("Enter password", type="password")
    if password != "agency123":  # Replace with your own secure check
        st.error("Incorrect password")
        return

    st.success("Logged in successfully!")
    st.subheader("List of Candidates")
    candidates = get_all_candidates()
    if candidates:
        for candidate in candidates:
            candidate_id, full_name, email, *_ = candidate
            if st.button(f"{full_name} ({email})", key=candidate_id):
                st.session_state.selected_candidate_id = candidate_id
                st.session_state.selected_candidate = candidate
                st.experimental_rerun()
    
    # If a candidate is selected, display detailed information and conversation history
    if "selected_candidate_id" in st.session_state:
        candidate_id = st.session_state.selected_candidate_id
        st.subheader("Candidate Details")
        st.write(st.session_state.selected_candidate)
        st.subheader("Conversation History")
        conversations = get_conversations_by_candidate_id(candidate_id)
        if conversations:
            for conv in conversations:
                st.write(f"[{conv[4]}] **{conv[2]}**: {conv[3]}")
        else:
            st.info("No conversation history found for this candidate.")

# --- Main Routing ---
def main():
    st.title("TalentScout Hiring Assistant")
    
    # Create a sidebar menu to select role
    role = st.sidebar.selectbox("Select your role", ["Candidate", "Agency"])
    
    if role == "Candidate":
        if "chat_started" not in st.session_state:
            candidate_registration()
            
            # Show "Proceed to Chat" button after successful registration
            if "show_proceed_button" in st.session_state:
                if st.button("Proceed to Chat"):
                    st.session_state.chat_started = True
                    st.rerun()
        else:
            candidate_chat()
    else:
        agency_dashboard()

if __name__ == "__main__":
    main()