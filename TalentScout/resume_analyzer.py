import os
import pdfplumber 
from typing import Optional, List
from llama_index.core import Settings, VectorStoreIndex, ServiceContext
from llama_index.core import PromptTemplate
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Document
import streamlit as st
import chardet

class ResumeAnalyzer:
    def __init__(self):
        self.query_engine = None
        self.resume_content = None
        self.interview_questions = []
        
    def initialize_models(self) -> bool:
        """Initialize the embedding and language models."""
        try:
            # Initialize embedding model
            embed_model = HuggingFaceEmbedding(
                model_name="BAAI/bge-large-en-v1.5",
                trust_remote_code=True
            )
            
            # Initialize LLM
            llm = Ollama(model="llama3.2:latest", request_timeout=120.0)
            
            # Configure settings
            Settings.embed_model = embed_model
            Settings.llm = llm
            
            return True
        except Exception as e:
            st.error(f"Error initializing models: {str(e)}")
            return False

    def detect_encoding(self, file_content: bytes) -> str:
        """Detect the encoding of the file content."""
        result = chardet.detect(file_content)
        return result['encoding'] or 'utf-8'

    def read_text_file(self, file_content: bytes) -> str:
        """Read text file content with automatic encoding detection."""
        encoding = self.detect_encoding(file_content)
        try:
            return file_content.decode(encoding)
        except UnicodeDecodeError:
            # Fallback encodings if the detected one fails
            for enc in ['utf-8', 'latin-1', 'cp1252', 'ascii']:
                try:
                    return file_content.decode(enc)
                except UnicodeDecodeError:
                    continue
            raise ValueError("Unable to decode file with any supported encoding")

    def process_resume(self, resume_file) -> bool:
        """Process the uploaded resume and create the query engine."""
        try:
            # Reset file pointer to beginning
            resume_file.seek(0)
            file_content = resume_file.read()
            
            # Determine file type and extract text
            file_name = resume_file.name.lower()
            
            if file_name.endswith('.pdf'):
                # Handle PDF files
                resume_file.seek(0)  # Reset pointer for PDF reading
                with pdfplumber.open(resume_file) as pdf:
                    resume_text = "\n".join(
                        page.extract_text() or "" 
                        for page in pdf.pages
                    )
                    if not resume_text.strip():
                        raise ValueError("No text could be extracted from the PDF")
            
            elif file_name.endswith('.txt'):
                # Handle text files with automatic encoding detection
                resume_text = self.read_text_file(file_content)
            
            else:
                raise ValueError(f"Unsupported file format: {file_name}")

            # Store the processed text
            self.resume_content = resume_text

            # Create document and index
            documents = [Document(text=resume_text)]
            index = VectorStoreIndex.from_documents(documents)
            
            # Create query engine with custom prompt
            qa_prompt_tmpl_str = (
                "You are an expert technical recruiter analyzing a candidate's resume. "
                "Context information is below.\n"
                "---------------------\n"
                "{context_str}\n"
                "---------------------\n"
                "Based on this context, think carefully about the candidate's background "
                "and generate relevant technical questions.\n\n"
                "THINKING:\n"
                "[Your analysis of the candidate's experience]\n\n"
                "RESPONSE:\n"
                "[Your technical questions or insights]\n\n"
                "Query: {query_str}\n"
            )
            qa_prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str)
            
            self.query_engine = index.as_query_engine(
                streaming=True,
                similarity_top_k=2
            )
            
            self.query_engine.update_prompts(
                {"response_synthesizer:text_qa_template": qa_prompt_tmpl}
            )
            
            # Generate initial questions based on resume
            self.generate_interview_questions()
            
            return True

        except Exception as e:
            st.error(f"Error processing resume: {str(e)}")
            return False

    def generate_interview_questions(self) -> List[str]:
        """Generate interview questions based on the resume content."""
        if not self.query_engine:
            return []
        
        prompts = [
            "What technical skills does the candidate have? Generate 2 specific technical questions based on their strongest skills.",
            "Based on the candidate's project experience, generate 2 questions about their most significant projects.",
            "Looking at the candidate's work history, generate 1 question about their role and responsibilities."
        ]
        
        questions = []
        for prompt in prompts:
            try:
                response = self.query_engine.query(prompt)
                if response and hasattr(response, 'response'):
                    # Extract questions from the response
                    response_text = response.response
                    if "RESPONSE:" in response_text:
                        questions_part = response_text.split("RESPONSE:")[1].strip()
                        questions.extend([q.strip() for q in questions_part.split('\n') if '?' in q])
            except Exception as e:
                st.warning(f"Error generating question for prompt: {prompt}. Error: {str(e)}")
                continue
        
        self.interview_questions = questions[:5]  # Keep top 5 questions
        return self.interview_questions
    
    def ask_question(self, question: str) -> Optional[str]:
        """Query the resume with a specific question."""
        if not self.query_engine:
            return None
        
        try:
            response = self.query_engine.query(question)
            return response.response if hasattr(response, 'response') else str(response)
        except Exception as e:
            st.error(f"Error querying resume: {str(e)}")
            return None
            
    def get_resume_summary(self) -> Optional[str]:
        """Generate a summary of the resume."""
        if not self.query_engine:
            return None
            
        prompt = (
            "Provide a brief summary of the candidate's background, including their "
            "key skills, experience, and potential fit for technical roles."
        )
        
        try:
            response = self.query_engine.query(prompt)
            return response.response if hasattr(response, 'response') else str(response)
        except Exception as e:
            st.error(f"Error generating resume summary: {str(e)}")
            return None