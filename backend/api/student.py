from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict
from services.file_service import get_file_service
from services.rag_service import get_rag_service

router = APIRouter()

# Request models
class SummaryRequest(BaseModel):
    subject: str
    unit: str
    chapter: Optional[str] = None

class MCQRequest(BaseModel):
    subject: str
    unit: str
    count: int = 10
    previous_questions: Optional[List[str]] = None

class FlashcardRequest(BaseModel):
    subject: str
    unit: str
    count: int = 10
    previous_cards: Optional[List[str]] = None

class AskRequest(BaseModel):
    subject: str
    unit: str
    question: str

@router.post("/summary")
async def generate_summary(request: SummaryRequest):

    
    file_service = get_file_service()
    
    # Check if embeddings exist
    if not file_service.is_embedding_done(request.subject, request.unit):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No study materials available. Please contact faculty to upload materials."
        )
    
    rag_service = get_rag_service()
    
    try:
        result = rag_service.generate_summary(
            request.subject,
            request.unit,
            request.chapter
        )
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating summary: {str(e)}"
        )

@router.post("/mcq")
async def generate_mcq(request: MCQRequest):

    
    file_service = get_file_service()
    
    # Check if embeddings exist
    if not file_service.is_embedding_done(request.subject, request.unit):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No study materials available. Please contact faculty to upload materials."
        )
    
    rag_service = get_rag_service()
    
    try:
        result = rag_service.generate_mcqs(
            request.subject,
            request.unit,
            request.count,
            request.previous_questions
        )
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating MCQs: {str(e)}"
        )

@router.post("/flashcards")
async def generate_flashcards(request: FlashcardRequest):

    
    file_service = get_file_service()
    
    # Check if embeddings exist
    if not file_service.is_embedding_done(request.subject, request.unit):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No study materials available. Please contact faculty to upload materials."
        )
    
    rag_service = get_rag_service()
    
    try:
        result = rag_service.generate_flashcards(
            request.subject,
            request.unit,
            request.count,
            request.previous_cards
        )
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating flashcards: {str(e)}"
        )

@router.post("/ask")
async def ask_question(request: AskRequest):

    
    file_service = get_file_service()
    
    # Check if embeddings exist
    if not file_service.is_embedding_done(request.subject, request.unit):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No study materials available. Please contact faculty to upload materials."
        )
    
    rag_service = get_rag_service()
    
    try:
        result = rag_service.ask_question(
            request.subject,
            request.unit,
            request.question
        )
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error answering question: {str(e)}"
        )

@router.get("/subjects")
async def get_subjects():

    file_service = get_file_service()
    subjects = file_service.get_all_subjects()
    return {"subjects": subjects}

@router.get("/units/{subject}")
async def get_units(subject: str):

    file_service = get_file_service()
    units = file_service.get_units_for_subject(subject)
    return {"subject": subject, "units": units}
