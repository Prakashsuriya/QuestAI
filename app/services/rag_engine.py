import os
import re
from typing import List, Dict, Any
import openai
from app.services.vector_store import VectorStore
from app.models import ReferenceDocument

class RAGEngine:
    """Retrieval-Augmented Generation engine for answering questions."""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
        self.vector_store = VectorStore()
        
        # Confidence thresholds
        self.HIGH_CONFIDENCE = 0.8
        self.MEDIUM_CONFIDENCE = 0.5
        self.LOW_CONFIDENCE = 0.1  # Lowered threshold to allow more answers
    
    def answer_question(self, question: str, user_id: int) -> Dict[str, Any]:
        """Generate an answer for a question using RAG."""
        
        # Step 1: Retrieve relevant documents
        retrieved_docs = self.vector_store.search(question, user_id, n_results=5)
        
        if not retrieved_docs:
            return {
                'answer': "Not found in references.",
                'confidence': 0.0,
                'citations': [],
                'evidence_snippets': []
            }
        
        # Step 2: Calculate confidence based on retrieval quality
        confidence = self._calculate_confidence(retrieved_docs, question)
        
        # Step 3: Extract citations and evidence
        citations = self._extract_citations(retrieved_docs)
        evidence_snippets = self._extract_evidence(retrieved_docs, question)
        
        # Step 4: Generate answer using LLM or fallback
        if confidence < self.LOW_CONFIDENCE:
            # Low confidence - return not found but still show evidence
            return {
                'answer': "Not found in references.",
                'confidence': confidence,
                'citations': [],
                'evidence_snippets': evidence_snippets[:2]
            }
        
        # Generate answer based on retrieved content
        if self.api_key and self.api_key != 'your-openai-api-key-here':
            context = self._prepare_context(retrieved_docs)
            answer = self._generate_with_llm(question, context)
        else:
            answer = self._generate_without_llm(question, retrieved_docs)
        
        return {
            'answer': answer,
            'confidence': confidence,
            'citations': citations,
            'evidence_snippets': evidence_snippets
        }
    
    def _calculate_confidence(self, docs: List[Dict], question: str) -> float:
        """Calculate confidence score based on retrieval quality."""
        if not docs:
            return 0.0
        
        # ChromaDB returns cosine distances (range 0-2)
        # Convert distance to similarity score (0-1)
        similarities = []
        for doc in docs:
            distance = doc.get('distance', 1.0)
            # Cosine distance to similarity: 1 - (distance / 2)
            similarity = 1 - (distance / 2)
            similarity = max(0, min(1, similarity))  # Clamp between 0 and 1
            similarities.append(similarity)
        
        # Average similarity of top 3 results
        top_similarities = sorted(similarities, reverse=True)[:3]
        avg_similarity = sum(top_similarities) / len(top_similarities) if top_similarities else 0
        
        # Check if question keywords appear in retrieved documents
        question_keywords = set(re.findall(r'\b\w+\b', question.lower()))
        # Filter out short words
        question_keywords = {kw for kw in question_keywords if len(kw) > 3}
        
        if not question_keywords:
            question_keywords = set(re.findall(r'\b\w+\b', question.lower()))
        
        keyword_matches = 0
        total_keywords = len(question_keywords) if question_keywords else 1
        
        for doc in docs[:2]:
            doc_text = doc.get('text', '').lower()
            matches = sum(1 for keyword in question_keywords if keyword in doc_text)
            keyword_matches += matches / total_keywords
        
        keyword_score = min(keyword_matches / 2, 1.0)  # Normalize to max 1.0
        
        # Combined score - give more weight to keyword matching for better results
        confidence = (avg_similarity * 0.5) + (keyword_score * 0.5)
        
        # Ensure minimum confidence if we have any results
        if confidence < 0.15 and avg_similarity > 0.3:
            confidence = 0.15
        
        return round(min(confidence, 1.0), 2)
    
    def _prepare_context(self, docs: List[Dict]) -> str:
        """Prepare context from retrieved documents."""
        context_parts = []
        for i, doc in enumerate(docs[:3], 1):
            text = doc.get('text', '')
            metadata = doc.get('metadata', {})
            filename = metadata.get('filename', 'Unknown')
            
            context_parts.append(f"[Document {i}: {filename}]\n{text}\n")
        
        return "\n".join(context_parts)
    
    def _generate_with_llm(self, question: str, context: str) -> str:
        """Generate answer using OpenAI API."""
        try:
            prompt = f"""Based on the following reference documents, please answer the question. 
If the information is not found in the references, respond with "Not found in references."

Reference Documents:
{context}

Question: {question}

Provide a clear, concise answer based only on the information in the references above."""

            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided reference documents. Always cite your sources and be concise."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content.strip()
            return answer
            
        except Exception as e:
            print(f"LLM generation error: {e}")
            return self._generate_without_llm(question, [{'text': context}])
    
    def _generate_without_llm(self, question: str, docs: List[Dict]) -> str:
        """Generate answer without LLM using simple extraction."""
        # Combine text from all retrieved docs
        combined_text = ""
        for doc in docs[:2]:  # Use top 2 docs
            text = doc.get('text', '')
            combined_text += text + " "
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', combined_text)
        
        # Find sentences most relevant to the question
        question_keywords = set(re.findall(r'\b\w+\b', question.lower()))
        relevant_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:  # Skip very short sentences
                continue
            sentence_lower = sentence.lower()
            score = sum(2 for keyword in question_keywords if keyword in sentence_lower and len(keyword) > 3)
            # Bonus for sentences that look like answers (contain specific info)
            if any(word in sentence_lower for word in ['is', 'are', 'uses', 'provides', 'requires', 'encrypted', 'authenticated']):
                score += 1
            if score > 0:
                relevant_sentences.append((sentence, score))
        
        # Sort by relevance and return top sentences
        relevant_sentences.sort(key=lambda x: x[1], reverse=True)
        
        if relevant_sentences:
            # Take the best sentence or combine top 2 if they're different
            if len(relevant_sentences) >= 2 and relevant_sentences[0][1] > relevant_sentences[1][1] * 1.5:
                return relevant_sentences[0][0]
            else:
                top_sentences = [s[0] for s in relevant_sentences[:2]]
                return " ".join(top_sentences)
        
        return "Information found in references but requires manual review."
    
    def _extract_citations(self, docs: List[Dict]) -> List[Dict[str, Any]]:
        """Extract citation information from retrieved documents."""
        citations = []
        seen_docs = set()
        
        for doc in docs[:3]:
            metadata = doc.get('metadata', {})
            filename = metadata.get('filename', 'Unknown')
            
            if filename not in seen_docs:
                citations.append({
                    'document_name': filename,
                    'page': metadata.get('page_number'),
                    'section': metadata.get('section')
                })
                seen_docs.add(filename)
        
        return citations
    
    def _extract_evidence(self, docs: List[Dict], question: str) -> List[Dict[str, Any]]:
        """Extract evidence snippets from retrieved documents."""
        snippets = []
        question_keywords = set(re.findall(r'\b\w+\b', question.lower()))
        
        for doc in docs[:3]:
            metadata = doc.get('metadata', {})
            text = doc.get('text', '')
            filename = metadata.get('filename', 'Unknown')
            
            # Calculate relevance score
            text_lower = text.lower()
            matches = sum(1 for keyword in question_keywords if keyword in text_lower and len(keyword) > 3)
            relevance = min(matches / max(len(question_keywords), 1), 1.0)
            
            # Truncate text if too long
            snippet_text = text[:500] + "..." if len(text) > 500 else text
            
            snippets.append({
                'document_name': filename,
                'text': snippet_text,
                'relevance': round(relevance, 2)
            })
        
        # Sort by relevance
        snippets.sort(key=lambda x: x['relevance'], reverse=True)
        
        return snippets[:3]
