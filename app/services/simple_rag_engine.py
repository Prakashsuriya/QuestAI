"""
Simplified RAG Engine for Render deployment.
Uses keyword matching instead of vector search to reduce memory usage.
"""
import re
from typing import List, Dict, Any
from app.models import ReferenceDocument

class SimpleRAGEngine:
    """Lightweight RAG engine using keyword matching instead of vector search."""
    
    def __init__(self):
        pass
    
    def answer_question(self, question: str, user_id: int) -> Dict[str, Any]:
        """Generate an answer using simple keyword matching."""
        
        # Get all reference documents for the user
        ref_docs = ReferenceDocument.query.filter_by(user_id=user_id).all()
        
        if not ref_docs:
            return {
                'answer': "Not found in references.",
                'confidence': 0.0,
                'citations': [],
                'evidence_snippets': []
            }
        
        # Extract keywords from question
        question_keywords = set(re.findall(r'\b\w+\b', question.lower()))
        question_keywords = {kw for kw in question_keywords if len(kw) > 3}
        
        if not question_keywords:
            return {
                'answer': "Not found in references.",
                'confidence': 0.0,
                'citations': [],
                'evidence_snippets': []
            }
        
        # Score each document
        doc_scores = []
        for doc in ref_docs:
            content_lower = doc.content.lower()
            matches = sum(1 for kw in question_keywords if kw in content_lower)
            if matches > 0:
                score = matches / len(question_keywords)
                doc_scores.append((doc, score, content_lower))
        
        if not doc_scores:
            return {
                'answer': "Not found in references.",
                'confidence': 0.0,
                'citations': [],
                'evidence_snippets': []
            }
        
        # Sort by score
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Get best document
        best_doc, confidence, content_lower = doc_scores[0]
        
        # Extract relevant sentences
        sentences = re.split(r'(?<=[.!?])\s+', best_doc.content)
        relevant_sentences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            matches = sum(1 for kw in question_keywords if kw in sentence_lower)
            if matches > 0:
                relevant_sentences.append((sentence, matches))
        
        # Sort by relevance
        relevant_sentences.sort(key=lambda x: x[1], reverse=True)
        
        if not relevant_sentences:
            return {
                'answer': "Information found but requires manual review.",
                'confidence': round(confidence * 0.5, 2),
                'citations': [{'document_name': best_doc.original_filename}],
                'evidence_snippets': [{
                    'document_name': best_doc.original_filename,
                    'text': best_doc.content[:300] + "...",
                    'relevance': round(confidence, 2)
                }]
            }
        
        # Build answer
        top_sentences = [s[0] for s in relevant_sentences[:2]]
        answer = " ".join(top_sentences)
        
        return {
            'answer': answer,
            'confidence': round(min(confidence + 0.3, 1.0), 2),
            'citations': [{'document_name': best_doc.original_filename}],
            'evidence_snippets': [{
                'document_name': best_doc.original_filename,
                'text': answer[:300] + "..." if len(answer) > 300 else answer,
                'relevance': round(confidence, 2)
            }]
        }
