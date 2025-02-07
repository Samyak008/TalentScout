# TalentScout Hiring Assistant

A Streamlit-based application that enables candidates to register, upload resumes, and interact with a hiring assistant chatbot for job opportunities.

![TalentScout Interface](assets/home_page.png)

## Features

- 📄 **Resume Upload & Processing**: Supports PDF and TXT file uploads for automated resume analysis.
- 🔍 **Candidate Registration**: Collects key details such as name, email, experience, and desired position.
- 🤖 **AI-Powered Chatbot**: Engages candidates in real-time conversations to assess skills and match job opportunities.
- 🏢 **Agency Dashboard**: Allows hiring agencies to access candidate data and past conversations.
- 🔄 **Persistent Chat History**: Stores candidate conversations for future reference.
- 🖥️ **User-Friendly Interface**: Built using Streamlit for an intuitive and seamless experience.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Samyak008/TalentScout.git
   cd TalentScout
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:

   ```bash
   streamlit run app.py
   ```

## How to Use

### Candidate Workflow
1. Upload a resume (PDF or TXT) for analysis.
2. Fill out the registration form with personal and professional details.
3. Proceed to chat with the TalentScout Hiring Assistant.
4. Receive tailored job suggestions and interview guidance.

### Agency Workflow
1. View all registered candidates and their details.
2. Access past chat conversations to assess candidate suitability.
3. Engage with candidates via AI-driven chat capabilities.

## Requirements

Key dependencies include:

- `streamlit==1.32.0`
- `ollama==0.1.0`
- `db-sqlite3`
- `llama-index-core`
- `llama-index-embeddings-huggingface`
- `llama-index-llms-ollama`
- `pdfplumber`
- `chardet`
 
## Project Structure

```bash
TalentScout/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Project dependencies
├── assets/                # UI-related images and icons
├── TalentScout/
│   ├── database.py        # Database management (SQLite)
│   ├── chat_capabilities.py # Chatbot logic & processing
│   ├── resume_analyzer.py # Resume parsing and analysis
│   ├── utils.py           # Helper functions
└── README.md              # Documentation
```

## Features in Detail

- **Resume Parsing**: Extracts key details such as skills, experience, and education.
- **AI Chatbot**: Provides interview tips, job matches, and career advice.
- **Candidate & Agency Modes**: Allows both job seekers and recruiters to interact with the system.
- **Database Integration**: Stores candidate details and chat history for streamlined hiring.

## Contributing

Contributions are welcome! Feel free to submit a pull request with improvements.

## License

[Add your license information here]

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
