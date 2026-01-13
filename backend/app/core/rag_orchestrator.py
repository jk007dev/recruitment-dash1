import logging
import json
from typing import List, Dict, Any
from langgraph.graph import StateGraph
from pydantic import BaseModel
from app.services import (
    get_embedding_service,
    get_vector_store_service,
    get_llm_service,
    get_observability_service
)
from app.models.schemas import MatchResult

logger = logging.getLogger(__name__)

class CVMatchingState(BaseModel):
    """State for CV matching workflow"""
    job_description: str
    job_title: str
    cv_id: str
    cv_text: str
    embedding: List[float] = None
    similar_cvs: List[Dict] = None
    llm_analysis: str = None
    match_result: MatchResult = None
    error: str = None

class RAGOrchestrator:
    """LangGraph-based orchestrator for CV matching RAG pipeline"""
    
    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.vector_store = get_vector_store_service()
        self.observability = get_observability_service()
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        workflow = StateGraph(CVMatchingState)
        
        # Add nodes
        workflow.add_node("embed_jd", self.embed_jd)
        workflow.add_node("retrieve_candidates", self.retrieve_candidates)
        workflow.add_node("analyze_cv", self.analyze_cv)
        workflow.add_node("llm_scoring", self.llm_scoring)
        workflow.add_node("format_result", self.format_result)
        
        # Add edges
        workflow.add_edge("embed_jd", "retrieve_candidates")
        workflow.add_edge("retrieve_candidates", "analyze_cv")
        workflow.add_edge("analyze_cv", "llm_scoring")
        workflow.add_edge("llm_scoring", "format_result")
        
        workflow.set_entry_point("embed_jd")
        workflow.set_finish_point("format_result")
        
        return workflow.compile()
    
    def embed_jd(self, state: CVMatchingState) -> CVMatchingState:
        """Embed job description"""
        try:
            logger.info(f"Embedding JD: {state.job_title}")
            embedding = self.embedding_service.embed_text(
                f"{state.job_title}\n{state.job_description}"
            )
            state.embedding = embedding
            self.observability.log_embedding_generation(
                len(state.job_description), len(embedding)
            )
            return state
        except Exception as e:
            logger.error(f"Error embedding JD: {e}")
            state.error = str(e)
            return state
    
    def retrieve_candidates(self, state: CVMatchingState) -> CVMatchingState:
        """Retrieve similar candidates from vector store"""
        try:
            logger.info(f"Retrieving candidates for JD: {state.job_title}")
            similar = self.vector_store.query_similar(state.embedding, top_k=10)
            state.similar_cvs = [
                {
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                }
                for match in similar
            ]
            return state
        except Exception as e:
            logger.error(f"Error retrieving candidates: {e}")
            state.error = str(e)
            return state
    
    def analyze_cv(self, state: CVMatchingState) -> CVMatchingState:
        """Analyze CV content"""
        try:
            logger.info(f"Analyzing CV: {state.cv_id}")
            # Extract key information from CV
            lines = state.cv_text.split('\n')
            state.cv_text = '\n'.join(lines[:50])  # Limit to first 50 lines for analysis
            return state
        except Exception as e:
            logger.error(f"Error analyzing CV: {e}")
            state.error = str(e)
            return state
    
    def llm_scoring(self, state: CVMatchingState) -> CVMatchingState:
        """Use LLM to score the match"""
        try:
            logger.info(f"Scoring CV match with LLM: {state.cv_id}")
            
            llm = get_llm_service()
            
            prompt = f"""
You are an expert recruiter. Analyze the match between a CV and a job description.

JOB TITLE: {state.job_title}
JOB DESCRIPTION:
{state.job_description}

CV CONTENT:
{state.cv_text}

Provide your analysis in the following JSON format:
{{
    "match_score": <0-1>,
    "reasoning": "<brief reasoning>",
    "matched_skills": [<list of matched skills>],
    "experience_alignment": "<excellent/good/fair/poor>",
    "overall_assessment": "<brief assessment>"
}}

Respond with only the JSON, no additional text.
"""
            
            response = llm.invoke(prompt)
            
            try:
                analysis = json.loads(response)
                state.llm_analysis = analysis
            except json.JSONDecodeError:
                logger.warning("Failed to parse LLM response as JSON")
                state.llm_analysis = {
                    "match_score": 0.5,
                    "reasoning": response,
                    "matched_skills": [],
                    "experience_alignment": "unknown",
                    "overall_assessment": "Analysis incomplete"
                }
            
            return state
        except Exception as e:
            logger.error(f"Error in LLM scoring: {e}")
            state.error = str(e)
            return state
    
    def format_result(self, state: CVMatchingState) -> CVMatchingState:
        """Format the final result"""
        try:
            if state.error:
                return state
            
            analysis = state.llm_analysis or {}
            
            state.match_result = MatchResult(
                cv_id=state.cv_id,
                filename=state.cv_id,
                match_score=float(analysis.get("match_score", 0.0)),
                reasoning=analysis.get("reasoning", ""),
                matched_skills=analysis.get("matched_skills", []),
                experience_alignment=analysis.get("experience_alignment", ""),
                overall_assessment=analysis.get("overall_assessment", "")
            )
            
            self.observability.log_cv_matching(
                state.cv_id,
                state.job_title,
                state.match_result.match_score,
                state.match_result.reasoning
            )
            
            return state
        except Exception as e:
            logger.error(f"Error formatting result: {e}")
            state.error = str(e)
            return state
    
    def process(self, job_description: str, job_title: str, cv_id: str, cv_text: str):
        """Process CV matching workflow"""
        initial_state = CVMatchingState(
            job_description=job_description,
            job_title=job_title,
            cv_id=cv_id,
            cv_text=cv_text
        )
        
        result = self.graph.invoke(initial_state)
        return result

# Global instance
rag_orchestrator = None

def get_rag_orchestrator() -> RAGOrchestrator:
    global rag_orchestrator
    if rag_orchestrator is None:
        rag_orchestrator = RAGOrchestrator()
    return rag_orchestrator
