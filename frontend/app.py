import streamlit as st
import pandas as pd
from services.api_client import APIClient
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="CV Matching Dashboard",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if "api_client" not in st.session_state:
    st.session_state.api_client = APIClient()

if "uploaded_cvs" not in st.session_state:
    st.session_state.uploaded_cvs = []

if "matching_results" not in st.session_state:
    st.session_state.matching_results = None

# Header
st.title("📋 CV Matching Dashboard")
st.markdown("Intelligent CV matching powered by RAG and LLMs")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Backend status
    if st.session_state.api_client.health_check():
        st.success("✅ Backend Connected")
    else:
        st.error("❌ Backend Disconnected")
    
    # LLM Provider selection
    llm_provider = st.selectbox(
        "Select LLM Provider",
        options=["openai", "claude", "grok"],
        help="Choose the LLM for CV analysis"
    )
    
    # Top K results
    top_k = st.slider(
        "Number of Top Matches",
        min_value=1,
        max_value=20,
        value=5,
        help="How many top matching CVs to return"
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This dashboard uses:
    - **LangGraph** for orchestration
    - **Pinecone** for vector storage
    - **LLMs** for decision making
    - **Langfuse** for observability
    """)

# Main content
tab1, tab2, tab3 = st.tabs(["📤 Upload CVs", "🔍 Match", "📊 Results"])

# Tab 1: Upload CVs
with tab1:
    st.header("Upload CVs")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_files = st.file_uploader(
            "Upload CV files (PDF, DOCX, or TXT)",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            help="Select one or more CV files"
        )
    
    with col2:
        if st.button("Upload Selected", type="primary"):
            if uploaded_files:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, file in enumerate(uploaded_files):
                    status_text.text(f"Uploading {file.name}...")
                    
                    # Save file temporarily
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file.name) as tmp:
                        tmp.write(file.getbuffer())
                        tmp_path = tmp.name
                    
                    # Upload to backend
                    result = st.session_state.api_client.upload_cv(
                        cv_id=file.name.replace(".", "_"),
                        file_path=tmp_path
                    )
                    
                    if "error" not in result:
                        st.session_state.uploaded_cvs.append({
                            "filename": file.name,
                            "cv_id": file.name.replace(".", "_"),
                            "uploaded_at": datetime.now()
                        })
                        st.success(f"✅ {file.name} uploaded")
                    else:
                        st.error(f"❌ Error uploading {file.name}: {result.get('error')}")
                    
                    progress_bar.progress((idx + 1) / len(uploaded_files))
    
    # Display uploaded CVs
    if st.session_state.uploaded_cvs:
        st.subheader("Uploaded CVs")
        df = pd.DataFrame(st.session_state.uploaded_cvs)
        st.dataframe(df, use_container_width=True, hide_index=True)

# Tab 2: Match CVs
with tab2:
    st.header("Match CVs Against Job Description")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        job_title = st.text_input(
            "Job Title",
            placeholder="e.g., Senior Python Developer",
            help="Title of the position"
        )
    
    with col2:
        required_skills_input = st.text_input(
            "Required Skills (comma-separated)",
            placeholder="Python, FastAPI, Docker",
            help="Optional: Skills required for the position"
        )
    
    job_description = st.text_area(
        "Job Description",
        placeholder="Enter the complete job description here...",
        height=300,
        help="Paste the full job description"
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        match_button = st.button("🔍 Find Matching CVs", type="primary", use_container_width=True)
    
    with col2:
        if st.button("📋 Clear", use_container_width=True):
            st.rerun()
    
    # Perform matching
    if match_button:
        if not job_title or not job_description:
            st.error("Please fill in Job Title and Job Description")
        elif not st.session_state.uploaded_cvs:
            st.error("Please upload at least one CV first")
        else:
            with st.spinner("🔄 Matching CVs..."):
                required_skills = [s.strip() for s in required_skills_input.split(",")] if required_skills_input else None
                
                result = st.session_state.api_client.match_cvs(
                    jd={
                        "job_title": job_title,
                        "job_description": job_description,
                        "required_skills": required_skills
                    },
                    cv_ids=[cv["cv_id"] for cv in st.session_state.uploaded_cvs],
                    llm_provider=llm_provider,
                    top_k=top_k
                )
                
                if "error" in result:
                    st.error(f"Matching failed: {result['error']}")
                else:
                    st.session_state.matching_results = result
                    st.success("✅ Matching completed!")

# Tab 3: Results
with tab3:
    st.header("Matching Results")
    
    if st.session_state.matching_results is None:
        st.info("👈 Run a matching from the 'Match' tab to see results here")
    else:
        results = st.session_state.matching_results
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Job Title", results.get("job_title", "N/A"))
        with col2:
            st.metric("Total Matches", results.get("total_cvs_matched", 0))
        with col3:
            if results.get("matches"):
                top_score = max([m.get("match_score", 0) for m in results.get("matches", [])])
                st.metric("Best Match Score", f"{top_score:.2%}")
        
        st.markdown("---")
        
        # Display matches
        if results.get("matches"):
            st.subheader("Top Matching CVs")
            
            for idx, match in enumerate(results.get("matches", []), 1):
                with st.expander(
                    f"#{idx} - {match.get('filename')} - {match.get('match_score', 0):.1%} Match",
                    expanded=(idx == 1)
                ):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Match Score", f"{match.get('match_score', 0):.1%}")
                    with col2:
                        st.metric("Experience", match.get('experience_alignment', 'N/A'))
                    with col3:
                        st.metric("CV ID", match.get('cv_id', 'N/A'))
                    
                    st.markdown("**Reasoning:**")
                    st.write(match.get('reasoning', 'N/A'))
                    
                    st.markdown("**Matched Skills:**")
                    if match.get('matched_skills'):
                        cols = st.columns(len(match.get('matched_skills', [])))
                        for col, skill in zip(cols, match.get('matched_skills', [])):
                            with col:
                                st.tag(skill)
                    else:
                        st.write("No specific skills matched")
                    
                    st.markdown("**Overall Assessment:**")
                    st.write(match.get('overall_assessment', 'N/A'))
        else:
            st.warning("No matches found. Try adjusting the job description or uploading more CVs.")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
    <p>CV Matching Dashboard v1.0 | Powered by RAG & LLMs</p>
    </div>
    """, unsafe_allow_html=True)
