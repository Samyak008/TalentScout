from typing import Dict, List, Tuple, Optional
from TalentScout.resume_analyzer import ResumeAnalyzer
from TalentScout.chat_engine import chat
import re

class ChatState:
    GREETING = "greeting"
    TECHNICAL_ASSESSMENT = "technical_assessment"
    RESUME_QUESTIONS = "resume_questions"  # Added new state
    FOLLOW_UP = "follow_up"
    ENDING = "ending"

class TechnicalAssessment:
    def __init__(self, tech_stack: str):
        self.tech_stack = tech_stack.lower().split(',')
        self.current_question_index = 0
        self.questions = []
        self.answers = []
        self.generate_questions()
        
    def generate_questions(self):
        """Generate technical questions using the chat engine."""
        techs = ", ".join(self.tech_stack)
        prompt = [
            {
                "role": "system",
                "content": "You are an expert technical interviewer. Generate specific, technical questions based on the candidate's tech stack."
            },
            {
                "role": "user",
                "content": f"Generate 5 technical interview questions for a candidate who knows: {techs}. Make questions specific to these technologies."
            }
        ]
        
        response = chat(prompt)
        # Split response into questions
        self.questions = [q.strip() for q in response["content"].split('\n') if '?' in q][:5]
        
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
        self.resume_analyzer = ResumeAnalyzer()
        self.resume_questions = []
        self.current_resume_question_index = 0
        self.chat_history = []

    def process_resume(self, resume_file) -> bool:
        """Process the uploaded resume."""
        if self.resume_analyzer.initialize_models():
            success = self.resume_analyzer.process_resume(resume_file)
            if success:
                # Store resume-based questions
                self.resume_questions = self.resume_analyzer.interview_questions
                return True
        return False
        
    def initialize_with_registration(self, candidate_data: Dict):
        """Initialize chat manager with registration data."""
        self.candidate_data = candidate_data
        self.state = ChatState.GREETING
        return self.get_greeting()
        
    def get_greeting(self) -> str:
        """Generate personalized greeting using chat engine."""
        prompt = [
            {
                "role": "system",
                "content": "You are a friendly technical interviewer. Generate a warm, personalized greeting."
            },
            {
                "role": "user",
                "content": f"Generate a greeting for {self.candidate_data['full_name']} who is applying for {self.candidate_data['desired_position']} position with {self.candidate_data['years_of_experience']} years of experience."
            }
        ]
        
        response = chat(prompt)
        # If we have resume questions, start with those
        if self.resume_questions:
            self.state = ChatState.RESUME_QUESTIONS
            greeting = response["content"] + "\n\nI've reviewed your resume, and I'd like to ask you some specific questions about your experience."
            return greeting + "\n\n" + self.get_next_resume_question()
        else:
            self.state = ChatState.TECHNICAL_ASSESSMENT
            return response["content"] + "\n\nLet's begin with some technical questions based on your experience."

    def get_next_resume_question(self) -> Optional[str]:
        """Get the next resume-based question."""
        if self.current_resume_question_index < len(self.resume_questions):
            question = self.resume_questions[self.current_resume_question_index]
            self.current_resume_question_index += 1
            return question
        return None
        
    def handle_resume_questions(self, message: str) -> str:
        """Handle resume-based questions phase."""
        # Store the answer
        if hasattr(self.resume_analyzer, 'store_answer'):
            self.resume_analyzer.store_answer(message)
        
        next_question = self.get_next_resume_question()
        if next_question:
            return f"Thank you for your response. Next question:\n{next_question}"
        else:
            self.state = ChatState.TECHNICAL_ASSESSMENT
            return "Thank you for those insights about your experience. Now, let's move on to some technical questions.\n\n" + self.handle_technical_assessment("")
            
    def handle_technical_assessment(self, message: str) -> str:
        """Handle technical assessment phase."""
        if not self.technical_assessment:
            self.technical_assessment = TechnicalAssessment(self.candidate_data["tech_stack"])
            return self.technical_assessment.get_next_question()
            
        if message:  # Only analyze answer if there's a message
            # Record the answer and analyze it using chat engine
            self.technical_assessment.record_answer(message)
            
            # Generate follow-up based on the answer
            prompt = [
                {
                    "role": "system",
                    "content": "You are an expert technical interviewer. Analyze the candidate's answer and provide a relevant follow-up or move to the next question."
                },
                {
                    "role": "user",
                    "content": f"Previous question: {self.technical_assessment.questions[self.technical_assessment.current_question_index-1]}\nCandidate's answer: {message}\nProvide a brief response and move to the next question if appropriate."
                }
            ]
            
            response = chat(prompt)
            response_content = response["content"]
        else:
            response_content = ""

        if self.technical_assessment.is_complete():
            self.state = ChatState.ENDING
            return self.end_conversation()
            
        next_question = self.technical_assessment.get_next_question()
        if next_question:
            return f"{response_content}\n\nNext question: {next_question}" if response_content else next_question
        else:
            self.state = ChatState.ENDING
            return self.end_conversation()
    
    def process_message(self, message: str) -> str:
        """Process incoming message and return appropriate response."""
        # Add message to chat history
        self.chat_history.append({"role": "user", "content": message})
        
        response = ""
        if self.state == ChatState.GREETING:
            response = self.get_greeting()
        elif self.state == ChatState.RESUME_QUESTIONS:
            response = self.handle_resume_questions(message)
        elif self.state == ChatState.TECHNICAL_ASSESSMENT:
            response = self.handle_technical_assessment(message)
        elif self.state == ChatState.ENDING:
            response = self.end_conversation()
        else:
            response = self.handle_fallback()
            
        # Add response to chat history
        self.chat_history.append({"role": "assistant", "content": response})
        return response
    
    def end_conversation(self) -> str:
        """Generate personalized conversation ending."""
        prompt = [
            {
                "role": "system",
                "content": "You are a friendly technical interviewer. Generate a warm closing message."
            },
            {
                "role": "user",
                "content": f"Generate a closing message for {self.candidate_data['full_name']}'s technical interview for the {self.candidate_data['desired_position']} position."
            }
        ]
        
        response = chat(prompt)
        return response["content"]
    
    def handle_fallback(self) -> str:
        """Handle unexpected inputs using chat engine."""
        prompt = [
            {
                "role": "system",
                "content": "You are a friendly technical interviewer. Generate a response for unexpected input."
            },
            {
                "role": "user",
                "content": "Generate a friendly message asking the candidate to provide relevant information for the technical interview."
            }
        ]
        
        response = chat(prompt)
        return response["content"]