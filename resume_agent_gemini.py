import os
from typing import List, Dict
import chromadb
from sentence_transformers import SentenceTransformer
import PyPDF2
import io
import google.generativeai as genai
import time

class ResumeScreeningAgent:
    """AI Agent for screening and ranking resumes using Google Gemini (Free tier available)"""
    
    def __init__(self, api_key: str):
        """Initialize the resume screening agent with Gemini"""
        self.api_key = api_key
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        # Use gemini-2.0-flash for higher free tier limits
        self.llm = genai.GenerativeModel('models/gemini-2.0-flash')
        
        # Initialize sentence transformer for embeddings (free, runs locally)
        self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.Client()
    
    def extract_text_from_pdf(self, file) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def extract_text_from_txt(self, file) -> str:
        """Extract text from TXT file"""
        try:
            return file.read().decode('utf-8')
        except Exception as e:
            raise Exception(f"Error reading TXT: {str(e)}")
    
    def extract_text(self, file) -> str:
        """Extract text from uploaded file"""
        filename = file.name.lower()
        
        if filename.endswith('.pdf'):
            return self.extract_text_from_pdf(file)
        elif filename.endswith('.txt'):
            return self.extract_text_from_txt(file)
        else:
            raise ValueError(f"Unsupported file type: {filename}")
    
    def create_vector_store(self, resumes: List[Dict[str, str]]):
        """Create vector store from resumes"""
        # Create or get collection
        try:
            self.chroma_client.delete_collection("resumes")
        except:
            pass
        
        collection = self.chroma_client.create_collection(
            name="resumes",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Add resumes to collection
        for idx, resume in enumerate(resumes):
            # Generate embedding using sentence transformer
            embedding = self.embeddings_model.encode(resume['text']).tolist()
            
            # Add to collection
            collection.add(
                embeddings=[embedding],
                documents=[resume['text']],
                metadatas=[{"filename": resume['filename']}],
                ids=[f"resume_{idx}"]
            )
        
        return collection
    
    def score_resume(self, job_description: str, resume_text: str, filename: str) -> Dict:
        """Score a single resume using Gemini with retry logic"""
        
        prompt = f"""You are an expert HR recruiter. Analyze the following resume against the job description and provide a detailed assessment.

Job Description:
{job_description}

Resume:
{resume_text[:4000]}

Provide your analysis in the following format:
1. Overall Score (0-100): [Your score]
2. Key Strengths: [List 2-3 key strengths]
3. Relevant Skills Match: [How well skills match]
4. Experience Relevance: [How relevant is the experience]
5. Gaps or Concerns: [Any concerns or missing qualifications]
6. Recommendation: [Hire/Interview/Reject with brief reason]

Be specific and objective in your assessment."""
        
        # Retry logic for rate limiting
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                # Get Gemini response
                response = self.llm.generate_content(prompt)
                analysis = response.text
                
                # Extract score from response
                score = self._extract_score(analysis)
                
                # Add delay between requests to avoid rate limiting
                time.sleep(1)
                
                return {
                    'filename': filename,
                    'score': score,
                    'reasoning': analysis
                }
            except Exception as e:
                error_msg = str(e)
                
                # Check if it's a rate limit error
                if '429' in error_msg or 'quota' in error_msg.lower():
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (attempt + 1)
                        print(f"Rate limit hit for {filename}, waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return {
                            'filename': filename,
                            'score': 50,
                            'reasoning': f"Rate limit exceeded after {max_retries} attempts. Please wait a moment and try again, or check your API quota at https://ai.dev/usage"
                        }
                else:
                    # Other errors
                    return {
                        'filename': filename,
                        'score': 50,
                        'reasoning': f"Error analyzing resume: {error_msg}"
                    }
        
        return {
            'filename': filename,
            'score': 50,
            'reasoning': "Failed to analyze resume after multiple attempts"
        }
    
    def _extract_score(self, analysis: str) -> int:
        """Extract numerical score from LLM analysis"""
        try:
            # Look for score in format "Score (0-100): XX" or "Score: XX"
            lines = analysis.split('\n')
            for line in lines:
                if 'score' in line.lower() and ':' in line:
                    # Extract number
                    parts = line.split(':')[1].strip()
                    # Get first number found
                    import re
                    numbers = re.findall(r'\d+', parts)
                    if numbers:
                        score = int(numbers[0])
                        return min(max(score, 0), 100)  # Clamp between 0-100
            
            # Default score if not found
            return 50
        except:
            return 50
    
    def screen_resumes(self, job_description: str, uploaded_files) -> List[Dict]:
        """Main method to screen and rank resumes"""
        
        # Extract text from all resumes
        resumes = []
        for file in uploaded_files:
            try:
                text = self.extract_text(file)
                resumes.append({
                    'filename': file.name,
                    'text': text
                })
                # Reset file pointer for potential re-reading
                file.seek(0)
            except Exception as e:
                print(f"Error processing {file.name}: {str(e)}")
                continue
        
        if not resumes:
            raise ValueError("No valid resumes to process")
        
        # Create vector store
        collection = self.create_vector_store(resumes)
        
        # Generate embedding for job description
        job_embedding = self.embeddings_model.encode(job_description).tolist()
        
        # Query similar resumes (get all, we'll score them all)
        results = collection.query(
            query_embeddings=[job_embedding],
            n_results=len(resumes)
        )
        
        # Score each resume with Gemini
        scored_resumes = []
        for resume in resumes:
            score_result = self.score_resume(
                job_description,
                resume['text'],
                resume['filename']
            )
            scored_resumes.append(score_result)
        
        # Sort by score (descending)
        scored_resumes.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_resumes
