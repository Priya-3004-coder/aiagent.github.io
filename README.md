# Resume Screening Agent

## Overview
An AI-powered resume screening agent that automatically ranks and scores resumes based on job descriptions. The agent uses semantic similarity and LLM-based analysis to match candidate profiles with job requirements, providing detailed scoring and reasoning for each resume.

## Features
- **Semantic Resume Matching**: Uses vector embeddings to find semantic similarities between resumes and job descriptions
- **AI-Powered Scoring**: Leverages OpenAI GPT to provide detailed scoring (0-100) with reasoning
- **Batch Processing**: Upload multiple resumes (PDF/TXT) for simultaneous screening
- **Detailed Analysis**: Get skill matching, experience relevance, and qualification assessment
- **Interactive UI**: Clean Streamlit interface for easy interaction
- **Export Results**: Download ranked results as CSV

## Limitations
- PDF parsing may struggle with complex layouts or scanned documents
- Requires OpenAI API key (costs apply based on usage)
- Best results with well-structured resumes
- Limited to English language resumes
- Maximum file size: 10MB per resume

## Tech Stack & APIs Used
- **AI Model**: OpenAI GPT-4 (via OpenAI API)
- **Framework**: LangChain for orchestration
- **Vector DB**: ChromaDB for semantic search
- **UI**: Streamlit for web interface
- **Libraries**: 
  - PyPDF2 for PDF parsing
  - sentence-transformers for embeddings
  - pandas for data handling

## Setup & Run Instructions

### Prerequisites
- Python 3.8 or higher
- OpenAI API key

### Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### Running the Application

**Local (OpenAI version):**
```bash
streamlit run app.py
```

**Local (Gemini FREE version):**
```bash
streamlit run app_gemini.py
```

**Cloud deployment:**
```bash
streamlit run app_gemini_cloud.py
```

The application will open in your browser at `http://localhost:8501`

### Deploying to Streamlit Cloud

1. Push your code to GitHub
2. Go to https://share.streamlit.io/
3. Connect your GitHub repository
4. Set main file to `app_gemini_cloud.py`
5. Add your `GEMINI_API_KEY` in Secrets (Settings → Secrets)
6. Deploy!

### Usage

1. Enter the job description in the text area
2. Upload one or more resumes (PDF or TXT format)
3. Click "Screen Resumes" to start the analysis
4. View ranked results with scores and detailed reasoning
5. Download results as CSV if needed

## Architecture

```
┌─────────────────┐
│   User Input    │
│ (Job Desc +     │
│   Resumes)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Streamlit UI   │
│   (app.py)      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│     Resume Screening Agent          │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  1. Document Processing      │  │
│  │     - Extract text from PDFs │  │
│  │     - Clean and normalize    │  │
│  └──────────┬───────────────────┘  │
│             │                       │
│             ▼                       │
│  ┌──────────────────────────────┐  │
│  │  2. Vector Embedding         │  │
│  │     - Generate embeddings    │  │
│  │     - Store in ChromaDB      │  │
│  └──────────┬───────────────────┘  │
│             │                       │
│             ▼                       │
│  ┌──────────────────────────────┐  │
│  │  3. Semantic Search          │  │
│  │     - Query with job desc    │  │
│  │     - Retrieve top matches   │  │
│  └──────────┬───────────────────┘  │
│             │                       │
│             ▼                       │
│  ┌──────────────────────────────┐  │
│  │  4. LLM Analysis (GPT-4)     │  │
│  │     - Detailed scoring       │  │
│  │     - Reasoning generation   │  │
│  └──────────┬───────────────────┘  │
│             │                       │
└─────────────┼───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│     Ranked Results Display          │
│  - Scores (0-100)                   │
│  - Detailed reasoning               │
│  - Skill matching analysis          │
│  - CSV export option                │
└─────────────────────────────────────┘
```

## How It Works

1. **Input Processing**: User provides job description and uploads resumes
2. **Text Extraction**: Agent extracts text from PDF/TXT files
3. **Embedding Generation**: Creates vector embeddings using sentence-transformers
4. **Vector Storage**: Stores embeddings in ChromaDB for efficient similarity search
5. **Semantic Matching**: Compares job description with resume embeddings
6. **LLM Scoring**: GPT-4 analyzes each resume against job requirements
7. **Ranking**: Sorts candidates by score and presents results
8. **Output**: Displays ranked list with detailed feedback

## Potential Improvements

- **Multi-language Support**: Add support for resumes in multiple languages
- **Advanced Parsing**: Integrate better PDF parsing (e.g., pdfplumber, Camelot)
- **Custom Scoring Weights**: Allow users to prioritize different criteria (skills vs experience)
- **Interview Question Generation**: Auto-generate interview questions based on resume gaps
- **ATS Integration**: Connect with Applicant Tracking Systems via APIs
- **Batch Job Processing**: Support multiple job descriptions simultaneously
- **Resume Anonymization**: Remove bias by hiding personal information
- **Skills Extraction**: Use NER to extract and categorize skills automatically
- **Experience Timeline**: Visualize candidate career progression
- **Comparison View**: Side-by-side comparison of top candidates
- **Email Integration**: Auto-send results to hiring managers
- **Database Persistence**: Store historical screening data for analytics
- **Fine-tuned Models**: Train custom models on company-specific hiring data
- **Video Resume Analysis**: Extend to analyze video introductions
- **Social Profile Integration**: Pull data from LinkedIn, GitHub, etc.

## License
MIT License
