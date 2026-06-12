"""Multi-Agent System for complex query reasoning"""
from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService
from typing import List, Dict, Optional
import logging
import json

logger = logging.getLogger(__name__)

class PlannerAgent:
    """Plans how to approach complex queries"""
    
    def __init__(self):
        self.llm = LLMService()
        logger.info("PlannerAgent initialized")
    
    def plan(self, query: str) -> Dict:
        """
        Break down complex query into sub-tasks
        
        Args:
            query: Original query
            
        Returns:
            Plan with subtasks and strategy
        """
        prompt = f"""Analyze the following user query and create a plan to answer it.
        
User Query: {query}

Create a JSON response with:
1. query_type: 'definition', 'procedure', 'comparison', 'scenario', 'general'
2. subtasks: List of specific subtasks to answer the query
3. key_concepts: Important concepts to look for
4. expected_length: 'short', 'medium', 'long'
5. complexity: 'simple', 'moderate', 'complex'

Respond with valid JSON only."""
        
        try:
            response = self.llm.generate_quick_response(prompt, max_tokens=800)
            
            # Parse JSON response
            try:
                plan = json.loads(response)
            except:
                # Fallback if JSON parsing fails
                plan = {
                    "query_type": "general",
                    "subtasks": ["Search knowledge base", "Generate answer"],
                    "key_concepts": [],
                    "expected_length": "medium",
                    "complexity": "simple"
                }
            
            logger.info(f"Query plan created: type={plan.get('query_type')}, subtasks={len(plan.get('subtasks', []))}")
            return plan
            
        except Exception as e:
            logger.error(f"Error in planner: {str(e)}")
            return {
                "query_type": "general",
                "subtasks": ["Retrieve documents", "Generate answer"],
                "key_concepts": [],
                "expected_length": "medium",
                "complexity": "simple"
            }


class RetrieverAgent:
    """Retrieves relevant documents for each subtask"""
    
    def __init__(self):
        self.retrieval = RetrievalService()
        logger.info("RetrieverAgent initialized")
    
    def retrieve(self, task: str, query: str, top_k: int = 5) -> Dict:
        """
        Retrieve documents for a specific task
        
        Args:
            task: Specific task/subtask
            query: Original or enhanced query
            top_k: Number of documents to retrieve
            
        Returns:
            Retrieved documents and metadata
        """
        try:
            # Enhance query with task context
            enhanced_query = f"{query} {task}".strip()
            
            results = self.retrieval.search(enhanced_query, top_k=top_k)
            
            logger.info(f"Retrieved {results.get('filtered_count', 0)} documents for task: {task}")
            return results
            
        except Exception as e:
            logger.error(f"Error in retriever: {str(e)}")
            return {"documents": [[]], "metadatas": [[]]}


class ReasoningAgent:
    """Reasons about retrieved information"""
    
    def __init__(self):
        self.llm = LLMService()
        logger.info("ReasoningAgent initialized")
    
    def reason(self, task: str, documents: List[str]) -> Dict:
        """
        Reason about documents and extract insights
        
        Args:
            task: Task/subtask to reason about
            documents: Retrieved documents
            
        Returns:
            Reasoning output with key insights
        """
        if not documents:
            return {"insights": [], "analysis": "No documents to analyze"}
        
        doc_text = "\n\n".join([f"[DOC {i+1}] {doc[:500]}" for i, doc in enumerate(documents)])
        
        prompt = f"""Analyze the following documents to address this task:
Task: {task}

Documents:
{doc_text}

Provide analysis in JSON format with:
1. key_insights: Main findings
2. contradictions: Any conflicting information
3. confidence: Overall confidence in the documents (0-1)
4. gaps: Missing information
5. summary: Brief summary of findings

Respond with valid JSON only."""
        
        try:
            response = self.llm.generate_quick_response(prompt, max_tokens=1000)
            
            try:
                analysis = json.loads(response)
            except:
                analysis = {
                    "key_insights": [],
                    "contradictions": [],
                    "confidence": 0.7,
                    "gaps": [],
                    "summary": response
                }
            
            logger.info(f"Reasoning complete: confidence={analysis.get('confidence', 0)}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in reasoning: {str(e)}")
            return {"insights": [], "analysis": "Error during reasoning"}


class ResponseAgent:
    """Generates final response"""
    
    def __init__(self):
        self.llm = LLMService()
        logger.info("ResponseAgent initialized")
    
    def generate(
        self,
        query: str,
        context: str,
        reasoning: Optional[Dict] = None,
        style: str = "professional"
    ) -> Dict:
        """
        Generate final response
        
        Args:
            query: Original query
            context: Formatted context from retrieval
            reasoning: Reasoning analysis (optional)
            style: Response style ('professional', 'casual', 'technical')
            
        Returns:
            Final response with answer and metadata
        """
        try:
            # Adjust system prompt based on style
            styles = {
                "professional": """You are AlphaResearch Assistant, a production-grade knowledge assistant for Indian broking operations.

Answer like a senior brokerage operations and compliance analyst.
Use only the supplied context. If the context is insufficient, say what is missing.
Write in polished research-note format:
- Use short descriptive Markdown section headings.
- Use numbered sections for comparisons or workflows.
- Use bullets for controls, risks, documents, and action items.
- Keep paragraphs concise and executive-ready.
Do not expose chunk labels or internal retrieval wording.
Cite source filenames naturally, for example: Source: SOPs.md.
Do not provide personalized investment, legal, or tax advice.""",
                "casual": "You are AlphaResearch Assistant. Use clear conversational language while staying grounded in the supplied context.",
                "technical": "You are AlphaResearch Assistant. Provide detailed technical explanations grounded in the supplied context."
            }
            
            system_prompt = styles.get(style, styles["professional"])
            
            answer = self.llm.generate_with_context(
                question=query,
                context=context,
                system_prompt=system_prompt,
                max_tokens=2000
            )
            
            # Prepare confidence based on reasoning
            confidence = 0.8
            if reasoning:
                confidence = min(
                    reasoning.get('confidence', 0.8),
                    1.0 - (len(reasoning.get('gaps', [])) * 0.05)
                )
            
            return {
                "answer": answer,
                "confidence": confidence,
                "style": style,
                "reasoning_considered": reasoning is not None
            }
            
        except Exception as e:
            logger.error(f"Error in response generation: {str(e)}")
            return {
                "answer": f"Unable to generate response: {str(e)}",
                "confidence": 0.0,
                "style": style,
                "error": str(e)
            }


class MultiAgentOrchestrator:
    """Orchestrates multi-agent system"""
    
    def __init__(self):
        self.planner = PlannerAgent()
        self.retriever = RetrieverAgent()
        self.reasoner = ReasoningAgent()
        self.responder = ResponseAgent()
        logger.info("MultiAgentOrchestrator initialized")
    
    def execute(
        self,
        query: str,
        enable_reasoning: bool = True,
        top_k: int = 5
    ) -> Dict:
        """
        Execute full multi-agent pipeline
        
        Args:
            query: User query
            enable_reasoning: Whether to enable reasoning agent
            top_k: Number of documents to retrieve
            
        Returns:
            Final response with all metadata
        """
        try:
            logger.info(f"Starting multi-agent execution for: {query[:100]}")
            
            # Step 1: Plan
            plan = self.planner.plan(query)
            logger.info(f"Plan created: {plan.get('complexity')} query")
            
            # Step 2: Retrieve for main query
            planned_subtasks = plan.get('subtasks', ['General retrieval'])
            subtasks = [query] + [task for task in planned_subtasks if task != query]
            all_documents = []
            all_sources = []
            all_pairs = []
            all_results = []
            
            for subtask in subtasks[:3]:  # Limit to 3 subtasks for efficiency
                results = self.retriever.retrieve(subtask, query, top_k)
                docs = results.get('documents', [[]])[0] if results.get('documents') else []
                metadatas = results.get('metadatas', [[]])[0] if results.get('metadatas') else []
                all_documents.extend(docs)
                all_sources.extend(self._format_source(meta) for meta in metadatas)
                all_pairs.extend(zip(docs, metadatas))
                all_results.append({
                    "subtask": subtask,
                    "document_count": len(docs)
                })
            
            # Remove duplicates while preserving order
            unique_docs = []
            unique_pairs = []
            seen = set()
            for doc, metadata in all_pairs:
                if doc[:100] not in seen:
                    unique_docs.append(doc)
                    unique_pairs.append((doc, metadata))
                    seen.add(doc[:100])
            
            unique_docs = unique_docs[:top_k]
            unique_pairs = unique_pairs[:top_k]
            logger.info(f"Retrieved {len(unique_docs)} unique documents")
            
            # Step 3: Reason (optional)
            reasoning_analysis = None
            if enable_reasoning and unique_docs:
                reasoning_analysis = self.reasoner.reason(
                    query,
                    unique_docs
                )
                logger.info(f"Reasoning complete: {reasoning_analysis.get('confidence', 0)}")
            
            # Step 4: Generate response
            context = "\n\n".join([
                f"Source: {self._format_source(metadata)}\n{self._clean_context(doc[:1400])}"
                for i, (doc, metadata) in enumerate(unique_pairs)
            ])
            response = self.responder.generate(
                query,
                context,
                reasoning_analysis
            )
            
            return {
                "question": query,
                "answer": response.get('answer'),
                "sources": list(dict.fromkeys(all_sources))[:top_k],
                "confidence": response.get('confidence'),
                "plan": plan,
                "retrieval_summary": all_results,
                "reasoning": reasoning_analysis,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error in multi-agent execution: {str(e)}")
            return {
                "question": query,
                "answer": None,
                "error": str(e),
                "status": "failed"
            }

    def _clean_context(self, text: str) -> str:
        """Remove markdown noise before sending snippets to the response model."""
        import re

        text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
        text = text.replace("**", "")
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _format_source(self, metadata: Dict) -> str:
        """Format official provenance if present, otherwise local filename."""
        if metadata.get("source_url") or metadata.get("circular_no") or metadata.get("exchange"):
            parts = [
                metadata.get("exchange", "").strip(),
                metadata.get("circular_no", "").strip(),
                metadata.get("date", "").strip(),
                metadata.get("section", "").strip(),
            ]
            label = " | ".join(part for part in parts if part)
            title = metadata.get("source", "").strip()
            url = metadata.get("source_url", "").strip()
            if title and label:
                label = f"{title} ({label})"
            else:
                label = title or label
            return f"{label} - {url}" if url else label

        return metadata.get("source", "unknown")
