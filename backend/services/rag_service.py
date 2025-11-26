
import os
from typing import List, Dict, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from services.embedding_service import get_embedding_service
import json
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RAGService:

    
    def __init__(self):
        # Initialize Groq LLM
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        # Remove quotes if present
        groq_api_key = groq_api_key.strip('"').strip("'")
        
        self.llm = ChatGroq(
            api_key=groq_api_key,
            model="llama-3.3-70b-versatile",  # Updated to current supported model
            temperature=0.7
        )
    
    def generate_summary(self, subject: str, unit: str, chapter: Optional[str] = None) -> Dict:

        embedding_service = get_embedding_service()
        
        # Get all documents content
        content = embedding_service.get_all_documents_content(subject, unit)
        
        if not content:
            return {
                "status": "error",
                "message": "No content found for this subject/unit"
            }
        
        # Limit content size (first 15000 characters to avoid token limits)
        if len(content) > 15000:
            content = content[:15000] + "..."
        
        # Summary prompt
        prompt = PromptTemplate(
            input_variables=["content"],
            template="""You are an expert educator. Summarize the following educational content into a structured, note-wise format with clear bullet points.

Content:
{content}

Create a comprehensive summary with:
1. Main topics and concepts
2. Key definitions and terminology
3. Important formulas or principles (if applicable)
4. Examples and applications

Format the summary with clear headings and bullet points for easy study."""
        )
        
        # Create chain using LCEL
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            result = chain.invoke({"content": content})
            
            return {
                "status": "success",
                "subject": subject,
                "unit": unit,
                "summary": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error generating summary: {str(e)}"
            }
    
    def generate_mcqs(self, subject: str, unit: str, count: int = 10, previous_questions: list = None) -> Dict:

        embedding_service = get_embedding_service()
        
        # Get all documents content
        content = embedding_service.get_all_documents_content(subject, unit)
        
        if not content:
            return {
                "status": "error",
                "message": "No content found for this subject/unit"
            }
        
        # Limit content size
        if len(content) > 12000:
            content = content[:12000] + "..."
        
        # Build previous questions context
        previous_context = ""
        if previous_questions and len(previous_questions) > 0:
            previous_context = "\n\nPREVIOUSLY ASKED QUESTIONS (DO NOT REPEAT OR CREATE SIMILAR QUESTIONS):\n"
            for i, pq in enumerate(previous_questions, 1):
                previous_context += f"{i}. {pq}\n"
            previous_context += "\nIMPORTANT: Create questions on DIFFERENT topics/concepts than the above questions.\n"
        
        # MCQ prompt
        prompt = PromptTemplate(
            input_variables=["content", "count", "previous_context"],
            template="""You are an expert educator creating diverse multiple choice questions. Based on the following educational content, create {count} multiple choice questions that cover DIFFERENT topics and concepts from across the entire content.

Content:
{content}
{previous_context}
IMPORTANT INSTRUCTIONS:
1. Cover DIVERSE topics - each question should test a different concept or area from the content
2. If previous questions are provided above, ensure your new questions cover COMPLETELY DIFFERENT topics
3. Vary difficulty levels - include easy, medium, and challenging questions
4. Use different question types:
   - Factual recall ("What is...?", "Which of the following...?")
   - Conceptual understanding ("Why does...?", "How does...?")
   - Application-based ("In which scenario...?", "What would happen if...?")
   - Analysis ("Compare...", "What is the relationship between...?")
5. Ensure NO repetitive or similar questions
6. Make all distractors (wrong options) plausible but clearly incorrect

For each question, provide:
1. The question text
2. Four options (A, B, C, D)
3. The correct answer (A, B, C, or D)
4. A brief explanation

Format each MCQ as follows:
Question X: [question text]
A) [option A]
B) [option B]
C) [option C]
D) [option D]
Correct Answer: [A/B/C/D]
Explanation: [brief explanation]

---

Create {count} DIVERSE questions covering DIFFERENT concepts and topics from the entire content."""
        )
        
        # Create chain using LCEL
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            result = chain.invoke({"content": content, "count": count, "previous_context": previous_context})
            
            # Parse MCQs
            mcqs = self._parse_mcqs(result)
            
            return {
                "status": "success",
                "subject": subject,
                "unit": unit,
                "count": len(mcqs),
                "mcqs": mcqs
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error generating MCQs: {str(e)}"
            }
    
    def _parse_mcqs(self, mcq_text: str) -> List[Dict]:

        mcqs = []
        
        # Split by question separator
        questions = mcq_text.split("---")
        
        for q_text in questions:
            if not q_text.strip():
                continue
            
            # Extract question
            question_match = re.search(r'Question \d+:\s*(.+?)(?=\n[A-D]\))', q_text, re.DOTALL)
            if not question_match:
                continue
            
            question = question_match.group(1).strip()
            
            # Extract options
            options = {}
            for letter in ['A', 'B', 'C', 'D']:
                option_match = re.search(rf'{letter}\)\s*(.+?)(?=\n[A-D]\)|Correct Answer|$)', q_text, re.DOTALL)
                if option_match:
                    options[letter] = option_match.group(1).strip()
            
            # Extract correct answer
            answer_match = re.search(r'Correct Answer:\s*([A-D])', q_text)
            correct_answer = answer_match.group(1) if answer_match else "A"
            
            # Extract explanation
            explanation_match = re.search(r'Explanation:\s*(.+?)(?=\n---|\Z)', q_text, re.DOTALL)
            explanation = explanation_match.group(1).strip() if explanation_match else ""
            
            if question and len(options) == 4:
                mcqs.append({
                    "question": question,
                    "options": options,
                    "correct_answer": correct_answer,
                    "explanation": explanation
                })
        
        return mcqs
    
    def generate_flashcards(self, subject: str, unit: str, count: int = 10, previous_cards: list = None) -> Dict:

        embedding_service = get_embedding_service()
        
        # Get all documents content
        content = embedding_service.get_all_documents_content(subject, unit)
        
        if not content:
            return {
                "status": "error",
                "message": "No content found for this subject/unit"
            }
        
        # Limit content size
        if len(content) > 12000:
            content = content[:12000] + "..."
        
        # Build previous cards context
        previous_context = ""
        if previous_cards and len(previous_cards) > 0:
            previous_context = "\n\nPREVIOUSLY CREATED FLASHCARDS (DO NOT REPEAT OR CREATE SIMILAR TOPICS):\n"
            for i, pc in enumerate(previous_cards, 1):
                previous_context += f"{i}. {pc}\n"
            previous_context += "\nIMPORTANT: Create flashcards on DIFFERENT topics/concepts than the above flashcards.\n"
        
        # Flashcard prompt
        prompt = PromptTemplate(
            input_variables=["content", "count", "previous_context"],
            template="""You are an expert educator creating comprehensive study flashcards. Based on the following educational content, create {count} flashcards that systematically cover the ENTIRE unit.

Content:
{content}
{previous_context}
IMPORTANT INSTRUCTIONS:
1. Cover ALL major topics and subtopics from the content
2. If previous flashcards are provided above, ensure your new flashcards cover COMPLETELY DIFFERENT topics
3. Distribute flashcards across different sections of the material
4. Include a mix of:
   - Key definitions and terminology
   - Important concepts and principles
   - Formulas, equations, or procedures (if applicable)
   - Real-world applications and examples
   - Relationships between concepts
5. Progress from fundamental to advanced concepts
6. Ensure NO duplicate or overlapping content
7. Keep answers concise but informative (2-3 sentences)

For each flashcard, provide:
- Front: A clear question or term
- Back: A concise, accurate answer or definition

Format each flashcard as follows:
Flashcard X:
Front: [question or term]
Back: [concise answer - 2-3 sentences maximum]

---

Create {count} flashcards that comprehensively cover the ENTIRE unit from beginning to end."""
        )
        
        # Create chain using LCEL
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            result = chain.invoke({"content": content, "count": count, "previous_context": previous_context})
            
            # Parse flashcards
            flashcards = self._parse_flashcards(result)
            
            return {
                "status": "success",
                "subject": subject,
                "unit": unit,
                "count": len(flashcards),
                "flashcards": flashcards
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error generating flashcards: {str(e)}"
            }
    
    def _parse_flashcards(self, flashcard_text: str) -> List[Dict]:

        flashcards = []
        
        # Split by flashcard separator
        cards = flashcard_text.split("---")
        
        for card_text in cards:
            if not card_text.strip():
                continue
            
            # Extract front
            front_match = re.search(r'Front:\s*(.+?)(?=\nBack:)', card_text, re.DOTALL)
            if not front_match:
                continue
            
            front = front_match.group(1).strip()
            
            # Extract back
            back_match = re.search(r'Back:\s*(.+?)(?=\n---|\Z)', card_text, re.DOTALL)
            back = back_match.group(1).strip() if back_match else ""
            
            if front and back:
                flashcards.append({
                    "front": front,
                    "back": back
                })
        
        return flashcards
    
    def ask_question(self, subject: str, unit: str, question: str) -> Dict:

        embedding_service = get_embedding_service()
        
        # Query relevant documents
        relevant_docs = embedding_service.query_documents(subject, unit, question, n_results=5)
        
        if not relevant_docs:
            return {
                "status": "error",
                "message": "No relevant content found for this question"
            }
        
        # Combine context
        context = "\n\n".join([doc["content"] for doc in relevant_docs])
        
        # QA prompt
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a helpful teaching assistant. Answer the student's question based on the provided context.

Context:
{context}

Student's Question: {question}

Instructions:
- Answer clearly and concisely
- Use the context to provide accurate information
- If the context doesn't contain enough information, say "I don't have enough information in the study materials to fully answer this question."
- Be educational and helpful

Answer:"""
        )
        
        # Create chain using LCEL
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            answer = chain.invoke({"context": context, "question": question})
            
            return {
                "status": "success",
                "question": question,
                "answer": answer,
                "sources": [doc["metadata"].get("source", "Unknown") for doc in relevant_docs]
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error answering question: {str(e)}"
            }

# Global instance
_rag_service_instance = None

def get_rag_service() -> RAGService:

    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
    return _rag_service_instance
