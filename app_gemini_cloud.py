import streamlit as st
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass  # dotenv not needed in cloud deployment

from resume_agent_gemini import ResumeScreeningAgent
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Resume Screening Agent (Gemini)",
    page_icon="📄",
    layout="wide"
)

# Title and description
st.title("📄 AI Resume Screening Agent (Powered by Gemini)")
st.markdown("Upload resumes and provide a job description to get AI-powered candidate rankings")
st.info("🆓 This version uses Google Gemini API which has a FREE tier!")

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None

# Sidebar for API key
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Try to get API key from environment or secrets first
    default_key = os.getenv("GEMINI_API_KEY", "")
    if not default_key:
        try:
            default_key = st.secrets.get("GEMINI_API_KEY", "")
        except:
            pass
    
    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        value=default_key,
        help="Get your free API key from https://makersuite.google.com/app/apikey"
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This agent uses AI to screen and rank resumes based on job requirements.")
    st.markdown("**Tech Stack:**")
    st.markdown("- Google Gemini Pro (FREE)")
    st.markdown("- Sentence Transformers")
    st.markdown("- ChromaDB")
    st.markdown("- Streamlit")
    
    st.markdown("---")
    st.markdown("### Get Free API Key")
    st.markdown("[Get Gemini API Key →](https://makersuite.google.com/app/apikey)")

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Job Description")
    job_description = st.text_area(
        "Enter the job description",
        height=300,
        placeholder="Paste the job description here...\n\nExample:\nWe are looking for a Senior Python Developer with 5+ years of experience in backend development, strong knowledge of Django/Flask, experience with AWS, and excellent problem-solving skills..."
    )

with col2:
    st.subheader("📎 Upload Resumes")
    uploaded_files = st.file_uploader(
        "Upload resume files (PDF or TXT)",
        type=['pdf', 'txt'],
        accept_multiple_files=True,
        help="Upload one or more resumes to screen"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
        for file in uploaded_files:
            st.text(f"• {file.name}")

# Screen button
st.markdown("---")
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

with col_btn2:
    screen_button = st.button("🚀 Screen Resumes", type="primary", use_container_width=True)

# Process resumes
if screen_button:
    if not api_key:
        st.error("❌ Please provide a Gemini API key in the sidebar")
        st.info("Get your free API key from: https://makersuite.google.com/app/apikey")
    elif not job_description.strip():
        st.error("❌ Please enter a job description")
    elif not uploaded_files:
        st.error("❌ Please upload at least one resume")
    else:
        try:
            # Initialize agent
            agent = ResumeScreeningAgent(api_key)
            
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🔍 Initializing agent...")
            progress_bar.progress(10)
            
            status_text.text(f"📄 Processing {len(uploaded_files)} resume(s)...")
            progress_bar.progress(30)
            
            # Process resumes
            results = agent.screen_resumes(job_description, uploaded_files)
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            
            # Store in session state
            st.session_state.results = results
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            st.success("✅ Screening complete!")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Display results
if st.session_state.results:
    st.markdown("---")
    st.header("📊 Screening Results")
    
    results = st.session_state.results
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Resumes", len(results))
    with col2:
        avg_score = sum(r['score'] for r in results) / len(results)
        st.metric("Average Score", f"{avg_score:.1f}")
    with col3:
        top_score = max(r['score'] for r in results)
        st.metric("Top Score", f"{top_score:.1f}")
    with col4:
        qualified = sum(1 for r in results if r['score'] >= 70)
        st.metric("Qualified (≥70)", qualified)
    
    st.markdown("---")
    
    # Detailed results
    for idx, result in enumerate(results, 1):
        score = result['score']
        
        # Color coding based on score
        if score >= 80:
            color = "🟢"
            badge_color = "green"
        elif score >= 60:
            color = "🟡"
            badge_color = "orange"
        else:
            color = "🔴"
            badge_color = "red"
        
        with st.expander(f"{color} **Rank #{idx}: {result['filename']}** - Score: {score}/100", expanded=(idx <= 3)):
            col_a, col_b = st.columns([2, 1])
            
            with col_a:
                st.markdown("**📝 Analysis:**")
                st.write(result['reasoning'])
            
            with col_b:
                st.markdown(f"**Score:** :{badge_color}[{score}/100]")
                st.markdown(f"**Rank:** #{idx}")
                st.markdown(f"**File:** {result['filename']}")
    
    # Export option
    st.markdown("---")
    col_export1, col_export2, col_export3 = st.columns([1, 1, 1])
    
    with col_export2:
        # Create DataFrame for export
        df = pd.DataFrame([
            {
                'Rank': idx,
                'Filename': r['filename'],
                'Score': r['score'],
                'Reasoning': r['reasoning']
            }
            for idx, r in enumerate(results, 1)
        ])
        
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Results (CSV)",
            data=csv,
            file_name="resume_screening_results.csv",
            mime="text/csv",
            use_container_width=True
        )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>Built with ❤️ using Google Gemini, Sentence Transformers, ChromaDB & Streamlit</div>",
    unsafe_allow_html=True
)
