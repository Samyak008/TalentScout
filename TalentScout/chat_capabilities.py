from typing import Dict, List, Tuple, Optional
import re

# Constants for fields to collect
FIELDS = [
    ("full_name", "What's your full name?"),
    ("email", "What's your email address?"),
    ("phone", "What's your phone number?"),
    ("years_of_experience", "How many years of experience do you have?"),
    ("desired_position", "What position are you applying for?"),
    ("current_location", "What's your current location?"),
    ("tech_stack", "What's your tech stack? (e.g., Python, Django, React)")
]

class ChatState:
    GREETING = "greeting"
    COLLECTING_INFO = "collecting_info"
    TECHNICAL_ASSESSMENT = "technical_assessment"
    FOLLOW_UP = "follow_up"
    ENDING = "ending"

class TechnicalAssessment:
    def __init__(self, tech_stack: str):
        self.tech_stack = tech_stack.lower().split(',')
        self.current_question_index = 0
        self.questions = self.generate_questions()  # Generate questions immediately
        self.answers = []
        
    def generate_questions(self) -> List[str]:
        """Generate technical questions based on tech stack."""
        questions = []
        for tech in self.tech_stack:
            tech = tech.strip()
            if "python" in tech:
                questions.extend([
                    "What are decorators in Python and how do they work?",
                    "Explain the difference between lists and tuples in Python.",
                    "How does Python's garbage collection work?"
                ])
            elif "django" in tech:
                questions.extend([
                    "Explain Django's MTV architecture.",
                    "What are Django middlewares?",
                    "How do you handle authentication in Django?"
                ])
            elif "react" in tech:
                questions.extend([
                    "Explain React hooks and their advantages.",
                    "What is the virtual DOM in React?",
                    "How do you handle state management in React?"
                ])
            # Add more technology-specific questions here
        
        # If no technology-specific questions were generated, add general programming questions
        if not questions:
            questions = [
                "Explain the concept of Object-Oriented Programming.",
                "What is the difference between compiled and interpreted languages?",
                "How do you approach debugging in your preferred programming language?",
                "Explain the importance of version control in software development.",
                "What are your thoughts on code documentation?"
            ]
        
        return questions[:5]  # Limit to 5 questions
    
    def get_next_question(self) -> Optional[str]:
        """Get the next question in the assessment."""
        if self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            self.current_question_index += 1
            return question
        return None
    
    def record_answer(self, answer: str):
        """Record the candidate's answer."""
        self.answers.append(answer)
    
    def is_complete(self) -> bool:
        """Check if all questions have been answered."""
        return self.current_question_index >= len(self.questions)

class ChatManager:
    def __init__(self):
        self.state = ChatState.GREETING
        self.candidate_data = {}
        self.technical_assessment = None
        
    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, email))
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format."""
        pattern = r'^\+?1?\d{9,15}$'
        return bool(re.match(pattern, phone))
    
    def process_message(self, message: str) -> str:
        """Process incoming message and return appropriate response."""
        if self.state == ChatState.GREETING:
            self.state = ChatState.COLLECTING_INFO
            return self.get_next_info_prompt()
            
        elif self.state == ChatState.COLLECTING_INFO:
            return self.handle_info_collection(message)
            
        elif self.state == ChatState.TECHNICAL_ASSESSMENT:
            return self.handle_technical_assessment(message)
            
        elif self.state == ChatState.ENDING:
            return self.end_conversation()
            
        return self.handle_fallback()
    
    def handle_info_collection(self, message: str) -> str:
        """Handle the information collection phase."""
        current_field = next((field for field, _ in FIELDS 
                            if field not in self.candidate_data), None)
        
        if current_field:
            # Validate input based on field type
            if current_field == "email" and not self.validate_email(message):
                return "Please provide a valid email address."
            elif current_field == "phone" and not self.validate_phone(message):
                return "Please provide a valid phone number."
            elif current_field == "years_of_experience":
                try:
                    years = int(message)
                    if years < 0:
                        return "Please provide a valid number of years."
                    self.candidate_data[current_field] = years
                except ValueError:
                    return "Please provide a valid number for years of experience."
            else:
                self.candidate_data[current_field] = message.strip()
            
            # Get next field or move to technical assessment
            next_field = next((field for field, _ in FIELDS 
                             if field not in self.candidate_data), None)
            if next_field:
                return self.get_next_info_prompt()
            else:
                self.state = ChatState.TECHNICAL_ASSESSMENT
                self.technical_assessment = TechnicalAssessment(
                    self.candidate_data.get("tech_stack", ""))
                return self.start_technical_assessment()
        
        return self.handle_fallback()
    
    def handle_technical_assessment(self, message: str) -> str:
        """Handle the technical assessment phase."""
        if not self.technical_assessment:
            self.technical_assessment = TechnicalAssessment(
                self.candidate_data.get("tech_stack", ""))
        
        self.technical_assessment.record_answer(message)
        
        if self.technical_assessment.is_complete():
            self.state = ChatState.ENDING
            return self.end_conversation()
        
        next_question = self.technical_assessment.get_next_question()
        if next_question:
            return f"Next question:\n{next_question}"
        else:
            self.state = ChatState.ENDING
            return self.end_conversation()
    
    def get_next_info_prompt(self) -> str:
        """Get the next information collection prompt."""
        for field, prompt in FIELDS:
            if field not in self.candidate_data:
                return prompt
        
        # If all fields are collected, move to technical assessment
        self.state = ChatState.TECHNICAL_ASSESSMENT
        self.technical_assessment = TechnicalAssessment(
            self.candidate_data.get("tech_stack", ""))
        return self.start_technical_assessment()
    
    def start_technical_assessment(self) -> str:
        """Start the technical assessment phase."""
        if not self.technical_assessment:
            self.technical_assessment = TechnicalAssessment(
                self.candidate_data.get("tech_stack", ""))
        
        first_question = self.technical_assessment.get_next_question()
        return (
            "Great! Now let's assess your technical knowledge.\n"
            "I'll ask you a few questions based on your tech stack.\n\n"
            f"First question:\n{first_question}"
        )
    
    def end_conversation(self) -> str:
        """End the conversation and provide next steps."""
        return (
            "Thank you for completing the initial screening!\n"
            "Our team will review your responses and get back to you soon.\n"
            "If you have any questions, feel free to reach out to our HR team.\n"
            "Best of luck with your application!"
        )
    
    def handle_fallback(self) -> str:
        """Handle unexpected inputs."""
        return (
            "I'm sorry, I didn't understand that. "
            "Could you please provide the requested information?"
        )