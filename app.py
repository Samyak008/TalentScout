import streamlit as st
from TalentScout.chat_capabilities import greet, collect_info, generate_tech_questions, handle_fallback, end_conversation
from TalentScout.database import initialize_database, insert_conversation, get_candidate_by_email

def main():
    """Main function to run the Streamlit app."""
    st.title("TalentScout Hiring Assistant")
    initialize_database()

    # Initialize session state
    if "candidate_data" not in st.session_state:
        st.session_state.candidate_data = {}
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": greet()}]

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Handle user input
    user_input = st.chat_input("Type your message here...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        bot_response = collect_info(st.session_state.candidate_data)
        st.session_state.messages.append({"role": "assistant", "content": bot_response})

if __name__ == "__main__":
    main()