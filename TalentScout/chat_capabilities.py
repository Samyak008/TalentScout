from TalentScout.database import insert_candidate, insert_conversation, get_candidate_by_email
from TalentScout.chat_engine import chat

def greet() -> str:
    """Greet the candidate and explain the chatbot's purpose."""
    return (
        "👋 Welcome to TalentScout Hiring Assistant!\n"
        "I'll help you with the initial screening process.\n"
        "Let's start by gathering some basic information about you."
    )

def collect_info(candidate_data: dict) -> str:
    """Collect candidate information step by step."""
    if not candidate_data.get("full_name"):
        return "What's your full name?"
    elif not candidate_data.get("email"):
        return "What's your email address?"
    elif not candidate_data.get("phone"):
        return "What's your phone number?"
    elif not candidate_data.get("years_of_experience"):
        return "How many years of experience do you have?"
    elif not candidate_data.get("desired_position"):
        return "What position are you applying for?"
    elif not candidate_data.get("current_location"):
        return "What's your current location?"
    elif not candidate_data.get("tech_stack"):
        return "What's your tech stack? (e.g., Python, Django, React)"
    else:
        # Save candidate data to the database
        candidate_id = insert_candidate(**candidate_data)
        return generate_tech_questions(candidate_data["tech_stack"])

def generate_tech_questions(tech_stack: str) -> str:
    """Generate technical questions based on the declared tech stack."""
    prompt = (
        f"Generate 3-5 technical interview questions for a candidate with the following tech stack: {tech_stack}.\n"
        "Ensure the questions are relevant and challenging."
    )
    response = chat([{"role": "user", "content": prompt}])
    return response["content"]

def handle_fallback() -> str:
    """Handle unexpected inputs."""
    return "I'm sorry, I didn't understand that. Can you please rephrase or provide the requested information?"

def end_conversation() -> str:
    """End the conversation gracefully."""
    return (
        "Thank you for your time! We'll review your responses and get back to you soon.\n"
        "Have a great day!"
    )