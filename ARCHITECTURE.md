# Resume Screening Agent - Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE LAYER                          │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                      Streamlit Web UI (app.py)                    │ │
│  │                                                                   │ │
│  │  • Job Description Input                                         │ │
│  │  • Resume File Upload (PDF/TXT)                                  │ │
│  │  • Results Display & Export                                      │ │
│  └───────────────────────────┬───────────────────────────────────────┘ │
└────────────────────────────────┼─────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      AGENT ORCHESTRATION LAYER                          │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │            ResumeScreeningAgent (resume_agent.py)                 │ │
│  │                                                                   │ │
│  │  Main Methods:                                                   │ │
│  │  • screen_resumes()      - Main orchestration                    │ │
│  │  • extract_text()        - Document processing                   │ │
│  │  • create_vector_store() - Embedding management                  │ │
│  │  • score_resume()        - LLM-based scoring                     │ │
│  └───────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
                 ┌───────────────┼───────────────┐
                 │               │               │
                 ▼               ▼               ▼
┌──────────────────────┐ ┌──────────────┐ ┌─────────────────────┐
│  DOCUMENT PROCESSING │ │ VECTOR STORE │ │   LLM PROCESSING    │
│                      │ │              │ │                     │
│  ┌────────────────┐  │ │ ┌──────────┐ │ │  ┌──────────────┐  │
│  │   PyPDF2       │  │ │ │ChromaDB  │ │ │  │  OpenAI      │  │
│  │   Text Extract │  │ │ │Vector DB │ │ │  │  GPT-4       │  │
│  └────────────────┘  │ │ └──────────┘ │ │  └──────────────┘  │
│                      │ │              │ │                     │
│  • Parse PDF files   │ │ • Store      │ │  • Analyze resume  │
│  • Extract text      │ │   embeddings │ │  • Generate score  │
│  • Clean content     │ │ • Semantic   │ │  • Provide reason  │
│                      │ │   search     │ │  • Match skills    │
└──────────────────────┘ └──────────────┘ └─────────────────────┘
         │                       │                    │
         └───────────────────────┼────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICES                               │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                        OpenAI API                                │  │
│  │                                                                  │  │
│  │  • text-embedding-ada-002  (Embeddings)                          │  │
│  │  • gpt-4                   (Analysis & Scoring)                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            OUTPUT LAYER                                 │
│                                                                         │
│  • Ranked Resume List (Score 0-100)                                    │
│  • Detailed Analysis & Reasoning                                       │
│  • Skill Matching Assessment                                           │
│  • CSV Export                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Step-by-Step Process

```
1. INPUT STAGE
   ├─ User enters job description
   └─ User uploads resume files (PDF/TXT)
          │
          ▼
2. DOCUMENT PROCESSING
   ├─ Extract text from PDFs using PyPDF2
   ├─ Parse TXT files
   └─ Clean and normalize text
          │
          ▼
3. EMBEDDING GENERATION
   ├─ Generate embeddings for each resume
   │  using OpenAI text-embedding-ada-002
   ├─ Generate embedding for job description
   └─ Store in ChromaDB vector database
          │
          ▼
4. SEMANTIC SEARCH
   ├─ Query ChromaDB with job description embedding
   ├─ Calculate cosine similarity
   └─ Retrieve all resumes with similarity scores
          │
          ▼
5. LLM ANALYSIS (for each resume)
   ├─ Create structured prompt with:
   │  • Job description
   │  • Resume content
   ├─ Send to GPT-4 for analysis
   ├─ Extract:
   │  • Overall score (0-100)
   │  • Key strengths
   │  • Skill matching
   │  • Experience relevance
   │  • Gaps/concerns
   │  └─ Recommendation
          │
          ▼
6. RANKING & OUTPUT
   ├─ Sort resumes by score (descending)
   ├─ Display ranked results
   ├─ Show detailed analysis for each
   └─ Provide CSV export option
```

## Component Details

### 1. Streamlit UI (app.py)
- **Purpose**: User interface and interaction
- **Responsibilities**:
  - Accept job description input
  - Handle file uploads
  - Display results with color-coded rankings
  - Export functionality
  - API key management

### 2. Resume Screening Agent (resume_agent.py)
- **Purpose**: Core business logic
- **Key Components**:
  - `__init__()`: Initialize OpenAI and ChromaDB clients
  - `extract_text()`: Parse PDF/TXT files
  - `create_vector_store()`: Manage embeddings
  - `score_resume()`: LLM-based analysis
  - `screen_resumes()`: Main orchestration

### 3. ChromaDB Vector Store
- **Purpose**: Semantic search capability
- **Features**:
  - In-memory vector storage
  - Cosine similarity search
  - Fast retrieval
  - Metadata storage

### 4. OpenAI Integration
- **Models Used**:
  - `text-embedding-ada-002`: Generate 1536-dim embeddings
  - `gpt-4`: Detailed resume analysis
- **Via**: LangChain framework

### 5. LangChain Framework
- **Purpose**: LLM orchestration
- **Components**:
  - OpenAIEmbeddings wrapper
  - ChatOpenAI wrapper
  - PromptTemplate for structured prompts

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| UI | Streamlit | Web interface |
| Framework | LangChain | LLM orchestration |
| AI Model | OpenAI GPT-4 | Resume analysis |
| Embeddings | text-embedding-ada-002 | Semantic search |
| Vector DB | ChromaDB | Similarity matching |
| PDF Parser | PyPDF2 | Document processing |
| Data Export | Pandas | CSV generation |

## Security & Configuration

- API keys stored in `.env` file (not committed)
- Environment variables loaded via python-dotenv
- Secure input handling in Streamlit
- No data persistence (privacy-focused)

## Scalability Considerations

**Current Implementation:**
- In-memory ChromaDB (suitable for small batches)
- Synchronous processing
- Single-threaded

**For Production Scale:**
- Persistent ChromaDB with disk storage
- Async processing for multiple resumes
- Batch API calls to reduce latency
- Caching for repeated job descriptions
- Queue system for large volumes
